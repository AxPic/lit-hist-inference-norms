#!/usr/bin/env python3
"""Geschichtete Stichprobenziehung für die Intra-Relationen-Evaluation (IAA + P/R/F1).

Reproduziert mit SEED=20260706 exakt die ausgelieferten Annotationsbögen.

Design
------
Rahmen      : Sätze mit 2-6 Propositionen (ohne Kapitel '(Unbekannt)')
Schichtung  : Kapitel (15) x Modell-Signal {UNA-only, nur BER, mit FLG, mit INK}
Allokation  : je Kapitel 2/3/1/1 -> 105 Saetze, 353 Paare
Gewicht     : N/n je Schicht (Satz-Ebene; Paare erben das Gewicht ihres Satzes)

Urteilsdesign
-------------
PLAUSIBILITAETSDESIGN MIT SICHTBARER MODELL-ANNOTATION (kein Blinddesign).
Die Boegen zeigen je Propositionspaar die Entscheidung des Modells - entweder eine
Relation mit Typ und Richtung (z. B. 'PR-BER: P1 -> P2') oder 'Keine Relation' - und
beurteilt wird, ob diese Entscheidung plausibel ist. Ein Ankereffekt ist damit
moeglich und wird in der Auswertung ausgewiesen. Das Urteil ist streng: 'nicht
plausibel' umfasst auch falschen Typ und falsche Richtung. Weil auch alle
Nicht-Relationen der gezogenen Saetze paarweise beurteilt werden, sind Precision UND
Recall bestimmbar. Die Modell-Paare stehen zusaetzlich in der Schluesseldatei.

(Hinweis zur Versionsgeschichte: Bis V9 beschrieb dieser Docstring ein Blinddesign
ohne Modell-Annotation in den Boegen. Das entsprach nicht den ausgelieferten Boegen
und ist hier korrigiert; die Ziehung selbst ist unveraendert.)

R6 / V10
--------
Verbundene Praemissen ({P1, P2} -> P3) werden NICHT hier gezogen. Die Ziehung liefert
nur die Kennzeichnung 'Verbund moeglich' (Saetze mit >= 3 Propositionen), weil nur
dort ein Verbund vorkommen kann. Die R6-Blaetter ('Saetze', 'Verbuende') erzeugt der
Bogen-Generator; die Auswertung erfolgt in eval_precision_recall_V10.ipynb. R6
veraendert Rahmen, Schichtung, Gewichte und Paarmetriken nicht.

Aufruf: python stichprobe_ziehung.py <stufe1.xlsx>
"""
import sys, re, itertools
import numpy as np
import pandas as pd

SEED = 20260706
ALLOC = {"UNA-only": 2, "nur BER": 3, "mit FLG": 1, "mit INK": 1}
MIN_PROPS_VERBUND = 3          # ab hier ist ein Verbund (R6) ueberhaupt moeglich
PAIR = re.compile(r"(P\(\d+\.\d+\))\s*\u2192\s*(P\(\d+\.\d+\))\s*:\s*(PR-\w+)")

def snum(pid): return re.match(r"P\((\d+)\.", pid).group(1)
def pnum(pid): return int(re.match(r"P\(\d+\.(\d+)\)", pid).group(1))

def main(stufe1_path):
    df = pd.read_excel(stufe1_path)
    df = df[df["Kapitel"].astype(str) != "(Unbekannt)"].copy()

    pairs = []
    for _, r in df.iterrows():
        for von, nach, typ in PAIR.findall(str(r["Intra-Satz-Relationen"] or "")):
            pairs.append({"Satz-ID": r["Satz-ID"], "von": von, "nach": nach, "typ": typ})
    mp = pd.DataFrame(pairs).drop_duplicates()
    mp = mp[(mp["von"] != mp["nach"]) & (mp["typ"] != "PR-UNA")]
    mp = mp[mp["von"].map(snum) == mp["nach"].map(snum)]

    g = df.groupby("Satz-ID").agg(Kapitel=("Kapitel", "first"),
                                  n_props=("Propositions-ID", "size"),
                                  Originaltext=("Originaltext", "first"))
    g = g[(g["n_props"] >= 2) & (g["n_props"] <= 6)]
    typ_je_satz = mp.groupby("Satz-ID")["typ"].agg(set)
    def signal(sid):
        t = typ_je_satz.get(sid, set())
        if not t: return "UNA-only"
        if "PR-INK" in t: return "mit INK"
        if "PR-FLG" in t: return "mit FLG"
        return "nur BER"
    g["Signal"] = g.index.map(signal)

    rng = np.random.default_rng(SEED)
    rows = []
    for (kap, sig), grp in g.groupby(["Kapitel", "Signal"]):
        n = min(ALLOC[sig], len(grp))
        for sid, r in grp.sample(n=n, random_state=rng.integers(1e9)).iterrows():
            rows.append({"Satz-ID": sid, "Kapitel": kap, "Signal": sig,
                         "n_props": r["n_props"], "N_Stratum": len(grp), "n_Stratum": n,
                         "Gewicht": len(grp) / n, "Originaltext": r["Originaltext"]})
    sample = pd.DataFrame(rows).sample(frac=1, random_state=SEED).reset_index(drop=True)
    sample.insert(0, "Satz-Nr", range(1, len(sample) + 1))

    # Abgeleitete Spalten (veraendern die Ziehung nicht)
    sample["moegl_Paare"] = sample["n_props"] * (sample["n_props"] - 1) // 2
    sample["Verbund moeglich"] = np.where(sample["n_props"] >= MIN_PROPS_VERBUND, "ja", "nein")

    n_verbund = int((sample["Verbund moeglich"] == "ja").sum())
    print(f"{len(sample)} Saetze gezogen; Modell-Paare in Stichprobe: "
          f"{mp['Satz-ID'].isin(sample['Satz-ID']).sum()}")
    print(f"Paar-Urteile insgesamt: {int(sample['moegl_Paare'].sum())}")
    print(f"Verbundfaehige Saetze (>= {MIN_PROPS_VERBUND} Propositionen): {n_verbund} "
          f"({n_verbund / len(sample) * 100:.1f} %) mit "
          f"{int(sample.loc[sample['Verbund moeglich'] == 'ja', 'moegl_Paare'].sum())} Paarzeilen "
          f"- Grundgesamtheit der R6-Erhebung")
    return sample, mp, df

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "Beutin_complete_Direktzitat_stufe1.xlsx")
