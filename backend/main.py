import hashlib

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import uuid
from pathlib import Path
from dotenv import load_dotenv
from DTOTypes import SearchByImageResponseDTO, SearchByHashResponseDTO, SearchResultDTO 
from ORM.db import get_db, Image, Hash, init_db
from services.hash_service import compute_phash, compute_similarity, search_similar_hashes
from validation import validate_file

load_dotenv()
# Directory to save uploaded files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PORT = int(os.getenv("BACKEND_PORT", 8000))

app = FastAPI(
    title="Lookyloo Image Matcher",
    description="Image matching and vector search API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

def save_file(image_data: bytes) -> Path:
    # Calculate SHA256 hash and use it to create a unique nested directory structure
    sha256_hash = hashlib.sha256(image_data).hexdigest()
    
    # Create nested directory: uploads/a/b/c/def.../
    dir_path = UPLOAD_DIR / sha256_hash[0]
    for c in sha256_hash[1:4]:  # Use first 4 chars for directory depth
        dir_path = dir_path / c
    dir_path.mkdir(parents=True, exist_ok=True)
    
    # Full file path: uploads/a/b/c/def.../hash.jpg
    file_path = dir_path / f"{sha256_hash}.jpg"
    
    # Save the file to disk if it doesn't exist
    if not file_path.exists():
        try:
            with file_path.open("wb") as buffer:
                buffer.write(image_data)
            print(f"[DEBUG] Saved file: {file_path} ({len(image_data)} bytes)")
        except Exception as e:
            print(f"[ERROR] Failed to save file: {e}")
            raise
    else:
        print(f"[DEBUG] File already exists: {file_path}")
    
    # Verify file exists and is readable
    if not file_path.exists():
        raise FileNotFoundError(f"File was not saved properly: {file_path}")
    
    file_size = file_path.stat().st_size
    print(f"[DEBUG] File verified: {file_path} ({file_size} bytes)")
    
    return file_path

def add_file_to_db(file_path: Path, uid: uuid.UUID = None) -> uuid.UUID:
    """
    Save image file record to database.
    
    Args:
        file_path: Path to the saved image file
        uid: Optional user ID
        
    Returns:
        Unique ID of the image record in the database
    """
    db = get_db()
    
    try:
        # Create image record
        image_record = Image(
            uid=uid or uuid.uuid4(),
            metadata_={"filename": file_path.name},
        )
        db.add(image_record)
        db.flush()
        db.commit()
        return image_record.uniq_id
    except Exception as e:
        db.rollback()
        raise Exception(f"Error saving file to database: {str(e)}")


def add_hash_to_db(image_uniq_id: uuid.UUID, hash_hex: str):
    """
    Save PhotoDNA hash to database.
    
    Args:
        image_uniq_id: ID of the image record
        hash_hex: PhotoDNA hash hex string
    """
    db = get_db()
    
    try:
        # Create hash record with embedding = hash hex string
        hash_record = Hash(
            uniq_id=image_uniq_id,
            embedding=hash_hex  # Store hash hex in embedding column
        )
        db.add(hash_record)
        db.commit()
        print(f"[DEBUG] Hash stored: {hash_hex[:16]}...")
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Failed to save hash: {e}")
        raise Exception(f"Error saving hash to database: {str(e)}")

@app.post("/get_hash")
async def get_hash(file: UploadFile = File(...)):
    """
    Endpoint to receive an image, compute its PhotoDNA hash,
    save the image and hash to the database.
    """
    try:
        # Read image data and save to disk
        image_data = await file.read()
        
        if not image_data:
            return {"error": "Image file is empty"}
        
        # Save file to disk
        file_path = save_file(image_data)
        
        # Compute PhotoDNA hash from file path
        hash_hex = compute_phash(file_path)
        
        # Save to database
        image_id = add_file_to_db(file_path)
        add_hash_to_db(image_id, hash_hex)

        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "hash": hash_hex,
            "file_path": str(file_path),
            "image_id": str(image_id)
        }
    except Exception as e:
        return {"error": str(e)}


# Search by image endpoint


@app.post("/search/by-image", response_model=SearchByImageResponseDTO)
async def search_by_image(
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    print("WTHURHUWh")
    try:
        print("-1")
        # Validate file type, Throw HTTPException if validation fails   
        await validate_file(image)
        print("0")
        
        # Read image file
        image_data = await image.read()
        
        if not image_data:
            raise HTTPException(status_code=400, detail="Image file is empty")
        

        print("1")
        # Save to temp file first (needed for PhotoDNA library)
        file_path = save_file(image_data)
        print("2")
        
        # Compute PhotoDNA hash from file path
        hash_hex = compute_phash(file_path)
        print("3")

        # Search database for similar images
        results = search_similar_hashes(db, hash_hex, limit=10)
        print("4")
        
        return SearchByImageResponseDTO(
            calculated_hash=hash_hex,
            total_matches=len(results),
            results=[SearchResultDTO(**r) for r in results]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error processing image: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)

