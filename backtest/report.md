# Backtest: Auswahlverfahren ueber S&P 500 + DAX 40
Stand: 2026-11-22 06:53 UTC. Reine Simulation, keine Anlageberatung.

Zeitraum: 2022-11-11 bis 2026-11-09, 207 Wochen (nicht ueberlappend). Aktien geladen: 539 von 544. Je Regel 5 Aktien, Haltedauer 5 Handelstage.

## Rendite pro Woche vor Kosten (Brutto)

| Regel | Mittel | Median | Wochen im Plus | schlechteste | beste | Gesamt (aufgezinst) |
|---|---|---|---|---|---|---|
| vorsichtig | +0.27 % | +0.31 % | 57 % | -8.2 % | +5.6 % | +68 % |
| ausgewogen | +0.23 % | +0.28 % | 56 % | -9.4 % | +7.0 % | +52 % |
| riskant | +0.58 % | +0.39 % | 53 % | -16.2 % | +19.8 % | +142 % |
| zufall | +0.35 % | +0.49 % | 62 % | -12.0 % | +7.2 % | +98 % |
| alle_aktien | +0.35 % | +0.41 % | 60 % | -11.8 % | +7.3 % | +97 % |

## Besser als Zufall?

Unterschied pro Woche zur Zufallsauswahl (Mittel aus vielen Ziehungen). t-Wert ueber etwa 2 waere ein Hinweis, dass es nicht nur Glueck war.

| Regel | Mittel Unterschied | t-Wert | Wochen besser als Zufall |
|---|---|---|---|
| vorsichtig | -0.08 % | -0.59 | 48 % |
| ausgewogen | -0.12 % | -0.89 | 47 % |
| riskant | +0.23 % | +0.68 | 52 % |

## Kosten

Bei 100 EUR und 1.00 EUR je Order kosten 5 Aktien pro Woche (Kauf und Verkauf) etwa 10 % des Einsatzes. Netto waeren die Wochenmittel um diesen Wert niedriger. Mit 100 EUR ist Streuung ueber mehrere Einzelaktien nicht wirtschaftlich.

| Regel | Mittel nach Kosten |
|---|---|
| vorsichtig | -9.73 % |
| ausgewogen | -9.77 % |
| riskant | -9.42 % |

## Was die Zahlen nicht zeigen

- Ueberlebens-Verzerrung: Getestet wird mit den heutigen Mitgliedern von S&P 500 und DAX. Firmen, die in den letzten Jahren ausgeschieden oder gescheitert sind, fehlen. Das macht die Ergebnisse tendenziell zu gut.
- Die Regeln wurden vor dem Test festgelegt, aber es sind drei Regeln auf einem Zeitraum. Ein gutes Ergebnis kann Zufall sein.
- Dollar-Aktien sind in Dollar gerechnet, DAX-Aktien in Euro. Wechselkurseffekte fehlen.
- Vergangene Wochen sagen nichts sicher ueber kommende Wochen.
