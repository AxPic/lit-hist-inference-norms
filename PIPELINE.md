# Arbeitspipeline — Schritt für Schritt

Dieses Dokument beschreibt das vollständige Verfahren von der digitalen Vorlage bis zu den
ausgewerteten Metriken. Die Pipeline gliedert sich in **Ebene 0** (Preprocessing, Propositionen und ihre
inferentiellen Relationen, in zwei Stufen), **Ebene 1** (Systembezug), **Ebene 2**
(Gegenstandsextraktion) sowie die **Analyse** (Graph, Metriken, Netzwerkauswertung).

```
   Beutin-PDF
       │  (pdfplumber, kapitelweise)
       ▼
┌─ EBENE 0 ─────────────────────────────────────────────────┐
│  Stufe 1  Propositionsextraktion + Intra-Satz-Relationen  │  prompt_intra-satz_cot.md
│           → …_stufe1.{xlsx,csv,json}                      │  stufe1_…ipynb
│                         │                                 │
│  Stufe 2  Inter-Satz-Relationen (Satzpaare A→B)           │  prompt_inter-satz_cot.md
│           → …_gesamt.{xlsx,csv}, …_stufe2_inter.{csv,json}│  stufe2_…ipynb
└──────────────────────────┬────────────────────────────────┘
                           ▼
   EBENE 1  Systembezug   LIT · NLIT · LIT-NLIT            (Richtlinien §3)
   EBENE 2  Gegenstände   LIT-Gegenstand × NLIT-Gegenstand (Richtlinien §4)
            → …_gesamt_sytembezug.xlsx  (+ Blatt „Verknüpfungen LIT-NLIT")
                           │
                           ▼
   ANALYSE  Inferenzgraph → Metriken      inferenzgraph_analyse_…V3.ipynb → …_metriken.xlsx
            Systembezug-Netzwerk          systembezug_netzwerk_analyse.ipynb

   EVALUATION  Stichprobenziehung             stichprobe_ziehung.py
               Intra-Relationen (P/R/F1)      eval_precision_recall.ipynb   ← Hauptevaluation
               Systembezug & Gegenstände      eval_systembezug.ipynb
               Plausibilität (Vorstudie)      eval_plausibility.ipynb
```


---

## Voraussetzungen

- Python ≥ 3.10; Pakete `anthropic`, `pdfplumber`, `pandas`, `numpy`, `openpyxl`,
  `networkx`, `matplotlib` (Visualisierung: `pyvis`/`plotly`; Evaluation: `scikit-learn`).
- Anthropic-API-Schlüssel.
- Modell `claude-opus-4-8` für alle generativen Schritte.
- Alle generativen Schritte schreiben **Checkpoints**, sodass unterbrochene Läufe wiederaufgenommen werden können.

Konvention: `STEM = "Beutin_complete_Direktzitat"`; Ausgabedateien folgen dem Muster
`{STEM}_…`.

**Richtlinienstand.** Die Prompts operationalisieren
`Brandom_Annotationsrichtlinien_V9.docx`. Für die **menschliche** Nachannotation in der
Evaluation gilt zusätzlich `Brandom_Annotationsrichtlinien_V9-1_Addendum.docx` (R1–R5).
Die Prompts wurden nach V9.1 bewusst **nicht** nachgeführt, damit das gesamte Korpus unter
einem einheitlichen Richtlinienstand erzeugt bleibt; die Abweichung ist in Evaluation A
dokumentiert und quantifiziert.

---

## Schritt 0 — Eingangskorpus

**Textgrundlage:** Beutin, Wolfgang/Beilein, Matthias/Emmerich, Wolfgang u. a.: Deutsche Literaturgeschichte: Von den Anfängen bis zur Gegenwart, Stuttgart 2019. DOI: https://doi.org/10.1007/978-3-476-04953-7 (Volltext als PDF).
Das Notebook `stufe1_…ipynb` liest das PDF mit `pdfplumber` und rekonstruiert die **Kapitelstruktur**, sodass die nachfolgenden Schritte kapitelweise arbeiten.

> Das PDF ist aus urheberrechtlichen Gründen **nicht** Teil des Repositories. Es bildet
> den Einstiegspunkt der Pipeline und muss lokal bereitgestellt werden.

---

## Ebene 0 · Stufe 1 — Propositionsextraktion + Intra-Satz-Relationen

