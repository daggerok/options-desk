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
# WHAT IT DOES (v4 — missing-first then oldest-first rotation, per-ticker index):
#   1. Builds a UNIVERSE of US stocks (NASDAQ / NYSE / NYSE American / NYSE Arca)
#      sorted DESC by market cap, pulled live from the NASDAQ screener (no key).
#      Filters to the Microcap floor (>= $10M) so it walks the tiers
#      Mega(176B+) -> Large(36B+) -> Mid(6B+) -> Small(2B+) -> Micro(10M+).
#      Falls back to a small built-in list if the screener is unreachable.
#   2. Builds a WORK QUEUE in two phases (this is the v4 change — see below):
#        PHASE 1 (COVERAGE): every universe symbol that has NO cached file yet,
#          in market-cap order (Mega -> Micro). The #1 goal is to get data for
#          ALL possible tickers FIRST, resuming DOWN the list where the previous
#          run stopped — NOT re-looping the top-cap names over and over.
#        PHASE 2 (REFRESH): once nothing is missing, refresh EXISTING files that
#          are STALE (per the working-day rules), OLDEST-UPDATED FIRST, so the
#          cache rotates evenly and the least-fresh data is always updated next.
#      Files that are still FRESH today are skipped in both phases.
#   3. Fetches the full option chain via yfinance and WRITES/OVERWRITES
#      data/{SYMBOL}.json. Stops when EITHER we hit the per-run budget
#      (MAX_FETCHES) OR the source appears to rate-limit us (a streak of
#      empty/error responses). Each run does NEW work; the next run resumes.
#   4. Rewrites data/index.json as a per-ticker manifest that records EACH
#      ticker's own `updated` timestamp (see OUTPUT SHAPE) so freshness is
#      visible without opening every file. It is regenerated from the files on
#      disk (each file's real `updated`), so unchanged tickers keep their old
#      timestamp — the manifest no longer churns a single global `updated`.
#
# FRESHNESS RULES (see _file_is_fresh): a cached file is SKIPPED when...
#   * it was updated TODAY (any day); OR
#   * TODAY is NOT a trading day (weekend/holiday) AND it was updated on the LAST
#     trading day (or later) — that's the freshest data that exists.
#   ...and it is RE-FETCHED (stale) when TODAY is a trading day (Mon-Fri, not a
#   holiday) and the file is from an earlier day. So across a week the cache ends
#   up fully refreshed, and yesterday's files get updated today.
#
# WHY THIS DESIGN:
#   - No hand-maintained ticker list (user request): the universe is discovered.
#   - COVERAGE-FIRST, then ROTATING REFRESH: the previous version re-walked the
#     universe top-down every run, so if it never got past the mega-caps it kept
#     re-fetching the SAME first tickers and never reached the rest. v4 fixes that
#     by doing all MISSING tickers first (so every ticker eventually gets cached),
#     then cycling the OLDEST existing files so refreshes spread across the whole
#     cache instead of piling on the top names.
#   - Idempotent + resumable: safe to run many times/day from GitHub Actions.
#
# OUTPUT SHAPE (matches the "Static cache" provider in main.tsx):
#   data/index.json        -> { "files": { "<TICKER>": "<updated ISO>", ... },
#                               "count": N, "generated": ISO }
#                             (v4: per-ticker `updated` map. The app derives the
#                             ticker list from sorted keys of `files`. "generated"
#                             is just when the manifest was rebuilt; the per-ticker
#                             timestamps are what drive freshness decisions.)
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
#   MAX_FETCHES      default 40      NEW (non-skipped) fetches per run.
#   UNIVERSE_SIZE    default 6000    how many top-market-cap symbols to consider.
#   MIN_MARKET_CAP   default 1e7     Microcap floor in USD (drops nano-caps).
#   MAX_EXPIRATIONS  default 12      expirations stored per ticker (keeps JSON small)
#   RATE_LIMIT_HITS  default 3    consecutive failures that mean "we're blocked".
#   REQUEST_SLEEP    default 0.6  seconds between fetches (be polite to Yahoo).
# =============================================================================

import json
import os
import sys
import math
import time
from datetime import datetime, timezone, timedelta

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
# How deep the market-cap-ranked universe goes. The NASDAQ screener returns
# ~7k US tickers across NASDAQ/NYSE/AMEX/Arca; the whole optionable universe is a
# few thousand, so a high default lets the resumable runs eventually cache them
# ALL (Mega -> Micro), a chunk per run.
UNIVERSE_SIZE = int(os.environ.get("UNIVERSE_SIZE", "6000"))
# Minimum market cap to include (USD). Default $10M = Microcap floor; anything
# smaller (nano-caps) is dropped — they rarely have listed options.
MIN_MARKET_CAP = float(os.environ.get("MIN_MARKET_CAP", "10000000"))
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


