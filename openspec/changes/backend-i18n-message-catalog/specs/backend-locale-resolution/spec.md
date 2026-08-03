## ADDED Requirements

### Requirement: A request's language is resolved by an explicit precedence chain
The backend SHALL resolve the language for a request in this order: an explicit language parameter on the request, then the `Accept-Language` header, then the configured default. The default SHALL be English.

#### Scenario: An explicit parameter wins
- **WHEN** a request carries a language parameter and an `Accept-Language` header naming a different language
- **THEN** the parameter is used, because generation is frequently performed on behalf of an audience rather than by the reader

#### Scenario: No signal is present
- **WHEN** a request carries neither a parameter nor a usable header
- **THEN** English is used

#### Scenario: An unsupported language is requested
- **WHEN** a request asks for a language the catalog does not carry
- **THEN** the request succeeds in the default language rather than failing
- **AND** the fallback is logged, so an unsupported request is observable rather than silent

### Requirement: Report generation accepts a language and ignores the header
`POST /reports/generate` SHALL accept an optional language, and the generated artefact SHALL use it for all catalog-sourced text in every format. Report generation SHALL NOT consult `Accept-Language`: it takes the explicit parameter, otherwise the configured default.

#### Scenario: A Spanish report is requested
- **WHEN** a report is generated with the language set to Spanish
- **THEN** its section titles, labels and disclosures are Spanish across PDF, PPTX and Excel alike

#### Scenario: The parameter is omitted
- **WHEN** a report is generated with no language
- **THEN** the artefact is produced in the configured default, preserving the behaviour of callers written before this parameter existed

#### Scenario: The operator's browser language differs from the request
- **WHEN** a report is generated with no language parameter by an operator whose `Accept-Language` is Spanish
- **THEN** the artefact is English, because a report is produced for an audience rather than for whoever triggered it, and the operator's locale must not leak into someone else's document

### Requirement: Outbound email uses the resolved language
Email the backend sends SHALL take its subject and body text from the catalog in the resolved language rather than a hard-coded language.

#### Scenario: A password reset is requested
- **WHEN** a password-reset email is sent
- **THEN** its subject comes from the catalog in the resolved language, not a Spanish literal

### Requirement: Generated analysis text and provider data are not localised
Prose the system composes from data, and values supplied by external providers, SHALL remain in English regardless of the resolved language. This boundary SHALL be stated to the reader rather than left to be discovered.

#### Scenario: A Spanish report contains a finding
- **WHEN** a report is generated in Spanish and a section states a finding composed from data
- **THEN** the finding text is English, and this is expected rather than a defect

#### Scenario: A Spanish report names a concept
- **WHEN** a Spanish report cites a concept sourced from OpenAlex
- **THEN** the concept appears in English, as the provider supplies it

#### Scenario: The limitation is disclosed
- **WHEN** an artefact is generated in a language other than English
- **THEN** it states that analysis text and source-derived names remain in English, so a reader is not left to interpret the mixture as an error
