# Translator Tool Folder Structure

## 루트
`D:\21. MD Files\translator-tool`

## 구조
```text
translator-tool/
  docs/
    translator-tool-plan.md
    translator-tool-structure.md
  app/
    main.py
    config.py
    models/
      job.py
      translator.py
    routes/
      health.py
      jobs.py
      translate.py
    services/
      job_runner.py
      segmenter.py
      result_writer.py
      translators/
        base.py
        libretranslate.py
        google_free.py
        deepl_free.py
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
      source.txt
      translated.txt
      translated.md
      metadata.json
  .venv/
  requirements.txt
  run-local-tool.ps1
  start-translator-tool.bat
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
- `translate.py`: 번역 요청 생성

### `app/services/`
핵심 로직.
- `job_runner.py`: 작업 실행
- `segmenter.py`: 긴 텍스트 분할
- `result_writer.py`: 출력 파일 생성

### `app/services/translators/`
엔진별 어댑터.
- `base.py`: 공통 인터페이스
- `libretranslate.py`: 기본 무료 엔진
- `google_free.py`: 비공식 Google 번역 엔진
- `deepl_free.py`: 선택형 Free API 엔진

### `app/static/`
로컬 브라우저 UI 파일.

### `workspace/`
작업 중간 데이터.
- `jobs.json`: 작업 상태
- `uploads/`: 업로드 원본
- `temp/`: 세그먼트/임시 산출물

### `outputs/`
최종 결과 저장.
작업별 폴더 생성.

## 실행 파일
### `start-translator-tool.bat`
사용자용 진입점.
더블클릭 실행.

### `run-local-tool.ps1`
가상환경 준비와 앱 실행 담당.

## 저장 원칙
- 원문과 번역문 분리 저장
- 작업별 폴더 사용
- 메타데이터 JSON 저장
- 실패 로그도 보존 가능하게 설계

## 추천 초기 구현 순서
1. `app/main.py`
2. `app/routes/translate.py`
3. `app/services/translators/base.py`
4. `app/services/translators/libretranslate.py`
5. `app/static/index.html`
6. `app/static/app.js`
7. `app/static/styles.css`
8. `start-translator-tool.bat`