**Notebook:** `stufe1_propositionsextraktion_kapitel_final.ipynb`
**Prompt:** `prompt_intra-satz_cot.md`

**Verfahren.**
1. **Setup & Konfiguration** (Modell, Pfade, API-Client).
2. **PDF-Textextraktion** mit Kapitelstruktur (`pdfplumber`).
3. **Propositionsextraktion via Claude (Chain of Thought).** Jeder Satz wird in
   eigenständige Propositionen zerlegt (Subjekt + Prädikat; Pronomen aufgelöst;
   Nummerierung `P(Satz-ID.n)`). Für jedes Propositionspaar innerhalb eines Satzes
   durchläuft das Modell explizit den **dreistufigen Abgrenzungstest**:
   - *Festlegungstest* → `PR-FLG`, sonst weiter
   - *Berechtigungstest* → `PR-BER`, sonst weiter
   - *Inkompatibilitätstest* → `PR-INK`, sonst **kein Paar** (`PR-UNA`).
4. **DataFrame** erstellen, **Export**, **Statistiken**.

**Checkpoints:** `checkpoint_batch_XXXX.json` (+ `checkpoint_latest.json`).

**Ausgabe:** `{STEM}_stufe1.{csv,xlsx,json}` — Blatt *Propositionen*:
`Kapitel · Satz-ID · Originaltext · Propositions-ID · Proposition · Intra-Satz-Relationen · Relationstypen · Reasoning`.
Das `reasoning`-Feld dokumentiert den vollständigen Testdurchlauf je Relation.

> **Hinweis zur Weiterverarbeitung.** Die Spalte `Intra-Satz-Relationen` enthält die
> Relationen eines Satzes **in jeder Propositionszeile dieses Satzes**. Wer Relationen
> aus Stufe 1 zählt oder zu Paaren auflöst, muss je Satz deduplizieren, sonst werden
> Relationen mehrfach gezählt. `stichprobe_ziehung.py` und
> `eval_precision_recall.ipynb` tun dies; ältere Ad-hoc-Auswertungen taten es nicht.

---

## Ebene 0 · Stufe 2 — Inter-Satz-Relationen

**Notebook:** `stufe2_inter_satz_relationen_kapitel_final.ipynb`
**Prompt:** `prompt_inter-satz_cot.md`

**Verfahren.**
1. **Setup** (liest `{STEM}_stufe1.json` und `{STEM}_stufe1.csv`).
2. **Satzpaare bilden** — kapitelweise jeweils aufeinanderfolgende Sätze (Satz A, Satz B).
3. **Inter-Satz-Relationen extrahieren.** Das Modell prüft, welche Proposition aus A mit
   welcher aus B inferentiell verbunden ist (immer **A↔B-übergreifend**, nie satzintern),
   erneut über den dreistufigen Abgrenzungstest. Der Prompt schärft besonders die
   **Fehlerquellen** ein, die *keine* Relation begründen: Kontrast/Gegenüberstellung,
   metadiskursive Leerformeln, bloße thematische Nähe, parallele Aufzählung und rein
   **zeitlich-chronologische** Abfolge. Leeres Array (inferentielle Unabhängigkeit) ist
   der häufigste Fall.
4. **DataFrames erstellen**, **Zusammenführung mit Stufe 1**, **Export**, **Statistiken**.

**Richtung.** `Von → Nach` folgt dem Begründungsverhältnis (stützende → gestützte
Proposition), **nicht** der Satzreihenfolge.

**Checkpoints:** `checkpoint_pair_XXXX.json` (+ `checkpoint_latest.json`).

**Ausgabe:** `{STEM}_gesamt.{csv,xlsx}` und `{STEM}_stufe2_inter.{csv,json}`.
Die `…_gesamt_inf.xlsx` enthält
- Blatt *Propositionen* (Stufe 1 + Spalten `Inter-Satz-Relationen`, `Inter-Satz-Typen`)
- Blatt *Inter-Satz-Relationen*: `Kapitel · Satz A · Satz B · Von · Nach · Relationstyp · Konnektor · Reasoning`.

---

## Ebene 1 — Systembezug  ·  Ebene 2 — Gegenstandsextraktion

**Spezifikation:** `Brandom_Annotationsrichtlinien_V9.docx`, §§ 3–4.

**Ebene 1 (Systembezug).** Jede Proposition wird klassifiziert als
`LIT` (literarisch), `NLIT` (nicht-literarisch) oder `LIT-NLIT` (systemverknüpfende Brücke).

