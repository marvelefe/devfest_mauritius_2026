.PHONY: install keys directory real fake check web test lint format

RUN := uv run
RUN_ENV := uv run --env-file .env

install:          ## Install pinned dependencies into .venv
	uv sync

keys:             ## Generate demo signing keys into keys/ (once)
	$(RUN) python -m trustcards.keys

directory:        ## Terminal 1: the public agent directory (:9000)
	$(RUN) python -m trustcards.directory

real: .env        ## Terminal 2: the real Lalang translator (:9001)
	$(RUN_ENV) python -m trustcards.translator real

fake: .env        ## Terminal 3: the attacker's lookalike (:9002)
	$(RUN_ENV) python -m trustcards.translator fake

check:            ## Are the directory and both translators up?
	$(RUN) python -m trustcards.check

web: .env check   ## Terminal 4: ADK web UI (:8000). Refuses to start until servers are up
	$(RUN_ENV) adk web --host 127.0.0.1 --port 8000 --log_level warning agents

test:
	$(RUN) pytest -q

lint:
	$(RUN) ruff check .
	$(RUN) black --check .

format:
	$(RUN) ruff check --fix .
	$(RUN) black .

.env:
	@echo "Missing .env: run 'cp .env.example .env' and add your Gemini API key." && exit 1
