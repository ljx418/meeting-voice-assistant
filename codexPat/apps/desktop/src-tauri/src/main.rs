mod bridge;
mod sound;

use serde::{Deserialize, Serialize};
use std::{
    fs,
    path::PathBuf,
    sync::{Arc, Mutex},
    time::{SystemTime, UNIX_EPOCH},
};
use tauri::{
    image::Image,
    menu::{Menu, MenuItem, PredefinedMenuItem},
    tray::TrayIconBuilder,
    AppHandle, Emitter, Manager, PhysicalPosition, PhysicalSize, WebviewUrl, WebviewWindow,
    WebviewWindowBuilder, WindowEvent,
};

const PET_WIDTH: u32 = 220;
const PET_HEIGHT: u32 = 220;
const SAFE_MARGIN: i32 = 24;
const PET_SPAWN_GAP: i32 = 24;
const DEFAULT_CAT_PROFILE_ID: &str = "default-cat";
pub(crate) const TOTAL_PET_SOFT_LIMIT: usize = 6;
pub(crate) const TOTAL_PET_HARD_LIMIT: usize = 12;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct AppSettings {
    muted: bool,
    pet_visible: bool,
    pet_x: Option<i32>,
    pet_y: Option<i32>,
    #[serde(default = "default_cat_profile_id")]
    default_cat_profile_id: String,
    #[serde(default)]
    pet_instances: Vec<PetInstance>,
}

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            muted: false,
            pet_visible: true,
            pet_x: None,
            pet_y: None,
            default_cat_profile_id: default_cat_profile_id(),
            pet_instances: Vec::new(),
        }
    }
}

