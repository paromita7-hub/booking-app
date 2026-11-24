# Azzurro Hotels — Booking.com Review Insights Dashboard

A production-quality operational analytics and guest satisfaction platform built for Azzurro Hotels. The application monitors, aggregates, and analyzes guest reviews across four Sydney hotel properties:
1. **Olympic Hotel Paddington**
2. **Potts Point**
3. **Central Sydney**
4. **Darling Harbour**

The platform is purpose-built for non-technical hotel operations teams and general managers to monitor guest satisfaction trends, compare property benchmarks, isolate recurring operational failures, and take immediate corrective action.

---

## 1. Project Overview

Non-technical hotel operations staff require a real-time, trustworthy dashboard to understand guest feedback without sifting through hundreds of raw Booking.com review cards. 

This platform provides:
- **Operations & Performance Overview**: Dynamic KPI cards, historical trend lines, sentiment breakdown, property benchmarks, and top recurring issue alerts.
- **Properties Portfolio**: Side-by-side performance comparison, negative issue badges, and deep-dive inspection drawers.
- **Reviews Explorer**: Multi-dimensional search and filtering (by property, date range, 1-10 rating scale, sentiment, and the 8 standard operational topics), full pagination, and CSV export.
- **Operational Insights Action Center**: Weekly comparison of operational issue ratios (e.g., *"Cleanliness mentioned in 40% of negative reviews this week, up from 25% last week"*), root-cause interpretations, and supporting guest review quotes.
- **Data Imports Hub**: Pluggable CSV and JSON ingestion with SHA-256 fingerprint deduplication, audit logging, and downloadable CSV template.

---

## 2. Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router, React 18, TypeScript)
- **Styling**: Tailwind CSS with custom design tokens for light theme, navy accents, and subtle neutral cards
- **Data Visualization**: Recharts (interactive LineCharts and BarCharts)
- **Icons**: Lucide React
- **Architecture**: Responsive layout with collapsible sidebar and property scope selector

### Backend
- **Framework**: Python 3.12+ / FastAPI
- **ORM & Migrations**: SQLAlchemy 2.x and Alembic
- **Validation**: Pydantic v2
- **Data Processing**: Pandas, Python-dateutil, Pytz
- **Testing**: Pytest & Pytest-asyncio

### Database
- **Database Engine**: PostgreSQL 16
- **Architecture**: Normalized relational schema with strict foreign keys, cascade rules, and compound indexes

### Deployment & Tooling
- **Containerization**: Docker & Docker Compose
- **Fast Package Management**: `uv` (Python) and `npm` (Node.js)

---

## 3. Architecture Overview

```
                          ┌─────────────────────────────┐
                          │   Next.js 14 Frontend App   │
                          │   (Tailwind CSS + Recharts) │
                          └──────────────┬──────────────┘
                                         │  REST JSON
                                         ▼
                          ┌─────────────────────────────┐
                          │     FastAPI Monolith API    │
                          │  (/properties, /reviews,    │
                          │   /analytics, /ingestion)   │
                          └──────┬───────────────┬──────┘
                                 │               │
                 ┌───────────────▼──┐         ┌──▼──────────────────┐
                 │ Analysis Engine  │         │ Ingestion Service   │
                 │ - Sentiment      │         │ - CSV/JSON Adapters │
                 │ - 8 Topic Rules  │         │ - Fingerprinting    │
                 │ - BaseClassifier │         │ - Scraper Gate      │
                 └──────────────────┘         └──┬──────────────────┘
                                                 │
                                                 ▼
                          ┌─────────────────────────────┐
                          │    PostgreSQL Database      │
                          │  - properties               │
                          │  - reviews                  │
                          │  - review_topics            │
                          │  - ingestion_logs           │
                          └─────────────────────────────┘
```

---

## 4. Folder Structure