# ---- Working-day / freshness helpers ----------------------------------------
# US market holidays (NYSE/NASDAQ full-day closures). Extend yearly as needed.
US_MARKET_HOLIDAYS = {
    # 2025
    "2025-01-01", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26",
    "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25",
    # 2026
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
    # 2027
    "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31",
    "2027-06-18", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24",
}


def _is_trading_day(d):
    """True if date `d` is a US market trading day (Mon-Fri and not a holiday)."""
    if d.weekday() >= 5:              # Sat=5, Sun=6
        return False
    return d.strftime("%Y-%m-%d") not in US_MARKET_HOLIDAYS


def _last_trading_day(ref):
    """The most recent trading day on or BEFORE `ref` (a date)."""
    d = ref
    for _ in range(10):              # walk back at most ~10 days
        if _is_trading_day(d):
            return d
        d = d - timedelta(days=1)
    return d


def _file_is_fresh(updated_iso):
    """
    Decide whether a cached file's `updated` date is still FRESH (skip) given the
    business rules:
      * Fetched TODAY (any day)                       -> fresh (skip).
      * TODAY is NOT a trading day (weekend/holiday), and the file was updated on
        the LAST trading day (or later)               -> fresh (skip).
      * TODAY IS a trading day and the file was updated on an earlier day (i.e.
        before today)                                 -> STALE (re-fetch).
    `updated_iso` is the stored "YYYY-MM-DD..." string; returns True to SKIP.
    """
    day = str(updated_iso)[:10]
    if not day:
        return False
    today = datetime.now(timezone.utc).date()
    today_str = today.strftime("%Y-%m-%d")

    if day == today_str:
        return True  # already refreshed today

    if not _is_trading_day(today):
        # Market closed today: data from the last trading day is the freshest
        # available, so anything updated on/after that day is still current.
        ltd = _last_trading_day(today).strftime("%Y-%m-%d")
        return day >= ltd

    # Today is a trading day but the file is from a previous day -> stale.
    return False


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

    # The unfiltered NASDAQ screener already spans ALL US exchanges
    # (NASDAQ / NYSE / NYSE American / NYSE Arca) in one response (~7k rows).
    url = ("https://api.nasdaq.com/api/screener/stocks"
           "?tableonly=true&limit=25000&download=true")
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; OptionsDeskBot/1.0)",
        "Accept": "application/json",
    }
    try:
        r = requests.get(url, headers=headers, timeout=45)
        r.raise_for_status()
        rows = r.json().get("data", {}).get("rows", []) or []

        def cap(row):
            try:
                return float(str(row.get("marketCap", "0")).replace(",", "") or 0)
            except ValueError:
                return 0.0

        # Keep real, optionable-looking tickers (drop warrants/units/odd chars)
        # and enforce the Microcap floor (>= MIN_MARKET_CAP). Sort DESC by cap so
        # runs walk Mega -> Large -> Mid -> Small -> Micro, top to bottom.
        clean = [x for x in rows if x.get("symbol")
                 and "^" not in x["symbol"] and "/" not in x["symbol"]
                 and cap(x) >= MIN_MARKET_CAP]
        clean.sort(key=cap, reverse=True)
        syms = [x["symbol"].upper().strip() for x in clean]
        if syms:
            # Tier breakdown (Mega 176B+, Large 36B+, Mid 6B+, Small 2B+, Micro 10M+).
            def tier(c):
                return ('Mega' if c >= 176e9 else 'Large' if c >= 36e9 else
                        'Mid' if c >= 6e9 else 'Small' if c >= 2e9 else 'Micro')
            from collections import Counter
            counts = Counter(tier(cap(x)) for x in clean)
            print(f"  universe: {len(syms)} symbols from NASDAQ screener "
                  f"(>= ${MIN_MARKET_CAP:,.0f}); "
                  f"tiers={{'Mega':{counts['Mega']}, 'Large':{counts['Large']}, "
                  f"'Mid':{counts['Mid']}, 'Small':{counts['Small']}, "
                  f"'Micro':{counts['Micro']}}}; top: {', '.join(syms[:5])}")
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