fn default_cat_profile_id() -> String {
    DEFAULT_CAT_PROFILE_ID.to_string()
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub(crate) struct WindowPosition {
    pub(crate) x: i32,
    pub(crate) y: i32,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct PetInstance {
    instance_id: String,
    source_kind: String,
    source_id: String,
    display_name: String,
    window_label: String,
    #[serde(default)]
    workspace_label: Option<String>,
    workspace_hash: Option<String>,
    position: WindowPosition,
    visible: bool,
    current_state: String,
    cat_profile_id: String,
    created_at: String,
    updated_at: String,
    last_event_at: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct PetInstanceView {
    pub(crate) instance_id: String,
    pub(crate) source_kind: String,
    pub(crate) source_id: String,
    pub(crate) display_name: String,
    pub(crate) window_label: String,
    pub(crate) workspace_label: Option<String>,
    pub(crate) workspace_hash: Option<String>,
    pub(crate) position: WindowPosition,
    pub(crate) visible: bool,
    pub(crate) current_state: String,
    pub(crate) cat_profile_id: String,
    pub(crate) created_at: String,
    pub(crate) updated_at: String,
    pub(crate) last_event_at: Option<String>,
    pub(crate) is_default: bool,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct PetInstanceLimits {
    pub(crate) total_count: usize,
    pub(crate) soft_limit: usize,
    pub(crate) hard_limit: usize,
    pub(crate) over_soft_limit: bool,
    pub(crate) at_hard_limit: bool,
}

#[derive(Debug, Clone, Serialize)]
#[serde(rename_all = "camelCase")]
struct CatProfile {
    id: String,
    name: String,
    description: String,
    css_class: String,
    preview_color: String,
    built_in: bool,
}

#[derive(Clone)]
pub(crate) struct AppState {
    pub(crate) settings: Arc<Mutex<AppSettings>>,
    settings_path: PathBuf,
    pub(crate) api_debug: bridge::BridgeDebugHandle,
    pub(crate) sound: sound::SoundHandle,
}

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            let settings_path = settings_path(app.handle())?;
            let settings = read_settings(&settings_path);
            let sound = sound::SoundHandle::new(app.handle().clone(), settings.muted);
            let bridge_runtime = bridge::start(app.handle().clone(), sound.clone())?;
            let state = AppState {
                settings: Arc::new(Mutex::new(settings)),
                settings_path,
                api_debug: bridge_runtime.debug.clone(),
                sound,
            };

            app.manage(state.clone());
            app.manage(bridge_runtime);

            if let Some(window) = app.get_webview_window("main") {
                apply_initial_pet_window(app.handle(), &window, &state)?;
                install_window_persistence(window, state.clone());
            }
            restore_instance_windows(app.handle(), &state)?;

            setup_tray(app.handle(), state)?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_settings,
            set_muted,
            get_pet_position,
            get_api_debug_state,
            get_current_pet_instance,
            list_pet_instances,
            create_pet_instance,
            rename_pet_instance,
            list_cat_profiles,
            set_pet_instance_profile,
            set_pet_instance_visible,
            reset_pet_instance_position,
            detach_pet_instance
        ])
        .run(tauri::generate_context!())
        .expect("failed to run Agent Desktop Pet");
}

#[tauri::command]
fn get_settings(state: tauri::State<AppState>) -> Result<AppSettings, String> {
    state
        .settings
        .lock()
        .map(|settings| settings.clone())
        .map_err(|error| error.to_string())
}

#[tauri::command]
fn set_muted(muted: bool, state: tauri::State<AppState>) -> Result<AppSettings, String> {
    let updated = {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        settings.muted = muted;
        settings.clone()
    };
    save_settings(&state, &updated)?;
    state.sound.set_muted(updated.muted);
    Ok(updated)
}

#[tauri::command]
fn get_pet_position(app: AppHandle) -> Result<WindowPosition, String> {
    let window = app
        .get_webview_window("main")
        .ok_or_else(|| "main window not found".to_string())?;
    let position = window.outer_position().map_err(|error| error.to_string())?;
    Ok(WindowPosition {
        x: position.x,
        y: position.y,
    })
}

#[tauri::command]
fn get_api_debug_state(state: tauri::State<AppState>) -> Result<bridge::BridgeDiagnostics, String> {
    Ok(state.api_debug.snapshot(state.sound.diagnostics()))
}

#[tauri::command]
fn get_current_pet_instance(
    window: tauri::Window,
    state: tauri::State<AppState>,
) -> Result<PetInstanceView, String> {
    let label = window.label().to_string();
    let settings = state.settings.lock().map_err(|error| error.to_string())?;
    if label == "main" {
        return Ok(default_instance_view(&settings));
    }
    settings
        .pet_instances
        .iter()
        .find(|instance| instance.window_label == label)
        .map(instance_view)
        .ok_or_else(|| format!("pet instance not found for window {label}"))
}

#[tauri::command]
fn list_pet_instances(state: tauri::State<AppState>) -> Result<Vec<PetInstanceView>, String> {
    let settings = state.settings.lock().map_err(|error| error.to_string())?;
    Ok(pet_instance_views(&settings))
}

#[tauri::command]
fn create_pet_instance(
    display_name: Option<String>,
    app: AppHandle,
    state: tauri::State<AppState>,
) -> Result<PetInstanceView, String> {
    let display_name = display_name
        .map(|name| name.trim().to_string())
        .filter(|name| !name.is_empty())
        .unwrap_or_else(|| "Codex Cat".to_string());
    create_pet_instance_for_source(
        &app,
        &state,
        display_name,
        "codex".to_string(),
        "codex.local".to_string(),
        None,
        None,
    )
}

#[tauri::command]
fn rename_pet_instance(
    instance_id: String,
    display_name: String,
    app: AppHandle,
    state: tauri::State<AppState>,
) -> Result<PetInstanceView, String> {
    if !is_valid_instance_id(&instance_id) {
        return Err("instance_id_invalid".to_string());
    }
    let display_name = display_name.trim().to_string();
    validate_display_name(&display_name).map_err(|_| "display_name_invalid".to_string())?;
    let updated = {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        let instance = settings
            .pet_instances
            .iter_mut()
            .find(|instance| instance.instance_id == instance_id)
            .ok_or_else(|| "instance_not_found".to_string())?;
        instance.display_name = display_name;
        instance.updated_at = now_millis();
        let view = instance_view(instance);
        let snapshot = settings.clone();
        drop(settings);
        save_settings(&state, &snapshot)?;
        view
    };
    if let Some(window) = app.get_webview_window(&updated.window_label) {
        let _ = window.emit("pet-instance:updated", updated.clone());
    }
    Ok(updated)
}

#[tauri::command]
fn list_cat_profiles() -> Vec<CatProfile> {
    built_in_cat_profiles()
}

#[tauri::command]
fn set_pet_instance_profile(
    instance_id: String,
    cat_profile_id: String,
    app: AppHandle,
    state: tauri::State<AppState>,
) -> Result<PetInstanceView, String> {
    if !is_valid_instance_id(&instance_id) {
        return Err("instance_id_invalid".to_string());
    }
    if !is_valid_cat_profile_id(&cat_profile_id) {
        return Err("cat_profile_invalid".to_string());
    }

    if instance_id == "default" {
        let updated = {
            let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
            settings.default_cat_profile_id = cat_profile_id;
            let snapshot = settings.clone();
            drop(settings);
            save_settings(&state, &snapshot)?;
            default_instance_view(&snapshot)
        };
        if let Some(window) = app.get_webview_window("main") {
            let _ = window.emit("pet-instance:updated", updated.clone());
        }
        return Ok(updated);
    }

    let updated = {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        let instance = settings
            .pet_instances
            .iter_mut()
            .find(|instance| instance.instance_id == instance_id)
            .ok_or_else(|| "instance_not_found".to_string())?;
        instance.cat_profile_id = cat_profile_id;
        instance.updated_at = now_millis();
        let view = instance_view(instance);
        let snapshot = settings.clone();
        drop(settings);
        save_settings(&state, &snapshot)?;
        view
    };

    if let Some(window) = app.get_webview_window(&updated.window_label) {
        let _ = window.emit("pet-instance:updated", updated.clone());
    }

    Ok(updated)
}

#[tauri::command]
fn set_pet_instance_visible(
    instance_id: String,
    visible: bool,
    app: AppHandle,
    state: tauri::State<AppState>,
) -> Result<PetInstanceView, String> {
    if !is_valid_instance_id(&instance_id) {
        return Err("instance_id_invalid".to_string());
    }

    if instance_id == "default" {
        let updated = {
            let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
            settings.pet_visible = visible;
            let snapshot = settings.clone();
            drop(settings);
            save_settings(&state, &snapshot)?;
            default_instance_view(&snapshot)
        };
        if let Some(window) = app.get_webview_window("main") {
            if visible {
                window.show().map_err(|error| error.to_string())?;
            } else {
                window.hide().map_err(|error| error.to_string())?;
            }
        }
        return Ok(updated);
    }

    let (instance, slot) = {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        let index = settings
            .pet_instances
            .iter()
            .position(|instance| instance.instance_id == instance_id)
            .ok_or_else(|| "instance_not_found".to_string())?;
        let instance = settings
            .pet_instances
            .get_mut(index)
            .ok_or_else(|| "instance_not_found".to_string())?;
        instance.visible = visible;
        instance.updated_at = now_millis();
        let instance = instance.clone();
        let snapshot = settings.clone();
        drop(settings);
        save_settings(&state, &snapshot)?;
        (instance, index + 1)
    };

    if visible {
        create_or_show_instance_window(&app, &state, &instance, slot)
            .map_err(|error| error.to_string())?;
    } else if let Some(window) = app.get_webview_window(&instance.window_label) {
        window.hide().map_err(|error| error.to_string())?;
    }

    Ok(instance_view(&instance))
}

#[tauri::command]
fn reset_pet_instance_position(
    instance_id: String,
    app: AppHandle,
    state: tauri::State<AppState>,
) -> Result<PetInstanceView, String> {
    if !is_valid_instance_id(&instance_id) {
        return Err("instance_id_invalid".to_string());
    }

    let size = PhysicalSize::new(PET_WIDTH, PET_HEIGHT);
    if instance_id == "default" {
        let position = pet_spawn_position_for_slot(&app, size, 0);
        let updated = {
            let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
            settings.pet_x = Some(position.x);
            settings.pet_y = Some(position.y);
            let snapshot = settings.clone();
            drop(settings);
            save_settings(&state, &snapshot)?;
            default_instance_view(&snapshot)
        };
        if let Some(window) = app.get_webview_window("main") {
            window
                .set_position(position)
                .map_err(|error| error.to_string())?;
        }
        return Ok(updated);
    }

    let (instance, index) = {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        let index = settings
            .pet_instances
            .iter()
            .position(|instance| instance.instance_id == instance_id)
            .ok_or_else(|| "instance_not_found".to_string())?;
        let position = reset_position_for_index(&app, index + 1);
        let instance = settings
            .pet_instances
            .get_mut(index)
            .ok_or_else(|| "instance_not_found".to_string())?;
        instance.position = WindowPosition {
            x: position.x,
            y: position.y,
        };
        instance.updated_at = now_millis();
        let instance = instance.clone();
        let snapshot = settings.clone();
        drop(settings);
        save_settings(&state, &snapshot)?;
        (instance, index)
    };

    let position = reset_position_for_index(&app, index + 1);
    if let Some(window) = app.get_webview_window(&instance.window_label) {
        window
            .set_position(position)
            .map_err(|error| error.to_string())?;
    }

    Ok(instance_view(&instance))
}

#[tauri::command]
fn detach_pet_instance(
    instance_id: String,
    app: AppHandle,
    state: tauri::State<AppState>,
) -> Result<Vec<PetInstanceView>, String> {
    detach_pet_instance_by_id(&app, &state, &instance_id)?;
    list_pet_instances(state)
}

pub(crate) fn detach_pet_instance_by_id(
    app: &AppHandle,
    state: &AppState,
    instance_id: &str,
) -> Result<PetInstanceView, String> {
    if !is_valid_instance_id(&instance_id) {
        return Err("instance_id_invalid".to_string());
    }
    if instance_id == "default" {
        return Err("default_instance_cannot_detach".to_string());
    }
    let removed = {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        let Some(index) = settings
            .pet_instances
            .iter()
            .position(|instance| instance.instance_id == instance_id)
        else {
            return Err("instance_not_found".to_string());
        };
        let removed = settings.pet_instances.remove(index);
        let snapshot = settings.clone();
        drop(settings);
        save_settings(&state, &snapshot)?;
        removed
    };

    if let Some(window) = app.get_webview_window(&removed.window_label) {
        let _ = window.close();
    }

    Ok(instance_view(&removed))
}

fn settings_path(app: &AppHandle) -> tauri::Result<PathBuf> {
    let dir = app.path().app_config_dir()?;
    fs::create_dir_all(&dir)?;
    Ok(dir.join("settings.json"))
}

fn read_settings(path: &PathBuf) -> AppSettings {
    fs::read_to_string(path)
        .ok()
        .and_then(|content| serde_json::from_str::<AppSettings>(&content).ok())
        .unwrap_or_default()
}

fn save_settings(state: &AppState, settings: &AppSettings) -> Result<(), String> {
    if let Some(parent) = state.settings_path.parent() {
        fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    }
    let content = serde_json::to_string_pretty(settings).map_err(|error| error.to_string())?;
    fs::write(&state.settings_path, content).map_err(|error| error.to_string())
}

fn now_millis() -> String {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_millis().to_string())
        .unwrap_or_else(|_| "0".to_string())
}

