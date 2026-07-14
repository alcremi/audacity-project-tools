# ADR 0001 — Project scope

## Status

Accepted

## Context

The initial need is to migrate a large number of legacy Audacity
projects from `.aup` format to `.aup3`.

During investigation, it became clear that reliable automation of
Audacity itself is a reusable capability.

## Decision

The project will not be limited to a single migration script.

It will provide reusable automation tools for Audacity projects,
with migration as the first application.

## Consequences

Positive:

- reusable architecture;
- easier future extensions;
- clearer separation between library and applications.

Negative:

- slightly more initial design work.
