# ListCraft AI

ListCraft AI is a full-stack app that turns product photos into editable eBay listing drafts, lets a seller connect their own eBay account with OAuth, validates sandbox setup, and publishes listings through the eBay Sell Inventory API.

## Stack

- `frontend/`: React, TypeScript, Vite, Tailwind
- `backend/`: FastAPI

## Planned End-to-End Flow

1. Upload up to 3 product images and optional seller notes.
2. Generate a structured listing draft with OpenAI on the backend.
3. Review and edit title, condition, description, specifics, and pricing.
4. Connect an eBay Sandbox seller account through server-side OAuth.
5. Validate marketplace, policies, inventory location, category support, and image strategy.
6. Create and publish the listing to eBay Sandbox.

## Requirements

- Node.js 22+
- npm 10+
- Python 3.13+

## Local Development

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Default local URLs:

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Health check: `GET /health`

## Environment

Backend configuration lives in `backend/.env`.

Key variables:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `DATABASE_URL`
- `EBAY_CLIENT_ID`
- `EBAY_CLIENT_SECRET`
- `EBAY_REDIRECT_URI`
- `EBAY_ENV` with `sandbox` as the default
- `EBAY_MARKETPLACE_ID`
- `FRONTEND_URL`
- `SECRET_KEY`

## Constraints

- OpenAI keys, eBay client credentials, access tokens, and refresh tokens stay server-side.
- eBay Sandbox is the default environment.
- Production publishing is not enabled by default.