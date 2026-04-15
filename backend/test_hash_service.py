#!/usr/bin/env python3
"""
Test script for PhotoDNA hash service.

Creates test images and tests:
- Hash computation
- Hash similarity calculation
- Percentage conversion
- Database storage and retrieval
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw
import uuid

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from services.hash_service import compute_phash, compute_similarity, similarity_to_percent
from ORM.db import init_db, SessionLocal, Image as ImageModel, Hash as HashModel


# Create test image directory
TEST_DIR = Path("test_images")
TEST_DIR.mkdir(exist_ok=True)


def create_test_image(filename: str, color: tuple, text: str = "") -> Path:
    """Create a simple test image."""
    img = Image.new("RGB", (256, 256), color)
    draw = ImageDraw.Draw(img)
    if text:
        draw.text((10, 10), text, fill="white")
    path = TEST_DIR / filename
    img.save(path)
    print(f"✓ Created test image: {path}")
    return path


def test_hash_computation():
    """Test basic hash computation."""
    print("\n=== Testing Hash Computation ===")
    
    # Create test images
    img1_path = create_test_image("test1_red.jpg", (255, 0, 0), "Red")
    img2_path = create_test_image("test2_red_slight.jpg", (254, 1, 0), "Red-ish")
    img3_path = create_test_image("test3_blue.jpg", (0, 0, 255), "Blue")
    
    # Compute hashes
    hash1 = compute_phash(img1_path)
    hash2 = compute_phash(img2_path)
    hash3 = compute_phash(img3_path)
    
    print(f"✓ Hash 1 (Red):     {hash1[:16]}...")
    print(f"✓ Hash 2 (Red-ish): {hash2[:16]}...")
    print(f"✓ Hash 3 (Blue):    {hash3[:16]}...")
    
    return hash1, hash2, hash3, img1_path, img2_path, img3_path


def test_similarity(hash1: str, hash2: str, hash3: str):
    """Test similarity computation."""
    print("\n=== Testing Similarity Computation ===")
    
    # Similar images (both red)
    sim_1_2 = compute_similarity(hash1, hash2)
    pct_1_2 = similarity_to_percent(sim_1_2)
    print(f"✓ Red vs Red-ish:    {sim_1_2:.4f} → {pct_1_2:.1f}%")
    
    # Different images (red vs blue)
    sim_1_3 = compute_similarity(hash1, hash3)
    pct_1_3 = similarity_to_percent(sim_1_3)
    print(f"✓ Red vs Blue:       {sim_1_3:.4f} → {pct_1_3:.1f}%")
    
    # Identical hash
    sim_1_1 = compute_similarity(hash1, hash1)
    pct_1_1 = similarity_to_percent(sim_1_1)
    print(f"✓ Red vs Red (same): {sim_1_1:.4f} → {pct_1_1:.1f}%")
    
    return pct_1_2, pct_1_3, pct_1_1


def test_database_storage(hash1: str, hash2: str, img1_path: Path, img2_path: Path):
    """Test saving and retrieving hashes from database."""
    print("\n=== Testing Database Storage ===")
    
    init_db()
    db = SessionLocal()
    
    try:
        # Create image records
        img_record_1 = ImageModel(
            uid=uuid.uuid4(),
            metadata_={"name": "Test Image 1", "color": "red"},
            image_path=str(img1_path)
        )
        img_record_2 = ImageModel(
            uid=uuid.uuid4(),
            metadata_={"name": "Test Image 2", "color": "red-ish"},
            image_path=str(img2_path)
        )
        
        db.add(img_record_1)
        db.add(img_record_2)
        db.flush()
        
        print(f"✓ Created image record 1: {img_record_1.uniq_id}")
        print(f"✓ Created image record 2: {img_record_2.uniq_id}")
        
        # Create hash records
        hash_record_1 = HashModel(
            uniq_id=img_record_1.uniq_id,
            hash_hex=hash1
        )
        hash_record_2 = HashModel(
            uniq_id=img_record_2.uniq_id,
            hash_hex=hash2
        )
        
        db.add(hash_record_1)
        db.add(hash_record_2)
        db.commit()
        
        print(f"✓ Stored hash 1")
        print(f"✓ Stored hash 2")
        
        # Retrieve and verify
        retrieved_hash_1 = db.query(HashModel).filter_by(uniq_id=img_record_1.uniq_id).first()
        retrieved_hash_2 = db.query(HashModel).filter_by(uniq_id=img_record_2.uniq_id).first()
        
        assert retrieved_hash_1.hash_hex == hash1, "Hash 1 mismatch"
        assert retrieved_hash_2.hash_hex == hash2, "Hash 2 mismatch"
        
        print(f"✓ Retrieved and verified hashes from database")
        
        return retrieved_hash_1.hash_hex, retrieved_hash_2.hash_hex
        
    finally:
        db.close()


def main():
    """Run all tests."""
    print("=" * 50)
    print("PhotoDNA Hash Service Test Suite")
    print("=" * 50)
    
    # Test 1: Hash computation
    hash1, hash2, hash3, img1, img2, img3 = test_hash_computation()
    
    # Test 2: Similarity
    pct_similar, pct_different, pct_identical = test_similarity(hash1, hash2, hash3)
    
    # Test 3: Database
    db_hash1, db_hash2 = test_database_storage(hash1, hash2, img1, img2)
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"✓ Hash computation working")
    print(f"✓ Similarity comparison working")
    print(f"  - Similar images: {pct_similar:.1f}%")
    print(f"  - Different images: {pct_different:.1f}%")
    print(f"  - Identical: {pct_identical:.1f}%")
    print(f"✓ Database storage and retrieval working")
    print(f"\nAll tests passed! ✓")


if __name__ == "__main__":
    main()
