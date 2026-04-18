from __future__ import annotations

from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from photo_dna_rs import Hash


def build_public_image_path(filename: str) -> str | None:
    stem = Path(filename).stem

    if len(stem) < 4:
        return None

    nested_path = Path("uploads") / stem[0] / stem[1] / stem[2] / stem[3] / filename
    return f"/{nested_path.as_posix()}"


def normalize_image_meta(meta: dict | None) -> dict | None:
    if not meta:
        return meta

    normalized_meta = dict(meta)
    image_path = normalized_meta.get("image_path")

    if isinstance(image_path, str) and image_path:
        normalized_meta["image_path"] = image_path if image_path.startswith("/") else f"/{image_path}"
        return normalized_meta

    filename = normalized_meta.get("filename")
    if isinstance(filename, str) and filename:
        derived_path = build_public_image_path(filename)
        if derived_path:
            normalized_meta["image_path"] = derived_path

    return normalized_meta


def compute_phash(file_path: Path | str) -> str:
    file_path = Path(file_path) if isinstance(file_path, str) else file_path

    if not file_path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")

    hash_obj = Hash.from_image_path(str(file_path))
    return hash_obj.to_hex_str()


def compute_similarity(hash_hex_a: str, hash_hex_b: str) -> float:
    """Return similarity score between 0.0 and 1.0"""
    hash_a = Hash.from_hex_str(hash_hex_a)
    hash_b = Hash.from_hex_str(hash_hex_b)
    return float(hash_a.similarity_log2p(hash_b))


def search_similar_hashes(
    db: Session,
    query_hex: str,
    limit: int = 10,
    min_similarity: float = 0.7,
) -> list[dict]:

    if not query_hex or len(query_hex) < 32:
        raise ValueError("Invalid query hash")

    query_hash = Hash.from_hex_str(query_hex)

    rows = db.execute(
        text(
            """
            SELECT
                h.uniq_id,
                h.embedding AS hash_hex,
                i.uid,
                i.metadata
            FROM hashes h
            JOIN images i ON i.uniq_id = h.uniq_id
            """
        )
    ).fetchall()

    results = []

    for row in rows:
        try:
            db_hash = Hash.from_hex_str(row.hash_hex)
            sim = float(query_hash.similarity_log2p(db_hash))

            if sim < min_similarity:
                continue

            results.append(
                {
                    "id": str(row.uniq_id),
                    "uid": str(row.uid) if row.uid else None,
                    "hash_hex": row.hash_hex,
                    "match_percentage": round(sim * 100, 2),
                    "meta": normalize_image_meta(row.metadata),
                }
            )

        except Exception as exc:
            print(f"exception raised, skipping {row.uniq_id}: {exc}")
            continue

    results.sort(key=lambda r: r["match_percentage"], reverse=True)

    return results[:limit]