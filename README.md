# Inferentielle Analyse von Literaturgeschichten nach Robert Brandom

Dieses Repository enthält die Daten, Annotationsrichtlinien, Prompts und Auswertungs­notebooks
eines Projekts, das eine Literaturgeschichte (Beutin et al., *Deutsche Literaturgeschichte*)
mit den Mitteln von Robert Brandoms Inferentialismus rekonstruiert. Ziel ist es, die **impliziten Begründungs- und Verknüpfungsmuster** literaturgeschichtlichen Schreibens sichtbar zu machen:
Welche Propositionen stützen, erzwingen oder schließen einander aus, und wie wird das
Literatursystem mit dem Nicht-Literatursystem verknüpft?

Die Erschließung erfolgt in drei aufeinander aufbauenden Ebenen (Ebene 0–2), gefolgt von
einer graphen- und netzwerkbasierten Auswertung. Eine ausführliche Schritt-für-Schritt-
Beschreibung des Verfahrens steht in **[`PIPELINE.md`](./PIPELINE.md)**.

---

## Repository-Struktur

```
.
├── README.md                                  ← diese Datei (Überblick & Inhalt)
├── PIPELINE.md                                ← detaillierte Arbeitspipeline
│
├── guidelines/
│   ├── Brandom_Annotationsrichtlinien_V9.docx          ← Annotationsspezifikation (Ebene 0–2)
│   └── Brandom_Annotationsrichtlinien_V9-1_Addendum.docx ← Präzisierungen R1–R5 (verbindlich
│                                                           für die Hauptevaluation)
│
├── prompts/
│   ├── prompt_intra-satz_cot.md               ← System-Prompt Ebene 0 / Stufe 1
│   └── prompt_inter-satz_cot.md               ← System-Prompt Ebene 0 / Stufe 2
│
├── notebooks/
│   ├── stufe1_propositionsextraktion_kapitel_final.ipynb
│   ├── stufe2_inter_satz_relationen_kapitel_final.ipynb
│   ├── inferenzgraph_analyse_kapitel_final_V3.ipynb
│   ├── systembezug_netzwerk_analyse.ipynb
│   ├── eval_precision_recall.ipynb  ← Hauptevaluation Inferenzen (IAA + P/R/F1)
│   ├── eval_plausibility.ipynb      ← Vorstudie Inferenzen (Kapitel 1, Propositionsebene)
│   └── eval_systembezug.ipynb       ← Evaluation: Systembezug
│
├── stichprobe_ziehung.py                      ← Ziehung der Evaluationsstichprobe (Seed 20260706)
│
└── data/
    ├── Beutin_complete_Direktzitat_stufe1.xlsx
    ├── Beutin_complete_Direktzitat_gesamt_inf.xlsx
    ├── Beutin_complete_Direktzitat_gesamt_sytembezug.xlsx
    ├── Beutin_complete_Direktzitat_metriken.xlsx
    ├── stichprobe_schluessel.xlsx                         ← gezogene Sätze, Schichten, Gewichte
    ├── intra_relationen_eval_ergebnisse.xlsx              ← Hauptevaluation Inferenzen
    ├── Beutin_complete_INF+System_eval_ergebnisse.xlsx    ← Vorstudie Inferenzen
    └── systembezug_eval_ergebnisse.xlsx                   ← Eval-Ergebnisse Systembezug
```

---

## Inhalt im Detail

### `guidelines/` — Annotationsrichtlinien

**`Brandom_Annotationsrichtlinien_V9.docx`** ist die maßgebliche Spezifikation des
gesamten Verfahrens (9. Fassung). Sie definiert die theoretische Verortung, die
Extraktionsregeln, die vier Relationstypen, den Abgrenzungstest sowie alle drei Ebenen
und enthält ein vollständig durchgearbeitetes Beispiel:

1. Einleitung und Zielsetzung (theoretische Verortung, Architektur)
2. Ebene 0: Propositionen und ihre Relationen (Extraktion, Relationen, Richtung, Abgrenzungstest)
3. Ebene 1: Systembezug (Typen, Annotations- und Abgrenzungsregeln, Beispiele)
4. Ebene 2: Gegenstandsextraktion bei LIT-NLIT
5. Annotationsformat im Überblick
6. Durchgearbeitetes Beispiel (Klassik-Kapitel)
7. Hinweise zur LLM-Implementation

