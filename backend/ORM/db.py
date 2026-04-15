from sqlalchemy import create_engine, ForeignKey, DateTime, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import os


db_info = {
    "user": "postgres",
    "password": os.getenv("DB_PASSWORD", "password"),
    "port": os.getenv("DB_PORT", "5432"),
    "db_name": "mydb"
}
# Using localhost because the backend runs locally, while postgres is in a container.
database_url = f"postgresql://{db_info['user']}:{db_info['password']}@localhost:{db_info['port']}/{db_info['db_name']}"
engine = create_engine(database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Image(Base):
    __tablename__ = "images"

    uniq_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()")  # calls uuid-ossp's uuidv4()
    )
    uid: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False)
    analysis_timestamp: Mapped[datetime] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )

    hash: Mapped["Hash"] = relationship("Hash", back_populates="image", uselist=False)


class Hash(Base):
    __tablename__ = "hashes"

    uniq_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("images.uniq_id"),
        primary_key=True
    )
    embedding: Mapped[str] = mapped_column(nullable=False)

    image: Mapped["Image"] = relationship("Image", back_populates="hash")



def init_db():
    try:
        with engine.connect() as conn:
            conn.execute(text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))
            conn.commit()
    except Exception as e:
        print(f"Error creating extensions: {e}")
    
    Base.metadata.create_all(bind=engine)

db = SessionLocal()
def get_db():
    return db