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
    sha256: Mapped[str | None] = mapped_column(nullable=True)
    meta_information: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
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
    try:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE images ADD COLUMN IF NOT EXISTS sha256 VARCHAR(64)"))
            conn.execute(text("ALTER TABLE images ADD COLUMN IF NOT EXISTS meta_information JSONB"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_images_sha256 ON images(sha256)"))
            conn.execute(
                text(
                    """
                    UPDATE images
                    SET sha256 = split_part(metadata->>'filename', '.', 1)
                    WHERE (sha256 IS NULL OR sha256 = '')
                      AND metadata ? 'filename'
                    """
                )
            )
            conn.execute(
                text(
                    """
                    UPDATE images
                    SET meta_information = metadata
                    WHERE meta_information IS NULL
                    """
                )
            )
            conn.execute(
                text(
                    """
                    UPDATE images
                    SET metadata = COALESCE(metadata, '{}'::jsonb)
                        || jsonb_build_object(
                            'capture_date',
                            to_char(analysis_timestamp, 'YYYY-MM-DD HH24:MI:SS')
                        )
                    WHERE COALESCE(metadata->>'capture_date', '') = ''
                    """
                )
            )
            conn.execute(
                text(
                    """
                    UPDATE images
                    SET meta_information = COALESCE(meta_information, '{}'::jsonb)
                        || jsonb_build_object(
                            'capture_date',
                            to_char(analysis_timestamp, 'YYYY-MM-DD HH24:MI:SS')
                        )
                    WHERE COALESCE(meta_information->>'capture_date', '') = ''
                    """
                )
            )
            conn.commit()
    except Exception as e:
        print(f"Error applying sha256 migration: {e}")

db = SessionLocal()
def get_db():
    return db