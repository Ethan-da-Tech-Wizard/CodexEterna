const { contextBridge, ipcRenderer } = require('electron');

// Expose a safe API to the renderer (dashboard)
contextBridge.exposeInMainWorld('electronAPI', {
  getConfig: () => ipcRenderer.invoke('get-config'),
  platform: process.platform,
});
