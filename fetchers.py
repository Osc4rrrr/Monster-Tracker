"""
Price-fetching functions for Coles and Woolworths.

IMPORTANT - read this before running anything:

Neither retailer publishes an official public API, and I can't test
against coles.com.au or woolworths.com.au from where I generate this
code (they're not reachable from my sandbox). So the endpoints below
are marked as TODO placeholders rather than guessed-and-hoped-for URLs
that might quietly return the wrong thing.

To fill them in (takes about 10 minutes total), on your own computer:

  1. Open coles.com.au (or woolworths.com.au) in Chrome/Firefox.
  2. Open DevTools (F12) -> Network tab -> filter to "Fetch/XHR".
  3. Search for "Monster energy" in the site's search bar.
  4. Look through the requests that appear. One of them will be the
     product search call - click it, check the "Response" tab, and
     you'll see JSON containing the product name, price, and a
     product ID/SKU.
  5. Copy that request's URL into COLES_SEARCH_URL / WOOLWORTHS_SEARCH_URL
     below, and note the JSON key path to the price
     (e.g. response["results"][0]["pricing"]["now"]) so you can update
     `_extract_price_coles` / `_extract_price_woolworths`.
  6. Do the same on each site's store-locator / "change store" flow with
     postcode 7005 to get the numeric store ID for Sandy Bay - that ID
     usually needs to be sent as a header or cookie so the price you get
     back matches your local store rather than a default one.

Use test_fetch.py (in this folder) to iterate quickly once you've got
real values - no need to touch the Pi until it works.
"""

import requests

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# --- Coles -------------------------------------------------------------

COLES_SEARCH_URL = "TODO: fill in from DevTools, e.g. https://www.coles.com.au/api/..."


def fetch_coles_price(session: requests.Session, product_id: str, store_id: str) -> float:
    """Return the current price (as a float, e.g. 4.50) for a Coles product."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        # Coles' site typically needs a store-context cookie/header set
        # from a normal browsing session first - if you get 403s, visit
        # coles.com.au in the same session before calling the API.
    }
    params = {"productId": product_id, "storeId": store_id}
    response = session.get(COLES_SEARCH_URL, headers=headers, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    return _extract_price_coles(data)


def _extract_price_coles(data: dict) -> float:
    # TODO: adjust this path once you've seen the real response shape.
    return float(data["pricing"]["now"])


# --- Woolworths ----------------------------------------------------------

WOOLWORTHS_SEARCH_URL = "TODO: fill in from DevTools, e.g. https://www.woolworths.com.au/apis/..."


def fetch_woolworths_price(session: requests.Session, product_id: str, store_id: str) -> float:
    """Return the current price (as a float, e.g. 4.50) for a Woolworths product."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    # Woolworths' storefront generally needs a fulfillment-store cookie set
    # (from choosing a store on the site) before product prices reflect
    # your local specials - check DevTools for the cookie name.
    payload = {"ProductId": product_id, "StoreId": store_id}
    response = session.post(WOOLWORTHS_SEARCH_URL, headers=headers, json=payload, timeout=15)
    response.raise_for_status()
    data = response.json()
    return _extract_price_woolworths(data)


def _extract_price_woolworths(data: dict) -> float:
    # TODO: adjust this path once you've seen the real response shape.
    return float(data["Price"])


FETCHERS = {
    "coles": fetch_coles_price,
    "woolworths": fetch_woolworths_price,
}
