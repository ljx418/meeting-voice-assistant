use jsonschema::JSONSchema;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::sync::OnceLock;

const PET_EVENT_SCHEMA: &str =
    include_str!("../../../../../packages/pet-protocol/schemas/pet-event.schema.json");

const ACTIONS: &[&str] = &[
    "idle",
    "thinking",
    "running",
    "success",
    "warning",
    "error",
    "need_input",
    "sleeping",
];
const SOUNDS: &[&str] = &[
    "none",
    "success_chime",
    "warning_chime",
    "error_chime",
    "need_input_chime",
];
const LIGHT_EFFECTS: &[&str] = &[
    "none",
    "thinking_blue",
    "running_cyan",
    "success_green",
    "warning_amber",
    "error_red",
    "need_input_purple",
    "sleeping_warm_dim",
];

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct PetEventSource {
    pub id: String,
    pub kind: String,
    pub name: Option<String>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct AcceptedPetEvent {
    pub source: PetEventSource,
    pub via: String,
    pub level: String,
    pub title: Option<String>,
    pub message: Option<String>,
    pub action: Option<String>,
    pub sound: Option<String>,
    pub duration_ms: Option<u32>,
    pub hardware: Option<Value>,
    pub metadata: Option<Value>,
    pub received_at: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_instance_id: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub target_window_label: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Capabilities {
    pub levels: &'static [&'static str],
    pub actions: &'static [&'static str],
    pub sounds: SoundCapabilities,
    pub hardware: HardwareCapabilities,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct SoundCapabilities {
    pub playback: bool,
    pub accepted_ids: &'static [&'static str],
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct HardwareCapabilities {
    pub light: bool,
    pub accepted_effects: &'static [&'static str],
}

pub fn capabilities() -> Capabilities {
    Capabilities {
        levels: ACTIONS,
        actions: ACTIONS,
        sounds: SoundCapabilities {
            playback: cfg!(target_os = "macos"),
            accepted_ids: SOUNDS,
        },
        hardware: HardwareCapabilities {
            light: false,
            accepted_effects: LIGHT_EFFECTS,
        },
    }
}

pub fn validate_pet_event(value: &Value) -> Result<(), String> {
    let schema = schema()?;
    if let Err(errors) = schema.validate(value) {
        let messages = errors
            .take(3)
            .map(|error| error.to_string())
            .collect::<Vec<_>>()
            .join("; ");
        return Err(messages);
    }

    validate_whitelists(value)?;
    validate_metadata_size(value)
}

pub fn accepted_event_from_value(
    value: Value,
    received_at: String,
) -> Result<AcceptedPetEvent, String> {
    let source = value
        .get("source")
        .cloned()
        .ok_or_else(|| "source is required".to_string())?;
    let source =
        serde_json::from_value::<PetEventSource>(source).map_err(|error| error.to_string())?;

    Ok(AcceptedPetEvent {
        source,
        via: "http".to_string(),
        level: string_field(&value, "level").unwrap_or_else(|| "idle".to_string()),
        title: string_field(&value, "title"),
        message: string_field(&value, "message"),
        action: string_field(&value, "action"),
        sound: string_field(&value, "sound"),
        duration_ms: value
            .get("durationMs")
            .and_then(|duration| duration.as_u64())
            .map(|duration| duration as u32),
        hardware: value.get("hardware").cloned(),
        metadata: value.get("metadata").cloned(),
        received_at,
        target_instance_id: None,
        target_window_label: None,
    })
}

fn schema() -> Result<&'static JSONSchema, String> {
    static SCHEMA: OnceLock<Result<JSONSchema, String>> = OnceLock::new();
    SCHEMA
        .get_or_init(|| {
            let value = serde_json::from_str::<Value>(PET_EVENT_SCHEMA)
                .map_err(|error| error.to_string())?;
            JSONSchema::compile(&value).map_err(|error| error.to_string())
        })
        .as_ref()
        .map_err(|error| error.clone())
}

fn validate_whitelists(value: &Value) -> Result<(), String> {
    if let Some(action) = string_field(value, "action") {
        ensure_allowed("action", &action, ACTIONS)?;
    }
    if let Some(sound) = string_field(value, "sound") {
        ensure_allowed("sound", &sound, SOUNDS)?;
    }
    if let Some(effect) = value
        .get("hardware")
        .and_then(|hardware| hardware.get("light"))
        .and_then(|light| light.get("effect"))
        .and_then(|effect| effect.as_str())
    {
        ensure_allowed("hardware.light.effect", effect, LIGHT_EFFECTS)?;
    }
    Ok(())
}

fn ensure_allowed(field: &str, value: &str, allowed: &[&str]) -> Result<(), String> {
    if allowed.contains(&value) {
        Ok(())
    } else {
        Err(format!("{field} is not allowed"))
    }
}

fn validate_metadata_size(value: &Value) -> Result<(), String> {
    if let Some(metadata) = value.get("metadata") {
        let size = serde_json::to_vec(metadata)
            .map_err(|error| error.to_string())?
            .len();
        if size > 4096 {
            return Err("metadata exceeds 4KB".to_string());
        }
    }
    Ok(())
}

fn string_field(value: &Value, field: &str) -> Option<String> {
    value
        .get(field)
        .and_then(|value| value.as_str())
        .map(ToString::to_string)
}
