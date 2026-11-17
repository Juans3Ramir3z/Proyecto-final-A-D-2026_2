"""Ensambla el informe .docx a partir de los textos del equipo y de results/.

El texto matematico (formalizacion, deduccion de T(n), reduccion desde Max
Coverage, analisis de cotas) lo redacta el equipo en ``informe/texto/*.md``
(subconjunto de Markdown: ``# `` y ``## `` para titulos, parrafos separados por
linea en blanco). Este script solo lo ensambla con las figuras y tablas reales
generadas en ``results/``; no calcula ni inventa cifras.

Uso: python informe/build_informe.py [--results results] [--texto informe/texto] [--out informe/informe.docx]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from docx import Document
from docx.shared import Inches


def _add_markdown(doc: Document, text: str) -> None:
    para: list[str] = []

    def flush() -> None:
        if para:
            doc.add_paragraph(" ".join(para))
            para.clear()

    for line in text.splitlines():
        s = line.strip()
        if s.startswith("## "):
            flush()
            doc.add_heading(s[3:], level=2)
        elif s.startswith("# "):
            flush()
            doc.add_heading(s[2:], level=1)
        elif not s:
            flush()
        else:
            para.append(s)
    flush()


def _add_table(doc: Document, df: pd.DataFrame) -> None:
    table = doc.add_table(rows=1, cols=len(df.columns))
    table.style = "Table Grid"
    for i, c in enumerate(df.columns):
        table.rows[0].cells[i].text = str(c)
    for _, r in df.iterrows():
        cells = table.add_row().cells
        for i, v in enumerate(r):
            cells[i].text = f"{v:.4g}" if isinstance(v, float) else str(v)


def build_informe(results_dir: Path, text_dir: Path, out_path: Path) -> None:
    results_dir, text_dir, out_path = Path(results_dir), Path(text_dir), Path(out_path)
    doc = Document()
    doc.add_heading("Optimizacion de configuraciones de prompt bajo presupuesto de consultas", level=0)
    doc.add_paragraph("Proyecto semestral 2026-2 - Analisis y Diseno de Algoritmos")
    for md in sorted(text_dir.glob("*.md")):
        _add_markdown(doc, md.read_text(encoding="utf-8"))
    doc.add_heading("Validacion experimental", level=1)
    csv = results_dir / "counts_time.csv"
    if csv.exists():
        df = pd.read_csv(csv)
        summary = df.groupby(["algo", "m"])[["queries", "queries_theory"]].mean().reset_index()
        doc.add_paragraph("Consultas medidas frente a consultas teoricas (media por algoritmo y tamano m).")
        _add_table(doc, summary)
    for png in sorted(results_dir.glob("*.png")):
        doc.add_picture(str(png), width=Inches(5.5))
        doc.add_paragraph(png.stem.replace("_", " "))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default="results")
    ap.add_argument("--texto", default="informe/texto")
    ap.add_argument("--out", default="informe/informe.docx")
    a = ap.parse_args()
    build_informe(Path(a.results), Path(a.texto), Path(a.out))
