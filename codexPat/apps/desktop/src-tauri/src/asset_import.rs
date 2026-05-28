use serde::{Deserialize, Serialize};
use serde_json::Value;
use std::{
    collections::hash_map::DefaultHasher,
    fs,
    hash::{Hash, Hasher},
    path::{Path, PathBuf},
    time::{SystemTime, UNIX_EPOCH},
};
use tauri::{AppHandle, Manager};

const CORE_ACTIONS: [&str; 8] = [
    "idle",
    "thinking",
    "running",
    "success",
    "warning",
    "error",
    "need_input",
    "sleeping",
];
const MAX_PACK_BYTES: u64 = 50 * 1024 * 1024;
const MAX_ASSET_BYTES: u64 = 25 * 1024 * 1024;
const MAX_GLTF_MESHES: usize = 32;
const MAX_GLTF_MATERIALS: usize = 64;
const MAX_GLTF_TEXTURES: usize = 64;
const MAX_GLTF_ANIMATIONS: usize = 32;
const GLB_JSON_CHUNK: u32 = 0x4e4f_534a;

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct PersonalizedAssetPackView {
    pub(crate) pack_id: String,
    pub(crate) display_name: String,
    pub(crate) renderer_kind: String,
    pub(crate) copied_asset_ids: Vec<String>,
    pub(crate) manifest_hash: String,
    pub(crate) created_at: String,
    pub(crate) active_instances: Vec<String>,
    pub(crate) validation_status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(crate) struct PersonalizedAssetImportResult {
    pub(crate) pack_id: String,
    pub(crate) display_name: String,
    pub(crate) renderer_kind: String,
    pub(crate) copied_asset_ids: Vec<String>,
    pub(crate) manifest_hash: String,
    pub(crate) app_managed_storage: bool,
    pub(crate) validation_status: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ImportedPackRecord {
    pack_id: String,
    display_name: String,
    renderer_kind: String,
    copied_asset_ids: Vec<String>,
    manifest_hash: String,
    created_at: String,
    #[serde(default)]
    active_instances: Vec<String>,
}

#[derive(Debug, Default, Serialize, Deserialize)]
struct AssetStore {
    #[serde(default)]
    packs: Vec<ImportedPackRecord>,
}

pub(crate) fn list_personalized_asset_packs(
    app: &AppHandle,
) -> Result<Vec<PersonalizedAssetPackView>, String> {
    let store = read_store(&store_path(app)?);
    Ok(store.packs.iter().map(pack_view).collect())
}

pub(crate) fn import_personalized_asset_pack(
    app: &AppHandle,
    manifest_path: String,
    display_name: Option<String>,
) -> Result<PersonalizedAssetImportResult, String> {
    import_pack_with_paths(
        PathBuf::from(manifest_path),
        display_name,
        store_path(app)?,
        storage_root(app)?,
    )
}

fn import_pack_with_paths(
    manifest_path: PathBuf,
    display_name: Option<String>,
    store_path: PathBuf,
    storage_root: PathBuf,
) -> Result<PersonalizedAssetImportResult, String> {
    let manifest_path = manifest_path
        .canonicalize()
        .map_err(|_| "asset_manifest_not_found".to_string())?;
    let manifest_dir = manifest_path
        .parent()
        .ok_or_else(|| "asset_manifest_not_found".to_string())?
        .to_path_buf();
    let raw_manifest = fs::read_to_string(&manifest_path)
        .map_err(|_| "asset_manifest_not_found".to_string())?;
    let manifest: Value = serde_json::from_str(&raw_manifest)
        .map_err(|_| "asset_manifest_invalid_json".to_string())?;
    validate_manifest(&manifest)?;

    let pack_id = string_field(&manifest, "packId")?;
    let renderer_kind = string_field(&manifest, "rendererKind")?;
    let display_name = sanitize_display_name(
        display_name
            .as_deref()
            .or_else(|| manifest.get("displayName").and_then(Value::as_str))
            .unwrap_or(pack_id),
        pack_id,
    );
    let assets = manifest
        .get("assets")
        .and_then(Value::as_object)
        .ok_or_else(|| "asset_manifest_invalid".to_string())?;

    let mut copied_asset_ids = Vec::new();
    let target_dir = storage_root.join(pack_id);
    let temp_dir = storage_root.join(format!("{pack_id}.importing"));
    let _ = fs::remove_dir_all(&temp_dir);
    fs::create_dir_all(&temp_dir).map_err(|_| "asset_import_copy_failed".to_string())?;

    let copy_result = (|| {
        let mut total_bytes = raw_manifest.len() as u64;
        for (asset_id, asset) in assets {
            let file_name = asset
                .get("fileName")
                .and_then(Value::as_str)
                .ok_or_else(|| "asset_file_invalid".to_string())?;
            let source = manifest_dir.join(file_name);
            reject_symlink(&source)?;
            let metadata = fs::metadata(&source).map_err(|_| "asset_file_not_found".to_string())?;
            if !metadata.is_file() {
                return Err("asset_file_not_found".to_string());
            }
            if metadata.len() > MAX_ASSET_BYTES {
                return Err("asset_pack_too_large".to_string());
            }
            total_bytes = total_bytes.saturating_add(metadata.len());
            if total_bytes > MAX_PACK_BYTES {
                return Err("asset_pack_too_large".to_string());
            }
            if renderer_kind == "gltf" {
                scan_gltf_asset(&source)?;
            }
            fs::copy(&source, temp_dir.join(file_name))
                .map_err(|_| "asset_import_copy_failed".to_string())?;
            copied_asset_ids.push(asset_id.clone());
        }
        fs::write(temp_dir.join("manifest.json"), &raw_manifest)
            .map_err(|_| "asset_import_copy_failed".to_string())?;
        Ok::<(), String>(())
    })();

    if let Err(error) = copy_result {
        let _ = fs::remove_dir_all(&temp_dir);
        return Err(error);
    }

    fs::create_dir_all(&storage_root).map_err(|_| "asset_import_copy_failed".to_string())?;
    let backup_dir = storage_root.join(format!("{pack_id}.previous"));
    let _ = fs::remove_dir_all(&backup_dir);
    if target_dir.exists() {
        fs::rename(&target_dir, &backup_dir).map_err(|_| "asset_import_copy_failed".to_string())?;
    }
    if let Err(_error) = fs::rename(&temp_dir, &target_dir) {
        let _ = fs::remove_dir_all(&temp_dir);
        if backup_dir.exists() {
            let _ = fs::rename(&backup_dir, &target_dir);
        }
        return Err("asset_import_copy_failed".to_string());
    }
    let _ = fs::remove_dir_all(&backup_dir);

    let mut store = read_store(&store_path);
    let previous_active = store
        .packs
        .iter()
        .find(|pack| pack.pack_id == pack_id)
        .map(|pack| pack.active_instances.clone())
        .unwrap_or_default();
    let record = ImportedPackRecord {
        pack_id: pack_id.to_string(),
        display_name,
        renderer_kind: renderer_kind.to_string(),
        copied_asset_ids: copied_asset_ids.clone(),
        manifest_hash: stable_hash(&raw_manifest),
        created_at: now_millis(),
        active_instances: previous_active,
    };
    store.packs.retain(|pack| pack.pack_id != pack_id);
    store.packs.push(record.clone());
    write_store(&store_path, &store)?;

    Ok(PersonalizedAssetImportResult {
        pack_id: record.pack_id,
        display_name: record.display_name,
        renderer_kind: record.renderer_kind,
        copied_asset_ids,
        manifest_hash: record.manifest_hash,
        app_managed_storage: true,
        validation_status: "valid".to_string(),
    })
}

fn validate_manifest(manifest: &Value) -> Result<(), String> {
    if scan_forbidden(manifest) {
        return Err("asset_manifest_forbidden_content".to_string());
    }
    if manifest.get("schemaVersion").and_then(Value::as_str) != Some("5.8") {
        return Err("asset_manifest_schema_invalid".to_string());
    }
    let pack_id = string_field(manifest, "packId")?;
    if !is_safe_id(pack_id) {
        return Err("asset_pack_invalid".to_string());
    }
    let display_name = string_field(manifest, "displayName")?;
    if !is_safe_text(display_name) {
        return Err("asset_display_name_invalid".to_string());
    }
    let renderer_kind = string_field(manifest, "rendererKind")?;
    if renderer_kind != "sprite" && renderer_kind != "gltf" {
        return Err("asset_renderer_invalid".to_string());
    }
    if !manifest.get("license").is_some_and(Value::is_object) {
        return Err("asset_license_missing".to_string());
    }
    let assets = manifest
        .get("assets")
        .and_then(Value::as_object)
        .ok_or_else(|| "asset_manifest_invalid".to_string())?;
    let actions = manifest
        .get("actions")
        .and_then(Value::as_object)
        .ok_or_else(|| "asset_manifest_invalid".to_string())?;

    for action in CORE_ACTIONS {
        let action_entry = actions
            .get(action)
            .and_then(Value::as_object)
            .ok_or_else(|| "core_action_missing".to_string())?;
        let asset_id = action_entry
            .get("assetId")
            .and_then(Value::as_str)
            .ok_or_else(|| "core_action_missing".to_string())?;
        if !assets.contains_key(asset_id) {
            return Err("asset_missing".to_string());
        }
    }

    for (asset_id, asset) in assets {
        if !is_safe_id(asset_id) {
            return Err("asset_manifest_invalid".to_string());
        }
        let Some(file_name) = asset.get("fileName").and_then(Value::as_str) else {
            return Err("asset_file_invalid".to_string());
        };
        if !is_safe_file_name(file_name, renderer_kind) {
            return Err("asset_file_invalid".to_string());
        }
    }
    Ok(())
}

fn scan_gltf_asset(path: &Path) -> Result<(), String> {
    let bytes = fs::read(path).map_err(|_| "asset_file_not_found".to_string())?;
    let json = if path.extension().and_then(|value| value.to_str()) == Some("gltf") {
        serde_json::from_slice::<Value>(&bytes)
            .map_err(|_| "gltf_external_resource_rejected".to_string())?
    } else {
        parse_glb_json_chunk(&bytes)?
    };
    scan_gltf_json(&json)
}

fn parse_glb_json_chunk(bytes: &[u8]) -> Result<Value, String> {
    if bytes.len() < 20 || &bytes[0..4] != b"glTF" {
        return Err("gltf_external_resource_rejected".to_string());
    }
    let version = u32::from_le_bytes([bytes[4], bytes[5], bytes[6], bytes[7]]);
    let total_length = u32::from_le_bytes([bytes[8], bytes[9], bytes[10], bytes[11]]) as usize;
    if version != 2 || total_length != bytes.len() {
        return Err("gltf_external_resource_rejected".to_string());
    }
    let chunk_length = u32::from_le_bytes([bytes[12], bytes[13], bytes[14], bytes[15]]) as usize;
    let chunk_type = u32::from_le_bytes([bytes[16], bytes[17], bytes[18], bytes[19]]);
    if chunk_type != GLB_JSON_CHUNK || bytes.len() < 20 + chunk_length {
        return Err("gltf_external_resource_rejected".to_string());
    }
    serde_json::from_slice::<Value>(&bytes[20..20 + chunk_length])
        .map_err(|_| "gltf_external_resource_rejected".to_string())
}

fn scan_gltf_json(json: &Value) -> Result<(), String> {
    reject_gltf_uris(json)?;
    if array_len(json, "meshes") > MAX_GLTF_MESHES
        || array_len(json, "materials") > MAX_GLTF_MATERIALS
        || array_len(json, "textures") > MAX_GLTF_TEXTURES
        || array_len(json, "animations") > MAX_GLTF_ANIMATIONS
    {
        return Err("asset_pack_too_large".to_string());
    }
    if let Some(required) = json.get("extensionsRequired").and_then(Value::as_array) {
        if !required.is_empty() {
            return Err("gltf_required_extension_rejected".to_string());
        }
    }
    if let Some(animations) = json.get("animations").and_then(Value::as_array) {
        for animation in animations {
            let Some(name) = animation.get("name").and_then(Value::as_str) else {
                return Err("gltf_external_resource_rejected".to_string());
            };
            if !CORE_ACTIONS.contains(&name) {
                return Err("gltf_external_resource_rejected".to_string());
            }
        }
    }
    Ok(())
}

fn reject_gltf_uris(value: &Value) -> Result<(), String> {
    match value {
        Value::String(text) => {
            let lower = text.to_ascii_lowercase();
            if lower.contains("://")
                || lower.starts_with("data:")
                || lower.starts_with("javascript:")
                || lower.contains("..")
                || lower.starts_with('/')
                || lower.contains("\\")
            {
                return Err("gltf_external_resource_rejected".to_string());
            }
            Ok(())
        }
        Value::Array(items) => {
            for item in items {
                reject_gltf_uris(item)?;
            }
            Ok(())
        }
        Value::Object(fields) => {
            for (key, nested) in fields {
                if key == "uri" {
                    if nested.as_str().is_some_and(|uri| !uri.is_empty()) {
                        return Err("gltf_external_resource_rejected".to_string());
                    }
                }
                reject_gltf_uris(nested)?;
            }
            Ok(())
        }
        _ => Ok(()),
    }
}

fn reject_symlink(path: &Path) -> Result<(), String> {
    let metadata = fs::symlink_metadata(path).map_err(|_| "asset_file_not_found".to_string())?;
    if metadata.file_type().is_symlink() {
        return Err("asset_symlink_rejected".to_string());
    }
    Ok(())
}

fn store_path(app: &AppHandle) -> Result<PathBuf, String> {
    Ok(app_data_root(app)?.join("personalized-assets.json"))
}

fn storage_root(app: &AppHandle) -> Result<PathBuf, String> {
    Ok(app_data_root(app)?.join("asset-packs"))
}

fn app_data_root(app: &AppHandle) -> Result<PathBuf, String> {
    if cfg!(target_os = "macos") {
        if let Ok(home) = std::env::var("HOME") {
            return Ok(PathBuf::from(home)
                .join("Library")
                .join("Application Support")
                .join("agent-desktop-pet"));
        }
    }
    Ok(app
        .path()
        .app_data_dir()
        .map_err(|_| "asset_store_unavailable".to_string())?)
}

fn read_store(path: &Path) -> AssetStore {
    fs::read_to_string(path)
        .ok()
        .and_then(|content| serde_json::from_str::<AssetStore>(&content).ok())
        .unwrap_or_default()
}

fn write_store(path: &Path, store: &AssetStore) -> Result<(), String> {
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|_| "asset_import_copy_failed".to_string())?;
    }
    let content = serde_json::to_string_pretty(store).map_err(|_| "asset_import_copy_failed".to_string())?;
    fs::write(path, content).map_err(|_| "asset_import_copy_failed".to_string())
}

