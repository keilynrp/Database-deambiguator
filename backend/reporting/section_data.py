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
    blocks: tuple[Block, ...] = field(default_factory=tuple)

    #: What the section's data shows, as a statement rather than a label.
    #: Produced by the collector alongside the figures it describes, never
    #: composed by a renderer — see report-presentation.
    takeaway: str = ""

    #: Where the data came from, as-of when, and any caveat needed to read the
    #: figures correctly. Mandatory in the finished contract: a section with no
    #: caveat still states its source and as-of date.
    method: str = ""

    materiality: Materiality = Materiality.ROUTINE

    def __post_init__(self) -> None:
        if not self.key.strip():
            raise ValueError("SectionData requires a non-empty key")
        if not self.title.strip():
            raise ValueError("SectionData requires a non-empty title")

    # `takeaway` and `method` default to "" and are NOT yet validated as
    # non-empty. Enforcing that now would break the eleven collectors that
    # predate this contract, all at once. The defaults come off — and the
    # emptiness check goes in above — once every collector supplies real
    # values, at which point the type enforces the contract instead of this
    # comment asking for it. Tracked as task 3.7.

    @property
    def has_presentation(self) -> bool:
        """Whether this section already carries its presentation contract.

        Lets callers and tests distinguish a migrated section from one still
        running on defaults, without inspecting the strings themselves.
        """
        return bool(self.takeaway.strip()) and bool(self.method.strip())
