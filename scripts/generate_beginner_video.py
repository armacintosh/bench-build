#!/usr/bin/env python3
"""
Generates the Simplified Beginner DIY Instructional Video (`modular_couch_beginner_video.mp4`):
1. Synthesizes plain-English, zero-jargon voiceover via Deepgram Aura TTS (Tool + Material + Action).
2. Builds a clean, full-screen 1920x1080 3D CAD stage (`beginner_studio_stage.html`) with minimal text.
"""
import json
import os
import re
import subprocess
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "scripts" else SCRIPT_DIR
VIDEO_BUILD_DIR = os.path.join(BASE_DIR, ".video_build")
AUDIO_DIR = os.path.join(VIDEO_BUILD_DIR, "audio_beginner")
STAGE_HTML_PATH = os.path.join(VIDEO_BUILD_DIR, "beginner_studio_stage.html")
MANIFEST_PATH = os.path.join(VIDEO_BUILD_DIR, "beginner_manifest.json")
os.makedirs(AUDIO_DIR, exist_ok=True)


def load_deepgram_key() -> str:
    key = os.environ.get("DEEPGRAM_API_KEY", "").strip()
    if key:
        return key
    for env_path in [os.path.join(BASE_DIR, ".env"), ".env", os.path.expanduser("~/.env")]:
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("DEEPGRAM_API_KEY="):
                        val = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if val:
                            return val
    raise RuntimeError("DEEPGRAM_API_KEY not found in environment or .env")


