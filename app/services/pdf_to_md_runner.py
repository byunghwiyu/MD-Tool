import asyncio
import time
from pathlib import Path

from app.config import MARKER_PATH
from app.services.job_store import job_store


def estimate_duration(file_size: int) -> int:
    size_mb = file_size / (1024 * 1024)
    return max(20, min(int(18 + size_mb * 22), 420))


def compute_progress(elapsed: float, estimated: int, status: str) -> int:
    if status == "queued":  return 5
    if status == "done":    return 100
    if status == "failed":  return 0
    if estimated <= 0:      return 15
    ratio = min(elapsed / estimated, 0.95)
    return max(12, int(12 + ratio * 83))


async def run_marker(
    job_id: str,
    input_path: Path,
    output_dir: Path,
    output_format: str,
    page_range: str | None,
    force_ocr: bool,
) -> None:
    job = job_store.get(job_id)
    if not job:
        return

    if not MARKER_PATH.exists():
        job_store.update(
            job_id,
            status="failed", progress=0, eta_seconds=None,
            finished_at=job_store.utc_now(),
            error=f"marker_single.exe를 찾을 수 없습니다: {MARKER_PATH}",
        )
        return

    cmd = [str(MARKER_PATH), str(input_path), "--output_dir", str(output_dir), "--output_format", output_format]
    if page_range:
        cmd.extend(["--page_range", page_range])
    if force_ocr:
        cmd.append("--force_ocr")

    estimated = int(job.get("estimated_seconds") or estimate_duration(job.get("file_size", 0)))
    start = time.monotonic()

    job_store.update(
        job_id,
        status="running", command=cmd,
        started_at=job_store.utc_now(),
        progress=12, estimated_seconds=estimated, eta_seconds=estimated,
    )

    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    log_lines: list[str] = []
    assert process.stdout is not None

    while True:
        try:
            line = await asyncio.wait_for(process.stdout.readline(), timeout=1.0)
        except asyncio.TimeoutError:
            line = None

        elapsed = time.monotonic() - start
        progress = compute_progress(elapsed, estimated, "running")

        if line:
            log_lines.append(line.decode("utf-8", errors="replace").rstrip())

        job_store.update(
            job_id,
            log="\n".join(log_lines[-250:]),
            elapsed_seconds=int(elapsed),
            eta_seconds=max(0, estimated - int(elapsed)),
            progress=progress,
        )

        if line == b"":
            break

    return_code = await process.wait()
    elapsed = int(time.monotonic() - start)

    if return_code != 0:
        job_store.update(
            job_id,
            status="failed", progress=0,
            elapsed_seconds=elapsed, eta_seconds=None,
            finished_at=job_store.utc_now(),
            error=f"marker 종료 코드: {return_code}",
            log="\n".join(log_lines[-250:]),
        )
        return

    # 결과 파일 수집
    files = []
    for path in sorted(output_dir.rglob("*")):
        if path.is_file():
            files.append({
                "name": path.name,
                "relative_path": str(path.relative_to(output_dir)).replace("\\", "/"),
                "size": path.stat().st_size,
            })

    # 프리뷰 (첫 번째 md/html 파일)
    preview, preview_type = "", "text"
    preview_file = next((f for f in files if f["name"].lower().endswith((".md", ".html"))), None)
    if preview_file:
        p = output_dir / preview_file["relative_path"]
        preview = p.read_text(encoding="utf-8", errors="replace")
        preview_type = "markdown" if preview_file["name"].endswith(".md") else "html"

    job_store.update(
        job_id,
        status="done",
        finished_at=job_store.utc_now(),
        files=files,
        preview=preview[:200_000],
        preview_type=preview_type,
        log="\n".join(log_lines[-250:]),
        progress=100,
        elapsed_seconds=elapsed,
        eta_seconds=0,
    )
