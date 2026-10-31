# Security Policy

## Supported versions

Security fixes are applied to the latest release on the `main` branch.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's private vulnerability
reporting feature for this repository. Include reproduction steps, affected version, impact, and any
suggested mitigation. Avoid including live credentials or customer data.

## Demonstration limitations

This repository uses synthetic records. The `--customer` option selects a fixture and is not
authentication. Before deployment, place BiteHarbor behind an authenticated service boundary,
derive customer identity from verified claims, use managed secret storage, encrypt persisted state,
apply rate limits, and define data-retention controls.
