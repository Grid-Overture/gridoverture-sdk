.PHONY: help install lint test generate sync-openapi

help:
	@echo "install       uv sync: the SDK, editable, and the dev tools"
	@echo "lint          ruff check and ruff format --check"
	@echo "test          pytest, the generated client's check included"
	@echo "generate      regenerates src/gridoverture/_generated from spec/"
	@echo "sync-openapi  REF=<platform tag> FILE=<openapi.public.json>: vendors it and regenerates"

install:
	uv sync

lint:
	uv run ruff check .
	uv run ruff format --check .

test:
	uv run pytest

generate:
	uv run python scripts/generate.py

sync-openapi:
	$(if $(and $(REF),$(FILE)),,$(error usage: make sync-openapi REF=v0.2.0 FILE=path/to/openapi.public.json))
	uv run python scripts/sync_openapi.py $(REF) $(FILE)
