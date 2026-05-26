# V4.0 Project Usage Guide Image Prompts

Status: prepared for local `gpt-image-2` Garden Mode generation.

Garden Mode was checked with:

```bash
node /Users/Zhuanz/.agents/skills/gpt-image-2/scripts/check-mode.js --json
```

Current result at preparation time:

- `garden_mode_enabled=false`
- `has_api_key=false`
- mode is `B-or-C`

The PNG files must not be claimed as generated until Garden Mode is enabled and the generation commands succeed.

Enable local generation:

```bash
export ENABLE_GARDEN_IMAGEGEN=1
export OPENAI_API_KEY=your_key_here
export OPENAI_IMAGE_MODEL=gpt-image-2
```

Output directory:

```text
docs/design/V4.0/usage-guide-images/
```

## Image 01: Workflow Console Overview

Prompt file:

```text
docs/design/V4.0/usage-guide-prompts/01-workflow-console-overview.md
```

Target image:

```text
docs/design/V4.0/usage-guide-images/01-workflow-console-overview.png
```

Generation command:

```bash
node /Users/Zhuanz/.agents/skills/gpt-image-2/scripts/generate.js \
  --promptfile docs/design/V4.0/usage-guide-prompts/01-workflow-console-overview.md \
  --image docs/design/V4.0/usage-guide-images/01-workflow-console-overview.png \
  --size 1536x1024 \
  --quality high
```

## Image 02: Canvas Proposal Workflow

Prompt file:

```text
docs/design/V4.0/usage-guide-prompts/02-canvas-proposal-workflow.md
```

Target image:

```text
docs/design/V4.0/usage-guide-images/02-canvas-proposal-workflow.png
```

Generation command:

```bash
node /Users/Zhuanz/.agents/skills/gpt-image-2/scripts/generate.js \
  --promptfile docs/design/V4.0/usage-guide-prompts/02-canvas-proposal-workflow.md \
  --image docs/design/V4.0/usage-guide-images/02-canvas-proposal-workflow.png \
  --size 1536x1024 \
  --quality high
```

## Image 03: User Confirmed Editing

Prompt file:

```text
docs/design/V4.0/usage-guide-prompts/03-user-confirmed-editing.md
```

Target image:

```text
docs/design/V4.0/usage-guide-images/03-user-confirmed-editing.png
```

Generation command:

```bash
node /Users/Zhuanz/.agents/skills/gpt-image-2/scripts/generate.js \
  --promptfile docs/design/V4.0/usage-guide-prompts/03-user-confirmed-editing.md \
  --image docs/design/V4.0/usage-guide-images/03-user-confirmed-editing.png \
  --size 1536x1024 \
  --quality high
```

## Image 04: AgentTalk Handoff

Prompt file:

```text
docs/design/V4.0/usage-guide-prompts/04-agenttalk-handoff.md
```

Target image:

```text
docs/design/V4.0/usage-guide-images/04-agenttalk-handoff.png
```

Generation command:

```bash
node /Users/Zhuanz/.agents/skills/gpt-image-2/scripts/generate.js \
  --promptfile docs/design/V4.0/usage-guide-prompts/04-agenttalk-handoff.md \
  --image docs/design/V4.0/usage-guide-images/04-agenttalk-handoff.png \
  --size 1536x1024 \
  --quality high
```

## Image 05: Governance Evidence Review

Prompt file:

```text
docs/design/V4.0/usage-guide-prompts/05-governance-evidence-review.md
```

Target image:

```text
docs/design/V4.0/usage-guide-images/05-governance-evidence-review.png
```

Generation command:

```bash
node /Users/Zhuanz/.agents/skills/gpt-image-2/scripts/generate.js \
  --promptfile docs/design/V4.0/usage-guide-prompts/05-governance-evidence-review.md \
  --image docs/design/V4.0/usage-guide-images/05-governance-evidence-review.png \
  --size 1536x1024 \
  --quality high
```

## Image 06: Production Readiness Gates

Prompt file:

```text
docs/design/V4.0/usage-guide-prompts/06-production-readiness-gates.md
```

Target image:

```text
docs/design/V4.0/usage-guide-images/06-production-readiness-gates.png
```

Generation command:

```bash
node /Users/Zhuanz/.agents/skills/gpt-image-2/scripts/generate.js \
  --promptfile docs/design/V4.0/usage-guide-prompts/06-production-readiness-gates.md \
  --image docs/design/V4.0/usage-guide-images/06-production-readiness-gates.png \
  --size 1536x1024 \
  --quality high
```
