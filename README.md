# Inferentielle Analyse von Literaturgeschichten nach Robert Brandom

Dieses Repository enthält die Daten, Annotationsrichtlinien, Prompts und Auswertungs­notebooks
eines Projekts, das eine Literaturgeschichte (Beutin et al., *Deutsche Literaturgeschichte*)
mit den Mitteln von Robert Brandoms Inferentialismus rekonstruiert. Ziel ist es, die
**impliziten Schlussmuster** literaturgeschichtlichen Argumentierens explizit zu machen:
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
│   ├── inferenzgraph_analyse_kapitel_final_V2.ipynb
│   ├── systembezug_netzwerk_analyse.ipynb
│   ├── eval_plausibility.ipynb                ← Evaluation: Plausibilität der Inferenzen
│   └── eval_systembezug.ipynb                 ← Evaluation: Systembezug
│
└── data/
    ├── Beutin_complete_Direktzitat_stufe1.xlsx
    ├── Beutin_complete_Direktzitat_gesamt_inf.xlsx
    ├── Beutin_complete_Direktzitat_gesamt_sytembezug.xlsx
    ├── Beutin_complete_Direktzitat_metriken.xlsx
    ├── Beutin_complete_INF_System_EVAL_V1_eval_ergebnisse.xlsx  ← Eval-Ergebnisse Inferenzen
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
| `inferenzgraph_analyse_kapitel_final_V2.ipynb` | Graphkonstruktion + Metriken | Stufe-1/2-JSON + Systembezug-CSV → `…_metriken.xlsx` |
| `systembezug_netzwerk_analyse.ipynb` | Systembezug-Netzwerkanalyse | `…_metriken.xlsx` → Top-Gegenstände, Brücken, Diachronie |
| `eval_plausibility.ipynb` | Evaluation: Plausibilität der Inferenzen (IAA + LLM-Performance) | Annotations-XLSX → `…_EVAL_V1_eval_ergebnisse.xlsx` |
| `eval_systembezug.ipynb` | Evaluation: Systembezug (IAA + LLM vs. Goldstandard) | Annotations-/Gold-/LLM-XLSX → `systembezug_eval_ergebnisse.xlsx` |

Modell durchgängig: `claude-opus-4-8`. API-Schlüssel über die Umgebungsvariable
`MY_ANTHROPIC`. Beide Extraktionsnotebooks schreiben Checkpoints (`checkpoint_batch_*` bzw.
`checkpoint_pair_*`), um lange Läufe wiederaufnehmen zu können.

### `data/` — Ergebnistabellen

Die Tabellen bilden die Stufen der Pipeline ab. **Spaltenwörterbuch:**

**`…_stufe1.xlsx`** — Blatt *Propositionen* (29 448 Zeilen)
`Kapitel · Satz-ID · Originaltext*· Propositions-ID · Proposition · Intra-Satz-Relationen · Relationstypen · Reasoning`

**`…_gesamt_inf.xlsx`** — Ebene 0 vollständig
- Blatt *Propositionen*: wie Stufe 1, zusätzlich `Inter-Satz-Relationen · Inter-Satz-Typen`
- Blatt *Inter-Satz-Relationen* (11 144 Zeilen): `Kapitel · Satz A · Satz B · Von · Nach · Relationstyp · Konnektor · Reasoning`

**`…_gesamt_sytembezug.xlsx`** — Ebene 0 + Ebene 1 + Ebene 2
- Blatt *Propositionen*: zusätzlich `Systembezug · LIT-Gegenstand · NLIT-Gegenstand`
- Blatt *Verknüpfungen LIT-NLIT* (7 572 Zeilen): `Kapitel · Propositions-ID · Proposition · LIT-Gegenstand · NLIT-Gegenstand`

**`…_metriken.xlsx`** — Auswertung (enthält **keinen** Originaltext)
- *Knotenmetriken* (29 446): `Propositions-ID · Kapitel · Satz-ID · Proposition · Systembezug · LIT-Gegenstand · NLIT-Gegenstand · In-Degree · Out-Degree · Betweenness · Relationstyp`
- *Kantenliste* (15 624): `von · nach · typ · konnektor · scope`
- *Dichte pro Kapitel* (16): `Kapitel · Propositionen · Relationen · Isolierte (PR-UNA) · Vernetzungsgrad · Dichte · Komponenten · Größte Komponente`
- *Typverteilung* (4): `Typ · Anzahl · Anteil · Intra · Inter`
- *Systembezug pro Kapitel* (16): `Kapitel · Propositionen · LIT · NLIT · LIT-NLIT · Ohne · LIT % · NLIT % · LIT-NLIT %`

### Evaluation — Validierung der Annotationen

Zwei Notebooks prüfen die Qualität der automatischen Annotation gegen manuell annotierte
Stichproben: zunächst das **Inter-Annotator-Agreement** (IAA, Cohen's κ) zweier
unabhängiger Annotator:innen, dann die **LLM-Performance** gegen einen Goldstandard aus den
übereinstimmenden Annotationen (`scikit-learn`).

**`eval_plausibility.ipynb` → `Beutin_complete_INF_System_EVAL_V1_eval_ergebnisse.xlsx`**
— Post-hoc-Plausibilitätsvalidierung der Inferenzrelationen (N = 105). IAA Cohen's κ = 0.653
(substanziell), 92.4 % Übereinstimmung; LLM-Performance Accuracy 90.7 %, F1 0.951.
Blätter: *Zusammenfassung · Performance pro Typ · Nicht-plausible Relationen · Disagreements*.

**`eval_systembezug.ipynb` → `systembezug_eval_ergebnisse.xlsx`**
— Evaluation von Systembezug und Gegenstandsextraktion (N = 106). IAA Cohen's κ = 1.000
(100 % Übereinstimmung); LLM vs. Goldstandard Accuracy 96.2 %, κ = 0.823;
LIT-NLIT-Erkennung F1 0.842. Blätter: *Zusammenfassung · CM IAA · CM LLM vs Gold ·
Pro-Label-Metriken · Fehler*.


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
- Pakete: `anthropic`, `pdfplumber`, `pandas`, `openpyxl`, `networkx`, `matplotlib`
  (für die interaktive Visualisierung zusätzlich `pyvis`/`plotly`; für die Evaluation `scikit-learn`)
- Umgebungsvariable `MY_ANTHROPIC` mit gültigem Anthropic-API-Schlüssel
- Modell: `claude-opus-4-8`


---

## Wichtige Hinweise

**Urheberrecht.** Das Eingangskorpus (Beutin et al., *Deutsche Literaturgeschichte*) ist
**nicht** Teil dieses Repositories: https://doi.org/10.1007/978-3-476-04953-7 
Die Felder `Proposition` und `Reasoning` sind
KI-erzeugte Paraphrasen bzw. Begründungen, keine Zitate.

---

## Hinweis zur Erstellung

Die Notebooks in diesem Repository wurden **„vibe-coded"** — explorativ und KI-gestützt
entwickelt. Die damit erzeugten Ergebnisse (Propositionen, Relationen, Systembezug und
Metriken) wurden von den Verfasser:innen **manuell geprüft und validiert**.
