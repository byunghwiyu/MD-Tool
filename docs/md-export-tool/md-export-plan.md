# MD Export Tool Plan

## 목표
로컬에서 실행되는 Markdown 변환 툴을 만든다. `.md` 파일을 입력하면 보기 좋은 `HTML`과 `PDF`를 생성하고 결과를 저장할 수 있어야 한다.

## 제품 정의
- 로컬 전용 툴
- 브라우저 UI 사용
- `localhost`만 사용
- 입력: Markdown 파일 (`.md`)
- 출력: `HTML`, `PDF`
- 템플릿 선택 가능
- 출력 결과 다운로드 및 폴더 열기 지원

## 핵심 사용자 시나리오
1. 사용자가 `.md` 파일을 업로드한다.
2. 출력 템플릿을 선택한다.
3. HTML 미리보기를 확인한다.
4. HTML과 PDF를 생성한다.
5. 결과 파일을 열거나 저장한다.

## MVP 범위
- `.md` 파일 업로드
- 템플릿 선택
- HTML 미리보기
- HTML 저장
- PDF 저장
- 작업 상태 표시
- 출력 폴더 열기
- 작업 이력

## 제외 범위
- Markdown 편집기
- 협업 기능
- 클라우드 배포
- DOCX 출력
- 번역 기능
- 고급 문서 편집 UI

## 권장 아키텍처
- 백엔드: FastAPI
- 프론트엔드: 정적 HTML/CSS/JS
- HTML 렌더링: Python Markdown 라이브러리
- PDF 렌더링: Playwright 기반 headless browser
- 실행 환경: localhost only

## 처리 파이프라인
1. Markdown 파일 업로드
2. Markdown 읽기
3. HTML로 변환
4. 템플릿 CSS 적용
5. 최종 HTML 저장
6. HTML을 PDF로 렌더링
7. 결과 폴더에 저장

## 출력 전략
### 1차 출력
- `preview.html`
- `export.pdf`

### 추가 가능 출력
- `metadata.json`
- 렌더링 로그

## 템플릿 전략
초기에는 3가지 템플릿을 제공한다.

### Clean Report
- 보고서형
- 안정적인 여백
- 표/리스트 가독성 우선

### Technical Docs
- 코드블록 강조
- 표와 제목 계층 명확
- 개발 문서용

### Print Essay
- 긴 본문 읽기 최적화
- 인쇄 중심
- 미니멀 스타일

## 백엔드 책임
- 파일 업로드 처리
- Markdown -> HTML 변환
- 템플릿 주입
- PDF 생성
- 작업 상태 및 로그 저장
- 출력 파일 관리

## 프론트엔드 책임
- 업로드 UI
- 템플릿 선택 UI
- HTML 미리보기 UI
- 진행 상태 UI
- 결과 다운로드 UI
- 출력 폴더 열기 UI

## 권장 기술 선택
### Markdown 렌더링
- `markdown`
- 또는 `markdown-it-py`

### PDF 생성
- 1순위: `playwright`
- 대안: `weasyprint`
- 대안 2: `wkhtmltopdf`

권장 선택은 `playwright`다. HTML/CSS 렌더링 품질이 좋고 템플릿 결과를 PDF에 그대로 반영하기 쉽다.

## 리스크
- PDF 렌더러 설치/초기화 비용
- 이미지 경로 처리 문제
- 긴 문서의 페이지 나눔 제어
- Markdown 확장 문법 호환성
- 템플릿별 스타일 차이

## 대응 전략
- 기본 템플릿 우선 안정화
- 이미지 경로 상대/절대 경로 처리 규칙 고정
- page-break 관련 CSS 규칙 정리
- 실패 로그 저장
- HTML 우선 성공, 그 다음 PDF 안정화

## 개발 단계
### 1단계
- 프로젝트 골격 생성
- localhost 서버 실행
- 업로드 UI 구현

### 2단계
- Markdown -> HTML 변환
- HTML 미리보기 구현
- 작업 결과 저장

### 3단계
- 템플릿 3종 적용
- 템플릿 선택 UI 구현

### 4단계
- Playwright PDF 렌더링 추가
- PDF 저장 및 다운로드 구현

### 5단계
- 출력 폴더 열기
- 에러 처리 강화
- 작업 이력 정리

## 성공 기준
- `.md` 업로드 후 HTML 생성 가능
- PDF 생성 가능
- 템플릿 선택 가능
- 결과가 `outputs` 아래 작업별 폴더로 정리됨
- 비개발자가 BAT 파일로 실행 가능