def _file_updated(path):
    """Return a cached file's stored `updated` ISO string, or "" if unreadable.
    Used both to build the per-ticker index.json manifest and to order the
    REFRESH phase oldest-first."""
    try:
        with open(path) as f:
            return str(json.load(f).get("updated", ""))
    except Exception:
        return ""


def is_fresh(path):
    """True if the cached file exists and is FRESH per the working-day rules
    (see `_file_is_fresh`): skip today's data, skip last-trading-day data when
    the market is closed today, but re-fetch older data on a trading day."""
    if not os.path.exists(path):
        return False
    return _file_is_fresh(_file_updated(path))


# ---- Main loop --------------------------------------------------------------

def _cached_symbols():
    """Set of ticker symbols that already have a data/{SYMBOL}.json file."""
    return {
        f[:-5] for f in os.listdir(DATA_DIR)
        if f.endswith(".json") and f != "index.json"
    }


def build_work_queue(universe):
    """
    Build the ordered list of symbols to fetch this run, in TWO PHASES:

      PHASE 1 — COVERAGE (missing first): every universe symbol WITHOUT a cached
        file yet, kept in the universe's market-cap order (Mega -> Micro). This
        makes the run RESUME DOWN the list where prior runs stopped, so we work
        toward caching ALL tickers instead of re-looping the top-cap names.

      PHASE 2 — REFRESH (oldest first): only reached once nothing is missing.
        EXISTING files that are STALE per the working-day rules, ordered by their
        stored `updated` ASCENDING (oldest data first) so refreshes rotate evenly
        across the whole cache rather than always hitting the biggest names.

    Files that are still FRESH today are excluded from BOTH phases (skipped).
    Returns (queue, n_missing, n_stale, n_fresh_skipped).
    """
    cached = _cached_symbols()

    # PHASE 1: missing universe symbols, in market-cap order (universe order).
    missing = [s for s in universe if s not in cached]

    # PHASE 2: existing files that are stale (need refresh), oldest-updated first.
    #  We consider ALL cached files on disk (even ones no longer in the universe)
    #  so nothing goes permanently stale. Fresh files are skipped entirely.
    stale = []
    fresh_skipped = 0
    for sym in cached:
        path = os.path.join(DATA_DIR, f"{sym}.json")
        if is_fresh(path):
            fresh_skipped += 1
            continue
        stale.append((sym, _file_updated(path)))
    # Oldest `updated` first ("" sorts first -> unreadable/undated get priority).
    stale.sort(key=lambda t: t[1])
    stale_syms = [s for s, _ in stale]

    return missing + stale_syms, len(missing), len(stale_syms), fresh_skipped


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    universe = load_universe()

    queue, n_missing, n_stale, n_fresh = build_work_queue(universe)

    fetched = 0        # NEW fetches performed this run
    consecutive_fail = 0

    print(f"Smart fetch v4: budget={MAX_FETCHES} new, universe={len(universe)}, "
          f"today={_today_iso()}")
    print(f"  queue: {n_missing} missing (coverage) + {n_stale} stale (refresh, "
          f"oldest-first); {n_fresh} fresh skipped.")
    if n_missing == 0 and n_stale:
        print("  coverage complete — cycling oldest files for refresh.")

    for sym in queue:
        if fetched >= MAX_FETCHES:
            print(f"  reached MAX_FETCHES={MAX_FETCHES}; stopping (resume next run).")
            break

        path = os.path.join(DATA_DIR, f"{sym}.json")

        # Fetch (missing OR stale -> overwrite). The queue already excludes fresh
        # files, so no per-item freshness check is needed here.
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

    write_index()

    total = len(_cached_symbols())
    print(f"Done. new={fetched}, missing_left={max(0, n_missing - fetched)}, "
          f"total_cached={total}")


def write_index():
    """
    Rebuild data/index.json as a PER-TICKER manifest from the files on disk.
    Shape (v4): { "files": { TICKER: <updated ISO>, ... }, "count": N,
                  "generated": <ISO> }.
    Each ticker keeps ITS OWN `updated` (read from its file), so the manifest
    reflects real per-ticker freshness and unchanged tickers keep their old
    timestamp — no single global `updated` that churns every run.
    """
    files = {}
    for sym in sorted(_cached_symbols()):
        files[sym] = _file_updated(os.path.join(DATA_DIR, f"{sym}.json"))
    with open(os.path.join(DATA_DIR, "index.json"), "w") as f:
        json.dump(
            {"files": files, "count": len(files), "generated": _now_iso()},
            f, indent=2,
        )


if __name__ == "__main__":
    main()
