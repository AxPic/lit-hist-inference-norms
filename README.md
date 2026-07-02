# Inferentielle Analyse von Literaturgeschichten nach Robert Brandom

Dieses Repository enthält die Daten, Annotationsrichtlinien, Prompts und Auswertungs­notebooks
eines Projekts, das eine Literaturgeschichte (Beutin et al., *Deutsche Literaturgeschichte*)
mit den Mitteln von Robert Brandoms Inferentialismus rekonstruiert. Ziel ist es, die **impliziten Begründungsmuster** literaturgeschichtlichen Schreibens sichtbar zu machen:
Welche Propositionen stützen, erzwingen oder schließen einander aus, und wie wird das
Literarische mit dem Nicht-Literarischen verknüpft?

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
│   └── Brandom_Annotationsrichtlinien_V9.docx ← Annotationsspezifikation (Ebene 0–2)
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
│   ├── eval_plausibility.ipynb      ← Evaluation: Plausibilität der Inferenzen
│   └── eval_systembezug.ipynb       ← Evaluation: Systembezug
│
└── data/
    ├── Beutin_complete_Direktzitat_stufe1.xlsx
    ├── Beutin_complete_Direktzitat_gesamt_inf.xlsx
    ├── Beutin_complete_Direktzitat_gesamt_sytembezug.xlsx
    ├── Beutin_complete_Direktzitat_metriken.xlsx
    ├── Beutin_complete_INF+System_EVAL_eval_ergebnisse.xlsx     ← Eval-Ergebnisse Inferenzen
    └── systembezug_eval_ergebnisse.xlsx                         ← Eval-Ergebnisse Systembezug
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
| `systembezug_netzwerk_analyse_corrected.ipynb` | Systembezug-Netzwerkanalyse (kapitelübergreifende Vergleiche nur über skalengleiche Metriken) | `…_metriken.xlsx` → Top-Gegenstände, Brücken, Diachronie |
| `eval_plausibility_corrected.ipynb` | Evaluation: Plausibilität der Inferenzen (IAA + getrennte Extraktions-/Nicht-Extraktions-Kennzahlen) | Annotations-XLSX → `…_eval_ergebnisse.xlsx` |
| `eval_systembezug_corrected.ipynb` | Evaluation: Systembezug (IAA + LLM vs. Goldstandard) | Annotations-/LLM-XLSX → `systembezug_eval_ergebnisse.xlsx` |

Modell durchgängig: `claude-opus-4-8`. API-Schlüssel über die Umgebungsvariable
`MY_ANTHROPIC`. Beide Extraktionsnotebooks schreiben Checkpoints (`checkpoint_batch_*` bzw.
`checkpoint_pair_*`), um lange Läufe wiederaufnehmen zu können.

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

