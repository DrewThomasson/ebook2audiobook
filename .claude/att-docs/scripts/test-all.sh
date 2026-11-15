#!/usr/bin/env bash
# Runs every test file in the repository, then the static checks.
#
#   bash scripts/test-all.sh                run the tests, then the static checks
#   bash scripts/test-all.sh --tests-only   run only the tests
#   bash scripts/test-all.sh --checks-only  run only the static checks
#
# A test file is *.test.mjs (node --test), *_test.py (python3) or *_test.sh (bash).
# node_modules, .git and .claude/worktrees are skipped. A failing file does not stop
# the run; the script prints one line per file and a summary, and exits 1 if anything
# failed.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"

run_tests=1
run_checks=1
case "${1:-}" in
  '') ;;
  --tests-only) run_checks=0 ;;
  --checks-only) run_tests=0 ;;
  *) echo "usage: $0 [--tests-only | --checks-only]" >&2; exit 2 ;;
esac

export PYTHONDONTWRITEBYTECODE=1
passed=0
failed=0
failed_names=()

run_one() {
  local kind="$1" file="$2" log status
  log="$(mktemp)"
  status=0
  # stdin is /dev/null: the loop below feeds the file list on stdin, and a test that
  # reads stdin would swallow the rest of the list.
  case "$kind" in
    node) node --test "$file" >"$log" 2>&1 </dev/null || status=$? ;;
    python) python3 "$file" >"$log" 2>&1 </dev/null || status=$? ;;
    bash) bash "$file" >"$log" 2>&1 </dev/null || status=$? ;;
  esac
  if [ "$status" -eq 0 ]; then
    echo "PASS  $file"
    passed=$((passed + 1))
  else
    echo "FAIL  $file (exit $status)"
    # A long log puts its failures above the tail, so they are listed first.
    grep -E '^(FAIL|not ok)' "$log" | sed 's/^/      /' | head -n 20 || true
    sed 's/^/      /' "$log" | tail -n 40
    failed=$((failed + 1))
    failed_names+=("$file")
  fi
  rm -f "$log"
}

find_tests() {
  find . \( -name node_modules -o -path ./.git -o -path ./.claude/worktrees \) -prune -o \
    -type f -name "$1" -print | sed 's|^\./||' | sort
}

if [ "$run_tests" -eq 1 ]; then
  echo "== Tests"
  while IFS= read -r f; do run_one node "$f"; done < <(find_tests '*.test.mjs')
  while IFS= read -r f; do run_one python "$f"; done < <(find_tests '*_test.py')
  while IFS= read -r f; do run_one bash "$f"; done < <(find_tests '*_test.sh')
  echo
  echo "Tests: $passed passed, $failed failed"
fi

if [ "$run_checks" -eq 1 ]; then
  echo
  echo "== Static checks"
  if python3 -I scripts/validate.py; then
    echo "Static checks: passed"
  else
    echo "Static checks: failed"
    failed=$((failed + 1))
    failed_names+=("static checks")
  fi
  echo
  echo "== Skill tool names"
  if python3 -I scripts/bridge-tools/skill_tools.py; then
    echo "Skill tool names: passed"
  else
    echo "Skill tool names: failed"
    failed=$((failed + 1))
    failed_names+=("skill tool names")
  fi
fi

echo
if [ "$failed" -gt 0 ]; then
  echo "FAILED:"
  printf '  %s\n' "${failed_names[@]}"
  exit 1
fi
echo "All passed"
