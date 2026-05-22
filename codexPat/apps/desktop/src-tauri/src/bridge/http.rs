use super::{
    protocol::{accepted_event_from_value, capabilities, validate_pet_event},
    rate_limit::RateLimiter,
    received_at, BridgeDebugHandle, EventSummary, RejectReasonCode, LISTEN_ADDRESS,
};
use crate::sound::SoundHandle;
use axum::{
    body::Bytes,
    extract::{Path, State},
    http::{header::AUTHORIZATION, HeaderMap, StatusCode},
    response::IntoResponse,
    routing::{delete, get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::{
    net::SocketAddr,
    sync::{Arc, Mutex},
};
use tauri::{AppHandle, Emitter, Manager};
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

#[derive(Clone)]
struct EventTarget {
    instance_id: String,
    window_label: String,
    visible: bool,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct CreateInstanceRequest {
    source_kind: Option<String>,
    source_id: Option<String>,
    display_name: Option<String>,
    workspace_label: Option<String>,
    workspace_hash: Option<String>,
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
                    target_instance_id: None,
                    target_window_label: None,
                    status: StatusCode::SERVICE_UNAVAILABLE.as_u16(),
                    accepted: false,
                    reason_code: Some(RejectReasonCode::BridgeUnavailable),
                    reason_field: Some("bridge".to_string()),
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
                    target_instance_id: None,
                    target_window_label: None,
                    status: StatusCode::SERVICE_UNAVAILABLE.as_u16(),
                    accepted: false,
                    reason_code: Some(RejectReasonCode::PortBindFailed),
                    reason_field: Some("bridge".to_string()),
                    reason: Some("port bind failed".to_string()),
                });
                return;
            }
        };

        debug.set_enabled(true);
        let app = Router::new()
            .route("/api/health", get(health))
            .route("/api/capabilities", get(get_capabilities))
            .route("/api/diagnostics", get(get_diagnostics))
            .route("/api/instances", get(get_instances).post(post_instance))
            .route("/api/instances/:instance_id", delete(delete_instance))
            .route("/api/events", post(post_event))
            .route(
                "/api/instances/:instance_id/events",
                post(post_instance_event),
            )
            .route(
                "/api/instances/:invalid_a/:invalid_b/events",
                post(post_invalid_instance_path),
            )
            .route(
                "/api/instances/:invalid_a/:invalid_b/:invalid_c/events",
                post(post_invalid_instance_path),
            )
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
        let reason = sanitized_reason(code, "auth");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            status,
            reason,
        ));
        return (
            status,
            Json(json!({
                "ok": false,
                "accepted": false,
                "reasonCode": reason_code_str(code),
                "reasonField": reason.field,
                "reason": reason.message
            })),
        )
            .into_response();
    }

    Json(state.debug.snapshot(state.sound.diagnostics())).into_response()
}

async fn get_instances(State(state): State<HttpState>, headers: HeaderMap) -> impl IntoResponse {
    if let Err((status, code)) = authorize(&headers, &state.token) {
        let reason = sanitized_reason(code, "auth");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            status,
            reason,
        ));
        return error_response(status, reason).into_response();
    }

    match state.app.try_state::<crate::AppState>() {
        Some(app_state) => match app_state.settings.lock() {
            Ok(settings) => Json(json!({
                "ok": true,
                "instances": crate::pet_instance_views(&settings),
                "limits": crate::pet_instance_limits(&settings)
            }))
            .into_response(),
            Err(_error) => {
                let reason = sanitized_reason(RejectReasonCode::BridgeUnavailable, "bridge");
                error_response(StatusCode::SERVICE_UNAVAILABLE, reason).into_response()
            }
        },
        None => {
            let reason = sanitized_reason(RejectReasonCode::BridgeUnavailable, "bridge");
            error_response(StatusCode::SERVICE_UNAVAILABLE, reason).into_response()
        }
    }
}

