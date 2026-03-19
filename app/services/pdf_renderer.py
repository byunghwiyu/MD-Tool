import asyncio
import concurrent.futures
from pathlib import Path
from playwright.async_api import async_playwright


async def _render_pdf_async(html_path: Path, output_path: Path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(html_path.as_uri(), wait_until="networkidle", timeout=15000)
        await page.pdf(
            path=str(output_path),
            format="A4",
            margin={"top": "20mm", "bottom": "20mm", "left": "18mm", "right": "18mm"},
            print_background=True,
        )
        await browser.close()


def render_pdf(html_path: Path, output_path: Path) -> Path:
    html_path  = html_path.resolve()
    output_path = output_path.resolve()
    try:
        asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(asyncio.run, _render_pdf_async(html_path, output_path)).result()
    except RuntimeError:
        asyncio.run(_render_pdf_async(html_path, output_path))
    return output_path
