# Design principles

## Readability over cleverness

Code is written primarily for humans.
The computer execution is only one part of the software lifecycle.

## Explicit over implicit

Important concepts should be visible in types, names and interfaces.

## Small responsibilities

Each component should have one clear purpose.

## Types are documentation

Type annotations should express the domain model whenever possible.

## Side effects are isolated

Communication with Audacity, filesystem access and process control
are kept at clearly identified boundaries.

## Decisions are documented

Important architectural choices are recorded as ADRs.
