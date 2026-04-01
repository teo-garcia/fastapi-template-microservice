<div align="center">

# FastAPI Template Microservice

**Production-oriented FastAPI microservice boundary for messaging-first and
integration-focused services**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9)](https://docs.astral.sh/uv/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Redis](https://img.shields.io/badge/Redis-Messaging-DC382D?logo=redis&logoColor=white)](https://redis.io)

Part of the [@teo-garcia/templates](https://github.com/teo-garcia/templates)
ecosystem

</div>

---

## Features

| Category          | Technologies                                              |
| ----------------- | --------------------------------------------------------- |
| **Framework**     | FastAPI with explicit service boundaries                  |
| **Messaging**     | Event-driven or broker-based communication first-class    |
| **Persistence**   | Service-owned data model with isolated storage boundaries |
| **Observability** | Health checks, metrics, structured logging, trace propagation |
| **Testing**       | HTTP contract, worker flow, and messaging integration coverage |
| **Code Quality**  | Planned ruff, mypy, pre-commit baseline                   |

---

## Requirements

- Python 3.12+
- uv (package manager)
- Docker and Docker Compose
- PostgreSQL
- Redis or another broker transport

---

## Status

This repository defines the template boundary but is not fully scaffolded yet.
Clone it and use the README as a starting point for a narrow microservice
contract rather than a broad monolith-style API.

---

## Shared Governance

| Area               | Tooling                                        |
| ------------------ | ---------------------------------------------- |
| Dependency updates | Renovate                                       |
| Issue intake       | GitHub issue templates                         |
| Change review      | Pull request template                          |
| Repo hygiene       | Pre-commit baseline                            |
| Delivery model     | Draft-only until the full scaffold is in place |

---

## Boundary vs Monolith

| Dimension          | `fastapi-template-monolith`          | `fastapi-template-microservice`       |
| ------------------ | ------------------------------------ | ------------------------------------- |
| Primary role       | Single service API                   | Messaging-first or integration service |
| API shape          | Broad REST surface                   | Narrow service contract               |
| Module ownership   | Multiple product modules             | One bounded context                   |
| Communication      | HTTP-first                           | Events/messages first, HTTP second    |
| Data ownership     | Application-owned schema             | Service-owned with explicit boundaries |
| Scaling model      | Scale the whole API                  | Scale per service need                |

---

## When to Use This Template

- The service publishes or consumes events
- The service belongs to a larger distributed system
- Failure isolation and independent scaling matter
- You need the FastAPI equivalent of `nest-template-microservice`

Use `fastapi-template-monolith` instead for broad application APIs.

---

## Tooling Comparison (NestJS Parity)

| NestJS                       | FastAPI                      | Role            |
| ---------------------------- | ---------------------------- | --------------- |
| pnpm                         | uv                           | Package manager |
| ESLint + Prettier            | ruff                         | Lint + format   |
| tsc --noEmit                 | mypy                         | Type checking   |
| Jest                         | pytest                       | Testing         |
| `@nestjs/microservices`      | broker adapter + consumers   | Messaging       |
| Prisma                       | SQLAlchemy + Alembic         | ORM + migrations |
| Winston                      | structlog                    | Logging         |
| prom-client                  | prometheus-client            | Metrics         |

---

## Related Templates

| Template                       | Description                |
| ------------------------------ | -------------------------- |
| `fastapi-template-monolith`    | FastAPI single-service API |
| `nest-template-microservice`   | NestJS equivalent          |
| `nest-template-monolith`       | NestJS single-service API  |
| `react-template-next`          | Next.js frontend           |

---

## License

MIT

---

<div align="center">
  <sub>Built by <a href="https://github.com/teo-garcia">teo-garcia</a></sub>
</div>