**`Brandom_Annotationsrichtlinien_V9-1_Addendum.docx`** ergänzt V9 um fünf Präzisierungen
(R1–R5), die im Zuge der Annotatorenschulung nötig wurden und für die **Hauptevaluation
verbindlich** sind: Behandlung kontrastiver Konnektoren, Abgrenzung von Aufzählung und
Begründung, Richtung bei Beleg-/Beispielrelationen, Umgang mit metadiskursiven Sätzen
sowie die Strenge des Plausibilitätsurteils (Typ- und Richtungsfehler gelten als
»nicht plausibel«). V9 bleibt der Stand, der in den Modell-Prompts operationalisiert ist;
das Addendum betrifft ausschließlich die menschliche Nachannotation. Beide Dokumente
zusammen sind der Referenzstand für die Reproduktion der Evaluation.

### `prompts/` — System-Prompts (Chain of Thought)

Die Prompts operationalisieren die Richtlinien für das Sprachmodell. Jeder Prompt erzwingt
einen expliziten dreistufigen Abgrenzungstest (Festlegungs-, Berechtigungs-, Inkompatibilitäts­test).

| Datei | Ebene/Stufe | Aufgabe |
|---|---|---|
| `prompt_intra-satz_cot.md` | Ebene 0 / Stufe 1 | Propositionsextraktion + Intra-Satz-Relationen |
| `prompt_inter-satz_cot.md` | Ebene 0 / Stufe 2 | Inter-Satz-Relationen zwischen aufeinanderfolgenden Sätzen |

### `notebooks/` — Pipeline und Auswertung

| Notebook | Funktion | Eingabe → Ausgabe |
|---|---|---|
| `stufe1_propositionsextraktion_kapitel_final.ipynb` | PDF-Erschließung + Stufe 1 | Beutin-PDF + Intra-Prompt → `…_stufe1.{xlsx,csv,json}` |
| `stufe2_inter_satz_relationen_kapitel_final.ipynb` | Stufe 2 + Zusammenführung | `…_stufe1.json/csv` + Inter-Prompt → `…_gesamt.{xlsx,csv}`, `…_stufe2_inter.{csv,json}` |
| `inferenzgraph_analyse_kapitel_final_V3.ipynb` | Graphkonstruktion + Metriken (Betweenness in drei Varianten, s. u.) | Stufe-1/2-JSON + Systembezug-CSV → `…_metriken.xlsx` |
| `systembezug_netzwerk_analyse.ipynb` | Systembezug-Netzwerkanalyse (kapitelübergreifende Vergleiche nur über skalengleiche Metriken) + Begründungsrichtungen über die Systemgrenze (Achsenmodell, aufwärts/abwärts) + Spitzenknoten-Analyse (zentralste Knoten je Kapitel/Netzwerk, klasseneindeutige Gleichstandsauflösung) | `…_metriken.xlsx` → Top-Gegenstände, Brücken, Diachronie, `begruendungsrichtungen.xlsx`, `spitzenknoten_analyse.xlsx` |
| `eval_precision_recall.ipynb` | **Hauptevaluation** Intra-Satz-Relationen: IAA + Precision/Recall/F1 auf Paarebene, ungewichtet und schichtgewichtet | Annotationsbögen A/B → `intra_relationen_eval_ergebnisse.xlsx` |
| `eval_plausibility.ipynb` | **Vorstudie**: Plausibilität der Inferenzen auf Propositionsebene (Kapitel 1) | Annotations-XLSX → `Beutin_complete_INF+System_eval_ergebnisse.xlsx` |
| `eval_systembezug.ipynb` | Evaluation: Systembezug (IAA + LLM vs. Goldstandard) | Annotations-/LLM-XLSX → `systembezug_eval_ergebnisse.xlsx` |

