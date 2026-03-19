// ── 탭 전환 ───────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(`tab-${tab.dataset.tab}`).classList.add('active');
  });
});

// ── Engine 상태 확인 ──────────────────────────────
async function checkEngine() {
  try {
    const res  = await fetch('/convert/health');
    const data = await res.json();
    const dot   = document.getElementById('engineDot');
    const label = document.getElementById('engineLabel');
    if (data.marker_exists) {
      dot.className = 'engine-dot ok';
      label.textContent = 'marker 준비됨';
    } else {
      dot.className = 'engine-dot error';
      label.textContent = 'marker 없음';
    }
  } catch {
    document.getElementById('engineDot').className = 'engine-dot error';
    document.getElementById('engineLabel').textContent = 'marker 확인 실패';
  }
}

// ── MD Export ─────────────────────────────────────
let selectedFile = null;

const uploadZone          = document.getElementById('uploadZone');
const fileInput           = document.getElementById('fileInput');
const uploadLabel         = document.getElementById('uploadLabel');
const exportBtn           = document.getElementById('exportBtn');
const exportStatusStrip   = document.getElementById('exportStatusStrip');
const exportStatusMsg     = document.getElementById('exportStatusMsg');
const previewEmpty        = document.getElementById('previewEmpty');
const previewFrame        = document.getElementById('previewFrame');
const resultActions       = document.getElementById('resultActions');
const downloadHtmlBtn     = document.getElementById('downloadHtmlBtn');
const downloadPdfBtn      = document.getElementById('downloadPdfBtn');
const openExportFolderBtn = document.getElementById('openExportFolderBtn');
const historyBar          = document.getElementById('historyBar');

uploadZone.addEventListener('click', () => fileInput.click());
uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  if (e.dataTransfer.files[0]) setExportFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener('change', () => { if (fileInput.files[0]) setExportFile(fileInput.files[0]); });

function setExportFile(file) {
  if (!file.name.endsWith('.md')) {
    showExportStatus('error', '.md 파일만 업로드 가능합니다.');
    return;
  }
  selectedFile = file;
  uploadLabel.textContent = file.name;
  uploadZone.classList.add('has-file');
  exportBtn.disabled = false;
  hideExportStatus();
}

document.querySelectorAll('.tmpl').forEach(el => {
  el.addEventListener('click', () => {
    document.querySelectorAll('.tmpl').forEach(o => o.classList.remove('selected'));
    el.classList.add('selected');
    el.querySelector('input[type=radio]').checked = true;
  });
});

function getSelectedTemplate() {
  return document.querySelector('input[name="template"]:checked')?.value ?? 'clean-report';
}

exportBtn.addEventListener('click', async () => {
  if (!selectedFile) return;
  exportBtn.disabled = true;
  showExportStatus('loading', '변환 중...');
  const formData = new FormData();
  formData.append('file', selectedFile);
  formData.append('template', getSelectedTemplate());
  try {
    const res  = await fetch('/export', { method: 'POST', body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail ?? '변환 실패');
    const pdfReady = !!data.pdf_url;
    showExportStatus('success',
      pdfReady
        ? `✅ 변환 완료 — HTML + PDF (${data.job_id})`
        : `✅ HTML 변환 완료 — PDF 생성 실패 (${data.job_id})`
    );
    showExportPreview(data.preview_url, data.pdf_url, data.job_id, selectedFile.name);
    addHistory(data.job_id, selectedFile.name, 'export', () =>
      showExportPreview(data.preview_url, data.pdf_url, data.job_id, selectedFile.name)
    );
  } catch (err) {
    showExportStatus('error', `❌ ${err.message}`);
  } finally {
    exportBtn.disabled = false;
  }
});

function showExportPreview(previewUrl, pdfUrl, jobId, filename) {
  previewEmpty.hidden = true;
  previewFrame.hidden = false;
  previewFrame.src = previewUrl;
  resultActions.hidden = false;
  downloadHtmlBtn.href     = previewUrl;
  downloadHtmlBtn.download = filename.replace('.md', '.html');
  if (pdfUrl) {
    downloadPdfBtn.href     = pdfUrl;
    downloadPdfBtn.download = filename.replace('.md', '.pdf');
    downloadPdfBtn.hidden   = false;
  } else {
    downloadPdfBtn.hidden = true;
  }
  openExportFolderBtn.onclick = () => fetch(`/open-folder/${jobId}`);
}

function showExportStatus(type, msg) {
  exportStatusStrip.hidden    = false;
  exportStatusStrip.className = `status-strip ${type}`;
  exportStatusMsg.textContent = msg;
}
function hideExportStatus() {
  exportStatusStrip.hidden    = true;
  exportStatusStrip.className = 'status-strip';
}

// ── 통합 이력 바 ──────────────────────────────────
function addHistory(id, filename, type, onClick) {
  const item      = document.createElement('div');
  item.className  = 'history-item';
  const typeLabel = type === 'export' ? 'MD' : 'PDF→MD';
  item.innerHTML  = `${filename}<span class="item-type">${typeLabel}</span>`;
  item.addEventListener('click', onClick);
  historyBar.insertBefore(item, historyBar.children[1] ?? null);
}

async function loadExportHistory() {
  try {
    const res  = await fetch('/jobs');
    const jobs = await res.json();
    jobs.forEach(job => {
      addHistory(job.job_id, job.source_filename ?? job.job_id, 'export', () =>
        showExportPreview(job.preview_url, job.pdf_url ?? null, job.job_id, job.source_filename ?? job.job_id)
      );
    });
  } catch { /* 이력 없음 */ }
}

// ── 초기화 ────────────────────────────────────────
checkEngine();
loadExportHistory();