async fn post_instance(
    State(state): State<HttpState>,
    headers: HeaderMap,
    body: Bytes,
) -> impl IntoResponse {
    if let Err((status, code)) = authorize(&headers, &state.token) {
        let reason = sanitized_reason(code, "auth");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            status,
            reason,
        ));
        return error_response(status, reason).into_response();
    }

    if body.len() > 4096 {
        let reason = sanitized_reason(RejectReasonCode::PayloadTooLarge, "payload");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            reason,
        ));
        return error_response(StatusCode::BAD_REQUEST, reason).into_response();
    }

    let request = match serde_json::from_slice::<CreateInstanceRequest>(&body) {
        Ok(request) => request,
        Err(_error) => {
            let reason = sanitized_reason(RejectReasonCode::SchemaInvalid, "payload");
            state.debug.record_rejected(rejected_summary(
                state.debug.event_id(),
                None,
                None,
                None,
                None,
                None,
                StatusCode::BAD_REQUEST,
                reason,
            ));
            return error_response(StatusCode::BAD_REQUEST, reason).into_response();
        }
    };

    let source_kind = request.source_kind.unwrap_or_else(|| "codex".to_string());
    if !matches!(source_kind.as_str(), "codex" | "custom") {
        let reason = sanitized_reason(RejectReasonCode::SourceKindInvalid, "source.kind");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            reason,
        ));
        return error_response(StatusCode::BAD_REQUEST, reason).into_response();
    }

    let source_id = request.source_id.unwrap_or_else(|| {
        if source_kind == "codex" {
            "codex.local".to_string()
        } else {
            "custom.local".to_string()
        }
    });
    if !is_valid_source_id(&source_id) {
        let reason = sanitized_reason(RejectReasonCode::WhitelistInvalid, "source.id");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            reason,
        ));
        return error_response(StatusCode::BAD_REQUEST, reason).into_response();
    }

    let display_name = request
        .display_name
        .map(|value| value.trim().to_string())
        .unwrap_or_else(|| "Codex Cat".to_string());
    if !is_valid_display_name(&display_name) {
        let reason = sanitized_reason(RejectReasonCode::DisplayNameInvalid, "display_name");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            reason,
        ));
        return error_response(StatusCode::BAD_REQUEST, reason).into_response();
    }

    if !is_valid_optional_label(request.workspace_label.as_deref()) {
        let reason = sanitized_reason(RejectReasonCode::WorkspaceLabelInvalid, "workspace_label");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            reason,
        ));
        return error_response(StatusCode::BAD_REQUEST, reason).into_response();
    }

    if !is_valid_optional_workspace_hash(request.workspace_hash.as_deref()) {
        let reason = sanitized_reason(RejectReasonCode::WorkspaceHashInvalid, "workspace_hash");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            reason,
        ));
        return error_response(StatusCode::BAD_REQUEST, reason).into_response();
    }

    let app_state = match state.app.try_state::<crate::AppState>() {
        Some(app_state) => app_state,
        None => {
            let reason = sanitized_reason(RejectReasonCode::BridgeUnavailable, "bridge");
            return error_response(StatusCode::SERVICE_UNAVAILABLE, reason).into_response();
        }
    };
    if let Ok(settings) = app_state.settings.lock() {
        if crate::pet_instance_limits(&settings).at_hard_limit {
            let reason = sanitized_reason(RejectReasonCode::InstanceLimitReached, "instance_limit");
            state.debug.record_rejected(rejected_summary(
                state.debug.event_id(),
                None,
                None,
                None,
                None,
                None,
                StatusCode::CONFLICT,
                reason,
            ));
            return error_response(StatusCode::CONFLICT, reason).into_response();
        }
    }
    let instance = match crate::create_pet_instance_for_source(
        &state.app,
        &app_state,
        display_name,
        source_kind,
        source_id,
        request.workspace_label,
        request.workspace_hash,
    ) {
        Ok(instance) => instance,
        Err(error) => {
            if error == "instance_limit_reached" {
                let reason =
                    sanitized_reason(RejectReasonCode::InstanceLimitReached, "instance_limit");
                return error_response(StatusCode::CONFLICT, reason).into_response();
            }
            let reason = sanitized_reason(RejectReasonCode::BridgeUnavailable, "bridge");
            return error_response(StatusCode::SERVICE_UNAVAILABLE, reason).into_response();
        }
    };

    Json(json!({
        "ok": true,
        "created": true,
        "instanceId": instance.instance_id,
        "displayName": instance.display_name,
        "windowLabel": instance.window_label,
        "export": format!("export AGENT_DESKTOP_PET_INSTANCE_ID={}", instance.instance_id),
        "instance": instance
    }))
    .into_response()
}