Modell durchgängig: `claude-opus-4-8`. API-Schlüssel über die Umgebungsvariable
`MY_ANTHROPIC`. Beide Extraktionsnotebooks schreiben Checkpoints (`checkpoint_batch_*` bzw.
`checkpoint_pair_*`), um lange Läufe wiederaufnehmen zu können.

### `stichprobe_ziehung.py` — Ziehung der Evaluationsstichprobe

Reproduziert mit `SEED = 20260706` exakt die Stichprobe der Hauptevaluation und schreibt
`data/stichprobe_schluessel.xlsx` (gezogene Sätze mit Kapitel, Schicht, Propositionszahl,
Schichtgrößen und Gewicht; **ohne** Originaltext). Aufruf:

```bash
python stichprobe_ziehung.py data/Beutin_complete_Direktzitat_stufe1.xlsx
```

Design und Kennzahlen der Ziehung stehen unten unter »Evaluation«.

### `data/` — Ergebnistabellen

Die Tabellen bilden die Stufen der Pipeline ab. **Spaltenwörterbuch:**

**`…_stufe1.xlsx`** — Blatt *Propositionen* (29 448 Zeilen)
`Kapitel · Satz-ID · Originaltext* · Propositions-ID · Proposition · Intra-Satz-Relationen · Relationstypen · Reasoning`

**`…_gesamt_inf.xlsx`** — Ebene 0 vollständig
- Blatt *Propositionen*: wie Stufe 1, zusätzlich `Inter-Satz-Relationen · Inter-Satz-Typen`
- Blatt *Inter-Satz-Relationen* (11 144 Zeilen, davon 5 814 Relationen und 5 330
  `[Keine Relation]`-Platzhalter für relationslose Satzpaare):
  `Kapitel · Satz A · Satz B · Von · Nach · Relationstyp · Konnektor · Reasoning`

**`…_gesamt_sytembezug.xlsx`** — Ebene 0 + Ebene 1 + Ebene 2
- Blatt *Propositionen*: zusätzlich `Systembezug · LIT-Gegenstand · NLIT-Gegenstand`
- Blatt *Verknüpfungen LIT-NLIT* (7 572 Zeilen): `Kapitel · Propositions-ID · Proposition · LIT-Gegenstand · NLIT-Gegenstand`

**`…_metriken.xlsx`** — Auswertung (enthält **keinen** Originaltext; Format von
`inferenzgraph_analyse_kapitel_final_V3.ipynb`)
- *Knotenmetriken* (29 446): `Propositions-ID · Kapitel · Satz-ID · Proposition ·
  Systembezug · LIT-Gegenstand · NLIT-Gegenstand · In-Degree · Out-Degree ·
  Betweenness (roh) · Betweenness (komponentennormalisiert) · Cross-System-Betweenness ·
  Brücken-Score · Komponentengröße · Relationstyp`
- *Kantenliste* (15 624): `von · nach · typ · konnektor · scope`
- *Dichte pro Kapitel* (16): `Kapitel · Propositionen · Relationen · Isolierte (PR-UNA) ·
  Vernetzungsgrad · Relationen pro Proposition · Graphdichte (gerichtet) · Komponenten ·
  Größte Komponente`
- *Typverteilung* (4): `Typ · Anzahl · Anteil · Intra · Inter`
- *Systembezug pro Kapitel* (16): `Kapitel · Propositionen · LIT · NLIT · LIT-NLIT · Ohne · LIT % · NLIT % · LIT-NLIT %`

**`stichprobe_schluessel.xlsx`** — Ziehungsschlüssel der Hauptevaluation (105 Zeilen):
`Satz-Nr · Satz-ID · Kapitel · Signal · n_props · N_Stratum · n_Stratum · Gewicht ·
moegl_Paare` sowie die Modellannotationen der gezogenen Sätze.

**`intra_relationen_eval_ergebnisse.xlsx`** — Ergebnisse der Hauptevaluation.
Blätter: *Zusammenfassung · Plausibilität pro Typ · Fehler (FP-FN) · Disagreements*.

\* Die `Originaltext`-Spalten sind in allen ausgelieferten Dateien **aus
urheberrechtlichen Gründen geleert** (vgl. »Wichtige Hinweise«); die Spalte bleibt
als Platzhalter erhalten, damit lokal erzeugte Fassungen spaltenkompatibel sind.

