"""Données initiales, à lancer UNE fois après le premier déploiement :

    scalingo --app <app-api> run python seed.py

Le mot de passe du compte démo vient de l'environnement (SEED_PASSWORD), jamais du code.
"""

import os
import sys

from sqlalchemy import select

from app.db import SessionLocal
from app.models import Note, User
from app.security import hash_password

EMAIL = os.environ.get("SEED_EMAIL", "demo@example.com")
PASSWORD = os.environ.get("SEED_PASSWORD")


def main() -> None:
    if not PASSWORD or len(PASSWORD) < 8:
        sys.exit("Définissez SEED_PASSWORD (8 caractères minimum).")
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == EMAIL)):
            print(f"{EMAIL} existe déjà, rien à faire.")
            return
        user = User(email=EMAIL, password_hash=hash_password(PASSWORD))
        user.notes = [
            Note(title="Bienvenue 👋", content="Cette note vient du script seed.py."),
            Note(title="Déployé sur Scalingo", content="Client React + API FastAPI + PostgreSQL."),
        ]
        db.add(user)
        db.commit()
        print(f"Compte démo créé : {EMAIL}")


if __name__ == "__main__":
    main()
