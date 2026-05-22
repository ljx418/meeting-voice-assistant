mod http;
mod log;
pub(crate) mod protocol;
mod queue;
mod rate_limit;

use serde::Serialize;
use std::{
    fs,
    path::PathBuf,
    sync::atomic::{AtomicU64, Ordering},
    sync::{Arc, Mutex},
};
use tauri::{AppHandle, Manager};
use tokio::sync::oneshot;

use crate::sound::{SoundDiagnostics, SoundHandle};

pub const LISTEN_ADDRESS: &str = "127.0.0.1:17321";

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum RejectReasonCode {
    AuthMissing,
    AuthInvalid,
    SchemaInvalid,
    WhitelistInvalid,
    PayloadTooLarge,
    RateLimited,
    QueueFull,
    InstanceIdInvalid,
    InstanceNotFound,
    DefaultInstanceCannotDetach,
    InstanceLimitReached,
    DisplayNameInvalid,
    SourceKindInvalid,
    WorkspaceLabelInvalid,
    WorkspaceHashInvalid,
    #[allow(dead_code)]
    QueueReplaced,
    BridgeUnavailable,
    PortBindFailed,
    #[allow(dead_code)]
    EmitFailed,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct EventSummary {
    pub id: String,
    pub received_at: String,
    pub source_id: Option<String>,
    pub level: Option<String>,
    pub title_preview: Option<String>,
    pub message_preview: Option<String>,
    pub target_instance_id: Option<String>,
    pub target_window_label: Option<String>,
    pub status: u16,
    pub accepted: bool,
    pub reason_code: Option<RejectReasonCode>,
    pub reason_field: Option<String>,
    pub reason: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct BridgeDiagnostics {
    pub enabled: bool,
    pub listen_address: String,
    pub queue_length: usize,
    pub queue_capacity: usize,
    pub accepted_events: Vec<EventSummary>,
    pub rejected_events: Vec<EventSummary>,
    pub last_accepted: Option<EventSummary>,
    pub last_rejected: Option<EventSummary>,
    pub sound: SoundDiagnostics,
    pub hardware_light: bool,
    pub startup_error: Option<String>,
}

impl Default for BridgeDiagnostics {
    fn default() -> Self {
        Self {
            enabled: false,
            listen_address: LISTEN_ADDRESS.to_string(),
            queue_length: 0,
            queue_capacity: queue::INGRESS_QUEUE_CAPACITY,
            accepted_events: Vec::new(),
            rejected_events: Vec::new(),
            last_accepted: None,
            last_rejected: None,
            sound: SoundDiagnostics::default(),
            hardware_light: false,
            startup_error: None,
        }
    }
}

struct BridgeState {
    enabled: bool,
    startup_error: Option<String>,
    accepted_events: log::RingBuffer<EventSummary>,
    rejected_events: log::RingBuffer<EventSummary>,
    queue: queue::IngressQueue,
}

impl Default for BridgeState {
    fn default() -> Self {
        Self {
            enabled: false,
            startup_error: None,
            accepted_events: log::RingBuffer::default(),
            rejected_events: log::RingBuffer::default(),
            queue: queue::IngressQueue::new(queue::INGRESS_QUEUE_CAPACITY),
        }
    }
}

#[derive(Clone)]
pub struct BridgeDebugHandle {
    inner: Arc<Mutex<BridgeState>>,
    next_id: Arc<AtomicU64>,
}

impl BridgeDebugHandle {
    pub fn new() -> Self {
        Self {
            inner: Arc::new(Mutex::new(BridgeState::default())),
            next_id: Arc::new(AtomicU64::new(1)),
        }
    }

    pub fn snapshot(&self, sound: SoundDiagnostics) -> BridgeDiagnostics {
        self.inner
            .lock()
            .map(|state| BridgeDiagnostics {
                enabled: state.enabled,
                listen_address: LISTEN_ADDRESS.to_string(),
                queue_length: state.queue.len(),
                queue_capacity: state.queue.capacity(),
                accepted_events: state.accepted_events.latest_first(),
                rejected_events: state.rejected_events.latest_first(),
                last_accepted: state.accepted_events.last(),
                last_rejected: state.rejected_events.last(),
                sound,
                hardware_light: false,
                startup_error: state.startup_error.clone(),
            })
            .unwrap_or_default()
    }

    pub fn event_id(&self) -> String {
        format!(
            "evt_{}_{}",
            received_at(),
            self.next_id.fetch_add(1, Ordering::Relaxed)
        )
    }

    pub fn set_enabled(&self, enabled: bool) {
        if let Ok(mut state) = self.inner.lock() {
            state.enabled = enabled;
            if enabled {
                state.startup_error = None;
            }
        }
    }

    pub fn set_startup_error(&self, error: String) {
        if let Ok(mut state) = self.inner.lock() {
            state.enabled = false;
            state.startup_error = Some(error);
        }
    }

    pub fn record_accepted(&self, summary: EventSummary) {
        if let Ok(mut state) = self.inner.lock() {
            state.accepted_events.push(summary);
        }
    }

    pub fn record_rejected(&self, summary: EventSummary) {
        if let Ok(mut state) = self.inner.lock() {
            state.rejected_events.push(summary);
        }
    }

    pub fn admit_event(
        &self,
        event_id: String,
        event: protocol::AcceptedPetEvent,
    ) -> Result<queue::QueueAdmission, queue::QueueReject> {
        self.inner
            .lock()
            .map_err(|_| queue::QueueReject::Full)?
            .queue
            .admit(queue::QueuedEvent {
                event_id,
                event,
                emitted: false,
            })
    }

    pub fn mark_emitted(&self, event_id: &str) {
        if let Ok(mut state) = self.inner.lock() {
            state.queue.mark_emitted(event_id);
        }
    }
}

pub struct BridgeRuntime {
    pub debug: BridgeDebugHandle,
    shutdown: Arc<Mutex<Option<oneshot::Sender<()>>>>,
}

impl BridgeRuntime {
    pub fn shutdown(&self) {
        if let Ok(mut sender) = self.shutdown.lock() {
            if let Some(sender) = sender.take() {
                let _ = sender.send(());
            }
        }
    }
}

impl Drop for BridgeRuntime {
    fn drop(&mut self) {
        self.shutdown();
    }
}

#[derive(Serialize)]
struct TokenFile {
    token: String,
}

pub fn received_at() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    let millis = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_millis())
        .unwrap_or_default();
    millis.to_string()
}