async fn delete_instance(
    State(state): State<HttpState>,
    Path(instance_id): Path<String>,
    headers: HeaderMap,
) -> impl IntoResponse {
    if let Err((status, code)) = authorize(&headers, &state.token) {
        let reason = sanitized_reason(code, "auth");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            status,
            reason,
        ));
        return error_response(status, reason).into_response();
    }

    if !is_valid_instance_id(&instance_id) {
        let reason = sanitized_reason(RejectReasonCode::InstanceIdInvalid, "instance");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            reason,
        ));
        return error_response(StatusCode::BAD_REQUEST, reason).into_response();
    }

    if instance_id == "default" {
        let reason = sanitized_reason(RejectReasonCode::DefaultInstanceCannotDetach, "instance");
        state.debug.record_rejected(rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            reason,
        ));
        return error_response(StatusCode::BAD_REQUEST, reason).into_response();
    }

    let app_state = match state.app.try_state::<crate::AppState>() {
        Some(app_state) => app_state,
        None => {
            let reason = sanitized_reason(RejectReasonCode::BridgeUnavailable, "bridge");
            return error_response(StatusCode::SERVICE_UNAVAILABLE, reason).into_response();
        }
    };

    match crate::detach_pet_instance_by_id(&state.app, &app_state, &instance_id) {
        Ok(instance) => Json(json!({
            "ok": true,
            "detached": true,
            "instanceId": instance.instance_id,
            "windowLabel": instance.window_label
        }))
        .into_response(),
        Err(error) if error == "instance_not_found" => {
            let reason = sanitized_reason(RejectReasonCode::InstanceNotFound, "instance");
            state.debug.record_rejected(rejected_summary(
                state.debug.event_id(),
                None,
                None,
                None,
                None,
                None,
                StatusCode::NOT_FOUND,
                reason,
            ));
            error_response(StatusCode::NOT_FOUND, reason).into_response()
        }
        Err(error) if error == "default_instance_cannot_detach" => {
            let reason = sanitized_reason(RejectReasonCode::DefaultInstanceCannotDetach, "instance");
            state.debug.record_rejected(rejected_summary(
                state.debug.event_id(),
                None,
                None,
                None,
                None,
                None,
                StatusCode::BAD_REQUEST,
                reason,
            ));
            error_response(StatusCode::BAD_REQUEST, reason).into_response()
        }
        Err(_error) => {
            let reason = sanitized_reason(RejectReasonCode::BridgeUnavailable, "bridge");
            error_response(StatusCode::SERVICE_UNAVAILABLE, reason).into_response()
        }
    }
}

async fn post_event(
    State(state): State<HttpState>,
    headers: HeaderMap,
    body: Bytes,
) -> impl IntoResponse {
    post_event_for_target(state, headers, body, None).await
}

async fn post_instance_event(
    State(state): State<HttpState>,
    Path(instance_id): Path<String>,
    headers: HeaderMap,
    body: Bytes,
) -> impl IntoResponse {
    if let Err((status, code)) = authorize(&headers, &state.token) {
        let reason = sanitized_reason(code, "auth");
        let summary = rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            status,
            reason,
        );
        state.debug.record_rejected(summary);
        return error_response(status, reason).into_response();
    }

    let Some(target) = resolve_instance_target(&state, &instance_id) else {
        let reason = if is_valid_instance_id(&instance_id) {
            sanitized_reason(RejectReasonCode::InstanceNotFound, "instance")
        } else {
            sanitized_reason(RejectReasonCode::InstanceIdInvalid, "instance")
        };
        let status = if reason.code == RejectReasonCode::InstanceNotFound {
            StatusCode::NOT_FOUND
        } else {
            StatusCode::BAD_REQUEST
        };
        let summary = rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            status,
            reason,
        );
        state.debug.record_rejected(summary);
        return error_response(status, reason).into_response();
    };

    post_event_for_target_with_authorized_request(state, body, Some(target))
        .await
        .into_response()
}

