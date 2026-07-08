#!/usr/bin/env python3
# =============================================================================
# AGENTIC AI ENFORCED SPECIFICATION & GUIDELINES (CRITICAL)
# =============================================================================
# 1. PERSIST ALL COMMENTS: Do not remove or truncate the docs in this file.
# 2. AGENT READ-WRITE RULE: Keep this header synchronized with behavior on every
#    change (mirrors the main.tsx / index.css agentic-guide convention).
# 3. This file is INFRASTRUCTURE for the "build-time static cache" strategy. It
#    is NOT part of the 3-file app source (index.html / index.css / main.tsx).
# =============================================================================
#
# PROJECT: Options Desk — SMART build-time data fetcher
#
# WHAT IT DOES (v2 — smart, self-driving universe, no manual ticker list):
#   1. Builds a UNIVERSE of US stocks sorted DESC by market cap, pulled live from
#      the NASDAQ stock screener API (no key). Falls back to a small built-in
#      list if the screener is unreachable.
#   2. Walks the universe TOP-DOWN (largest market cap first). For each symbol:
#        - If data/{SYMBOL}.json exists AND its stored "updated" date is TODAY,
#          SKIP it (already fresh) and move to the next symbol.
#        - Otherwise fetch the full option chain via yfinance and WRITE/OVERWRITE
#          data/{SYMBOL}.json (a stale file is refreshed).
#   3. Stops when EITHER we hit the per-run budget (MAX_FETCHES) OR we detect the
#      data source is rate-limiting us (consecutive empty/error responses).
#      This way each run fetches "as much as we can" and APPENDS to the cache;
#      the next run resumes where this one left off (skipping fresh files).
#   4. Rewrites data/index.json as the manifest of ALL cached tickers.
#
# WHY THIS DESIGN:
#   - No hand-maintained ticker list (user request): the universe is discovered.
#   - Idempotent + resumable: safe to run hourly/daily from GitHub Actions; it
#     only does NEW work (missing or stale files), so it "grows" the cache.
#   - Freshness rule: same-day files are trusted; older files are re-fetched.
#
# OUTPUT SHAPE (matches the "Static cache" provider in main.tsx):
#   data/index.json        -> { "tickers": [...sorted...], "updated": ISO }
#   data/{TICKER}.json     -> { symbol, updated (ISO), underlyingPrice,
#                               expirations[], quotes[] }  (greeks null; yfinance
#                               gives IV/OI/volume/bid/ask/last, no greeks)
#
# USAGE:
#   pip install yfinance requests
#   python scripts/fetch_data.py                 # smart auto-universe run
#   MAX_FETCHES=50 python scripts/fetch_data.py  # cap how many NEW fetches
#   UNIVERSE_SIZE=500 python scripts/fetch_data.py  # how deep the ranked list is
#   MAX_EXPIRATIONS=8 python scripts/fetch_data.py  # cap expirations per ticker
#   TICKERS="AAPL MSFT" python scripts/fetch_data.py # override: only these
#
# TUNABLES (env):
#   MAX_FETCHES      default 40   NEW (non-skipped) fetches per run.
#   UNIVERSE_SIZE    default 300  how many top-market-cap symbols to consider.
#   MAX_EXPIRATIONS  default 12   expirations stored per ticker (keeps JSON small)
#   RATE_LIMIT_HITS  default 3    consecutive failures that mean "we're blocked".
#   REQUEST_SLEEP    default 0.6  seconds between fetches (be polite to Yahoo).
# =============================================================================

import json
import os
import sys
import math
import time
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance", file=sys.stderr)
    sys.exit(1)

try:
    import requests
except ImportError:
    requests = None  # only needed for the live universe; we degrade gracefully

# ---- Paths & configuration --------------------------------------------------
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
MAX_FETCHES = int(os.environ.get("MAX_FETCHES", "40"))
UNIVERSE_SIZE = int(os.environ.get("UNIVERSE_SIZE", "300"))
MAX_EXPIRATIONS = int(os.environ.get("MAX_EXPIRATIONS", "12"))
RATE_LIMIT_HITS = int(os.environ.get("RATE_LIMIT_HITS", "3"))
REQUEST_SLEEP = float(os.environ.get("REQUEST_SLEEP", "0.6"))

# Small, dependable fallback universe (already market-cap-ish ordered) used only
# if the live NASDAQ screener cannot be reached.
FALLBACK_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK.B", "AVGO",
    "JPM", "LLY", "V", "XOM", "UNH", "MA", "COST", "HD", "PG", "JNJ", "WMT",
    "NFLX", "BAC", "ORCL", "CRM", "AMD", "KO", "PEP", "TMUS", "ADBE", "CVX",
    "QQQ", "SPY", "IWM", "DIA",  # popular ETFs traders watch
]


def _num(v):
    """Coerce to a JSON-safe float or None (NaN/inf -> None)."""
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def _mid(bid, ask):
    """Mid = (bid+ask)/2 when both are positive, else None."""
    if bid is not None and ask is not None and bid > 0 and ask > 0:
        return (bid + ask) / 2.0
    return None


def _today_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


# ---- Universe discovery ------------------------------------------------------