pub(crate) fn create_pet_instance_for_source(
    app: &AppHandle,
    state: &AppState,
    display_name: String,
    source_kind: String,
    source_id: String,
    workspace_label: Option<String>,
    workspace_hash: Option<String>,
) -> Result<PetInstanceView, String> {
    validate_display_name(&display_name)?;
    validate_optional_label(workspace_label.as_deref(), "workspace label")?;
    validate_optional_workspace_hash(workspace_hash.as_deref())?;

    let count = {
        let settings = state.settings.lock().map_err(|error| error.to_string())?;
        let total_count = pet_total_count(&settings);
        if total_count >= TOTAL_PET_HARD_LIMIT {
            return Err("instance_limit_reached".to_string());
        }
        settings.pet_instances.len() + 1
    };
    let instance = new_pet_instance(
        app,
        display_name,
        count,
        source_kind,
        source_id,
        workspace_label,
        workspace_hash,
    );
    let view = instance_view(&instance);

    {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        settings.pet_instances.push(instance.clone());
        let snapshot = settings.clone();
        drop(settings);
        save_settings(state, &snapshot)?;
    }

    create_or_show_instance_window(app, state, &instance, count).map_err(|error| error.to_string())?;
    Ok(view)
}

fn validate_display_name(display_name: &str) -> Result<(), String> {
    let trimmed = display_name.trim();
    let length = trimmed.chars().count();
    if !(1..=40).contains(&length) {
        return Err("display name must be 1 to 40 characters".to_string());
    }
    if trimmed
        .chars()
        .any(|character| character.is_control() || matches!(character, '/' | '\\' | ':'))
    {
        return Err("display name contains invalid characters".to_string());
    }
    Ok(())
}