BEGINNER_CHAPTERS = [
    {
        "id": "00_intro",
        "badge": "OVERVIEW",
        "title": "80\" Playroom Couch, Bench & Table",
        "tool": "Circular Saw, Drill, Chisel & Clamps",
        "material": "4×4s, 2×4s, Two 2×6s, 1×6 Trim & 1 Plywood Sheet",
        "action": "Build a sturdy couch that converts to a table",
        "narration": (
            "Here is how to build our eighty-inch playroom couch, bench, and table. "
            "You only need basic tools like a circular saw, a drill, a chisel, and clamps. "
            "Let's walk through the build step by step."
        ),
    },
    {
        "id": "01_cuts",
        "badge": "PREP",
        "title": "Measure & Cut Your Wood",
        "tool": "Circular Saw, Tape Measure & Pencil",
        "material": "3/4\" Plywood, 4×4, Six 2×4s, Two 2×6s & 1×6 Trim",
        "action": "Cut boards to size and label each piece",
        "narration": (
            "First, use your tape measure and circular saw to cut your wood. "
            "Cut one sheet of three-quarter-inch plywood into the main seat board and two backrest boards. "
            "Then cut your four-by-four legs, your two-by-four frame boards, two two-by-six boards for the doubled backrest posts, and your one-by-six trim boards."
        ),
    },
    {
        "id": "02_step1_legs",
        "badge": "STEP 1",
        "title": "Prep the Five 4×4 Legs",
        "tool": "Circular Saw, Drill & Wood Chisel",
        "material": "Five 4×4 Posts (18-5/8\"), 3 Rollers & 2 Pads",
        "action": "Attach bottom wheels & pads, then notch tops",
        "narration": (
            "Step one: prepare the five four-by-four legs. "
            "Use a drill and chisel to hollow out a small pocket in the bottom of the three back legs and screw in the rollers. "
            "Screw the rubber grip pads onto the bottom of the two front legs. "
            "Then use your circular saw and a chisel to cut an L-shaped notch out of the top of each leg."
        ),
    },
    {
        "id": "03_step2_beams",
        "badge": "STEP 2",
        "title": "Attach the Front & Back Beams",
        "tool": "Bar Clamps & Cordless Drill",
        "material": "Three Long 2×4s, Wood Glue & 3\" Screws",
        "action": "Glue two front 2×4s together & screw to legs",
        "narration": (
            "Step two: attach the main front and back boards. "
            "Spread wood glue between the two long front two-by-fours, clamp them together, and drive in two-and-three-quarter-inch screws. "
            "Set this thick front beam into the front leg notches, set the back two-by-four into the three back legs, and lock them in with glue and three-inch screws."
        ),
    },
    {
        "id": "04_step3_grid",
        "badge": "STEP 3",
        "title": "Add Cross Boards & Back Slots",
        "tool": "Drill, Pocket-Hole Jig & Clamps",
        "material": "Seven 2×4 Cross Boards & Five Spacer Blocks",
        "action": "Screw cross boards in place & leave four 3-1/8\" slots",
        "narration": (
            "Step three: build the middle frame and backrest slots. "
            "Use your drill and two-and-a-half-inch pocket screws to attach the two side boards and five middle cross-boards. "
            "At the back, screw in five two-by-four spacer blocks and a back board to leave four open slots that are three and one-eighth inches wide by one and a half inches deep."
        ),
    },
    {
        "id": "05_step4_deck",
        "badge": "STEP 4",
        "title": "Screw Down the Plywood Seat",
        "tool": "Cordless Drill & Wood Glue",
        "material": "3/4\" Birch Plywood Sheet (78-1/2\" × 23-3/4\")",
        "action": "Glue and screw the plywood seat onto the frame",
        "narration": (
            "Step four: attach the plywood seat. "
            "Spread wood glue along the top of the two-by-four frame and lay the big three-quarter-inch plywood sheet on top, leaving the four back slots open. "
            "Use your drill to drive one-and-three-quarter-inch screws every eight inches all the way around."
        ),
    },
    {
        "id": "06_step5_trim",
        "badge": "STEP 5",
        "title": "Attach the Outer 1×6 Trim Boards",
        "tool": "Circular Saw (45° Bevel), Clamps & Drill",
        "material": "Four 1×6 Trim Boards & 1-7/8\" Screws",
        "action": "Clamp trim 1\" above seat & screw from inside",
        "narration": (
            "Step five: wrap the outside with one-by-six trim boards. "
            "Clamp the trim boards around the outside so the top edge sticks up one inch above the plywood seat—this lip keeps the cushion from sliding off. "
            "Drive one-and-seven-eighths-inch screws from the inside of the frame so no screw holes show on the outside."
        ),
    },
    {
        "id": "07_step6_backrests",
        "badge": "STEP 6",
        "title": "Build the Two Doubled-2×6 Backrests",
        "tool": "Circular Saw, Clamps & Cordless Drill",
        "material": "Two 2×6 Boards (8 Halves → 4 Posts) & 2 Panels",
        "action": "Cut 90° back ledge + 10° front lean, glue pairs & attach panels",
        "narration": (
            "Step six: build the two removable backrests from two two-by-six boards. "
            "Cut eight pieces to twenty-three and a half inches long. "
            "On the back edge, cut a ninety-degree L-notch at the bottom to leave a one-and-seven-sixteenths-inch peg and a flat solid wood shoulder ledge that rests right on top of the couch. "
            "On the front edge, cut a ten-degree angle where people lean back. "
            "Glue and screw the eight halves together in pairs to make four thick three-inch-wide posts, screw the plywood panels onto the front, and drop them into the slots."
        ),
    },
    {
        "id": "08_step7_finish",
        "badge": "STEP 7",
        "title": "Sand, Wax & Drop In the Cushions",
        "tool": "Orbital Sander, Paintbrush & Candle Wax",
        "material": "Sandpaper, Stain/Clear Coat & 4\" Foam Cushion",
        "action": "Sand smooth, wax post bottoms & add cushions",
        "narration": (
            "Step seven: sand, finish, and drop in the cushions. "
            "Smooth all the wood with an orbital sander and apply your stain or clear coat. "
            "Rub plain candle wax on the bottom ends of the backrest posts so they slide in and out easily. "
            "Drop in your foam seat cushion and slide your toy baskets underneath. "
            "Lift the front edge one inch to roll the couch on its back wheels, or pull the backrests out anytime to use it as a play table."
        ),
    },
]


