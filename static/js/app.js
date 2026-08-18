// Frontend Controller for SentiMind AI
document.addEventListener('DOMContentLoaded', () => {
  // Navigation & Tab Switching
  const navItems = document.querySelectorAll('.nav-item');
  const tabPanes = document.querySelectorAll('.tab-pane');
  const pageTitle = document.getElementById('page-title');
  const pageSubtitle = document.getElementById('page-subtitle');

  const tabMeta = {
    'single-tab': {
      title: 'Single Review Sentiment Analysis',
      subtitle: 'Real-time deep learning inference using fine-tuned DistilBERT'
    },
    'batch-tab': {
      title: 'Batch Dataset CSV Analysis',
      subtitle: 'Analyze thousands of customer reviews with theme detection & KPIs'
    },
    'insights-tab': {
      title: 'AI Business Intelligence & Strategy',
      subtitle: 'Executive action plans, operational risk synthesis, and customer pain points'
    },
    'performance-tab': {
      title: 'Model Evaluation Benchmarks',
      subtitle: 'DistilBERT test metrics fine-tuned on 20,000 Amazon customer reviews'
    }
  };

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const targetTab = item.getAttribute('data-tab');
      navItems.forEach(n => n.classList.remove('active'));
      tabPanes.forEach(p => p.classList.remove('active'));

      item.classList.add('active');
      const activePane = document.getElementById(targetTab);
      if (activePane) activePane.classList.add('active');

      if (tabMeta[targetTab]) {
        pageTitle.textContent = tabMeta[targetTab].title;
        pageSubtitle.textContent = tabMeta[targetTab].subtitle;
      }

      if (targetTab === 'performance-tab') {
        renderPerformanceChart();
      }
    });
  });

  // Health and Model Status Check
  checkModelHealth();

  // Single Review Logic
  initSingleReview();

  // Batch Review Logic
  initBatchReview();

  // Initial Benchmarks
  renderPerformanceChart();
});

// Toast notification helper
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  let icon = 'fa-info-circle';
  if (type === 'success') icon = 'fa-check-circle text-success';
  if (type === 'error') icon = 'fa-exclamation-triangle text-danger';

  toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Health Check
async function checkModelHealth() {
  const statusDot = document.getElementById('model-status-dot');
  const statusText = document.getElementById('model-status-text');
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    if (data.model_status && data.model_status.status === 'ready') {
      statusDot.className = 'status-dot pulsing';
      statusDot.style.background = 'var(--success)';
      statusText.textContent = 'DistilBERT Ready';
    } else {
      statusDot.className = 'status-dot';
      statusDot.style.background = 'var(--warning)';
      statusText.textContent = 'Model Standby';
    }
  } catch (err) {
    statusDot.style.background = 'var(--danger)';
    statusText.textContent = 'Backend Offline';
  }
}

