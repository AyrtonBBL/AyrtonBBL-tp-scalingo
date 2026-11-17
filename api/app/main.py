import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.routers import auth, notes

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
log = logging.getLogger("api")

# Pas de create_all ici : le schéma est géré par Alembic (process postdeploy).
app = FastAPI(title="Notes API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_list,  # uniquement l'URL du client, jamais "*"
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(notes.router)


@app.get("/health", tags=["ops"])
def health(db: Session = Depends(get_db)) -> JSONResponse:
    """Health check : 200 si l'API répond ET que la base est joignable, sinon 503."""
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        log.exception("Health check : base injoignable")
        return JSONResponse({"status": "error", "database": "down"}, status_code=503)
    return JSONResponse({"status": "ok", "database": "up"})
