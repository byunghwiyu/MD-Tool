from app.services.markdown_renderer import render_markdown
from app.services.template_loader import build_html
from app.services.result_writer import save_export_output, make_stem
from app.services.pdf_renderer import render_pdf


def run_export_job(
    job_id: str,
    md_text: str,
    template_name: str,
    source_filename: str,
    translation_options: dict | None = None,
) -> dict:
    """
    MD Export 파이프라인

    스텝:
      1. [addon] 번역 (translation_options 있을 때만)
      2. Markdown → HTML
      3. 템플릿 적용
      4. 저장
      5. PDF 렌더링
    """
    translated_md = None
    content_md = md_text

    # 스텝 1: 번역 (addon — 현재 비활성)
    if translation_options:
        # TODO: from app.services.translators import translate
        # content_md = translate(md_text, translation_options)
        # translated_md = content_md
        pass

    # 스텝 2-3: MD → HTML + 템플릿
    title = source_filename.removesuffix(".md") if source_filename else "Document"
    html = build_html(render_markdown(content_md), template_name, title=title)

    # 스텝 4: 저장
    stem = make_stem(source_filename or "document")
    job_dir = save_export_output(
        job_id, md_text, html,
        {"template": template_name, "source_filename": source_filename, "translation": translation_options},
        translated_md,
    )
    dir_name = job_dir.name  # "{stem}_{job_id}"

    # 스텝 5: PDF
    pdf_url = None
    try:
        render_pdf(job_dir / f"{stem}.html", job_dir / f"{stem}.pdf")
        pdf_url = f"/outputs/{dir_name}/{stem}.pdf"
    except Exception as e:
        print(f"[pdf_renderer] 실패 (job={job_id}): {e}")

    return {
        "job_id":             job_id,
        "type":               "export",
        "status":             "done",
        "preview_url":        f"/outputs/{dir_name}/{stem}.html",
        "html_download_url":  f"/outputs/{dir_name}/{stem}.html",
        "pdf_url":            pdf_url,
        "output_dir":         str(job_dir),
    }
