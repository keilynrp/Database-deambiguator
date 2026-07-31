# notification-event-fanout Specification

## Purpose
TBD - created by archiving change wire-notification-events. Update Purpose after archive.
## Requirements
### Requirement: A domain event reaches every configured sink from one call

The system SHALL fan a domain event out to all four notification sinks — the
audit log (in-app Notification Center), customer webhooks, alert channels
(Slack/Teams/Discord/webhook), and email — from a single emit call, so that a
sink cannot be silently omitted at an emit site.

The audit write SHALL occur in the caller's transaction; the three outbound
sinks SHALL each run on their own session.

#### Scenario: One call reaches all four sinks

- **WHEN** `emit_event()` is called for an action that maps to an alert event
  and has an email toggle
- **THEN** an audit row is written in the caller's session
- **AND** the webhook dispatcher is invoked
- **AND** the alert-channel dispatcher is invoked
- **AND** the email dispatcher is invoked

#### Scenario: A site that writes its own audit row emits only outbound

- **WHEN** `emit_outbound()` is called at a site that already writes its own
  audit row
- **THEN** the three outbound sinks fire
- **AND** no second audit row is written

#### Scenario: The audit row stays in the caller's transaction

- **WHEN** `emit_event()` is called with the request session
- **THEN** the audit row is visible in that session before it commits
- **AND** committing remains the caller's responsibility

### Requirement: The two event taxonomies are bridged

The system SHALL translate the dotted audit/webhook **action** vocabulary into
the alert-channel **event id** catalogue, so an emit site does not have to know
which vocabulary its sink uses.

An action already present in the catalogue SHALL pass through unchanged, so an
event with no natural audit action can be emitted by its own id.

#### Scenario: A known action maps to its event id

- **WHEN** an event is emitted with action `harmonization.apply`
- **THEN** the alert channels receive event `harmonization.applied`

#### Scenario: Both import actions map to the same alert event

- **WHEN** an event is emitted with action `upload` or with action `pull`
- **THEN** the alert channels receive event `entities.imported`

#### Scenario: A catalogue id passes through

- **WHEN** an event is emitted with action `report.sent`
- **THEN** the alert channels receive event `report.sent`

#### Scenario: An unmapped action reaches no alert channel

- **WHEN** an event is emitted with an action that is neither mapped nor in the
  catalogue
- **THEN** no alert-channel dispatch occurs
- **AND** the remaining sinks are unaffected

### Requirement: Every catalogue event has an emit site

The system SHALL emit every event advertised in the subscribable catalogue, so
that a channel subscribed to any advertised event receives traffic.

#### Scenario: All nine advertised events are emitted

- **WHEN** the catalogue advertises `entities.imported`,
  `enrichment.completed`, `harmonization.applied`, `quality.low`,
  `report.sent`, `report.failed`, `import.scheduled`, `ops.check_failed`, and
  `disambiguation.resolved`
- **THEN** each one has at least one emit site in operational code

### Requirement: Email notifications are gated on the stored toggles

The system SHALL send an email notification only when the notification settings
are enabled **and** the toggle governing that action is on, so that changing a
toggle in the settings UI has an observable effect.

#### Scenario: The toggle is on

- **WHEN** an event is emitted for an action with an email toggle
- **AND** notification settings are enabled with that toggle on
- **THEN** an email notification is sent

#### Scenario: The toggle is off

- **WHEN** the same event is emitted with that toggle off
- **THEN** no email is sent
- **AND** the other sinks still fire

#### Scenario: Notifications are disabled wholesale

- **WHEN** notification settings are disabled
- **THEN** no email is sent regardless of the individual toggle

#### Scenario: An action with no toggle sends no email

- **WHEN** an event is emitted for an action that has no email toggle
- **THEN** no email is sent

### Requirement: Notification delivery never breaks the triggering request

The system SHALL deliver the outbound sinks fire-and-forget, and SHALL swallow
and log any sink failure, so that an unreachable Slack workspace or SMTP host
cannot fail the operation that produced the event.

#### Scenario: A failing sink does not propagate

- **WHEN** a sink raises during dispatch
- **THEN** the emit call still returns normally
- **AND** the failure is logged

#### Scenario: Delivery does not block the caller

- **WHEN** an event is emitted
- **THEN** the outbound sinks run off the request path

### Requirement: A low-quality alert fires on a downward crossing

The system SHALL emit `quality.low` for a domain only when its average quality
score crosses from at-or-above the threshold to below it, so that a domain that
is already below the threshold does not alert on every recompute.

The threshold SHALL be configurable via `UKIP_QUALITY_LOW_THRESHOLD`.

#### Scenario: The average crosses downward

- **WHEN** a domain's average was at or above the threshold before a recompute
  and is below it after
- **THEN** `quality.low` is emitted for that domain

#### Scenario: The domain was already below

- **WHEN** a domain's average was already below the threshold before the
  recompute
- **THEN** no `quality.low` is emitted for it

#### Scenario: The average stays above

- **WHEN** a domain's average is at or above the threshold both before and after
- **THEN** no `quality.low` is emitted for it

#### Scenario: There is no prior baseline

- **WHEN** a domain has no average before the recompute
- **THEN** no `quality.low` is emitted for it

