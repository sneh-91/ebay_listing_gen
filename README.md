# ListCraft AI

ListCraft AI is a full-stack web application for turning product photos into eBay listing drafts and, in later phases, publishing those drafts through eBay's seller APIs.

Phase 1 establishes the project shell only:

- React + TypeScript + Vite frontend
- Tailwind CSS dark landing page
- FastAPI backend
- `GET /health` endpoint
- backend CORS configuration
- starter environment examples

## Project Structure

```text
frontend/   React + TypeScript + Vite + Tailwind
backend/    FastAPI application
```

## Prerequisites

- Node.js 22+
- npm 10+
- Python 3.13+

## Frontend Setup

From [frontend/package.json](/C:/Users/snehi/projects/ebay_listing_gen/frontend/package.json):

```bash
cd frontend
npm install
npm run dev
```

The frontend runs on `http://localhost:5173`.

Copy `frontend/.env.example` to `frontend/.env` if you need to override the backend API base URL.

## Backend Setup

From [backend/requirements.txt](/C:/Users/snehi/projects/ebay_listing_gen/backend/requirements.txt):

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs on `http://localhost:8000`.

Copy `backend/.env.example` to `backend/.env` before adding any non-default configuration.

## Phase 1 Verification

1. Start the backend and open `http://localhost:8000/health`.
2. Confirm the API responds with JSON similar to:

```json
{
  "status": "ok",
  "service": "listcraft-ai-api"
}
```

3. Start the frontend and open `http://localhost:5173`.
4. Confirm the landing page shows:
   - `ListCraft AI`
   - `Turn product photos into eBay listings.`
   - `Create Listing`
   - `Connect eBay`

## Notes

- This phase does not include upload flow, OpenAI integration, eBay OAuth, or eBay listing creation.
- `EBAY_ENV` is documented as `sandbox` by default and production publishing is not enabled.
- Secrets and tokens must remain server-side in later phases.
