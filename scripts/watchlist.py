#!/usr/bin/env python3
"""Watchlist-Daten: 2 Jahre Tageskurse und Kennzahlen (Yahoo Finance) fuer die beobachteten Einzelaktien.

Ausgabe:
  analysis/prices/<TICKER>.csv   (Date,Open,High,Low,Close,Volume, wie in data/)
  analysis/fundamentals.csv      (Bewertung, Wachstum, Marge, Verschuldung, Analystenziele ...)
Reine Datenbeschaffung, keine Anlageberatung.
"""
from __future__ import annotations
import csv, os, sys, time
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("WATCHLIST_OUT_DIR", os.path.join(ROOT, "analysis"))

# Genannt von Analysten/Kommentatoren (Stand 17.11.2026). Hier beliebig aendern.
WATCH = ["NVDA", "MU", "AVGO", "TSM", "APP", "TTWO", "SPOT", "GOOGL", "AAPL", "KO",
         "ZBH", "TDY", "ON", "BE", "GEV"]

FIELDS = ["shortName", "sector", "marketCap", "currentPrice", "fiftyTwoWeekLow", "fiftyTwoWeekHigh",
          "trailingPE", "forwardPE", "pegRatio", "priceToSalesTrailing12Months", "profitMargins",
          "operatingMargins", "revenueGrowth", "earningsGrowth", "returnOnEquity", "debtToEquity",
          "freeCashflow", "dividendYield", "beta", "targetMeanPrice", "targetLowPrice", "targetHighPrice",
          "recommendationMean", "numberOfAnalystOpinions"]


def main() -> int:
    import yfinance as yf
    os.makedirs(os.path.join(OUT, "prices"), exist_ok=True)
    rows, ok = [], 0
    for t in WATCH:
        row = {"ticker": t}
        try:
            h = yf.Ticker(t).history(period="2y", interval="1d", auto_adjust=True)
            if len(h):
                with open(os.path.join(OUT, "prices", f"{t}.csv"), "w", newline="", encoding="utf-8") as f:
                    w = csv.writer(f)
                    w.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])
                    for d, r in h.iterrows():
                        w.writerow([d.strftime("%Y-%m-%d"), f"{r['Open']:.4f}", f"{r['High']:.4f}",
                                    f"{r['Low']:.4f}", f"{r['Close']:.4f}", int(r["Volume"])])
                row["bars"] = len(h)
                row["last_date"] = h.index[-1].strftime("%Y-%m-%d")
                ok += 1
            else:
                print(f"{t}: keine Kurse", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            print(f"{t}: Kurse fehlgeschlagen: {e}", file=sys.stderr)
        try:
            info = yf.Ticker(t).info or {}
            for k in FIELDS:
                row[k] = info.get(k, "")
        except Exception as e:  # noqa: BLE001
            print(f"{t}: Kennzahlen fehlgeschlagen: {e}", file=sys.stderr)
        rows.append(row)
        time.sleep(1)
    cols = ["ticker", "bars", "last_date"] + FIELDS
    with open(os.path.join(OUT, "fundamentals.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(OUT, "_status.txt"), "w", encoding="utf-8") as f:
        f.write(f"Stand {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC, Kurse fuer {ok} von {len(WATCH)} Aktien\n")
    print(f"Kurse fuer {ok} von {len(WATCH)} Aktien geladen")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