### Metriken: Definitionen und Gültigkeitsbereiche

- **Relationen pro Proposition** (»Dichte«): Kanten je Knoten, d. h. der halbe
  mittlere Grad. **Keine** Graphdichte im graphentheoretischen Sinn; diese steht —
  korrekt als m/(n·(n−1)) berechnet — in der Spalte **Graphdichte (gerichtet)** und
  liegt bei Graphen dieser Größenordnung erwartbar nahe null.
- **Betweenness (roh)**: absolute Zahl kürzester Pfade durch den Knoten. Als Rangordnung
  **nur innerhalb eines Kapitels bzw. einer Komponente** interpretierbar.
- **Betweenness (komponentennormalisiert)**: Rohwert geteilt durch (k−1)(k−2) der
  eigenen schwachen Komponente (Größe k). Kapitelübergreifend skalengleich, begünstigt
  aber Kleinstkomponenten (der Mittelknoten jeder Dreierkette erreicht 0.5) — nicht als
  alleiniges Ranking-Kriterium verwenden.
- **Cross-System-Betweenness**: Anzahl kürzester Pfade zwischen LIT- und
  NLIT-Propositionen (beide Richtungen) durch den Knoten — die absolute
  **Vermittlungslast zwischen den Systemen** und Grundlage des Top-Brücken-Rankings.
