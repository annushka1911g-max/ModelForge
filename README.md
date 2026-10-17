# ⚡ ModelForge

<div align="center">

![ModelForge Banner](https://img.shields.io/badge/ModelForge-Production%20MLOps%20Platform-4F46E5?style=for-the-badge&logo=fastapi&logoColor=white)

**A Self-Hosted MLOps Platform for One-Click Machine Learning Model Deployment, Dynamic Serving, and Real-Time Telemetry**

[![CI Status](https://img.shields.io/badge/CI-Passing%20(75%2F75%20tests)-success?style=flat-square&logo=githubactions&logoColor=white)](https://github.com/annushka1911g-max/ModelForge/actions)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%20%7C%20Vite%205-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?style=flat-square&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker%20Compose-Ready-2496ED?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?style=flat-square&logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?style=flat-square&logo=grafana&logoColor=white)](https://grafana.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

[Quickstart](#-quickstart--local-setup) • [Architecture](#-architecture-overview) • [Key Features](#-key-features) • [Deployment Options](#-deployment-options) • [API Reference](#-api-reference--usage) • [Demo Credentials](#-default-demo-credentials)

</div>

---

## 📌 Executive Summary

**ModelForge** bridges the gap between experimental data science notebooks and resilient production microservices. It is a lightweight, self-hosted, enterprise-grade MLOps platform engineered to take trained machine learning models from serialized artifacts (`.pkl`, `.joblib`, `.json`) to live, low-latency production inference APIs with a single click.

Without third-party vendor lock-in or complex Kubernetes dependencies, ModelForge provides:
- **Centralized Model Registry & Lineage**: Versioning, artifact hashing, feature schema contracts, and training metadata.
- **Sub-Millisecond Dynamic Serving Engine**: In-memory LRU model caching with auto-invalidation on rollback.
- **Strict Pydantic v2 Schema Guardrails**: Rejects malformed payloads with descriptive `422 Unprocessable Entity` diagnostics before touching the ML model runner.
- **Full Deployment Lifecycle Control**: Zero-downtime `DEPLOY`, `STOP`, `RESTART`, and one-click atomic `ROLLBACK`.
- **Dual Inference Modes**: Low-latency real-time REST endpoints and asynchronous bulk CSV batch processing.
- **Production Observability**: Built-in Prometheus telemetry exporter, pre-provisioned Grafana dashboards, and detailed access logging.
- **Enterprise Governance & Security**: Role-Based Access Control (`ADMIN`, `ML_ENGINEER`, `VIEWER`), programmatic API key management (`mf_live_...`), and immutable audit trails.

---

## 🏗️ Architecture Overview

### System Topology

```
                                ┌────────────────────────────────────────┐
                                │           Client / Web Browser         │
                                │   (React 18 + Vite + Tailwind CSS)     │
                                └──────────────────┬─────────────────────┘
                                                   │
                                                   ▼
                                ┌────────────────────────────────────────┐
                                │        Nginx Gateway / Reverse Proxy   │
                                │      (Port 80 / SSL Termination)       │
                                └─────────┬────────────────────┬─────────┘
                                          │                    │
                          /api/v1/*       │                    │  Static Assets
                                          ▼                    ▼
               ┌──────────────────────────────────────┐    ┌───────────────────────┐
               │      ModelForge FastAPI Backend      │    │  Vite Production SPA  │
               │               (:8000)                │    │        (:3000)        │
               ├──────────────────┬───────────────────┤    └───────────────────────┘
               │ Auth & RBAC      │ Catalog & Lineage │
               │ Deployment Engine│ Batch Processor   │
               │ API Key Service  │ Audit Logger      │
               │ Prometheus Expose│ Experiment Tracker│
               └─────────┬────────┴─────────┬─────────┘
                         │                  │
         Model Execution │                  │ Read / Write Metadata
                         ▼                  ▼
     ┌────────────────────────────────┐   ┌────────────────────────────────┐
     │    Inference Serving Engine    │   │      PostgreSQL Database       │
     │ - In-Memory LRU Model Cache    │   │  - Users, Roles & API Keys     │
     │ - Framework Adapters:          │   │  - Models, Versions & Schemas  │
     │   • Scikit-learn (.pkl/.joblib)│   │  - Deployments & Predictions   │
     │   • XGBoost (Booster/Scikit)   │   │  - Batch Jobs & Audit Logs     │
     │ - Pydantic Feature Validator   │   │  - Experiment Runs & Metrics   │
     └───────────────┬────────────────┘   └────────────────────────────────┘
                     │                                    │
                     ▼                                    ▼
     ┌────────────────────────────────┐   ┌────────────────────────────────┐
     │   Object Storage (MinIO / S3)  │   │  Observability (Prom / Grafana)│
     │  - models/ (Artifact Storage)  │   │  - Prometheus Collector (:9090)│
     │  - batch-jobs/ (CSV I/O)       │   │  - Grafana Dashboards (:3001)  │
     └────────────────────────────────┘   └────────────────────────────────┘
```

### Real-Time Prediction Request Lifecycle

```mermaid
sequenceDiagram
    autonumber
    actor Client as Client / API Consumer
    participant Gateway as Nginx / API Gateway
    participant Backend as FastAPI Router (/deployments/{id}/predict)
    participant Validator as Feature Schema Validator
    participant Cache as In-Memory LRU Cache
    participant Adapter as ML Framework Adapter
    participant Metrics as Prometheus Instrumentator
    participant DB as PostgreSQL (Audit / Logs)

    Client->>Gateway: POST /api/v1/deployments/1/predict (JWT / API Key)
    Gateway->>Backend: Forward Authorized Request
    Backend->>Validator: Validate Request Body against Model Schema
    alt Schema Mismatch (Missing / Extra Fields / Type Error)
        Validator-->>Client: 422 Unprocessable Entity (Detailed Schema Diagnostic)
    else Valid Payload
        Backend->>Cache: Fetch Loaded Model Instance (deployment_id)
        alt Cache Miss
            Cache->>Cache: Download Artifact from Storage & Deserialize
        end
        Backend->>Adapter: Execute predict() & predict_proba()
        Adapter-->>Backend: Return Raw Predictions & Probabilities
        Backend->>Metrics: Record Latency Histogram & Counter
        Backend->>DB: Log Asynchronous Prediction Access Record
        Backend-->>Client: 200 OK (prediction, probabilities, latency_ms, timestamp)
    end
```

---

## 🚀 Key Features

### 1. Centralized Model Catalog & Lineage
- Register models with semantic metadata: name, display name, framework (`scikit-learn`, `xgboost`, `pytorch`, `tensorflow`), task type (`classification`, `regression`), and descriptive tags.
- Upload versioned artifacts (`.pkl`, `.joblib`, `.json`) with automatic SHA-256 integrity verification.
- Enforce strict JSON schema definitions for feature inputs and target outputs.
- Star/favorite models for quick team collaboration.
- Version-to-version schema and parameter diffing.

### 2. Sub-Millisecond Dynamic Serving Engine
- **In-Memory LRU Model Caching**: Eliminates per-request deserialization overhead, keeping active model instances warm in memory.
- **Configurable Cache Eviction**: Controlled via `MODEL_CACHE_MAX_SIZE` (default: 5 active models per worker).
- **Automatic Invalidation**: Evicts cached models instantly when a deployment is stopped or rolled back.

### 3. Strict Schema Guardrails & Drift Awareness
- Incoming payloads undergo rigorous schema validation against registered model feature types (`float`, `int`, `str`, `bool`).
- Automatically rejects missing features, unexpected extra fields, and invalid types with standard `422` error messages.
- Feature importance visualization and input distribution drift awareness.

### 4. Complete Deployment Lifecycle Management
| State Action | HTTP Endpoint | Description |
| :--- | :--- | :--- |
| **Deploy** | `POST /api/v1/deployments/` | Instantly spins up a dedicated serving endpoint for any ready model version. |
| **Stop** | `POST /api/v1/deployments/{id}/stop` | Safely suspends incoming traffic and evicts the model from memory without deleting configuration. |
| **Restart** | `POST /api/v1/deployments/{id}/restart` | Re-activates suspended deployments with zero downtime. |
| **Rollback** | `POST /api/v1/deployments/{id}/rollback` | Reverts the active deployment to a specified target version in a single atomic transaction. |

### 5. High-Throughput Asynchronous Batch Inference
- Process bulk CSV datasets asynchronously without blocking the web event loop.
- Client-side and server-side CSV header validation against the registered feature schema.
- Real-time job state transitions: `PENDING` &rarr; `PROCESSING` &rarr; `COMPLETED` / `FAILED`.
- Direct one-click download of processed CSV files containing generated prediction columns.

### 6. Experiment Tracking & Run Comparisons
- Log hyperparameters, training metrics (accuracy, F1-score, ROC-AUC, RMSE, loss), and dataset references.
- Compare candidate runs side-by-side with visual delta indicators.
- Promote winning experimental runs directly into the Model Catalog with a single click.

### 7. Observability & Telemetry
- Native Prometheus exporter at `/api/v1/monitoring/metrics`:
  - `modelforge_predictions_total`: Prediction volume counters tagged by deployment ID and status.
  - `modelforge_prediction_latency_ms`: Execution latency histogram across predefined buckets.
  - `modelforge_active_deployments`: Real-time gauge of active deployments.
- Pre-configured Grafana dashboards in `monitoring/grafana/dashboards`.
- Live access logs with filtering by status code, latency, and deployment.

### 8. Enterprise Role-Based Access Control (RBAC) & API Keys
- Secure JWT-based session authentication with bcrypt password hashing.
- Programmatic service-to-service API keys (`mf_live_...`) with configurable expiration and instant revocation.
- Fine-grained permission model:
  - `ADMIN`: Full platform configuration, user provisioning, role assignments, audit logs.
  - `ML_ENGINEER`: Register models, upload versions, deploy/stop/restart/rollback, run batch jobs, track experiments.
  - `VIEWER`: Read-only access to catalog, deployments, telemetry, and testing in the Playground.
- Append-only audit logging recording all critical user and system actions.

### 9. Modern Web Console & Interactive Playground
- Built with React 18, Vite, and Tailwind CSS.
- **Inference Playground**: Test live endpoints with JSON or 1-click sample dataset injectors (Iris classifier), inspect raw probabilities, and review execution latencies.
- **Global Search**: Instantly query across models, deployments, experiments, and audit records with `Cmd+K` / `Ctrl+K`.

---

## 💻 Tech Stack

| Domain | Technology | Purpose |
| :--- | :--- | :--- |
| **API & Web Framework** | [FastAPI](https://fastapi.tiangolo.com/) | High-performance asynchronous REST API with auto OpenAPI docs |
| **Language & Runtime** | [Python 3.12](https://www.python.org/) | Core backend, data processing, and inference execution |
| **Database & ORM** | [PostgreSQL 16](https://www.postgresql.org/) + [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | Relational metadata catalog and Alembic schema migrations |
| **Schema Validation** | [Pydantic v2](https://docs.pydantic.dev/) | High-speed request validation and settings management |
| **Serving Adapters** | [scikit-learn](https://scikit-learn.org/) & [XGBoost](https://xgboost.readthedocs.io/) | Production model inference runners |
| **Object Storage** | [MinIO](https://min.io/) / AWS S3 | S3-compatible storage for artifacts and batch CSV files |
| **Observability** | [Prometheus](https://prometheus.io/) & [Grafana](https://grafana.com/) | Real-time metric scraping, latency monitoring, and visual dashboards |
| **Frontend Platform** | [React 18](https://react.dev/) + [Vite 5](https://vitejs.dev/) | Fast single-page application dashboard |
| **Type System** | [TypeScript 5](https://www.typescriptlang.org/) | End-to-end type safety for API contracts |
| **Styling & UI** | [Tailwind CSS](https://tailwindcss.com/) + [Lucide Icons](https://lucide.dev/) | Clean, responsive, modern user interface |
| **Containerization** | [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/) | Multi-service local and server orchestration |

---

## 📂 Project Structure

```
ModelForge/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD pipeline (backend & frontend)
├── backend/
│   ├── alembic/                 # Alembic migration scripts
│   ├── app/
│   │   ├── authentication/      # JWT handlers, bcrypt password hashing, RBAC guards
│   │   ├── configuration/       # Pydantic BaseSettings & env configs
│   │   ├── core/                # Logging middleware, custom exceptions, health probes
│   │   ├── database/            # SQLAlchemy session, engine, initial database seed
│   │   ├── models/              # ORM models (User, Model, Version, Deployment, etc.)
│   │   ├── repositories/        # Clean data-access repository layer
│   │   ├── routes/              # Versioned API routes (/api/v1)
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── services/            # Business logic (inference, storage, batch, audit)
│   ├── Dockerfile               # Production multi-stage Docker build for backend
│   └── requirements.txt         # Pinned backend Python dependencies
├── frontend/
│   ├── src/
│   │   ├── authentication/      # AuthContext, ProtectedRoute, useAuth hook
│   │   ├── components/          # Reusable UI components (Navbar, Sidebar, Badges, Modals)
│   │   ├── pages/               # Dashboard, Models, ModelDetail, Deployments,
│   │   │                        # Playground, BatchPredict, Experiments, Monitoring,
│   │   │                        # AuditLogs, UserAdmin, Settings
│   │   ├── services/            # Typed Axios clients for API v1 integration
│   │   └── types/               # TypeScript interface definitions
│   ├── Dockerfile               # Production static build for frontend SPA
│   ├── package.json             # Frontend dependencies & scripts
│   └── vite.config.ts           # Vite configuration & dev proxy
├── inference/
│   ├── adapters/                # Framework adapters (sklearn, xgboost, pytorch, tensorflow)
│   ├── engine/                  # In-memory ModelCache (LRU) and ModelRunner
│   └── validators/              # FeatureSchemaValidator for inference guardrails
├── models/
│   └── samples/                 # Sample training scripts & Iris dataset files
│       ├── iris_batch_input.csv # Sample CSV for batch prediction
│       └── train_sample_model.py# Standalone script to train & export sample model
├── monitoring/
│   ├── prometheus/              # Prometheus scraping configuration
│   └── grafana/                 # Pre-provisioned Grafana dashboards & datasources
├── storage/                     # Local file storage directory (models & batch outputs)
├── tests/
│   ├── integration/             # End-to-end integration tests (auth, API, models, batch)
│   └── unit/                    # Unit tests for adapters, cache, schemas, and settings
├── docker-compose.yml           # Complete multi-container platform orchestration
├── render.yaml                  # 1-Click Render Cloud Blueprint configuration
├── vercel.json                  # Vercel SPA routing rewrite configuration
├── setup.cfg                    # Pytest configuration & test markers
└── .env.example                 # Environment variables template
```

---

## ⚡ Quickstart & Local Setup

You can run ModelForge using **Docker Compose** (recommended for a complete full-stack environment) or **Bare-Metal Local Development**.

### Option A: 🐳 Docker Compose (Recommended)

Spins up the complete stack: Nginx Gateway, React Frontend, FastAPI Backend, PostgreSQL 16, MinIO, Prometheus, and Grafana.

```bash
# 1. Clone the repository
git clone https://github.com/annushka1911g-max/ModelForge.git
cd ModelForge

# 2. Copy the environment configuration
cp .env.example .env

# 3. Build and start all services
docker compose up --build -d
```

#### Service Endpoints

| Service | URL | Credentials / Notes |
| :--- | :--- | :--- |
| **Web Console (Frontend)** | [http://localhost](http://localhost) *(or port 3000)* | See [Demo Credentials](#-default-demo-credentials) |
| **FastAPI Swagger Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive OpenAPI documentation |
| **Health Check Probe** | [http://localhost:8000/health](http://localhost:8000/health) | Live backend & database status |
| **MinIO Console** | [http://localhost:9001](http://localhost:9001) | `minio_admin` / `minio_secure_admin_password_placeholder` |
| **Prometheus Metrics** | [http://localhost:9090](http://localhost:9090) | Metric queries & scrape targets |
| **Grafana Dashboards** | [http://localhost:3001](http://localhost:3001) | `admin` / `grafana_secure_admin_password_placeholder` |

To stop the environment:
```bash
docker compose down
```

---

### Option B: 💻 Bare-Metal Local Development

#### 1. Prerequisites
- **Python 3.12+**
- **Node.js 18+** & **npm**
- **PostgreSQL 14+** (running locally)

#### 2. Backend Setup
```bash
# 1. Create and activate a virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# 2. Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env to set your local PostgreSQL credentials in DATABASE_URL:
# e.g., DATABASE_URL=postgresql://postgres:password@localhost:5432/modelforge_db

# 4. Start the FastAPI backend server
uvicorn backend.app.main:app --port 8000 --reload
```
The backend initializes the database schema and seeds default demo accounts automatically on startup.
Verify the API is running at [http://localhost:8000/docs](http://localhost:8000/docs).

#### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend

# Install Node dependencies
npm install

# Start Vite development server
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## ☁️ Deployment Options

### Deploy to Render (`render.yaml`)
ModelForge includes a production-ready Blueprint specification for [Render](https://render.com/):
1. Push your repository to GitHub.
2. In the Render Dashboard, click **New +** &rarr; **Blueprint**.
3. Select your repository. Render will automatically detect `render.yaml` and provision:
   - **`modelforge-backend`**: Managed Python web service with automatic health checks at `/healthz`.
   - **`modelforge-frontend`**: Static web application serving the React/Vite SPA.
   - **`modelforge-db`**: Managed PostgreSQL database instance.

### Deploy Frontend to Vercel (`vercel.json`)
The repository includes a `vercel.json` configuration configured with Single-Page Application (SPA) routing rewrites.
1. Connect your repository to [Vercel](https://vercel.com/).
2. Set the root directory or build command to:
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Output Directory**: `frontend/dist`
3. Add the `VITE_API_BASE_URL` environment variable pointing to your deployed backend URL (e.g. `https://your-backend.onrender.com/api/v1`).

---

## 🔑 Default Demo Credentials

The platform is pre-seeded with three demo accounts for testing Role-Based Access Control:

| Role | Email | Password | Permissions & Capabilities |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@modelforge.io` | `AdminPassword123!` | Complete control: user administration, status & role changes, audit logs, system settings. |
| **ML Engineer** | `engineer@modelforge.io` | `EngineerPassword123!` | Model catalog registration, artifact version upload, deployment lifecycle (deploy/stop/restart/rollback), batch inference, experiment tracking. |
| **Viewer** | `viewer@modelforge.io` | `ViewerPassword123!` | Read-only browsing: view catalog, monitor deployments, review telemetry, execute test requests in the Playground. |

> 💡 *Quick demo buttons are embedded directly on the Login page for instant one-click credential autofill.*

---

## 📖 API Reference & Usage

ModelForge exposes a clean, versioned RESTful API under `/api/v1`. Full interactive documentation is available via Swagger UI at `/docs`.

### 1. Authentication

#### User Login (JWT)
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=engineer@modelforge.io&password=EngineerPassword123!"
```
**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

#### Programmatic API Key Authentication
You can also authenticate external microservices using API keys generated from the UI or `/api/v1/api-keys/`:
```bash
curl -X GET http://localhost:8000/api/v1/models/ \
  -H "X-API-Key: mf_live_your_api_key_here"
```

---

### 2. Real-Time Inference

#### Execute Prediction
```bash
curl -X POST http://localhost:8000/api/v1/deployments/1/predict \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "features": {
      "sepal_length": 5.1,
      "sepal_width": 3.5,
      "petal_length": 1.4,
      "petal_width": 0.2
    }
  }'
```

**Response (200 OK):**
```json
{
  "prediction": [0],
  "probabilities": [1.0, 0.0, 0.0],
  "model_version": 1,
  "latency_ms": 1.42,
  "timestamp": "2026-10-17T22:15:00.000000Z"
}
```

#### Strict Schema Validation (Negative Example)
If extra unexpected features or missing required features are submitted:
```bash
curl -X POST http://localhost:8000/api/v1/deployments/1/predict \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"features": {"sepal_length": 5.1, "unknown_field": 99.9}}'
```
**Response (422 Unprocessable Entity):**
```json
{
  "detail": "Feature validation failed: Missing required features: ['sepal_width', 'petal_length', 'petal_width']. Unexpected extra features: ['unknown_field']."
}
```

---

### 3. Asynchronous Batch Inference

#### Submit Batch Job
```bash
curl -X POST http://localhost:8000/api/v1/batch/ \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -F "deployment_id=1" \
  -F "file=@models/samples/iris_batch_input.csv"
```
**Response (201 Created):**
```json
{
  "id": 1,
  "deployment_id": 1,
  "status": "PROCESSING",
  "total_records": 15,
  "created_at": "2026-10-17T22:15:30.000000Z"
}
```

#### Download Completed Batch Output
```bash
curl -X GET http://localhost:8000/api/v1/batch/1/download \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -o predictions_output.csv
```

---

### 4. Deployment Lifecycle Controls

```bash
# Pause / Stop active deployment
curl -X POST http://localhost:8000/api/v1/deployments/1/stop \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"

# Restart stopped deployment
curl -X POST http://localhost:8000/api/v1/deployments/1/restart \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>"

# Atomic Rollback to previous version (e.g., version 2)
curl -X POST http://localhost:8000/api/v1/deployments/1/rollback \
  -H "Authorization: Bearer <JWT_ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"target_version_id": 2}'
```

---

### 5. Telemetry & Metrics Exporter

Scrape live Prometheus metrics:
```bash
curl -X GET http://localhost:8000/api/v1/monitoring/metrics
```

**Sample Output:**
```promql
# HELP modelforge_predictions_total Total predictions served
# TYPE modelforge_predictions_total counter
modelforge_predictions_total{deployment_id="1",status="success"} 42.0

# HELP modelforge_prediction_latency_ms Prediction latency in milliseconds
# TYPE modelforge_prediction_latency_ms histogram
modelforge_prediction_latency_ms_bucket{le="5.0"} 38.0
modelforge_prediction_latency_ms_bucket{le="10.0"} 41.0
modelforge_prediction_latency_ms_bucket{le="+Inf"} 42.0

# HELP modelforge_active_deployments Number of active deployments
# TYPE modelforge_active_deployments gauge
modelforge_active_deployments 1.0
```

---

## 🎯 Step-by-Step Demo Workflow

Try the complete ModelForge workflow in under 3 minutes using the bundled sample model:

1. **Sign In**: Navigate to `http://localhost:3000/login` and click **ML Engineer** for quick login.
2. **Dashboard Overview**: Check the platform health overview, active deployments count, and prediction throughput gauges.
3. **Inspect Model Catalog**: Navigate to **Models** to review the pre-registered `iris_classifier` model.
4. **Inspect Lineage & Schemas**: Click on the model to review version lineage (v1, v2, v3), inspect the expected feature types, and observe training parameters.
5. **Manage Deployment**:
   - Go to **Deployments** to see the active serving endpoint.
   - Click **Stop** to suspend traffic, verify that requests are safely rejected with `400 Bad Request`, then click **Restart**.
6. **Inference Playground**:
   - Navigate to the **Inference Playground**.
   - Click **Load Iris Sample** to automatically populate valid features.
   - Click **Run Prediction** to view real-time class inference, confidence probability bars, and sub-millisecond execution latency.
7. **Run Batch Prediction**:
   - Go to **Batch Prediction**, select Deployment #1.
   - Upload `models/samples/iris_batch_input.csv` (or click *Download Sample Iris CSV* in the UI).
   - Click **Submit Batch Job** and observe live state progression (`PENDING` &rarr; `PROCESSING` &rarr; `COMPLETED`).
   - Download the generated output CSV with appended `prediction` and confidence columns.
8. **Audit Trail & Monitoring**:
   - Visit **Monitoring** to view live latency charts, prediction volume, and recent request logs.
   - Check **Audit Logs** to view a tamper-evident audit record of all model actions.
9. **User Administration (Admin Role)**:
   - Log out and log in as `admin@modelforge.io`.
   - Access **User Admin** to invite new users, toggle user access states, or promote roles.

---

## ⚙️ Environment Variables Reference

| Variable | Description | Default Value | Required |
| :--- | :--- | :--- | :---: |
| `ENVIRONMENT` | Operational environment (`development`, `production`, `testing`) | `development` | No |
| `DEBUG` | Enable verbose debug output and reload | `True` | No |
| `APP_NAME` | Display name of the application | `ModelForge` | No |
| `SECRET_KEY` | Cryptographic secret for signing JWT tokens | `*must be set in prod*` | **Yes** |
| `ALGORITHM` | JWT signing algorithm | `HS256` | No |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Lifetime of issued JWT session tokens | `60` | No |
| `DATABASE_URL` | Full SQLAlchemy connection string for PostgreSQL | `postgresql://...` | **Yes** |
| `BACKEND_CORS_ORIGINS` | JSON list of allowed CORS client origins | `["http://localhost:3000"]` | No |
| `STORAGE_BACKEND` | Artifact storage engine (`local` or `s3`) | `local` | No |
| `STORAGE_DIR` | Local filesystem path for artifact persistence | `./storage` | No |
| `MINIO_ENDPOINT` | Host and port for MinIO S3 object storage | `localhost:9000` | If S3 |
| `MINIO_ROOT_USER` | MinIO root access key | `minio_admin` | If S3 |
| `MINIO_ROOT_PASSWORD` | MinIO root secret password | `minio_secure_password` | If S3 |
| `MINIO_BUCKET_MODELS` | Bucket name for serialized model artifacts | `models` | No |
| `MINIO_BUCKET_BATCH` | Bucket name for batch prediction CSVs | `batch-jobs` | No |
| `MODEL_CACHE_MAX_SIZE` | Maximum number of concurrent models held in LRU memory | `5` | No |
| `MODEL_STORAGE_DIR` | Directory for staging downloaded model artifacts | `/tmp/modelforge/cache` | No |

---

## 🧪 Automated Testing & Quality Assurance

ModelForge enforces comprehensive test coverage across both unit logic and integration flows.

### Running the Pytest Suite
```bash
# Run all 75 automated tests in quiet mode
python -m pytest -q
```

### Test Coverage Highlights (75 Tests Passing)
- **Authentication & RBAC**: JWT token issuing, expiration, bcrypt hashing, role permission guards (Admin, ML Engineer, Viewer), unauthorized/forbidden action rejection (`401` & `403`).
- **API Key Lifecycle**: Generation of `mf_live_...` keys, header verification, expiration enforcement, and instant revocation.
- **Model Registry & Versions**: Model creation, duplicate constraint handling, artifact upload, SHA-256 verification, and JSON schema parsing.
- **Deployment Lifecycle**: End-to-end `deploy` &rarr; `stop` &rarr; `restart` &rarr; `rollback` state validation and cache invalidation.
- **Inference Guardrails**: Valid prediction execution, missing feature detection (`422`), unexpected feature rejection (`422`), type mismatch validation (`422`), stopped deployment rejection (`400`).
- **Batch Processing**: Asynchronous CSV job creation, header validation, execution runner, and result download.
- **Audit Logging & Telemetry**: Event recording, Prometheus metric counters, latency histograms, and system health checks (`/health`, `/health/live`, `/health/ready`).

---

## 🤝 Contributing

Contributions to ModelForge are always welcome!

1. Fork the Project repository.
2. Create your Feature Branch:
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. Commit your Changes:
   ```bash
   git commit -m "feat: add AmazingFeature support"
   ```
4. Push to the Branch:
   ```bash
   git push origin feature/AmazingFeature
   ```
5. Open a Pull Request.

Please ensure all tests pass (`python -m pytest`) and code is formatted cleanly before opening a pull request.

---

## 📄 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more information.

---

<div align="center">
  <sub>Built with care for Machine Learning Engineers and Platform Architects.</sub><br>
  <sub>ModelForge • Open Source Self-Hosted MLOps</sub>
</div>
