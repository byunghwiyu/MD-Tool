import json
from fastapi import APIRouter, HTTPException
from app.config import OUTPUTS_DIR

router = APIRouter()


def _build_job_meta(job_dir) -> dict:
    meta_file = job_dir / "metadata.json"
    if not meta_file.exists():
        return None
    meta = json.loads(meta_file.read_text(encoding="utf-8"))
    job_type = meta.get("type", "export")
    stem = meta.get("stem", "preview")
    meta["preview_url"] = f"/outputs/{job_dir.name}/{stem}.html" if job_type == "export" else None
    meta["pdf_url"] = (
        f"/outputs/{job_dir.name}/{stem}.pdf"
        if job_type == "export" and (job_dir / f"{stem}.pdf").exists()
        else None
    )
    return meta


@router.get("/jobs")
def list_jobs():
    jobs = []
    if OUTPUTS_DIR.exists():
        for job_dir in sorted(OUTPUTS_DIR.iterdir(), reverse=True):
            meta = _build_job_meta(job_dir)
            if meta:
                jobs.append(meta)
    return jobs


@router.get("/jobs/{job_id}")
def get_job(job_id: str):
    job_dir = OUTPUTS_DIR / job_id
    meta = _build_job_meta(job_dir)
    if not meta:
        raise HTTPException(status_code=404, detail="작업을 찾을 수 없습니다.")
    return meta
