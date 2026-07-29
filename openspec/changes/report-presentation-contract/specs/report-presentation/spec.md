## ADDED Requirements

### Requirement: Every rendered section states its finding

The system SHALL give each rendered section a takeaway that states what the
section's data shows, not what the data is named. The dataset label SHALL remain
available as secondary text so the report stays scannable.

The takeaway SHALL be produced by the section's collector, alongside the figures
it describes, and SHALL NOT be composed by a format renderer.

#### Scenario: A section reports a finding rather than a label

- **WHEN** a section is collected
- **THEN** its payload carries a takeaway asserting the section's finding
- **AND** the takeaway is a complete statement, not a dataset name

#### Scenario: The takeaway travels with the figures

- **WHEN** a format renderer produces output for a section
- **THEN** it uses the takeaway from the section payload
- **AND** does not derive, reword or recompose it

#### Scenario: A takeaway asserts only what the section renders

- **WHEN** a section's takeaway cites a figure
- **THEN** that figure appears in the same section's rendered output

### Requirement: Every rendered section discloses its source and method

The system SHALL state, for each rendered section, the origin of its data, the
as-of date, and any caveat required to read its figures correctly. This
disclosure SHALL be mandatory: a section with no caveat still states its source
and as-of date.

Where a figure is a proxy for a better-known measure, the disclosure SHALL name
what it is not.

#### Scenario: Disclosure is present for every section

- **WHEN** any section is collected
- **THEN** its payload carries source and as-of information
- **AND** rendering a section without it fails rather than omitting it silently

#### Scenario: A proxy metric names what it is not

- **WHEN** a section reports the journal NIF
- **THEN** its disclosure states that the figure is a field-normalized open
  proxy and is not the Journal Impact Factor

#### Scenario: A locally-scoped count says so

- **WHEN** a section reports a works count derived from local records
- **THEN** its disclosure states that the figure is local and not the upstream
  global count

### Requirement: Exhibits are identified within the document

The system SHALL assign each rendered section an exhibit ordinal, so a reader
can reference a specific exhibit within a report.

Ordinals SHALL be assigned at document assembly, after section selection, and
SHALL be treated as within-document references only. The section key SHALL
remain the stable cross-report identifier.

#### Scenario: Exhibits are numbered in document order

- **WHEN** a report renders a selected set of sections
- **THEN** each rendered section carries an ordinal reflecting its position

#### Scenario: Ordinals are not cross-report identifiers

- **WHEN** two reports are produced with different section selections
- **THEN** the same section may carry different ordinals
- **AND** the section key is unchanged in both

### Requirement: The executive summary orders findings by materiality

The system SHALL open a report with a summary carrying the takeaway of every
rendered section, ordered by materiality rather than by section order, with
non-material findings de-emphasized rather than omitted.

Each section SHALL supply its own materiality signal, computed from its own
thresholds, as an ordinal rather than a boolean.

#### Scenario: All findings appear, ordered by materiality

- **WHEN** a report is rendered with a set of sections
- **THEN** the summary lists a takeaway for every rendered section
- **AND** the order reflects materiality, not section order

#### Scenario: Coverage is visible even when nothing is notable

- **WHEN** a section computes successfully but its finding is not material
- **THEN** its takeaway still appears in the summary, de-emphasized
- **AND** the reader can tell the section was computed

#### Scenario: Materiality is section-defined

- **WHEN** two sections report a numerically similar change
- **THEN** each may classify its own materiality differently, per its thresholds

### Requirement: Sections with insufficient data say so

The system SHALL make a section with no data or insufficient data state that
explicitly, rather than rendering an empty table beneath a heading that asserts
a finding.

#### Scenario: An empty section is explicit

- **WHEN** a section's collector finds no qualifying records
- **THEN** its takeaway states that there is nothing to report and why
- **AND** the section does not present an empty table under an assertive heading

#### Scenario: An empty section is not material

- **WHEN** a section has no data
- **THEN** its materiality signal ranks it below any section with a finding