- **Brücken-Score**: min(#LIT-Nachbarn, #NLIT-Nachbarn); > 0 genau dann, wenn der Knoten
  tatsächlich beide Systeme verbindet.
- **Spitzenknoten** (zentralster Knoten eines Kapitels bzw. Inferenznetzwerks): Knoten
  mit der höchsten rohen Betweenness. **Gleichstandsbehandlung (klasseneindeutig):**
  Teilen sich mehrere Knoten den Spitzenwert, zählt das Netzwerk zur Klasse, sofern alle
  punktgleichen Knoten derselben Systembezug-Klasse angehören; klassengemischte
  Gleichstände (162 von 2 329 Netzwerken) werden ausgewiesen und ausgeschlossen.
  Ergebnisse: Kapitelebene 8 der 15 Kapitel eindeutig `LIT` (1× `LIT-NLIT`, 3× `NLIT`,
  3 klassenambig); Netzwerkebene (n = 2 167): `LIT` 54,1 %, `LIT-NLIT` 30,0 %, `NLIT`
  15,8 % gegenüber Basisraten von 55,5 / 27,6 / 16,8 % unter den vernetzten
  Propositionen — `LIT-NLIT` als Spitzenknoten leicht überrepräsentiert. Alternative
  Gleichstandsbehandlungen bestätigen den Befund (Blatt *Robustheit Gleichstände* in
  `spitzenknoten_analyse.xlsx`).
- Kapitelübergreifende Klassenvergleiche (Ø-Zentralität nach Systembezug, Top-Brücken)
  verwenden ausschließlich die normalisierten bzw. Cross-System-Werte.

---

## Evaluation — Validierung der Annotationen

Die Annotationsqualität wurde in drei Erhebungen geprüft. Alle folgen demselben Aufbau:
zunächst das **Inter-Annotator-Agreement** (IAA, Cohen's κ) zweier Annotator:innen, dann
die **Modellgüte** gegen die übereinstimmenden Urteile (`scikit-learn`).

| Erhebung | Notebook | Einheit | Umfang | Reichweite |
|---|---|---|---|---|
| **Hauptevaluation Inferenzen** | `eval_precision_recall.ipynb` | Propositions**paare** | 353 Paare aus 105 Sätzen | alle 15 Kapitel, geschichtet |
| Vorstudie Inferenzen | `eval_plausibility.ipynb` | **Propositionen** | 105 Propositionen | Kapitel 1, Sätze 1–39 |
| Systembezug | `eval_systembezug.ipynb` | Propositionen | 106 Propositionen | Kapitel 1, Sätze 1–32 |

Die Vorstudie bleibt dokumentiert, weil sie den Entwurf der Hauptevaluation begründet;
ihre Kennzahlen sind mit denen der Hauptevaluation **nicht vergleichbar** (andere
Erhebungseinheit, anderer Rahmen, anderes Urteilskriterium).

### Hauptevaluation — Intra-Satz-Relationen (Precision/Recall/F1)

**Notebook:** `eval_precision_recall.ipynb` → `data/intra_relationen_eval_ergebnisse.xlsx`
**Richtlinienstand:** V9 (Modell) + V9.1 Addendum (menschliche Annotation).

**Stichprobendesign.** Rahmen sind alle Sätze mit 2–6 Propositionen außerhalb des
Pseudo-Kapitels `(Unbekannt)` (7 979 Sätze, 95 % der paarfähigen Sätze des Korpus).
Geschichtet wird nach **Kapitel (15) × Modell-Signal** (`UNA-only`, `nur BER`, `mit FLG`,
`mit INK`) mit der Allokation 2/3/1/1 je Kapitel; gezogen wurden 105 Sätze mit insgesamt
**353 Propositionspaaren**. Jede Schicht trägt das Gewicht N_Schicht / n_Schicht; Paare
erben das Gewicht ihres Satzes. Die Ziehung ist mit `stichprobe_ziehung.py`
(Seed 20260706) reproduzierbar, der Schlüssel liegt als `data/stichprobe_schluessel.xlsx` bei.

**Urteilsdesign.** Beurteilt werden **alle** Paare der gezogenen Sätze, also auch die vom
Modell nicht annotierten. Damit sind Precision **und** Recall bestimmbar. Das Urteil ist
**streng**: »nicht plausibel« umfasst neben einer falsch angenommenen Relation auch
falschen Relationstyp und falsche Richtung. Die Bögen zeigen die Modellentscheidung
(Plausibilitätsdesign mit sichtbarer Modellannotation, kein Blinddesign); ein
**Ankereffekt** zugunsten des Modells ist damit möglich und wird unten als Vorbehalt
geführt.

**Inter-Annotator-Agreement.** Cohen's κ = **0.524** bei 89.5 % Übereinstimmung
(N = 353). Getrennt: κ = 0.605 für die vom Modell annotierten Relationen (84.2 %,
n = 101), κ = 0.319 für die Nicht-Relationen (91.7 %, n = 252). Der niedrige κ-Wert der
zweiten Gruppe ist ein **Prävalenzeffekt** — bei 91.7 % Übereinstimmung und stark
schiefer Randverteilung fällt κ systematisch niedrig aus. Die 37 Disagreements wurden
**nicht adjudiziert, sondern aus der Metrikberechnung ausgeschlossen**; es verbleiben
316 entschiedene Paare.

**Modellgüte (316 entschiedene Paare).**

| Kennzahl | ungewichtet | schichtgewichtet |
|---|---:|---:|
| Accuracy | **0.918** | — |
| Precision | **0.765** | 0.818 |
| Recall | **0.915** | 0.967 |
| F1 | **0.833** | 0.886 |

Konfusion: TP 65 · FP 20 · FN 6 · TN 225. Die gewichteten Werte rechnen auf den Rahmen
(Sätze mit 2–6 Propositionen) hoch und liegen höher, weil die relationsarmen Schichten im
Korpus stärker vertreten sind als in der Stichprobe.

**Nach Modellannotation.**

| Modellannotation | n | plausibel | Anteil |
|---|---:|---:|---:|
| keine Relation | 231 | 225 | 97.4 % |
| PR-BER | 55 | 51 | 92.7 % |
| PR-FLG | 16 | 14 | 87.5 % |
| **PR-INK** | **14** | **0** | **0 %** |

**Befund PR-INK.** Keine einzige der 14 als PR-INK annotierten Relationen wurde von
beiden Annotator:innen als plausibel beurteilt. Die Ursache ist eine **Spezifikations­
schwäche in V9**: Die Typentabelle führt »sondern«, »aber (bei Negation)« und
»nicht … sondern« als Konnektoren der Inkompatibilität auf. Das sind jedoch Marker
**kontrastiver Korrektur** — der Sprecher nimmt eine Lesart zurück und ersetzt sie —,
keine Festlegungen, die einander wechselseitig die Berechtigung entziehen. Das Modell hat
die Richtlinie insofern korrekt befolgt; die Fehlklassifikation geht auf die Richtlinie
zurück, nicht auf das Modell. V9.1 Addendum R1 korrigiert dies für die menschliche
Annotation; die Prompts wurden **nicht** nachgeführt, damit das ausgelieferte Korpus
konsistent unter einem Richtlinienstand erzeugt bleibt.

**Robustheit des Graphen gegenüber PR-INK.** PR-INK macht 907 Kanten des Gesamtgraphen
aus (863 davon intra-satzlich), 5,8 % aller Kanten. Werden sie versuchsweise entfernt,
ändert sich die Struktur nur geringfügig:

| | mit PR-INK | ohne PR-INK |
|---|---:|---:|
| Kanten | 15 578 | 14 683 |
| isolierte Propositionen | 8 243 | 9 144 (+10,9 %) |
| Isolationsrate | 28,0 % | 31,1 % |
| nicht-triviale Komponenten | 5 805 | 5 763 |
| größte Komponente | 22 | 22 |
| Ø Komponentengröße | 3,65 | 3,52 |

Die zentralen Befunde — hohe Isolationsrate, viele kleine Begründungsinseln, Obergrenze
der größten Komponente bei 22 Knoten — bleiben unter beiden Varianten bestehen.

**Reichweite.** Die Hauptevaluation deckt alle 15 Kapitel und alle vier Relationstypen
ab; die Beschränkung früherer Fassungen auf Kapitel 1 ist damit für die Inferenzebene
**aufgehoben**. Es bleiben drei Vorbehalte: (a) Evaluiert sind ausschließlich
**Intra-Satz-Relationen**; für Inter-Satz-Relationen liegen keine Paarmetriken vor.
(b) Der Rahmen schließt Sätze mit mehr als 6 Propositionen aus (5 % der paarfähigen
Sätze). (c) Das sichtbare Modellurteil kann einen Ankereffekt erzeugt haben; die
berichteten Werte sind insofern als **obere Schranke** zu lesen.

### Vorstudie — Plausibilität auf Propositionsebene

**Notebook:** `eval_plausibility.ipynb` → `data/Beutin_complete_INF+System_eval_ergebnisse.xlsx`

Erste Erhebung auf **Propositionsebene** (N = 105, davon 97 entschieden) aus Kapitel 1,
Sätze 1–39. IAA Cohen's κ = 0.653 bei 92.4 % Übereinstimmung. Extraktionspräzision 100 %
(60/60 extrahierte Relationen plausibel), Korrektheit der Nicht-Extraktion (PR-UNA)
75.7 % (28/37), Gesamtplausibilität 90.7 % (88/97). Recall und F1 sind in diesem Design
nicht bestimmbar, weil nur die vom Modell erzeugten Annotationen beurteilt wurden.
PR-INK ist in dieser Stichprobe nicht vertreten.

Die Grenzen dieses Designs — fehlender Recall, Beschränkung auf ein Kapitel, PR-INK nicht
abgedeckt — waren der Anlass für die Hauptevaluation. Die Zahlen bleiben hier als
Vorstudie dokumentiert und sollten nicht neben den Paarmetriken zitiert werden.

### Systembezug und Gegenstandsextraktion

**Notebook:** `eval_systembezug.ipynb` → `data/systembezug_eval_ergebnisse.xlsx`

N = 106 Propositionen aus Kapitel 1 (Sätze 1–32). IAA Cohen's κ = 1.000 (100 %
Übereinstimmung); LLM vs. Goldstandard Accuracy 96.2 %, κ = 0.823; LIT-NLIT-Erkennung
Precision 0.889 / Recall 0.800 / F1 0.842.

**Reichweite.** Für die Systembezug-Evaluation besteht die Beschränkung auf Kapitel 1
**unverändert fort**. Hinzu kommt, dass die Pro-Label-Metriken für `LIT` auf nur
**3 Goldfällen** beruhen und entsprechend instabil sind (F1 0.667). Die Kennzahlen dieser
Erhebung sind daher nicht ohne Weiteres auf das Gesamtkorpus übertragbar; eine über
Kapitel geschichtete Stichprobe nach dem Muster der Inferenz-Hauptevaluation steht aus.

---

## Bekannte Datenartefakte

Die ausgelieferten Ergebnisdaten enthalten quantifizierte Restfehler der automatischen
Extraktion, die bei der Interpretation zu berücksichtigen sind:

- Ein Pseudo-Kapitel **`(Unbekannt)`** (11 Propositionen aus 5 Sätzen mit vom Modell
  erfundenen Satz-IDs) läuft als eigene Zeile durch die Kapitel-Blätter; die inhaltlichen
  »16 Kapitel« sind real 15 Kapitel plus dieses Artefakt. Der Evaluationsrahmen schließt
  es aus.
- **2 duplizierte Propositions-IDs** (`P(11066.1/2)`) mit unterschiedlichen Texten; der
  Graph führt sie zusammen (daher 29 446 Knoten bei 29 448 Propositionszeilen).
- **15 Selbstschleifen** und **11 Kanten vom Typ PR-UNA** in der Kantenliste
  (schemawidrig, da PR-UNA »kein Paar« bedeutet); **53 als `intra` markierte Kanten**
  verbinden Propositionen verschiedener Sätze; **31 parallele Kantenpaare** werden im
  Graphen dedupliziert.
- Auf kürzeste Pfade und damit auf alle Betweenness-Werte haben Selbstschleifen keinen
  Einfluss; der Brücken-Score schließt sie explizit aus.
- **PR-INK ist als Relationstyp nicht validiert** (0/14 in der Hauptevaluation, s. o.).
  Befunde, die wesentlich auf PR-INK-Kanten beruhen, sind mit Vorbehalt zu lesen; die
  Robustheitstabelle oben zeigt, dass die Strukturbefunde davon nicht abhängen.

---

## Begriffe in Kürze

**Relationstypen (Ebene 0).**
`PR-FLG` festlegungserhaltend (die Prämisse *erzwingt* die Konklusion; selten) ·
`PR-BER` berechtigungserhaltend (die Prämisse *berechtigt* defeasibel) ·
`PR-INK` Inkompatibilität (Festlegung auf das eine schließt die Berechtigung zum anderen aus) ·
`PR-UNA` ohne inferentielle Beziehung (isoliert).

**Systembezug (Ebene 1).**
`LIT` literarisch · `NLIT` nicht-literarisch · `LIT-NLIT` systemverknüpfende Brücke.

---

## Voraussetzungen & Setup

- Python ≥ 3.10
- Pakete: `anthropic`, `pdfplumber`, `pandas`, `openpyxl`, `networkx`, `matplotlib`,
  `numpy`, `scikit-learn` (Evaluation); für die interaktive Visualisierung zusätzlich
  `pyvis`/`plotly`
- Umgebungsvariable `MY_ANTHROPIC` mit gültigem Anthropic-API-Schlüssel
- Modell: `claude-opus-4-8`

---

## Wichtige Hinweise

**Urheberrecht.** Das Eingangskorpus (Beutin et al., *Deutsche Literaturgeschichte*) ist
**nicht** Teil dieses Repositories: https://doi.org/10.1007/978-3-476-04953-7
Die Felder `Proposition` und `Reasoning` sind KI-erzeugte Paraphrasen bzw. Begründungen,
keine Zitate; die `Originaltext`-Spalten sind geleert. Aus demselben Grund enthält das
Repository **nicht** die ausgefüllten Annotationsbögen der Evaluation (sie führen den
Satzwortlaut mit), sondern nur den Ziehungsschlüssel und die aggregierten Ergebnisse.

---

## Hinweis zur Erstellung

Die Notebooks in diesem Repository wurden **»vibe-coded«** — explorativ und KI-gestützt
entwickelt. Die damit erzeugten Ergebnisse (Propositionen, Relationen, Systembezug und
Metriken) wurden von den Verfasser:innen **manuell geprüft und validiert**.
