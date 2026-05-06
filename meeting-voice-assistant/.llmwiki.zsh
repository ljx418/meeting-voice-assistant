# Load this from anywhere:
#   source /absolute/path/to/.llmwiki.zsh
#
# After loading, you can run:
#   llmwiki search "query"

export LLMWIKI_REPO_DIR="${${(%):-%x}:A:h}"

function llmwiki() {
  local repo_dir python_bin fallback_python

  repo_dir="${LLMWIKI_REPO_DIR:-${PWD:A}}"
  fallback_python="$repo_dir/backend/venv312/bin/python"

  if [[ -n "$VIRTUAL_ENV" && -x "$VIRTUAL_ENV/bin/python" ]]; then
    python_bin="$VIRTUAL_ENV/bin/python"
  else
    python_bin="$fallback_python"
  fi

  if [[ ! -x "$python_bin" ]]; then
    echo "llmwiki: no usable Python interpreter found" >&2
    echo "  active venv: ${VIRTUAL_ENV:-<none>}" >&2
    echo "  fallback: $fallback_python" >&2
    return 1
  fi

  PYTHONPATH="$repo_dir/backend" "$python_bin" -m app.llmwiki "$@"
}
