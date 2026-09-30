/**
 * API Service for YT Cuts Backend
 */
const API = {
  /**
   * Fetch metadata for a YouTube URL
   */
  async fetchVideoInfo(url) {
    const res = await fetch(`/api/info?url=${encodeURIComponent(url)}`);
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.detail || 'Failed to fetch video details.');
    }
    return data.data;
  },

  /**
   * Start clip download task
   */
  async startDownload(payload) {
    const res = await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.detail || 'Failed to start download task.');
    }
    return data;
  },

  async cancelDownload(taskId) {
    const res = await fetch(`/api/download/${encodeURIComponent(taskId)}/cancel`, {
      method: 'POST'
    });
    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.detail || 'Failed to stop download.');
    }
    return data;
  },

  /**
   * Subscribe to download progress stream via SSE
   */
  subscribeProgress(taskId, onMessage, onError) {
    const eventSource = new EventSource(`/api/download/progress/${taskId}`);
    
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
        if (['completed', 'failed', 'cancelled'].includes(data.status)) {
          eventSource.close();
        }
      } catch (err) {
        console.error("Failed to parse SSE payload:", err);
      }
    };

    eventSource.onerror = (err) => {
      console.error("SSE connection error:", err);
      if (onError) onError(err);
      eventSource.close();
    };

    return eventSource;
  },

  /**
   * List all files in downloads folder
   */
  async getFiles() {
    const res = await fetch('/api/files');
    if (!res.ok) throw new Error('Failed to retrieve clip list.');
    return await res.json();
  },

  async getSupportConfiguration() {
    const res = await fetch('/api/support');
    if (!res.ok) throw new Error('Failed to retrieve support link.');
    return await res.json();
  },

  /**
   * Delete a clip from downloads folder
   */
  async deleteFile(filename) {
    const res = await fetch(`/api/files/${encodeURIComponent(filename)}`, {
      method: 'DELETE'
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to delete file.');
    return data;
  }
};
