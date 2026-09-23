# ModelForge

> **A Self-Hosted MLOps Platform for One-Click Model Deployment**

ModelForge is a lightweight, self-hosted MLOps platform engineered to take trained machine learning models from artifacts to live production inference APIs with a single click.

---

## Architecture Overview

```
ModelForge/
├── backend/          # FastAPI REST API, database models, schemas, and services
├── frontend/         # React + TypeScript + Tailwind CSS web dashboard
├── inference/        # Dynamic model serving engine and ML framework adapters
├── monitoring/       # Prometheus scraper configs and pre-provisioned Grafana dashboards
├── deployment/       # Nginx gateway config and initialization scripts
├── models/           # Sample model artifacts, training scripts, and input schemas
├── tests/            # Automated test suite (unit and integration tests)
├── docker-compose.yml# Multi-container local orchestration
├── .env.example      # Environment variable template
├── .gitignore        # Git ignore rules
└── README.md         # Documentation and setup guide
```

---

## Quick Start Guide

### 1. Prerequisites
- Docker Engine & Docker Compose (v2.20+)
- Python 3.12+ (for local development/testing)
- Node.js 20+ & npm (for local frontend development)

### 2. Configure Environment Variables
Copy the `.env.example` template:
```bash
cp .env.example .env
```
Update `.env` with secure credentials and random secret keys.

### 3. Run with Docker Compose
Launch all services in detached mode:
```bash
docker compose up -d --build
```

### 4. Service Endpoints
- **Web Dashboard**: [http://localhost](http://localhost) (via Nginx reverse proxy)
- **API Documentation (Swagger)**: [http://localhost/docs](http://localhost/docs)
- **MinIO Console**: [http://localhost:9001](http://localhost:9001)
- **Prometheus UI**: [http://localhost:9090](http://localhost:9090)
- **Grafana Dashboards**: [http://localhost:3001](http://localhost:3001)

---

## Supported ML Frameworks
- **Scikit-Learn** (`.joblib`, `.pkl`)
- **XGBoost** (`.json`, `.model`)
- **PyTorch** (`.pt`, `.pth`)
- **TensorFlow / Keras** (`SavedModel`, `.keras`, `.h5`)

---

## Development Guidelines
- **Zero Business Logic in Skeleton**: This initial scaffold establishes clean architectural boundaries, dependency inversion, and typing contracts.
- **Role-Based Access Control**: Standardized permissions across `ADMIN`, `ML_ENGINEER`, and `VIEWER`.
- **Stateless Model Serving**: Dynamic inference engine loads models on-demand from MinIO into an in-memory LRU cache.