def get_audio_duration(path: str) -> float:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            path,
        ],
        text=True,
    ).strip()
    return float(out)


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def synthesize_all(api_key: str) -> list[dict]:
    manifest = []
    total_dur = 0.0
    for ch in BEGINNER_CHAPTERS:
        mp3_path = os.path.join(AUDIO_DIR, f"{ch['id']}.mp3")
        if not os.path.exists(mp3_path) or os.path.getsize(mp3_path) < 1000:
            url = "https://api.deepgram.com/v1/speak?model=aura-2-orion-en"
            payload = json.dumps({"text": ch["narration"]}).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    "Authorization": f"Token {api_key}",
                    "Content-Type": "application/json",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    with open(mp3_path, "wb") as f:
                        f.write(resp.read())
            except urllib.error.HTTPError:
                url2 = "https://api.deepgram.com/v1/speak?model=aura-orion-en"
                req2 = urllib.request.Request(
                    url2,
                    data=payload,
                    headers={
                        "Authorization": f"Token {api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urllib.request.urlopen(req2, timeout=30) as resp:
                    with open(mp3_path, "wb") as f:
                        f.write(resp.read())

        dur = get_audio_duration(mp3_path)
        total_dur += dur
        info = {
            **ch,
            "audio_file": mp3_path,
            "duration": round(dur, 3),
            "sentences": split_sentences(ch["narration"]),
        }
        manifest.append(info)
        print(f"[OK] Beginner TTS {ch['id']}: {dur:.2f}s")

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Total beginner voiceover duration: {total_dur:.2f}s ({total_dur/60:.2f} min)")
    return manifest


def build_beginner_stage_html(chapters: list[dict]):
    stage_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Beginner DIY 3D CAD Walkthrough</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body style="margin:0; background:#0b1120; overflow:hidden;">
<canvas id="broadcast-canvas" width="1920" height="1080"></canvas>
<script>
const CHAPTERS = {json.dumps(chapters)};
const bCanvas = document.getElementById('broadcast-canvas');
const ctx = bCanvas.getContext('2d');

// Full-screen 1920x1080 Three.js WebGLRenderer
const W = 1920, H = 1080;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(34, W / H, 1, 1000);
const renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true, alpha: true }});
renderer.setSize(W, H);
renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const ambLight = new THREE.AmbientLight(0xffffff, 0.62);
scene.add(ambLight);
const dirLight = new THREE.DirectionalLight(0xfffbeb, 0.82);
dirLight.position.set(65, 115, 90);
dirLight.castShadow = true;
scene.add(dirLight);
const fillLight = new THREE.DirectionalLight(0x93c5fd, 0.38);
fillLight.position.set(-70, 55, -60);
scene.add(fillLight);

const gridHelper = new THREE.GridHelper(150, 30, 0x334155, 0x1e293b);
gridHelper.position.y = 0;
scene.add(gridHelper);

function makeWoodTexture(baseHex, grainHex, repeatX, repeatY) {{
  const c = document.createElement('canvas');
  c.width = 256; c.height = 256;
  const g = c.getContext('2d');
  g.fillStyle = baseHex;
  g.fillRect(0, 0, 256, 256);
  g.strokeStyle = grainHex;
  for (let i = 0; i < 70; i++) {{
    g.globalAlpha = 0.08 + (i % 5) * 0.03;
    g.lineWidth = 1 + (i % 3);
    g.beginPath();
    const y = (i * 3.7) % 256;
    g.moveTo(0, y);
    g.bezierCurveTo(85, y + ((i % 7) - 3) * 3, 170, y - ((i % 5) - 2) * 3, 256, y);
    g.stroke();
  }}
  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(repeatX || 2, repeatY || 1);
  return tex;
}}

function makeFabricTexture(baseHex, fleckHex) {{
  const c = document.createElement('canvas');
  c.width = 128; c.height = 128;
  const g = c.getContext('2d');
  g.fillStyle = baseHex;
  g.fillRect(0, 0, 128, 128);
  g.fillStyle = fleckHex;
  for (let y = 0; y < 128; y += 4) {{
    for (let x = 0; x < 128; x += 4) {{
      if ((x + y) % 8 === 0) g.fillRect(x, y, 2, 2);
    }}
  }}
  const tex = new THREE.CanvasTexture(c);
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(6, 3);
  return tex;
}}

const cadMats = {{
  post: new THREE.MeshStandardMaterial({{ color: 0xf59e0b, roughness: 0.5 }}),
  beam: new THREE.MeshStandardMaterial({{ color: 0x3b82f6, roughness: 0.5 }}),
  joist: new THREE.MeshStandardMaterial({{ color: 0x38bdf8, roughness: 0.52 }}),
  spacer: new THREE.MeshStandardMaterial({{ color: 0xf43f5e, roughness: 0.5 }}),
  deck: new THREE.MeshStandardMaterial({{ color: 0xfacc15, roughness: 0.45 }}),
  trim: new THREE.MeshStandardMaterial({{ color: 0xa855f7, roughness: 0.42 }}),
  backSpine: new THREE.MeshStandardMaterial({{ color: 0x10b981, roughness: 0.5 }}),
  backPanel: new THREE.MeshStandardMaterial({{ color: 0x34d399, roughness: 0.45 }}),
  cushion: new THREE.MeshStandardMaterial({{ color: 0x60a5fa, roughness: 0.7, transparent: true, opacity: 0.9 }}),
  pad: new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.9 }}),
  roller: new THREE.MeshStandardMaterial({{ color: 0xe2e8f0, metalness: 0.6, roughness: 0.3 }}),
  basket: new THREE.MeshStandardMaterial({{ color: 0x92400e, roughness: 0.85, transparent: true, opacity: 0.45 }})
}};

