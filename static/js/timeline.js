/**
 * Visual Timeline & Dual Slider Controller
 */

function secondsToFormatted(totalSec) {
  if (isNaN(totalSec) || totalSec < 0) totalSec = 0;
  const secNum = Math.floor(totalSec);
  const hours = Math.floor(secNum / 3600);
  const minutes = Math.floor((secNum % 3600) / 60);
  const seconds = secNum % 60;

  const pad = (num) => String(num).padStart(2, '0');

  if (hours > 0) {
    return `${pad(hours)}:${pad(minutes)}:${pad(seconds)}`;
  }
  return `${pad(minutes)}:${pad(seconds)}`;
}

function formattedToSeconds(str) {
  if (!str) return 0;
  const parts = str.trim().split(':').map(Number);
  if (parts.some(isNaN)) return 0;

  if (parts.length === 3) {
    return parts[0] * 3600 + parts[1] * 60 + parts[2];
  } else if (parts.length === 2) {
    return parts[0] * 60 + parts[1];
  } else if (parts.length === 1) {
    return parts[0];
  }
  return 0;
}

class TimelineController {
  constructor(options) {
    this.startRangeInput = document.getElementById(options.startRangeId);
    this.endRangeInput = document.getElementById(options.endRangeId);
    this.startTimeInput = document.getElementById(options.startTimeInputId);
    this.endTimeInput = document.getElementById(options.endTimeInputId);
    this.selectedRangeEl = document.getElementById(options.selectedRangeId);
    this.playheadEl = document.getElementById(options.playheadId);
    this.clipDurationEl = document.getElementById(options.clipDurationId);
    this.timelineTrack = document.getElementById(options.trackId);
    
    this.totalDuration = 100; // default max seconds
    this.onRangeChange = options.onRangeChange;

    this.initEvents();
  }

  setDuration(duration) {
    this.totalDuration = Math.max(1, duration);
    this.startRangeInput.max = this.totalDuration;
    this.endRangeInput.max = this.totalDuration;
    this.renderTimeMarkers();

    // Reset default start to 0 and end to total duration or 60s
    this.setStart(0);
    this.setEnd(Math.min(this.totalDuration, 60));
    this.updateUI();
  }

  getMarkerInterval() {
    if (this.totalDuration <= 60) return 5;
    if (this.totalDuration <= 300) return 15;
    if (this.totalDuration <= 900) return 30;
    if (this.totalDuration <= 3600) return 60;
    return Math.ceil(this.totalDuration / 12 / 60) * 60;
  }

  renderTimeMarkers() {
    if (!this.timelineTrack) return;

    const oldMarkers = this.timelineTrack.querySelector('.timeline-markers');
    if (oldMarkers) oldMarkers.remove();

    const markers = document.createElement('div');
    markers.className = 'timeline-markers';
    const interval = this.getMarkerInterval();

    for (let seconds = 0; seconds <= this.totalDuration; seconds += interval) {
      const marker = document.createElement('span');
      marker.className = 'timeline-marker';
      marker.style.left = `${(seconds / this.totalDuration) * 100}%`;
      if (seconds === 0 || seconds + interval >= this.totalDuration || seconds % (interval * 2) === 0) {
        marker.classList.add('major');
      }
      markers.appendChild(marker);
    }

    this.timelineTrack.appendChild(markers);
  }

  getStart() {
    return parseFloat(this.startRangeInput.value) || 0;
  }

  getEnd() {
    return parseFloat(this.endRangeInput.value) || this.totalDuration;
  }

  setStart(sec) {
    sec = Math.max(0, Math.min(sec, this.getEnd() - 1));
    this.startRangeInput.value = sec;
    this.startTimeInput.value = secondsToFormatted(sec);
    this.updateUI();
  }

  setEnd(sec) {
    sec = Math.max(this.getStart() + 1, Math.min(sec, this.totalDuration));
    this.endRangeInput.value = sec;
    this.endTimeInput.value = secondsToFormatted(sec);
    this.updateUI();
  }

  stepStart(delta) {
    this.setStart(this.getStart() + delta);
    if (this.onRangeChange) this.onRangeChange('start', this.getStart());
  }

  stepEnd(delta) {
    this.setEnd(this.getEnd() + delta);
    if (this.onRangeChange) this.onRangeChange('end', this.getEnd());
  }

  updatePlayhead(currentSec) {
    if (!this.totalDuration) return;
    const pct = Math.max(0, Math.min(100, (currentSec / this.totalDuration) * 100));
    if (this.playheadEl) {
      this.playheadEl.style.left = `${pct}%`;
    }
  }

  updateUI() {
    const startSec = this.getStart();
    const endSec = this.getEnd();

    // Update range bar highlight styling
    const startPct = (startSec / this.totalDuration) * 100;
    const endPct = (endSec / this.totalDuration) * 100;

    if (this.selectedRangeEl) {
      this.selectedRangeEl.style.left = `${startPct}%`;
      this.selectedRangeEl.style.width = `${endPct - startPct}%`;
    }

    // Update duration pill
    const diff = Math.max(0, endSec - startSec);
    if (this.clipDurationEl) {
      this.clipDurationEl.textContent = `Clip Length: ${secondsToFormatted(diff)} (${Math.round(diff)}s)`;
    }
  }

  initEvents() {
    // Slider Start knob input
    this.startRangeInput.addEventListener('input', () => {
      let val = parseFloat(this.startRangeInput.value);
      if (val >= this.getEnd()) {
        val = this.getEnd() - 1;
        this.startRangeInput.value = val;
      }
      this.startTimeInput.value = secondsToFormatted(val);
      this.updateUI();
      if (this.onRangeChange) this.onRangeChange('start', val);
    });

    // Slider End knob input
    this.endRangeInput.addEventListener('input', () => {
      let val = parseFloat(this.endRangeInput.value);
      if (val <= this.getStart()) {
        val = this.getStart() + 1;
        this.endRangeInput.value = val;
      }
      this.endTimeInput.value = secondsToFormatted(val);
      this.updateUI();
      if (this.onRangeChange) this.onRangeChange('end', val);
    });

    // Precision Text Input change
    this.startTimeInput.addEventListener('change', () => {
      const sec = formattedToSeconds(this.startTimeInput.value);
      this.setStart(sec);
      if (this.onRangeChange) this.onRangeChange('start', this.getStart());
    });

    this.endTimeInput.addEventListener('change', () => {
      const sec = formattedToSeconds(this.endTimeInput.value);
      this.setEnd(sec);
      if (this.onRangeChange) this.onRangeChange('end', this.getEnd());
    });
  }
}
