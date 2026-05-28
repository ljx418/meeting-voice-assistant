# V5.8 Local Asset Import Final Acceptance Report

status: passed-scoped

date: 2026-05-28

## Scope

V5.8 adds a manifest-validated local import path for standardized personalized sprite or GLTF packs.

## Accepted Format

- `schemaVersion: "5.8"`.
- `rendererKind: "sprite" | "gltf"`.
- all eight core actions are required.
- asset file names must be safe basenames.
- imported files are copied into app-managed storage.

## Rejections

- missing core action.
- remote URL.
- absolute local path.
- path traversal.
- script or executable-like field.
- missing asset file.

## Allowed Claim

```text
V5.8 manifest-validated local personalized asset import passed for tested sprite and GLTF asset packs.
```

## Forbidden

```text
remote asset loading ready
asset marketplace ready
provider integration verified
production signed release ready
```
