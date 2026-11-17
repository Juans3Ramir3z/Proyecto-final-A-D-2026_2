from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SearchResult:
    """Resultado comun de todos los algoritmos de busqueda."""

    best_config: tuple[int, ...]
    queries: int
    stats: dict = field(default_factory=dict)
