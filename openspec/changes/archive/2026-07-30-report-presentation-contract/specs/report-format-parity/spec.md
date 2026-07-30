## ADDED Requirements

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
