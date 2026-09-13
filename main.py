"""
Main entry point - runs ONE check cycle across every product in
config.json, compares against the last known price, and notifies
Discord on any change. Meant to be invoked periodically by a systemd
timer or cron (see systemd/ for a ready-made unit).
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

import storage
from fetchers import FETCHERS
from notifier import send_error, send_price_change

CONFIG_PATH = Path(__file__).parent / "config.json"
LOG_PATH = Path(__file__).parent / "tracker.log"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def load_config() -> dict:
    with open(CONFIG_PATH) as f:
        return json.load(f)


def run_once(config: dict) -> None:
    storage.init_db()
    session = requests.Session()
    webhook_url = config["discord_webhook_url"]
    notify_on = config.get("notify_on", "any")  # "any" or "drops"

    for product in config["products"]:
        retailer = product["retailer"]
        store_id = config["stores"][retailer]["store_id"]
        fetch = FETCHERS[retailer]

        try:
            new_price = fetch(session, product["product_id"], store_id)
        except Exception as exc:  # noqa: BLE001
            log.warning("Fetch failed for %s: %s", product["label"], exc)
            continue

        old_price = storage.get_last_price(product["id"])
        checked_at = datetime.now(timezone.utc).isoformat()
        storage.upsert_price(product["id"], product["label"], new_price, checked_at)

        log.info("%s: $%.2f (was %s)", product["label"], new_price, old_price)

        if old_price is None:
            send_price_change(webhook_url, product["label"], None, new_price)
            continue

        if new_price == old_price:
            continue

        if notify_on == "drops" and new_price >= old_price:
            continue  # only care about drops, and this went up

        send_price_change(webhook_url, product["label"], old_price, new_price)


def main() -> None:
    config = load_config()
    try:
        run_once(config)
    except Exception as exc:  # noqa: BLE001
        log.exception("Run failed")
        send_error(config["discord_webhook_url"], f"Tracker run failed: {exc}")


if __name__ == "__main__":
    main()
