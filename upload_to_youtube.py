#!/usr/bin/env python3
"""
Uploads both instructional videos (`modular_couch_beginner_video.mp4` and
`modular_couch_instructional_video.mp4`) to YouTube as Unlisted.
Reads/stores YouTube OAuth credentials (`YOUTUBE_CLIENT_ID`, `YOUTUBE_CLIENT_SECRET`,
`YOUTUBE_REFRESH_TOKEN`) in the git-ignored `.env` file.
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
VIDEO_BUILD_DIR = os.path.join(BASE_DIR, ".video_build")
os.makedirs(VIDEO_BUILD_DIR, exist_ok=True)
RESULTS_PATH = os.path.join(VIDEO_BUILD_DIR, "youtube_upload_results.json")

QUOTA_PROJECT = "gws-mcp-alex-130626"
REDIRECT_URI = "https://antigravity.google/oauth-callback"
SCOPE = "https://www.googleapis.com/auth/youtube.upload"
LOGIN_HINT = "alexander.macintosh@gmail.com"

GITHUB_REPO_URL = "https://github.com/armacintosh/bench-build"
HTML_GUIDE_LIVE_URL = "https://armacintosh.github.io/bench-build/modular_couch_build_guide.html"
HTML_GUIDE_SOURCE_URL = "https://github.com/armacintosh/bench-build/blob/main/modular_couch_build_guide.html"


VIDEOS_TO_UPLOAD = [
    {
        "key": "beginner",
        "file": os.path.join(BASE_DIR, "modular_couch_beginner_video.mp4"),
        "title": "How to Build an 80\" Modular Playroom Couch, Bench & Table (Beginner 3D DIY Guide)",
        "description": (
            "Step-by-step beginner 3D DIY build guide for an 80\" × 29\" modular playroom couch, bench, and table.\n\n"
            "📐 Interactive 3D CAD Build Guide & Cut Lists (HTML Instructions):\n"
            f"👉 {HTML_GUIDE_LIVE_URL}\n\n"
            "💻 GitHub Repository (Blueprints, Cut Maps, Specs & Source Files):\n"
            f"👉 {GITHUB_REPO_URL}\n"
            f"👉 HTML File in Repo: {HTML_GUIDE_SOURCE_URL}\n\n"
            "🛠️ Tools Needed:\n"
            "• Circular saw, cordless drill/driver, wood chisel, pocket-hole jig, bar clamps, orbital sander, tape measure\n\n"
            "⏱️ Chapters:\n"
            "00:00 Overview & Tools Needed\n"
            "00:13 Measure & Cut Your Wood\n"
            "00:33 Step 1: Prep the Five 4×4 Legs (Wheels, Pads & Top Notches)\n"
            "00:52 Step 2: Attach the Front & Back Beams\n"
            "01:18 Step 3: Add Cross Boards & 4 Backrest Slots\n"
            "01:46 Step 4: Screw Down the 3/4\" Plywood Seat\n"
            "02:05 Step 5: Attach the Outer 1×6 Trim Boards (1\" Cushion Lip)\n"
            "02:26 Step 6: Build the Two Drop-In Backrests\n"
            "02:50 Step 7: Sand, Wax Tenons & Drop In the Cushions\n"
        ),
        "tags": ["DIY Furniture", "Woodworking", "Modular Couch", "Playroom Bench", "3D CAD Guide"],
    },
    {
        "key": "detailed",
        "file": os.path.join(BASE_DIR, "modular_couch_instructional_video.mp4"),
        "title": "80\" × 29\" Modular Playroom Couch, Bench & Table — Full 3D CAD & Blueprint Walkthrough",
        "description": (
            "Complete 7-phase engineering, orthographic blueprint, and 3D CAD assembly walkthrough for the 80\" × 29\" "
            "heavy-duty modular playroom couch, bench, and activity table (1,000+ lb dynamic capacity).\n\n"
            "📐 Interactive 3D CAD Build Guide, Cut Lists & Printable Blueprints (HTML Instructions):\n"
            f"👉 {HTML_GUIDE_LIVE_URL}\n\n"
            "💻 GitHub Repository (Full Specification, CAD Generator & Blueprints):\n"
            f"👉 {GITHUB_REPO_URL}\n"
            f"👉 HTML File in Repo: {HTML_GUIDE_SOURCE_URL}\n\n"
            "🎥 Simplified Beginner 3D DIY Video:\n"
            "👉 https://youtu.be/gW_k-L_8o7U\n\n"
            "⏱️ Chapters:\n"
            "00:00 Overview & Coplanar Torsion-Box Specs\n"
            "00:25 Master Cut Maps & Material Layout (Parts A–M)\n"
            "00:50 Phase 1: Prepping the Five Notched 4×4 Legs & Rollers\n"
            "01:20 Phase 2: Laminating the Front Beam & Perimeter Portals\n"
            "01:48 Phase 3: Ladder Joist Grid & Captive Mortise Sleeves\n"
            "02:20 Phase 4: Installing the 3/4\" Birch Plywood Torsion Deck\n"
            "02:49 Phase 5: Blind-Fastened 1×6 Stain-Grade Apron Trim\n"
            "03:17 Phase 6: Building the Two 40\" Slanted Drop-In Backrests\n"
            "03:41 Phase 7: Finishing, Waxing Tenons & Table Conversion\n"
        ),
        "tags": ["Woodworking Plans", "3D CAD", "Furniture Engineering", "DIY Couch", "Modular Bench"],
    },
]


def load_env_dict() -> dict[str, str]:
    env = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip()
                if s and not s.startswith("#") and "=" in s:
                    k, v = s.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def upsert_env_vars(updates: dict[str, str]):
    lines = []
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

    existing_keys = set()
    new_lines = []
    for line in lines:
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            k = s.split("=", 1)[0].strip()
            if k in updates:
                new_lines.append(f"{k}={updates[k]}")
                existing_keys.add(k)
                continue
        new_lines.append(line)

    for k, v in updates.items():
        if k not in existing_keys:
            new_lines.append(f"{k}={v}")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")


def extract_code_from_text(txt: str) -> str | None:
    txt = txt.strip()
    if "code=" in txt:
        parsed = urllib.parse.urlparse(txt)
        qs = urllib.parse.parse_qs(parsed.query)
        if "code" in qs:
            return qs["code"][0]
    if txt.startswith("4/") and len(txt) > 20 and " " not in txt and "\n" not in txt:
        return txt
    return None


def get_oauth_token() -> str:
    env = load_env_dict()
    client_id = env.get("YOUTUBE_CLIENT_ID", "")
    client_secret = env.get("YOUTUBE_CLIENT_SECRET", "")
    refresh_token = env.get("YOUTUBE_REFRESH_TOKEN", "")

    if not client_id or not client_secret:
        raise RuntimeError("YOUTUBE_CLIENT_ID and YOUTUBE_CLIENT_SECRET must be set in .env")

    if refresh_token:
        data = urllib.parse.urlencode(
            {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            }
        ).encode("utf-8")
        req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
        with urllib.request.urlopen(req, timeout=15) as resp:
            refreshed = json.loads(resp.read().decode("utf-8"))
            return refreshed["access_token"]

    auth_params = urllib.parse.urlencode(
        {
            "client_id": client_id,
            "redirect_uri": REDIRECT_URI,
            "response_type": "code",
            "scope": SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "login_hint": LOGIN_HINT,
        }
    )
    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{auth_params}"
    print(f"Opening browser for {LOGIN_HINT} YouTube OAuth authorization...")
    subprocess.Popen(["open", auth_url])

    print("Waiting for authorization code on clipboard...")
    initial_clip = subprocess.check_output(["pbpaste"], text=True, errors="ignore").strip()
    auth_code = None

    for _ in range(600):
        cur_clip = subprocess.check_output(["pbpaste"], text=True, errors="ignore").strip()
        if cur_clip != initial_clip:
            candidate = extract_code_from_text(cur_clip)
            if candidate:
                auth_code = candidate
                print("Detected OAuth authorization code from clipboard!")
                break
        time.sleep(0.5)

    if not auth_code:
        raise RuntimeError("Timed out waiting for OAuth authorization code on clipboard")

    token_data = urllib.parse.urlencode(
        {
            "code": auth_code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": REDIRECT_URI,
            "grant_type": "authorization_code",
        }
    ).encode("utf-8")

    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=token_data, method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        tok = json.loads(resp.read().decode("utf-8"))
    if tok.get("refresh_token"):
        upsert_env_vars({"YOUTUBE_REFRESH_TOKEN": tok["refresh_token"]})
    return tok["access_token"]


def upload_video(access_token: str, meta: dict) -> dict:
    file_path = meta["file"]
    file_size = os.path.getsize(file_path)
    print(f"\nInitiating YouTube resumable upload for {os.path.basename(file_path)} ({file_size / (1024*1024):.1f} MB)...")

    body = {
        "snippet": {
            "title": meta["title"],
            "description": meta["description"],
            "tags": meta["tags"],
            "categoryId": "26",
        },
        "status": {
            "privacyStatus": "unlisted",
            "selfDeclaredMadeForKids": False,
        },
    }
    body_bytes = json.dumps(body).encode("utf-8")

    init_url = "https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status"
    init_req = urllib.request.Request(
        init_url,
        data=body_bytes,
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Goog-User-Project": QUOTA_PROJECT,
            "Content-Type": "application/json; charset=UTF-8",
            "X-Upload-Content-Length": str(file_size),
            "X-Upload-Content-Type": "video/mp4",
        },
        method="POST",
    )

    with urllib.request.urlopen(init_req, timeout=30) as resp:
        upload_url = resp.headers.get("Location")

    if not upload_url:
        raise RuntimeError("No resumable upload Location header returned by YouTube API")

    print("Uploading video bytes...")
    with open(file_path, "rb") as vf:
        video_bytes = vf.read()

    put_req = urllib.request.Request(
        upload_url,
        data=video_bytes,
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Goog-User-Project": QUOTA_PROJECT,
            "Content-Type": "video/mp4",
            "Content-Length": str(file_size),
        },
        method="PUT",
    )
    with urllib.request.urlopen(put_req, timeout=600) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    vid_id = result["id"]
    watch_url = f"https://youtu.be/{vid_id}"
    print(f"[SUCCESS] Uploaded '{meta['title']}' -> {watch_url} (Unlisted)")
    return {
        "key": meta["key"],
        "title": meta["title"],
        "video_id": vid_id,
        "url": watch_url,
        "embed_url": f"https://www.youtube.com/embed/{vid_id}",
        "privacy": "unlisted",
    }


def main():
    token = get_oauth_token()
    results = []
    for v in VIDEOS_TO_UPLOAD:
        res = upload_video(token, v)
        results.append(res)
    with open(RESULTS_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved YouTube upload results to {RESULTS_PATH}")


if __name__ == "__main__":
    main()
