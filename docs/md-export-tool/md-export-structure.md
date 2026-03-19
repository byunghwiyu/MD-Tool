# MD Export Tool Folder Structure

## 루트
`D:\21. MD Files\md-export-tool`

## 구조
```text
md-export-tool/
  docs/
    md-export-plan.md
    md-export-structure.md
  app/
    main.py
    config.py
    routes/
      health.py
      jobs.py
      export.py
    services/
      markdown_renderer.py
      pdf_renderer.py
      template_loader.py
      job_runner.py
      result_writer.py
    templates/
      base.html
      clean-report.css
      technical-docs.css
      print-essay.css
    static/
      index.html
      styles.css
      app.js
  workspace/
    jobs.json
    uploads/
    temp/
  outputs/
    <job_id>/
      source.md
      preview.html
      export.pdf
      metadata.json
  .venv/
  requirements.txt
  run-local-tool.ps1
  start-md-export-tool.bat
  README.md
```

## 폴더 설명
### `docs/`
기획 문서와 구조 문서 보관.

### `app/`
실행 코드 루트.

### `app/routes/`
FastAPI 라우트.
- `health.py`: 상태 확인
- `jobs.py`: 작업 조회
- `export.py`: 변환 요청 생성

### `app/services/`
핵심 처리 로직.
- `markdown_renderer.py`: Markdown -> HTML
- `pdf_renderer.py`: HTML -> PDF
- `template_loader.py`: 템플릿 적용
- `job_runner.py`: 작업 실행
- `result_writer.py`: 출력 파일 저장

### `app/templates/`
출력 템플릿 리소스.
- `base.html`: HTML 래퍼
- CSS 템플릿 3종

### `app/static/`
로컬 웹 UI 파일.

### `workspace/`
작업 중간 데이터 보관.
- `jobs.json`: 상태 저장
- `uploads/`: 업로드 원본
- `temp/`: 중간 렌더링 파일

### `outputs/`
최종 결과 저장 루트.
각 작업별 폴더 생성.

## 실행 파일
### `start-md-export-tool.bat`
사용자용 진입점.
더블클릭 실행.

### `run-local-tool.ps1`
가상환경 준비 및 앱 실행 담당.

## 저장 원칙
- 업로드 원본과 결과를 분리 저장
- 작업별 폴더 사용
- HTML과 PDF를 함께 저장
- 메타데이터 JSON 저장

## 추천 초기 구현 순서
1. `app/main.py`
2. `app/routes/export.py`
3. `app/services/markdown_renderer.py`
4. `app/services/template_loader.py`
5. `app/static/index.html`
6. `app/static/app.js`
7. `app/static/styles.css`
8. `app/services/pdf_renderer.py`
9. `start-md-export-tool.bat`