const realMats = {{
  post: new THREE.MeshStandardMaterial({{ map: makeWoodTexture('#c89d66', '#8c5a2b', 1, 2), roughness: 0.65 }}),
  beam: new THREE.MeshStandardMaterial({{ map: makeWoodTexture('#d6ab73', '#9c6b36', 3, 1), roughness: 0.6 }}),
  joist: new THREE.MeshStandardMaterial({{ map: makeWoodTexture('#d6ab73', '#9c6b36', 2, 1), roughness: 0.65 }}),
  spacer: new THREE.MeshStandardMaterial({{ map: makeWoodTexture('#c49358', '#855421', 1, 1), roughness: 0.65 }}),
  deck: new THREE.MeshStandardMaterial({{ map: makeWoodTexture('#e8cfa0', '#b8965c', 4, 2), roughness: 0.42 }}),
  trim: new THREE.MeshStandardMaterial({{ map: makeWoodTexture('#6b3e26', '#3d1e0d', 4, 1), roughness: 0.28 }}),
  backSpine: new THREE.MeshStandardMaterial({{ map: makeWoodTexture('#b07d48', '#73481d', 1, 2), roughness: 0.55 }}),
  backPanel: new THREE.MeshStandardMaterial({{ map: makeWoodTexture('#e3c591', '#ab864c', 3, 2), roughness: 0.38 }}),
  cushion: new THREE.MeshStandardMaterial({{ map: makeFabricTexture('#e5ddd0', '#c4b9a5'), roughness: 0.92 }}),
  pad: new THREE.MeshStandardMaterial({{ color: 0x111827, roughness: 0.95 }}),
  roller: new THREE.MeshStandardMaterial({{ color: 0xcbd5e1, metalness: 0.8, roughness: 0.2 }}),
  basket: new THREE.MeshStandardMaterial({{ map: makeWoodTexture('#a67c52', '#6e4924', 2, 2), roughness: 0.88 }})
}};

const allParts = [];
function addBox(w, d, h, x, y, z, matKey, phaseNum, flyOffset) {{
  const geom = new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geom, cadMats[matKey]);
  const basePos = new THREE.Vector3(x + w/2 - 40, z + h/2, 14.5 - (y + d/2));
  mesh.position.copy(basePos);
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  const edges = new THREE.EdgesGeometry(geom);
  const line = new THREE.LineSegments(
    edges,
    new THREE.LineBasicMaterial({{ color: 0x0f172a, transparent: true, opacity: 0.6 }})
  );
  mesh.add(line);
  scene.add(mesh);

  const partObj = {{
    mesh,
    line,
    matKey,
    phaseNum,
    basePos,
    flyOffset: new THREE.Vector3(flyOffset[0], flyOffset[1], flyOffset[2])
  }};
  allParts.push(partObj);
  return partObj;
}}

// STEP 1: 5 Notched 4x4 Legs + Front Rubber Pads + Rear Rollers
[0.75, 75.75].forEach(lx => {{
  addBox(3.5, 3.5, 0.375, lx, 0.75, 0.0, 'pad', 1, [0, -8, 0]);
  addBox(3.5, 3.5, 15.125, lx, 0.75, 0.375, 'post', 1, [0, -14, 0]);
  addBox(3.5, 2.0, 3.5, lx, 2.25, 15.5, 'post', 1, [0, -14, 0]);
}});
[0.75, 38.25, 75.75].forEach(lx => {{
  addBox(2.5, 1.5, 0.375, lx + 0.5, 25.75, 0.0, 'roller', 1, [0, -8, 0]);
  addBox(3.5, 3.5, 15.125, lx, 24.75, 0.375, 'post', 1, [0, -14, 0]);
  addBox(3.5, 2.0, 3.5, lx, 24.75, 15.5, 'post', 1, [0, -14, 0]);
}});

