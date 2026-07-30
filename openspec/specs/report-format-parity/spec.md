# report-format-parity Specification

## Purpose
Guarantee that every selectable report section is rendered in every export
format (or explicitly declared unsupported), that section data is separated from
presentation, and that all export endpoints validate section names consistently.
Created by archiving change unify-report-format-coverage.
## Requirements
### Requirement: Every selectable section is available in every export format

The system SHALL render each section returned by `GET /reports/sections` in
every export format, or explicitly declare that format cannot represent it.
Silent omission SHALL NOT occur.

#### Scenario: A selected section reaches every format

- **WHEN** a report is requested in HTML, PDF, Excel and PPTX with the same
  section list
- **THEN** each output contains a recognizable representation of every
  requested section, except those the format has declared unsupported

#### Scenario: Section registry and format coverage cannot drift apart

- **WHEN** a new section is added to the section registry
- **AND** no renderer declares it supported or unsupported
- **THEN** the parity test fails

#### Scenario: Unsupported sections are reported, not dropped

- **WHEN** a requested section is declared unsupported by the requested format
- **THEN** the response identifies the omitted sections to the caller
- **AND** the remaining requested sections still render

### Requirement: Section data is format-neutral

The system SHALL separate section data collection from section presentation, so
each section is authored once and rendered by every format.

#### Scenario: Collection is reusable without HTML

- **WHEN** a section's collector is invoked
- **THEN** it returns a structured payload containing no markup

#### Scenario: Renderers consume only the payload

- **WHEN** a format renderer produces output for a section
- **THEN** it derives that output solely from the section payload, without
  issuing its own entity or harmonization queries

#### Scenario: Migration preserves existing HTML sections

- **WHEN** a section is migrated from a direct HTML builder to the
  collector-plus-renderer path
- **THEN** the section's existing rendering tests still pass

### Requirement: Export endpoints validate section names consistently

The system SHALL apply the same unknown-section validation to every export
endpoint.

#### Scenario: Excel rejects unknown sections

- **WHEN** `POST /exports/excel` is called with a section name that is not in
  the section registry
- **THEN** the response is 422
- **AND** the detail lists the valid section names

#### Scenario: Deprecated aliases resolve before rendering

- **WHEN** a section is requested by the public id that `GET /reports/sections`
  returns
- **THEN** every format renders it, regardless of any deprecated alias the
  section also answers to

#### Scenario: All export endpoints agree on validity

- **WHEN** the same unknown section name is sent to the HTML, PDF, Excel and
  PPTX endpoints
- **THEN** all four reject it with 422

### Requirement: Per-format availability is discoverable before export

The system SHALL expose which formats can render each section, so a caller can
see availability before requesting an export.

#### Scenario: The section listing carries format availability

- **WHEN** `GET /reports/sections` is requested
- **THEN** each section entry states which export formats support it

#### Scenario: Scheduled reports do not silently under-deliver

- **WHEN** a scheduled report is configured with sections its format cannot
  render
- **THEN** the omission is recorded on the run rather than passing as a clean
  delivery

### Requirement: Presentation elements reach every export format

The system SHALL carry each section's takeaway and method disclosure into every
export format that renders that section. No format may declare these elements
unsupported while rendering the section they describe.

Formats that are not documents SHALL place the elements where they survive
normal use of that format, rather than omit them for lack of an obvious slot.

This extends the existing parity requirement, which covers section availability,
to the statements that make a section's figures readable.

#### Scenario: A rendered section carries its statements in every format

- **WHEN** the same section is exported to HTML, PDF, Excel and PPTX
- **THEN** each output contains that section's takeaway and method disclosure

#### Scenario: A copied spreadsheet range keeps its caveat

- **WHEN** a section is exported to Excel
- **THEN** its caveat appears adjacent to the section's table, not only in a
  separate sheet
- **AND** a dedicated methodology sheet lists every exhibit's source and caveat

#### Scenario: A presented deck keeps its disclosure

- **WHEN** a section is exported to PPTX
- **THEN** the takeaway is the slide's title
- **AND** the method disclosure is present in the slide footer and speaker notes

#### Scenario: Presentation coverage cannot drift from section coverage

- **WHEN** a format renders a section
- **AND** that format does not emit the section's takeaway or disclosure
- **THEN** the parity test fails

#### Scenario: A format that does not render a section is unaffected

- **WHEN** a format has declared a section unsupported
- **THEN** it is not required to carry that section's presentation elements
- **AND** the existing unsupported-section reporting is unchanged

