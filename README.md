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

| Category          | Technologies / Direction                                     |
| ----------------- | ------------------------------------------------------------ |
| **Framework**     | FastAPI with explicit service boundaries                     |
| **Messaging**     | Event-driven or broker-based communication as a first-class concern |
| **Persistence**   | Service-owned data model with isolated storage boundaries    |
| **Observability** | Health checks, metrics, structured logging, trace propagation |
| **Architecture**  | Transport adapters, application layer, infrastructure separation |
| **Testing**       | HTTP contract, worker flow, and messaging integration coverage |
| **Code Quality**  | Planned Python lint, format, type-check, and pre-commit baseline |
| **DevOps**        | Planned containerization and CI/CD baseline                  |

---

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (package manager)
- Docker and Docker Compose
- PostgreSQL
- Redis or another broker/stream transport

---

## Quick Start

This repository is intentionally not scaffolded yet. The current goal is to
define the boundary before implementation begins.

```bash
# 1. Clone the template
npx degit teo-garcia/fastapi-template-microservice my-service
cd my-service

# 2. Read the template boundary
open README.md

# 3. Wait for scaffold implementation
# No runnable app is included yet
```

When scaffold work starts, this template is expected to serve a narrow
microservice contract rather than a broad monolith-style API.

---

## Available Scripts

No scripts are available yet. This repository currently defines template scope
only.

Planned script categories:

| Command | Description |
| ------- | ----------- |
| `make dev` | Start development server |
| `make test` | Run test suite |
| `make lint` | Run lint checks |
| `make format` | Run formatting |
| `make check` | Run full validation pipeline |

---

## Testing

No test suite exists yet because the template scaffold has not been created.

**Planned Test Coverage:**

- **HTTP contract tests**: Validate service endpoints and request/response boundaries
- **Messaging flow tests**: Validate publish/consume behavior
- **Worker tests**: Validate async/background processing behavior
- **Integration tests**: Validate service infrastructure boundaries

---

## Health & Observability

Planned baseline:

### Health Checks

- `GET /health/live` - Liveness probe
- `GET /health/ready` - Readiness probe for broker and persistence dependencies
- `GET /health` - Consolidated health summary

### Metrics

- `GET /metrics` - Prometheus-compatible metrics endpoint

### Logging

- Structured logs with request or trace correlation
- Consistent error reporting at transport boundaries
- Support for distributed tracing propagation across service calls and events

---

## Architecture Notes

### Service Model

- Single bounded-context service
- Intended for event-driven or integration-heavy systems
- Communication is message-first, with HTTP used for a focused service contract
- Independent deployment and scaling are expected

### Boundary vs Monolith

| Dimension | `fastapi-template-monolith` | `fastapi-template-microservice` |
| --------- | --------------------------- | ------------------------------- |
| Primary role | Single service API | Messaging-first or integration-focused service |
| System position | Main application backend | Member of a distributed system |
| API shape | Broad REST surface | Narrow service contract |
| Module ownership | Multiple product modules | One bounded context or capability |
| Communication style | HTTP-first | Events/messages first, HTTP second |
| Data ownership | Wider application-owned schema | Service-owned schema with explicit boundaries |
| Scaling model | Scale the whole API | Scale per service need |

### Use This Template When

- The service publishes or consumes events
- The service belongs to a larger distributed system
- Failure isolation and independent scaling matter
- You need the FastAPI equivalent of `nest-template-microservice`

### Do Not Use This Template When

- You are building a primary product API with broad CRUD coverage
- Messaging is optional rather than core to the service
- A standard single-service REST backend is enough

Use `fastapi-template-monolith` instead for broad application APIs.

---

## Deployment

### Docker

Container and deployment files are not implemented yet.

Planned deployment direction:

```bash
# Build production image
docker build -f docker/Dockerfile -t my-service:latest .

# Run service stack
docker-compose up -d
```

---

## Environment Variables

No `.env.example` exists yet. Planned configuration areas include:

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `SERVICE_NAME` | Service identifier for logs and traces | `microservice` |
| `PORT` | Application port | `8000` |
| `DATABASE_URL` | Persistence connection string | Required |
| `BROKER_URL` | Messaging transport connection string | Required |
| `LOG_LEVEL` | Logging verbosity | `info` |
| `METRICS_ENABLED` | Enable metrics endpoint | `true` |

---

## Tooling Comparison (NestJS Parity)

| NestJS | FastAPI | Role |
| ------ | ------- | ---- |
| pnpm | uv | Package manager |
| ESLint + Prettier | ruff | Lint + format |
| tsc --noEmit | mypy | Type checking |
| Jest | pytest | Testing |
| `@nestjs/microservices` | broker adapter + async consumers | Messaging |
| Prisma | SQLAlchemy + Alembic | ORM + migrations |
| class-validator | Pydantic v2 | Validation |
| `@nestjs/config` | Pydantic Settings | Configuration |
| Winston | structlog | Structured logging |
| prom-client | prometheus-client | Metrics |
| Husky + commitlint | pre-commit + commitizen | Git hooks |

---

## Related Templates

- [fastapi-template-monolith](https://github.com/teo-garcia/fastapi-template-monolith) -
  FastAPI single-service API
- [nest-template-microservice](https://github.com/teo-garcia/nest-template-microservice) -
  Event-driven NestJS microservice
- [nest-template-monolith](https://github.com/teo-garcia/nest-template-monolith) -
  NestJS single-service API

---

## License

MIT