fn is_valid_instance_id(value: &str) -> bool {
    let length = value.chars().count();
    (1..=64).contains(&length)
        && !value.contains("..")
        && value.chars().all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | '-')
        })
}

fn validate_optional_label(value: Option<&str>, label: &str) -> Result<(), String> {
    let Some(value) = value else {
        return Ok(());
    };
    let value = value.trim();
    if value.chars().count() > 80 {
        return Err(format!("{label} must be at most 80 characters"));
    }
    if value
        .chars()
        .any(|character| character.is_control() || matches!(character, '/' | '\\' | ':'))
    {
        return Err(format!("{label} contains invalid characters"));
    }
    Ok(())
}

fn validate_optional_workspace_hash(value: Option<&str>) -> Result<(), String> {
    let Some(value) = value else {
        return Ok(());
    };
    let length = value.chars().count();
    if !(1..=128).contains(&length)
        || !value
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '_' | '-'))
    {
        return Err("workspace hash is invalid".to_string());
    }
    Ok(())
}

fn new_pet_instance(
    app: &AppHandle,
    display_name: String,
    index: usize,
    source_kind: String,
    source_id: String,
    workspace_label: Option<String>,
    workspace_hash: Option<String>,
) -> PetInstance {
    let prefix = if source_kind == "codex" {
        "codex"
    } else {
        "pet"
    };
    let instance_id = format!("{prefix}_{}", now_millis());
    let window_label = format!("pet-{instance_id}");
    let now = now_millis();
    let size = PhysicalSize::new(PET_WIDTH, PET_HEIGHT);
    let position = pet_spawn_position_for_slot(app, size, index);
    let cat_profile_id = profile_id_for_index(index);
    PetInstance {
        source_kind,
        source_id,
        instance_id,
        display_name,
        window_label,
        workspace_label,
        workspace_hash,
        position: WindowPosition {
            x: position.x,
            y: position.y,
        },
        visible: true,
        current_state: "idle".to_string(),
        cat_profile_id,
        created_at: now.clone(),
        updated_at: now,
        last_event_at: None,
    }
}