// Single Review Module
function initSingleReview() {
  const input = document.getElementById('single-review-input');
  const analyzeBtn = document.getElementById('analyze-single-btn');
  const clearBtn = document.getElementById('clear-single-btn');
  const emptyState = document.getElementById('single-empty-state');
  const resultContent = document.getElementById('single-result-content');
  const latencyBadge = document.getElementById('single-latency');

  // Quick Samples
  document.querySelectorAll('.sample-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      input.value = pill.getAttribute('data-text');
      analyzeReview();
    });
  });

  clearBtn.addEventListener('click', () => {
    input.value = '';
    emptyState.style.display = 'block';
    resultContent.style.display = 'none';
    latencyBadge.textContent = 'Ready';
  });

  analyzeBtn.addEventListener('click', () => {
    analyzeReview();
  });

  async function analyzeReview() {
    const text = input.value.trim();
    if (!text) {
      showToast('Please enter review text to analyze.', 'error');
      return;
    }

    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';
    latencyBadge.textContent = 'Running...';

    const startTime = performance.now();

    try {
      const res = await fetch('/api/predict/single', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ review: text })
      });

      const data = await res.json();
      const elapsed = Math.round(performance.now() - startTime);

      if (!res.ok) {
        throw new Error(data.detail || 'Prediction request failed');
      }

      latencyBadge.textContent = `${elapsed} ms`;
      renderSingleResult(data);
    } catch (err) {
      showToast(err.message, 'error');
      latencyBadge.textContent = 'Error';
    } finally {
      analyzeBtn.disabled = false;
      analyzeBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Analyze Sentiment';
    }
  }

  function renderSingleResult(data) {
    emptyState.style.display = 'none';
    resultContent.style.display = 'block';

    const banner = document.getElementById('sentiment-banner');
    const icon = document.getElementById('sentiment-icon');
    const title = document.getElementById('sentiment-title');
    const confVal = document.getElementById('confidence-value');

    const isPos = data.sentiment === 'POSITIVE';
    banner.className = `sentiment-banner ${isPos ? 'positive' : 'negative'}`;
    icon.innerHTML = isPos 
      ? '<i class="fa-solid fa-face-smile"></i>' 
      : '<i class="fa-solid fa-face-frown"></i>';
    title.textContent = data.sentiment;
    confVal.textContent = `${data.confidence.toFixed(1)}%`;

    const posProb = data.probabilities ? data.probabilities.positive : (isPos ? data.confidence : 100 - data.confidence);
    const negProb = data.probabilities ? data.probabilities.negative : (isPos ? 100 - data.confidence : data.confidence);

    document.getElementById('pos-prob-val').textContent = `${posProb.toFixed(1)}%`;
    document.getElementById('pos-prob-fill').style.width = `${posProb}%`;

    document.getElementById('neg-prob-val').textContent = `${negProb.toFixed(1)}%`;
    document.getElementById('neg-prob-fill').style.width = `${negProb}%`;

    const strong = document.getElementById('alert-strong');
    const desc = document.getElementById('alert-desc');
    if (isPos) {
      strong.textContent = 'Positive Sentiment Detected';
      desc.textContent = 'Customer feedback conveys approval, satisfaction, or praise with high confidence.';
    } else {
      strong.textContent = 'Negative Sentiment Detected';
      desc.textContent = 'Customer feedback points to dissatisfaction, defects, delivery friction, or unmet expectations.';
    }
  }
}

// Batch Review Module
let sentimentChartInstance = null;
let confidenceChartInstance = null;
let batchDataCache = null;

