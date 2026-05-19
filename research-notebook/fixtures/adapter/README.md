# Adapter Fixtures

Source: synthetic adapter contract fixtures used to test frontend normalization paths that were not observed as successful backend smoke responses.

- data_service commit context: `c774626a`
- frontend commit baseline: `c774626a` plus RC5 working-tree updates
- date: 2026-05-19
- sanitization: no local absolute paths, cache paths, or physical artifact paths

These fixtures must not be reported as real backend pass cases.

Current adapter-only cases:

- `query-hit-source-registry-id.json`: tests traceable registry source id evidence mapping.
- `session-query-with-evidence.json`: tests session evidence rendering/normalization.
- `graph-community-without-node-id.json`: tests graph overview behavior when communities do not expose selectable node ids.
