# Real Fixtures

Source: real `data_service` smoke responses captured by `npm run smoke:release`.

- data_service commit: `c774626a`
- frontend commit baseline: `c774626a` plus RC6 working-tree updates
- date: 2026-05-19
- sanitization: path/cache/physical artifact fields are stripped by the smoke script

These fixtures represent backend-observed behavior. They must not contain local absolute paths, cache paths, artifact physical paths, sensitive filenames, or private content.

Accepted RC3/RC6 observations:

- source trace for a minimal text registry `source_id` returned 404, confirmed again in RC6 with `src_2003ad3198c69861`;
- workspace query evidence was llmwiki/sourceRef-style metadata;
- session query returned no evidence items;
- graph community with node ids and node-scoped neighbors passed.