```
booking_app/
├── backend/
│   ├── alembic/                 # Alembic migration scripts and versions
│   │   ├── env.py
│   │   └── versions/
│   ├── app/
│   │   ├── api/                 # FastAPI REST route controllers
│   │   │   ├── analytics.py
│   │   │   ├── ingestion.py
│   │   │   ├── properties.py
│   │   │   └── reviews.py
│   │   ├── models/              # SQLAlchemy 2.0 ORM models
│   │   │   ├── ingestion_log.py
│   │   │   ├── property.py
│   │   │   ├── review.py
│   │   │   └── review_topic.py
│   │   ├── schemas/             # Pydantic v2 validation schemas
│   │   │   ├── analytics.py
│   │   │   ├── ingestion.py
│   │   │   ├── property.py
│   │   │   └── review.py
│   │   ├── services/            # Core business logic
│   │   │   ├── analysis_engine.py
│   │   │   ├── analytics_service.py
│   │   │   └── ingestion_service.py
│   │   ├── config.py            # Environment settings
│   │   ├── database.py          # SQLAlchemy engine & sessionmaker
│   │   └── main.py              # Application entrypoint & middleware
│   ├── tests/                   # Pytest test suite
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
├── frontend/
│   ├── app/                     # Next.js App Router pages
│   │   ├── imports/page.tsx     # Data Ingestion Hub
│   │   ├── insights/page.tsx    # Operational Insights Action Center
│   │   ├── properties/page.tsx  # Properties Portfolio
│   │   ├── reviews/page.tsx     # Reviews Explorer Feed
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx             # Overview Dashboard
│   ├── components/              # Sidebar, Header, KPI Cards
│   ├── lib/                     # API client & utility functions
│   ├── types/                   # TypeScript schemas
│   ├── Dockerfile
│   └── package.json
├── data/
│   └── sample_reviews.csv       # Pre-generated 105 demo reviews
├── scripts/
│   └── seed.py                  # Idempotent database seed script
├── docs/                        # Internal documentation
├── docker-compose.yml           # Full multi-container composition
├── .env.example                 # Sanitized environment template
└── README.md
```

---

## 5. Database Schema Overview

### `properties`
Stores hotel properties managed by Azzurro Hotels.
- `id` (INT, PK): 1 to 4
- `name` (VARCHAR): Unique hotel name
- `booking_url` (VARCHAR): Official Booking.com listing URL
- `location` (VARCHAR): Location / Suburb
- `created_at` (TIMESTAMPTZ)

### `reviews`
Stores guest reviews collected via CSV, JSON, or authorized scraping.
- `id` (INT, PK)
- `external_id` (VARCHAR, Indexed): External review ID from Booking.com export
- `property_id` (INT, FK -> properties.id, Indexed)
- `title` (VARCHAR)
- `positive_text` (TEXT): Positive review remarks ("What they liked")
- `negative_text` (TEXT): Negative review remarks ("What could be improved")
- `rating` (FLOAT, Indexed): Rating on 1.0–10.0 scale
- `review_date` (DATE, Indexed): Date of review publication
- `stay_date` (DATE): Date of stay
- `reviewer_country` (VARCHAR, Indexed)
- `traveler_type` (VARCHAR, Indexed): Couple, Solo traveler, Family, etc.
- `room_type` (VARCHAR)
- `language` (VARCHAR)
- `source` (VARCHAR): `csv_import`, `json_import`, `demo_seed`
- `content_fingerprint` (VARCHAR(64), UNIQUE, Indexed): SHA-256 hash of normalized content
- `is_demo` (BOOLEAN, Indexed): Indicates synthetic demo record
- `created_at` & `updated_at` (TIMESTAMPTZ)

### `review_topics`
Normalized operational topic classifications per review.
- `id` (INT, PK)
- `review_id` (INT, FK -> reviews.id, Indexed, Cascade Delete)
- `topic` (VARCHAR, Indexed): One of the 8 operational topics
- `sentiment` (VARCHAR, Indexed): Positive, Negative, Mixed, Neutral
- `confidence` (FLOAT): Confidence score (0.0 - 1.0)
- `matched_keywords` (JSON): Matched keywords

### `ingestion_logs`
Audit log tracking each ingestion execution.
- `id` (INT, PK)
- `source` (VARCHAR)
- `property_id` (INT, FK, Nullable)
- `status` (VARCHAR): `completed`, `partial`, `failed`
- `records_processed`, `records_added`, `records_skipped` (INT)
- `error_message` (TEXT)
- `started_at` & `completed_at` (TIMESTAMPTZ)

