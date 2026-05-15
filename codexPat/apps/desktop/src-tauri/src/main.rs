mod bridge;
mod sound;

use serde::{Deserialize, Serialize};
use std::{
    fs,
    path::PathBuf,
    sync::{Arc, Mutex},
};
use tauri::{
    image::Image,
    menu::{Menu, MenuItem, PredefinedMenuItem},
    tray::TrayIconBuilder,
    AppHandle, Manager, PhysicalPosition, PhysicalSize, WebviewUrl, WebviewWindow,
    WebviewWindowBuilder, WindowEvent,
};

const PET_WIDTH: u32 = 220;
const PET_HEIGHT: u32 = 220;
const SAFE_MARGIN: i32 = 24;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct AppSettings {
    muted: bool,
    pet_visible: bool,
    pet_x: Option<i32>,
    pet_y: Option<i32>,
}

impl Default for AppSettings {
    fn default() -> Self {
        Self {
            muted: false,
            pet_visible: true,
            pet_x: None,
            pet_y: None,
        }
    }
}

#[derive(Debug, Clone, Serialize)]
struct WindowPosition {
    x: i32,
    y: i32,
}

#[derive(Clone)]
struct AppState {
    settings: Arc<Mutex<AppSettings>>,
    settings_path: PathBuf,
    api_debug: bridge::BridgeDebugHandle,
    sound: sound::SoundHandle,
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

            setup_tray(app.handle(), state)?;
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            get_settings,
            set_muted,
            get_pet_position,
            get_api_debug_state
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

fn install_window_persistence(window: WebviewWindow, state: AppState) {
    let persistence_window = window.clone();
    window.on_window_event(move |event| {
        if matches!(event, WindowEvent::Moved(_)) {
            if let Ok(position) = persistence_window.outer_position() {
                if let Ok(mut settings) = state.settings.lock() {
                    settings.pet_x = Some(position.x);
                    settings.pet_y = Some(position.y);
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

    primary_safe_position(app, size)
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

fn primary_safe_position(app: &AppHandle, size: PhysicalSize<u32>) -> PhysicalPosition<i32> {
    if let Ok(Some(monitor)) = app.primary_monitor() {
        let origin = monitor.position();
        let monitor_size = monitor.size();
        return PhysicalPosition::new(
            origin.x + monitor_size.width as i32 - size.width as i32 - SAFE_MARGIN,
            origin.y + monitor_size.height as i32 - size.height as i32 - SAFE_MARGIN,
        );
    }

    PhysicalPosition::new(SAFE_MARGIN, SAFE_MARGIN)
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
        .title("Agent Desktop Pet Settings")
        .inner_size(520.0, 460.0)
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
    let position = primary_safe_position(app, PhysicalSize::new(PET_WIDTH, PET_HEIGHT));
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
