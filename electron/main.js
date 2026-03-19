const { app, BrowserWindow, Menu, shell, dialog, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');
const net = require('net');
const fs = require('fs');

// ─── Child processes ────────────────────────────────────────────────────────
let pingProcess = null;
let sportsProcess = null;
let mainWindow = null;

const PING_PORT = 5000;
const SPORTS_PORT = 5001;

// ─── Helpers ────────────────────────────────────────────────────────────────

/** Check whether a TCP port is free */
function isPortFree(port) {
  return new Promise((resolve) => {
    const tester = net.createServer()
      .once('error', () => resolve(false))
      .once('listening', () => tester.close(() => resolve(true)))
      .listen(port, '127.0.0.1');
  });
}

/** Poll a URL until it responds or we time out */
function waitForUrl(url, timeoutMs = 30000) {
  const http = require('http');
  const start = Date.now();
  return new Promise((resolve, reject) => {
    const attempt = () => {
      http.get(url, (res) => {
        if (res.statusCode < 500) return resolve();
        retry();
      }).on('error', retry);
    };
    const retry = () => {
      if (Date.now() - start > timeoutMs) return reject(new Error(`Timeout waiting for ${url}`));
      setTimeout(attempt, 500);
    };
    attempt();
  });
}

/** Resolve the path to a bundled resource */
function resourcePath(...parts) {
  // In production the app is packaged; in dev we fall back to project root
  if (app.isPackaged) {
    return path.join(process.resourcesPath, ...parts);
  }
  return path.join(__dirname, '..', ...parts);
}

// ─── Start the C# PingService ───────────────────────────────────────────────
function startPingService() {
  return new Promise((resolve, reject) => {
    const isWin = process.platform === 'win32';
    const exe = resourcePath('PingService', isWin ? 'PingService.exe' : 'PingService');

    if (!fs.existsSync(exe)) {
      // Dev mode — expect the service to already be running or skip
      console.warn('[PingService] Executable not found at', exe, '— assuming dev mode');
      return resolve();
    }

    console.log('[PingService] Starting:', exe);
    pingProcess = spawn(exe, [], {
      env: {
        ...process.env,
        ASPNETCORE_URLS: `http://localhost:${PING_PORT}`,
        ASPNETCORE_ENVIRONMENT: 'Production',
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    pingProcess.stdout.on('data', (d) => process.stdout.write(`[PingService] ${d}`));
    pingProcess.stderr.on('data', (d) => process.stderr.write(`[PingService] ${d}`));
    pingProcess.on('error', reject);
    pingProcess.on('exit', (code) => {
      if (code && code !== 0) console.error(`[PingService] Exited with code ${code}`);
    });

    // Wait until the HTTP server is accepting connections
    waitForUrl(`http://localhost:${PING_PORT}/api/ping/health`)
      .then(resolve)
      .catch(reject);
  });
}

// ─── Start the Python SportsService ─────────────────────────────────────────
function startSportsService() {
  return new Promise((resolve, reject) => {
    const isWin = process.platform === 'win32';
    const exe = resourcePath('SportsService', isWin ? 'SportsService.exe' : 'SportsService');

    // DB lives in the user's app-data folder so it persists between launches
    const userDataDir = app.getPath('userData');
    const dbPath = path.join(userDataDir, 'sportsdata.db');

    if (!fs.existsSync(exe)) {
      console.warn('[SportsService] Executable not found at', exe, '— assuming dev mode');
      return resolve();
    }

    console.log('[SportsService] Starting:', exe);
    sportsProcess = spawn(exe, [], {
      env: {
        ...process.env,
        DATABASE_URL: `sqlite:///${dbPath}`,
        PORT: String(SPORTS_PORT),
      },
      stdio: ['ignore', 'pipe', 'pipe'],
    });

    sportsProcess.stdout.on('data', (d) => process.stdout.write(`[SportsService] ${d}`));
    sportsProcess.stderr.on('data', (d) => process.stderr.write(`[SportsService] ${d}`));
    sportsProcess.on('error', reject);
    sportsProcess.on('exit', (code) => {
      if (code && code !== 0) console.error(`[SportsService] Exited with code ${code}`);
    });

    waitForUrl(`http://localhost:${SPORTS_PORT}/health`)
      .then(resolve)
      .catch(reject);
  });
}

// ─── Kill child processes ────────────────────────────────────────────────────
function stopServices() {
  if (pingProcess)   { pingProcess.kill();   pingProcess = null; }
  if (sportsProcess) { sportsProcess.kill(); sportsProcess = null; }
}

// ─── Loading / splash window ─────────────────────────────────────────────────
function createLoadingWindow() {
  const win = new BrowserWindow({
    width: 480,
    height: 300,
    frame: false,
    resizable: false,
    center: true,
    backgroundColor: '#111827',
    webPreferences: { contextIsolation: true },
  });

  win.loadURL(`data:text/html,
    <html>
    <head><style>
      body { margin:0; background:#111827; color:#f9fafb;
             font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
             display:flex; flex-direction:column; align-items:center;
             justify-content:center; height:100vh; }
      h2  { font-size:1.6rem; margin-bottom:0.4rem; background:linear-gradient(135deg,#60a5fa,#a78bfa);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
      p   { color:#9ca3af; font-size:0.95rem; }
      .bar-wrap { width:260px; height:6px; background:#374151; border-radius:3px; margin-top:1.4rem; overflow:hidden; }
      .bar      { height:100%; width:30%; background:linear-gradient(90deg,#2563eb,#7c3aed);
                  border-radius:3px; animation:slide 1.4s ease-in-out infinite; }
      @keyframes slide { 0%{margin-left:0}50%{margin-left:70%}100%{margin-left:0} }
    </style></head>
    <body>
      <h2>CodexEterna</h2>
      <p>Starting services, please wait…</p>
      <div class="bar-wrap"><div class="bar"></div></div>
    </body>
    </html>
  `);
  return win;
}

// ─── Main application window ─────────────────────────────────────────────────
function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1600,
    height: 960,
    minWidth: 1200,
    minHeight: 700,
    title: 'CodexEterna — Real-Time Data Pipeline',
    backgroundColor: '#111827',
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  mainWindow.loadURL(`http://localhost:${PING_PORT}`);

  mainWindow.once('ready-to-show', () => mainWindow.show());

  mainWindow.on('closed', () => { mainWindow = null; });

  // Build the application menu
  const menu = Menu.buildFromTemplate([
    {
      label: 'CodexEterna',
      submenu: [
        { label: 'About CodexEterna', role: 'about' },
        { type: 'separator' },
        { label: 'Quit', accelerator: 'CmdOrCtrl+Q', click: () => app.quit() },
      ],
    },
    {
      label: 'View',
      submenu: [
        { label: 'Reload', accelerator: 'CmdOrCtrl+R', click: () => mainWindow?.reload() },
        { label: 'Toggle DevTools', accelerator: 'CmdOrCtrl+Shift+I', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: 'Actual Size', role: 'resetZoom' },
        { label: 'Zoom In', role: 'zoomIn' },
        { label: 'Zoom Out', role: 'zoomOut' },
        { type: 'separator' },
        { label: 'Fullscreen', role: 'togglefullscreen' },
      ],
    },
    {
      label: 'Data',
      submenu: [
        {
          label: 'Pause Ping Stream',
          accelerator: 'CmdOrCtrl+P',
          click: () => mainWindow?.webContents.executeJavaScript('togglePause && togglePause()'),
        },
        {
          label: 'Reset Ping Data',
          click: () => mainWindow?.webContents.executeJavaScript('resetSystem && resetSystem()'),
        },
        { type: 'separator' },
        {
          label: 'Open Ping API Docs',
          click: () => shell.openExternal(`http://localhost:${PING_PORT}/swagger`),
        },
        {
          label: 'Open Sports API Docs',
          click: () => shell.openExternal(`http://localhost:${SPORTS_PORT}/docs`),
        },
      ],
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'View Logs',
          click: () => shell.openPath(app.getPath('logs')),
        },
        {
          label: 'Open Data Folder',
          click: () => shell.openPath(app.getPath('userData')),
        },
      ],
    },
  ]);
  Menu.setApplicationMenu(menu);

  return mainWindow;
}

// ─── App lifecycle ───────────────────────────────────────────────────────────
app.whenReady().then(async () => {
  // Check ports are free
  const [pingFree, sportsFree] = await Promise.all([
    isPortFree(PING_PORT),
    isPortFree(SPORTS_PORT),
  ]);

  if (!pingFree || !sportsFree) {
    dialog.showErrorBox(
      'Port Conflict',
      `Port ${!pingFree ? PING_PORT : SPORTS_PORT} is already in use.\n\n` +
      'Please close the other application using that port and try again.'
    );
    app.quit();
    return;
  }

  const loadingWin = createLoadingWindow();

  try {
    // Start both services in parallel
    await Promise.all([startPingService(), startSportsService()]);
  } catch (err) {
    loadingWin.close();
    dialog.showErrorBox('Startup Failed', `A service failed to start:\n\n${err.message}`);
    stopServices();
    app.quit();
    return;
  }

  // Services are up — open the real window
  loadingWin.close();
  createMainWindow();
});

app.on('window-all-closed', () => {
  stopServices();
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createMainWindow();
});

app.on('before-quit', stopServices);

// ─── IPC from renderer (optional helpers) ───────────────────────────────────
ipcMain.handle('get-config', () => ({
  pingPort: PING_PORT,
  sportsPort: SPORTS_PORT,
}));
