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
   ANALYSE  Inferenzgraph → Metriken      inferenzgraph_analyse_…V2.ipynb → …_metriken.xlsx
            Systembezug-Netzwerk          systembezug_netzwerk_analyse.ipynb
```


---

## Voraussetzungen

- Python ≥ 3.10; Pakete `anthropic`, `pdfplumber`, `pandas`, `openpyxl`, `networkx`,
  `matplotlib` (Visualisierung: `pyvis`/`plotly`).
- Anthropic-API-Schlüssel.
- Modell `claude-opus-4-8` für alle generativen Schritte.
- Alle generativen Schritte schreiben **Checkpoints**, sodass unterbrochene Läufe wiederaufgenommen werden können.

Konvention: `STEM = "Beutin_complete_Direktzitat"`; Ausgabedateien folgen dem Muster
`{STEM}_…`.

---

## Schritt 0 — Eingangskorpus

**Textgrundlage:** Beutin, Wolfgang/Beilein, Matthias/Emmerich, Wolfgang u. a.: Deutsche Literaturgeschichte: Von den Anfängen bis zur Gegenwart, Stuttgart 2019. DOI: https://doi.org/10.1007/978-3-476-04953-7 (Volltext als PDF).
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

**Notebook:** `inferenzgraph_analyse_kapitel_final_V2.ipynb`
**Eingabe:** `{STEM}_stufe1.json`, `{STEM}_stufe2_inter.json`, `{STEM}_systembezug.csv`.

Aus Propositionen (Knoten, gefärbt nach Systembezug) und Relationen (Kanten,
Grund → gestützte Aussage) wird mit `networkx` ein Graph konstruiert. Das Notebook berechnet
u. a.: tragende Knoten (global), unbegründete „Fundamentalbehauptungen", Relationstyp-
Verteilung, inferentielle Dichte pro Kapitel, Konnektoranalyse, Betweenness-Zentralität,
Systembezug-Verteilung pro Kapitel, systemgrenzenüberschreitende Kanten,
Verknüpfungsmuster (LIT-NLIT) sowie eine kapitelweise interaktive Visualisierung.

**Ausgabe:** `{STEM}_metriken.xlsx` mit den Blättern *Knotenmetriken · Kantenliste ·
Dichte pro Kapitel · Typverteilung · Systembezug pro Kapitel*.

---

## Analyse B — Systembezug-Netzwerkanalyse

**Notebook:** `systembezug_netzwerk_analyse.ipynb`
**Eingabe:** `{STEM}_metriken.xlsx` (die Metrik-Datei **mit** Systembezug).

Vertiefende Auswertung der Systemverknüpfung: Systembezug-Verteilung; die **vermittelte
Grenze** (Kanten über die Systemgrenze laufen überwiegend über `LIT-NLIT`-Brücken);
Zentralität nach Systembezug; „Woran wird Literatur geknüpft?" (häufigste NLIT-Gegenstände);
Brücken mit höchster Betweenness; sowie die **diachrone Entwicklung** über die Epochen
(zwei Diagramme). **Ausgabe:** `nlit_gegenstaende_top40.xlsx`, `lit_nlit_bruecken_top.xlsx`,
`entwicklung_ueber_zeit.xlsx`.

---

## Reproduktion — Ausführungsreihenfolge

1. PDF bereitstellen → **Stufe 1** ausführen → `…_stufe1.{json,csv,xlsx}`.
2. **Stufe 2** ausführen → `…_gesamt.{xlsx,csv}`, `…_stufe2_inter.{json,csv}`.
3. **Ebene 1–2** (Systembezug/Gegenstände) ausführen → `…_gesamt_sytembezug.xlsx`,
   `…_systembezug.csv`.
4. **Analyse A** ausführen → `…_metriken.xlsx`.
5. **Analyse B** ausführen → Top-Gegenstände, Brücken, Diachronie.

**Hinweise.** Die Notebooks lesen ihre Eingaben teils als **JSON/CSV** (nicht als XLSX);
die Pfadkonstanten am Anfang jedes Notebooks ggf. anpassen. Die generativen Schritte sind
kosten- und laufzeitintensiv (29 448 Propositionen, kapitel-/paarweise API-Aufrufe) —
deshalb die Checkpoint-Logik. Zwischendateien (`…_stufe1.json`, `…_stufe2_inter.json`,
`…_systembezug.csv`) müssen für die Analyse vorliegen.

---

## Methodische Vorbehalte

- **Fensterbreite.** Inter-Satz-Relationen werden nur zwischen *unmittelbar*
  aufeinanderfolgenden Sätzen erhoben (≈ 99 % der Inter-Kanten verbinden benachbarte Sätze).
  Das begünstigt die Detektion **lokaler** gegenüber weitreichenden Begründungs­
  zusammenhängen; der Befund vieler kleiner „Begründungsinseln" ist daher teilweise von
  dieser Setzung mitbedingt und sollte durch Variation der Reichweite auf Robustheit
  geprüft werden.
- **Beschreibungsanspruch.** Das Brandom-Modell dient als *Beschreibungsapparat* für Verknüpfungsmuster.

---

## Hinweis zur Erstellung

Die Notebooks in diesem Repository wurden **„vibe-coded"** — explorativ und KI-gestützt
entwickelt. Die damit erzeugten Ergebnisse (Propositionen, Relationen, Systembezug und
Metriken) wurden von den Verfasser:innen **manuell geprüft und validiert**.
