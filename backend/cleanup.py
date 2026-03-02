"""
Background cleanup task:
  - Every 24 h: delete orphaned upload files not referenced by any DB record
  - Every 24 h: compress static images (JPG/PNG/WEBP) whose updated_at is
    older than 30 days and have not been compressed yet
"""
import asyncio
import io
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


async def cleanup_loop():
    """Launched at startup; waits 1 h before the first run, then repeats daily."""
    await asyncio.sleep(3600)
    while True:
        try:
            await asyncio.to_thread(_run_cleanup)
        except Exception as exc:
            logger.error("Cleanup task failed: %s", exc)
        await asyncio.sleep(86400)


# ── Sync implementation (runs in thread pool) ─────────────────────────────────

def _run_cleanup():
    from database import db
    from config import UPLOAD_DIR

    with db() as conn:
        _delete_orphans(conn, UPLOAD_DIR)
        _compress_old(conn, UPLOAD_DIR)


def _delete_orphans(conn, upload_dir: Path):
    rows = conn.execute("SELECT original_path, processed_path FROM images").fetchall()
    referenced = set()
    for r in rows:
        if r["original_path"]:  referenced.add(r["original_path"])
        if r["processed_path"]: referenced.add(r["processed_path"])

    deleted = 0
    for f in upload_dir.iterdir():
        if f.is_file() and f.name not in referenced:
            try:
                f.unlink()
                deleted += 1
            except Exception as exc:
                logger.warning("Could not delete orphan %s: %s", f, exc)

    if deleted:
        logger.info("Cleanup: removed %d orphaned file(s)", deleted)


def _compress_old(conn, upload_dir: Path):
    threshold = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    rows = conn.execute(
        "SELECT id, original_path, processed_path FROM images "
        "WHERE is_compressed = 0 AND updated_at < ?",
        (threshold,),
    ).fetchall()

    compressed_count = 0
    for row in rows:
        changed = False
        for path_str in (row["original_path"], row["processed_path"]):
            if path_str and _compress_file(upload_dir / path_str):
                changed = True
        if changed:
            conn.execute("UPDATE images SET is_compressed = 1 WHERE id = ?", (row["id"],))
            compressed_count += 1

    if compressed_count:
        logger.info("Cleanup: compressed %d image record(s)", compressed_count)


def _compress_file(path: Path) -> bool:
    """Recompress a static image in-place. Returns True if the file was overwritten."""
    if not path.exists():
        return False

    ext = path.suffix.lower()
    if ext == ".gif":
        return False  # Animated GIF — never touch it

    try:
        from PIL import Image

        original_size = path.stat().st_size
        if original_size < 150 * 1024:   # Skip files already under 150 KB
            return False

        with Image.open(path) as img:
            buf = io.BytesIO()
            if ext in (".jpg", ".jpeg"):
                rgb = img.convert("RGB") if img.mode in ("RGBA", "P", "LA") else img
                rgb.save(buf, format="JPEG", quality=82, optimize=True)
            elif ext == ".png":
                img.save(buf, format="PNG", optimize=True, compress_level=9)
            elif ext == ".webp":
                img.save(buf, format="WEBP", quality=82, method=6)
            else:
                return False

        compressed = buf.getvalue()
        if len(compressed) < original_size:
            path.write_bytes(compressed)
            logger.debug("Compressed %s  %d → %d bytes", path.name, original_size, len(compressed))
            return True

    except Exception as exc:
        logger.warning("Failed to compress %s: %s", path, exc)

    return False
