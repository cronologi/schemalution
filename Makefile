.DEFAULT_GOAL := help

SHELL := /bin/sh

PYTHON := $(shell command -v python3 || command -v python)
UV ?= uv
UV_EXTRAS ?= dev

.PHONY: help check-uv setup venv lock sync lint format format-check typecheck test ci build list-packages clean

help:
	@printf "Targets:\n"
	@printf "  check-uv       Ensure uv is installed\n"
	@printf "  setup          Ensure uv is installed and deps are synced\n"
	@printf "  venv           Create .venv with uv\n"
	@printf "  lock           Create/refresh uv.lock\n"
	@printf "  sync           Sync deps (defaults to extra: %s)\n" "$(UV_EXTRAS)"
	@printf "  lint           Run ruff check\n"
	@printf "  format         Run ruff format + import fixes\n"
	@printf "  format-check   Check formatting without writing\n"
	@printf "  typecheck      Run pyright\n"
	@printf "  test           Run pytest\n"
	@printf "  ci             Lint + format-check + typecheck + test\n"
	@printf "  build          Build all packages (or PKG=...)\n"
	@printf "  list-packages  List package directories\n"
	@printf "  clean          Remove local caches and build artifacts\n"

check-uv:
	@if [ -z "$(PYTHON)" ]; then \
		echo "Python not found on PATH. Set PYTHON=... and retry." >&2; \
		exit 1; \
	fi
	$(PYTHON) scripts/ensure_uv.py

setup: check-uv sync

venv: check-uv
	$(UV) venv

lock: setup
	$(UV) lock

sync: check-uv
	$(UV) sync --all-packages --extra $(UV_EXTRAS)

lint: setup
	$(UV) run ruff check .

format: setup
	$(UV) run ruff format .
	$(UV) run ruff check . --fix

format-check: setup
	$(UV) run ruff format --check .

typecheck: setup
	$(UV) run pyright

test: setup
	$(UV) run pytest

ci: lint format-check typecheck test

build: setup
	@set -e; \
	if [ -n "$(PKG)" ]; then \
		if [ -d "$(PKG)" ]; then \
			target="$(PKG)"; \
		elif [ -d "packages/$(PKG)" ]; then \
			target="packages/$(PKG)"; \
		else \
			echo "Unknown package: $(PKG)" >&2; \
			exit 1; \
		fi; \
		$(UV) build "$$target"; \
	else \
		$(UV) build --all-packages; \
	fi

list-packages:
	@$(PYTHON) -c "from pathlib import Path; print('\n'.join(str(p) for p in sorted(Path('packages').glob('*')) if p.is_dir()))"

clean:
	@$(PYTHON) -c "from pathlib import Path; import shutil; roots=['.venv','.ruff_cache','.pytest_cache','.mypy_cache','dist']; [shutil.rmtree(r, ignore_errors=True) for r in roots]; [shutil.rmtree(p, ignore_errors=True) for p in Path('packages').glob('*/dist')]"
