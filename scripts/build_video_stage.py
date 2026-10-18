#!/usr/bin/env python3
"""
Builds the 1920x1080 Broadcast CAD + 3D + Blueprint Canvas Compositor (`video_studio_stage.html`)
that renders Three.js 3D WebGL + inline SVG Blueprints + Broadcast HUD directly to a 1920x1080
HTML5 Canvas and exports base64 JPEG frames via `window.renderBroadcastFrame(...)` with zero
dependency on macOS CVDisplayLink or Page.captureScreenshot.
"""
import base64
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_BUILD_DIR = os.path.join(BASE_DIR, ".video_build")
HTML_GUIDE_PATH = os.path.join(BASE_DIR, "modular_couch_build_guide.html")
MANIFEST_PATH = os.path.join(VIDEO_BUILD_DIR, "chapters_manifest.json")
STAGE_HTML_PATH = os.path.join(VIDEO_BUILD_DIR, "video_studio_stage.html")


def extract_svgs_as_data_uris(html_path: str) -> list[str]:
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
    svgs = re.findall(r"<svg[\s\S]*?</svg>", html)
    uris = []
    for s in svgs:
        if 'xmlns=' not in s[:120]:
            s = s.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1)
        b64 = base64.b64encode(s.encode("utf-8")).decode("ascii")
        uris.append(f"data:image/svg+xml;base64,{b64}")
    print(f"Extracted {len(uris)} SVG data URIs from {os.path.basename(html_path)}")
    return uris


def split_sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def build_stage_html():
    svg_uris = extract_svgs_as_data_uris(HTML_GUIDE_PATH)
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        chapters = json.load(f)

    svg_pairs_for_chapter = [
        (3, 5, "Blueprint 1: Side Cross-Section (Y–Z Plane)", "Blueprint 3: Front & Rear Elevations (X–Z)"),
        (0, 1, "Cut Map 1: 3/4\" Birch Plywood Sheet (48\" × 96\")", "Cut Map 2: Zero-Waste 2×6 Angled Spine Layout"),
        (7, 6, "Phase 1 Diagram: 18-5/8\" Notched 4×4 Legs & Rollers", "Blueprint 4: Half-Lap Notch & 3/8\" Roller Recess"),
        (8, 5, "Phase 2 Diagram: Dual Laminated 2×4 Front Beam", "Blueprint 3: 71.50\" Unobstructed Front Span"),
        (9, 4, "Phase 3 Diagram: Ladder Joist Grid & Spacer Gauge", "Blueprint 2: Top Structural Plan & 4 Mortise Slots"),
        (10, 3, "Phase 4 Diagram: 3/4\" Birch Plywood Torsion Deck", "Blueprint 1: Coplanar Z = 19.00\"–19.75\" Deck"),
        (11, 6, "Phase 5 Diagram: Blind-Fastened 1×6 Stain-Grade Trim", "Blueprint 4 (Detail B): Inside Blind Screw Fastening"),
        (12, 1, "Phase 6 Diagram: Two 40\" Drop-In 10° Backrests", "Cut Map 2: 23.5\" One-Piece Angled 2×6 Uprights"),
        (13, 3, "Phase 7 Diagram: Waxed Tenons & Cushion Drop-In", "Blueprint 1: Final Coplanar Z-Stack Assembly"),
    ]

    for idx, ch in enumerate(chapters):
        s1, s2, lbl1, lbl2 = svg_pairs_for_chapter[idx]
        ch["svg_primary_idx"] = s1
        ch["svg_secondary_idx"] = s2
        ch["svg_primary_label"] = lbl1
        ch["svg_secondary_label"] = lbl2
        ch["sentences"] = split_sentences(ch["narration"])

    stage_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Modular Couch 1080p Broadcast Compositor</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body style="margin:0; background:#070b14; overflow:hidden;">
<canvas id="broadcast-canvas" width="1920" height="1080"></canvas>
<script>
const SVG_URIS = {json.dumps(svg_uris)};
const CHAPTERS = {json.dumps(chapters)};

const bCanvas = document.getElementById('broadcast-canvas');
const ctx = bCanvas.getContext('2d');

