"""Format-neutral section payload (unify-report-format-coverage, phase 1).

A section's data is collected once into a `SectionData` of these blocks; each
per-format renderer turns the blocks into HTML, Excel or PPTX. Four primitives
cover every existing section (verified against the current HTML output):

  * StatGrid — labelled KPI cards.
  * Table    — columns + rows, optionally with one column drawn as a bar.
  * Narrative — a heading and paragraphs of prose.
  * Meter    — a single labelled percentage bar.

All types are frozen: a payload is data, not a mutable buffer, so a renderer
cannot alter what a later renderer sees.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Union


@dataclass(frozen=True)
class StatItem:
    label: str
    value: str
    sub: str | None = None


@dataclass(frozen=True)
class StatGrid:
    items: tuple[StatItem, ...]


@dataclass(frozen=True)
class Table:
    columns: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]
    # Index of a column to draw as a proportional bar (e.g. a share %). Optional.
    bar_column: int | None = None

    def __post_init__(self) -> None:
        width = len(self.columns)
        for row in self.rows:
            if len(row) != width:
                raise ValueError(
                    f"row {row!r} has {len(row)} cells, expected {width}"
                )
        if self.bar_column is not None and not (0 <= self.bar_column < width):
            raise ValueError(
                f"bar_column {self.bar_column} out of range for {width} columns"
            )


@dataclass(frozen=True)
class Narrative:
    heading: str
    paragraphs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not self.heading.strip():
            raise ValueError("Narrative requires a non-empty heading")


@dataclass(frozen=True)
class Meter:
    label: str
    pct: float

    def __post_init__(self) -> None:
        if not (0 <= self.pct <= 100):
            raise ValueError(f"Meter pct {self.pct} out of range [0, 100]")


Block = Union[StatGrid, Table, Narrative, Meter]


class Materiality(IntEnum):
    """How much of a reader's attention a section's finding deserves.

    An ordinal rather than a boolean: the executive summary lists every
    section's takeaway ordered by materiality, so it needs a sort key, not a
    filter. Higher is more material, so `sorted(..., reverse=True)` leads with
    LEAD. IntEnum gives the comparison semantics for free.

    Each collector decides its own level from its own thresholds — a two-point
    coverage drop is noise where twenty points is not, and only the section
    knows which of those it is looking at.
    """

    EMPTY = 0     # nothing to report; ranks below any section with a finding
    ROUTINE = 1   # computed and unremarkable
    NOTABLE = 2   # worth reading, not worth leading with
    LEAD = 3      # belongs at the top of the summary


@dataclass(frozen=True)
class SectionData:
    key: str
    title: str

    #: What the section's data shows, as a statement rather than a label.
    #: Produced by the collector alongside the figures it describes, never
    #: composed by a renderer — see report-presentation.
    takeaway: str

    #: Where the data came from, as-of when, and any caveat needed to read the
    #: figures correctly. A section with no caveat still states its source and
    #: as-of date: making this optional would let the sections that most need a
    #: caveat be the ones that omit it, because their author sits closest to the
    #: data and is least likely to see the ambiguity.
    method: str

    blocks: tuple[Block, ...] = field(default_factory=tuple)

    #: Defaulted, unlike takeaway and method. Every section has a level —
    #: "unremarkable" is an answer — whereas a blank takeaway or method is a
    #: section nobody has written yet.
    materiality: Materiality = Materiality.ROUTINE

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("SectionData requires a non-empty key")
        if not self.title.strip():
            raise ValueError("SectionData requires a non-empty title")
        # Required since task 3.7, once every collector supplied real values.
        # The type now enforces the presentation contract rather than a comment
        # asking for it: a new section cannot be added without stating what it
        # shows and where the figures came from.
        if not self.takeaway.strip():
            raise ValueError(
                f"SectionData({self.key!r}) requires a non-empty takeaway — "
                "state what the section shows, not what it is called"
            )
        if not self.method.strip():
            raise ValueError(
                f"SectionData({self.key!r}) requires a non-empty method — "
                "state the source and as-of date even when there is no caveat"
            )
