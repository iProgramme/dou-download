// --- Navigation ---

const navItems = document.querySelectorAll('.nav-item');
const pages = document.querySelectorAll('.page');

navItems.forEach(item => {
    item.addEventListener('click', () => {
        const page = item.dataset.page;
        navItems.forEach(n => n.classList.remove('active'));
        pages.forEach(p => p.classList.remove('active'));
        item.classList.add('active');
        document.getElementById('page-' + page).classList.add('active');
        if (page === 'history') loadHistory();
        if (page === 'tasks') loadTasks();
    });
});

// --- API Helpers ---

async function api(method, url, body) {
    const opts = { method, headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(url, opts);
    return res.json();
}

function showToast(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = 'toast ' + type;
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
}

function formatTime(iso) {
    if (!iso) return '-';
    const d = new Date(iso);
    return d.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

// --- Settings ---

async function loadSettings() {
    const data = await api('GET', '/api/settings');
    document.getElementById('setting-cookie').value = data.cookie || '';
    document.getElementById('setting-path').value = data.download_path || '';
}

document.getElementById('btn-save-settings').addEventListener('click', async () => {
    const cookie = document.getElementById('setting-cookie').value.trim();
    const path = document.getElementById('setting-path').value.trim();
    if (!cookie) {
        showToast('请输入 Cookie', 'error');
        return;
    }
    await api('PUT', '/api/settings', { cookie, download_path: path });
    showToast('设置已保存');
});

document.getElementById('btn-browse').addEventListener('click', async () => {
    // Try pywebview API first
    if (window.pywebview && window.pywebview.api) {
        try {
            const path = await window.pywebview.api.browse_folder();
            if (path) {
                document.getElementById('setting-path').value = path;
            }
            return;
        } catch (e) { /* fallback */ }
    }
    showToast('请直接在输入框中填写路径', 'success');
});

// --- Download ---

const downloadUrl = document.getElementById('download-url');
const btnDownload = document.getElementById('btn-download');
const statusCard = document.getElementById('status-card');
const statusText = document.getElementById('status-text');
const logOutput = document.getElementById('log-output');
let statusTimer = null;

btnDownload.addEventListener('click', async () => {
    const url = downloadUrl.value.trim();
    if (!url) {
        showToast('请输入博主链接或用户 ID', 'error');
        return;
    }
    btnDownload.disabled = true;
    btnDownload.textContent = '下载中...';
    statusCard.style.display = 'block';
    logOutput.innerHTML = '';
    statusText.textContent = '正在启动...';

    const res = await api('POST', '/api/download', { url });
    if (!res.ok) {
        showToast(res.message || '启动失败', 'error');
        btnDownload.disabled = false;
        btnDownload.textContent = '开始下载';
        return;
    }

    // Poll status
    startStatusPoll();
});

function startStatusPoll() {
    if (statusTimer) clearInterval(statusTimer);
    statusTimer = setInterval(async () => {
        const data = await api('GET', '/api/status');
        statusText.textContent = data.progress || '运行中...';
        if (data.log && data.log.length > logOutput._count) {
            const newLines = data.log.slice(logOutput._count);
            logOutput._count = data.log.length;
            logOutput.textContent += newLines.join('\n') + '\n';
            logOutput.scrollTop = logOutput.scrollHeight;
        }
        if (!data.running) {
            clearInterval(statusTimer);
            statusTimer = null;
            btnDownload.disabled = false;
            btnDownload.textContent = '开始下载';
            statusText.textContent = data.progress || '完成';
        }
    }, 1000);
    logOutput._count = 0;
}

// Allow Enter key to trigger download
downloadUrl.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') btnDownload.click();
});

// --- Tasks ---

const taskList = document.getElementById('task-list');
const modalOverlay = document.getElementById('modal-overlay');

