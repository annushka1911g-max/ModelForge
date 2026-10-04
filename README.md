# ModelForge

> **A Self-Hosted MLOps Platform for One-Click Machine Learning Model Deployment**

ModelForge is a complete, lightweight, self-hosted MLOps platform engineered to take trained machine learning models from artifacts to live production inference APIs with a single click. It provides robust model registry, artifact storage, feature schema validation, dynamic serving with in-memory caching, deployment lifecycle management (deploy, stop, restart, rollback), real-time & batch inference, Prometheus telemetry, and role-based access control (RBAC).

---

## Architecture Overview

```
                               ┌────────────────────────────────────────┐
                               │           Client / Frontend            │
                               │      (React + Vite + Tailwind)         │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                               ┌────────────────────────────────────────┐
                               │        Nginx Gateway / Reverse Proxy   │
                               │           (Port 80 / localhost)        │
                               └──────────────────┬─────────────────────┘
                                                  │
                                                  ▼
                        ┌───────────────────────────────────────────────────────┐
                        │              ModelForge FastAPI Backend               │
                        │                       (/api/v1)                       │
                        ├───────────────────┬───────────────────────────────────┤
                        │ Auth & RBAC       │ Models & Lineage Catalog          │
                        │ Deployment Service│ Storage Service (Local / MinIO)   │
                        │ Batch Processor   │ Prometheus Metrics & Logs         │
                        └─────────┬─────────┴─────────────────┬─────────────────┘
                                  │                           │
                                  ▼                           ▼
          ┌──────────────────────────────────┐      ┌─────────────────────────────┐
          │     Inference Serving Engine     │      │     PostgreSQL Metadata     │
          │  - Dynamic Model Runner          │      │  - Users & Roles            │
          │  - In-Memory LRU Cache           │      │  - Models & Versions        │
          │  - Schema Validators             │      │  - Deployments & Logs       │
          │  - Sklearn / XGBoost Adapters    │      │  - Batch Jobs               │
          └──────────────────────────────────┘      └─────────────────────────────┘
```

---

## Key Features

1. **Model Catalog & Version Lineage**: Register models, upload versioned model artifacts (`.pkl`, `.joblib`, `.json`), track training metrics, file hashes, and feature schemas.
2. **Dynamic Inference Serving**: Dynamic in-memory LRU model caching avoids reload overhead per request while preserving sub-millisecond predictions.
3. **Strict Feature Schema Validation**: Validates all incoming inference features against the model's schema before invocation, rejecting missing features, unexpected fields, and type mismatches with clean 422 HTTP responses.
4. **Complete Deployment Lifecycle**:
   - `DEPLOY`: Instantly serve any ready model version.
   - `STOP`: Safely suspend endpoints without deleting configuration.
   - `RESTART`: Re-activate stopped deployments.
   - `ROLLBACK`: Seamless one-click reversion to prior versions with automatic cache eviction.
5. **High-Throughput Batch Predictions**: Upload bulk dataset CSVs for asynchronous batch processing, progress tracking (`PENDING` &rarr; `PROCESSING` &rarr; `COMPLETED`/`FAILED`), and instant CSV result downloads.
6. **Telemetry & Monitoring**: Live calculation of prediction volumes, success/error rates, execution latencies, Prometheus metrics export (`/api/v1/monitoring/metrics`), and detailed prediction access logging.
7. **Role-Based Access Control (RBAC)**:
   - `ADMIN`: Full platform control, user administration, status/role assignment.
   - `ML_ENGINEER`: Register models, upload versions, deploy, stop, restart, rollback, run inferences.
   - `VIEWER`: Read-only access to catalog, deployments, logs, and telemetry.

---

## Tech Stack

### Backend
- **Python 3.12**
- **FastAPI** (REST API & OpenAPI)
- **SQLAlchemy** (PostgreSQL ORM)
- **Pydantic v2** (Strict schema validation)
- **Passlib & python-jose** (Bcrypt password hashing & JWT authentication)
- **Alembic** (Database schema migrations)
- **pytest & httpx** (Automated test suite)

### Serving & ML
- **scikit-learn** (Primary production serving engine)
- **XGBoost** (Booster & Scikit-learn API models)
- **pandas & numpy** (Vectorized feature manipulation)

### Frontend
- **React 18**
- **Vite 5**
- **TypeScript**
- **Tailwind CSS**
- **Axios & Lucide React**

---

## Project Structure

