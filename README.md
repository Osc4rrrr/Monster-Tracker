# Monster Price Tracker

Tracks the price of a Monster single can and 4-pack at Coles Sandy Bay
and Woolworths Sandy Bay, and posts to a Discord webhook whenever a
price changes.

## Files

- `config.json` — webhook URL, store IDs, product IDs, settings
- `fetchers.py` — gets the current price from Coles/Woolworths
- `storage.py` — remembers the last price seen (SQLite, `prices.db`)
- `notifier.py` — sends the Discord message
- `main.py` — runs one check cycle across all products (this is what gets scheduled)
- `test_fetch.py` — quick local test harness for a single fetch, without touching the Pi
- `systemd/` — service + timer to run `main.py` every hour on the Pi

## Setup

### 1. Find your real API endpoints (do this on your own computer first)

`fetchers.py` currently has placeholder endpoints marked `TODO` — I
couldn't verify Coles/Woolworths' actual private API from where I
generated this code. Follow the instructions at the top of
`fetchers.py` (open DevTools → Network tab → search for "Monster" on
each site) to find:

- The real search/product-detail request URL for each retailer
- The JSON path to the price in the response
- The store ID for Sandy Bay on each site (needed so prices reflect
  your local specials, not a random default store)

Use `test_fetch.py` to iterate quickly:

```bash
python test_fetch.py coles <product_id> <store_id>
python test_fetch.py woolworths <product_id> <store_id>
```

Once both print a sane price, fill in `config.json` with the real
store IDs and product IDs.

### 2. Set your Discord webhook

Paste your webhook URL into `discord_webhook_url` in `config.json`.

### 3. Test locally

```bash
pip install requests
python main.py
```

Check `tracker.log` and your Discord channel — you should see a
"started tracking" message for each of the 4 products the first time
it runs.

### 4. Deploy to the Pi

```bash
scp -r monster-tracker/ pi@<your-pi-ip>:/home/pi/
ssh pi@<your-pi-ip>
cd monster-tracker
python3 -m venv venv
./venv/bin/pip install requests
```

Then install the scheduler:

```bash
sudo cp systemd/monster-tracker.service systemd/monster-tracker.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now monster-tracker.timer

# Run once immediately to confirm it works:
sudo systemctl start monster-tracker.service
journalctl -u monster-tracker.service -n 50
```

## If you start getting blocked

Both retailers use bot-protection, so if requests start returning
403s / CAPTCHAs after a while:

- Increase `check_interval_minutes` and edit the timer's `OnCalendar`
  accordingly (e.g. `OnCalendar=*-*-* *:00/3:00` for every 3 hours)
- Make sure `fetchers.py` is reusing a `requests.Session()` so cookies
  persist between requests (already done in `main.py`)
- As a last resort, the same approach can be swapped to drive a real
  headless browser (Playwright/Selenium) instead of raw `requests` —
  heavier on the Pi Zero 2 W's 512MB RAM, but more resilient. Happy to
  build that version if the lightweight one gets blocked.

## Notes

- `notify_on` in `config.json` can be `"any"` (default) or `"drops"`
  if you only want to hear about price decreases.
- The single-can and 4-pack prices are tracked per one representative
  flavour per store — if that flavour is ever priced differently from
  the rest of the range, this won't catch it, but should track pack
  and can pricing accurately in general.
"# Monster-Tracker" 
