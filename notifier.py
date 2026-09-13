"""
Sends a nicely formatted embed to a Discord webhook whenever a
tracked product's price changes.
"""

import requests

TIMEOUT_SECONDS = 10


def send_price_change(webhook_url: str, label: str, old_price, new_price: float) -> None:
    if old_price is None:
        # First time we've ever seen this product - no "change" to report,
        # just record a quiet baseline message so the channel isn't silent.
        description = f"Started tracking **{label}** — current price: **${new_price:.2f}**"
        color = 0x5865F2  # Discord blurple
    else:
        direction = "up" if new_price > old_price else "down"
        arrow = "📈" if direction == "up" else "📉"
        color = 0xE74C3C if direction == "up" else 0x2ECC71
        description = (
            f"{arrow} **{label}** price changed\n"
            f"${old_price:.2f} → **${new_price:.2f}**"
        )

    payload = {
        "embeds": [
            {
                "title": "Monster Price Tracker",
                "description": description,
                "color": color,
            }
        ]
    }

    response = requests.post(webhook_url, json=payload, timeout=TIMEOUT_SECONDS)
    response.raise_for_status()


def send_error(webhook_url: str, message: str) -> None:
    """Optional: ping the channel if a fetch keeps failing, so you notice
    without having to SSH into the Pi and check logs."""
    payload = {
        "embeds": [
            {
                "title": "Monster Price Tracker — Error",
                "description": message,
                "color": 0xF1C40F,
            }
        ]
    }
    try:
        requests.post(webhook_url, json=payload, timeout=TIMEOUT_SECONDS)
    except requests.RequestException:
        pass  # don't let a notification failure crash the whole run
