// ── PDF→MD 탭 ─────────────────────────────────────
let pdfFile       = null;
let activeJobId   = null;
let pollingHandle = null;

const pdfDropzone  = document.getElementById('pdfDropzone');
const pdfInput     = document.getElementById('pdfInput');
const pdfDropTitle = document.getElementById('pdfDropTitle');
const convertBtn   = document.getElementById('convertBtn');
const pageRange    = document.getElementById('pageRange');
const forceOcr     = document.getElementById('forceOcr');

const resultIdle    = document.getElementById('resultIdle');
const resultRunning = document.getElementById('resultRunning');
const resultDone    = document.getElementById('resultDone');
const resultFailed  = document.getElementById('resultFailed');

// 포맷 선택
document.querySelectorAll('.fmt').forEach(el => {
  el.addEventListener('click', () => {
    document.querySelectorAll('.fmt').forEach(o => o.classList.remove('selected'));
    el.classList.add('selected');
    el.querySelector('input[type=radio]').checked = true;
  });
});

// 드롭존
pdfDropzone.addEventListener('click', () => pdfInput.click());
pdfDropzone.addEventListener('dragover', e => { e.preventDefault(); pdfDropzone.classList.add('drag-active'); });
pdfDropzone.addEventListener('dragleave', () => pdfDropzone.classList.remove('drag-active'));
pdfDropzone.addEventListener('drop', e => {
  e.preventDefault();
  pdfDropzone.classList.remove('drag-active');
  if (e.dataTransfer.files[0]) setPdfFile(e.dataTransfer.files[0]);
});
pdfInput.addEventListener('change', () => { if (pdfInput.files[0]) setPdfFile(pdfInput.files[0]); });

function setPdfFile(file) {
  if (!file.name.toLowerCase().endsWith('.pdf')) {
    alert('PDF 파일만 업로드 가능합니다.');
    return;
  }
  pdfFile = file;
  pdfDropTitle.textContent = file.name;
  pdfDropzone.classList.add('has-file');
  convertBtn.disabled = false;
}

// 변환 시작
convertBtn.addEventListener('click', async () => {
  if (!pdfFile) return;
  convertBtn.disabled = true;

  const formData = new FormData();
  formData.append('file', pdfFile);
  formData.append('output_format', document.querySelector('input[name="output_format"]:checked')?.value ?? 'markdown');
  formData.append('page_range', pageRange.value.trim());
  formData.append('force_ocr', forceOcr.checked ? 'true' : 'false');

  try {
    const res  = await fetch('/convert/jobs', { method: 'POST', body: formData });
    const job  = await res.json();
    if (!res.ok) throw new Error(job.detail ?? '변환 시작 실패');

    activeJobId = job.id;
    showRunning(job);
    addHistory(job.id, job.filename, 'convert', () => loadJob(job.id));
    startPolling();
  } catch (err) {
    showFailed({ error: err.message, log: '' });
  } finally {
    convertBtn.disabled = false;
  }
});

// ── 상태 표시 ─────────────────────────────────────
function showState(...ids) {
  ['resultIdle','resultRunning','resultDone','resultFailed'].forEach(id => {
    document.getElementById(id).classList.add('hidden');
  });
  ids.forEach(id => document.getElementById(id).classList.remove('hidden'));
}

function showRunning(job) {
  showState('resultRunning');
  document.getElementById('runningFilename').textContent = job.filename;
  updateProgress(job);
}

function updateProgress(job) {
  const pct = Math.max(0, Math.min(100, job.progress || 0));
  document.getElementById('progressBar').style.width = `${pct}%`;
  document.getElementById('progressPct').textContent  = `${pct}%`;
  document.getElementById('progressEta').textContent  = `ETA ${fmtSec(job.eta_seconds)}`;
  document.getElementById('progressElapsed').textContent = `경과 ${fmtSec(job.elapsed_seconds)}`;

  const note = document.getElementById('progressNote');
  if (job.status === 'queued')  note.textContent = `대기 중 — 예상 완료까지 약 ${fmtSec(job.eta_seconds)}`;
  else if (job.status === 'running') note.textContent = `변환 중 — 예상 완료까지 약 ${fmtSec(job.eta_seconds)}`;
}