async fn post_invalid_instance_path(
    State(state): State<HttpState>,
    headers: HeaderMap,
    _body: Bytes,
) -> impl IntoResponse {
    if let Err((status, code)) = authorize(&headers, &state.token) {
        let reason = sanitized_reason(code, "auth");
        let summary = rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            None,
            status,
            reason,
        );
        state.debug.record_rejected(summary);
        return error_response(status, reason).into_response();
    }

    let reason = sanitized_reason(RejectReasonCode::InstanceIdInvalid, "instance");
    let summary = rejected_summary(
        state.debug.event_id(),
        None,
        None,
        None,
        None,
        None,
        StatusCode::BAD_REQUEST,
        reason,
    );
    state.debug.record_rejected(summary);
    error_response(StatusCode::BAD_REQUEST, reason).into_response()
}

async fn post_event_for_target(
    state: HttpState,
    headers: HeaderMap,
    body: Bytes,
    target: Option<EventTarget>,
) -> (StatusCode, Json<Value>) {
    if let Err((status, code)) = authorize(&headers, &state.token) {
        let reason = sanitized_reason(code, "auth");
        let summary = rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            target.as_ref(),
            status,
            reason,
        );
        state.debug.record_rejected(summary);
        return error_response(status, reason);
    }

    post_event_for_target_with_authorized_request(state, body, target).await
}

async fn post_event_for_target_with_authorized_request(
    state: HttpState,
    body: Bytes,
    target: Option<EventTarget>,
) -> (StatusCode, Json<Value>) {
    if body.len() > 8192 {
        let reason = sanitized_reason(RejectReasonCode::PayloadTooLarge, "payload");
        let summary = rejected_summary(
            state.debug.event_id(),
            None,
            None,
            None,
            None,
            target.as_ref(),
            StatusCode::BAD_REQUEST,
            reason,
        );
        state.debug.record_rejected(summary);
        return error_response(StatusCode::BAD_REQUEST, reason);
    }

    let value = match serde_json::from_slice::<Value>(&body) {
        Ok(value) => value,
        Err(_error) => {
            let reason = sanitized_reason(RejectReasonCode::SchemaInvalid, "payload");
            let summary = rejected_summary(
                state.debug.event_id(),
                None,
                None,
                None,
                None,
                target.as_ref(),
                StatusCode::BAD_REQUEST,
                reason,
            );
            state.debug.record_rejected(summary);
            return error_response(StatusCode::BAD_REQUEST, reason);
        }
    };

    if let Err(error) = validate_pet_event(&value) {
        let code = classify_validation_error(&error);
        let field = infer_validation_reason_field(&value, &error);
        let reason = sanitized_reason(code, field);
        let summary = rejected_summary(
            state.debug.event_id(),
            safe_source_id(&value),
            safe_level(&value),
            None,
            None,
            target.as_ref(),
            StatusCode::BAD_REQUEST,
            reason,
        );
        state.debug.record_rejected(summary);
        return error_response(StatusCode::BAD_REQUEST, reason);
    }

    let source_id_for_limit = rate_limit_key(&value, target.as_ref());
    if state
        .rate_limiter
        .lock()
        .map_err(|error| error.to_string())
        .and_then(|mut limiter| limiter.check(&source_id_for_limit))
        .is_err()
    {
        let reason = sanitized_reason(RejectReasonCode::RateLimited, "rate_limit");
        let summary = rejected_summary(
            state.debug.event_id(),
            source_id(&value),
            level(&value),
            string_field(&value, "title"),
            string_field(&value, "message"),
            target.as_ref(),
            StatusCode::TOO_MANY_REQUESTS,
            reason,
        );
        state.debug.record_rejected(summary);
        return error_response(StatusCode::TOO_MANY_REQUESTS, reason);
    }

    let received_at = received_at();
    let mut accepted = match accepted_event_from_value(value, received_at.clone()) {
        Ok(event) => event,
        Err(_error) => {
            let reason = sanitized_reason(RejectReasonCode::SchemaInvalid, "payload");
            let summary = rejected_summary(
                state.debug.event_id(),
                None,
                None,
                None,
                None,
                target.as_ref(),
                StatusCode::BAD_REQUEST,
                reason,
            );
            state.debug.record_rejected(summary);
            return error_response(StatusCode::BAD_REQUEST, reason);
        }
    };
    if let Some(target) = target.as_ref() {
        accepted.target_instance_id = Some(target.instance_id.clone());
        accepted.target_window_label = Some(target.window_label.clone());
    }

    let event_id = state.debug.event_id();
    if state
        .debug
        .admit_event(event_id.clone(), accepted.clone())
        .is_err()
    {
        let reason = sanitized_reason(RejectReasonCode::QueueFull, "queue");
        let summary = rejected_summary(
            event_id,
            Some(accepted.source.id),
            Some(accepted.level),
            accepted.title,
            accepted.message,
            target.as_ref(),
            StatusCode::TOO_MANY_REQUESTS,
            reason,
        );
        state.debug.record_rejected(summary);
        return error_response(StatusCode::TOO_MANY_REQUESTS, reason);
    }

    let summary = EventSummary {
        id: event_id.clone(),
        received_at: received_at.clone(),
        source_id: Some(accepted.source.id.clone()),
        level: Some(accepted.level.clone()),
        title_preview: preview(accepted.title.as_deref(), 80),
        message_preview: preview(accepted.message.as_deref(), 120),
        target_instance_id: target.as_ref().map(|target| target.instance_id.clone()),
        target_window_label: target.as_ref().map(|target| target.window_label.clone()),
        status: StatusCode::ACCEPTED.as_u16(),
        accepted: true,
        reason_code: None,
        reason_field: None,
        reason: None,
    };
    state.debug.record_accepted(summary);
    if let Some(target) = target.as_ref() {
        if let Some(app_state) = state.app.try_state::<crate::AppState>() {
            let _ = crate::update_pet_instance_runtime(
                &app_state,
                &target.instance_id,
                &accepted.level,
                &received_at,
            );
        }
    }

    let emit_result = if let Some(target) = target.as_ref() {
        if target.visible {
            state
                .app
                .get_webview_window(&target.window_label)
                .ok_or(())
                .and_then(|window| window.emit("pet-event:accepted", &accepted).map_err(|_| ()))
        } else {
            Ok(())
        }
    } else {
        state
            .app
            .emit("pet-event:accepted", &accepted)
            .map_err(|_| ())
    };
    if emit_result.is_err() {
        let reason = sanitized_reason(RejectReasonCode::BridgeUnavailable, "bridge");
        let summary = rejected_summary(
            event_id.clone(),
            Some(accepted.source.id),
            Some(accepted.level),
            accepted.title,
            accepted.message,
            target.as_ref(),
            StatusCode::INTERNAL_SERVER_ERROR,
            reason,
        );
        state.debug.record_rejected(summary);
        return error_response(StatusCode::SERVICE_UNAVAILABLE, reason);
    }

    state.debug.mark_emitted(&event_id);
    let target_visible = target.as_ref().map(|target| target.visible).unwrap_or(true);
    state.sound.handle_event(&accepted, target_visible);

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

fn resolve_instance_target(state: &HttpState, instance_id: &str) -> Option<EventTarget> {
    if !is_valid_instance_id(instance_id) {
        return None;
    }
    let app_state = state.app.try_state::<crate::AppState>()?;
    let settings = app_state.settings.lock().ok()?;
    crate::pet_instance_target(&settings, instance_id).map(
        |(instance_id, window_label, visible)| EventTarget {
            instance_id,
            window_label,
            visible,
        },
    )
}

fn is_valid_instance_id(value: &str) -> bool {
    let length = value.chars().count();
    (1..=64).contains(&length)
        && !value.contains("..")
        && value.chars().all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | '-')
        })
}

