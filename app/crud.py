from sqlalchemy.orm import Session
from app import models, schemas

def create_note(db: Session, data: schemas.NoteCreate) -> models.Note:
    note = models.Note(**data.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def get_note(db: Session, note_id: int) -> models.Note | None:
    return db.query(models.Note).filter(models.Note.id == note_id).first()

def list_notes(db: Session, skip: int = 0, limit: int = 100) -> list[models.Note]:
    return db.query(models.Note).offset(skip).limit(limit).all()

def update_note(db: Session, note_id: int, data: schemas.NoteUpdate) -> models.Note | None:
    note = get_note(db, note_id)
    if not note:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(note, key, value)
    db.commit()
    db.refresh(note)
    return note

def delete_note(db: Session, note_id: int) -> bool:
    note = get_note(db, note_id)
    if not note:
        return False
    db.delete(note)
    db.commit()
    return True