fn pack_view(pack: &ImportedPackRecord) -> PersonalizedAssetPackView {
    PersonalizedAssetPackView {
        pack_id: pack.pack_id.clone(),
        display_name: pack.display_name.clone(),
        renderer_kind: pack.renderer_kind.clone(),
        copied_asset_ids: pack.copied_asset_ids.clone(),
        manifest_hash: pack.manifest_hash.clone(),
        created_at: pack.created_at.clone(),
        active_instances: pack.active_instances.clone(),
        validation_status: "valid".to_string(),
    }
}

fn string_field<'a>(manifest: &'a Value, field: &str) -> Result<&'a str, String> {
    manifest
        .get(field)
        .and_then(Value::as_str)
        .ok_or_else(|| "asset_manifest_invalid".to_string())
}

fn is_safe_id(value: &str) -> bool {
    (1..=64).contains(&value.len())
        && value
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | '-'))
}

fn is_safe_text(value: &str) -> bool {
    (1..=160).contains(&value.chars().count())
        && !value.chars().any(|character| character.is_control())
}

fn is_safe_file_name(file_name: &str, renderer_kind: &str) -> bool {
    if !(1..=96).contains(&file_name.len()) {
        return false;
    }
    if !file_name
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | '-'))
    {
        return false;
    }
    if renderer_kind == "sprite" {
        return file_name.to_ascii_lowercase().ends_with(".png");
    }
    file_name.to_ascii_lowercase().ends_with(".glb")
        || file_name.to_ascii_lowercase().ends_with(".gltf")
}

