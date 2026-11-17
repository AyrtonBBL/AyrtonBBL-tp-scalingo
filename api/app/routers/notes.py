from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Note, User
from app.schemas import NoteIn, NoteOut
from app.security import current_user

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteOut])
def list_notes(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[Note]:
    return list(db.scalars(select(Note).where(Note.owner_id == user.id).order_by(Note.id.desc())))


@router.post("", response_model=NoteOut, status_code=status.HTTP_201_CREATED)
def create_note(body: NoteIn, user: User = Depends(current_user), db: Session = Depends(get_db)) -> Note:
    note = Note(owner_id=user.id, **body.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)) -> None:
    note = db.get(Note, note_id)
    if note is None or note.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Note introuvable")
    db.delete(note)
    db.commit()
