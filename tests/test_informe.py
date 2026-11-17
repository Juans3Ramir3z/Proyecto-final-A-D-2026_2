import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from docx import Document

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "informe"))
from build_informe import build_informe  # noqa: E402


def test_build_informe_embeds_figures(tmp_path):
    res, txt = tmp_path / "results", tmp_path / "texto"
    res.mkdir()
    txt.mkdir()
    for name in ("a.png", "b.png"):
        fig, ax = plt.subplots()
        ax.plot([0, 1])
        fig.savefig(res / name)
        plt.close(fig)
    pd.DataFrame({"algo": ["x"], "m": [32], "queries": [10], "queries_theory": [10]}).to_csv(
        res / "counts_time.csv", index=False)
    (txt / "01_formalizacion.md").write_text("# Formalizacion\nTexto del equipo.", encoding="utf-8")
    out = tmp_path / "informe.docx"
    build_informe(res, txt, out)
    doc = Document(out)
    headings = [p.text for p in doc.paragraphs if p.style.name.startswith("Heading")]
    assert "Formalizacion" in headings
    assert "Validacion experimental" in headings
    assert len(doc.inline_shapes) == 2


def test_marker_places_results_in_position(tmp_path):
    res, txt = tmp_path / "results", tmp_path / "texto"
    res.mkdir()
    txt.mkdir()
    fig, ax = plt.subplots()
    ax.plot([0, 1])
    fig.savefig(res / "a.png")
    plt.close(fig)
    (txt / "06.md").write_text("# Seis\nAntes.\n\n[[RESULTADOS]]\n\n# Siete\nDespues.", encoding="utf-8")
    out = tmp_path / "i.docx"
    build_informe(res, txt, out)
    doc = Document(out)
    heads = [p.text for p in doc.paragraphs if p.style.name.startswith("Heading")]
    assert heads.count("Validacion experimental") == 0
    body = [p._p for p in doc.paragraphs]
    texts = [p.text for p in doc.paragraphs]
    assert texts.index("Antes.") < texts.index("a") < texts.index("Despues.")