// STEP 2: Front Beam (2x 2x4) & Rear 2x4 Rail
addBox(78.5, 1.5, 3.5, 0.75, 0.75, 15.5, 'beam', 2, [0, 16, 12]);
addBox(78.5, 1.5, 3.5, 0.75, 2.25, 15.5, 'beam', 2, [0, 18, 8]);
addBox(78.5, 1.5, 3.5, 0.75, 26.75, 15.5, 'beam', 2, [0, 16, -12]);

// STEP 3: Side Boards, 5 Middle Cross Boards, Back Slot Rail & 5 Spacer Blocks
addBox(1.5, 22.25, 3.5, 0.75, 3.75, 15.5, 'joist', 3, [-15, 14, 0]);
addBox(1.5, 22.25, 3.5, 77.75, 3.75, 15.5, 'joist', 3, [15, 14, 0]);
[16.0, 28.0, 40.0, 52.0, 64.0].forEach(jx => {{
  addBox(1.5, 20.0, 3.5, jx - 0.75, 3.75, 15.5, 'joist', 3, [0, 16, 0]);
}});
addBox(78.5, 1.5, 3.5, 0.75, 23.75, 15.5, 'beam', 3, [0, 18, -5]);
[[0.75, 5.50], [9.375, 21.25], [33.75, 12.50], [49.375, 21.25], [73.75, 5.50]].forEach(([sx, sw]) => {{
  addBox(sw, 1.5, 3.5, sx, 25.25, 15.5, 'spacer', 3, [0, 20, -8]);
}});

// STEP 4: 3/4" Plywood Seat Board
addBox(78.5, 23.75, 0.75, 0.75, 0.75, 19.0, 'deck', 4, [0, 22, 0]);
addBox(78.5, 1.5, 0.75, 0.75, 26.75, 19.0, 'deck', 4, [0, 22, -6]);

// STEP 5: 1x6 Outer Trim Boards
addBox(80.0, 0.75, 5.5, 0.0, 0.0, 15.25, 'trim', 5, [0, 6, 18]);
addBox(80.0, 0.75, 4.5, 0.0, 28.25, 15.25, 'trim', 5, [0, 6, -18]);
addBox(0.75, 29.0, 5.5, 0.0, 0.0, 15.25, 'trim', 5, [-20, 6, 0]);
addBox(0.75, 29.0, 5.5, 79.25, 0.0, 15.25, 'trim', 5, [20, 6, 0]);

// STEP 6: Two Drop-In Backrests (4 Doubled 2x6 Uprights = 8 Halves with 90° Solid Wood Rear Ledge + 10° Front Lean)
function addExtruded2x6Half(x0, phaseNum, flyOffset) {{
  const sh = new THREE.Shape();
  sh.moveTo(0.0, 0.0);
  sh.lineTo(1.44, 0.0);
  sh.lineTo(1.44, 4.25);
  sh.lineTo(5.50, 4.25);
  sh.lineTo(5.50, 23.50);
  sh.lineTo(3.39, 23.50);
  sh.lineTo(0.0, 4.25);
  sh.closePath();
  const geom = new THREE.ExtrudeGeometry(sh, {{ depth: 1.50, bevelEnabled: false }});
  geom.rotateY(Math.PI / 2);
  const mesh = new THREE.Mesh(geom, cadMats['backSpine']);
  const basePos = new THREE.Vector3(x0 - 40, 15.5, 14.5 - 25.25);
  mesh.position.copy(basePos);
  mesh.castShadow = true;
  mesh.receiveShadow = true;
  const edges = new THREE.EdgesGeometry(geom);
  const line = new THREE.LineSegments(
    edges,
    new THREE.LineBasicMaterial({{ color: 0x0f172a, transparent: true, opacity: 0.6 }})
  );
  mesh.add(line);
  scene.add(mesh);
  allParts.push({{
    mesh, line, matKey: 'backSpine', phaseNum, basePos,
    flyOffset: new THREE.Vector3(flyOffset[0], flyOffset[1], flyOffset[2])
  }});
}}
[6.3125, 30.6875, 46.3125, 70.6875].forEach(ux => {{
  addExtruded2x6Half(ux, 6, [0, 24, 0]);
  addExtruded2x6Half(ux + 1.50, 6, [0, 24, 0]);
}});
[0.5, 40.25].forEach(bx => {{
  const bp = addBox(39.25, 0.75, 15.0, bx, 25.3, 23.25, 'backPanel', 6, [0, 26, 0]);
  bp.mesh.rotation.x = -10 * Math.PI / 180;
}});

