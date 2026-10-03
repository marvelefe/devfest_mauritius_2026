# Trust, but Verify: Securing Agent-to-Agent Communication using Signed Cards

Code for the DevFest Mauritius 2026 workshop. An AI Assistant hands a private letter to a translator agent over [A2A](https://github.com/a2aproject/A2A). An attacker publishes a lookalike Agent Card and receives the letter instead. Signed cards and **pinned keys** stop it.

| Folder | What it is | Runs where |
|---|---|---|
| [`lab/`](lab/trust_but_verify_lab.ipynb) | Hands-on notebook: break a seal, forge a card, fix the check | Google Colab, no API key |
| [`demo/`](demo/) | The live demo: a Gemini Assistant, a real and a fake translator, an agent directory | Your laptop, needs a Gemini API key |

## Lab (Colab)

Open `lab/trust_but_verify_lab.ipynb` in [Google Colab](https://colab.research.google.com/) (`File → Upload notebook`, or `File → Open notebook → GitHub` once this repo is public), then run the cells top to bottom. Everything runs in memory: no servers, no API key.

## Demo (local)

**Requirements:** [uv](https://docs.astral.sh/uv/), Python 3.12, and a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

```bash
cd demo
make install                 # pinned dependencies into .venv
make keys                    # demo signing keys into keys/ (gitignored)
cp .env.example .env         # then paste your key into .env
```

Then follow the demo guide below.

## Demo guide

### 1. Start the servers (before the talk)

Open four terminals in `demo/`. Start them **in this order**, because the Assistants read the directory and the cards when they load:

| Terminal | Command | You should see |
|---|---|---|
| 1 | `make directory` | `📒 Agent directory on http://directory.localhost:9000/...` |
| 2 | `make real` | 🟢 `REAL translator on http://lalang.localhost:9001` |
| 3 | `make fake` | 🔴 `FAKE (attacker) translator on http://lalang-translator.localhost:9002` |
| 4 | `make web` | `✅` for all three servers, then `ADK Web Server started` |

`make web` runs `make check` first and refuses to start if a server is down. You can also run `make check` on its own at any time.

**Screen layout:** browser on the left at about 150% zoom. Terminals 2 (🟢) and 3 (🔴) stacked on the right. Terminal 4 somewhere you can glance at, since it prints the ⚠️ / 🛑 / ✅ lines.

### 2. Demo 1: the Assistant gets tricked

1. Open <http://127.0.0.1:8000>. It says *"Welcome to ADK! Select an agent to begin."*
2. Click **Select an app** (top left) and choose **`assistant`**.
   - Terminal 4 prints `⚠️  Using http://lalang-translator.localhost:9002/ (first listing, not checked)`.
3. Paste into **Type a message...** and press Enter:
   > Translate this letter into French: Dear Priya, your lease for the flat in Rose Hill renews on 1 November. Monthly rent: Rs 18,000. Tenant ID: MU-4471.
4. The chat shows three steps:
   - `#2 transfer_to_agent("translator")`: the Assistant hands the job off
   - `#3 assistant → translator`
   - `#4` the French translation: *"Chère Priya, votre bail…"*
5. Meanwhile 🔴 terminal 3 prints `📥 RECEIVED Translate this letter… Tenant ID: MU-4471.` **The attacker has the letter.**

Click an event to open the left panel, which shows the `assistant → translator` graph. It's handy to point at.

The translation takes about 20–50 seconds, because it's a real Gemini call on another agent. Fill the pause with the "what could have stopped this?" question.

### 3. Demo 2: the same attack, blocked

1. Click **New Session**, then switch the app dropdown to **`assistant_verified`**.
   - Terminal 4 prints:
     `🛑 Skipped http://lalang-translator.localhost:9002/: No valid signature found`
     `✅ Verified http://lalang.localhost:9001/`
2. Paste the same letter.
3. The chat looks the same, but this time 🟢 terminal 2 prints `📥 RECEIVED …` and 🔴 terminal 3 stays silent.

The 🛑 / ✅ lines appear the **first** time you select each app after starting `make web`, because that's when the Assistant loads. To show them again, restart `make web`.

### Troubleshooting

| Symptom | Fix |
|---|---|
| `Can't reach http://…:9000… Start the demo servers first` | A server isn't running. Start it, run `make check`, then pick the app again |
| Selecting an app does nothing, or the chat fails with 500 | Same cause: the servers weren't up when the app loaded. Start them, then retry |
| `503 UNAVAILABLE … high demand` in the chat | Gemini is busy. Model calls already retry up to 5 times, so just send the message again. If it keeps happening, play the recording |
| Old behaviour after changing code | Restart `make web`: ADK caches each Assistant after it first loads |

### How the code is organised

Everything lives in `demo/trustcards/`, and each piece is written once:

| Module | Job |
|---|---|
| `config.py` | Names, addresses, models, key ids: the single source of truth |
| `keys.py` | Generate and load ES256 key pairs |
| `cards.py` | Build, sign (`a2a-sdk`), and fetch Agent Cards |
| `trust.py` | The pinned verifier: only keys saved in advance, the card's `jku` ignored |
| `directory.py` | The public directory, newest listing first |
| `translator.py` | One translator for both roles: `python -m trustcards.translator real\|fake` |
| `assistant.py` | `choose_translator()`: first listing wins, or first *verified* listing wins |
| `models.py` | Gemini models with retries on 429/503 |
| `fetch.py` | HTTP GETs with a "start the servers" error message |
| `check.py` | `make check`: are all three servers up? |

`demo/agents/assistant*/agent.py` are 5-line entry points for ADK web.

```bash
make test    # pytest: signing, tampering, round-trip, selection, served card + JWKS
make lint    # ruff + black
```

### Security notes

This is a teaching demo, **not** a deployment template:

- The servers listen on loopback only (`127.0.0.1`), so nobody else on your network can reach them.
- They have **no authentication**. Don't expose them to a network as-is.
- `keys/` and `.env` are gitignored. The keys are demo keys, so regenerate them with `make keys` and never reuse them.
- The `*.localhost` names resolve to loopback on macOS and most Linux systems. If yours doesn't resolve them, add them to `/etc/hosts` pointing at `127.0.0.1`.

Built with `google-adk` 2.10.0, `a2a-sdk` 1.1.5, `gemini-3.5-flash-lite` (the Assistant) and `gemini-3.8-flash` (the translators).
