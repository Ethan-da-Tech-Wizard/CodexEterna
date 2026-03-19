"""
Entry point used by PyInstaller to create a standalone SportsService executable.
"""
import os
import sys

# When frozen by PyInstaller, add the bundle dir to the path
if getattr(sys, 'frozen', False):
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, log_level="info")