// Preload all 14 SVG images
const svgImages = [];
let loadedCount = 0;
window.allAssetsReady = false;

SVG_URIS.forEach((uri, idx) => {{
  const img = new Image();
  img.onload = () => {{
    loadedCount++;
    if (loadedCount === SVG_URIS.length) {{
      window.allAssetsReady = true;
    }}
  }};
  img.onerror = () => {{
    loadedCount++;
    if (loadedCount === SVG_URIS.length) {{
      window.allAssetsReady = true;
    }}
  }};
  img.src = uri;
  svgImages[idx] = img;
}});

// Build Three.js offscreen WebGLRenderer (1120 x 812)
const W = 1120, H = 812;
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, W / H, 1, 1000);
const renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true, alpha: true }});
renderer.setSize(W, H);
renderer.setPixelRatio(1);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const ambLight = new THREE.AmbientLight(0xffffff, 0.56);
scene.add(ambLight);
const dirLight = new THREE.DirectionalLight(0xfffbeb, 0.78);
dirLight.position.set(65, 110, 85);
dirLight.castShadow = true;
scene.add(dirLight);
const fillLight = new THREE.DirectionalLight(0x93c5fd, 0.35);
fillLight.position.set(-70, 50, -60);
scene.add(fillLight);

const gridHelper = new THREE.GridHelper(130, 26, 0x334155, 0x1e293b);
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
  post: new THREE.MeshStandardMaterial({{ color: 0xd97706, roughness: 0.55 }}),
  beam: new THREE.MeshStandardMaterial({{ color: 0x3b82f6, roughness: 0.5 }}),
  joist: new THREE.MeshStandardMaterial({{ color: 0x60a5fa, roughness: 0.55 }}),
  spacer: new THREE.MeshStandardMaterial({{ color: 0xf43f5e, roughness: 0.5 }}),
  deck: new THREE.MeshStandardMaterial({{ color: 0xfbbf24, roughness: 0.45 }}),
  trim: new THREE.MeshStandardMaterial({{ color: 0xa855f7, roughness: 0.4 }}),
  backSpine: new THREE.MeshStandardMaterial({{ color: 0x10b981, roughness: 0.5 }}),
  backPanel: new THREE.MeshStandardMaterial({{ color: 0x34d399, roughness: 0.45 }}),
  cushion: new THREE.MeshStandardMaterial({{ color: 0x38bdf8, roughness: 0.7, transparent: true, opacity: 0.88 }}),
  pad: new THREE.MeshStandardMaterial({{ color: 0x1e293b, roughness: 0.9 }}),
  roller: new THREE.MeshStandardMaterial({{ color: 0x94a3b8, metalness: 0.6, roughness: 0.3 }}),
  basket: new THREE.MeshStandardMaterial({{ color: 0x78350f, roughness: 0.85, transparent: true, opacity: 0.35 }})
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
function addBox(w, d, h, x, y, z, matKey, phaseNum, flyOffset, edgeHex) {{
  const geom = new THREE.BoxGeometry(w, h, d);
  const mesh = new THREE.Mesh(geom, cadMats[matKey]);
  const basePos = new THREE.Vector3(x + w/2 - 40, z + h/2, 14.5 - (y + d/2));
  mesh.position.copy(basePos);
  mesh.castShadow = true;
  mesh.receiveShadow = true;

  const edges = new THREE.EdgesGeometry(geom);
  const line = new THREE.LineSegments(
    edges,
    new THREE.LineBasicMaterial({{ color: edgeHex || 0x0f172a, transparent: true, opacity: 0.55 }})
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

// PHASE 1: 5 Notched 4x4 Legs + Front Rubber Pads + Rear Rollers
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

// PHASE 2: Dual Laminated Front Beam (2x 2x4) & Rear Outer 2x4 Rail
addBox(78.5, 1.5, 3.5, 0.75, 0.75, 15.5, 'beam', 2, [0, 16, 12]);
addBox(78.5, 1.5, 3.5, 0.75, 2.25, 15.5, 'beam', 2, [0, 18, 8]);
addBox(78.5, 1.5, 3.5, 0.75, 26.75, 15.5, 'beam', 2, [0, 16, -12]);

// PHASE 3: End Rails, 5 Interior Joists, Inner Mortise Rail, 5 Spacer Blocks
addBox(1.5, 22.25, 3.5, 0.75, 3.75, 15.5, 'joist', 3, [-15, 14, 0]);
addBox(1.5, 22.25, 3.5, 77.75, 3.75, 15.5, 'joist', 3, [15, 14, 0]);
[16.0, 28.0, 40.0, 52.0, 64.0].forEach(jx => {{
  addBox(1.5, 20.0, 3.5, jx - 0.75, 3.75, 15.5, 'joist', 3, [0, 16, 0]);
}});
addBox(78.5, 1.5, 3.5, 0.75, 23.75, 15.5, 'beam', 3, [0, 18, -5]);
[[0.75, 5.25], [9.50, 21.00], [34.00, 12.00], [49.50, 21.00], [74.00, 5.25]].forEach(([sx, sw]) => {{
  addBox(sw, 1.5, 3.5, sx, 25.25, 15.5, 'spacer', 3, [0, 20, -8]);
}});

// PHASE 4: 3/4" Birch Plywood Seat Deck + 1x2 Rear Pocket Caps
addBox(78.5, 23.75, 0.75, 0.75, 0.75, 19.0, 'deck', 4, [0, 22, 0]);
addBox(78.5, 1.5, 0.75, 0.75, 26.75, 19.0, 'deck', 4, [0, 22, -6]);

// PHASE 5: Stain-Grade 1x6 Outer Apron Trim (Z = 15.25 to 20.75)
addBox(80.0, 0.75, 5.5, 0.0, 0.0, 15.25, 'trim', 5, [0, 6, 18]);
addBox(80.0, 0.75, 5.5, 0.0, 28.25, 15.25, 'trim', 5, [0, 6, -18]);
addBox(0.75, 29.0, 5.5, 0.0, 0.0, 15.25, 'trim', 5, [-20, 6, 0]);
addBox(0.75, 29.0, 5.5, 79.25, 0.0, 15.25, 'trim', 5, [20, 6, 0]);

// PHASE 6: Two 40" Drop-In 10-Degree Slanted Backrests
[6.0, 30.5, 46.0, 70.5].forEach(sx => {{
  addBox(3.5, 1.5, 4.25, sx, 25.25, 15.5, 'backSpine', 6, [0, 24, 0]);
  const p = addBox(3.5, 2.2, 16.0, sx, 25.6, 19.75, 'backSpine', 6, [0, 24, 0]);
  p.mesh.rotation.x = -10 * Math.PI / 180;
}});
[0.5, 40.25].forEach(bx => {{
  const bp = addBox(39.25, 0.75, 15.0, bx, 24.9, 20.2, 'backPanel', 6, [0, 26, 0]);
  bp.mesh.rotation.x = -10 * Math.PI / 180;
}});

// PHASE 7: Recessed Seat Cushion (78x23.5x4), 2 Back Cushions, 4 Under-Bench Baskets
addBox(78.0, 23.5, 4.0, 1.0, 1.0, 19.75, 'cushion', 7, [0, 25, 0]);
[1.25, 40.25].forEach(cx => {{
  const bc = addBox(38.5, 4.0, 13.5, cx, 21.2, 23.8, 'cushion', 7, [0, 28, 6]);
  bc.mesh.rotation.x = -10 * Math.PI / 180;
}});
[5.5, 22.8, 40.1, 57.4].forEach(bx => {{
  addBox(15.0, 20.0, 13.5, bx, 3.5, 0.5, 'basket', 7, [0, 0, 22]);
}});

const CAM_PATHS = [
  [-0.55, 0.50, 1.12, 1.04, 118, 112, 14],
  [-0.40, 0.45, 0.92, 0.85, 132, 126, 16],
  [-0.75, 0.25, 1.22, 1.12, 98, 90, 10],
  [-0.45, 0.40, 1.16, 1.08, 108, 102, 14],
  [-0.35, 0.65, 0.78, 0.88, 110, 104, 15],
  [-0.50, 0.30, 0.95, 1.08, 112, 106, 16],
  [-0.65, 0.45, 1.18, 1.10, 106, 100, 15],
  [-0.40, 0.55, 1.05, 0.96, 114, 106, 18],
  [-0.55, 0.60, 1.12, 1.04, 116, 110, 15]
];

const ACTIVE_PARTS_LABELS = [
  'Full 80" × 29" Modular Couch, Bench & Table System (Parts A–M)',
  'Exploded Material Nesting: 1× Birch Plywood (4ft × 8ft) + 8ft Dimensional Boards',
  'Installing: Part A (3× Rear 4×4 Legs + Rollers) & Part B (2× Front 4×4 Legs + Grip Pads)',
  'Installing: Part C (Dual Laminated 78.5" Front 2×4 Beam) & Part D (Rear 78.5" Rail)',
  'Installing: Part E (Side Rails), Part F (5× Joists @ 16"–64") & Part G (5× Mortise Spacers)',
  'Installing: Part H (78.50" × 23.75" × 3/4" Birch Deck) & Part M (1×2 Pocket Caps)',
  'Installing: Part I (2× 80" Front/Rear 1×6 Trim) & Part J (2× 29" Side 1×6 Trim)',
  'Installing: Part K (4× 10° Angled 2×6 Spines) & Part L (2× 39.25" Birch Back Panels)',
  'Final Assembly: 78" × 23.5" × 4" Foam Cushion, Waxed Tenons & Storage Baskets'
];

const Z_PILL_LABELS = [
  'Z = 0.00" .. 34.50" FULL STACK',
  'PARTS A–M MASTER CUT MAP',
  'Z = 0.00" .. 19.00" (18-5/8" LEGS)',
  'Z = 15.50" .. 19.00" (3.0"×3.5" BEAM)',
  'Z = 15.50" .. 19.00" (4× MORTISE SLOTS)',
  'Z = 19.00" .. 19.75" (3/4" BIRCH DECK)',
  'Z = 15.25" .. 20.75" (1.00" CUSHION LIP)',
  'Z = 15.50" .. 34.50" (10° BACKRESTS)',
  'FINISHED RENDER & TABLE MODE'
];

const PILL_NAMES = ['Overview', 'Cut Maps', 'P1 Legs', 'P2 Beams', 'P3 Grid', 'P4 Deck', 'P5 Trim', 'P6 Back', 'P7 Finish'];

function easeOutCubic(x) {{
  return 1 - Math.pow(1 - Math.max(0, Math.min(1, x)), 3);
}}

function formatMMSS(sec) {{
  const s = Math.max(0, Math.floor(sec));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return String(m).padStart(2, '0') + ':' + String(r).padStart(2, '0');
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

function fillWrappedText(ctx, text, x, y, maxWidth, lineHeight) {{
  const words = text.split(' ');
  let line = '';
  let curY = y;
  for (let n = 0; n < words.length; n++) {{
    const testLine = line + words[n] + ' ';
    const metrics = ctx.measureText(testLine);
    if (metrics.width > maxWidth && n > 0) {{
      ctx.fillText(line.trim(), x, curY);
      line = words[n] + ' ';
      curY += lineHeight;
    }} else {{
      line = testLine;
    }}
  }}
  if (line.trim()) ctx.fillText(line.trim(), x, curY);
}}

window.renderBroadcastFrame = function(chapterIdx, tNorm, elapsedGlobalSec, totalGlobalSec) {{
  const ch = CHAPTERS[chapterIdx];
  const isRealRender = (chapterIdx === 0 && tNorm < 0.45) || (chapterIdx === 8 && tNorm > 0.30);

  // 1. Update 3D Scene
  const flyEase = easeOutCubic(tNorm / 0.42);
  allParts.forEach(p => {{
    const targetMat = isRealRender ? realMats[p.matKey] : cadMats[p.matKey];
    p.mesh.material = targetMat;
    p.line.visible = true;
    p.line.material.opacity = isRealRender ? 0.18 : 0.55;

    if (chapterIdx === 0) {{
      p.mesh.visible = true;
      const explodeAmt = (tNorm >= 0.45 && tNorm < 0.82) ? Math.sin((tNorm - 0.45) / 0.37 * Math.PI) * 0.45 : 0;
      p.mesh.position.copy(p.basePos).addScaledVector(p.flyOffset, explodeAmt);
    }} else if (chapterIdx === 1) {{
      p.mesh.visible = p.phaseNum <= 6;
      const explodeAmt = 0.35 + 0.25 * Math.sin(tNorm * Math.PI);
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
          hlMat.emissive = new THREE.Color(0xf59e0b);
          hlMat.emissiveIntensity = 0.28 * offsetFactor;
          p.mesh.material = hlMat;
        }}
        if (activePhase === 7 && tNorm > 0.72 && p.phaseNum === 6) {{
          p.mesh.position.y += (tNorm - 0.72) * 30;
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

  // 2. Composite 1920x1080 Broadcast Frame on bCanvas
  ctx.fillStyle = '#070b14';
  ctx.fillRect(0, 0, 1920, 1080);

  // Top Header Bar (0..86)
  ctx.fillStyle = '#0f172a';
  ctx.fillRect(0, 0, 1920, 86);
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(0, 86); ctx.lineTo(1920, 86); ctx.stroke();

  // Phase Badge
  ctx.fillStyle = '#f59e0b';
  roundRect(ctx, 28, 22, 190, 42, 8);
  ctx.fill();
  ctx.fillStyle = '#0f172a';
  ctx.font = '900 14px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText(ch.badge, 28 + 95, 48);

  // Title & Subtitle
  ctx.textAlign = 'left';
  ctx.fillStyle = '#f8fafc';
  ctx.font = '800 25px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.fillText(ch.title, 236, 44);
  ctx.fillStyle = '#94a3b8';
  ctx.font = '600 13px Menlo, monospace';
  ctx.fillText(ch.subtitle, 236, 68);

  // Step Pills on Right of Top Bar
  let pillX = 1185;
  for (let i = 0; i < PILL_NAMES.length; i++) {{
    const pw = 74, ph = 30, py = 28;
    if (i < chapterIdx) {{
      ctx.fillStyle = 'rgba(16, 185, 129, 0.18)';
      ctx.strokeStyle = '#10b981';
    }} else if (i === chapterIdx) {{
      ctx.fillStyle = '#3b82f6';
      ctx.strokeStyle = '#60a5fa';
    }} else {{
      ctx.fillStyle = '#090d16';
      ctx.strokeStyle = '#1e293b';
    }}
    roundRect(ctx, pillX, py, pw, ph, 6);
    ctx.fill();
    ctx.lineWidth = 1.5;
    ctx.stroke();

    ctx.fillStyle = i === chapterIdx ? '#ffffff' : (i < chapterIdx ? '#34d399' : '#64748b');
    ctx.font = '700 11px -apple-system, BlinkMacSystemFont, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(PILL_NAMES[i], pillX + pw / 2, py + 19);
    pillX += pw + 6;
  }}

  // Left 3D Panel Background (x=24, y=102, w=1120, h=812)
  const cadGrad = ctx.createRadialGradient(24 + 560, 102 + 320, 40, 24 + 560, 102 + 406, 650);
  if (isRealRender) {{
    cadGrad.addColorStop(0, '#292524');
    cadGrad.addColorStop(1, '#0c0a09');
  }} else {{
    cadGrad.addColorStop(0, '#1e293b');
    cadGrad.addColorStop(1, '#090d16');
  }}
  ctx.fillStyle = cadGrad;
  roundRect(ctx, 24, 102, 1120, 812, 16);
  ctx.fill();

  // Draw WebGL 3D Canvas onto Broadcast Canvas
  ctx.save();
  roundRect(ctx, 24, 102, 1120, 812, 16);
  ctx.clip();
  ctx.drawImage(renderer.domElement, 24, 102, 1120, 812);
  ctx.restore();

  ctx.strokeStyle = isRealRender ? '#f59e0b' : '#334155';
  ctx.lineWidth = 2;
  roundRect(ctx, 24, 102, 1120, 812, 16);
  ctx.stroke();

  // Top-Left Mode Tag inside 3D Viewport
  ctx.fillStyle = isRealRender ? 'rgba(120, 53, 15, 0.92)' : 'rgba(15, 23, 42, 0.9)';
  ctx.strokeStyle = isRealRender ? '#f59e0b' : '#475569';
  roundRect(ctx, 42, 120, 330, 36, 8);
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = isRealRender ? '#fef3c7' : '#e2e8f0';
  ctx.font = '700 13px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(isRealRender ? '✨ FINISHED WOOD & FABRIC STUDIO RENDER' : '🔧 3D CAD ENGINEERING VIEW', 56, 143);

  // Top-Right Camera Angle Readout inside 3D Viewport
  const camLabel = `CAM AZIMUTH ${{(theta * 180 / Math.PI).toFixed(0)}}° • ELEV ${{((Math.PI/2 - phi) * 180 / Math.PI).toFixed(0)}}°`;
  ctx.fillStyle = 'rgba(15, 23, 42, 0.9)';
  ctx.strokeStyle = '#475569';
  roundRect(ctx, 896, 120, 230, 36, 8);
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#93c5fd';
  ctx.font = '700 12px Menlo, monospace';
  ctx.textAlign = 'center';
  ctx.fillText(camLabel, 896 + 115, 143);

  // Bottom Active Parts Banner inside 3D Viewport
  ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
  ctx.strokeStyle = '#3b82f6';
  roundRect(ctx, 42, 846, 1084, 52, 10);
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#f59e0b';
  ctx.fillRect(42, 846, 6, 52);

  ctx.fillStyle = '#f8fafc';
  ctx.font = '700 15px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(ACTIVE_PARTS_LABELS[chapterIdx], 64, 877);

  // Z-Stack Pill inside Banner
  ctx.fillStyle = 'rgba(56, 189, 248, 0.15)';
  ctx.strokeStyle = '#38bdf8';
  roundRect(ctx, 835, 856, 275, 32, 6);
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#38bdf8';
  ctx.font = '700 12px Menlo, monospace';
  ctx.textAlign = 'center';
  ctx.fillText(Z_PILL_LABELS[chapterIdx], 835 + 137.5, 877);

  // Right Column Top: Orthographic Blueprint / Step SVG Card (x=1164, y=102, w=732, h=536)
  const useSecondary = tNorm >= 0.55;
  const svgIdx = useSecondary ? ch.svg_secondary_idx : ch.svg_primary_idx;
  const svgLabel = useSecondary ? ch.svg_secondary_label : ch.svg_primary_label;

  ctx.fillStyle = '#f8fafc';
  roundRect(ctx, 1164, 102, 732, 536, 14);
  ctx.fill();

  // Blueprint Header
  ctx.fillStyle = '#0f172a';
  roundRect(ctx, 1164, 102, 732, 44, 14);
  ctx.fill();
  ctx.fillRect(1164, 130, 732, 16);

  ctx.fillStyle = '#e2e8f0';
  ctx.font = '700 14px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText(svgLabel, 1182, 129);

  ctx.fillStyle = '#38bdf8';
  ctx.font = '700 11px Menlo, monospace';
  ctx.textAlign = 'right';
  ctx.fillText(useSecondary ? 'ARCHITECTURAL BLUEPRINT' : 'STEP CAD DIAGRAM', 1878, 129);

  // Draw SVG Image centered in Blueprint Card Body (x=1174, y=154, w=712, h=474)
  const svgImg = svgImages[svgIdx];
  if (svgImg && svgImg.complete && svgImg.naturalWidth > 0) {{
    const availW = 712, availH = 474;
    const scale = Math.min(availW / svgImg.naturalWidth, availH / svgImg.naturalHeight);
    const dw = svgImg.naturalWidth * scale;
    const dh = svgImg.naturalHeight * scale;
    const dx = 1174 + (availW - dw) / 2;
    const dy = 154 + (availH - dh) / 2;
    ctx.drawImage(svgImg, dx, dy, dw, dh);
  }}

  ctx.strokeStyle = '#334155';
  ctx.lineWidth = 2;
  roundRect(ctx, 1164, 102, 732, 536, 14);
  ctx.stroke();

  // Right Column Bottom: HUD Fasteners & Pro-Tip Card (x=1164, y=654, w=732, h=260)
  ctx.fillStyle = '#0f172a';
  ctx.strokeStyle = '#334155';
  roundRect(ctx, 1164, 654, 732, 260, 14);
  ctx.fill(); ctx.stroke();

  // Fasteners Block
  ctx.fillStyle = 'rgba(30, 41, 59, 0.85)';
  roundRect(ctx, 1184, 672, 692, 104, 10);
  ctx.fill();
  ctx.fillStyle = '#38bdf8';
  ctx.fillRect(1184, 672, 5, 104);
  ctx.font = '800 11px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('🔩 FASTENERS, LUMBER & KEY SPECS', 1204, 694);
  ctx.fillStyle = '#f1f5f9';
  ctx.font = '600 15px -apple-system, BlinkMacSystemFont, sans-serif';
  fillWrappedText(ctx, ch.fasteners, 1204, 720, 656, 22);

  // Pro-Tip Block
  ctx.fillStyle = 'rgba(30, 41, 59, 0.85)';
  roundRect(ctx, 1184, 792, 692, 104, 10);
  ctx.fill();
  ctx.fillStyle = '#10b981';
  ctx.fillRect(1184, 792, 5, 104);
  ctx.fillStyle = '#34d399';
  ctx.font = '800 11px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.fillText('💡 MASTER WOODWORKER PRO-TIP', 1204, 814);
  ctx.fillStyle = '#f1f5f9';
  ctx.font = '600 15px -apple-system, BlinkMacSystemFont, sans-serif';
  fillWrappedText(ctx, ch.pro_tip, 1204, 840, 656, 22);

  // Bottom Lower-Third Caption & Progress Bar (y=930..1080)
  ctx.fillStyle = '#090d16';
  ctx.fillRect(0, 930, 1920, 150);
  ctx.strokeStyle = '#1e293b';
  ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(0, 930); ctx.lineTo(1920, 930); ctx.stroke();

  // Deepgram Badge
  ctx.fillStyle = 'rgba(59, 130, 246, 0.16)';
  ctx.strokeStyle = 'rgba(59, 130, 246, 0.45)';
  roundRect(ctx, 28, 954, 175, 44, 10);
  ctx.fill(); ctx.stroke();
  ctx.fillStyle = '#60a5fa';
  ctx.font = '800 13px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('🔊 DEEPGRAM AURA', 28 + 87.5, 981);

  // Spoken Sentence Caption
  const sents = ch.sentences;
  const sIdx = Math.min(sents.length - 1, Math.floor(tNorm * sents.length));
  ctx.fillStyle = '#f8fafc';
  ctx.font = '600 21px -apple-system, BlinkMacSystemFont, sans-serif';
  ctx.textAlign = 'left';
  fillWrappedText(ctx, sents[sIdx], 224, 974, 1660, 28);

  // Global Progress Bar
  ctx.fillStyle = '#1e293b';
  roundRect(ctx, 28, 1044, 1740, 10, 5);
  ctx.fill();

  const pct = Math.max(0, Math.min(1, elapsedGlobalSec / totalGlobalSec));
  const fillGrad = ctx.createLinearGradient(28, 0, 1768, 0);
  fillGrad.addColorStop(0, '#3b82f6');
  fillGrad.addColorStop(1, '#f59e0b');
  ctx.fillStyle = fillGrad;
  roundRect(ctx, 28, 1044, Math.max(12, 1740 * pct), 10, 5);
  ctx.fill();

  // Time Readout
  ctx.fillStyle = '#94a3b8';
  ctx.font = '700 13px Menlo, monospace';
  ctx.textAlign = 'right';
  ctx.fillText(formatMMSS(elapsedGlobalSec) + ' / ' + formatMMSS(totalGlobalSec), 1892, 1054);

  return bCanvas.toDataURL('image/jpeg', 0.92);
}};
</script>
</body>
</html>
"""
    with open(STAGE_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(stage_html)
    print(f"Wrote Canvas Compositor stage HTML to {STAGE_HTML_PATH}")


if __name__ == "__main__":
    build_stage_html()