fn scan_forbidden(value: &Value) -> bool {
    match value {
        Value::String(text) => {
            let lower = text.to_ascii_lowercase();
            lower.contains("://")
                || lower.contains("file://")
                || lower.contains("javascript:")
                || lower.contains("..")
                || lower.contains("/users/")
                || lower.contains("/private/")
                || lower.contains("/volumes/")
                || lower.contains("\\")
                || lower.ends_with(".sh")
                || lower.ends_with(".js")
                || lower.ends_with(".mjs")
                || lower.ends_with(".command")
        }
        Value::Array(items) => items.iter().any(scan_forbidden),
        Value::Object(fields) => fields.iter().any(|(key, nested)| {
            let key = key.to_ascii_lowercase();
            key.contains("raw")
                || key.contains("payload")
                || key.contains("prompt")
                || key.contains("photo")
                || key.contains("path")
                || key.contains("token")
                || key.contains("authorization")
                || key.contains("workspace")
                || key.contains("config")
                || key.contains("transcript")
                || scan_forbidden(nested)
        }),
        _ => false,
    }
}

fn sanitize_display_name(value: &str, fallback: &str) -> String {
    let sanitized = value
        .chars()
        .filter(|character| !character.is_control())
        .collect::<String>()
        .split_whitespace()
        .collect::<Vec<_>>()
        .join(" ");
    if sanitized.is_empty() || sanitized.chars().count() > 80 {
        fallback.to_string()
    } else {
        sanitized
    }
}

