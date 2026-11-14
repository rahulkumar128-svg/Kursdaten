#!/usr/bin/env python3
"""Backtest des Auswahlverfahrens ueber S&P 500 + DAX 40.

Jede Woche (alle 5 Handelstage) waehlt jede Regel 5 Aktien, nur mit Daten bis zu diesem Tag.
Gemessen wird die Rendite der folgenden 5 Handelstage. Verglichen wird mit Zufallsauswahl
(Mittel aus vielen Ziehungen) und dem Durchschnitt aller Aktien.
Ausgabe: backtest/report.md und backtest/weekly.csv. Reine Simulation, keine Anlageberatung.
"""
from __future__ import annotations
import os, sys, time
from datetime import datetime, timezone
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.environ.get("BACKTEST_OUT_DIR", os.path.join(ROOT, "backtest"))

CFG = {
    "years": 5,            # Kurshistorie
    "k": 5,                # Aktien je Regel
    "hold_days": 5,        # Haltedauer in Handelstagen (1 Woche)
    "vol_days": 252,       # Fenster fuer Schwankung
    "mom_days": 126,       # Fenster fuer Trend (ca. 6 Monate)
    "random_draws": 200,   # Zufallsziehungen je Woche
    "seed": 42,
    "budget_eur": 100.0,
    "fee_eur_per_order": 1.0,
}

# DAX 40, Stand aus dem Gedaechtnis (Zusammensetzung aendert sich). Nicht ladbare Ticker werden uebersprungen.
DAX40 = ["ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE", "CBK.DE", "CON.DE",
         "1COV.DE", "DTG.DE", "DBK.DE", "DB1.DE", "DHL.DE", "DTE.DE", "EOAN.DE", "ENR.DE", "FRE.DE", "FME.DE",
         "G24.DE", "HNR1.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "P911.DE",
         "PAH3.DE", "QIA.DE", "RHM.DE", "RWE.DE", "SAP.DE", "SHL.DE", "SIE.DE", "SY1.DE", "VNA.DE", "VOW3.DE",
         "ZAL.DE"]
SP500_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"


def universe() -> list[str]:
    sp = [s.replace(".", "-") for s in pd.read_csv(SP500_URL)["Symbol"].astype(str)]
    return sorted(set(sp + DAX40))


def load_prices(tickers: list[str], years: int) -> pd.DataFrame:
    if os.environ.get("BACKTEST_FAKE") == "1":  # nur fuer Tests, erzeugt Zufallskurse
        rng = np.random.default_rng(1)
        idx = pd.bdate_range(end="2026-11-13", periods=years * 252)
        vols = rng.uniform(0.008, 0.04, len(tickers))
        return pd.DataFrame(100 * np.exp(np.cumsum(rng.normal(0, 1, (len(idx), len(tickers))) * vols, axis=0)),
                            index=idx, columns=tickers)
    import yfinance as yf
    frames = []
    for i in range(0, len(tickers), 80):
        chunk = tickers[i:i + 80]
        for attempt in range(3):
            try:
                d = yf.download(chunk, period=f"{years}y", interval="1d", auto_adjust=True,
                                progress=False, threads=True)
                close = d["Close"]
                if isinstance(close, pd.Series):
                    close = close.to_frame(chunk[0])
                frames.append(close)
                break
            except Exception as e:  # noqa: BLE001
                print(f"Chunk {i} Versuch {attempt + 1} fehlgeschlagen: {e}", file=sys.stderr)
                time.sleep(5)
        time.sleep(2)
    if not frames:
        raise SystemExit("Keine Kursdaten geladen")
    px = pd.concat(frames, axis=1)
    px = px.loc[:, ~px.columns.duplicated()]
    return px


def evaluate(px: pd.DataFrame) -> pd.DataFrame:
    k, hold = CFG["k"], CFG["hold_days"]
    px = px.sort_index().ffill(limit=3)
    ret1 = px.pct_change(fill_method=None)
    vol = ret1.rolling(CFG["vol_days"], min_periods=int(CFG["vol_days"] * 0.8)).std()
    mom = px / px.shift(CFG["mom_days"]) - 1
    short = px / px.shift(5) - 1
    fwd = px.shift(-hold) / px - 1
    rng = np.random.default_rng(CFG["seed"])
    rows = []
    for i in range(CFG["vol_days"], len(px) - hold, hold):
        v, m, s, f = vol.iloc[i], mom.iloc[i], short.iloc[i], fwd.iloc[i]
        ok = v.notna() & m.notna() & s.notna() & (v > 0)  # nur Wissen bis zum Stichtag
        if ok.sum() < 50:
            continue
        v, m, s = v[ok], m[ok], s[ok]
        fv = f[ok]
        safe = v.nsmallest(k).index
        cand_b = v[v <= v.median()].index
        balanced = m[cand_b].nlargest(k).index
        cand_r = v[v >= v.quantile(0.8)].index
        risky = s[cand_r].nlargest(k).index
        pool = np.array(v.index)
        draws = [np.nanmean(fv[rng.choice(pool, k, replace=False)].to_numpy()) for _ in range(CFG["random_draws"])]
        rows.append({"datum": px.index[i].date().isoformat(),
                     "vorsichtig": np.nanmean(fv[safe]), "ausgewogen": np.nanmean(fv[balanced]),
                     "riskant": np.nanmean(fv[risky]), "zufall": float(np.mean(draws)),
                     "alle_aktien": np.nanmean(fv.to_numpy()), "anzahl_aktien": int(ok.sum())})
    return pd.DataFrame(rows).dropna()