function showDone(job) {
  showState('resultDone');

  document.getElementById('doneFilename').textContent = job.filename;
  document.getElementById('doneMeta').textContent =
    `완료 · ${fmtSec(job.elapsed_seconds)} 소요 · ${job.options?.output_format ?? ''}`;

  // 파일 목록
  const list = document.getElementById('fileList');
  list.innerHTML = '';
  for (const file of job.files || []) {
    const li   = document.createElement('li');
    const url  = `/convert/jobs/${job.id}/download?path=${encodeURIComponent(file.relative_path)}`;
    li.innerHTML = `<a href="${url}" target="_blank">${file.name}</a><span class="file-size">${fmtBytes(file.size)}</span>`;
    list.appendChild(li);
  }

  // 프리뷰
  document.getElementById('previewRaw').textContent = job.preview || '';
  renderConvertPreview(job);

  // 로그
  document.getElementById('logContent').textContent = job.log || '';

  // 폴더 열기
  document.getElementById('openConvertFolderBtn').onclick = async () => {
    await fetch(`/convert/jobs/${job.id}/open-folder`, { method: 'POST' });
  };
}

function showFailed(job) {
  showState('resultFailed');
  document.getElementById('failedMsg').textContent = job.error || '알 수 없는 오류';
  document.getElementById('failedLog').textContent = job.log  || '';
}

// 프리뷰 렌더링 (Raw / Rendered 토글)
let currentPreviewMode = 'raw';

document.getElementById('rawBtn').addEventListener('click', () => {
  currentPreviewMode = 'raw';
  document.getElementById('rawBtn').classList.add('active');
  document.getElementById('renderedBtn').classList.remove('active');
  document.getElementById('previewRaw').classList.remove('hidden');
  document.getElementById('previewRendered').classList.add('hidden');
});

document.getElementById('renderedBtn').addEventListener('click', () => {
  currentPreviewMode = 'rendered';
  document.getElementById('renderedBtn').classList.add('active');
  document.getElementById('rawBtn').classList.remove('active');
  document.getElementById('previewRaw').classList.add('hidden');
  document.getElementById('previewRendered').classList.remove('hidden');
});

function renderConvertPreview(job) {
  const el = document.getElementById('previewRendered');
  if (!job.preview) { el.innerHTML = '<p style="color:var(--muted)">미리볼 내용이 없습니다.</p>'; return; }
  if (job.preview_type === 'markdown') {
    el.innerHTML = simpleMarkdown(job.preview);
  } else if (job.preview_type === 'html') {
    el.innerHTML = job.preview;
  } else {
    el.innerHTML = `<pre>${escHtml(job.preview)}</pre>`;
  }
}

function simpleMarkdown(md) {
  const esc = escHtml(md);
  return esc.split(/\n\n+/).map(block => {
    if (block.startsWith('### ')) return `<h3>${block.slice(4)}</h3>`;
    if (block.startsWith('## '))  return `<h2>${block.slice(3)}</h2>`;
    if (block.startsWith('# '))   return `<h1>${block.slice(2)}</h1>`;
    if (block.startsWith('- ')) {
      const items = block.split('\n').map(l => `<li>${l.replace(/^-\s+/,'')}</li>`).join('');
      return `<ul>${items}</ul>`;
    }
    return `<p>${block.replace(/\n/g,'<br>')}</p>`;
  }).join('');
}

function escHtml(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

// ── 폴링 ──────────────────────────────────────────
function startPolling() {
  clearTimeout(pollingHandle);
  pollingHandle = setTimeout(pollJob, 1000);
}

async function pollJob() {
  if (!activeJobId) return;
  await loadJob(activeJobId);
}

async function loadJob(jobId) {
  try {
    const res = await fetch(`/convert/jobs/${jobId}`);
    const job = await res.json();

    if (job.status === 'queued' || job.status === 'running') {
      showRunning(job);
      startPolling();
    } else if (job.status === 'done') {
      showDone(job);
    } else {
      showFailed(job);
    }
  } catch (err) {
    showFailed({ error: `폴링 실패: ${err.message}`, log: '' });
  }
}

// ── 변환 이력 불러오기 ─────────────────────────────
async function loadConvertHistory() {
  try {
    const res  = await fetch('/convert/jobs');
    const data = await res.json();
    (data.jobs || []).forEach(job => {
      addHistory(job.id, job.filename, 'convert', () => loadJob(job.id));
    });
  } catch { /* 이력 없음 */ }
}

// ── 유틸 ──────────────────────────────────────────
function fmtSec(v) {
  if (v === null || v === undefined) return '—';
  const m = Math.floor(v / 60), s = v % 60;
  return m > 0 ? `${m}m ${String(s).padStart(2,'0')}s` : `${s}s`;
}
function fmtBytes(v) {
  if (!v) return '—';
  if (v < 1024) return `${v} B`;
  if (v < 1024*1024) return `${Math.ceil(v/1024)} KB`;
  return `${(v/(1024*1024)).toFixed(1)} MB`;
}

// ── 초기화 ────────────────────────────────────────
loadConvertHistory();
