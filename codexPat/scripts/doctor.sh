#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0

section() {
  printf "\n== %s ==\n" "$1"
}

ok() {
  printf "OK   %s\n" "$1"
}

warn() {
  printf "WARN %s\n" "$1"
}

fail() {
  printf "FAIL %s\n" "$1"
  FAILED=1
}

need_cmd() {
  if command -v "$1" >/dev/null 2>&1; then
    ok "$1: $($1 --version 2>/dev/null | head -n 1)"
  else
    fail "$1 is not installed or not on PATH"
  fi
}

section "Project"
ok "root: $ROOT_DIR"

section "Node / pnpm"
need_cmd node
need_cmd pnpm
if command -v pnpm >/dev/null 2>&1; then
  REGISTRY="$(pnpm config get registry 2>/dev/null || true)"
  ok "pnpm registry: ${REGISTRY:-unknown}"
fi

section "Rust / Cargo"
need_cmd rustc
need_cmd cargo
if command -v rustup >/dev/null 2>&1; then
  ok "rustup: $(rustup --version 2>/dev/null | head -n 1)"
else
  warn "rustup is not installed; rust-toolchain.toml will not auto-install toolchains"
fi

section "macOS Native Toolchain"
if [[ "$(uname -s)" == "Darwin" ]]; then
  if xcode-select -p >/dev/null 2>&1; then
    ok "xcode-select: $(xcode-select -p)"
  else
    fail "Xcode Command Line Tools are missing; run: xcode-select --install"
  fi
  need_cmd clang
else
  warn "not macOS; skip Xcode Command Line Tools check"
fi

section "Tauri CLI"
if (cd "$ROOT_DIR" && pnpm --filter desktop tauri --version >/tmp/agent-desktop-pet-tauri-version 2>&1); then
  ok "$(cat /tmp/agent-desktop-pet-tauri-version | tail -n 1)"
else
  warn "Tauri CLI is unavailable until JS dependencies are installed"
fi

section "Network"
for URL in \
  "https://registry.npmjs.org/typescript" \
  "https://index.crates.io/config.json" \
  "https://sh.rustup.rs"
do
  if command -v curl >/dev/null 2>&1 && curl -I --connect-timeout 5 "$URL" >/dev/null 2>&1; then
    ok "$URL"
  else
    warn "cannot reach $URL"
  fi
done

section "Local Dev Server"
if command -v node >/dev/null 2>&1; then
  if node -e "require('net').createServer().listen(1420,'127.0.0.1',function(){this.close(()=>process.exit(0))}).on('error',e=>{console.error(e.message); process.exit(1)})" >/tmp/agent-desktop-pet-port-check 2>&1; then
    ok "127.0.0.1:1420 can be used by Vite"
  else
    warn "cannot listen on 127.0.0.1:1420: $(cat /tmp/agent-desktop-pet-port-check)"
  fi
else
  warn "node missing; skip local dev server port check"
fi

section "Workspace Artifacts"
if [[ -d "$ROOT_DIR/node_modules" || -d "$ROOT_DIR/apps/desktop/node_modules" ]]; then
  ok "node_modules present"
else
  warn "node_modules missing; run: pnpm install"
fi

if [[ -f "$ROOT_DIR/pnpm-lock.yaml" ]]; then
  ok "pnpm-lock.yaml present"
else
  warn "pnpm-lock.yaml missing; run pnpm install after registry works"
fi

if [[ -f "$ROOT_DIR/apps/desktop/src-tauri/Cargo.lock" ]]; then
  ok "Cargo.lock present"
else
  warn "Cargo.lock missing; run cargo check after crates.io access works"
fi

section "Result"
if [[ "$FAILED" -eq 0 ]]; then
  ok "doctor completed with no hard failures"
else
  fail "doctor found hard failures"
fi

exit "$FAILED"
