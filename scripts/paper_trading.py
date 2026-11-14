#!/usr/bin/env python3
"""Paper-Trading: simuliert 100 EUR (virtuell) in mehreren Risikostufen auf Basis von data/<TICKER>.csv.

Regeln: Einstieg zum Schlusskurs am start_date (bzw. erstem Handelstag danach), Bruchstuecke erlaubt,
Gebuehr pro Order, Ticker auf .DE oder -EUR gelten als Euro-Kurse; andere (USD) werden mit data/<fx_ticker>.csv umgerechnet.
Ausgabe: paper/state.json und paper/report.md. Keine echten Orders.
"""
from __future__ import annotations
import csv, json, os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.environ.get("PAPER_DATA_DIR", os.path.join(ROOT, "data"))
OUT = os.environ.get("PAPER_OUT_DIR", os.path.join(ROOT, "paper"))


def load_close(ticker: str) -> dict[str, float]:
    path = os.path.join(DATA, f"{ticker}.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Keine Kursdatei fuer {ticker} (Ticker in tickers.txt eintragen)")
    with open(path, encoding="utf-8") as f:
        return {r["Date"]: float(r["Close"]) for r in csv.DictReader(f)}


def is_eur(ticker: str) -> bool:
    """Ticker, die schon in Euro notieren (Euro-Boersen wie .DE, .MI, .PA; Krypto -EUR)."""
    t = ticker.upper()
    return t.endswith("-EUR") or t.endswith((".DE", ".F", ".MI", ".PA", ".AS", ".MC", ".BR", ".VI", ".HE", ".LS", ".IR"))


def run(cfg: dict) -> dict:
    start, end = cfg["start_date"], cfg["end_date"]
    cash, fee = float(cfg["start_cash_eur"]), float(cfg["fee_eur_per_order"])
    need_fx = any(not is_eur(t) for w in cfg["strategies"].values() for t in w)
    fx = load_close(cfg["fx_ticker"]) if need_fx else {}  # USD je EUR
    fx_dates = sorted(fx)
    result = {"updated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
              "start_date": start, "end_date": end, "strategies": {}}

    def fx_on(d: str, t: str = "") -> float:
        if is_eur(t):
            return 1.0
        prev = [x for x in fx_dates if x <= d]
        return fx[prev[-1]] if prev else fx[fx_dates[0]]

    for name, weights in cfg["strategies"].items():
        try:
            prices = {t: load_close(t) for t in weights}
        except FileNotFoundError as e:
            result["strategies"][name] = {"status": f"Kursdaten fehlen ({e})", "weights": weights}
            continue
        common = sorted(set.intersection(*[set(p) for p in prices.values()]))
        days = [d for d in common if start <= d <= end]
        if not days:
            result["strategies"][name] = {"status": "wartet auf erste Kurse", "weights": weights}
            continue
        d0 = days[0]
        investable = cash - fee * len(weights)
        shares = {t: investable * w / (prices[t][d0] / fx_on(d0, t)) for t, w in weights.items()}
        curve = []
        for d in days:
            val = sum(shares[t] * prices[t][d] / fx_on(d, t) for t in weights)
            curve.append({"date": d, "value_eur": round(val, 2)})
        last = curve[-1]
        net_exit = last["value_eur"] - fee * len(weights)
        peak, max_dd = 0.0, 0.0
        for p in curve:
            peak = max(peak, p["value_eur"])
            max_dd = min(max_dd, p["value_eur"] / peak - 1)
        result["strategies"][name] = {
            "status": "abgeschlossen" if last["date"] >= end else "laufend",
            "weights": weights, "entry_date": d0, "last_date": last["date"],
            "value_eur": last["value_eur"], "net_after_exit_fee_eur": round(net_exit, 2),
            "change_pct_net": round((net_exit / cash - 1) * 100, 2),
            "max_drawdown_pct": round(max_dd * 100, 2), "curve": curve}
    return result


def report(res: dict, cfg: dict) -> str:
    L = [f"# Paper-Trading: {cfg['start_cash_eur']:.0f} EUR virtuell, {res['start_date']} bis {res['end_date']}",
         f"Stand: {res['updated_utc']} UTC. Reine Simulation, keine Anlageberatung.", "",
         "| Variante | Status | Wert (EUR) | Netto nach Verkauf (EUR) | Veraenderung | Tiefster Rueckgang |",
         "|---|---|---|---|---|---|"]
    for n, s in res["strategies"].items():
        if "value_eur" not in s:
            L.append(f"| {n} | {s['status']} | - | - | - | - |")
        else:
            L.append(f"| {n} | {s['status']} (Kurs {s['last_date']}) | {s['value_eur']:.2f} | "
                     f"{s['net_after_exit_fee_eur']:.2f} | {s['change_pct_net']:+.2f} % | {s['max_drawdown_pct']:.2f} % |")
    L += ["", f"Annahmen: Einstieg zum Schlusskurs, {cfg['fee_eur_per_order']:.2f} EUR je Order (Kauf und Verkauf), "
          "Kurse in EUR (Xetra bzw. Krypto in EUR), US-Ticker werden zum Tageskurs umgerechnet, keine Steuern."]
    return "\n".join(L) + "\n"


def main() -> int:
    with open(os.path.join(OUT, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    res = run(cfg)
    with open(os.path.join(OUT, "state.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1)
    with open(os.path.join(OUT, "report.md"), "w", encoding="utf-8") as f:
        f.write(report(res, cfg))
    print(report(res, cfg))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