fn is_valid_display_name(value: &str) -> bool {
    let length = value.chars().count();
    (1..=40).contains(&length)
        && !value
            .chars()
            .any(|character| character.is_control() || matches!(character, '/' | '\\' | ':'))
}

fn is_valid_optional_label(value: Option<&str>) -> bool {
    let Some(value) = value else {
        return true;
    };
    value.chars().count() <= 80
        && !value
            .chars()
            .any(|character| character.is_control() || matches!(character, '/' | '\\' | ':'))
}

fn is_valid_optional_workspace_hash(value: Option<&str>) -> bool {
    let Some(value) = value else {
        return true;
    };
    let length = value.chars().count();
    (1..=128).contains(&length)
        && value
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '_' | '-'))
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
    target: Option<&EventTarget>,
    status: StatusCode,
    reason: SanitizedRejectReason,
) -> EventSummary {
    EventSummary {
        id,
        received_at: received_at(),
        source_id,
        level,
        title_preview: preview(title.as_deref(), 80),
        message_preview: preview(message.as_deref(), 120),
        target_instance_id: target.map(|target| target.instance_id.clone()),
        target_window_label: target.map(|target| target.window_label.clone()),
        status: status.as_u16(),
        accepted: false,
        reason_code: Some(reason.code),
        reason_field: Some(reason.field.to_string()),
        reason: Some(reason.message.to_string()),
    }
}

