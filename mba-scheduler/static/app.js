document.addEventListener('DOMContentLoaded', () => {
    const btnHowToUse = document.getElementById('btn-how-to-use');
    const modalHowToUse = document.getElementById('modal-how-to-use');
    const closeBtn = document.querySelector('.close-btn');
    
    const btnDownload = document.getElementById('btn-download');
    const fileUpload = document.getElementById('file-upload');
    const btnUpload = document.getElementById('btn-upload');
    
    const statusArea = document.getElementById('status-area');
    const statusIcon = document.getElementById('status-icon');
    const statusTitle = document.getElementById('status-title');
    const statusMessage = document.getElementById('status-message');
    
    const nextStepsArea = document.getElementById('next-steps-area');
    const btnGenerate = document.getElementById('btn-generate');

    // Modal logic
    btnHowToUse.addEventListener('click', () => {
        modalHowToUse.classList.add('active');
    });

    closeBtn.addEventListener('click', () => {
        modalHowToUse.classList.remove('active');
    });

    window.addEventListener('click', (e) => {
        if (e.target === modalHowToUse) {
            modalHowToUse.classList.remove('active');
        }
    });

    // Download Template logic
    btnDownload.addEventListener('click', async () => {
        try {
            btnDownload.textContent = 'Downloading...';
            btnDownload.disabled = true;
            
            const response = await fetch('/api/download_template');
            if (!response.ok) throw new Error('Failed to download template');
            
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'MBA_Scheduler_Template.xlsx';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            showStatus('error', 'Download Failed', 'Could not download the template. Please try again later.');
        } finally {
            btnDownload.textContent = 'Download Template';
            btnDownload.disabled = false;
        }
    });

    // File Input logic
    fileUpload.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            btnUpload.disabled = false;
        } else {
            btnUpload.disabled = true;
        }
        // Hide previous status
        statusArea.classList.add('hidden');
        nextStepsArea.classList.add('hidden');
    });

    // Upload Data logic
    btnUpload.addEventListener('click', async () => {
        const file = fileUpload.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            btnUpload.textContent = 'Uploading...';
            btnUpload.disabled = true;

            const response = await fetch('/api/upload_template', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (!response.ok) {
                showStatus('error', 'Validation Error', result.error || 'An unknown error occurred.');
            } else {
                showStatus('success', 'Data Validated', result.message);
                nextStepsArea.classList.remove('hidden');
                btnGenerate.disabled = false;
            }
        } catch (error) {
            showStatus('error', 'Upload Failed', 'A network error occurred while uploading the file.');
        } finally {
            btnUpload.textContent = 'Upload Data';
            btnUpload.disabled = false;
        }
    });

    // Status display helper
    function showStatus(type, title, message) {
        statusArea.className = `status-card ${type}`;
        statusTitle.textContent = title;
        statusMessage.textContent = message;
        statusIcon.textContent = type === 'error' ? '✖' : '✔';
        statusArea.classList.remove('hidden');
    }
});
