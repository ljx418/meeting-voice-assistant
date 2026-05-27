# Agent Desktop Pet Usage Guide Image Prompt

mode: B-or-C

target model: gpt-image-2

## Prompt

Create a polished five-panel visual usage guide for a macOS developer tool called "Agent Desktop Pet".

Format: wide horizontal infographic, 16:9, clean product documentation style, crisp vector-like UI illustration, light neutral background, subtle shadows, high readability, no tiny unreadable text.

Audience: software developers using Codex in terminal windows.

Panel 1: "Start the desktop pet"
Show a macOS menu bar app and a small friendly desktop cat near the lower corner of the screen. Include a small local health check badge: "localhost bridge OK".

Panel 2: "Launch Codex with a bound cat"
Show a terminal window running:
`petctl codex launch --name "Review Cat" -- ...`
Show an arrow from the terminal window to one specific cat. The terminal title area should read "Agent Pet: Review Cat".

Panel 3: "States follow this session"
Show the same terminal sending state events: thinking, need_input, success, error. Show the bound cat changing expression or pose for each state. Make the mapping one-to-one and clear.

Panel 4: "Two windows, two cats"
Show Terminal A bound to Cat A and Terminal B bound to Cat B. Use distinct colors and arrows. Emphasize that events do not cross-route between cats.

Panel 5: "Safety boundary"
Show a shield around localhost HTTP bridge. Include short labels only: "schema", "token", "whitelist", "rate limit", "redaction". Indicate that the agent sends structured status events only, not direct UI control.

Style requirements:
- Use a practical developer-tool visual language, not a marketing landing page.
- Avoid dark cyberpunk styling, decorative blobs, mascots overwhelming the content, or exaggerated gradients.
- Text must be large enough to read.
- Use the product name "Agent Desktop Pet" once as the header.
- Do not include secrets, local file paths, Authorization headers, or raw payloads.

Negative prompt:
No real tokens, no full local paths, no API keys, no raw JSON payload dumps, no fake "Claude Code verified" label, no "OS-level ready" claim, no Windows logo, no production release badge.
