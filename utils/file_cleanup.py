import os
import time
from config.db import db
from models.material import Material  # assuming a Material model exists

# Configuration (could be moved to config)
MAX_AGE_SECONDS = 30 * 24 * 60 * 60  # 30 days

def cleanup_orphaned_uploads():
    """Delete files in the uploads directory that are older than MAX_AGE_SECONDS
    and have no corresponding Material DB record.
    """
    base_dir = os.path.join(os.getcwd(), 'uploads')
    now = time.time()
    for root, _, files in os.walk(base_dir):
        for f in files:
            file_path = os.path.join(root, f)
            # Age check
            if now - os.path.getmtime(file_path) > MAX_AGE_SECONDS:
                # Verify DB record
                rel_path = os.path.relpath(file_path, base_dir)
                material = Material.query.filter_by(path=rel_path).first()
                if not material:
                    try:
                        os.remove(file_path)
                        print(f'Removed orphaned file: {file_path}')
                    except OSError as e:
                        print(f'Failed to remove {file_path}: {e}')
