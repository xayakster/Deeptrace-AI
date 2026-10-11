/* frontend/static/js/main.js
   DeepTrace AI — Precision Forensic Client Scripts
*/

document.addEventListener('DOMContentLoaded', () => {
    // Clock initialization
    const clockEl = document.getElementById('clock');
    if (clockEl) {
        const updateClock = () => {
            const now = new Date();
            clockEl.innerText = now.toTimeString().split(' ')[0];
        };
        updateClock();
        setInterval(updateClock, 1000);
    }

    // Drag and Drop support for Forensic Evidence upload
    const uploadBar = document.getElementById('upload-text');
    const fileInput = document.getElementById('file-input');

    if (uploadBar && fileInput) {
        ['dragenter', 'dragover'].forEach(eventName => {
            uploadBar.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadBar.style.borderColor = 'var(--coral-primary)';
                uploadBar.style.backgroundColor = 'var(--coral-tint)';
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadBar.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                uploadBar.style.borderColor = '';
                uploadBar.style.backgroundColor = '';
            }, false);
        });

        uploadBar.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                const event = new Event('change');
                fileInput.dispatchEvent(event);
            }
        }, false);
    }
});

// Diagnostic Log Helper
function addLog(msg) {
    const logs = document.getElementById('logs');
    if (logs) {
        const timeStr = new Date().toTimeString().split(' ')[0];
        const line = document.createElement('div');
        line.innerHTML = `<span class="log-time" style="color:#64748B; margin-right:6px;">[${timeStr}]</span> ${msg}`;
        logs.appendChild(line);
        logs.scrollTop = logs.scrollHeight;
    }
}