async function loadTasks() {
    const tasks = await api('GET', '/api/tasks');
    if (!tasks.length) {
        taskList.innerHTML = '<p class="empty-hint">暂无定时任务，点击右上角新建。</p>';
        return;
    }
    taskList.innerHTML = tasks.map(t => `
        <div class="card">
            <div class="task-item">
                <div class="task-info">
                    <div class="task-url">${escapeHtml(t.user_url)}</div>
                    <div class="task-meta">
                        每 ${t.interval_hours} 小时 ·
                        上次: ${formatTime(t.last_run)} ·
                        下次: ${formatTime(t.next_run)}
                    </div>
                </div>
                <div class="task-actions">
                    <label class="toggle">
                        <input type="checkbox" ${t.enabled ? 'checked' : ''} onchange="toggleTask(${t.id}, this.checked)">
                        <span class="toggle-slider"></span>
                    </label>
                    <button class="btn btn-small btn-secondary" onclick="runTask(${t.id})">立即执行</button>
                    <button class="btn-icon" onclick="deleteTask(${t.id})" title="删除">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

async function toggleTask(id, enabled) {
    await api('PUT', `/api/tasks/${id}`, { enabled });
    showToast(enabled ? '任务已启用' : '任务已暂停');
}

async function runTask(id) {
    const res = await api('POST', `/api/tasks/${id}/run`);
    if (res.ok) showToast('手动执行已启动');
}

async function deleteTask(id) {
    await api('DELETE', `/api/tasks/${id}`);
    showToast('任务已删除');
    loadTasks();
}

// Modal
document.getElementById('btn-new-task').addEventListener('click', () => {
    modalOverlay.style.display = 'flex';
    document.getElementById('task-url').value = '';
    document.getElementById('task-interval').value = '6';
});

document.getElementById('btn-cancel-task').addEventListener('click', () => {
    modalOverlay.style.display = 'none';
});

modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) modalOverlay.style.display = 'none';
});

document.getElementById('btn-confirm-task').addEventListener('click', async () => {
    const url = document.getElementById('task-url').value.trim();
    const interval = document.getElementById('task-interval').value;
    if (!url) {
        showToast('请输入博主链接', 'error');
        return;
    }
    const res = await api('POST', '/api/tasks', { url, interval_hours: parseInt(interval) });
    if (res.ok) {
        showToast('定时任务已创建');
        modalOverlay.style.display = 'none';
        loadTasks();
    } else {
        showToast(res.message || '创建失败', 'error');
    }
});

// --- History ---

let historyPage = 1;

async function loadHistory(page) {
    if (page) historyPage = page;
    const data = await api('GET', `/api/history?page=${historyPage}&per_page=15`);
    const list = document.getElementById('history-list');
    const pagination = document.getElementById('history-pagination');

    if (!data.items.length) {
        list.innerHTML = '<p class="empty-hint">暂无下载记录。</p>';
        pagination.innerHTML = '';
        return;
    }

    list.innerHTML = data.items.map(h => `
        <div class="card">
            <div class="history-item">
                <div class="history-info">
                    <div class="history-nickname">${escapeHtml(h.nickname || h.user_url)}</div>
                    <div class="history-meta">
                        ${h.video_count} 个视频 · ${formatTime(h.started_at)}
                        ${h.finished_at ? ' - ' + formatTime(h.finished_at) : ''}
                        ${h.message ? ' · ' + escapeHtml(h.message) : ''}
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:8px;">
                    <span class="status-badge ${h.status}">${statusLabel(h.status)}</span>
                    <button class="btn-icon" onclick="deleteHistory(${h.id})" title="删除">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"/></svg>
                    </button>
                </div>
            </div>
        </div>
    `).join('');

    // Pagination
    const totalPages = Math.ceil(data.total / data.per_page);
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }
    let btns = '';
    btns += `<button ${historyPage <= 1 ? 'disabled' : ''} onclick="loadHistory(${historyPage - 1})">上一页</button>`;
    for (let i = 1; i <= totalPages && i <= 10; i++) {
        btns += `<button class="${i === historyPage ? 'active' : ''}" onclick="loadHistory(${i})">${i}</button>`;
    }
    btns += `<button ${historyPage >= totalPages ? 'disabled' : ''} onclick="loadHistory(${historyPage + 1})">下一页</button>`;
    pagination.innerHTML = btns;
}

async function deleteHistory(id) {
    await api('DELETE', `/api/history/${id}`);
    loadHistory();
}

function statusLabel(s) {
    return { success: '成功', failed: '失败', running: '运行中' }[s] || s;
}

function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str;
    return d.innerHTML;
}

// --- Init ---

loadSettings();
loadHistory();
