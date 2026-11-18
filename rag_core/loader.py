"""Carga del PDF: texto completo + lista de secciones.

La lista de secciones la usa la parte 2 (validación): comprobamos que el
resumen cite secciones que realmente existen en el documento.
"""

import re
import unicodedata

from pypdf import PdfReader


def load_pdf_text(pdf_path: str) -> str:
    """Devuelve todo el texto del PDF como un solo string."""
    reader = PdfReader(pdf_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(pages)
    # Normalizamos ligaduras tipográficas (p.ej. "ﬁ" -> "fi") y caracteres equivalentes,
    # para que los títulos de sección coincidan de forma exacta en la validación.
    return unicodedata.normalize("NFKC", text)


# Un encabezado tipo "1. Introduction" o "3.1. Residual Learning":
# uno o más números separados por puntos, y un título que empieza con mayúscula.
_SECTION_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.?\s+([A-Z][A-Za-z][^\n]{1,60})\s*$")


def extract_sections(text: str) -> list[str]:
    """Extrae los títulos de sección (p.ej. '3 Deep Residual Learning').

    Un encabezado real es corto y no lleva comas ni dos puntos; con eso
    descartamos pies de figura o frases que empiezan con un número de página.
    """
    sections: list[str] = []
    for line in text.splitlines():
        match = _SECTION_RE.match(line)
        if not match:
            continue
        number, title = match.group(1), match.group(2).strip()
        if ":" in title or "," in title or len(title.split()) > 8:
            continue
        sections.append(f"{number} {title}")
    # Quitamos duplicados conservando el orden de aparición.
    return list(dict.fromkeys(sections))
