#!/usr/bin/env python3
"""
Generates voiceover narration segments using Deepgram Aura TTS API
for the 80" x 29" Heavy-Duty Modular Playroom Couch / Bench / Table instructional video.
"""
import json
import os
import subprocess
import urllib.request
import urllib.error

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR) if os.path.basename(SCRIPT_DIR) == "scripts" else SCRIPT_DIR
VIDEO_BUILD_DIR = os.path.join(BASE_DIR, ".video_build")
AUDIO_DIR = os.path.join(VIDEO_BUILD_DIR, "audio")
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


CHAPTERS = [
    {
        "id": "00_intro",
        "phase_num": 0,
        "badge": "OVERVIEW & SPECS",
        "title": "80\" × 29\" Modular Playroom Couch, Bench & Table",
        "subtitle": "Coplanar Torsion-Box Architecture • >1,000 lb Dynamic Rating • 71.5\" × 15.5\" Basket Bay",
        "fasteners": "5× Notched 4×4 Legs (18-5/8\") • Dual 2×4 Laminated Beam • 3/4\" Birch Deck • 1×6 Trim Lip",
        "pro_tip": "Rear legs ride on recessed 3/8\" rollers while front legs grip on 3/8\" rubber pads—lift front 1\" to roll!",
        "narration": (
            "Welcome to the step-by-step CAD workshop walkthrough for the eighty-inch by twenty-nine-inch "
            "Heavy-Duty Modular Playroom Couch, Bench, and Activity Table. Engineered around a coplanar "
            "torsion-box frame rated for over one thousand pounds, it features a seventy-one-and-a-half-inch "
            "unobstructed front basket bay, a one-inch recessed cushion pocket, hidden wheelbarrow rear rollers, "
            "and two forty-inch drop-in slanted backrests."
        ),
    },
    {
        "id": "01_cut_maps",
        "phase_num": 0,
        "badge": "PRE-BUILD CUT MAPS",
        "title": "Master Cut List & Doubled 2×6 Backrest Layout",
        "subtitle": "Parts A–M • 1 Sheet 3/4\" Birch Plywood + Two 2×6 Boards (8 Halves → 4 Doubled Posts)",
        "fasteners": "Part G: 78.50\" × 23.75\" Deck • Part L: 2× 39.25\" × 15.0\" Back Panels • Part K: 8× 23.5\" 2×6 Halves",
        "pro_tip": "Cut 8 identical 23.5\" halves from two 8-foot 2×6 boards (90° rear shoulder ledge + 10° front lean) and glue in pairs!",
        "narration": (
            "Before cutting, label every board from Part A through Part M. From one sheet of three-quarter-inch "
            "birch plywood, rip the seventy-eight-and-a-half by twenty-three-and-three-quarter-inch seat deck "
            "and two backrest panels. From two eight-foot two-by-six boards, cut eight twenty-three-and-a-half-inch halves, "
            "each with a one-and-seven-sixteenths-inch bottom peg, a ninety-degree solid wood rear shoulder ledge, and a ten-degree front lean."
        ),
    },
    {
        "id": "02_phase1_legs",
        "phase_num": 1,
        "badge": "PHASE 1 OF 7",
        "title": "Prepping the Five Notched 4×4 Legs & Rollers",
        "subtitle": "Z = 0.00\" to 19.00\" • 18-5/8\" Post Length • 1.5\" × 3.5\" Top Half-Lap Notches",
        "fasteners": "3× Recessed Rear Rollers (#8 × 1\" pan-head) • 2× Front 3/8\" Rubber Grip Pads",
        "pro_tip": "Set your circular saw depth to 1-1/2\" and make kerf cuts every 1/4\" across the top 3-1/2\" of each 4×4.",
        "narration": (
            "Phase One: Prep the five four-by-four legs, cut to exactly eighteen and five-eighths inches. "
            "Bore the recessed roller mortises into the bottom of the three rear legs so the wheels protrude "
            "three-eighths of an inch, and screw three-eighths-inch solid rubber grip pads to the two front legs. "
            "Then cut the one-and-a-half by three-and-a-half-inch top half-lap notches so every two-by-four rail rests on solid end-grain."
        ),
    },
    {
        "id": "03_phase2_beams",
        "phase_num": 2,
        "badge": "PHASE 2 OF 7",
        "title": "Laminating the Front Beam & Perimeter Frames",
        "subtitle": "Z = 15.50\" to 19.00\" • 3.0\" × 3.5\" Structural Header Over 71.50\" Clear Span",
        "fasteners": "16× 2-3/4\" #10 Lamination Screws + 10× 3\" #10 Structural Lag Screws + Titebond Glue",
        "pro_tip": "Crown both front 2×4s upward (cupping up at center) before face-gluing to counteract gravity sag.",
        "narration": (
            "Phase Two: Build the unbreakable front beam and rear frame. Face-glue and clamp two "
            "seventy-eight-and-a-half-inch two-by-fours together, driving two-and-three-quarter-inch structural "
            "screws in a staggered pattern. Seat this three-inch-thick laminated beam into the front leg notches, "
            "and anchor the rear rail across all three back legs using three-inch structural lag screws and wood glue."
        ),
    },
    {
        "id": "04_phase3_grid",
        "phase_num": 3,
        "badge": "PHASE 3 OF 7",
        "title": "Ladder Joist Grid & Four 3-1/8\" × 1-1/2\" Slots",
        "subtitle": "5 Interior Joists (X = 16\", 28\", 40\", 52\", 64\") + 5 Spacers (5.50\", 21.25\", 12.50\")",
        "fasteners": "24× 2-1/2\" HD Pocket Screws + 24× 3\" #10 Structural Screws Through Spacer Blocks",
        "pro_tip": "Use a 3.00\" doubled block plus a 1/8\" shim as a spacer gauge so every slot is 3-1/8\" × 1-1/2\"!",
        "narration": (
            "Phase Three: Assemble the ladder joist grid and four rear backrest slots. Connect the front "
            "and rear assemblies with side rails and five interior cross-joists spaced at sixteen, twenty-eight, "
            "forty, fifty-two, and sixty-four inches. Behind the main back rail, install five spacer blocks "
            "at five and a half, twenty-one and a quarter, and twelve and a half inches, leaving four open slots "
            "that are three and one-eighth inches wide by one and a half inches deep."
        ),
    },
    {
        "id": "05_phase4_deck",
        "phase_num": 4,
        "badge": "PHASE 4 OF 7",
        "title": "Installing the 3/4\" Birch Plywood Torsion Deck",
        "subtitle": "Z = 19.00\" to 19.75\" • 78.50\" × 23.75\" Stressed-Skin Seat Deck + 1×2 Pocket Caps",
        "fasteners": "36× #8 × 1-3/4\" Countersunk Deck Screws (8\" O.C.) + 10× #8 × 1-1/2\" Trim Screws",
        "pro_tip": "Check frame diagonals for exact equality before screwing down the plywood—the deck permanently locks squareness.",
        "narration": (
            "Phase Four: Lock in the three-quarter-inch birch plywood seat deck. Apply a continuous bead of "
            "wood glue across the top of the two-by-four grid and set the seventy-eight-and-a-half by "
            "twenty-three-and-three-quarter-inch deck flush with the front beam, leaving the rear mortise channel open. "
            "Drive one-and-three-quarter-inch deck screws every eight inches, turning the frame into a rigid torsion box."
        ),
    },
    {
        "id": "06_phase5_trim",
        "phase_num": 5,
        "badge": "PHASE 5 OF 7",
        "title": "Wrapping the Blind-Fastened 1×6 Stain-Grade Apron",
        "subtitle": "Z = 15.25\" to 20.75\" • Projects 1.00\" Above Deck to Form the Recessed Cushion Tray",
        "fasteners": "32× #8 × 1-7/8\" Pan-Head Screws Driven From Inside 2×4 Frame (Zero Visible Outer Screws)",
        "pro_tip": "Use 1\" scrap blocks resting on the plywood deck to set the exact 1.00\" upper cushion lip all around.",
        "narration": (
            "Phase Five: Wrap the perimeter in stain-grade one-by-six apron trim with forty-five-degree mitered corners. "
            "Position each board so its top edge rises exactly one inch above the plywood deck, creating the recessed "
            "cushion tray. Drive one-and-seven-eighths-inch trim screws from the inside of the two-by-four framing into "
            "the back of the trim—leaving flawless, screw-free outer hardwood faces."
        ),
    },
    {
        "id": "07_phase6_backrests",
        "phase_num": 6,
        "badge": "PHASE 6 OF 7",
        "title": "Doubled 3.00\"-Wide 2×6 Uprights & 10° Backrests",
        "subtitle": "Z = 15.50\" to 39.00\" • 90° Solid Wood Rear Shoulder Ledge on Z = 19.75\" + 10° Front Lean",
        "fasteners": "20× 2-3/4\" #10 Lamination Screws + 16× #8 × 1-3/4\" Panel Screws + Wood Glue",
        "pro_tip": "The 90° solid wood rear shoulder ledge sits flat on top of the couch (6.75 sq in per post) for rock-solid support!",
        "narration": (
            "Phase Six: Build the four doubled two-by-six uprights and attach the backrest panels. "
            "Each two-by-six stands with its five-and-a-half-inch width running front-to-back, featuring a ninety-degree "
            "solid wood rear shoulder ledge that rests flat on top of the couch surface, a vertical back edge, and a ten-degree "
            "front lean. Glue and screw the eight halves together in pairs to form four three-inch-wide posts, "
            "screw the thirty-nine-and-a-quarter-inch birch panels onto the wide front faces, and drop both backrests into the slots."
        ),
    },
    {
        "id": "08_phase7_finish",
        "phase_num": 7,
        "badge": "PHASE 7 OF 7 • FINALE",
        "title": "Sanding, Waxing Tenons & Cushion / Table Conversion",
        "subtitle": "78.0\" × 23.5\" × 4.0\" High-Density Cushion • Paraffin-Waxed Tenons • Wheelbarrow Mobility",
        "fasteners": "80/120/180-Grit Sandpaper • Satin Polyurethane • Paraffin Wax on Raw Tenons",
        "pro_tip": "NEVER stain or varnish the bottom 4.25\" of the backrest tenons—rub them with candle wax for zero-bind glide!",
        "narration": (
            "Phase Seven: Sand all surfaces through one-eighty grit, apply finish, and rub paraffin wax onto the "
            "four backrest tenons—never stain or varnish the tenons so they glide smoothly. Drop in the seventy-eight "
            "by twenty-three-and-a-half-inch foam cushion and back pillows. Lift the front apron one inch to roll on "
            "the hidden rear wheels, or pull out both backrests in seconds for flat table mode."
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


def synthesize_chapter(api_key: str, chapter: dict, model: str = "aura-2-orion-en") -> dict:
    mp3_path = os.path.join(AUDIO_DIR, f"{chapter['id']}.mp3")
    if not os.path.exists(mp3_path) or os.path.getsize(mp3_path) < 1000:
        url = f"https://api.deepgram.com/v1/speak?model={model}"
        payload = json.dumps({"text": chapter["narration"]}).encode("utf-8")
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
                audio_bytes = resp.read()
                with open(mp3_path, "wb") as f:
                    f.write(audio_bytes)
        except urllib.error.HTTPError as e:
            if model != "aura-orion-en":
                print(f"Fallback from {model} to aura-orion-en ({e.code})")
                return synthesize_chapter(api_key, chapter, model="aura-orion-en")
            raise
    dur = get_audio_duration(mp3_path)
    print(f"[OK] {chapter['id']}: {dur:.2f}s ({os.path.getsize(mp3_path) // 1024} KB)")
    return {**chapter, "audio_file": mp3_path, "duration": round(dur, 3)}


def main():
    api_key = load_deepgram_key()
    manifest = []
    total_dur = 0.0
    for ch in CHAPTERS:
        info = synthesize_chapter(api_key, ch)
        manifest.append(info)
        total_dur += info["duration"]
    manifest_path = os.path.join(VIDEO_BUILD_DIR, "chapters_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nTotal voiceover duration across {len(manifest)} chapters: {total_dur:.2f}s ({total_dur/60:.2f} min)")
    print(f"Saved manifest to {manifest_path}")


if __name__ == "__main__":
    main()