**Ebene 2 (Gegenstände).** Für jede `LIT-NLIT`-Proposition werden der **LIT-Gegenstand**
und der **NLIT-Gegenstand** extrahiert, d. h. das literarische Objekt und der außerliterarische
Sachverhalt, die in der Brücke zusammengeführt werden.

**Ausgabe:** `{STEM}_gesamt_sytembezug.xlsx`
- Blatt *Propositionen*: Ebene 0 + `Systembezug · LIT-Gegenstand · NLIT-Gegenstand`
- Blatt *Verknüpfungen LIT-NLIT* (7 572 Brücken): `Kapitel · Propositions-ID · Proposition · LIT-Gegenstand · NLIT-Gegenstand`.

Zusätzlich wird eine CSV-Fassung (`{STEM}_systembezug.csv`) erzeugt, die die Analyse weiter
unten als Eingabe verwendet.

---

## Analyse A — Inferenzgraph & Metriken

**Notebook:** `inferenzgraph_analyse_kapitel_final_V3.ipynb`
**Eingabe:** `{STEM}_stufe1.json`, `{STEM}_stufe2_inter.json`, `{STEM}_systembezug.csv`.

Aus Propositionen (Knoten, gefärbt nach Systembezug) und Relationen (Kanten,
Grund → gestützte Aussage) wird mit `networkx` ein Graph konstruiert. Das Notebook berechnet
u. a.: tragende Knoten (global), unbegründete „Fundamentalbehauptungen", Relationstyp-
Verteilung, inferentielle Vernetzung pro Kapitel, Konnektoranalyse, Zentralitätsmetriken,
Systembezug-Verteilung pro Kapitel, systemgrenzenüberschreitende Kanten,
Verknüpfungsmuster (LIT-NLIT) sowie eine kapitelweise interaktive Visualisierung.

**Zentralität wird in drei klar getrennten Varianten berechnet** (V3):

1. **Betweenness (roh)** — absolute Zahl kürzester Pfade durch den Knoten. Als
   Rangordnung nur **innerhalb** eines Kapitels bzw. einer Komponente interpretierbar.
   Die komponentenweise Berechnung reproduziert die früheren kapitelweisen Rohwerte exakt.
2. **Betweenness (komponentennormalisiert)** — Rohwert geteilt durch (k−1)(k−2) der
   eigenen schwachen Komponente (Größe k). Kapitelübergreifend skalengleich; begünstigt
   jedoch Kleinstkomponenten (Mittelknoten einer Dreierkette = 0.5) und dient daher
   Mittelwert- und Anteilsvergleichen, **nicht** als alleiniges Ranking.
3. **Cross-System-Betweenness** — Anzahl kürzester Pfade zwischen `LIT`- und
   `NLIT`-Propositionen (beide Richtungen) durch den Knoten: die absolute
   **Vermittlungslast zwischen den Systemen**; Grundlage des Top-Brücken-Rankings.

