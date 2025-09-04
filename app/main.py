from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.wsgi import WSGIMiddleware

from app.api.ingest import router as ingest_router
from app.api.insights import router as insights_router
from app.ui.dashboard import build_dash_app

app = FastAPI(title="Metabolic BioTwin")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(ingest_router, prefix="/api", tags=["ingest"])
app.include_router(insights_router, prefix="/api", tags=["insights"])

# Mount static files for demo data
app.mount("/data", StaticFiles(directory="app/data"), name="data")

# Mount Dash app at /app
dash_app = build_dash_app()
app.mount("/app", WSGIMiddleware(dash_app.server))

# Redirect root to dashboard
@app.get("/")
async def root():
    return RedirectResponse(url="/app/")