fn stable_hash(value: &str) -> String {
    let mut hasher = DefaultHasher::new();
    value.hash(&mut hasher);
    format!("{:016x}", hasher.finish())
}

fn now_millis() -> String {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_millis().to_string())
        .unwrap_or_else(|_| "0".to_string())
}

fn array_len(json: &Value, key: &str) -> usize {
    json.get(key)
        .and_then(Value::as_array)
        .map(|items| items.len())
        .unwrap_or_default()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn imports_valid_sprite_pack_and_replaces_duplicate() {
        let root = temp_root("sprite");
        let pack = root.join("pack");
        fs::create_dir_all(&pack).unwrap();
        for action in CORE_ACTIONS {
            fs::write(pack.join(format!("{action}.png")), "png").unwrap();
        }
        fs::write(pack.join("manifest.json"), manifest_json("sprite", "png")).unwrap();
        let store = root.join("store.json");
        let storage = root.join("managed");

        let first = import_pack_with_paths(
            pack.join("manifest.json"),
            None,
            store.clone(),
            storage.clone(),
        )
        .unwrap();
        let second = import_pack_with_paths(
            pack.join("manifest.json"),
            Some("Mochi Replacement".to_string()),
            store.clone(),
            storage,
        )
        .unwrap();

        assert_eq!(first.pack_id, "mochi-sprite");
        assert_eq!(second.display_name, "Mochi Replacement");
        assert_eq!(read_store(&store).packs.len(), 1);
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn rejects_forbidden_manifest_and_missing_core_action() {
        let root = temp_root("bad");
        let pack = root.join("pack");
        fs::create_dir_all(&pack).unwrap();
        let mut manifest: Value = serde_json::from_str(&manifest_json("sprite", "png")).unwrap();
        manifest["actions"]["error"] = Value::Null;
        fs::write(pack.join("manifest.json"), serde_json::to_string(&manifest).unwrap()).unwrap();
        let result = import_pack_with_paths(
            pack.join("manifest.json"),
            None,
            root.join("store.json"),
            root.join("managed"),
        );
        assert_eq!(result.unwrap_err(), "core_action_missing");

        manifest["actions"]["error"] = serde_json::json!({ "assetId": "error", "loop": false, "priority": "urgent" });
        manifest["assets"]["idle"]["fileName"] = Value::String("../idle.png".to_string());
        fs::write(pack.join("manifest.json"), serde_json::to_string(&manifest).unwrap()).unwrap();
        let result = import_pack_with_paths(
            pack.join("manifest.json"),
            None,
            root.join("store.json"),
            root.join("managed"),
        );
        assert_eq!(result.unwrap_err(), "asset_manifest_forbidden_content");
        let _ = fs::remove_dir_all(root);
    }

    #[test]
    fn rejects_gltf_external_uri() {
        let root = temp_root("gltf");
        let pack = root.join("pack");
        fs::create_dir_all(&pack).unwrap();
        for action in CORE_ACTIONS {
            fs::write(pack.join(format!("{action}.gltf")), r#"{"asset":{"version":"2.0"},"buffers":[{"uri":"external.bin"}],"animations":[{"name":"idle"}]}"#).unwrap();
        }
        fs::write(pack.join("manifest.json"), manifest_json("gltf", "gltf")).unwrap();
        let result = import_pack_with_paths(
            pack.join("manifest.json"),
            None,
            root.join("store.json"),
            root.join("managed"),
        );
        assert_eq!(result.unwrap_err(), "gltf_external_resource_rejected");
        let _ = fs::remove_dir_all(root);
    }

    fn manifest_json(renderer_kind: &str, extension: &str) -> String {
        let mut assets = serde_json::Map::new();
        let mut actions = serde_json::Map::new();
        for action in CORE_ACTIONS {
            assets.insert(
                action.to_string(),
                serde_json::json!({ "assetId": action, "kind": renderer_kind, "fileName": format!("{action}.{extension}") }),
            );
            actions.insert(
                action.to_string(),
                serde_json::json!({ "assetId": action, "loop": matches!(action, "idle" | "thinking" | "running" | "sleeping"), "priority": "base" }),
            );
        }
        serde_json::json!({
            "schemaVersion": "5.8",
            "packId": format!("mochi-{renderer_kind}"),
            "displayName": "Mochi",
            "rendererKind": renderer_kind,
            "license": { "type": "user-generated", "attribution": "test" },
            "assets": assets,
            "actions": actions
        })
        .to_string()
    }

    fn temp_root(name: &str) -> PathBuf {
        let root = std::env::temp_dir().join(format!("adp-v5-{}-{}", name, now_millis()));
        fs::create_dir_all(&root).unwrap();
        root
    }
}
