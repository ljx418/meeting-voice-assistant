# V2.10 Phase 74 Multi-Project Evidence Report Plan

## Objective

Generate a readable V2.10 pattern evidence report for humans and agents across multiple projects.

## Report Sections

Required JSON/HTML sections:

1. Executive summary.
2. Adapter attempt matrix.
3. Accepted pattern evidence.
4. Binding and definition lookup map.
5. Manifest/runtime candidate status.
6. Pattern blocker table.
7. Project generality review.
8. Recommended next extraction improvements.

Mermaid views:

- `architecture_pattern_adapter_map.mmd`
- `architecture_binding_flow.mmd`

## Development Plan

Render report only from persisted V2.10 artifacts.

HTML rules:

- escape all text;
- sanitize links;
- no inline untrusted HTML;
- no absolute path;
- no raw command output.

Mermaid rules:

- node id generated from artifact id;
- label escaped;
- every node resolves to persisted artifact;
- no source path beyond repo-relative label.

## Acceptance Plan

Required repos:

- `data_service`;
- `HarnessOS`;
- generic fixture or third real repo.

Assertions:

- report shows adapter attempts even when accepted evidence is zero;
- report distinguishes accepted evidence and blockers;
- HarnessOS report explains whether blocker improved;
- generic fixture demonstrates at least three adapter types;
- HTML/Mermaid do not introduce unpersisted facts;
- report public payload has no absolute paths or secrets.

False-green rejection:

- report claims accepted evidence not present in artifact;
- report hides blockers;
- report is manually authored instead of generated from persisted artifacts;
- HarnessOS-only labels appear as generic adapter names.
