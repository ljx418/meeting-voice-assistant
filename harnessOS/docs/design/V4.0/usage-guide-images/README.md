# V4.0 Usage Guide Images

This directory is reserved for the local `gpt-image-2` Garden Mode output files.

Expected PNG files:

- `01-workflow-console-overview.png`
- `02-canvas-proposal-workflow.png`
- `03-user-confirmed-editing.png`
- `04-agenttalk-handoff.png`
- `05-governance-evidence-review.png`
- `06-production-readiness-gates.png`

Generation is currently blocked until the local environment enables Garden Mode:

```bash
export ENABLE_GARDEN_IMAGEGEN=1
export OPENAI_API_KEY=your_key_here
export OPENAI_IMAGE_MODEL=gpt-image-2
```

Prompts and exact commands are recorded in:

```text
docs/design/V4.0/v4_0_project_usage_guide_image_prompts.md
```

Do not claim these PNG assets exist until the generation commands succeed.