def report(w: pd.DataFrame, loaded: int, requested: int) -> str:
    fee = 2 * CFG["k"] * CFG["fee_eur_per_order"] / CFG["budget_eur"]
    n = len(w)
    names = ["vorsichtig", "ausgewogen", "riskant", "zufall", "alle_aktien"]
    L = [f"# Backtest: Auswahlverfahren ueber S&P 500 + DAX 40",
         f"Stand: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC. Reine Simulation, keine Anlageberatung.", "",
         f"Zeitraum: {w['datum'].iloc[0]} bis {w['datum'].iloc[-1]}, {n} Wochen (nicht ueberlappend). "
         f"Aktien geladen: {loaded} von {requested}. Je Regel {CFG['k']} Aktien, Haltedauer {CFG['hold_days']} Handelstage.", "",
         "## Rendite pro Woche vor Kosten (Brutto)", "",
         "| Regel | Mittel | Median | Wochen im Plus | schlechteste | beste | Gesamt (aufgezinst) |", "|---|---|---|---|---|---|---|"]
    for c in names:
        r = w[c]
        L.append(f"| {c} | {r.mean()*100:+.2f} % | {r.median()*100:+.2f} % | {(r>0).mean()*100:.0f} % | "
                 f"{r.min()*100:+.1f} % | {r.max()*100:+.1f} % | {((1+r).prod()-1)*100:+.0f} % |")
    L += ["", "## Besser als Zufall?", "",
          "Unterschied pro Woche zur Zufallsauswahl (Mittel aus vielen Ziehungen). t-Wert ueber etwa 2 waere ein Hinweis, "
          "dass es nicht nur Glueck war.", "",
          "| Regel | Mittel Unterschied | t-Wert | Wochen besser als Zufall |", "|---|---|---|---|"]
    for c in ["vorsichtig", "ausgewogen", "riskant"]:
        d = w[c] - w["zufall"]
        t = d.mean() / (d.std(ddof=1) / np.sqrt(n)) if d.std(ddof=1) > 0 else float("nan")
        L.append(f"| {c} | {d.mean()*100:+.2f} % | {t:+.2f} | {(d>0).mean()*100:.0f} % |")
    L += ["", "## Kosten", "",
          f"Bei {CFG['budget_eur']:.0f} EUR und {CFG['fee_eur_per_order']:.2f} EUR je Order kosten {CFG['k']} Aktien pro Woche "
          f"(Kauf und Verkauf) etwa {fee*100:.0f} % des Einsatzes. Netto waeren die Wochenmittel um diesen Wert niedriger. "
          "Mit 100 EUR ist Streuung ueber mehrere Einzelaktien nicht wirtschaftlich.", "",
          "| Regel | Mittel nach Kosten |", "|---|---|"]
    for c in ["vorsichtig", "ausgewogen", "riskant"]:
        L.append(f"| {c} | {(w[c].mean()-fee)*100:+.2f} % |")
    L += ["", "## Was die Zahlen nicht zeigen", "",
          "- Ueberlebens-Verzerrung: Getestet wird mit den heutigen Mitgliedern von S&P 500 und DAX. Firmen, die in den letzten Jahren "
          "ausgeschieden oder gescheitert sind, fehlen. Das macht die Ergebnisse tendenziell zu gut.",
          "- Die Regeln wurden vor dem Test festgelegt, aber es sind drei Regeln auf einem Zeitraum. Ein gutes Ergebnis kann Zufall sein.",
          "- Dollar-Aktien sind in Dollar gerechnet, DAX-Aktien in Euro. Wechselkurseffekte fehlen.",
          "- Vergangene Wochen sagen nichts sicher ueber kommende Wochen."]
    return "\n".join(L) + "\n"


def main() -> int:
    tickers = universe()
    px = load_prices(tickers, CFG["years"])
    px = px.loc[:, px.notna().sum() > CFG["vol_days"] + 60]
    print(f"{px.shape[1]} von {len(tickers)} Aktien geladen, {len(px)} Tage")
    w = evaluate(px)
    os.makedirs(OUT, exist_ok=True)
    w.to_csv(os.path.join(OUT, "weekly.csv"), index=False, float_format="%.5f")
    text = report(w, px.shape[1], len(tickers))
    with open(os.path.join(OUT, "report.md"), "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