---

## 6. Getting Started & Installation

### Option A: Running with Docker Compose (Recommended)

1. Clone the repository and navigate into the project directory:
   ```bash
   cd booking_app
   ```
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Start all services:
   ```bash
   docker compose up --build -d
   ```
4. Seed the four properties and 105 demo reviews:
   ```bash
   docker compose exec backend python scripts/seed.py
   ```
5. Access the application:
   - Frontend: **http://localhost:3000**
   - Backend API Docs (Swagger): **http://localhost:8000/api/docs**
   - API Health Check: **http://localhost:8000/api/health**

---

### Option B: Running Locally without Docker

#### Prerequisites
- Node.js 18+ & npm
- Python 3.12+ (or `uv`)
- PostgreSQL 14+ running locally with database `booking_reviews`

#### 1. Setup Backend
```bash
cd backend

# Create virtual environment and install packages
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Seed properties and demo reviews
python ../scripts/seed.py

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 2. Setup Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit **http://localhost:3000** in your browser.

---

## 7. Review Collection & Ingestion Methodology

### Source-Adapter Architecture
The ingestion service is architectured around a pluggable source-adapter pattern:
- `CSVIngestionAdapter`: Parses standard CSV exports. Contains intelligent column alias mapping (`pros` -> `positive_text`, `score` -> `rating`, etc.).
- `JSONIngestionAdapter`: Accepts structured JSON review arrays or wrapped objects (`{"reviews": [...]}`).
- `PlaywrightScraperAdapter`: A safe adapter that strictly checks `settings.ALLOW_AUTOMATED_SCRAPING`. If `false`, automated scraping is blocked.

### Deduplication Methodology
To guarantee incremental imports without duplicate records:
1. **External ID Match**: If an `external_id` (e.g., `DEMO-REV-0012`) exists for the property, the record is skipped.
2. **Deterministic Content Fingerprint**: If no external ID is available, the service generates a SHA-256 fingerprint:
   $$\text{SHA256}(\text{property\_id} \parallel \text{review\_date} \parallel \text{rating} \parallel \text{clean}(\text{title}) \parallel \text{clean}(\text{pos}) \parallel \text{clean}(\text{neg}))$$
   If this fingerprint already exists in the database, the incoming record is flagged as a duplicate, logged in `ingestion_logs.records_skipped`, and omitted.

---

## 8. Sentiment & Topic Classification Methodology

The Review Analysis Engine (`app/services/analysis_engine.py`) employs a multi-tiered rule engine built upon the `BaseClassifier` interface:

### Sentiment Classification
Reviews are classified into **Positive**, **Negative**, **Mixed**, or **Neutral**.
- The model evaluates `positive_text` and `negative_text` separately from the numerical rating.
- Reviews with high ratings but severe negative remarks are classified as **Mixed** rather than blindly marked positive.
- Negation handling inspects a 3-word window before keywords (`"not clean"`, `"wasn't noisy"`).

### 8 Operational Topics
1. **Cleanliness**: dirty, clean, dusty, stains, unhygienic, housekeeping, mold, bedsheets, towels.
2. **Check-in experience**: check-in, reception, waiting, keys, keycard, booking process, queue, front desk.
3. **Staff and receptionist behaviour**: friendly, rude, helpful, unprofessional, receptionist, polite, attitude.
4. **Noise**: noisy, loud, traffic, disturbance, soundproofing, street noise, thin walls.
5. **Facilities**: wifi, elevator, lift, air conditioning, gym, pool, kettle, television.
6. **Location**: nearby, convenient, transport, station, walking distance, bus, train, cbd.
7. **Room condition**: broken, damaged, maintenance, furniture, bathroom, bed, shower, water pressure, leak.
8. **Value for money**: expensive, overpriced, affordable, worth, money, price, costly, rip off.

### Drop-in Replacement for LLM Classifier
Because the engine uses `BaseClassifier`, replacing it with an LLM (e.g., Gemini 1.5 Flash or GPT-4o-mini) only requires implementing `LLMClassifier(BaseClassifier)` with the same `analyze(...)` signature. No API routes or database models need to change.

---

## 9. Weekly Metric Definitions (Sydney Timezone)

All weekly analytics adhere to hotel industry reporting standards:
- **Calendar Weeks**: Monday 00:00:00 to Sunday 23:59:59 in `Australia/Sydney` (AEST/AEDT).
- **Week-to-Date Comparison**: By default, the system compares the current week-to-date with the equivalent elapsed elapsed period of the previous week (e.g., Mon–Tue of this week vs Mon–Tue of last week).
- **Topic Denominators**: Clearly documented in the UI and API. Topic percentages are calculated as:
  $$\text{Topic Negative \%} = \frac{\text{Negative Reviews mentioning Topic}}{\text{Total Negative Reviews in Period}} \times 100$$
  Because a single review may mention multiple topics, topic percentages do not add up to 100%.

---

## 10. API Documentation

Comprehensive interactive documentation is generated automatically by FastAPI:
- Swagger UI: `http://localhost:8000/api/docs`
- ReDoc: `http://localhost:8000/api/redoc`
- OpenAPI Specification: `http://localhost:8000/api/openapi.json`