Ergänzend: **Brücken-Score** (min(#LIT-Nachbarn, #NLIT-Nachbarn); > 0 genau dann, wenn
der Knoten real beide Systeme verbindet) und **Komponentengröße**. Die frühere Spalte
„Dichte" heißt jetzt **Relationen pro Proposition** (Kanten je Knoten); die korrekt
definierte **Graphdichte (gerichtet)** (m/(n·(n−1))) wird als eigene Spalte ausgewiesen.

**Ausgabe:** `{STEM}_metriken.xlsx` mit den Blättern *Knotenmetriken · Kantenliste ·
Dichte pro Kapitel · Typverteilung · Systembezug pro Kapitel*.
Spalten *Knotenmetriken*: `… · In-Degree · Out-Degree · Betweenness (roh) ·
Betweenness (komponentennormalisiert) · Cross-System-Betweenness · Brücken-Score ·
Komponentengröße · Relationstyp`; Spalten *Dichte pro Kapitel*: `… · Vernetzungsgrad ·
Relationen pro Proposition · Graphdichte (gerichtet) · Komponenten · Größte Komponente`.

---

## Analyse B — Systembezug-Netzwerkanalyse

**Notebook:** `systembezug_netzwerk_analyse.ipynb`
**Eingabe:** `{STEM}_metriken.xlsx` (die Metrik-Datei **mit** Systembezug).

Vertiefende Auswertung der Systemverknüpfung: Systembezug-Verteilung; die **vermittelte
Grenze** (Kanten über die Systemgrenze laufen überwiegend über `LIT-NLIT`-Brücken);
Zentralität nach Systembezug (kapitelübergreifende Klassenvergleiche ausschließlich über
die **skalengleichen** Metriken: komponentennormalisierte und Cross-System-Betweenness);
„Woran wird Literatur geknüpft?" (häufigste NLIT-Gegenstände); **Top-Brücken nach
Cross-System-Betweenness** (Anzahl vermittelter kürzester LIT↔NLIT-Pfade; Sekundär­kriterium
rohe Betweenness); die **Begründungsrichtungen** über die Systemgrenze (Achsenmodell
NLIT < LIT-NLIT < LIT; eine systemüberschreitende Relation gilt als aufwärts gerichtet,
wenn die gestützte Aussage höher liegt als ihr Grund: 60,9 % der 4 203 Kanten, in allen
15 Kapiteln überwiegend); sowie die **diachrone Entwicklung** über die Epochen (zwei Diagramme).

**Spitzenknoten-Analyse (Abschnitt 4b).** Für jedes Epochenkapitel und jedes
Inferenznetzwerk (schwache Komponente mit max. Betweenness > 0) wird bestimmt, welcher
Systembezug-Klasse der zentralste Knoten angehört. **Gleichstandsbehandlung
(klasseneindeutige Auflösung):** Teilen sich mehrere Knoten den Spitzenwert, wird das
Netzwerk der Klasse zugerechnet, sofern alle punktgleichen Knoten derselben Klasse
angehören; nur klassengemischte Gleichstände bleiben unentscheidbar und werden
ausgewiesen und ausgeschlossen. Ergebnisse: Auf Kapitelebene stellt in 8 der 15 Kapitel
eindeutig eine `LIT`-Proposition den Spitzenknoten (je 1× `LIT-NLIT`, 3× `NLIT`; 3 Kapitel
klassenambig, `LIT` jeweils im Gleichstand vertreten). Auf Netzwerkebene entfallen von
2 167 klasseneindeutigen Spitzenknoten (von 2 329 bestimmbaren; 162 klassenambig)
54,1 % auf `LIT`, 30,0 % auf `LIT-NLIT` und 15,8 % auf `NLIT` — gemessen an den
Basisraten unter den vernetzten Propositionen (55,5 / 27,6 / 16,8 %) ist `LIT` damit
leicht unter-, `LIT-NLIT` leicht überrepräsentiert. Alternative Gleichstands­behandlungen
(anteilige Zurechnung: 52,9/31,1/16,0 %; Ausschluss aller Gleichstände: 52,9/31,4/15,7 %)
bestätigen den Befund; das Blatt *Robustheit Gleichstände* dokumentiert alle Varianten.

**Ausgabe:** `nlit_gegenstaende_top40.xlsx`, `lit_nlit_bruecken_top.xlsx`,
`entwicklung_ueber_zeit.xlsx`, `spitzenknoten_analyse.xlsx` (Blätter *Spitzenknoten je
Kapitel · Spitzenknoten je Netzwerk · Robustheit Gleichstände*) sowie die Diagramme
`spitzenknoten_je_kapitel.png` (Grundlage für Abbildung 2; klassenambige Kapitel
schraffiert markiert) und `spitzenknoten_vs_bestand.png`.

---

## Evaluation — Validierung der Annotationen

Die Annotationsqualität wurde in drei Erhebungen geprüft. Alle folgen demselben Aufbau:
zunächst das **Inter-Annotator-Agreement** (IAA, Cohen's κ) zweier Annotator:innen, dann
die **Modellgüte** gegen die übereinstimmenden Urteile (`scikit-learn`).

| Erhebung | Notebook | Einheit | Umfang | Reichweite |
|---|---|---|---|---|
| **A — Intra-Satz-Relationen** (Hauptevaluation) | `eval_precision_recall.ipynb` | Propositions**paare** | 353 Paare / 105 Sätze | alle 15 Kapitel, geschichtet |
| **B — Systembezug** | `eval_systembezug.ipynb` | Propositionen | 106 | Kapitel 1, Sätze 1–32 |
| **C — Plausibilität** (Vorstudie) | `eval_plausibility.ipynb` | Propositionen | 105 | Kapitel 1, Sätze 1–39 |

Erhebung C war die erste Validierung; ihre Grenzen (kein Recall bestimmbar, nur ein
Kapitel, PR-INK nicht vertreten) waren der Anlass für Erhebung A. Beide Erhebungen messen
**verschiedene Einheiten** und sind nicht ineinander umrechenbar; C bleibt als Vorstudie
dokumentiert.

---

### Evaluation A — Intra-Satz-Relationen (Precision/Recall/F1)

**Skript:** `stichprobe_ziehung.py` → **Notebook:** `eval_precision_recall.ipynb`
**Richtlinienstand:** V9 (Modell) + V9.1 Addendum (menschliche Annotation)
**Ausgabe:** `data/intra_relationen_eval_ergebnisse.xlsx` — Blätter
*Zusammenfassung · Plausibilität pro Typ · Fehler (FP-FN) · Disagreements*.

#### A.1 Stichprobenziehung

```bash
python stichprobe_ziehung.py data/Beutin_complete_Direktzitat_stufe1.xlsx
```

| Parameter | Wert |
|---|---|
| Seed | `20260706` |
| Rahmen | Sätze mit 2–6 Propositionen, ohne Kapitel `(Unbekannt)` — 7 979 Sätze (95 % der paarfähigen) |
| Schichtung | Kapitel (15) × Modell-Signal (4) |
| Modell-Signal | `UNA-only` (keine Modellrelation) · `nur BER` · `mit FLG` · `mit INK` |
| Allokation je Kapitel | 2 / 3 / 1 / 1 |
| Gezogen | 105 Sätze, **353 Propositionspaare** |
| Gewicht | N_Schicht / n_Schicht (Satzebene; Paare erben das Gewicht ihres Satzes) |

Die Schichtung nach Modell-Signal sichert, dass die seltenen Typen `PR-FLG` und `PR-INK`
überhaupt in der Stichprobe erscheinen; die Gewichte machen die Hochrechnung auf den
Rahmen möglich. Der Schlüssel (`data/stichprobe_schluessel.xlsx`) dokumentiert je
gezogenem Satz Kapitel, Schicht, Propositionszahl, Schichtgrößen und Gewicht.

#### A.2 Urteilsdesign

Beurteilt werden **alle** Propositionspaare der gezogenen Sätze — auch die, für die das
Modell keine Relation annotiert hat. Erst dadurch sind Precision **und** Recall
bestimmbar; das unterscheidet Erhebung A grundlegend von der Vorstudie C.

Das Urteil ist **streng**: »nicht plausibel« umfasst neben einer falsch angenommenen
Relation auch **falschen Relationstyp und falsche Richtung** (V9.1 R5).

Die Bögen zeigen je Paar die Entscheidung des Modells — Typ und Richtung oder
»keine Relation« — und fragen, ob sie plausibel ist. Es handelt sich also um ein
**Plausibilitätsdesign mit sichtbarer Modellannotation**, nicht um ein Blinddesign. Ein
**Ankereffekt** zugunsten des Modells ist möglich; die berichteten Werte sind als obere
Schranke zu lesen. Die Entscheidung für dieses Design war pragmatisch: eine
Blindannotation aller 353 Paare hätte den Aufwand mehr als verdoppelt.

#### A.3 Inter-Annotator-Agreement

| | κ | Übereinstimmung | n |
|---|---:|---:|---:|
| gesamt | **0.524** | 89.5 % | 353 |
| nur Modellrelationen | 0.605 | 84.2 % | 101 |
| nur Nicht-Relationen | 0.319 | 91.7 % | 252 |

Der niedrige κ-Wert für die Nicht-Relationen ist ein **Prävalenzeffekt**: Bei 91.7 %
Übereinstimmung und stark schiefer Randverteilung (fast alle Urteile »plausibel«) fällt κ
systematisch niedrig aus, ohne dass die Urteile tatsächlich unzuverlässig wären. Die
rohe Übereinstimmung ist in dieser Konstellation die aussagekräftigere Kennzahl.

Die **37 Disagreements** wurden **nicht adjudiziert, sondern ausgeschlossen**. Damit
beruhen die Metriken auf **316 entschiedenen Paaren**. Das Blatt *Disagreements*
dokumentiert sie vollständig mit beiden Urteilen und Anmerkungen.

#### A.4 Ergebnisse

| Kennzahl | ungewichtet | schichtgewichtet |
|---|---:|---:|
| Accuracy | **0.918** | — |
| Precision | **0.765** | 0.818 |
| Recall | **0.915** | 0.967 |
| F1 | **0.833** | 0.886 |

Konfusion: TP 65 · FP 20 · FN 6 · TN 225. Die gewichteten Werte rechnen auf den Rahmen
hoch und fallen höher aus, weil die relationsarmen Schichten im Korpus stärker vertreten
sind als in der Stichprobe.

Nach Modellannotation:

| Modellannotation | n | plausibel | Anteil |
|---|---:|---:|---:|
| keine Relation | 231 | 225 | 97.4 % |
| PR-BER | 55 | 51 | 92.7 % |
| PR-FLG | 16 | 14 | 87.5 % |
| **PR-INK** | **14** | **0** | **0 %** |

Das Muster ist asymmetrisch: Das Modell **übersieht kaum Relationen** (6 FN, Recall 0.915),
nimmt aber **zu viele an** (20 FP, Precision 0.765). Von den 20 Falschpositiven entfallen
14 auf PR-INK.

#### A.5 Der PR-INK-Befund

Keine der 14 als `PR-INK` annotierten Relationen wurde von beiden Annotator:innen als
plausibel beurteilt. Die Ursache ist eine **Spezifikationsschwäche in V9**: Die
Typentabelle führt »sondern«, »aber (bei Negation)« und »nicht … sondern« als Konnektoren
der Inkompatibilität auf. Das sind jedoch Marker **kontrastiver Korrektur** — eine Lesart
wird zurückgenommen und ersetzt —, keine Festlegungen, die einander wechselseitig die
Berechtigung entziehen. Das Modell hat die Richtlinie befolgt; der Fehler liegt in der
Richtlinie.

**Konsequenz für die Richtlinien.** V9.1 Addendum R1 streicht die kontrastiven Konnektoren
aus der PR-INK-Liste und verlangt den expliziten Inkompatibilitätstest. Die **Prompts
wurden nicht nachgeführt**, damit das ausgelieferte Korpus unter einem einheitlichen
Richtlinienstand erzeugt bleibt. Eine Neuextraktion unter V9.1 steht aus.

**Konsequenz für die Befunde.** PR-INK stellt 907 der 15 578 Kanten (5,8 %), davon 863
intra-satzlich. Eine Robustheitsrechnung entfernt sie versuchsweise aus dem Graphen:

| | mit PR-INK | ohne PR-INK |
|---|---:|---:|
| Kanten | 15 578 | 14 683 |
| isolierte Propositionen | 8 243 | 9 144 (+10,9 %) |
| Isolationsrate | 28,0 % | 31,1 % |
| nicht-triviale Komponenten | 5 805 | 5 763 |
| größte Komponente | 22 | 22 |
| Ø Komponentengröße | 3,65 | 3,52 |

Die tragenden Befunde — hohe Isolationsrate, viele kleine Begründungsinseln, Obergrenze
der größten Komponente bei 22 Knoten — bleiben in beiden Varianten bestehen. Die
Isolationsrate steigt um gut drei Prozentpunkte, was die Richtung des Befundes verstärkt
statt sie zu gefährden.

#### A.6 Reichweite

Die Beschränkung auf Kapitel 1 ist für die Inferenzebene **aufgehoben**: Erhebung A deckt
alle 15 Kapitel und alle vier Relationstypen ab. Es bleiben drei Vorbehalte:

1. **Nur Intra-Satz-Relationen.** Für Inter-Satz-Relationen (5 814 Relationen, Stufe 2)
   liegen keine Paarmetriken vor. Eine analoge Erhebung auf Satzpaarebene steht aus.
2. **Rahmenausschluss.** Sätze mit mehr als 6 Propositionen (5 % der paarfähigen Sätze)
   sind nicht erfasst; bei ihnen ist die Paarzahl und vermutlich auch die Fehlerrate höher.
3. **Ankereffekt.** Die sichtbare Modellannotation kann die Urteile zugunsten des Modells
   verschoben haben.

---

### Evaluation B — Systembezug und Gegenstandsextraktion

**Notebook:** `eval_systembezug.ipynb`
**Eingabe:** Annotator-Stichprobe (`…_EVAL_V1.xlsx`, zwei Blätter) und LLM-Klassifikat
(`…_classify_systembezug.xlsx`). Im Modus `BOTH` (Standard) wird der Goldstandard aus den
**übereinstimmenden Annotationen** der beiden Annotator-Blätter gebildet; eine separate
Goldstandard-Datei wird nur im Modus `EVAL` verwendet.
**Verfahren:** Teil A IAA (Cohen's κ, Konfusionsmatrix); Teil B LLM-Klassifikation gegen den
Goldstandard (Accuracy, κ, Pro-Label-Precision/Recall/F1, eigener Fokus auf die
LIT-NLIT-Erkennung); Fehleranalyse.
**Ergebnis (N = 106):** IAA Cohen's κ = 1.000 (100 % Übereinstimmung); LLM vs. Goldstandard
Accuracy 96.2 %, κ = 0.823; LIT-NLIT-Erkennung Precision 0.889 / Recall 0.800 / F1 0.842;
pro Label NLIT F1 0.984, LIT-NLIT 0.842, LIT 0.667.
**Ausgabe:** `systembezug_eval_ergebnisse.xlsx` — Blätter *Zusammenfassung · CM IAA ·
CM LLM vs Gold · Pro-Label-Metriken · Fehler*.

> **Reichweite — hier unverändert eingeschränkt.** Die Stichprobe stammt ausschließlich
> aus dem ersten Kapitel (*Mittelalterliche Literatur*, Sätze 1–32). Der Pro-Label-Wert
> für `LIT` beruht auf nur **3 Goldfällen** und ist entsprechend instabil (F1 0.667).
> Die Kennzahlen sind daher nicht ohne Weiteres auf das Gesamtkorpus übertragbar; eine
> über Kapitel geschichtete Stichprobe nach dem Muster von Evaluation A steht aus.

---

### Evaluation C — Plausibilität der Inferenzen (Vorstudie)

**Notebook:** `eval_plausibility.ipynb`
**Eingabe:** `Beutin_complete_INF+System_EVAL_V1.xlsx` (zwei Annotator-Blätter mit
Plausibilitätsurteilen über die modellgenerierten Annotationen).
**Verfahren:** IAA über das Plausibilitätsurteil → Goldstandard (übereinstimmende
Annotationen) → Post-hoc-Plausibilitätsmetriken, getrennt nach Fallart und Relationstyp.
**Ergebnis (N = 105, davon 97 entschieden):** IAA Cohen's κ = 0.653 bei 92.4 %
Übereinstimmung; Extraktionspräzision 100 % (60/60), Korrektheit der Nicht-Extraktion
(PR-UNA) 75.7 % (28/37), Gesamtplausibilität 90.7 % (88/97). Pro Typ: PR-BER und PR-FLG
je 100 % plausibel, PR-UNA 75.7 %; **PR-INK ist in dieser Stichprobe nicht vertreten**.
**Ausgabe:** `Beutin_complete_INF+System_eval_ergebnisse.xlsx` — Blätter
*Zusammenfassung · Performance pro Typ · Nicht-plausible Relationen · Disagreements*.

> **Status.** Evaluiert wurden post hoc nur die **vom Modell erzeugten** Annotationen,
> nicht alle Propositionspaare. Recall und F1 sind in diesem Design nicht bestimmbar.
> Die Erhebungseinheit ist die **Proposition**, nicht das Paar; PR-UNA erscheint hier als
> Eigenschaft einer Proposition, in Evaluation A dagegen als Urteil über ein Paar. Die
> Kennzahlen von A und C sind deshalb **nicht vergleichbar** und sollten nicht
> nebeneinander zitiert werden. Erhebung C bleibt als Vorstudie dokumentiert, weil sie
> den Entwurf von A begründet.

---

## Reproduktion — Ausführungsreihenfolge

1. PDF bereitstellen → **Stufe 1** ausführen → `…_stufe1.{json,csv,xlsx}`.
2. **Stufe 2** ausführen → `…_gesamt.{xlsx,csv}`, `…_stufe2_inter.{json,csv}`.
3. **Ebene 1–2** (Systembezug/Gegenstände) ausführen → `…_gesamt_sytembezug.xlsx`,
   `…_systembezug.csv`.
4. **Analyse A** ausführen → `…_metriken.xlsx` (Spaltenformat V3).
5. **Analyse B** ausführen → Top-Gegenstände, Brücken, Diachronie
   (läuft dank Kompatibilitätsmodus auch mit Metrik-Dateien im alten Format).
6. **(optional) Evaluation.**
   a. `python stichprobe_ziehung.py …_stufe1.xlsx` → Stichprobe und Schlüssel
      (reproduziert mit Seed 20260706 exakt die ausgelieferte Ziehung).
   b. Annotationsbögen A/B ausfüllen (Richtlinien V9 + V9.1 Addendum).
   c. `eval_precision_recall.ipynb` → `intra_relationen_eval_ergebnisse.xlsx`.
   d. `eval_systembezug.ipynb` → `systembezug_eval_ergebnisse.xlsx`.

**Hinweise.** Die Notebooks lesen ihre Eingaben teils als **JSON/CSV** (nicht als XLSX);
die Pfadkonstanten am Anfang jedes Notebooks ggf. anpassen. Die generativen Schritte sind
kosten- und laufzeitintensiv (29 448 Propositionen, kapitel-/paarweise API-Aufrufe) —
deshalb die Checkpoint-Logik. Zwischendateien (`…_stufe1.json`, `…_stufe2_inter.json`,
`…_systembezug.csv`) müssen für die Analyse vorliegen. Die **ausgefüllten
Annotationsbögen** sind aus urheberrechtlichen Gründen nicht Teil des Repositories (sie
führen den Satzwortlaut mit); Schritt 6c lässt sich daher nur mit lokal erzeugten Bögen
nachvollziehen, während die Ergebnisdatei und der Ziehungsschlüssel beiliegen.

---

## Methodische Vorbehalte

- **Fensterbreite.** Inter-Satz-Relationen werden nur zwischen *unmittelbar*
  aufeinanderfolgenden Sätzen erhoben (≈ 99 % der Inter-Kanten verbinden benachbarte Sätze).
  Das begünstigt die Detektion **lokaler** gegenüber weitreichenden Begründungs­
  zusammenhängen; der Befund vieler kleiner „Begründungsinseln" ist daher teilweise von
  dieser Setzung mitbedingt und sollte durch Variation der Reichweite auf Robustheit
  geprüft werden.
- **Gültigkeitsbereiche der Zentralitätsmetriken.** Die rohe Betweenness ist eine absolute
  Pfadzählung und nur kapitel-/komponentenintern vergleichbar; kapitelübergreifende
  Vergleiche und Rankings verwenden ausschließlich die komponentennormalisierte bzw. die
  Cross-System-Betweenness (Definitionen in Analyse A). „Relationen pro Proposition" ist
  keine Graphdichte im graphentheoretischen Sinn.
- **Gleichstände bei Spitzenknoten.** In 23 % der Netzwerke mit bestimmbarem Spitzenknoten
  teilen sich mehrere Knoten den Höchstwert (strukturell bedingt, z. B. Ketten gerader
  Länge). Alle Spitzenknoten-Anteile beruhen auf der klasseneindeutigen Auflösung
  (s. Analyse B); klassengemischte Gleichstände werden ausgewiesen, alternative
  Behandlungen als Robustheitsvarianten mitberichtet. Frühere Fassungen mit
  Gleichständen als eigener Restkategorie sind mit den aktuellen Anteilen nicht direkt
  vergleichbar.
- **PR-INK ist nicht validiert.** 0 von 14 Fällen der Hauptevaluation wurden als plausibel
  beurteilt; Ursache ist die Konnektorliste in V9 (s. Evaluation A.5). Befunde, die
  wesentlich auf PR-INK-Kanten beruhen, sind mit Vorbehalt zu lesen; die
  Robustheitsrechnung zeigt, dass die Strukturbefunde nicht davon abhängen.
- **Reichweite der Evaluation.** Für die **Intra-Satz-Relationen** ist die frühere
  Beschränkung auf Kapitel 1 aufgehoben (geschichtete Stichprobe über alle 15 Kapitel,
  alle Typen). Nicht evaluiert sind die **Inter-Satz-Relationen**; die
  **Systembezug-Evaluation** stammt weiterhin allein aus Kapitel 1 und stützt sich bei
  `LIT` auf nur 3 Goldfälle. Das Plausibilitätsdesign mit sichtbarer Modellannotation
  lässt einen Ankereffekt zu.
- **Beschreibungsanspruch.** Das Brandom-Modell dient als *Beschreibungsapparat* für Verknüpfungsmuster.

---

## Hinweis zur Erstellung

Die Notebooks in diesem Repository wurden **„vibe-coded"** — explorativ und KI-gestützt
entwickelt. Die damit erzeugten Ergebnisse (Propositionen, Relationen, Systembezug und
Metriken) wurden von den Verfasser:innen **manuell geprüft und validiert**.
