# Architecture Decision Records (ADRs)

This folder contains Architecture Decision Records documenting significant technical decisions.

---

## What is an ADR?

An ADR captures a significant architectural decision along with its context and consequences.

---

## Naming Convention

```
NNN-short-title.md

Examples:
001-use-postgresql.md
002-jwt-authentication.md
003-docker-deployment.md
```

---

## Template

```markdown
# ADR-NNN: [Title]

**Date**: [Date]  
**Status**: Proposed | Accepted | Deprecated | Superseded by ADR-XXX  
**Author**: [Name]

## Context

[What is the issue that we're seeing that is motivating this decision?]

## Decision

[What is the change that we're proposing and/or doing?]

## Options Considered

### Option 1: [Name]
- Pros: [...]
- Cons: [...]

### Option 2: [Name]
- Pros: [...]
- Cons: [...]

## Consequences

### Positive
- [Positive outcome 1]
- [Positive outcome 2]

### Negative
- [Negative outcome 1]
- [Mitigation strategy]

## References

- [Link to relevant docs]
- [Link to discussion]
```

---

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| 001 | [Example: Use PostgreSQL] | Accepted | 2024-01-09 |

---

## Example ADR

```markdown
# ADR-001: Use PostgreSQL for Primary Database

**Date**: 2024-01-09  
**Status**: Accepted  
**Author**: Jerry

## Context

We need to choose a primary database for the application. 
Key requirements:
- ACID compliance for financial transactions
- JSON support for flexible schema
- Full-text search capabilities
- Strong ecosystem and tooling

## Decision

We will use PostgreSQL 16 as our primary database.

## Options Considered

### Option 1: PostgreSQL
- Pros: ACID, JSON support, full-text search, mature ecosystem
- Cons: Requires more setup than SQLite

### Option 2: MySQL
- Pros: Popular, good performance
- Cons: Weaker JSON support, less feature-rich

### Option 3: MongoDB
- Pros: Flexible schema, easy scaling
- Cons: No ACID guarantees, different paradigm

## Consequences

### Positive
- Strong data integrity with ACID transactions
- JSONB for flexible document storage
- pg_trgm for full-text search
- Extensive tooling (pgAdmin, psql)

### Negative
- More complex setup than SQLite
- Requires connection pooling at scale
- Mitigation: Use SQLAlchemy with pooling

## References

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Why PostgreSQL](https://www.postgresql.org/about/)
```
