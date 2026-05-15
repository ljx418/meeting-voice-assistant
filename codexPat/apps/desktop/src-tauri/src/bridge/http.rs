use super::{
    protocol::{accepted_event_from_value, capabilities, validate_pet_event},
    rate_limit::RateLimiter,
    received_at, BridgeDebugHandle, EventSummary, RejectReasonCode, LISTEN_ADDRESS,
};
use crate::sound::SoundHandle;
use axum::{
    body::Bytes,
    extract::State,
    http::{header::AUTHORIZATION, HeaderMap, StatusCode},
    response::IntoResponse,
    routing::{get, post},
    Json, Router,
};
use serde::Serialize;
use serde_json::{json, Value};
use std::{
    net::SocketAddr,
    sync::{Arc, Mutex},
};
use tauri::{AppHandle, Emitter};
use tokio::{net::TcpListener, sync::oneshot};

#[derive(Clone)]
struct HttpState {
    app: AppHandle,
    token: String,
    debug: BridgeDebugHandle,
    sound: SoundHandle,
    rate_limiter: Arc<Mutex<RateLimiter>>,
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct HealthResponse {
    ok: bool,
    app: &'static str,
    phase: &'static str,
    listen_address: &'static str,
}

pub fn spawn_server(
    app: AppHandle,
    token: String,
    debug: BridgeDebugHandle,
    sound: SoundHandle,
    shutdown_rx: oneshot::Receiver<()>,
) {
    let state = HttpState {
        app,
        token,
        debug: debug.clone(),
        sound,
        rate_limiter: Arc::new(Mutex::new(RateLimiter::default())),
    };

    tauri::async_runtime::spawn(async move {
        let address = match LISTEN_ADDRESS.parse::<SocketAddr>() {
            Ok(address) => address,
            Err(error) => {
                debug.set_startup_error(error.to_string());
                debug.record_rejected(EventSummary {
                    id: debug.event_id(),
                    received_at: received_at(),
                    source_id: None,
                    level: None,
                    title_preview: None,
                    message_preview: None,
                    status: StatusCode::SERVICE_UNAVAILABLE.as_u16(),
                    accepted: false,
                    reason_code: Some(RejectReasonCode::BridgeUnavailable),
                    reason: Some("listen address is invalid".to_string()),
                });
                return;
            }
        };

        let listener = match TcpListener::bind(address).await {
            Ok(listener) => listener,
            Err(error) => {
                debug.set_startup_error(error.to_string());
                debug.record_rejected(EventSummary {
                    id: debug.event_id(),
                    received_at: received_at(),
                    source_id: None,
                    level: None,
                    title_preview: None,
                    message_preview: None,
                    status: StatusCode::SERVICE_UNAVAILABLE.as_u16(),
                    accepted: false,
                    reason_code: Some(RejectReasonCode::PortBindFailed),
                    reason: Some(error.to_string()),
                });
                return;
            }
        };

        debug.set_enabled(true);
        let app = Router::new()
            .route("/api/health", get(health))
            .route("/api/capabilities", get(get_capabilities))
            .route("/api/diagnostics", get(get_diagnostics))
            .route("/api/events", post(post_event))
            .with_state(state);

        let server = axum::serve(listener, app).with_graceful_shutdown(async {
            let _ = shutdown_rx.await;
        });

        if let Err(error) = server.await {
            debug.set_startup_error(error.to_string());
        }
    });
}

async fn health() -> Json<HealthResponse> {
    Json(HealthResponse {
        ok: true,
        app: "agent-desktop-pet",
        phase: "phase-4",
        listen_address: LISTEN_ADDRESS,
    })
}

async fn get_capabilities() -> Json<impl Serialize> {
    Json(capabilities())
}

async fn get_diagnostics(State(state): State<HttpState>, headers: HeaderMap) -> impl IntoResponse {
    if let Err((status, code)) = authorize(&headers, &state.token) {
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            status,
            code,
            reason_for_code(code),
        ));
        return (
            status,
            Json(json!({
                "ok": false,
                "accepted": false,
                "reasonCode": reason_code_str(code),
                "reason": reason_for_code(code)
            })),
        )
            .into_response();
    }

    Json(state.debug.snapshot(state.sound.diagnostics())).into_response()
}

