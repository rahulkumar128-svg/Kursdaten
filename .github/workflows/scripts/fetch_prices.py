#!/usr/bin/env python3
"""
Laedt Tageskurse (ca. 2 Jahre) fuer alle Ticker aus tickers.txt und schreibt je
Ticker eine CSV nach data/<TICKER>.csv (Spalten: Date,Open,High,Low,Close,Volume).
Zusaetzlich data/_status.json mit Anzahl Handelstage und letztem Datum.
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
PERIOD = "2y"


def read_tickers(path: str) -> list[str]:
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            s = line.split("#", 1)[0].strip()
            if s and s.upper() not in out:
                out.append(s.upper())
    return out


def write_csv(path: str, rows: list[tuple]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("Date,Open,High,Low,Close,Volume\n")
        for d, o, h, l, c, v in rows:
            f.write(f"{d},{o:.4f},{h:.4f},{l:.4f},{c:.4f},{int(v)}\n")


def fetch(sym: str):
    import yfinance as yf
    df = yf.Ticker(sym).history(period=PERIOD, interval="1d", auto_adjust=False)
    rows = []
    for ts, r in df.iterrows():
        c = r.get("Close")
        if c is None or c != c or c <= 0:
            continue
        rows.append((ts.strftime("%Y-%m-%d"), r["Open"], r["High"], r["Low"], c, r.get("Volume", 0) or 0))
    return rows


def main(fetch_fn=fetch) -> int:
    os.makedirs(DATA, exist_ok=True)
    tickers = read_tickers(os.path.join(ROOT, "tickers.txt"))
    status, ok = {}, 0
    for sym in tickers:
        try:
            rows = fetch_fn(sym)
        except Exception as e:
            status[sym] = {"status": "error", "error": str(e)[:200]}
            print(f"{sym}: FEHLER {e}", file=sys.stderr)
            continue
        if len(rows) < 5:
            status[sym] = {"status": "empty", "bars": len(rows)}
            print(f"{sym}: keine brauchbaren Daten", file=sys.stderr)
            continue
        write_csv(os.path.join(DATA, f"{sym}.csv"), rows)
        status[sym] = {"status": "ok", "bars": len(rows), "first": rows[0][0], "last": rows[-1][0]}
        ok += 1
        print(f"{sym}: {len(rows)} Tage bis {rows[-1][0]}")
    with open(os.path.join(DATA, "_status.json"), "w", encoding="utf-8") as f:
        json.dump({"updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"), "symbols": status}, f, indent=1)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
