import logging
import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
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


# --- Variante « une seule app » : l'API sert aussi le build React -------------
# Activé seulement si client/dist existe (build fait par le buildpack Node.js).
# Déclaré EN DERNIER : les routes de l'API (/auth, /notes, /health, /docs) restent prioritaires.
CLIENT_DIST = Path(os.environ.get("CLIENT_DIST", Path(__file__).resolve().parents[2] / "client" / "dist")).resolve()

if (CLIENT_DIST / "index.html").is_file():
    app.mount("/assets", StaticFiles(directory=CLIENT_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str) -> FileResponse:
        """Fichier statique s'il existe, sinon index.html (routage côté client, pas de 404 au rafraîchissement)."""
        candidate = (CLIENT_DIST / full_path).resolve()
        if full_path and candidate.is_file() and CLIENT_DIST in candidate.parents:
            return FileResponse(candidate)
        return FileResponse(CLIENT_DIST / "index.html")
