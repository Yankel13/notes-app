import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import crud, metrics, schemas
from app.cache import get_cached_note, invalidate_note, set_cached_note
from app.config import settings
from app.database import Base, engine, get_db

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(settings.app_name)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Application started")
    yield
    logger.info("Application stopped")


app = FastAPI(title=settings.app_name, lifespan=lifespan)
Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health():
    return {"status": "ok", "env": settings.app_env}


@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        from app.cache import redis_client

        redis_client.ping()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Not ready: {e}")


@app.post("/notes", response_model=schemas.NoteRead, status_code=201)
def create_note(payload: schemas.NoteCreate, db: Session = Depends(get_db)):
    note = crud.create_note(db, payload)
    metrics.notes_created_total.inc()
    logger.info(f"Note created: id={note.id}")
    return note


@app.get("/notes", response_model=list[schemas.NoteRead])
def list_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.list_notes(db, skip, limit)


@app.get("/notes/{note_id}", response_model=schemas.NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)):
    cached = get_cached_note(note_id)
    if cached:
        metrics.cache_hits_total.inc()
        return cached
    metrics.cache_misses_total.inc()
    note = crud.get_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    data = schemas.NoteRead.model_validate(note).model_dump()
    set_cached_note(note_id, data)
    return note


@app.patch("/notes/{note_id}", response_model=schemas.NoteRead)
def update_note(
    note_id: int, payload: schemas.NoteUpdate, db: Session = Depends(get_db)
):
    note = crud.update_note(db, note_id, payload)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    invalidate_note(note_id)
    return note


@app.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    if not crud.delete_note(db, note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    invalidate_note(note_id)
    metrics.notes_deleted_total.inc()