### Key Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Healthcheck & Sydney timestamp |
| `GET` | `/api/properties` | List all 4 properties with summary stats |
| `GET` | `/api/properties/{id}` | Single property statistics |
| `GET` | `/api/reviews` | Filtered, searchable, paginated reviews |
| `GET` | `/api/reviews/template` | Download sample CSV import template |
| `GET` | `/api/reviews/export` | Export filtered reviews to CSV |
| `POST` | `/api/reviews/import` | Upload and ingest reviews (CSV / JSON) |
| `GET` | `/api/analytics/overview` | KPI summary (WoW rating, counts, sentiments) |
| `GET` | `/api/analytics/weekly` | Historical weekly trend points |
| `GET` | `/api/analytics/properties` | Property-wise performance comparison |
| `GET` | `/api/analytics/topics` | Topic distribution across reviews |
| `GET` | `/api/analytics/operational-insights` | Actionable insights with supporting review quotes |
| `GET` | `/api/ingestion/status` | Current collection mode & permissions |
| `GET` | `/api/ingestion/history` | Audit log of previous imports |

---

## 11. Testing & Verification

The backend test suite verifies database models, deduplication, CSV/JSON parsing, sentiment classification, weekly analytics, and API contracts.

Run backend tests:
```bash
cd backend
.venv/bin/pytest -v
```

Expected output:
```
tests/test_analytics.py::test_weekly_analytics_and_insights PASSED
tests/test_api.py::test_properties_api PASSED
tests/test_api.py::test_reviews_pagination_and_filtering PASSED
tests/test_api.py::test_csv_template_download PASSED
tests/test_api.py::test_health_check_endpoint PASSED
tests/test_classification.py::test_sentiment_classification_positive PASSED
tests/test_classification.py::test_sentiment_classification_negative PASSED
tests/test_classification.py::test_sentiment_classification_mixed PASSED
tests/test_classification.py::test_all_eight_operational_topics_detection PASSED
tests/test_ingestion.py::test_csv_adapter_parsing PASSED
tests/test_ingestion.py::test_json_adapter_parsing PASSED
tests/test_ingestion.py::test_duplicate_prevention PASSED
tests/test_ingestion.py::test_invalid_rating_and_missing_property_handling PASSED
tests/test_models.py::test_property_and_review_relationships PASSED

======================== 14 passed in 0.15s =========================
```

Verify frontend production build:
```bash
cd frontend
npm run build
```

---

## 12. Known Limitations & Future Improvements

1. **Automated Scraping**: Automated browser collection remains disabled by default to respect Booking.com access boundaries and terms of service. An authorized client scraper adapter can be activated via configuration when written authorization is secured.
2. **Advanced NLP / LLM Classification**: The keyword-and-rule classifier is fast, deterministic, and requires no external API keys. Incorporating an asynchronous LLM batch classifier would enable nuanced sarcasm detection and multilingual text translation.
3. **Automated Notification Alerts**: Future releases could include automated Slack or email webhooks whenever negative complaints regarding Cleanliness or Check-in exceed 30% in a single day.
