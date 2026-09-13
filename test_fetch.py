"""
Run this on your own laptop/desktop (not the Pi) while you're figuring
out the real Coles/Woolworths endpoints. Quick feedback loop:

    python test_fetch.py coles <product_id> <store_id>
    python test_fetch.py woolworths <product_id> <store_id>

Prints the raw JSON response so you can see exactly what came back,
which is the fastest way to fix _extract_price_* in fetchers.py.
"""

import json
import sys

import requests

from fetchers import FETCHERS, USER_AGENT


def main() -> None:
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    retailer, product_id, store_id = sys.argv[1], sys.argv[2], sys.argv[3]
    if retailer not in FETCHERS:
        print(f"Unknown retailer '{retailer}'. Use 'coles' or 'woolworths'.")
        sys.exit(1)

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    try:
        price = FETCHERS[retailer](session, product_id, store_id)
        print(f"Success! Extracted price: ${price:.2f}")
    except Exception as exc:  # noqa: BLE001 - this is a debug tool
        print(f"Fetch/parse failed: {exc}")
        print("\nTip: temporarily add `print(response.text)` in the fetcher")
        print("function to see the raw response and fix the JSON path.")


if __name__ == "__main__":
    main()
