# SmartCloud Optimizer

SmartCloud Optimizer is a FinOps and cloud optimization MVP designed for a mid-sized SaaS company operating across India. It combines:

- public Azure VM pricing benchmark data from the Microsoft Azure Retail Prices API
- synthetic cloud resource inventory and 30-day time-series workload simulation
- intelligent downsizing, upsizing, and orphan cleanup recommendations
- CRON-based schedule simulation with emergency override logic
- a sleek React + Tailwind dashboard for infra and FinOps teams

## Tech stack

- Backend: Python, FastAPI, Pandas/NumPy, Pydantic
- Frontend: React + Vite + Tailwind CSS + Recharts + Lucide icons

## What this app does

- Simulates cloud resources across Noida, Bangalore, and Mumbai
- Tracks VM CPU, memory, and IOPS over 30 days
- Detects underutilized VMs and over-provisioned workloads
- Recommends performance-safe downsize vs reliability-driven upsize
- Flags orphaned block volumes and public IPs for termination
- Simulates CRON downscale windows with emergency spike override triggers
- Displays a FinOps dashboard for executive and operational review

## Data source note

This project intentionally uses:
- Azure Retail Prices API for public pricing benchmark data
- synthetic workload traces for the resource simulation

It does not claim to use live customer subscription telemetry, because that is not publicly available.

## Run locally

### 1) Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Then open:
- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs

## Repository structure

```text
backend/
  app/
    main.py
  requirements.txt
frontend/
  index.html
  package.json
  vite.config.js
  src/
    App.jsx
    main.jsx
    index.css
```

## Important note for hackathon use

This MVP is designed for a realistic FinOps demo and is built to be transparent about the public benchmark data source. It is a strong demonstration project for cloud cost optimization without making claims about private tenant telemetry.
