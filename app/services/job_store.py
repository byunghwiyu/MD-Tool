import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import WORKSPACE_DIR

_JOB_STATE_FILE = WORKSPACE_DIR / "convert_jobs.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class JobStore:
    def __init__(self) -> None:
        self._path = _JOB_STATE_FILE
        self.jobs: dict[str, dict[str, Any]] = {}
        self._load()
        self._reset_interrupted()

    def _load(self) -> None:
        if self._path.exists():
            try:
                self.jobs = json.loads(self._path.read_text(encoding="utf-8-sig"))
            except Exception:
                self.jobs = {}

    def _save(self) -> None:
        self._path.write_text(
            json.dumps(self.jobs, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _reset_interrupted(self) -> None:
        changed = False
        for job in self.jobs.values():
            if job.get("status") in {"queued", "running"}:
                job.update(
                    status="failed",
                    progress=0,
                    eta_seconds=None,
                    finished_at=_utc_now(),
                    error="서버가 재시작되어 작업이 중단되었습니다. 다시 실행하세요.",
                )
                changed = True
        if changed:
            self._save()

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.jobs[payload["id"]] = payload
        self._save()
        return payload

    def update(self, job_id: str, **fields: Any) -> dict[str, Any]:
        if job_id not in self.jobs:
            raise KeyError(job_id)
        self.jobs[job_id].update(fields)
        self._save()
        return self.jobs[job_id]

    def get(self, job_id: str) -> dict[str, Any] | None:
        return self.jobs.get(job_id)

    def list(self) -> list[dict[str, Any]]:
        return sorted(self.jobs.values(), key=lambda j: j["created_at"], reverse=True)

    @staticmethod
    def utc_now() -> str:
        return _utc_now()


# 싱글턴
job_store = JobStore()