fn default_instance_view(settings: &AppSettings) -> PetInstanceView {
    let cat_profile_id = normalize_cat_profile_id(&settings.default_cat_profile_id);
    PetInstanceView {
        instance_id: "default".to_string(),
        source_kind: "system".to_string(),
        source_id: "default".to_string(),
        display_name: "Agent Desktop Pet".to_string(),
        window_label: "main".to_string(),
        workspace_label: None,
        workspace_hash: None,
        position: WindowPosition {
            x: settings.pet_x.unwrap_or_default(),
            y: settings.pet_y.unwrap_or_default(),
        },
        visible: settings.pet_visible,
        current_state: "idle".to_string(),
        cat_profile_id,
        created_at: "legacy".to_string(),
        updated_at: "legacy".to_string(),
        last_event_at: None,
        is_default: true,
    }
}

fn instance_view(instance: &PetInstance) -> PetInstanceView {
    PetInstanceView {
        instance_id: instance.instance_id.clone(),
        source_kind: instance.source_kind.clone(),
        source_id: instance.source_id.clone(),
        display_name: instance.display_name.clone(),
        window_label: instance.window_label.clone(),
        workspace_label: instance.workspace_label.clone(),
        workspace_hash: instance.workspace_hash.clone(),
        position: instance.position.clone(),
        visible: instance.visible,
        current_state: instance.current_state.clone(),
        cat_profile_id: normalize_cat_profile_id(&instance.cat_profile_id),
        created_at: instance.created_at.clone(),
        updated_at: instance.updated_at.clone(),
        last_event_at: instance.last_event_at.clone(),
        is_default: false,
    }
}

fn built_in_cat_profiles() -> Vec<CatProfile> {
    vec![
        CatProfile {
            id: DEFAULT_CAT_PROFILE_ID.to_string(),
            name: "默认猫".to_string(),
            description: "沉稳的灰蓝开发者猫。".to_string(),
            css_class: "cat-profile-default-cat".to_string(),
            preview_color: "#8d99a8".to_string(),
            built_in: true,
        },
        CatProfile {
            id: "black-cat".to_string(),
            name: "黑猫".to_string(),
            description: "深色毛发，亮绿色眼睛。".to_string(),
            css_class: "cat-profile-black-cat".to_string(),
            preview_color: "#263241".to_string(),
            built_in: true,
        },
        CatProfile {
            id: "orange-tabby".to_string(),
            name: "橘色虎斑".to_string(),
            description: "暖橘色毛发，带虎斑花纹。".to_string(),
            css_class: "cat-profile-orange-tabby".to_string(),
            preview_color: "#d7833f".to_string(),
            built_in: true,
        },
        CatProfile {
            id: "white-cat".to_string(),
            name: "白猫".to_string(),
            description: "浅色毛发，蓝色眼睛和浅灰耳朵。".to_string(),
            css_class: "cat-profile-white-cat".to_string(),
            preview_color: "#e8edf2".to_string(),
            built_in: true,
        },
    ]
}

fn is_valid_cat_profile_id(value: &str) -> bool {
    built_in_cat_profiles()
        .iter()
        .any(|profile| profile.id == value)
}

fn normalize_cat_profile_id(value: &str) -> String {
    if is_valid_cat_profile_id(value) {
        value.to_string()
    } else {
        DEFAULT_CAT_PROFILE_ID.to_string()
    }
}

fn profile_id_for_index(index: usize) -> String {
    let profiles = built_in_cat_profiles();
    profiles
        .get(index % profiles.len())
        .map(|profile| profile.id.clone())
        .unwrap_or_else(default_cat_profile_id)
}

pub(crate) fn pet_instance_views(settings: &AppSettings) -> Vec<PetInstanceView> {
    let mut instances = vec![default_instance_view(settings)];
    instances.extend(settings.pet_instances.iter().map(instance_view));
    instances
}

pub(crate) fn pet_instance_limits(settings: &AppSettings) -> PetInstanceLimits {
    let total_count = pet_total_count(settings);
    PetInstanceLimits {
        total_count,
        soft_limit: TOTAL_PET_SOFT_LIMIT,
        hard_limit: TOTAL_PET_HARD_LIMIT,
        over_soft_limit: total_count >= TOTAL_PET_SOFT_LIMIT,
        at_hard_limit: total_count >= TOTAL_PET_HARD_LIMIT,
    }
}

fn pet_total_count(settings: &AppSettings) -> usize {
    1 + settings.pet_instances.len()
}

pub(crate) fn pet_instance_target(
    settings: &AppSettings,
    instance_id: &str,
) -> Option<(String, String, bool)> {
    if instance_id == "default" {
        return Some((
            "default".to_string(),
            "main".to_string(),
            settings.pet_visible,
        ));
    }
    settings
        .pet_instances
        .iter()
        .find(|instance| instance.instance_id == instance_id)
        .map(|instance| {
            (
                instance.instance_id.clone(),
                instance.window_label.clone(),
                instance.visible,
            )
        })
}

