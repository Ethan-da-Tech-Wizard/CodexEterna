# HOW TO RUN THIS - SUPER SIMPLE VERSION

Follow these steps EXACTLY. Don't skip any step.

---

## PART 1: Install Docker (ONE TIME ONLY)

### If you're on Windows:

1. Go to this website: https://www.docker.com/products/docker-desktop/
2. Click the big blue "Download for Windows" button
3. Run the file you downloaded (Docker Desktop Installer.exe)
4. Click "OK" or "Next" on everything
5. When it says "restart", restart your computer
6. After restart, open Docker Desktop from your Start Menu
7. Wait for it to say "Docker Desktop is running" (bottom left corner)

### If you're on Mac:

1. Go to this website: https://www.docker.com/products/docker-desktop/
2. Click "Download for Mac"
3. Open the file you downloaded
4. Drag Docker to your Applications folder
5. Open Docker from Applications
6. Click "Open" if it asks for permission
7. Wait for the whale icon in the top menu bar to stop moving

### Check Docker is Working:

**Windows:** Open Command Prompt (search "cmd" in Start Menu)
**Mac:** Open Terminal (search "terminal" in Spotlight)

Type this and press Enter:
```
docker --version
```

You should see something like "Docker version 24.0.6"

✅ If you see a version number, Docker is ready. Move to Part 2.
❌ If you see an error, make sure Docker Desktop is open and running.

---

## PART 2: Get the Code

### Option A: Download as ZIP (EASIEST - NO GIT NEEDED)

1. Go to: https://github.com/Ethan-da-Tech-Wizard/CodexEterna
2. Click the green "Code" button
3. Click "Download ZIP"
4. Unzip the file to your Desktop or Documents
5. Open the folder you just unzipped
6. **IMPORTANT:** Make sure you see these folders inside:
   - PingService
   - SportsService
   - docker-compose.yml file

**Now go to PART 3**

---

### Option B: Use Git (If you have it installed)

**Windows:** Open Command Prompt
**Mac:** Open Terminal

Type these commands EXACTLY (press Enter after each line):

```bash
cd Desktop
git clone https://github.com/Ethan-da-Tech-Wizard/CodexEterna.git
cd CodexEterna
git checkout claude/hybrid-data-pipeline-design-0Ekw7
```

**Now go to PART 3**

---

## PART 3: Start the System

### Step 1: Open Terminal/Command Prompt in the Right Place

**Windows:**
1. Open the CodexEterna folder (the one you unzipped or cloned)
2. Hold Shift, then RIGHT-CLICK on empty space in the folder
3. Click "Open PowerShell window here" or "Open Command Prompt here"

**Mac:**
1. Open Terminal
2. Type `cd ` (with a space after cd)
3. Drag the CodexEterna folder into the Terminal window
4. Press Enter

### Step 2: Check You're in the Right Place

Type this and press Enter:
```bash
dir
```
(On Mac, type `ls` instead)

You should see:
- PingService
- SportsService
- docker-compose.yml
- README.md

✅ If you see these, you're in the right place!
❌ If not, you're in the wrong folder. Go back to Step 1.

### Step 3: Start Everything

Type this EXACT command and press Enter:

```bash
docker-compose up --build
```

**What happens next:**
- You'll see LOTS of text scrolling
- It will download and build things (first time takes 5-10 minutes)
- **DON'T CLOSE THIS WINDOW!** Keep it open.

### Step 4: Wait for This Message

Keep watching the scrolling text. Wait until you see something like this:

```
pingservice     | Now listening on: http://[::]:5000
sportsservice   | INFO: Application startup complete
```

When you see that, IT'S READY! ✅

---

## PART 4: Open the Dashboard

1. Open your web browser (Chrome, Firefox, Edge, Safari)
2. In the address bar, type exactly:
   ```
   http://localhost:5000
   ```
3. Press Enter

**YOU SHOULD SEE THE DASHBOARD!** 🎉

You'll see:
- Numbers counting up very fast (Total Pings, Pings/Second, etc.)
- A table with coordinates and counts
- Sports data controls on the right

---

## PART 5: Try It Out

### Test the Coordinate Pings:

1. Watch the "Total Pings" number - it should be going up VERY fast
2. Watch "Pings/Second" - should be around 20,000
3. Click the yellow "Pause" button - numbers should STOP
4. Click "Resume" - numbers should START again
5. Click "Top 100" - table shows most frequent coordinates

### Test the Sports Data:

1. On the right side, click the dropdown that says "Choose a sport..."
2. Select "NFL Football"
3. Click the green "Fetch Latest" button
4. Wait 3 seconds
5. You should see game cards appear with scores!

---

## PART 6: Stop the System

When you're done:

1. Go back to the Terminal/Command Prompt window (the one with all the scrolling text)
2. Press `Ctrl+C` on your keyboard
3. Wait for it to stop (might take 10 seconds)
4. Type this and press Enter:
   ```bash
   docker-compose down
   ```

The system is now stopped.

---

## 🆘 PROBLEMS?

### Problem: "Port 5000 is already in use"

**Solution:**
1. Stop the system (Ctrl+C)
2. Open this file: `docker-compose.yml`
3. Find the line that says `"5000:5000"`
4. Change it to `"5001:5000"`
5. Save the file
6. Try starting again (docker-compose up --build)
7. Open `http://localhost:5001` instead

### Problem: "Cannot connect to Docker"

**Solution:**
1. Make sure Docker Desktop is open and running
2. Look for the whale icon (Windows: system tray, Mac: menu bar)
3. Click it - it should say "Docker Desktop is running"
4. If not, wait 1-2 minutes for Docker to start
5. Try again

### Problem: Dashboard shows "Connection Failed"

**Solution:**
1. Wait 30 more seconds - services might still be starting
2. Refresh the browser page (F5 or Cmd+R)
3. Check the Terminal - make sure you saw the "Now listening" message
4. If still not working:
   - Stop everything (Ctrl+C)
   - Type: `docker-compose down -v`
   - Wait for it to finish
   - Start again: `docker-compose up --build`

### Problem: "No games found" for sports data

**Solution:**
1. This is normal if there are no games today for that sport
2. Try a different sport (NBA usually has more games)
3. Or try MLB, NHL, or MLS
4. If NOTHING works, ESPN's API might be temporarily down - try again in 10 minutes

---

## 📋 QUICK REFERENCE

**Start the system:**
```bash
cd CodexEterna
docker-compose up --build
```

**Open dashboard:**
```
http://localhost:5000
```

**Stop the system:**
```
Ctrl+C
docker-compose down
```

**Start again (faster next time):**
```bash
docker-compose up
```
(No --build needed after first time)

---

## ✅ THAT'S IT!

If you followed these steps exactly, you should now have:
- ✅ A dashboard showing 20,000 coordinates/second
- ✅ Live sports data from ESPN
- ✅ A fully working real-time data pipeline

**Need help?** Check the Terminal/Command Prompt for error messages.

🎉 **Enjoy your demo!**
