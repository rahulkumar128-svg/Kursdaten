# Backtest: Auswahlverfahren ueber S&P 500 + DAX 40
Stand: 2026-11-14 15:47 UTC. Reine Simulation, keine Anlageberatung.

Zeitraum: 2022-11-04 bis 2026-11-02, 207 Wochen (nicht ueberlappend). Aktien geladen: 539 von 544. Je Regel 5 Aktien, Haltedauer 5 Handelstage.

## Rendite pro Woche vor Kosten (Brutto)

| Regel | Mittel | Median | Wochen im Plus | schlechteste | beste | Gesamt (aufgezinst) |
|---|---|---|---|---|---|---|
| vorsichtig | +0.25 % | +0.30 % | 57 % | -8.2 % | +5.6 % | +64 % |
| ausgewogen | +0.23 % | +0.28 % | 56 % | -9.4 % | +7.0 % | +53 % |
| riskant | +0.65 % | +0.43 % | 54 % | -16.2 % | +19.8 % | +180 % |
| zufall | +0.36 % | +0.36 % | 60 % | -11.8 % | +7.2 % | +104 % |
| alle_aktien | +0.38 % | +0.43 % | 61 % | -11.8 % | +7.3 % | +111 % |

## Besser als Zufall?

Unterschied pro Woche zur Zufallsauswahl (Mittel aus vielen Ziehungen). t-Wert ueber etwa 2 waere ein Hinweis, dass es nicht nur Glueck war.

| Regel | Mittel Unterschied | t-Wert | Wochen besser als Zufall |
|---|---|---|---|
| vorsichtig | -0.11 % | -0.76 | 47 % |
| ausgewogen | -0.13 % | -0.93 | 48 % |
| riskant | +0.29 % | +0.85 | 52 % |

## Kosten

Bei 100 EUR und 1.00 EUR je Order kosten 5 Aktien pro Woche (Kauf und Verkauf) etwa 10 % des Einsatzes. Netto waeren die Wochenmittel um diesen Wert niedriger. Mit 100 EUR ist Streuung ueber mehrere Einzelaktien nicht wirtschaftlich.

| Regel | Mittel nach Kosten |
|---|---|
| vorsichtig | -9.75 % |
| ausgewogen | -9.77 % |
| riskant | -9.35 % |

## Was die Zahlen nicht zeigen

- Ueberlebens-Verzerrung: Getestet wird mit den heutigen Mitgliedern von S&P 500 und DAX. Firmen, die in den letzten Jahren ausgeschieden oder gescheitert sind, fehlen. Das macht die Ergebnisse tendenziell zu gut.
- Die Regeln wurden vor dem Test festgelegt, aber es sind drei Regeln auf einem Zeitraum. Ein gutes Ergebnis kann Zufall sein.
- Dollar-Aktien sind in Dollar gerechnet, DAX-Aktien in Euro. Wechselkurseffekte fehlen.
- Vergangene Wochen sagen nichts sicher ueber kommende Wochen.