\* Die `Originaltext`-Spalten sind in allen ausgelieferten Dateien **aus
urheberrechtlichen Gründen geleert** (vgl. „Wichtige Hinweise"); die Spalte bleibt
als Platzhalter erhalten, damit lokal erzeugte Fassungen spaltenkompatibel sind.

### Metriken: Definitionen und Gültigkeitsbereiche

- **Relationen pro Proposition** („Dichte"): Kanten je Knoten, d. h. der halbe
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
- Kapitelübergreifende Klassenvergleiche (Ø-Zentralität nach Systembezug, Top-Brücken)
  verwenden ausschließlich die normalisierten bzw. Cross-System-Werte.

### Evaluation — Validierung der Annotationen

Zwei Notebooks prüfen die Qualität der automatischen Annotation gegen manuell annotierte
Stichproben: zunächst das **Inter-Annotator-Agreement** (IAA, Cohen's κ) zweier
Annotator:innen, dann die **LLM-Performance** gegen einen Goldstandard aus den
übereinstimmenden Annotationen (`scikit-learn`).

**`eval_plausibility.ipynb` → `Beutin_complete_INF+System_EVAL_eval_ergebnisse.xlsx`**
— Post-hoc-Plausibilitätsvalidierung der Inferenzannotationen (N = 105). IAA Cohen's
κ = 0.653 (substanziell), 92.4 % Übereinstimmung. LLM-Performance, getrennt nach Fallart:
**Extraktionspräzision 100 %** (60/60 extrahierte Relationen plausibel),
**Korrektheit der Nicht-Extraktion (PR-UNA) 75.7 %** (28/37; 9 übersehene Relationen),
Gesamtplausibilität 90.7 %. **Recall und F1 werden nicht berichtet:** Evaluiert wurden
post hoc die vom Modell erzeugten — von ihm also für plausibel gehaltenen —
Annotationen, kein unabhängig erstellter Goldstandard aller tatsächlich bestehenden
Relationen; die Vollständigkeit der Extraktion (Recall) ist auf dieser Basis nicht
bestimmbar, ein F1-Score wäre nicht aussagekräftig. Einen Hinweis auf die
Vollständigkeit geben lediglich die PR-UNA-Fälle der Stichprobe (9 von 37 als
übersehene Relationen beurteilt). 
Blätter: *Zusammenfassung · Performance pro Typ · Nicht-plausible Relationen · Disagreements*.

**`eval_systembezug.ipynb` → `systembezug_eval_ergebnisse.xlsx`**
— Evaluation von Systembezug und Gegenstandsextraktion (N = 106). IAA Cohen's κ = 1.000
(100 % Übereinstimmung); LLM vs. Goldstandard Accuracy 96.2 %, κ = 0.823;
LIT-NLIT-Erkennung F1 0.842.

**Reichweite der Evaluation.** Beide Stichproben stammen ausschließlich aus dem ersten
Kapitel (*Mittelalterliche Literatur*, Sätze 1–39); der Relationstyp PR-INK ist in der
Plausibilitätsstichprobe nicht vertreten, und die Pro-Label-Metriken für LIT beruhen auf
nur 3 Goldfällen. Die Kennzahlen sind daher **nicht ohne Weiteres auf das Gesamtkorpus
übertragbar**; für belastbare Aussagen ist eine über Kapitel und Typen geschichtete
Zufallsstichprobe erforderlich.

---

## Bekannte Datenartefakte

Die ausgelieferten Ergebnisdaten enthalten quantifizierte Restfehler der automatischen
Extraktion, die bei der Interpretation zu berücksichtigen sind:

- Ein Pseudo-Kapitel **`(Unbekannt)`** (11 Propositionen aus 5 Sätzen mit vom Modell
  erfundenen Satz-IDs) läuft als eigene Zeile durch die Kapitel-Blätter; die inhaltlichen
  „16 Kapitel" sind real 15 Kapitel plus dieses Artefakt.
- **2 duplizierte Propositions-IDs** (`P(11066.1/2)`) mit unterschiedlichen Texten; der
  Graph führt sie zusammen (daher 29 446 Knoten bei 29 448 Propositionszeilen).
- **15 Selbstschleifen** und **11 Kanten vom Typ PR-UNA** in der Kantenliste
  (schemawidrig, da PR-UNA „kein Paar" bedeutet); **53 als `intra` markierte Kanten**
  verbinden Propositionen verschiedener Sätze; **31 parallele Kantenpaare** werden im
  Graphen dedupliziert.
- Auf kürzeste Pfade und damit auf alle Betweenness-Werte haben Selbstschleifen keinen
  Einfluss; der Brücken-Score schließt sie explizit aus.

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
  `scikit-learn` (Evaluation); für die interaktive Visualisierung zusätzlich `pyvis`/`plotly`
- Umgebungsvariable `MY_ANTHROPIC` mit gültigem Anthropic-API-Schlüssel
- Modell: `claude-opus-4-8`

---

## Wichtige Hinweise

**Urheberrecht.** Das Eingangskorpus (Beutin et al., *Deutsche Literaturgeschichte*) ist
**nicht** Teil dieses Repositories: https://doi.org/10.1007/978-3-476-04953-7
Die Felder `Proposition` und `Reasoning` sind KI-erzeugte Paraphrasen bzw. Begründungen,
keine Zitate; die `Originaltext`-Spalten sind geleert.



---

## Hinweis zur Erstellung

Die Notebooks in diesem Repository wurden **„vibe-coded"** — explorativ und KI-gestützt
entwickelt. Die damit erzeugten Ergebnisse (Propositionen, Relationen, Systembezug und
Metriken) wurden von den Verfasser:innen **manuell geprüft und validiert**.
