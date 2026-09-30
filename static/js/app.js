/**
 * Main Application Orchestrator for YT Cuts
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const urlInput = document.getElementById('urlInput');
  const inspectBtn = document.getElementById('inspectBtn');
  const inspectBtnText = document.getElementById('inspectBtnText');

  const previewSection = document.getElementById('previewSection');
  const trimmerSection = document.getElementById('trimmerSection');
  const progressCard = document.getElementById('progressCard');

  const videoTitle = document.getElementById('videoTitle');
  const videoChannel = document.getElementById('videoChannel');
  const videoDurationText = document.getElementById('videoDurationText');
  const videoViewsText = document.getElementById('videoViewsText');
  const videoDescription = document.getElementById('videoDescription');

  const setStartCurBtn = document.getElementById('setStartCurBtn');
  const setEndCurBtn = document.getElementById('setEndCurBtn');
  const playSegmentBtn = document.getElementById('playSegmentBtn');

  const formatSelect = document.getElementById('formatSelect');
  const qualitySelect = document.getElementById('qualitySelect');
  const downloadBtn = document.getElementById('downloadBtn');

  const progressBadge = document.getElementById('progressBadge');
  const progressBarFill = document.getElementById('progressBarFill');
  const progressSpeed = document.getElementById('progressSpeed');
  const progressEta = document.getElementById('progressEta');
  const progressPct = document.getElementById('progressPct');
  const terminalConsole = document.getElementById('terminalConsole');
  const toggleTerminalBtn = document.getElementById('toggleTerminalBtn');
  const cancelDownloadBtn = document.getElementById('cancelDownloadBtn');

  const clipsGrid = document.getElementById('clipsGrid');
  const clipsCountBadge = document.getElementById('clipsCountBadge');
  const refreshClipsBtn = document.getElementById('refreshClipsBtn');
  const totalStorageDisplay = document.getElementById('totalStorageDisplay');
  const themeToggle = document.getElementById('themeToggle');

  // State
  let currentVideoMetadata = null;
  let activeEventSource = null;
  let activeTaskId = null;

  const savedTheme = localStorage.getItem('yt-cuts-theme') || 'dark';
  document.documentElement.dataset.theme = savedTheme;

  function updateThemeToggle() {
    const isLight = document.documentElement.dataset.theme === 'light';
    themeToggle.setAttribute('aria-pressed', String(isLight));
    themeToggle.setAttribute('aria-label', isLight ? 'Switch to dark mode' : 'Switch to light mode');
    themeToggle.querySelector('.theme-toggle-icon').textContent = isLight ? '☾' : '☼';
    themeToggle.querySelector('.theme-toggle-label').textContent = isLight ? 'Dark mode' : 'Light mode';
  }

  updateThemeToggle();
  themeToggle.addEventListener('click', () => {
    const nextTheme = document.documentElement.dataset.theme === 'light' ? 'dark' : 'light';
    document.documentElement.dataset.theme = nextTheme;
    localStorage.setItem('yt-cuts-theme', nextTheme);
    updateThemeToggle();
  });

  // Initialize YouTube Player Manager
  const ytPlayer = new YTPlayerManager('ytPlayerContainer', (currentTime) => {
    if (timeline) {
      timeline.updatePlayhead(currentTime);
    }
  }, null, (errorCode) => {
    ytPlayer.showFallback(currentVideoMetadata?.video_id);
    showToast(`YouTube preview unavailable for this video (error ${errorCode}).`, 'error');
  });

  // Initialize Timeline Controller
  const timeline = new TimelineController({
    startRangeId: 'startRange',
    endRangeId: 'endRange',
    trackId: 'timelineTrack',
    startTimeInputId: 'startTimeInput',
    endTimeInputId: 'endTimeInput',
    selectedRangeId: 'selectedRange',
    playheadId: 'timelinePlayhead',
    clipDurationId: 'clipDurationPill',
    onRangeChange: (type, seconds) => {
      ytPlayer.seekTo(seconds, true);
    }
  });

  // Load Clips Gallery on startup
  loadClipsGallery();

  // Toast Notification Helper
  function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 4000);
  }

  // Inspect Video Action
  async function handleInspectVideo() {
    const url = urlInput.value.trim();
    if (!url) {
      showToast('Please enter a valid YouTube video URL', 'error');
      return;
    }

    inspectBtn.disabled = true;
    inspectBtnText.textContent = 'Analyzing...';

    try {
      const data = await API.fetchVideoInfo(url);
      currentVideoMetadata = data;

      // Populate Video Metadata
      videoTitle.textContent = data.title;
      videoChannel.textContent = `📺 ${data.uploader}`;
      videoDurationText.textContent = secondsToFormatted(data.duration);
      videoViewsText.textContent = Number(data.view_count || 0).toLocaleString();
      videoDescription.textContent = data.description || '';

      // Populate Qualities dropdown
      qualitySelect.innerHTML = '<option value="best" selected>Best Available Quality</option>';
      if (data.available_qualities && data.available_qualities.length > 0) {
        data.available_qualities.forEach(h => {
          qualitySelect.innerHTML += `<option value="${h}">${h}p</option>`;
        });
      }

      // Show sections
      previewSection.style.display = 'grid';
      trimmerSection.style.display = 'flex';

      // Load YouTube Player & Set Timeline bounds
      ytPlayer.loadVideo(data.video_id);
      timeline.setDuration(data.duration);

      showToast('Video details loaded successfully!', 'success');

      // Smooth scroll to trimmer section
      trimmerSection.scrollIntoView({ behavior: 'smooth' });

    } catch (err) {
      showToast(err.message || 'Error fetching video info', 'error');
    } finally {
      inspectBtn.disabled = false;
      inspectBtnText.textContent = 'Inspect Video';
    }
  }

  inspectBtn.addEventListener('click', handleInspectVideo);
  urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') handleInspectVideo();
  });

  // Sample Chips
  document.querySelectorAll('.chip-btn[data-url]').forEach(chip => {
    chip.addEventListener('click', () => {
      urlInput.value = chip.getAttribute('data-url');
      handleInspectVideo();
    });
  });

  // Step buttons listener setup
  document.getElementById('startSub5').addEventListener('click', () => timeline.stepStart(-5));
  document.getElementById('startSub1').addEventListener('click', () => timeline.stepStart(-1));
  document.getElementById('startAdd1').addEventListener('click', () => timeline.stepStart(1));
  document.getElementById('startAdd5').addEventListener('click', () => timeline.stepStart(5));

  document.getElementById('endSub5').addEventListener('click', () => timeline.stepEnd(-5));
  document.getElementById('endSub1').addEventListener('click', () => timeline.stepEnd(-1));
  document.getElementById('endAdd1').addEventListener('click', () => timeline.stepEnd(1));
  document.getElementById('endAdd5').addEventListener('click', () => timeline.stepEnd(5));

  // Set Current Player Position buttons
  setStartCurBtn.addEventListener('click', () => {
    const cur = ytPlayer.getCurrentTime();
    timeline.setStart(cur);
    showToast(`Start set to ${secondsToFormatted(cur)}`, 'info');
  });

  setEndCurBtn.addEventListener('click', () => {
    const cur = ytPlayer.getCurrentTime();
    timeline.setEnd(cur);
    showToast(`End set to ${secondsToFormatted(cur)}`, 'info');
  });

  // Play Segment Preview
  playSegmentBtn.addEventListener('click', () => {
    const start = timeline.getStart();
    const end = timeline.getEnd();
    ytPlayer.playSegment(start, end);
    showToast(`Previewing clip from ${secondsToFormatted(start)} to ${secondsToFormatted(end)}`, 'info');
  });

  // Quick Presets
  document.getElementById('preset30s').addEventListener('click', () => {
    timeline.setStart(0);
    timeline.setEnd(30);
  });
  document.getElementById('preset1m').addEventListener('click', () => {
    timeline.setStart(0);
    timeline.setEnd(60);
  });
  document.getElementById('presetMid').addEventListener('click', () => {
    if (!currentVideoMetadata) return;
    const mid = currentVideoMetadata.duration / 2;
    timeline.setStart(Math.max(0, mid - 60));
    timeline.setEnd(Math.min(currentVideoMetadata.duration, mid + 60));
  });
  document.getElementById('presetFull').addEventListener('click', () => {
    if (!currentVideoMetadata) return;
    timeline.setStart(0);
    timeline.setEnd(currentVideoMetadata.duration);
  });

  // Format selection toggle
  formatSelect.addEventListener('change', () => {
    if (formatSelect.value === 'mp3') {
      qualitySelect.disabled = true;
    } else {
      qualitySelect.disabled = false;
    }
  });

  // Toggle Console Logs
  toggleTerminalBtn.addEventListener('click', () => {
    if (terminalConsole.style.display === 'none') {
      terminalConsole.style.display = 'flex';
      toggleTerminalBtn.textContent = 'Hide Console ▴';
    } else {
      terminalConsole.style.display = 'none';
      toggleTerminalBtn.textContent = 'Console Logs ▾';
    }
  });

  // Download Clip Action
  downloadBtn.addEventListener('click', async () => {
    const url = urlInput.value.trim();
    if (!url) {
      showToast('No video URL provided', 'error');
      return;
    }

    const payload = {
      url: url,
      start_time: document.getElementById('startTimeInput').value,
      end_time: document.getElementById('endTimeInput').value,
      quality: qualitySelect.value,
      output_format: formatSelect.value
    };

    downloadBtn.disabled = true;
    downloadBtn.textContent = '⏳ Preparing Download...';

    // Show Progress Card
    progressCard.style.display = 'flex';
    progressBadge.className = 'progress-status-badge downloading';
    progressBadge.textContent = 'Downloading';
    progressBarFill.style.width = '0%';
    progressPct.textContent = '0%';
    progressSpeed.textContent = '-';
    progressEta.textContent = '-';

    terminalConsole.innerHTML = '<div class="terminal-line" style="color: #64748b;">[System] Initiating yt-dlp section download...</div>';

    try {
      const res = await API.startDownload(payload);
      activeTaskId = res.task_id;
      cancelDownloadBtn.hidden = false;
      showToast('Download task started!', 'info');

      // Scroll to progress card
      progressCard.scrollIntoView({ behavior: 'smooth' });

      // Close previous SSE if any
      if (activeEventSource) activeEventSource.close();

      // Subscribe to real-time SSE stream
      activeEventSource = API.subscribeProgress(
        res.task_id,
        (data) => handleProgressUpdate(data),
        (err) => {
          showToast('Lost live logs connection. Polling fallback active.', 'error');
        }
      );

    } catch (err) {
      showToast(err.message || 'Failed to trigger download', 'error');
      downloadBtn.disabled = false;
      downloadBtn.textContent = '⚡ Download Trimmed Clip';
    }
  });

  cancelDownloadBtn.addEventListener('click', async () => {
    if (!activeTaskId) return;

    cancelDownloadBtn.disabled = true;
    cancelDownloadBtn.textContent = 'Stopping...';
    try {
      await API.cancelDownload(activeTaskId);
      showToast('Stopping download...', 'info');
    } catch (err) {
      cancelDownloadBtn.disabled = false;
      cancelDownloadBtn.textContent = 'Stop Download';
      showToast(err.message || 'Failed to stop download', 'error');
    }
  });

  function handleProgressUpdate(data) {
    if (data.progress !== undefined) {
      const pct = Math.round(data.progress);
      progressBarFill.style.width = `${pct}%`;
      progressPct.textContent = `${pct}%`;
    }

    if (data.speed) progressSpeed.textContent = data.speed;
    if (data.eta) progressEta.textContent = data.eta;

    if (data.logs && data.logs.length > 0) {
      data.logs.forEach(log => {
        const line = document.createElement('div');
        line.className = 'terminal-line';
        line.textContent = log;
        terminalConsole.appendChild(line);
      });
      terminalConsole.scrollTop = terminalConsole.scrollHeight;
    }

    if (data.status === 'merging') {
      progressBadge.textContent = 'Merging Streams';
      progressBadge.className = 'progress-status-badge downloading';
    } else if (data.status === 'completed') {
      progressBadge.textContent = 'Completed';
      progressBadge.className = 'progress-status-badge completed';
      progressBarFill.style.width = '100%';
      progressPct.textContent = '100%';

      downloadBtn.disabled = false;
      downloadBtn.textContent = '⚡ Download Trimmed Clip';
      cancelDownloadBtn.hidden = true;
      cancelDownloadBtn.disabled = false;
      cancelDownloadBtn.textContent = 'Stop Download';
      activeTaskId = null;

      showToast(`Clip saved as: ${data.filename || 'Clip'}`, 'success');
      loadClipsGallery();
    } else if (data.status === 'failed') {
      progressBadge.textContent = 'Failed';
      progressBadge.className = 'progress-status-badge failed';

      downloadBtn.disabled = false;
      downloadBtn.textContent = '⚡ Download Trimmed Clip';
      cancelDownloadBtn.hidden = true;
      cancelDownloadBtn.disabled = false;
      cancelDownloadBtn.textContent = 'Stop Download';
      activeTaskId = null;

      showToast(`Download failed: ${data.error || 'Unknown error'}`, 'error');
    } else if (data.status === 'cancelled') {
      progressBadge.textContent = 'Cancelled';
      progressBadge.className = 'progress-status-badge failed';
      downloadBtn.disabled = false;
      downloadBtn.textContent = '⚡ Download Trimmed Clip';
      cancelDownloadBtn.hidden = true;
      cancelDownloadBtn.disabled = false;
      cancelDownloadBtn.textContent = 'Stop Download';
      activeTaskId = null;
      showToast('Download cancelled.', 'info');
    }
  }

  // Load Downloaded Clips Gallery
  async function loadClipsGallery() {
    try {
      const data = await API.getFiles();
      clipsCountBadge.textContent = `${data.files.length} clip${data.files.length === 1 ? '' : 's'}`;
      totalStorageDisplay.textContent = data.total_storage;

      if (data.files.length === 0) {
        clipsGrid.innerHTML = `
          <div class="empty-state" style="grid-column: 1 / -1;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7 10 12 15 17 10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            <p>No clips downloaded yet. Trim a video section above to get started!</p>
          </div>
        `;
        return;
      }

      clipsGrid.innerHTML = '';
      data.files.forEach(file => {
        const card = document.createElement('div');
        card.className = 'clip-card';

        const safeUrl = escapeHtml(file.download_url);
        const safeFilename = escapeHtml(file.filename);
        const mediaTag = file.is_audio
          ? `<audio controls class="clip-media-preview" src="${safeUrl}"></audio>`
          : `<video controls class="clip-media-preview" src="${safeUrl}" preload="metadata"></video>`;

        const createdDate = new Date(file.created_at * 1000).toLocaleString();

        card.innerHTML = `
          <div>
            <h3 class="clip-title">${escapeHtml(file.filename)}</h3>
            <div class="clip-meta-row" style="margin-top: 0.5rem;">
              <span>📦 ${file.size_formatted}</span>
              <span>🕒 ${createdDate}</span>
            </div>
          </div>

          ${mediaTag}

          <div class="clip-actions">
            <a href="${safeUrl}" download="${safeFilename}" class="btn btn-secondary btn-sm" style="flex: 1; text-decoration: none;">
              ⬇ Save File
            </a>
            <button class="btn btn-danger btn-sm btn-icon-only delete-clip-btn" data-filename="${file.filename}" title="Delete Clip">
              🗑
            </button>
          </div>
        `;

        clipsGrid.appendChild(card);
      });

      // Bind delete buttons
      document.querySelectorAll('.delete-clip-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
          const fname = btn.getAttribute('data-filename');
          if (confirm(`Are you sure you want to delete '${fname}'?`)) {
            try {
              await API.deleteFile(fname);
              showToast(`Deleted ${fname}`, 'success');
              loadClipsGallery();
            } catch (err) {
              showToast(err.message || 'Failed to delete file', 'error');
            }
          }
        });
      });

    } catch (err) {
      console.error("Error loading clips gallery:", err);
    }
  }

  refreshClipsBtn.addEventListener('click', () => {
    loadClipsGallery();
    showToast('Refreshed clips gallery', 'info');
  });

  function escapeHtml(str) {
    return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }
});
