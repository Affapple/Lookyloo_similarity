from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import text
from photo_dna_rs import Hash as PhotoDNAHash

MAX_DISTANCE = 100.0 

def compute_phash(file_path: Path | str) -> str:

    file_path = Path(file_path) if isinstance(file_path, str) else file_path
    
    if not file_path.exists():
        raise FileNotFoundError(f"Image file not found: {file_path}")
    
    try:
        print(f"Computing hash for: {file_path} (size: {file_path.stat().st_size} bytes)")
        hash_obj = PhotoDNAHash.from_image_path(str(file_path))
        hash_hex = hash_obj.to_hex_str() 
        print(f"Hash computed successfully: {hash_hex[:16]}...")
        return hash_hex
    except Exception as e:
        print(f"Failed to compute hash for {file_path}: {e}")
        raise Exception(f"Failed to compute PhotoDNA hash: {str(e)}")


def compute_similarity(hash_hex_a: str, hash_hex_b: str) -> float:
    """Return similarity score between 0.0 and 1.0"""
    try:
        hash_a = PhotoDNAHash.from_hex_str(hash_hex_a)
        hash_b = PhotoDNAHash.from_hex_str(hash_hex_b)

        similarity = float(hash_a.similarity_log2p(hash_b))

        if similarity < 0:
            similarity = 0.0
        elif similarity > 1:
            similarity = 1.0

        return similarity

    except Exception as e:
        raise ValueError("Invalid hash comparison") from e


def similarity_to_percent(similarity: float) -> float:
    """Convert normalized similarity (0–1) to percentage"""
    return round(similarity * 100, 2)


def search_similar_hashes(
    db: Session,
    query_hex: str,
    limit: int = 10,
    min_similarity: float = 0.7,  
) -> list[dict]:

    if not query_hex or len(query_hex) < 32:
        raise ValueError("Invalid query hash")

    rows = db.execute(
        text(
            """
            SELECT
                h.uniq_id,
                h.hash_hex,
                i.uid,
                i.metadata_
            FROM hashes h
            JOIN images i ON i.uniq_id = h.uniq_id
            """
        )
    ).fetchall()

    results = []

    for row in rows:
        try:
            sim = compute_similarity(query_hex, row.hash_hex)

            # FILTER LOW MATCHES
            if sim < min_similarity:
                continue

            results.append(
                {
                    "id": str(row.uniq_id),
                    "uid": str(row.uid) if row.uid else None,
                    "hash_hex": row.hash_hex,
                    "match_percentage": similarity_to_percent(sim),
                    "meta": row.metadata_,
                }
            )

        except Exception as exc:
            print(f"exception raised, skipping {row.uniq_id}: {exc}")
            continue

    results.sort(key=lambda r: r["match_percentage"], reverse=True)

    return results[:limit]