pub(crate) fn update_pet_instance_runtime(
    state: &AppState,
    instance_id: &str,
    current_state: &str,
    last_event_at: &str,
) -> Result<(), String> {
    if instance_id == "default" {
        return Ok(());
    }
    let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
    let Some(instance) = settings
        .pet_instances
        .iter_mut()
        .find(|instance| instance.instance_id == instance_id)
    else {
        return Err("instance_not_found".to_string());
    };
    instance.current_state = current_state.to_string();
    instance.last_event_at = Some(last_event_at.to_string());
    instance.updated_at = now_millis();
    let snapshot = settings.clone();
    drop(settings);
    save_settings(state, &snapshot)
}

fn apply_initial_pet_window(
    app: &AppHandle,
    window: &WebviewWindow,
    state: &AppState,
) -> tauri::Result<()> {
    let settings = state
        .settings
        .lock()
        .map(|settings| settings.clone())
        .unwrap_or_default();
    let position = safe_pet_position(app, settings.pet_x, settings.pet_y);
    window.set_position(position)?;
    window.set_always_on_top(true)?;
    window.set_shadow(false)?;

    if settings.pet_visible {
        window.show()?;
        window.set_focus()?;
    }

    Ok(())
}

fn restore_instance_windows(app: &AppHandle, state: &AppState) -> tauri::Result<()> {
    let instances = state
        .settings
        .lock()
        .map(|settings| settings.pet_instances.clone())
        .unwrap_or_default();
    for (index, instance) in instances
        .iter()
        .enumerate()
        .filter(|(_, instance)| instance.visible)
    {
        create_or_show_instance_window(app, state, instance, index + 1)?;
    }
    Ok(())
}

fn create_or_show_instance_window(
    app: &AppHandle,
    state: &AppState,
    instance: &PetInstance,
    slot: usize,
) -> tauri::Result<()> {
    if let Some(window) = app.get_webview_window(&instance.window_label) {
        window.show()?;
        window.set_focus()?;
        return Ok(());
    }

    let window =
        WebviewWindowBuilder::new(app, &instance.window_label, WebviewUrl::App("/".into()))
            .title(&instance.display_name)
            .inner_size(PET_WIDTH as f64, PET_HEIGHT as f64)
            .resizable(false)
            .decorations(false)
            .transparent(true)
            .shadow(false)
            .always_on_top(true)
            .skip_taskbar(true)
            .visible(false)
            .accept_first_mouse(true)
            .build()?;

    let saved = PhysicalPosition::new(instance.position.x, instance.position.y);
    let safe = if position_is_visible(app, saved, PhysicalSize::new(PET_WIDTH, PET_HEIGHT)) {
        saved
    } else {
        pet_spawn_position_for_slot(app, PhysicalSize::new(PET_WIDTH, PET_HEIGHT), slot)
    };
    window.set_position(safe)?;
    window.set_always_on_top(true)?;
    window.set_shadow(false)?;
    window.show()?;
    install_window_persistence(window, state.clone());
    Ok(())
}

fn install_window_persistence(window: WebviewWindow, state: AppState) {
    let persistence_window = window.clone();
    let label = window.label().to_string();
    window.on_window_event(move |event| {
        if matches!(event, WindowEvent::Moved(_)) {
            if let Ok(position) = persistence_window.outer_position() {
                if let Ok(mut settings) = state.settings.lock() {
                    if label == "main" {
                        settings.pet_x = Some(position.x);
                        settings.pet_y = Some(position.y);
                    } else if let Some(instance) = settings
                        .pet_instances
                        .iter_mut()
                        .find(|instance| instance.window_label == label)
                    {
                        instance.position = WindowPosition {
                            x: position.x,
                            y: position.y,
                        };
                        instance.updated_at = now_millis();
                    }
                    let snapshot = settings.clone();
                    drop(settings);
                    let _ = save_settings(&state, &snapshot);
                }
            }
        }
    });
}

fn safe_pet_position(
    app: &AppHandle,
    saved_x: Option<i32>,
    saved_y: Option<i32>,
) -> PhysicalPosition<i32> {
    let size = PhysicalSize::new(PET_WIDTH, PET_HEIGHT);

    if let (Some(x), Some(y)) = (saved_x, saved_y) {
        let saved = PhysicalPosition::new(x, y);
        if position_is_visible(app, saved, size) {
            return saved;
        }
    }

    pet_spawn_position_for_slot(app, size, 0)
}

