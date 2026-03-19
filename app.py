"""
CodexEterna — Real-Time Data Pipeline
======================================
Single-file Python app.

• Generates 20,000 GPS coordinate pings per second, tracks counts
• Fetches live sports scores from ESPN
• Stores sports data in SQLite (in your home folder — persists across launches)
• Serves a live web dashboard; opens your browser automatically on launch

BUILD TO A STANDALONE EXE / BINARY (no Python needed on target machine):
  Windows :  double-click  build.bat
  Mac/Linux: run           ./build.sh
"""

import os
import sys
import time
import random
import sqlite3
import threading
import webbrowser
from datetime import datetime
from collections import defaultdict
from pathlib import Path

# ── find bundled assets when frozen by PyInstaller ───────────────────────────
def _res(*parts):
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return os.path.join(base, *parts)


# ── Flask + Socket.IO ─────────────────────────────────────────────────────────
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import requests as http_client

flask_app = Flask(
    __name__,
    template_folder=_res("templates"),
    static_folder=_res("static"),
)
flask_app.config["SECRET_KEY"] = "codex_eterna_secret"
socketio = SocketIO(flask_app, cors_allowed_origins="*", async_mode="threading")


# ── SQLite database (lives in user's home dir so it always persists) ──────────
DB_PATH = os.path.join(Path.home(), "codex_eterna.db")


def _db():
    return sqlite3.connect(DB_PATH)