// STEP 7: Cushions & Baskets
addBox(78.0, 23.5, 4.0, 1.0, 1.0, 19.75, 'cushion', 7, [0, 25, 0]);
[1.25, 40.25].forEach(cx => {{
  const bc = addBox(38.5, 4.0, 13.5, cx, 21.2, 23.8, 'cushion', 7, [0, 28, 6]);
  bc.mesh.rotation.x = -10 * Math.PI / 180;
}});
[5.5, 22.8, 40.1, 57.4].forEach(bx => {{
  addBox(15.0, 20.0, 13.5, bx, 3.5, 0.5, 'basket', 7, [0, 0, 22]);
}});

// Camera paths centered nicely in the full 1920x1080 frame
const CAM_PATHS = [
  [-0.55, 0.50, 1.12, 1.04, 126, 118, 13], // 00_intro
  [-0.45, 0.45, 0.94, 0.86, 140, 132, 15], // 01_cuts: exploded overview
  [-0.70, 0.30, 1.20, 1.10, 106, 96, 10],  // 02_step1_legs
  [-0.45, 0.40, 1.15, 1.06, 116, 108, 13], // 03_step2_beams
  [-0.35, 0.65, 0.78, 0.88, 118, 110, 14], // 04_step3_grid
  [-0.50, 0.35, 0.95, 1.08, 118, 110, 15], // 05_step4_deck
  [-0.65, 0.45, 1.16, 1.08, 114, 106, 14], // 06_step5_trim
  [-0.35, 0.60, 1.04, 0.96, 120, 112, 17], // 07_step6_backrests
  [-0.55, 0.60, 1.12, 1.04, 124, 116, 14]  // 08_step7_finish
];

function easeOutCubic(x) {{
  return 1 - Math.pow(1 - Math.max(0, Math.min(1, x)), 3);
}}

function roundRect(ctx, x, y, w, h, r) {{
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}}

window.allAssetsReady = true;

