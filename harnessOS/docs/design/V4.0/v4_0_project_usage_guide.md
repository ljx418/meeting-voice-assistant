# V4.0 Project Usage Guide

## Current V4.0 Status

V4.0 has reached the final audit and release gate package.

Allowed claim:

```text
V4.0 complete: governed dev/local Workflow Console and production readiness design gates ready for implementation review.
```

This means V4.0 has completed the governed dev/local Workflow Console baseline, canvas proposal workflow, AgentTalk handoff baseline, production readiness design gates, controlled executor gates, and final audit package.

Forbidden claims / No False Green: it does not mean the following are complete:

- production-ready external app support
- enterprise auth ready
- multi-tenant control plane ready
- OAuth ready
- SSO ready
- controlled executor ready
- Agent executor ready
- autonomous workflow editing ready
- complete Workflow Studio ready
- complete AgentTalkWindow ready
- full low-code canvas editing ready

## What Remains After V4.0

The remaining work is post-V4.0 implementation work, not unfinished V4.0 stage work.

1. Production auth implementation
   - OAuth / SSO / OIDC / SAML login
   - tenant mapping
   - user provisioning
   - service account lifecycle
   - production auth middleware

2. Tenant control plane implementation
   - tenant admin routes
   - workspace ownership enforcement
   - resource ownership enforcement
   - tenant audit ownership

3. Token lifecycle runtime
   - token issuance
   - expiration
   - rotation
   - revocation
   - emergency revoke
   - token audit

4. Production secret management
   - secret manager integration
   - connector credential isolation
   - signed URL policy
   - secret access audit

5. Observability and audit platform
   - metrics
   - alerting
   - trace retention
   - operation evidence retention
   - governance review export
   - incident timeline
   - SLO / SLA tracking

6. External app production onboarding
   - app registration
   - domain verification
   - origin allowlist review
   - quota / rate limits
   - abuse detection
   - customer offboarding
   - data export / deletion

7. Controlled executor implementation
   - policy matrix enforcement
   - approval gate runtime
   - sandbox boundary runtime
   - rollback descriptor
   - kill switch
   - executor evidence creation

8. Agent executor implementation
   - only after controlled executor implementation gates pass
   - Agent must not bypass user confirmation or approval gates

9. Complete Workflow Studio
   - full low-code editing
   - persistent layout descriptor
   - broader node and edge editing
   - production-grade UX hardening

10. Complete AgentTalkWindow
    - richer conversation lifecycle
    - production evidence navigation
    - final executor-aware UX only after executor gates

## Usage Flow

1. Open Workflow Console.
2. Review workflow board, status, stations, artifacts, quality, approval, and context.
3. Use canvas and Inspector as proposal surfaces only.
4. Generate patch proposals from Node / Edge / Inspector intent.
5. Review PatchDiffDTO and PatchQueueDTO.
6. Apply, reject, or publish only through user-confirmed operation panels.
7. Use AgentTalk for explain, summarize, suggest patch, and handoff.
8. Review governance evidence in read-only panels.
9. Treat EventBridge as refresh trigger only.
10. Do not trust event payload as runtime truth.

## Generated Guide Image Set

The planned local `gpt-image-2` image set is:

| Image | Purpose | Path |
|---|---|---|
| Workflow Console Overview | Product usage overview | `docs/design/V4.0/usage-guide-images/01-workflow-console-overview.png` |
| Canvas Proposal Workflow | Canvas proposal boundary | `docs/design/V4.0/usage-guide-images/02-canvas-proposal-workflow.png` |
| User Confirmed Editing | Governed apply/reject/publish | `docs/design/V4.0/usage-guide-images/03-user-confirmed-editing.png` |
| AgentTalk Handoff | Agent suggestion and panel handoff | `docs/design/V4.0/usage-guide-images/04-agenttalk-handoff.png` |
| Governance Evidence Review | Read-only evidence review | `docs/design/V4.0/usage-guide-images/05-governance-evidence-review.png` |
| Production Readiness Gates | Post-V4.0 design gate boundary | `docs/design/V4.0/usage-guide-images/06-production-readiness-gates.png` |

Prompt and generation commands are recorded in:

```text
docs/design/V4.0/v4_0_project_usage_guide_image_prompts.md
```

## Image Generation Status

At preparation time, local `gpt-image-2` Garden Mode is not enabled:

- `ENABLE_GARDEN_IMAGEGEN` is unset
- `OPENAI_API_KEY` is not visible to the process

The image prompts are ready and local target paths are fixed. PNG generation must be run only after Garden Mode is enabled.
