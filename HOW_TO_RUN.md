# How to Run CodexEterna

---

## Running the app

You need one file:

| Platform | File |
|----------|------|
| Mac      | `CodexEterna.app` |
| Windows  | `CodexEterna.exe` |

**Double-click it. Your browser opens. The app is running.**

That's it. No installs, no terminal, no setup — on your machine or anyone else's.
You can copy the file to your Desktop, AirDrop it to a friend, email it, share it via USB.
Whoever has the file just double-clicks it.

---

## Don't have the file yet? Build it once.

Someone on a dev machine runs the build script once to produce the file above.
That machine needs Python 3.11+ installed — [python.org/downloads](https://python.org/downloads)
(tick **Add to PATH** on Windows during install).

### On Mac

Open Terminal inside the CodexEterna folder and run:

```
chmod +x build.sh && ./build.sh
```

Output: `dist/CodexEterna.app` — copy this to wherever you want.

### On Windows

Double-click **`build.bat`** inside the CodexEterna folder.

Output: `dist\CodexEterna.exe` — copy this to wherever you want.

---

## What the app does

- **Left panel:** GPS coordinate pings at 20,000/second — pause, resume, filter by hemisphere or region
- **Right panel:** Live sports scores from ESPN — filter by score range, close games, high-scoring games
- Click **Fetch Latest** (right panel) to pull fresh sports data