window.renderBroadcastFrame = function(chapterIdx, tNorm, elapsedGlobalSec, totalGlobalSec) {{
  const ch = CHAPTERS[chapterIdx];
  const isRealRender = (chapterIdx === 0 && tNorm < 0.5) || (chapterIdx === 8 && tNorm > 0.35);

  // 1. Update 3D Scene
  const flyEase = easeOutCubic(tNorm / 0.42);
  allParts.forEach(p => {{
    const targetMat = isRealRender ? realMats[p.matKey] : cadMats[p.matKey];
    p.mesh.material = targetMat;
    p.line.visible = true;
    p.line.material.opacity = isRealRender ? 0.18 : 0.60;

    if (chapterIdx === 0) {{
      p.mesh.visible = true;
      p.mesh.position.copy(p.basePos);
    }} else if (chapterIdx === 1) {{
      p.mesh.visible = p.phaseNum <= 6;
      const explodeAmt = 0.42 + 0.22 * Math.sin(tNorm * Math.PI);
      p.mesh.position.copy(p.basePos).addScaledVector(p.flyOffset, explodeAmt);
    }} else {{
      const activePhase = chapterIdx - 1;
      if (p.phaseNum < activePhase) {{
        p.mesh.visible = true;
        p.mesh.position.copy(p.basePos);
      }} else if (p.phaseNum === activePhase) {{
        p.mesh.visible = true;
        const offsetFactor = 1.0 - flyEase;
        p.mesh.position.copy(p.basePos).addScaledVector(p.flyOffset, offsetFactor);
        if (offsetFactor > 0.02 && !isRealRender) {{
          const hlMat = targetMat.clone();
          hlMat.emissive = new THREE.Color(0xfbbf24);
          hlMat.emissiveIntensity = 0.35 * offsetFactor;
          p.mesh.material = hlMat;
        }}
        if (activePhase === 7 && tNorm > 0.72 && p.phaseNum === 6) {{
          p.mesh.position.y += (tNorm - 0.72) * 32;
        }}
      }} else {{
        p.mesh.visible = false;
      }}
    }}
  }});

  const cp = CAM_PATHS[chapterIdx];
  const theta = cp[0] + (cp[1] - cp[0]) * tNorm;
  const phi = cp[2] + (cp[3] - cp[2]) * tNorm;
  const dist = cp[4] + (cp[5] - cp[4]) * tNorm;
  const targetY = cp[6];
  camera.position.set(
    dist * Math.sin(phi) * Math.sin(theta),
    dist * Math.cos(phi) + targetY,
    dist * Math.sin(phi) * Math.cos(theta)
  );
  camera.lookAt(0, targetY, 0);
  renderer.render(scene, camera);

  // 2. Draw Full-Screen 1920x1080 3D Viewport Background
  const bgGrad = ctx.createRadialGradient(960, 480, 80, 960, 540, 1050);
  if (isRealRender) {{
    bgGrad.addColorStop(0, '#292524');
    bgGrad.addColorStop(1, '#0c0a09');
  }} else {{
    bgGrad.addColorStop(0, '#1e293b');
    bgGrad.addColorStop(1, '#090d16');
  }}
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, 1920, 1080);

  // Draw the full-bleed 3D WebGL scene
  ctx.drawImage(renderer.domElement, 0, 0, 1920, 1080);

  // 3. Minimal Top-Left Step Pill & Title Card
  ctx.fillStyle = 'rgba(15, 23, 42, 0.86)';
  ctx.strokeStyle = 'rgba(148, 163, 184, 0.25)';
  ctx.lineWidth = 1.5;
  roundRect(ctx, 36, 28, 620, 74, 14);
  ctx.fill();
  ctx.stroke();

  // Badge Pill
  ctx.fillStyle = '#f59e0b';
  roundRect(ctx, 54, 43, 116, 44, 9);
  ctx.fill();
  ctx.fillStyle = '#0f172a';
  ctx.font = '900 17px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(ch.badge, 54 + 58, 71);

  // Step Title
  ctx.fillStyle = '#f8fafc';
  ctx.font = '800 26px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(ch.title, 188, 74);

  // 4. Minimal Top-Right "Tool • Material • Action" Card
  ctx.fillStyle = 'rgba(15, 23, 42, 0.86)';
  ctx.strokeStyle = 'rgba(148, 163, 184, 0.25)';
  roundRect(ctx, 1340, 28, 544, 134, 14);
  ctx.fill();
  ctx.stroke();

  const rows = [
    ['🪚 TOOL', ch.tool, '#38bdf8'],
    ['🪵 WOOD', ch.material, '#fbbf24'],
    ['🔨 DO', ch.action, '#34d399']
  ];
  rows.forEach(([label, val, col], idx) => {{
    const ry = 62 + idx * 36;
    ctx.fillStyle = col;
    ctx.font = '800 13px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(label, 1362, ry);

    ctx.fillStyle = '#f1f5f9';
    ctx.font = '600 16px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.fillText(val, 1455, ry);
  }});

  // 5. Minimal Single-Line Subtitle Bar at Bottom
  const sents = ch.sentences;
  const sIdx = Math.min(sents.length - 1, Math.floor(tNorm * sents.length));
  const curSent = sents[sIdx];

  ctx.fillStyle = 'rgba(9, 13, 22, 0.88)';
  ctx.strokeStyle = 'rgba(59, 130, 246, 0.35)';
  roundRect(ctx, 140, 962, 1640, 76, 14);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = '#f8fafc';
  ctx.font = '600 23px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(curSent, 960, 1008, 1580);

  // Thin Progress Line at Very Bottom
  const pct = Math.max(0, Math.min(1, elapsedGlobalSec / totalGlobalSec));
  ctx.fillStyle = 'rgba(30, 41, 59, 0.8)';
  ctx.fillRect(0, 1072, 1920, 8);
  ctx.fillStyle = '#f59e0b';
  ctx.fillRect(0, 1072, 1920 * pct, 8);

  return bCanvas.toDataURL('image/jpeg', 0.92);
}};
</script>
</body>
</html>
"""
    with open(STAGE_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(stage_html)
    print(f"Wrote Beginner 3D Stage HTML to {STAGE_HTML_PATH}")


def main():
    api_key = load_deepgram_key()
    manifest = synthesize_all(api_key)
    build_beginner_stage_html(manifest)


if __name__ == "__main__":
    main()
