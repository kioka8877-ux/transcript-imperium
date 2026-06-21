// GitHub Configuration
const GITHUB_OWNER = 'kioka8877-ux';
const GITHUB_REPO = 'transcript-imperium';
const WORKFLOW_FILE = 'extract-transcripts.yml';

// DOM Elements
const extractBtn = document.getElementById('extractBtn');
const youtubeUrl = document.getElementById('youtubeUrl');
const progressContainer = document.getElementById('progressContainer');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const progressPercent = document.getElementById('progressPercent');
const statusText = document.getElementById('statusText');
const resultContainer = document.getElementById('resultContainer');
const downloadLink = document.getElementById('downloadLink');
const errorContainer = document.getElementById('errorContainer');
const errorMessage = document.getElementById('errorMessage');

// Status messages (Warhammer themed)
const statusMessages = [
    '💀 PURGING DATA HERESY 💀',
    '⚔️ SANCTIFYING THE MACHINE SPIRIT ⚔️',
    '🔥 BURNING THE UNCLEAN CODE 🔥',
    '⚙️ APPEASING THE OMNISSIAH ⚙️',
    '🛡️ FORTIFYING THE DATA FORTRESS 🛡️',
    '💀 FOR THE EMPEROR! 💀'
];

let currentStatusIndex = 0;
let statusInterval = null;

// Extract button click handler
extractBtn.addEventListener('click', async () => {
    const url = youtubeUrl.value.trim();
    const mode = document.querySelector('input[name="mode"]:checked').value;
    
    // Validate URL
    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }
    
    if (!isValidYouTubeUrl(url)) {
        showError('Invalid YouTube URL. Please check and try again.');
        return;
    }
    
    // Start extraction
    await startExtraction(url, mode);
});

// Validate YouTube URL
function isValidYouTubeUrl(url) {
    const patterns = [
        /^https?:\/\/(www\.)?youtube\.com\/watch\?v=[\w-]+/,
        /^https?:\/\/youtu\.be\/[\w-]+/,
        /^https?:\/\/(www\.)?youtube\.com\/@[\w-]+/,
        /^https?:\/\/(www\.)?youtube\.com\/channel\/[\w-]+/,
        /^https?:\/\/(www\.)?youtube\.com\/c\/[\w-]+/,
        /^https?:\/\/(www\.)?youtube\.com\/user\/[\w-]+/
    ];
    
    return patterns.some(pattern => pattern.test(url));
}

// Start extraction process
async function startExtraction(url, mode) {
    // Hide previous results/errors
    hideAll();
    
    // Show progress
    progressContainer.classList.remove('hidden');
    extractBtn.disabled = true;
    
    // Start status animation
    startStatusAnimation();
    
    try {
        // Trigger GitHub Actions workflow
        updateProgress(10, 'Initiating extraction workflow...');
        const runId = await triggerWorkflow(url, mode);
        
        if (!runId) {
            throw new Error('Failed to trigger workflow');
        }
        
        // Poll for completion
        updateProgress(20, 'Workflow started, processing...');
        await pollWorkflowStatus(runId);
        
    } catch (error) {
        console.error('Extraction error:', error);
        showError(error.message || 'An error occurred during extraction');
        resetUI();
    }
}

// Trigger GitHub Actions workflow
async function triggerWorkflow(url, mode) {
    try {
        // Note: This requires a backend proxy or GitHub App for security
        // For now, we'll use repository_dispatch which requires a token
        
        // This is a placeholder - you'll need to implement a secure backend
        const response = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/dispatches`, {
            method: 'POST',
            headers: {
                'Accept': 'application/vnd.github.v3+json',
                'Content-Type': 'application/json',
                // Note: Token should be handled by a backend proxy for security
            },
            body: JSON.stringify({
                event_type: 'extract_transcript',
                client_payload: {
                    url: url,
                    mode: mode,
                    timestamp: new Date().toISOString()
                }
            })
        });
        
        if (!response.ok) {
            throw new Error(`GitHub API error: ${response.statusText}`);
        }
        
        // Get the latest workflow run
        await new Promise(resolve => setTimeout(resolve, 2000)); // Wait for workflow to start
        const runsResponse = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs?per_page=1`);
        const runsData = await runsResponse.json();
        
        if (runsData.workflow_runs && runsData.workflow_runs.length > 0) {
            return runsData.workflow_runs[0].id;
        }
        
        return null;
        
    } catch (error) {
        console.error('Trigger workflow error:', error);
        throw error;
    }
}

// Poll workflow status
async function pollWorkflowStatus(runId) {
    const maxAttempts = 60; // 5 minutes max (5s intervals)
    let attempts = 0;
    
    while (attempts < maxAttempts) {
        try {
            const response = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs/${runId}`);
            const data = await response.json();
            
            const status = data.status;
            const conclusion = data.conclusion;
            
            if (status === 'completed') {
                if (conclusion === 'success') {
                    // Extraction successful
                    updateProgress(100, 'Extraction complete!');
                    await fetchResult(runId);
                    return;
                } else {
                    throw new Error(`Workflow failed with conclusion: ${conclusion}`);
                }
            }
            
            // Update progress based on status
            const progress = Math.min(20 + (attempts * 1.2), 90);
            updateProgress(progress, `Processing... (${Math.floor(progress)}%)`);
            
            // Wait before next poll
            await new Promise(resolve => setTimeout(resolve, 5000));
            attempts++;
            
        } catch (error) {
            console.error('Poll error:', error);
            throw error;
        }
    }
    
    throw new Error('Extraction timed out. Please try again.');
}

// Fetch extraction result
async function fetchResult(runId) {
    try {
        // Get artifacts
        const response = await fetch(`https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/runs/${runId}/artifacts`);
        const data = await response.json();
        
        if (data.artifacts && data.artifacts.length > 0) {
            const artifact = data.artifacts[0];
            const downloadUrl = artifact.archive_download_url;
            
            // Show success
            stopStatusAnimation();
            progressContainer.classList.add('hidden');
            resultContainer.classList.remove('hidden');
            downloadLink.href = downloadUrl;
            downloadLink.download = 'transcript.zip';
            
        } else {
            throw new Error('No artifacts found');
        }
        
    } catch (error) {
        console.error('Fetch result error:', error);
        throw error;
    } finally {
        resetUI();
    }
}

// Update progress
function updateProgress(percent, text) {
    progressFill.style.width = `${percent}%`;
    progressPercent.textContent = `${Math.floor(percent)}%`;
    progressText.textContent = text;
}

// Start status animation
function startStatusAnimation() {
    currentStatusIndex = 0;
    statusText.textContent = statusMessages[0];
    
    statusInterval = setInterval(() => {
        currentStatusIndex = (currentStatusIndex + 1) % statusMessages.length;
        statusText.textContent = statusMessages[currentStatusIndex];
    }, 2000);
}

// Stop status animation
function stopStatusAnimation() {
    if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
    }
}

// Show error
function showError(message) {
    errorMessage.textContent = message;
    errorContainer.classList.remove('hidden');
    stopStatusAnimation();
}

// Hide all result containers
function hideAll() {
    progressContainer.classList.add('hidden');
    resultContainer.classList.add('hidden');
    errorContainer.classList.add('hidden');
}

// Reset UI
function resetUI() {
    extractBtn.disabled = false;
    stopStatusAnimation();
}

// Allow Enter key to trigger extraction
youtubeUrl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        extractBtn.click();
    }
});