fn source_id(value: &Value) -> Option<String> {
    value
        .get("source")
        .and_then(|source| source.get("id"))
        .and_then(|id| id.as_str())
        .map(ToString::to_string)
}

fn rate_limit_key(value: &Value, target: Option<&EventTarget>) -> String {
    let source = source_id(value).unwrap_or_else(|| "unknown".to_string());
    match target {
        Some(target) => format!("{source}:{}", target.instance_id),
        None => format!("{source}:default"),
    }
}

fn safe_source_id(value: &Value) -> Option<String> {
    match source_id(value) {
        Some(source_id) if is_valid_source_id(&source_id) => Some(source_id),
        Some(_) => Some("invalid_source".to_string()),
        None => Some("unknown".to_string()),
    }
}

fn is_valid_source_id(value: &str) -> bool {
    let length = value.chars().count();
    (1..=64).contains(&length)
        && value.chars().all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | '-')
        })
}

fn level(value: &Value) -> Option<String> {
    value
        .get("level")
        .and_then(|level| level.as_str())
        .map(ToString::to_string)
}

fn safe_level(value: &Value) -> Option<String> {
    level(value).filter(|level| {
        matches!(
            level.as_str(),
            "idle"
                | "thinking"
                | "running"
                | "success"
                | "warning"
                | "error"
                | "need_input"
                | "sleeping"
        )
    })
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

#[derive(Clone, Copy)]
struct SanitizedRejectReason {
    code: RejectReasonCode,
    field: &'static str,
    message: &'static str,
}

fn sanitized_reason(code: RejectReasonCode, field: &'static str) -> SanitizedRejectReason {
    let field = normalized_reason_field(code, field);
    SanitizedRejectReason {
        code,
        field,
        message: reason_for_field(code, field),
    }
}

fn normalized_reason_field(code: RejectReasonCode, field: &'static str) -> &'static str {
    match code {
        RejectReasonCode::AuthMissing | RejectReasonCode::AuthInvalid => "auth",
        RejectReasonCode::SchemaInvalid => match field {
            "source.id" | "level" | "action" | "sound" | "hardware.light.effect" => field,
            _ => "payload",
        },
        RejectReasonCode::WhitelistInvalid => match field {
            "level" | "action" | "sound" | "hardware.light.effect" => field,
            _ => "payload",
        },
        RejectReasonCode::PayloadTooLarge => "payload",
        RejectReasonCode::RateLimited => "rate_limit",
        RejectReasonCode::InstanceIdInvalid => "instance",
        RejectReasonCode::InstanceNotFound => "instance",
        RejectReasonCode::DefaultInstanceCannotDetach => "instance",
        RejectReasonCode::InstanceLimitReached => "instance_limit",
        RejectReasonCode::DisplayNameInvalid => "display_name",
        RejectReasonCode::SourceKindInvalid => "source.kind",
        RejectReasonCode::WorkspaceLabelInvalid => "workspace_label",
        RejectReasonCode::WorkspaceHashInvalid => "workspace_hash",
        RejectReasonCode::QueueFull | RejectReasonCode::QueueReplaced => "queue",
        RejectReasonCode::BridgeUnavailable
        | RejectReasonCode::PortBindFailed
        | RejectReasonCode::EmitFailed => "bridge",
    }
}

fn infer_validation_reason_field(value: &Value, error: &str) -> &'static str {
    if source_id(value)
        .as_deref()
        .is_some_and(|source_id| !is_valid_source_id(source_id))
    {
        return "source.id";
    }
    if string_field(value, "sound")
        .as_deref()
        .is_some_and(|sound| !is_allowed_sound(sound))
    {
        return "sound";
    }
    if string_field(value, "action")
        .as_deref()
        .is_some_and(|action| !is_allowed_action_or_level(action))
    {
        return "action";
    }
    if value
        .get("hardware")
        .and_then(|hardware| hardware.get("light"))
        .and_then(|light| light.get("effect"))
        .and_then(|effect| effect.as_str())
        .is_some_and(|effect| !is_allowed_light_effect(effect))
    {
        return "hardware.light.effect";
    }
    if string_field(value, "level")
        .as_deref()
        .is_some_and(|level| !is_allowed_action_or_level(level))
    {
        return "level";
    }
    if string_field(value, "sound").is_some() && field_error_matches(error, "sound") {
        return "sound";
    }
    if string_field(value, "action").is_some() && field_error_matches(error, "action") {
        return "action";
    }
    if string_field(value, "level").is_some() && field_error_matches(error, "level") {
        return "level";
    }
    "payload"
}

fn is_allowed_action_or_level(value: &str) -> bool {
    matches!(
        value,
        "idle"
            | "thinking"
            | "running"
            | "success"
            | "warning"
            | "error"
            | "need_input"
            | "sleeping"
    )
}

fn is_allowed_sound(value: &str) -> bool {
    matches!(
        value,
        "none" | "success_chime" | "warning_chime" | "error_chime" | "need_input_chime"
    )
}

fn is_allowed_light_effect(value: &str) -> bool {
    matches!(
        value,
        "none"
            | "thinking_blue"
            | "running_cyan"
            | "success_green"
            | "warning_amber"
            | "error_red"
            | "need_input_purple"
            | "sleeping_warm_dim"
    )
}

fn field_error_matches(error: &str, field: &str) -> bool {
    error.contains(&format!("\"{field}\""))
        || error.contains(&format!("/{field}"))
        || error.contains(field)
}

fn error_response(status: StatusCode, reason: SanitizedRejectReason) -> (StatusCode, Json<Value>) {
    (
        status,
        Json(json!({
            "ok": false,
            "accepted": false,
            "reasonCode": reason_code_str(reason.code),
            "reasonField": reason.field,
            "reason": reason.message
        })),
    )
}

fn reason_for_field(code: RejectReasonCode, field: &'static str) -> &'static str {
    match code {
        RejectReasonCode::AuthMissing => "authorization bearer token is required",
        RejectReasonCode::AuthInvalid => "authorization bearer token is invalid",
        RejectReasonCode::SchemaInvalid | RejectReasonCode::WhitelistInvalid => match field {
            "source.id" => "source id is invalid",
            "level" => "level is not an accepted value",
            "action" => "action is not an accepted ID",
            "sound" => "sound is not an accepted ID",
            "hardware.light.effect" => "hardware light effect is not an accepted ID",
            _ => "payload failed schema validation",
        },
        RejectReasonCode::PayloadTooLarge => "payload is too large",
        RejectReasonCode::RateLimited => "source rate limit exceeded",
        RejectReasonCode::InstanceIdInvalid => "instance id is invalid",
        RejectReasonCode::InstanceNotFound => "instance was not found",
        RejectReasonCode::DefaultInstanceCannotDetach => "default instance cannot be detached",
        RejectReasonCode::InstanceLimitReached => "pet instance limit reached",
        RejectReasonCode::DisplayNameInvalid => "display name is invalid",
        RejectReasonCode::SourceKindInvalid => "source kind is not accepted",
        RejectReasonCode::WorkspaceLabelInvalid => "workspace label is invalid",
        RejectReasonCode::WorkspaceHashInvalid => "workspace hash is invalid",
        RejectReasonCode::QueueFull => "event queue is full",
        RejectReasonCode::QueueReplaced => "queued event was replaced",
        RejectReasonCode::BridgeUnavailable => "bridge unavailable",
        RejectReasonCode::PortBindFailed => "port bind failed",
        RejectReasonCode::EmitFailed => "bridge unavailable",
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
        RejectReasonCode::InstanceIdInvalid => "instance_id_invalid",
        RejectReasonCode::InstanceNotFound => "instance_not_found",
        RejectReasonCode::DefaultInstanceCannotDetach => "default_instance_cannot_detach",
        RejectReasonCode::InstanceLimitReached => "instance_limit_reached",
        RejectReasonCode::DisplayNameInvalid => "display_name_invalid",
        RejectReasonCode::SourceKindInvalid => "source_kind_invalid",
        RejectReasonCode::WorkspaceLabelInvalid => "workspace_label_invalid",
        RejectReasonCode::WorkspaceHashInvalid => "workspace_hash_invalid",
        RejectReasonCode::QueueFull => "queue_full",
        RejectReasonCode::QueueReplaced => "queue_replaced",
        RejectReasonCode::BridgeUnavailable => "bridge_unavailable",
        RejectReasonCode::PortBindFailed => "port_bind_failed",
        RejectReasonCode::EmitFailed => "emit_failed",
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    fn rejected_for_invalid_payload(value: Value) -> EventSummary {
        let error = validate_pet_event(&value).expect_err("payload should be invalid");
        let code = classify_validation_error(&error);
        let field = infer_validation_reason_field(&value, &error);
        rejected_summary(
            "evt_test".to_string(),
            safe_source_id(&value),
            safe_level(&value),
            None,
            None,
            None,
            StatusCode::BAD_REQUEST,
            sanitized_reason(code, field),
        )
    }

    fn assert_no_sensitive_text(summary: &EventSummary) {
        let serialized = serde_json::to_string(summary).expect("summary should serialize");
        for forbidden in [
            "../../x.wav",
            "file://",
            "http://",
            "https://",
            "/tmp/",
            "Application Support",
            "api-token.json",
            "/Users/",
            "C:\\Users\\",
            "nope",
        ] {
            assert!(
                !serialized.contains(forbidden),
                "summary should not contain forbidden text {forbidden}: {serialized}"
            );
        }
    }

    fn event_with_sound(sound: &str) -> Value {
        json!({
            "source": {
                "id": "smoke.local",
                "kind": "custom",
                "name": "Smoke"
            },
            "level": "success",
            "sound": sound
        })
    }

    #[test]
    fn sanitizes_invalid_sound_paths_and_urls() {
        for sound in [
            "../../x.wav",
            "file:///tmp/x.wav",
            "https://example.com/x.wav",
            "/Users/test/secret.wav",
            "C:\\Users\\test\\secret.wav",
        ] {
            let summary = rejected_for_invalid_payload(event_with_sound(sound));
            assert_eq!(
                summary.reason_code,
                Some(RejectReasonCode::WhitelistInvalid)
            );
            assert_eq!(summary.reason_field.as_deref(), Some("sound"));
            assert_eq!(
                summary.reason.as_deref(),
                Some("sound is not an accepted ID")
            );
            assert_no_sensitive_text(&summary);
        }
    }

    #[test]
    fn sanitizes_invalid_level_without_echoing_value() {
        let summary = rejected_for_invalid_payload(json!({
            "source": {
                "id": "smoke.local",
                "kind": "custom"
            },
            "level": "nope"
        }));
        assert_eq!(summary.reason_field.as_deref(), Some("level"));
        assert_eq!(
            summary.reason.as_deref(),
            Some("level is not an accepted value")
        );
        assert_eq!(summary.level, None);
        assert_no_sensitive_text(&summary);
    }

    #[test]
    fn sanitizes_invalid_source_id() {
        let summary = rejected_for_invalid_payload(json!({
            "source": {
                "id": "../../secret",
                "kind": "custom"
            },
            "level": "success"
        }));
        assert_eq!(summary.source_id.as_deref(), Some("invalid_source"));
        assert_eq!(summary.reason_field.as_deref(), Some("source.id"));
        assert_eq!(summary.reason.as_deref(), Some("source id is invalid"));
        assert_no_sensitive_text(&summary);
    }

    #[test]
    fn keeps_auth_and_rate_limit_reasons_readable() {
        let auth = sanitized_reason(RejectReasonCode::AuthMissing, "auth");
        assert_eq!(auth.field, "auth");
        assert_eq!(auth.message, "authorization bearer token is required");

        let rate_limited = sanitized_reason(RejectReasonCode::RateLimited, "rate_limit");
        assert_eq!(rate_limited.field, "rate_limit");
        assert_eq!(rate_limited.message, "source rate limit exceeded");
    }

    #[test]
    fn error_response_uses_sanitized_reason_and_field() {
        let (_status, Json(body)) = error_response(
            StatusCode::BAD_REQUEST,
            sanitized_reason(RejectReasonCode::WhitelistInvalid, "sound"),
        );
        assert_eq!(body["reasonCode"], "whitelist_invalid");
        assert_eq!(body["reasonField"], "sound");
        assert_eq!(body["reason"], "sound is not an accepted ID");
    }
}