fn position_is_visible(
    app: &AppHandle,
    position: PhysicalPosition<i32>,
    size: PhysicalSize<u32>,
) -> bool {
    app.available_monitors()
        .map(|monitors| {
            monitors.iter().any(|monitor| {
                let origin = monitor.position();
                let monitor_size = monitor.size();
                let left = origin.x + SAFE_MARGIN;
                let top = origin.y + SAFE_MARGIN;
                let right = origin.x + monitor_size.width as i32 - size.width as i32 - SAFE_MARGIN;
                let bottom =
                    origin.y + monitor_size.height as i32 - size.height as i32 - SAFE_MARGIN;
                position.x >= left
                    && position.x <= right
                    && position.y >= top
                    && position.y <= bottom
            })
        })
        .unwrap_or(false)
}

fn pet_spawn_position_for_slot(
    app: &AppHandle,
    size: PhysicalSize<u32>,
    slot: usize,
) -> PhysicalPosition<i32> {
    if let Ok(Some(monitor)) = app.primary_monitor() {
        let origin = monitor.position();
        let monitor_size = monitor.size();
        let left = origin.x + SAFE_MARGIN;
        let top = origin.y + SAFE_MARGIN;
        let right = origin.x + monitor_size.width as i32 - size.width as i32 - SAFE_MARGIN;
        let bottom = origin.y + monitor_size.height as i32 - size.height as i32 - SAFE_MARGIN;
        let step_x = (size.width as i32 * 2 / 3).max(1) + PET_SPAWN_GAP;
        let step_y = (size.height as i32 * 3 / 4).max(1) + PET_SPAWN_GAP;
        let anchor_x =
            origin.x + monitor_size.width as i32 * 3 / 4 - size.width as i32 / 2;
        let anchor_y =
            origin.y + monitor_size.height as i32 * 2 / 3 - size.height as i32 / 2;
        let vertical_slot = if slot == 0 {
            0
        } else {
            let distance = ((slot + 1) / 2) as i32;
            if slot % 2 == 1 {
                -distance
            } else {
                distance
            }
        };
        let max_columns = ((right - left) / step_x + 1).max(1) as usize;
        for column in 0..max_columns {
            let x_direction = if column % 2 == 0 { 1 } else { -1 };
            let x_distance = ((column + 1) / 2) as i32;
            let candidate = PhysicalPosition::new(
                anchor_x + x_direction * x_distance * step_x,
                anchor_y + vertical_slot * step_y,
            );
            let clamped = PhysicalPosition::new(
                candidate.x.clamp(left, right),
                candidate.y.clamp(top, bottom),
            );
            if position_is_visible(app, clamped, size) {
                return clamped;
            }
        }
        return PhysicalPosition::new(anchor_x.clamp(left, right), anchor_y.clamp(top, bottom));
    }

    PhysicalPosition::new(SAFE_MARGIN, SAFE_MARGIN)
}

fn reset_position_for_index(app: &AppHandle, index: usize) -> PhysicalPosition<i32> {
    let size = PhysicalSize::new(PET_WIDTH, PET_HEIGHT);
    pet_spawn_position_for_slot(app, size, index)
}

fn setup_tray(app: &AppHandle, state: AppState) -> tauri::Result<()> {
    let title = MenuItem::with_id(app, "title", "Agent Desktop Pet", false, None::<&str>)?;
    let settings = MenuItem::with_id(app, "settings", "显示设置", true, None::<&str>)?;
    let mute = MenuItem::with_id(app, "mute", "静音 / 取消静音", true, None::<&str>)?;
    let visibility = MenuItem::with_id(app, "visibility", "显示 / 隐藏猫咪", true, None::<&str>)?;
    let reset_position = MenuItem::with_id(app, "reset_position", "重置位置", true, None::<&str>)?;
    let quit = MenuItem::with_id(app, "quit", "退出", true, None::<&str>)?;
    let separator_a = PredefinedMenuItem::separator(app)?;
    let separator_b = PredefinedMenuItem::separator(app)?;

    let menu = Menu::with_items(
        app,
        &[
            &title,
            &separator_a,
            &settings,
            &mute,
            &visibility,
            &reset_position,
            &separator_b,
            &quit,
        ],
    )?;

    let tray_icon = build_tray_icon();
    let tray = TrayIconBuilder::with_id("main-tray")
        .menu(&menu)
        .show_menu_on_left_click(true);
    let tray = if let Some(icon) = tray_icon {
        tray.icon(icon)
    } else {
        tray
    };

    tray.on_menu_event(move |app, event| match event.id().as_ref() {
        "settings" => {
            let _ = open_settings_window(app);
        }
        "mute" => {
            let _ = toggle_muted(&state);
        }
        "visibility" => {
            let _ = toggle_pet_visibility(app, &state);
        }
        "reset_position" => {
            let _ = reset_pet_position(app, &state);
        }
        "quit" => {
            app.state::<bridge::BridgeRuntime>().shutdown();
            app.exit(0);
        }
        _ => {}
    })
    .build(app)?;

    Ok(())
}

