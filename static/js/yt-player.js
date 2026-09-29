/**
 * YouTube IFrame Player Wrapper & Event Dispatcher
 */
class YTPlayerManager {
  constructor(containerId, onTimeUpdate, onReady, onError) {
    this.containerId = containerId;
    this.player = null;
    this.onTimeUpdate = onTimeUpdate;
    this.onReady = onReady;
    this.onError = onError;
    this.updateInterval = null;
    this.clipEndBoundary = null;
    this.isAPIReady = false;

    this.initAPI();
  }

  initAPI() {
    if (window.YT && window.YT.Player) {
      this.isAPIReady = true;
    } else {
      const tag = document.createElement('script');
      tag.src = "https://www.youtube.com/iframe_api";
      const firstScriptTag = document.getElementsByTagName('script')[0];
      firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

      window.onYouTubeIframeAPIReady = () => {
        this.isAPIReady = true;
      };
    }
  }

  loadVideo(videoId) {
    if (!videoId) return;

    const createOrLoad = () => {
      if (this.player) {
        this.player.loadVideoById(videoId);
      } else {
        this.player = new YT.Player(this.containerId, {
          height: '100%',
          width: '100%',
          videoId: videoId,
          playerVars: {
            'autoplay': 0,
            'controls': 1,
            'modestbranding': 1,
            'rel': 0,
            'playsinline': 1,
            'origin': window.location.origin
          },
          events: {
            'onReady': () => {
              this.startTimer();
              if (this.onReady) this.onReady();
            },
            'onStateChange': (e) => this.handleStateChange(e),
            'onError': (e) => {
              if (this.onError) this.onError(e.data);
            }
          }
        });
      }
    };

    if (this.isAPIReady || (window.YT && window.YT.Player)) {
      createOrLoad();
    } else {
      const checkInterval = setInterval(() => {
        if (window.YT && window.YT.Player) {
          clearInterval(checkInterval);
          this.isAPIReady = true;
          createOrLoad();
        }
      }, 100);
    }
  }

  showFallback(videoId) {
    const container = document.getElementById(this.containerId);
    if (!container || !videoId) return;

    this.stopTimer();
    const thumbnailUrl = `https://img.youtube.com/vi/${encodeURIComponent(videoId)}/hqdefault.jpg`;
    const videoUrl = `https://www.youtube.com/watch?v=${encodeURIComponent(videoId)}`;
    container.innerHTML = `
      <div class="yt-player-fallback">
        <img src="${thumbnailUrl}" alt="YouTube video thumbnail">
        <div class="yt-player-fallback-content">
          <strong>Preview unavailable</strong>
          <a href="${videoUrl}" target="_blank" rel="noopener">Open this video on YouTube</a>
        </div>
      </div>`;
  }

  getCurrentTime() {
    if (this.player && typeof this.player.getCurrentTime === 'function') {
      return this.player.getCurrentTime() || 0;
    }
    return 0;
  }

  seekTo(seconds, allowSeekAhead = true) {
    if (this.player && typeof this.player.seekTo === 'function') {
      this.player.seekTo(seconds, allowSeekAhead);
    }
  }

  playSegment(startTime, endTime) {
    if (this.player) {
      this.clipEndBoundary = endTime;
      this.seekTo(startTime, true);
      this.player.playVideo();
    }
  }

  pause() {
    if (this.player && typeof this.player.pauseVideo === 'function') {
      this.player.pauseVideo();
    }
  }

  handleStateChange(event) {
    // YT.PlayerState.PLAYING is 1
    if (event.data === 1) {
      this.startTimer();
    } else {
      this.stopTimer();
    }
  }

  startTimer() {
    this.stopTimer();
    this.updateInterval = setInterval(() => {
      const curTime = this.getCurrentTime();
      
      // Auto pause if reached end boundary during segment play
      if (this.clipEndBoundary !== null && curTime >= this.clipEndBoundary) {
        this.pause();
        this.clipEndBoundary = null;
      }

      if (this.onTimeUpdate) {
        this.onTimeUpdate(curTime);
      }
    }, 150);
  }

  stopTimer() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }
}
