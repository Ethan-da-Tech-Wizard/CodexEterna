# How to Run CodexEterna

Two situations. Pick yours.

---

## Situation A — You want to share the app with someone (or run it yourself with no setup)

You need a single file: `CodexEterna.exe` (Windows) or `CodexEterna` (Mac/Linux).

Once you have that file:

1. Double-click it
2. A browser tab opens automatically — that's the app
3. Done

No installs. No terminal. No configuration.

> **Where do I get that file?**
> Either someone sends it to you, or you build it once yourself using Situation B below.

---

## Situation B — You want to build the app (one time, on your machine)

You only need **Python 3.11+** installed. That's it.

### Install Python (if you don't have it)

- Download from [python.org/downloads](https://python.org/downloads)
- **Windows:** tick **"Add Python to PATH"** during install
- Restart your computer after installing

### Build on Windows

1. Open the `CodexEterna` folder
2. Double-click **`build.bat`**
3. Watch it build (~2 minutes)
4. When it finishes, a `dist\` folder opens automatically
5. Your file is `dist\CodexEterna.exe`

### Build on Mac or Linux

1. Open Terminal in the `CodexEterna` folder
2. Run:
   ```
   chmod +x build.sh && ./build.sh
   ```
3. When it finishes, your file is `dist/CodexEterna`

---

## What you'll see when it's running

- **Left panel:** GPS coordinate pings counting up at 20,000/second
- **Right panel:** Live sports scores from ESPN
- Click **Pause** / **Resume** to control the ping stream
- Use the **Filters** sections to slice the data any way you want
- Select a sport and click **Fetch Latest** to pull current scores

---

That's it.