async fn post_event(
    State(state): State<HttpState>,
    headers: HeaderMap,
    body: Bytes,
) -> impl IntoResponse {
    if let Err((status, code)) = authorize(&headers, &state.token) {
        let summary = rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            status,
            code,
            reason_for_code(code),
        );
        state.debug.record_rejected(summary);
        return error_response(status, code, reason_for_code(code));
    }

    if body.len() > 8192 {
        let summary = rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            RejectReasonCode::PayloadTooLarge,
            "payload too large",
        );
        state.debug.record_rejected(summary);
        return error_response(
            StatusCode::BAD_REQUEST,
            RejectReasonCode::PayloadTooLarge,
            "payload too large",
        );
    }

    let value = match serde_json::from_slice::<Value>(&body) {
        Ok(value) => value,
        Err(error) => {
            let summary = rejected_summary(
                state.debug.event_id(),
                None,
                None,
                None,
                None,
                StatusCode::BAD_REQUEST,
                RejectReasonCode::SchemaInvalid,
                &error.to_string(),
            );
            state.debug.record_rejected(summary);
            return error_response(
                StatusCode::BAD_REQUEST,
                RejectReasonCode::SchemaInvalid,
                "invalid json",
            );
        }
    };

    let request_source_id = source_id(&value);
    let request_level = level(&value);
    let request_title = string_field(&value, "title");
    let request_message = string_field(&value, "message");

    if let Err(error) = validate_pet_event(&value) {
        let code = classify_validation_error(&error);
        let summary = rejected_summary(
            state.debug.event_id(),
            request_source_id,
            request_level,
            request_title,
            request_message,
            StatusCode::BAD_REQUEST,
            code,
            &error,
        );
        state.debug.record_rejected(summary);
        return error_response(StatusCode::BAD_REQUEST, code, "validation failed");
    }

    let source_id_for_limit = source_id(&value).unwrap_or_else(|| "unknown".to_string());
    if let Err(error) = state
        .rate_limiter
        .lock()
        .map_err(|error| error.to_string())
        .and_then(|mut limiter| limiter.check(&source_id_for_limit))
    {
        let summary = rejected_summary(
            state.debug.event_id(),
            source_id(&value),
            level(&value),
            string_field(&value, "title"),
            string_field(&value, "message"),
            StatusCode::TOO_MANY_REQUESTS,
            RejectReasonCode::RateLimited,
            &error,
        );
        state.debug.record_rejected(summary);
        return error_response(
            StatusCode::TOO_MANY_REQUESTS,
            RejectReasonCode::RateLimited,
            "rate limit exceeded",
        );
    }

    let received_at = received_at();
    let accepted = match accepted_event_from_value(value, received_at.clone()) {
        Ok(event) => event,
        Err(error) => {
            let summary = rejected_summary(
                state.debug.event_id(),
                None,
                None,
                None,
                None,
                StatusCode::BAD_REQUEST,
                RejectReasonCode::SchemaInvalid,
                &error,
            );
            state.debug.record_rejected(summary);
            return error_response(
                StatusCode::BAD_REQUEST,
                RejectReasonCode::SchemaInvalid,
                "invalid event",
            );
        }
    };

    let event_id = state.debug.event_id();
    if state
        .debug
        .admit_event(event_id.clone(), accepted.clone())
        .is_err()
    {
        let summary = rejected_summary(
            event_id,
            Some(accepted.source.id),
            Some(accepted.level),
            accepted.title,
            accepted.message,
            StatusCode::TOO_MANY_REQUESTS,
            RejectReasonCode::QueueFull,
            "ingress queue full",
        );
        state.debug.record_rejected(summary);
        return error_response(
            StatusCode::TOO_MANY_REQUESTS,
            RejectReasonCode::QueueFull,
            "ingress queue full",
        );
    }

    let summary = EventSummary {
        id: event_id.clone(),
        received_at,
        source_id: Some(accepted.source.id.clone()),
        level: Some(accepted.level.clone()),
        title_preview: preview(accepted.title.as_deref(), 80),
        message_preview: preview(accepted.message.as_deref(), 120),
        status: StatusCode::ACCEPTED.as_u16(),
        accepted: true,
        reason_code: None,
        reason: None,
    };
    state.debug.record_accepted(summary);

    if let Err(error) = state.app.emit("pet-event:accepted", &accepted) {
        let summary = rejected_summary(
            event_id.clone(),
            Some(accepted.source.id),
            Some(accepted.level),
            accepted.title,
            accepted.message,
            StatusCode::INTERNAL_SERVER_ERROR,
            RejectReasonCode::EmitFailed,
            &error.to_string(),
        );
        state.debug.record_rejected(summary);
        return error_response(
            StatusCode::SERVICE_UNAVAILABLE,
            RejectReasonCode::BridgeUnavailable,
            "emit failed",
        );
    }

    state.debug.mark_emitted(&event_id);
    state.sound.handle_event(&accepted);

    (
        StatusCode::ACCEPTED,
        Json(json!({
            "ok": true,
            "accepted": true,
            "eventId": event_id,
            "queued": true
        })),
    )
}

