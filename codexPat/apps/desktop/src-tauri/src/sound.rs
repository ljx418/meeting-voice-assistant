use serde::Serialize;
use std::{
    path::PathBuf,
    process::Command,
    sync::{Arc, Mutex},
    time::{Duration, Instant, SystemTime, UNIX_EPOCH},
};
use tauri::{AppHandle, Manager};

use crate::bridge::protocol::AcceptedPetEvent;

pub const SOUND_COOLDOWN_MS: u64 = 1200;
const SUCCESS_COOLDOWN_MS: u64 = 1500;
const WARNING_COOLDOWN_MS: u64 = 2500;
const ERROR_COOLDOWN_MS: u64 = 3000;
const NEED_INPUT_COOLDOWN_MS: u64 = 5000;

pub const ACCEPTED_SOUND_IDS: &[&str] = &[
    "none",
    "success_chime",
    "warning_chime",
    "error_chime",
    "need_input_chime",
];

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct SoundDiagnostics {
    pub playback_available: bool,
    pub muted: bool,
    pub cooldown_ms: u64,
    pub accepted_ids: &'static [&'static str],
    pub last_decision: Option<SoundDecision>,
}

impl Default for SoundDiagnostics {
    fn default() -> Self {
        Self {
            playback_available: cfg!(target_os = "macos"),
            muted: false,
            cooldown_ms: SOUND_COOLDOWN_MS,
            accepted_ids: ACCEPTED_SOUND_IDS,
            last_decision: None,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct SoundDecision {
    pub sound: String,
    pub played: bool,
    pub reason: SoundDecisionReason,
    pub decided_at: String,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum SoundDecisionReason {
    Played,
    Muted,
    Cooldown,
    HiddenTarget,
    LevelSilent,
    SoundNone,
    PlaybackUnavailable,
    PlaybackFailed,
}

#[derive(Clone)]
pub struct SoundHandle {
    inner: Arc<Mutex<SoundState>>,
}

struct SoundState {
    app: AppHandle,
    muted: bool,
    last_played_at: Option<Instant>,
    last_played_sound: Option<String>,
    last_decision: Option<SoundDecision>,
}

impl SoundHandle {
    pub fn new(app: AppHandle, muted: bool) -> Self {
        Self {
            inner: Arc::new(Mutex::new(SoundState {
                app,
                muted,
                last_played_at: None,
                last_played_sound: None,
                last_decision: None,
            })),
        }
    }

    pub fn set_muted(&self, muted: bool) {
        if let Ok(mut state) = self.inner.lock() {
            state.muted = muted;
        }
    }

    pub fn diagnostics(&self) -> SoundDiagnostics {
        self.inner
            .lock()
            .map(|state| SoundDiagnostics {
                playback_available: cfg!(target_os = "macos"),
                muted: state.muted,
                cooldown_ms: SOUND_COOLDOWN_MS,
                accepted_ids: ACCEPTED_SOUND_IDS,
                last_decision: state.last_decision.clone(),
            })
            .unwrap_or_default()
    }

    pub fn handle_event(&self, event: &AcceptedPetEvent, target_visible: bool) {
        if let Ok(mut state) = self.inner.lock() {
            state.handle_event(event, target_visible);
        }
    }
}

impl SoundState {
    fn handle_event(&mut self, event: &AcceptedPetEvent, target_visible: bool) {
        let Some(sound_id) = requested_sound_id(event) else {
            self.record("none", false, SoundDecisionReason::LevelSilent);
            return;
        };

        if sound_id == "none" {
            self.record(sound_id, false, SoundDecisionReason::SoundNone);
            return;
        }

        if self.muted {
            self.record(sound_id, false, SoundDecisionReason::Muted);
            return;
        }

        if !target_visible {
            self.record(sound_id, false, SoundDecisionReason::HiddenTarget);
            return;
        }

        if !cfg!(target_os = "macos") {
            self.record(sound_id, false, SoundDecisionReason::PlaybackUnavailable);
            return;
        }

        if self.in_cooldown(sound_id, cooldown_for_level(&event.level)) {
            self.record(sound_id, false, SoundDecisionReason::Cooldown);
            return;
        }

        match sound_path(&self.app, sound_id).and_then(play_sound) {
            Ok(()) => {
                self.last_played_at = Some(Instant::now());
                self.last_played_sound = Some(sound_id.to_string());
                self.record(sound_id, true, SoundDecisionReason::Played);
            }
            Err(_) => self.record(sound_id, false, SoundDecisionReason::PlaybackFailed),
        }
    }

    fn in_cooldown(&self, sound_id: &str, cooldown_ms: u64) -> bool {
        if self.last_played_sound.as_deref() != Some(sound_id) {
            return false;
        }
        self.last_played_at
            .map(|instant| instant.elapsed() < Duration::from_millis(cooldown_ms))
            .unwrap_or(false)
    }

    fn record(&mut self, sound: &str, played: bool, reason: SoundDecisionReason) {
        self.last_decision = Some(SoundDecision {
            sound: sound.to_string(),
            played,
            reason,
            decided_at: now_millis(),
        });
    }
}

fn requested_sound_id(event: &AcceptedPetEvent) -> Option<&'static str> {
    match event.level.as_str() {
        "success" => Some(sound_or_default(event.sound.as_deref(), "success_chime")),
        "warning" => Some(sound_or_default(event.sound.as_deref(), "warning_chime")),
        "error" => Some(sound_or_default(event.sound.as_deref(), "error_chime")),
        "need_input" => Some(sound_or_default(event.sound.as_deref(), "need_input_chime")),
        "idle" | "thinking" | "running" | "sleeping" => None,
        _ => None,
    }
}

fn sound_or_default(requested: Option<&str>, default: &'static str) -> &'static str {
    match requested {
        Some("none") => "none",
        Some("success_chime") => "success_chime",
        Some("warning_chime") => "warning_chime",
        Some("error_chime") => "error_chime",
        Some("need_input_chime") => "need_input_chime",
        _ => default,
    }
}

fn cooldown_for_level(level: &str) -> u64 {
    match level {
        "success" => SUCCESS_COOLDOWN_MS,
        "warning" => WARNING_COOLDOWN_MS,
        "error" => ERROR_COOLDOWN_MS,
        "need_input" => NEED_INPUT_COOLDOWN_MS,
        _ => SOUND_COOLDOWN_MS,
    }
}

fn sound_path(app: &AppHandle, sound_id: &str) -> Result<PathBuf, String> {
    let file_name = match sound_id {
        "success_chime" => "success_chime.wav",
        "warning_chime" => "warning_chime.wav",
        "error_chime" => "error_chime.wav",
        "need_input_chime" => "need_input_chime.wav",
        _ => return Err("sound id has no bundled resource".to_string()),
    };

    app.path()
        .resolve(
            format!("assets/sounds/{file_name}"),
            tauri::path::BaseDirectory::Resource,
        )
        .map_err(|error| error.to_string())
}

#[cfg(target_os = "macos")]
fn play_sound(path: PathBuf) -> Result<(), String> {
    Command::new("afplay")
        .arg(path)
        .spawn()
        .map(|_| ())
        .map_err(|error| error.to_string())
}

#[cfg(not(target_os = "macos"))]
fn play_sound(_path: PathBuf) -> Result<(), String> {
    Err("sound playback is only enabled for macOS-first MVP".to_string())
}

fn now_millis() -> String {
    let millis = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_millis())
        .unwrap_or_default();
    millis.to_string()
}