```
ModelForge/
├── backend/
│   ├── alembic/                # Alembic database migrations
│   └── app/
│       ├── authentication/     # JWT, password hashing, RBAC guards
│       ├── configuration/      # Pydantic BaseSettings & env configs
│       ├── core/               # Error handlers, logging middleware, health checks
│       ├── database/           # SQLAlchemy session, engine, seed script
│       ├── models/             # SQLAlchemy ORM database models
│       ├── repositories/       # Data access repository layer
│       ├── routes/             # Versioned REST API routers (/api/v1)
│       ├── schemas/            # Pydantic request/response schemas
│       └── services/           # Business logic layer (inference, models, deployments, batch, storage)
├── frontend/
│   ├── src/
│   │   ├── authentication/     # AuthContext, ProtectedRoute, useAuth hook
│   │   ├── components/         # Reusable UI components (Button, Badge, Modal, Navbar, Sidebar)
│   │   ├── dashboard/          # MetricsSummary, RecentDeployments components
│   │   ├── pages/              # Login, Register, Dashboard, Models, ModelDetail,
│   │   │                       # Deployments, Playground, BatchPredict, Monitoring, UserAdmin
│   │   ├── services/           # Typed API clients for backend integration
│   │   └── types/              # TypeScript definitions
│   └── package.json
├── inference/
│   ├── adapters/               # Framework adapters (sklearn, xgboost, pytorch, tensorflow)
│   ├── engine/                 # In-memory ModelCache and ModelRunner
│   └── validators/             # FeatureSchemaValidator
├── models/
│   └── samples/                # Sample training scripts and sample Iris dataset CSVs
├── storage/                    # Local artifact storage (models and batch outputs)
├── tests/
│   ├── integration/            # API, Auth, Models, Deployments, Inference, Batch, Monitoring tests
│   └── unit/                   # Adapters, cache, schemas, settings unit tests
├── docker-compose.yml          # Multi-service container orchestration
├── .env.example                # Environment variable template
└── README.md
```

---

## Quickstart & Local Setup

### 1. Prerequisites
- Python 3.12+ (in virtual environment `.venv`)
- PostgreSQL database
- Node.js 18+ & npm

### 2. Environment Configuration
Ensure `.env` exists (copied from `.env.example`):
```bash
cp .env.example .env
```

### 3. Run Backend Server
```bash
# In ModelForge directory:
source .venv/bin/activate
uvicorn backend.app.main:app --port 8000 --reload
```
API Documentation (Swagger UI) is available at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Run Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Default Demo Credentials

Pre-seeded demo accounts ready for immediate login:

| Role | Email | Password | Permissions |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@modelforge.io` | `AdminPassword123!` | Full admin access, user management, deployment lifecycle |
| **ML Engineer** | `engineer@modelforge.io` | `EngineerPassword123!` | Model registration, version upload, deploy, stop, restart, rollback |
| **Viewer** | `viewer@modelforge.io` | `ViewerPassword123!` | Read-only browsing, metrics, playground testing |

*(Quick demo buttons are also provided on the Login page for one-click credential autofill).*

---

## Running Automated Tests

Run the full pytest suite (67 unit and integration tests):
```bash
./.venv/bin/pytest -q
```

All 67 tests validate:
- Authentication & JWT token issuing
- RBAC permissions & forbidden action prevention (403)
- Model registration, retrieval, listing, duplicate rejection
- Model version artifact uploads & JSON schema parsing
- Deployment lifecycle (deploy &rarr; stop &rarr; restart &rarr; rollback)
- Real-time inference with schema validation:
  - Valid request processing (Iris classification)
  - Missing feature handling (422)
  - Unexpected/extra feature rejection (422)
  - Type mismatch rejection (422)
  - Deployment not found (404)
  - Stopped deployment rejection (400)
- High-throughput batch prediction CSV jobs (creation, execution, completion, schema mismatch failure, result download)
- Prometheus metrics & monitoring telemetry statistics

---

## Example Prediction Request (Iris Classifier)

### Endpoint
`POST /api/v1/deployments/1/predict`

### Request Headers
```http
Authorization: Bearer <JWT_ACCESS_TOKEN>
Content-Type: application/json
```

### Request Body
```json
{
  "features": {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }
}
```

### Response (200 OK)
```json
{
  "prediction": [0],
  "probabilities": [1.0, 0.0, 0.0],
  "model_version": 3,
  "latency_ms": 13.42,
  "timestamp": "2026-10-04T10:07:10.944276Z"
}
```

---

## End-to-End Demo Workflow

1. **Sign In**: Navigate to `http://localhost:3000/login` and click **ML Engineer** or **Admin** quick-login.
2. **Platform Dashboard**: Observe live metrics (Active Deployments, Total Inferences, Avg Latency).
3. **Model Catalog**: Navigate to **Models**, click **+ Register New Model** or select existing `iris_classifier`.
4. **Inspect Lineage & Artifacts**: View version history (v1, v2, v3), inspect the JSON feature schema, and click **Deploy v1**.
5. **Manage Deployment**: On the **Deployments** page, observe status `DEPLOYED`, test stopping the endpoint, restarting, or rolling back.
6. **Inference Playground**: Navigate to **Inference Playground**, click **Load Iris Sample**, and click **Run Prediction**. View real-time class predictions, probability distributions, and execution latency.
7. **Batch Prediction**: On **Batch Prediction**, select Deployment #1, upload `models/samples/iris_batch_input.csv` (or click *Download Sample Iris CSV*), click **Submit Batch Job**, and watch live progress complete with a downloadable CSV containing predictions.
8. **Telemetry & Monitoring**: Navigate to **Monitoring & Metrics** to inspect real-time call counts, error rates, and live access logs.
9. **User Administration (Admin Only)**: Log in as `admin@modelforge.io`, navigate to **User Admin**, toggle user statuses, and manage team roles.