fn build_tray_icon() -> Option<Image<'static>> {
    let width: usize = 32;
    let height: usize = 32;
    let mut rgba = Vec::with_capacity(width * height * 4);

    for y in 0..height {
        for x in 0..width {
            let dx = x as i32 - 16;
            let dy = y as i32 - 16;
            let in_face = dx * dx + dy * dy <= 12 * 12;
            let in_left_ear = x > 5 && x < 14 && y > 2 && y < 12 && y < 18 - x;
            let in_right_ear = x > 18 && x < 27 && y > 2 && y < 12 && y < x - 12;

            if in_face || in_left_ear || in_right_ear {
                rgba.extend_from_slice(&[91, 103, 122, 255]);
            } else {
                rgba.extend_from_slice(&[0, 0, 0, 0]);
            }
        }
    }

    Some(Image::new_owned(rgba, width as u32, height as u32))
}

fn open_settings_window(app: &AppHandle) -> tauri::Result<()> {
    if let Some(window) = app.get_webview_window("settings") {
        window.show()?;
        window.set_focus()?;
        return Ok(());
    }

    WebviewWindowBuilder::new(app, "settings", WebviewUrl::App("/".into()))
        .title("Agent Desktop Pet 设置")
        .inner_size(720.0, 680.0)
        .min_inner_size(460.0, 380.0)
        .resizable(true)
        .decorations(true)
        .build()?;

    Ok(())
}

fn toggle_muted(state: &AppState) -> Result<(), String> {
    let updated = {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        settings.muted = !settings.muted;
        settings.clone()
    };
    state.sound.set_muted(updated.muted);
    save_settings(state, &updated)
}

fn toggle_pet_visibility(app: &AppHandle, state: &AppState) -> Result<(), String> {
    let window = app
        .get_webview_window("main")
        .ok_or_else(|| "main window not found".to_string())?;
    let updated = {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        settings.pet_visible = !settings.pet_visible;
        if settings.pet_visible {
            window.show().map_err(|error| error.to_string())?;
            window.set_focus().map_err(|error| error.to_string())?;
        } else {
            window.hide().map_err(|error| error.to_string())?;
        }
        settings.clone()
    };
    save_settings(state, &updated)
}

fn reset_pet_position(app: &AppHandle, state: &AppState) -> Result<(), String> {
    let window = app
        .get_webview_window("main")
        .ok_or_else(|| "main window not found".to_string())?;
    let position = pet_spawn_position_for_slot(app, PhysicalSize::new(PET_WIDTH, PET_HEIGHT), 0);
    window
        .set_position(position)
        .map_err(|error| error.to_string())?;

    let updated = {
        let mut settings = state.settings.lock().map_err(|error| error.to_string())?;
        settings.pet_x = Some(position.x);
        settings.pet_y = Some(position.y);
        settings.pet_visible = true;
        settings.clone()
    };
    window.show().map_err(|error| error.to_string())?;
    save_settings(state, &updated)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn built_in_cat_profiles_have_safe_classes() {
        let profiles = built_in_cat_profiles();
        assert!(profiles.len() >= 4);
        for profile in profiles {
            assert!(profile.built_in);
            assert!(!profile.id.contains('/'));
            assert!(!profile.id.contains('\\'));
            assert!(!profile.id.contains("://"));
            assert!(profile.css_class.starts_with("cat-profile-"));
            assert!(!profile.css_class.contains('/'));
            assert!(!profile.css_class.contains('\\'));
        }
    }

    #[test]
    fn cat_profile_validation_rejects_external_values() {
        assert!(is_valid_cat_profile_id("default-cat"));
        assert!(is_valid_cat_profile_id("black-cat"));
        assert!(!is_valid_cat_profile_id("not-found-profile"));
        assert!(!is_valid_cat_profile_id("../../x.css"));
        assert!(!is_valid_cat_profile_id("file:///tmp/cat.css"));
        assert!(!is_valid_cat_profile_id("https://example.com/cat.css"));
    }

    #[test]
    fn unknown_cat_profile_falls_back_to_default() {
        assert_eq!(normalize_cat_profile_id("black-cat"), "black-cat");
        assert_eq!(
            normalize_cat_profile_id("not-found-profile"),
            DEFAULT_CAT_PROFILE_ID
        );
    }

    #[test]
    fn pet_instance_limits_count_default_pet() {
        let settings = AppSettings::default();
        let limits = pet_instance_limits(&settings);
        assert_eq!(limits.total_count, 1);
        assert_eq!(limits.soft_limit, TOTAL_PET_SOFT_LIMIT);
        assert_eq!(limits.hard_limit, TOTAL_PET_HARD_LIMIT);
        assert!(!limits.over_soft_limit);
        assert!(!limits.at_hard_limit);
    }
}