fn authorize(headers: &HeaderMap, token: &str) -> Result<(), (StatusCode, RejectReasonCode)> {
    let Some(value) = headers.get(AUTHORIZATION) else {
        return Err((StatusCode::UNAUTHORIZED, RejectReasonCode::AuthMissing));
    };
    let Ok(value) = value.to_str() else {
        return Err((StatusCode::UNAUTHORIZED, RejectReasonCode::AuthInvalid));
    };
    if value == format!("Bearer {token}") {
        Ok(())
    } else {
        Err((StatusCode::UNAUTHORIZED, RejectReasonCode::AuthInvalid))
    }
}

fn rejected_summary(
    id: String,
    source_id: Option<String>,
    level: Option<String>,
    title: Option<String>,
    message: Option<String>,
    status: StatusCode,
    reason_code: RejectReasonCode,
    reason: &str,
) -> EventSummary {
    EventSummary {
        id,
        received_at: received_at(),
        source_id,
        level,
        title_preview: preview(title.as_deref(), 80),
        message_preview: preview(message.as_deref(), 120),
        status: status.as_u16(),
        accepted: false,
        reason_code: Some(reason_code),
        reason: Some(reason.to_string()),
    }
}

fn source_id(value: &Value) -> Option<String> {
    value
        .get("source")
        .and_then(|source| source.get("id"))
        .and_then(|id| id.as_str())
        .map(ToString::to_string)
}

fn level(value: &Value) -> Option<String> {
    value
        .get("level")
        .and_then(|level| level.as_str())
        .map(ToString::to_string)
}

fn string_field(value: &Value, field: &str) -> Option<String> {
    value
        .get(field)
        .and_then(|value| value.as_str())
        .map(ToString::to_string)
}

fn preview(value: Option<&str>, max_chars: usize) -> Option<String> {
    value.map(|value| value.chars().take(max_chars).collect())
}

fn classify_validation_error(error: &str) -> RejectReasonCode {
    if error.contains("is not allowed") || error.contains("is not one of") {
        RejectReasonCode::WhitelistInvalid
    } else {
        RejectReasonCode::SchemaInvalid
    }
}

fn error_response(
    status: StatusCode,
    reason_code: RejectReasonCode,
    reason: &str,
) -> (StatusCode, Json<Value>) {
    (
        status,
        Json(json!({
            "ok": false,
            "accepted": false,
            "reasonCode": reason_code_str(reason_code),
            "reason": reason
        })),
    )
}

fn reason_for_code(code: RejectReasonCode) -> &'static str {
    match code {
        RejectReasonCode::AuthMissing => "authorization bearer token is required",
        RejectReasonCode::AuthInvalid => "authorization bearer token is invalid",
        RejectReasonCode::SchemaInvalid => "schema validation failed",
        RejectReasonCode::WhitelistInvalid => "whitelist validation failed",
        RejectReasonCode::PayloadTooLarge => "payload too large",
        RejectReasonCode::RateLimited => "rate limit exceeded",
        RejectReasonCode::QueueFull => "ingress queue full",
        RejectReasonCode::QueueReplaced => "queued event was replaced",
        RejectReasonCode::BridgeUnavailable => "bridge unavailable",
        RejectReasonCode::PortBindFailed => "port bind failed",
        RejectReasonCode::EmitFailed => "emit failed",
    }
}

fn reason_code_str(code: RejectReasonCode) -> &'static str {
    match code {
        RejectReasonCode::AuthMissing => "auth_missing",
        RejectReasonCode::AuthInvalid => "auth_invalid",
        RejectReasonCode::SchemaInvalid => "schema_invalid",
        RejectReasonCode::WhitelistInvalid => "whitelist_invalid",
        RejectReasonCode::PayloadTooLarge => "payload_too_large",
        RejectReasonCode::RateLimited => "rate_limited",
        RejectReasonCode::QueueFull => "queue_full",
        RejectReasonCode::QueueReplaced => "queue_replaced",
        RejectReasonCode::BridgeUnavailable => "bridge_unavailable",
        RejectReasonCode::PortBindFailed => "port_bind_failed",
        RejectReasonCode::EmitFailed => "emit_failed",
    }
}
