# Local Toolkit 개발 로그

## 개요

기존에 별도로 운영하던 두 개의 로컬 도구를 하나의 통합 앱으로 합친 작업 기록.

---

## 배경 — 통합 이전 상태

### md-export-tool
- `.md` → HTML + PDF 변환 도구
- FastAPI 백엔드 + 브라우저 UI
- Playwright로 HTML→PDF 렌더링
- 3개 템플릿 (clean-report, technical-docs, print-essay)
- 초기엔 가로 레이아웃(사이드바 + 프리뷰), 이후 세로로 변경

### marker-local-ui
- PDF → Markdown 변환 도구
- `marker_single.exe` CLI 래퍼
- 별도 UI 있었지만 UX 문제 다수:
  - 히어로 섹션 + 과도한 스크롤 구조
  - 수동 새로고침 필요 (자동 폴링 없음)
  - `alert()`으로 오류 표시

---

## 2026-03-20 작업 내역

### 1. 프로젝트 통합 (`local-toolkit`)

두 도구를 하나의 FastAPI 앱으로 통합.

- 폴더 새로 생성: `D:\21. MD Files\local-toolkit`
- 라우터 분리: `export`, `convert`, `jobs`, `health`
- 기존 `D:\21. PDF to MD Files` (marker-local-ui) 삭제

**신규 백엔드 파일:**
- `app/services/job_store.py` — PDF→MD 비동기 작업 상태 관리 (JSON 파일 기반 영속성)
- `app/services/pdf_to_md_runner.py` — `marker_single` 서브프로세스 비동기 실행, 진행률 추정, 로그 스트리밍
- `app/routes/convert.py` — PDF→MD API (`/convert/jobs` CRUD + 다운로드 + 폴더 열기)

### 2. UI/UX 전면 재설계

기존 두 도구의 UI를 하나의 디자인 언어로 통일.

**디자인 시스템:**
- 폰트: IBM Plex Sans KR
- 배경: warm cream 방사형 그라디언트 (`#f3efe6`)
- 액센트: `#c4582a` (테라코타 계열)
- 패널: 글래스모피즘 (`rgba(252,249,242,0.92)`)

**레이아웃:**
- 탭 네비게이션: [MD Export] / [PDF→MD]
- MD Export 탭: 상단 툴바(업로드존 + 템플릿 선택 + 변환 버튼) + 하단 프리뷰
- PDF→MD 탭: 좌측 사이드바(옵션) + 우측 결과 영역 (idle / running / done / failed 상태머신)
- 하단 통합 이력 바: 두 탭의 작업 이력 공유

**PDF→MD UX 개선:**
- 히어로 섹션 제거
- 자동 폴링 (1초 간격, 변환 완료 시 자동 전환)
- 진행률 바 + ETA + 경과시간 실시간 표시
- Raw / Rendered 프리뷰 토글
- 변환 로그 접기/펼치기 (`<details>`)

### 3. 버그 수정

| 버그 | 원인 | 수정 |
|------|------|------|
| Playwright `sync_playwright` 오류 | FastAPI 이벤트 루프 안에서 동기 API 사용 불가 | `async_playwright` + `ThreadPoolExecutor`로 별도 스레드에서 실행 |
| PDF URL이 null로 반환 | 서버 재시작 안 함 | 서버 재시작 |
| 한국어 폰트 깨짐 | `base.html`에 Google Fonts import 누락 | Noto Sans KR / Noto Serif KR 링크 추가 |
| 코드 블록 스타일 없음 | Pygments CSS 미주입 | `template_loader.py`에서 템플릿별 Pygments CSS 동적 주입 |
| citation 마커 출력 (`citeturn14view1` 등) | Claude.ai 출력 아티팩트 | `markdown_renderer.py`에 정규식 전처리 추가 |
| `previewEmpty` 변환 후에도 노출 | `.preview-empty { display: flex }`가 `hidden` 속성 덮어씀 | CSS 최상단에 `[hidden] { display: none !important }` 추가 |
| `relative path can't be expressed as a file URI` | Playwright에 상대경로 전달 | `html_path.resolve()` 호출로 절대경로 변환 |

### 4. outputs 파일명 개선

기존: `outputs/{job_id}/preview.html`
변경: `outputs/{파일명}_{job_id}/{파일명}.html`

- `result_writer.py`에 `make_stem()` 함수 추가 (파일시스템 안전 문자만 남김)
- HTML, PDF 파일명도 원본 파일명 기반으로 생성
- `jobs.py`, `export.py`, `convert.py` 전반 경로 참조 업데이트

---

## 아키텍처 메모

### 비동기 처리 구조 (PDF→MD)

`marker_single.exe`는 ML 모델 로딩 포함 수 분 소요.
FastAPI BackgroundTasks로 비동기 실행, 프론트엔드에서 1초 폴링.

```
POST /convert/jobs
  → job_store에 queued 상태 저장
  → BackgroundTasks로 run_marker() 등록
  → job 즉시 반환

run_marker() (백그라운드)
  → asyncio.create_subprocess_exec
  → stdout 스트리밍 + job_store 갱신
  → 완료 시 status=done, files=[], preview=...

GET /convert/jobs/{id} (프론트 폴링)
  → job_store에서 현재 상태 반환
```

### 번역 addon 아키텍처 (미구현, 준비됨)

번역 기능은 이번에 구현하지 않았지만, 추후 붙이기 쉽도록 자리만 잡아둔 상태.

```python
# app/config.py
TRANSLATION_ENABLED = False  # True로 바꾸면 활성화

# app/services/translators/base.py
class BaseTranslator:
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        raise NotImplementedError

# app/services/job_runner.py
# 스텝 1: 번역 (현재 pass)
if translation_options:
    # content_md = translate(md_text, translation_options)
    pass
```

---

## 번역 툴 addon 구현 계획

### 목표

MD Export 파이프라인에 번역 스텝을 옵션으로 추가.
`.md` → (번역) → HTML + PDF 흐름.

### 구현 항목

#### 백엔드

1. **`app/services/translators/base.py`** (이미 존재)
   - `BaseTranslator` 인터페이스 완성

2. **`app/services/translators/deepl.py`** (신규)
   - DeepL API 연동 (`deepl` 패키지)

3. **`app/services/translators/libre.py`** (신규)
   - LibreTranslate 로컬 서버 연동 (완전 오프라인 옵션)

4. **`app/services/job_runner.py`** 수정
   - 스텝 1 번역 로직 활성화
   - `TRANSLATION_ENABLED` 플래그 확인

5. **`app/routes/export.py`** 수정
   - `TranslationOptions` 폼 파라미터 수신

6. **`app/config.py`** 수정
   - `TRANSLATION_ENABLED = True`
   - `DEEPL_API_KEY` 또는 `LIBRETRANSLATE_URL` 환경변수 연동

#### 프론트엔드

7. **MD Export 탭 UI** 수정
   - 번역 옵션 토글 (on/off)
   - 엔진 선택 (DeepL / LibreTranslate)
   - 언어 방향 선택 (예: EN → KO)

#### 설치

```
pip install deepl          # DeepL 사용 시
pip install libretranslatepy  # LibreTranslate 사용 시
```

### 우선순위 추천

| 순서 | 항목 | 이유 |
|------|------|------|
| 1 | DeepL 연동 | API 키만 있으면 즉시 사용 가능, 품질 우수 |
| 2 | UI 옵션 추가 | 백엔드 완성 후 |
| 3 | LibreTranslate | 완전 로컬 운영 원할 때 |

---

## GitHub

- Repository: https://github.com/byunghwiyu/MD-Tool
- Branch: `main`