def load_universe():
    """
    Return a list of tickers sorted DESC by market cap.
    Source: NASDAQ stock screener API (no key). Falls back to FALLBACK_UNIVERSE.
    """
    # Explicit override wins (kept for convenience / testing).
    override = os.environ.get("TICKERS")
    if override:
        return [t.upper() for t in override.replace(",", " ").split() if t.strip()]

    if requests is None:
        print("  (requests not installed; using fallback universe)")
        return FALLBACK_UNIVERSE[:UNIVERSE_SIZE]

    url = ("https://api.nasdaq.com/api/screener/stocks"
           "?tableonly=true&limit=25000&download=true")
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; OptionsDeskBot/1.0)",
        "Accept": "application/json",
    }
    try:
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        rows = r.json().get("data", {}).get("rows", []) or []

        def cap(row):
            try:
                return float(str(row.get("marketCap", "0")).replace(",", "") or 0)
            except ValueError:
                return 0.0

        # Keep real, optionable-looking tickers (drop warrants/units with odd chars).
        clean = [x for x in rows if x.get("symbol") and "^" not in x["symbol"]
                 and "/" not in x["symbol"]]
        clean.sort(key=cap, reverse=True)
        syms = [x["symbol"].upper().strip() for x in clean if cap(x) > 0]
        if syms:
            print(f"  universe: {len(syms)} symbols from NASDAQ screener "
                  f"(top: {', '.join(syms[:5])})")
            return syms[:UNIVERSE_SIZE]
    except Exception as e:
        print(f"  ! NASDAQ screener failed ({e}); using fallback universe",
              file=sys.stderr)
    return FALLBACK_UNIVERSE[:UNIVERSE_SIZE]


# ---- Per-ticker fetch -------------------------------------------------------

def _spot(ticker):
    try:
        p = ticker.fast_info.get("last_price")
        if p:
            return _num(p)
    except Exception:
        pass
    try:
        hist = ticker.history(period="1d")
        if not hist.empty:
            return _num(hist["Close"].iloc[-1])
    except Exception:
        pass
    return None


def _rows_from_frame(frame, expiration, side):
    out = []
    for _, r in frame.iterrows():
        bid = _num(r.get("bid"))
        ask = _num(r.get("ask"))
        out.append({
            "symbol": str(r.get("contractSymbol", "")),
            "expiration": expiration,
            "side": side,
            "strike": _num(r.get("strike")) or 0,
            "bid": bid,
            "ask": ask,
            "mid": _mid(bid, ask),
            "last": _num(r.get("lastPrice")),
            "volume": _num(r.get("volume")),
            "openInterest": _num(r.get("openInterest")),
            "iv": _num(r.get("impliedVolatility")),  # decimal (0.25 = 25%)
            "delta": None, "gamma": None, "theta": None, "vega": None,
        })
    return out


def fetch_ticker(symbol):
    """Fetch and normalize the full (capped) chain for one ticker.
    Returns the payload dict, or None if the ticker has no options / failed."""
    symbol = symbol.upper().strip()
    t = yf.Ticker(symbol)
    exps = list(t.options or [])
    if not exps:
        return None
    exps = exps[:MAX_EXPIRATIONS]

    quotes = []
    for exp in exps:
        try:
            ch = t.option_chain(exp)
        except Exception as e:
            print(f"      ! skip {symbol} {exp}: {e}", file=sys.stderr)
            continue
        quotes.extend(_rows_from_frame(ch.calls, exp, "call"))
        quotes.extend(_rows_from_frame(ch.puts, exp, "put"))

    if not quotes:
        return None

    return {
        "symbol": symbol,
        "updated": _now_iso(),
        "underlyingPrice": _spot(t),
        "expirations": exps,
        "quotes": quotes,
    }


# ---- Freshness check --------------------------------------------------------

def is_fresh_today(path):
    """True if the JSON file exists and its stored 'updated' date is TODAY (UTC)."""
    if not os.path.exists(path):
        return False
    try:
        with open(path) as f:
            data = json.load(f)
        updated = str(data.get("updated", ""))
        return updated[:10] == _today_iso()
    except Exception:
        return False


# ---- Main loop --------------------------------------------------------------

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    universe = load_universe()

    fetched = 0        # NEW fetches performed this run
    skipped = 0        # already-fresh files skipped
    consecutive_fail = 0

    print(f"Smart fetch: budget={MAX_FETCHES} new, universe={len(universe)}, "
          f"today={_today_iso()}")

    for sym in universe:
        if fetched >= MAX_FETCHES:
            print(f"  reached MAX_FETCHES={MAX_FETCHES}; stopping (resume next run).")
            break

        path = os.path.join(DATA_DIR, f"{sym}.json")

        # Skip files already refreshed today (idempotent, resumable).
        if is_fresh_today(path):
            skipped += 1
            continue

        # Fetch (missing OR stale -> overwrite).
        try:
            payload = fetch_ticker(sym)
        except Exception as e:
            payload = None
            print(f"  ERROR {sym}: {e}", file=sys.stderr)

        if payload is None:
            # No options for this symbol, or a failure. Treat repeated failures
            # as a possible rate-limit / block and bail out early.
            consecutive_fail += 1
            print(f"  - {sym}: no data (fail streak {consecutive_fail})")
            if consecutive_fail >= RATE_LIMIT_HITS:
                print(f"  {RATE_LIMIT_HITS} consecutive failures — assuming "
                      f"rate-limited/blocked. Stopping; will resume next run.")
                break
            continue

        consecutive_fail = 0
        with open(path, "w") as f:
            json.dump(payload, f, separators=(",", ":"))
        fetched += 1
        print(f"  + {sym}: {len(payload['quotes'])} quotes "
              f"({fetched}/{MAX_FETCHES})")
        time.sleep(REQUEST_SLEEP)  # be polite to the data source

    # Rebuild the manifest from ALL cached files on disk (not just this run).
    cached = sorted(
        f[:-5] for f in os.listdir(DATA_DIR)
        if f.endswith(".json") and f != "index.json"
    )
    with open(os.path.join(DATA_DIR, "index.json"), "w") as f:
        json.dump({"tickers": cached, "updated": _now_iso()}, f, indent=2)

    print(f"Done. new={fetched}, skipped_fresh={skipped}, "
          f"total_cached={len(cached)}")


if __name__ == "__main__":
    main()