function initBatchReview() {
  const dropzone = document.getElementById('csv-dropzone');
  const fileInput = document.getElementById('csv-file-input');
  const fileInfoBar = document.getElementById('file-info-bar');
  const filenameEl = document.getElementById('selected-filename');
  const filesizeEl = document.getElementById('selected-filesize');
  const columnSelect = document.getElementById('column-select');
  const runBatchBtn = document.getElementById('run-batch-btn');
  const downloadCsvBtn = document.getElementById('download-csv-btn');

  let selectedFile = null;

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files.length) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files.length) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  function handleFileSelected(file) {
    if (!file.name.endsWith('.csv')) {
      showToast('Please select a valid .csv file.', 'error');
      return;
    }

    selectedFile = file;
    filenameEl.textContent = file.name;
    filesizeEl.textContent = `${(file.size / 1024).toFixed(1)} KB`;
    fileInfoBar.style.display = 'flex';

    // Peek columns by reading first chunk
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target.result;
      const firstLine = text.split('\n')[0];
      const cols = firstLine.split(',').map(c => c.replace(/["\r]/g, '').trim()).filter(Boolean);
      
      columnSelect.innerHTML = '';
      cols.forEach(col => {
        const opt = document.createElement('option');
        opt.value = col;
        opt.textContent = col;
        columnSelect.appendChild(opt);
      });

      // Prefer standard review columns
      const preferred = ['review', 'text', 'review_text', 'comment', 'feedback'];
      for (const pref of preferred) {
        if (cols.includes(pref)) {
          columnSelect.value = pref;
          break;
        }
      }
    };
    reader.readAsText(file.slice(0, 4096));
    showToast(`Loaded ${file.name}`, 'success');
  }

  runBatchBtn.addEventListener('click', async () => {
    if (!selectedFile) {
      showToast('Please select a CSV file first.', 'error');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);
    if (columnSelect.value) {
      formData.append('column', columnSelect.value);
    }

    runBatchBtn.disabled = true;
    runBatchBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';

    try {
      const res = await fetch('/api/predict/batch', {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Batch analysis failed');

      batchDataCache = data;
      renderBatchResults(data);
      populateInsights(data.insights);
      showToast(`Batch completed: ${data.total_analyzed} reviews analyzed`, 'success');
    } catch (err) {
      showToast(err.message, 'error');
    } finally {
      runBatchBtn.disabled = false;
      runBatchBtn.innerHTML = '<i class="fa-solid fa-play"></i> Run Batch Analysis';
    }
  });

  downloadCsvBtn.addEventListener('click', () => {
    if (!batchDataCache || !batchDataCache.all_rows) {
      showToast('No analyzed data to export.', 'error');
      return;
    }

    const rows = batchDataCache.all_rows;
    const colName = batchDataCache.selected_column;
    let csvContent = `data:text/csv;charset=utf-8,${colName},sentiment,confidence\n`;

    rows.forEach(r => {
      const escapedText = `"${String(r[colName]).replace(/"/g, '""')}"`;
      csvContent += `${escapedText},${r.sentiment},${r.confidence}\n`;
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `analyzed_${selectedFile ? selectedFile.name : 'reviews.csv'}`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  });
}

function renderBatchResults(data) {
  const container = document.getElementById('batch-results-container');
  container.style.display = 'block';

  // KPIs
  const summary = data.summary;
  document.getElementById('kpi-total').textContent = summary.total_reviews.toLocaleString();
  document.getElementById('kpi-positive').textContent = `${summary.positive_reviews} (${summary.positive_percentage}%)`;
  document.getElementById('kpi-negative').textContent = `${summary.negative_reviews} (${summary.negative_percentage}%)`;
  document.getElementById('kpi-confidence').textContent = `${summary.average_confidence}%`;

  // Sentiment Bar/Doughnut Chart
  renderSentimentCharts(summary);

  // Themes
  const themesList = document.getElementById('themes-list');
  const themesBadge = document.getElementById('themes-count-badge');
  themesList.innerHTML = '';
  themesBadge.textContent = `${data.themes.length} Themes`;

  if (data.themes && data.themes.length > 0) {
    data.themes.forEach(([theme, count]) => {
      const item = document.createElement('div');
      item.className = 'theme-item';
      item.innerHTML = `
        <span><i class="fa-solid fa-triangle-exclamation"></i> ${theme}</span>
        <span class="badge badge-warning">${count} mention${count > 1 ? 's' : ''}</span>
      `;
      themesList.appendChild(item);
    });
  } else {
    themesList.innerHTML = '<p class="text-muted" style="font-size:0.85rem;">No concentrated complaint themes detected.</p>';
  }

  // Sample Negatives
  const samplesList = document.getElementById('sample-negatives-list');
  samplesList.innerHTML = '';
  if (data.sample_negatives && data.sample_negatives.length > 0) {
    data.sample_negatives.forEach(sample => {
      const box = document.createElement('div');
      box.className = 'sample-review-box';
      box.textContent = `"${sample}"`;
      samplesList.appendChild(box);
    });
  } else {
    samplesList.innerHTML = '<p class="text-muted" style="font-size:0.85rem;">No negative review samples found in this dataset.</p>';
  }

  // Table Preview
  const tbody = document.getElementById('batch-table-body');
  tbody.innerHTML = '';
  const colName = data.selected_column;
  data.preview_rows.forEach(row => {
    const tr = document.createElement('tr');
    const isPos = row.sentiment === 'POSITIVE';
    tr.innerHTML = `
      <td>${row[colName]}</td>
      <td><span class="badge ${isPos ? 'badge-success' : 'badge-danger'}">${row.sentiment}</span></td>
      <td><strong>${row.confidence}%</strong></td>
    `;
    tbody.appendChild(tr);
  });
}

function renderSentimentCharts(summary) {
  const sentCtx = document.getElementById('sentimentChart').getContext('2d');
  const confCtx = document.getElementById('confidenceChart').getContext('2d');

  if (sentimentChartInstance) sentimentChartInstance.destroy();
  if (confidenceChartInstance) confidenceChartInstance.destroy();

  sentimentChartInstance = new Chart(sentCtx, {
    type: 'doughnut',
    data: {
      labels: ['Positive Sentiment', 'Negative Sentiment'],
      datasets: [{
        data: [summary.positive_reviews, summary.negative_reviews],
        backgroundColor: ['#10b981', '#ef4444'],
        borderColor: ['#064e3b', '#7f1d1d'],
        borderWidth: 2
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { labels: { color: '#cbd5e1', font: { family: 'Plus Jakarta Sans', size: 12 } } }
      }
    }
  });

  const dist = summary.confidence_distribution || {};
  const labels = Object.keys(dist);
  const values = Object.values(dist);

  confidenceChartInstance = new Chart(confCtx, {
    type: 'bar',
    data: {
      labels: labels.length ? labels : ['50-60%', '60-70%', '70-80%', '80-90%', '90-100%'],
      datasets: [{
        label: 'Reviews Count',
        data: values.length ? values : [0, 0, 0, 0, 0],
        backgroundColor: '#6366f1',
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { ticks: { color: '#94a3b8' }, grid: { display: false } },
        y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255,255,255,0.05)' } }
      }
    }
  });
}

function populateInsights(insights) {
  if (!insights) return;
  document.getElementById('insights-empty-state').style.display = 'none';
  document.getElementById('insights-content').style.display = 'block';

  document.getElementById('insight-situation').textContent = insights.Situation || 'N/A';
  document.getElementById('insight-priority').innerHTML = insights.Priority ? insights.Priority.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') : 'N/A';
  document.getElementById('insight-problems').innerHTML = insights['Main Problems'] ? insights['Main Problems'].replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') : 'N/A';

  const actionsContainer = document.getElementById('insight-actions');
  actionsContainer.innerHTML = '';
  const rawActions = insights['Recommended Actions'] || '';
  const actionLines = rawActions.split('\n').filter(l => l.trim().startsWith('-'));

  if (actionLines.length > 0) {
    actionLines.forEach(line => {
      const item = document.createElement('div');
      item.className = 'action-item';
      item.innerHTML = `<i class="fa-solid fa-arrow-right"></i> <span>${line.replace(/^- /, '')}</span>`;
      actionsContainer.appendChild(item);
    });
  } else {
    actionsContainer.innerHTML = '<p class="text-muted">No specific action items generated.</p>';
  }
}

let perfChartInstance = null;
function renderPerformanceChart() {
  const canvas = document.getElementById('performanceChart');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  if (perfChartInstance) return;

  perfChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Accuracy', 'Precision', 'Recall', 'F1 Score'],
      datasets: [{
        label: 'Metric (%)',
        data: [93.88, 94.20, 93.52, 93.86],
        backgroundColor: ['#6366f1', '#10b981', '#a855f7', '#ef4444'],
        borderRadius: 8
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: { ticks: { color: '#cbd5e1' }, grid: { display: false } },
        y: { 
          min: 80, 
          max: 100, 
          ticks: { color: '#94a3b8', callback: (v) => `${v}%` },
          grid: { color: 'rgba(255, 255, 255, 0.05)' }
        }
      }
    }
  });
}