pub fn start(app: AppHandle, sound: SoundHandle) -> Result<BridgeRuntime, String> {
    let token = load_or_create_token(&app)?;
    let debug = BridgeDebugHandle::new();
    let (shutdown_tx, shutdown_rx) = oneshot::channel::<()>();

    http::spawn_server(app, token, debug.clone(), sound, shutdown_rx);

    Ok(BridgeRuntime {
        debug,
        shutdown: Arc::new(Mutex::new(Some(shutdown_tx))),
    })
}

fn token_path(app: &AppHandle) -> Result<PathBuf, String> {
    let dir = app
        .path()
        .app_config_dir()
        .map_err(|error| error.to_string())?;
    fs::create_dir_all(&dir).map_err(|error| error.to_string())?;
    Ok(dir.join("api-token.json"))
}

fn load_or_create_token(app: &AppHandle) -> Result<String, String> {
    let path = token_path(app)?;
    if let Ok(content) = fs::read_to_string(&path) {
        if let Ok(file) = serde_json::from_str::<TokenFileRead>(&content) {
            if !file.token.trim().is_empty() {
                return Ok(file.token);
            }
        }
    }

    let token = generate_token();
    let content = serde_json::to_string_pretty(&TokenFile {
        token: token.clone(),
    })
    .map_err(|error| error.to_string())?;
    fs::write(path, content).map_err(|error| error.to_string())?;
    Ok(token)
}

#[derive(serde::Deserialize)]
struct TokenFileRead {
    token: String,
}

fn generate_token() -> String {
    use rand::{distributions::Alphanumeric, Rng};
    rand::thread_rng()
        .sample_iter(&Alphanumeric)
        .take(48)
        .map(char::from)
        .collect()
}
