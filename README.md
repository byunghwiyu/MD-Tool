# Local Toolkit

로컬에서 실행하는 문서 변환 도구 모음. 외부 서비스 없이 `.md → HTML/PDF` 변환과 `PDF → Markdown` 변환을 브라우저 UI로 처리합니다.

---

## 기능

### MD Export
- `.md` 파일을 HTML + PDF로 변환
- 3가지 템플릿 지원: **Clean Report** / **Technical Docs** / **Print Essay**
- 코드 블록 문법 하이라이팅 (Pygments)
- 한국어 폰트 최적화 (Noto Sans KR / Noto Serif KR)
- 변환 결과 브라우저 내 즉시 프리뷰

### PDF → MD
- PDF 파일을 Markdown 또는 HTML로 변환 (`marker` 엔진 사용)
- 비동기 처리 + 자동 폴링 (변환 진행률 실시간 표시)
- 페이지 범위 지정 및 OCR 강제 사용 옵션
- 변환 결과 Raw / Rendered 프리뷰 토글

### 공통
- 원본 파일명 기반 출력 폴더/파일명 생성 (`outputs/{파일명}_{job_id}/`)
- 변환 이력 바 (세션 내 작업 목록 유지)
- 결과 폴더 바로 열기

---

## 요구사항

- Python 3.10+
- [marker-pdf](https://github.com/VikParuchuri/marker) (`marker_single` CLI) — PDF→MD 변환에 필요
- Playwright Chromium — HTML→PDF 렌더링에 필요

---

## 실행 방법

### Windows (권장)

`start-local-toolkit.bat` 더블클릭

최초 실행 시 자동으로:
1. `.venv` 가상환경 생성
2. `requirements.txt` 패키지 설치
3. Playwright Chromium 설치
4. 서버 시작 (`http://localhost:8000`)

### 수동 실행

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
uvicorn app.main:app --port 8000
```

---

## 프로젝트 구조

```
local-toolkit/
├── app/
│   ├── main.py                  # FastAPI 앱 진입점
│   ├── config.py                # 경로 및 설정
│   ├── routes/
│   │   ├── export.py            # MD Export API
│   │   ├── convert.py           # PDF→MD API
│   │   ├── jobs.py              # Export 이력 조회
│   │   └── health.py            # marker 상태 확인
│   ├── services/
│   │   ├── job_runner.py        # MD Export 파이프라인
│   │   ├── job_store.py         # PDF→MD 작업 상태 관리
│   │   ├── pdf_to_md_runner.py  # marker 비동기 실행
│   │   ├── markdown_renderer.py # MD → HTML 변환
│   │   ├── template_loader.py   # 템플릿 + CSS 조합
│   │   ├── pdf_renderer.py      # Playwright HTML→PDF
│   │   └── result_writer.py     # 결과 파일 저장
│   ├── static/
│   │   ├── index.html
│   │   ├── styles.css
│   │   ├── app.js               # MD Export 탭 로직
│   │   └── convert.js           # PDF→MD 탭 로직
│   └── templates/               # HTML 템플릿 + CSS
├── outputs/                     # 변환 결과 저장 (gitignore)
├── workspace/                   # 업로드 임시 파일 (gitignore)
├── requirements.txt
└── start-local-toolkit.bat
```

---

## 설정

`app/config.py`에서 경로 및 옵션 변경 가능:

```python
MARKER_PATH = Path("...")  # marker_single.exe 경로
TRANSLATION_ENABLED = False  # 번역 addon (미구현)
```

---

## 출력 구조

```
outputs/
  {파일명}_{job_id}/
    {파일명}.html
    {파일명}.pdf
    source.md
    metadata.json
```
