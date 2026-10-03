"""Pre-flight check: are the directory and both translators up?

Run with: make check
"""

import sys

from trustcards import config, fetch


def main() -> int:
    targets = {"📒 Directory": config.DIRECTORY_URL} | {
        f"{t.colour}●{config.RESET} {t.role.title()} translator": t.card_url
        for t in config.TRANSLATORS.values()
    }
    down = []
    for label, url in targets.items():
        try:
            fetch.get_json(url)
            print(f"✅ {label}  {url}")
        except fetch.ServerNotRunningError:
            print(f"❌ {label}  not running ({url})")
            down.append(label)
    if down:
        print(f"\n{fetch.START_SERVERS}")
    return 1 if down else 0


if __name__ == "__main__":
    sys.exit(main())