def _init_db():
    con = _db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS games (
            game_id    TEXT PRIMARY KEY,
            league     TEXT,
            home_team  TEXT,
            away_team  TEXT,
            home_score INTEGER DEFAULT 0,
            away_score INTEGER DEFAULT 0,
            status     TEXT,
            date       TEXT,
            venue      TEXT,
            is_final   INTEGER DEFAULT 0,
            updated_at TEXT
        )
    """)
    con.commit()
    con.close()


# ── Coordinate ping state ─────────────────────────────────────────────────────
class _PingState:
    def __init__(self):
        self._counts = defaultdict(int)
        self._lock   = threading.Lock()
        self.paused  = False
        self.total   = 0
        self._start  = time.time()

    def record(self, lat, lon):
        key = f"{lat:.6f},{lon:.6f}"
        with self._lock:
            self._counts[key] += 1
            self.total += 1
            return key, self._counts[key]

    def top(self, n=100):
        with self._lock:
            items = sorted(self._counts.items(), key=lambda x: -x[1])
        return items[:n]

    def filter(self, min_lat=None, max_lat=None, min_lon=None, max_lon=None,
               min_count=None, max_count=None, hemisphere=None, limit=100):
        with self._lock:
            items = list(self._counts.items())

        result = []
        for key, cnt in items:
            lat_s, lon_s = key.split(",")
            lat, lon = float(lat_s), float(lon_s)
            if min_lat   is not None and lat < min_lat:   continue
            if max_lat   is not None and lat > max_lat:   continue
            if min_lon   is not None and lon < min_lon:   continue
            if max_lon   is not None and lon > max_lon:   continue
            if min_count is not None and cnt < min_count: continue
            if max_count is not None and cnt > max_count: continue
            if hemisphere:
                h = hemisphere.lower()
                if h == "north"     and lat <  0:           continue
                if h == "south"     and lat >= 0:           continue
                if h == "east"      and lon <  0:           continue
                if h == "west"      and lon >= 0:           continue
                if h == "northeast" and not (lat >= 0 and lon >= 0): continue
                if h == "northwest" and not (lat >= 0 and lon <  0): continue
                if h == "southeast" and not (lat <  0 and lon >= 0): continue
                if h == "southwest" and not (lat <  0 and lon <  0): continue
            result.append((key, cnt))

        result.sort(key=lambda x: -x[1])
        return result[:limit]

    def aggregate(self, group_by="hemisphere"):
        with self._lock:
            items = list(self._counts.items())

        stats = {}
        if group_by == "hemisphere":
            n = s = e = w = 0
            for key, _ in items:
                lat, lon = (float(x) for x in key.split(","))
                if lat >= 0: n += 1
                else:        s += 1
                if lon >= 0: e += 1
                else:        w += 1
            stats = {"North": n, "South": s, "East": e, "West": w}

        elif group_by == "quadrant":
            ne = nw = se = sw = 0
            for key, _ in items:
                lat, lon = (float(x) for x in key.split(","))
                if   lat >= 0 and lon >= 0: ne += 1
                elif lat >= 0 and lon <  0: nw += 1
                elif lat <  0 and lon >= 0: se += 1
                else:                       sw += 1
            stats = {"NE": ne, "NW": nw, "SE": se, "SW": sw}

        elif group_by == "count_range":
            buckets = {"1": 0, "2-5": 0, "6-10": 0, "11-50": 0, "51+": 0}
            for _, cnt in items:
                if   cnt == 1:           buckets["1"]     += 1
                elif cnt <= 5:           buckets["2-5"]   += 1
                elif cnt <= 10:          buckets["6-10"]  += 1
                elif cnt <= 50:          buckets["11-50"] += 1
                else:                    buckets["51+"]   += 1
            stats = buckets

        return stats

    def reset(self):
        with self._lock:
            self._counts.clear()
            self.total  = 0
            self._start = time.time()

    @property
    def unique(self):
        return len(self._counts)

    @property
    def rate(self):
        elapsed = max(time.time() - self._start, 0.001)
        return round(self.total / elapsed)

    @property
    def uptime(self):
        return int(time.time() - self._start)


ping = _PingState()


# ── Background ping generator ─────────────────────────────────────────────────
_TARGET   = 20_000   # pings / second
_BATCH    = 200      # generate in batches of 200
_EMIT_MS  = 0.10     # push to dashboard every 100 ms

def _ping_loop():
    sleep_per_batch = _BATCH / _TARGET
    pending = {}          # key -> latest count (accumulates between emits)
    last_emit = time.time()

    while True:
        if ping.paused:
            time.sleep(0.1)
            continue

        for _ in range(_BATCH):
            lat = round(random.uniform(-90,  90),  6)
            lon = round(random.uniform(-180, 180), 6)
            key, cnt = ping.record(lat, lon)
            pending[key] = cnt

        time.sleep(sleep_per_batch)

        now = time.time()
        if now - last_emit >= _EMIT_MS:
            socketio.emit("batch", list(pending.items()))
            socketio.emit("stats", {
                "total":  ping.total,
                "unique": ping.unique,
                "rate":   ping.rate,
                "paused": ping.paused,
                "uptime": ping.uptime,
            })
            pending.clear()
            last_emit = now


# ── ESPN sports helpers ───────────────────────────────────────────────────────
_LEAGUES = {
    "football/nfl":    ("football",    "nfl"),
    "basketball/nba":  ("basketball",  "nba"),
    "baseball/mlb":    ("baseball",    "mlb"),
    "hockey/nhl":      ("hockey",      "nhl"),
    "soccer/usa.1":    ("soccer",      "usa.1"),
    "basketball/wnba": ("basketball",  "wnba"),
}


def _fetch_espn(league):
    sport, code = _LEAGUES[league]
    url = (
        f"https://site.api.espn.com/apis/site/v2/sports"
        f"/{sport}/{code}/scoreboard"
    )
    resp = http_client.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    rows, created, updated = [], 0, 0
    for ev in data.get("events", []):
        comp  = ev.get("competitions", [{}])[0]
        teams = {c.get("homeAway"): c for c in comp.get("competitors", [])}
        home  = teams.get("home", {})
        away  = teams.get("away", {})

        row = (
            ev["id"],
            league,
            home.get("team", {}).get("displayName", "?"),
            away.get("team", {}).get("displayName", "?"),
            int(home.get("score", 0) or 0),
            int(away.get("score", 0) or 0),
            ev.get("status", {}).get("type", {}).get("description", "Unknown"),
            ev.get("date", ""),
            comp.get("venue", {}).get("fullName", ""),
            int(ev.get("status", {}).get("type", {}).get("completed", False)),
            datetime.utcnow().isoformat(),
        )

        con = _db()
        exists = con.execute(
            "SELECT 1 FROM games WHERE game_id=?", (ev["id"],)
        ).fetchone()

        if exists:
            con.execute(
                """UPDATE games
                   SET home_score=?,away_score=?,status=?,is_final=?,updated_at=?
                   WHERE game_id=?""",
                (row[4], row[5], row[6], row[9], row[10], ev["id"]),
            )
            updated += 1
        else:
            con.execute("INSERT INTO games VALUES (?,?,?,?,?,?,?,?,?,?,?)", row)
            created += 1

        con.commit()
        con.close()

    return created, updated


# ── HTTP routes ───────────────────────────────────────────────────────────────
@flask_app.route("/")
def index():
    return render_template("index.html")


# Ping controls
@flask_app.route("/api/ping/pause",  methods=["POST"])
def api_pause():
    ping.paused = True
    return jsonify({"status": "paused"})

@flask_app.route("/api/ping/resume", methods=["POST"])
def api_resume():
    ping.paused = False
    return jsonify({"status": "running"})

@flask_app.route("/api/ping/reset",  methods=["POST"])
def api_reset():
    ping.reset()
    return jsonify({"status": "reset"})

@flask_app.route("/api/ping/top")
def api_top():
    n = min(int(request.args.get("n", 100)), 1000)
    return jsonify([{"coord": k, "count": v} for k, v in ping.top(n)])

@flask_app.route("/api/ping/filter")
def api_filter():
    a = request.args
    def _f(k, cast): return cast(a[k]) if k in a else None
    results = ping.filter(
        min_lat=_f("minLat", float), max_lat=_f("maxLat", float),
        min_lon=_f("minLon", float), max_lon=_f("maxLon", float),
        min_count=_f("minCount", int), max_count=_f("maxCount", int),
        hemisphere=a.get("hemisphere"),
        limit=min(int(a.get("limit", 100)), 1000),
    )
    return jsonify([{"coord": k, "count": v} for k, v in results])

@flask_app.route("/api/ping/aggregate")
def api_aggregate():
    group_by = request.args.get("groupBy", "hemisphere")
    valid = {"hemisphere", "quadrant", "count_range"}
    if group_by not in valid:
        return jsonify({"error": f"groupBy must be one of {valid}"}), 400
    return jsonify({"groupBy": group_by, "stats": ping.aggregate(group_by)})

@flask_app.route("/api/ping/region/<region>")
def api_region(region):
    bounds = {
        "north_america": (-170, 15,  -50, 72),
        "south_america": ( -82,-56,  -34, 13),
        "europe":        ( -10, 36,   40, 71),
        "africa":        ( -18,-35,   52, 37),
        "asia":          (  25,-10,  180, 80),
        "oceania":       ( 110,-50,  180,  0),
    }
    if region not in bounds:
        return jsonify({"error": "unknown region"}), 400
    min_lon, min_lat, max_lon, max_lat = bounds[region]
    results = ping.filter(
        min_lat=min_lat, max_lat=max_lat,
        min_lon=min_lon, max_lon=max_lon,
        limit=int(request.args.get("limit", 100)),
    )
    return jsonify([{"coord": k, "count": v} for k, v in results])


# Sports data
@flask_app.route("/api/sports/fetch")
def api_sports_fetch():
    league = request.args.get("league", "")
    if league not in _LEAGUES:
        return jsonify({"error": "unknown league"}), 400
    try:
        created, updated = _fetch_espn(league)
        return jsonify({"success": True, "created": created, "updated": updated})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@flask_app.route("/api/sports/games")
def api_sports_games():
    a = request.args
    league   = a.get("league")
    is_final = a.get("is_final")
    status   = a.get("status")
    team     = a.get("team")
    sort_by  = a.get("sort_by", "updated_at")
    limit    = min(int(a.get("limit", 100)), 500)

    q      = "SELECT * FROM games"
    params = []
    where  = []

    if league:   where.append("league=?");              params.append(league)
    if is_final: where.append("is_final=?");            params.append(1 if is_final=="true" else 0)
    if status:   where.append("status LIKE ?");         params.append(f"%{status}%")
    if team:     where.append("(home_team LIKE ? OR away_team LIKE ?)"); params += [f"%{team}%"]*2

    if where:
        q += " WHERE " + " AND ".join(where)

    safe_sort = {"updated_at", "date", "home_score", "away_score"}
    q += f" ORDER BY {sort_by if sort_by in safe_sort else 'updated_at'} DESC LIMIT {limit}"

    con  = _db()
    rows = con.execute(q, params).fetchall()
    con.close()
    cols = ["game_id","league","home_team","away_team","home_score","away_score",
            "status","date","venue","is_final","updated_at"]
    return jsonify([dict(zip(cols, r)) for r in rows])

@flask_app.route("/api/sports/aggregate")
def api_sports_aggregate():
    group_by = request.args.get("group_by", "league")
    con = _db()
    if group_by == "league":
        rows = con.execute("SELECT league, COUNT(*) FROM games GROUP BY league").fetchall()
    elif group_by == "status":
        rows = con.execute("SELECT status, COUNT(*) FROM games GROUP BY status").fetchall()
    elif group_by == "final":
        rows = con.execute("SELECT is_final, COUNT(*) FROM games GROUP BY is_final").fetchall()
        rows = [("final" if r[0] else "live", r[1]) for r in rows]
    else:
        rows = []
    con.close()
    return jsonify({"group_by": group_by, "stats": dict(rows)})

@flask_app.route("/api/sports/high-scoring")
def api_high_scoring():
    threshold = int(request.args.get("threshold", 100))
    league    = request.args.get("league")
    limit     = min(int(request.args.get("limit", 50)), 500)
    q      = "SELECT * FROM games WHERE is_final=1"
    params = []
    if league:
        q += " AND league=?"; params.append(league)
    con  = _db()
    rows = con.execute(q, params).fetchall()
    con.close()
    cols = ["game_id","league","home_team","away_team","home_score","away_score",
            "status","date","venue","is_final","updated_at"]
    games = [dict(zip(cols, r)) for r in rows]
    games = [g for g in games if (g["home_score"] + g["away_score"]) >= threshold]
    games.sort(key=lambda g: -(g["home_score"] + g["away_score"]))
    return jsonify(games[:limit])

@flask_app.route("/api/sports/close-games")
def api_close_games():
    max_diff = int(request.args.get("max_diff", 5))
    league   = request.args.get("league")
    limit    = min(int(request.args.get("limit", 50)), 500)
    q      = "SELECT * FROM games WHERE is_final=1"
    params = []
    if league:
        q += " AND league=?"; params.append(league)
    con  = _db()
    rows = con.execute(q, params).fetchall()
    con.close()
    cols = ["game_id","league","home_team","away_team","home_score","away_score",
            "status","date","venue","is_final","updated_at"]
    games = [dict(zip(cols, r)) for r in rows]
    games = [g for g in games if abs(g["home_score"] - g["away_score"]) <= max_diff]
    games.sort(key=lambda g: abs(g["home_score"] - g["away_score"]))
    return jsonify(games[:limit])

@flask_app.route("/health")
def health():
    return jsonify({"status": "ok"})


# ── Launch ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    _init_db()

    # Start ping generator on a daemon thread
    threading.Thread(target=_ping_loop, daemon=True).start()

    # Open the browser half a second after the server starts
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:7890")).start()

    print("=" * 50)
    print("  CodexEterna is running!")
    print("  Dashboard → http://localhost:7890")
    print("  Press Ctrl+C to quit")
    print("=" * 50)

    socketio.run(
        flask_app,
        host="127.0.0.1",
        port=7890,
        debug=False,
        allow_unsafe_werkzeug=True,
        use_reloader=False,
    )
