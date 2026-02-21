from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Integer, String, select
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, Session
from typing import Generator, Literal
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)


class ItemCreate(BaseModel):
    name: str
    status: Literal["Pendiente", "En progreso", "Completado"]


class ItemUpdate(BaseModel):
    name: str | None = None
    status: Literal["Pendiente", "En progreso", "Completado"] | None = None


class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: str


def build_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("mysql://"):
            return database_url.replace("mysql://", "mysql+pymysql://", 1)
        return database_url

    def require_env(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value

    db_user = require_env("DB_USER")
    db_password = require_env("DB_PASSWORD")
    db_host = require_env("DB_HOST")
    db_port = require_env("DB_PORT")
    db_name = require_env("DB_NAME")
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


engine = create_engine(build_database_url(), pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_data(db: Session) -> None:
    existing = db.execute(select(Item)).scalars().first()
    if existing:
        return
    db.add_all(
        [
            Item(name="Módulo CI/CD", status="Completado"),
            Item(name="Módulo Docker", status="En progreso"),
            Item(name="Módulo Despliegue", status="Pendiente"),
        ]
    )
    db.commit()


def connect_database() -> None:
    max_retries = 10
    retry_interval = 5

    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Intento {attempt}/{max_retries}: Conectando a la base de datos...")
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as session:
                session.execute(select(1))
                seed_data(session)
            logger.info("Conexión a la base de datos exitosa")
            break
        except Exception as e:
            logger.warning(f"Error al conectar (intento {attempt}/{max_retries}): {e}")
            if attempt == max_retries:
                logger.error("No se pudo conectar a la base de datos después de múltiples intentos")
                raise
            logger.info(f"Reintentando en {retry_interval} segundos...")
            time.sleep(retry_interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_database()
    yield


app = FastAPI(
    title="API de Demostración Didáctica",
    description="Backend con FastAPI para la práctica de CI/CD",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "El Backend está funcionando correctamente.",
        "docs": "/docs"
    }

@app.get("/api/data")
async def get_data(db: Session = Depends(get_db)):
    items = db.execute(select(Item)).scalars().all()
    return {
        "items": [ItemOut.model_validate(item).model_dump() for item in items],
        "backend_engine": "FastAPI + MySQL"
    }


@app.get("/api/items", response_model=list[ItemOut])
async def list_items(db: Session = Depends(get_db)):
    items = db.execute(select(Item)).scalars().all()
    return [ItemOut.model_validate(item) for item in items]


@app.post("/api/items", response_model=ItemOut, status_code=201)
async def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = Item(name=payload.name, status=payload.status)
    db.add(item)
    db.commit()
    db.refresh(item)
    return ItemOut.model_validate(item)


@app.put("/api/items/{item_id}", response_model=ItemOut)
async def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    if payload.name is not None:
        item.name = payload.name
    if payload.status is not None:
        item.status = payload.status
    db.commit()
    db.refresh(item)
    return ItemOut.model_validate(item)


@app.delete("/api/items/{item_id}", status_code=204)
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
