<div align="center">

# FastAPI Template Microservice

**Production-oriented FastAPI microservice boundary for messaging-first and
integration-focused services**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![uv](https://img.shields.io/badge/uv-package%20manager-DE5FE9)](https://docs.astral.sh/uv/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![NATS](https://img.shields.io/badge/NATS-JetStream-27AAE1)](https://nats.io)
[![Redis](https://img.shields.io/badge/Redis-Cache%20%2F%20Rate%20Limit-DC382D?logo=redis&logoColor=white)](https://redis.io)

Part of the [@teo-garcia/templates](https://github.com/teo-garcia/templates)
ecosystem

</div>

---

## Features

| Category          | Technologies                                              |
| ----------------- | --------------------------------------------------------- |
| **Framework**     | FastAPI with explicit service boundaries                  |
| **Messaging**     | NATS JetStream boundary with governed stack interop       |
| **Persistence**   | Service-owned data model with isolated storage boundaries |
| **Observability** | Health checks, metrics, structured logging, trace propagation |
| **Testing**       | pytest, stack health checks, and NATS smoke coverage      |
| **Code Quality**  | Ruff, mypy, pre-commit baseline                           |

---

## Requirements

- Python 3.12+
- uv (package manager)
- Docker and Docker Compose
- PostgreSQL
- Redis
- NATS with JetStream enabled

---

## Status

This repository is active and scaffolded from the FastAPI monolith operational
baseline, then narrowed for bounded microservice work. It includes HTTP
endpoints, PostgreSQL, Redis, observability, health checks, and a NATS JetStream
messaging boundary.

---

## Shared Governance

| Area               | Tooling                                        |
| ------------------ | ---------------------------------------------- |
| Dependency updates | Renovate                                       |
| Issue intake       | GitHub issue templates                         |
| Change review      | Pull request template                          |
| Repo hygiene       | Pre-commit baseline                            |
| Delivery model     | Local stack through `microservices-template-stack` |

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
Use `fastapi-template-monolith` instead for broad application APIs.

---

## Local Stack Verification

Run the governed multi-service stack from the portfolio root:

```bash
docker compose -f microservices-template-stack/docker-compose.yml up --build -d
curl -fsS http://localhost:8000/health/ready
node microservices-template-stack/smoke/nats-template-interop-smoke.mjs
```

The readiness endpoint checks PostgreSQL, Redis, and NATS JetStream. Concrete
cross-service interop proofs live in the stack harness, not in this template's
application code.

---

## Production Boundaries

This template is production-oriented, but it is not a complete production
platform by itself. Before deploying a real service, define the auth boundary,
secrets source, ingress/API gateway, event catalog, tracing backend, deployment
topology, and release process for the target environment.

---

## Related Templates

| Template                       | Description                |
| ------------------------------ | -------------------------- |
| `fastapi-template-monolith`    | FastAPI single-service API |
| `react-template-next`          | Next.js frontend           |

---

## License

MIT

---

<div align="center">
  <sub>Built by <a href="https://github.com/teo-garcia">teo-garcia</a></sub>
</div>
