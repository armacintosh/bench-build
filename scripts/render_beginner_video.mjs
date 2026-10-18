#!/usr/bin/env node
/**
 * Renders 1920x1080 frames from `.video_build/beginner_studio_stage.html`
 * and muxes each step with its plain-English Deepgram Aura TTS audio into
 * `modular_couch_beginner_video.mp4`.
 */
import fs from 'node:fs';
import path from 'node:path';
import { spawn, execFileSync } from 'node:child_process';

const BASE_DIR = process.cwd();
const VIDEO_BUILD_DIR = path.join(BASE_DIR, '.video_build');
const FRAMES_DIR = path.join(VIDEO_BUILD_DIR, 'frames_beginner');
const SEGMENTS_DIR = path.join(VIDEO_BUILD_DIR, 'segments_beginner');
const MANIFEST_PATH = path.join(VIDEO_BUILD_DIR, 'beginner_manifest.json');
const STAGE_URL = 'file://' + path.join(VIDEO_BUILD_DIR, 'beginner_studio_stage.html');
const OUTPUT_MP4 = path.join(BASE_DIR, 'modular_couch_beginner_video.mp4');

fs.mkdirSync(FRAMES_DIR, { recursive: true });
fs.mkdirSync(SEGMENTS_DIR, { recursive: true });

const CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const CDP_PORT = 9298;
const FPS = 5; // 5 keyframes/sec of smooth 3D animation, encoded at 30fps H.264

function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function getPageWsUrl(port) {
  for (let attempt = 0; attempt < 40; attempt++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/list`);
      const pages = await res.json();
      const page = pages.find(p => p.type === 'page' && p.webSocketDebuggerUrl);
      if (page) return page.webSocketDebuggerUrl;
    } catch (_) {}
    await sleep(150);
  }
  throw new Error('Timed out waiting for Chrome DevTools target');
}

class CDPClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.id = 0;
    this.pending = new Map();
  }
  async connect() {
    this.ws = new WebSocket(this.wsUrl);
    await new Promise((resolve, reject) => {
      this.ws.addEventListener('open', resolve, { once: true });
      this.ws.addEventListener('error', reject, { once: true });
    });
    this.ws.addEventListener('message', ev => {
      const msg = JSON.parse(ev.data);
      if (msg.id && this.pending.has(msg.id)) {
        const { resolve, reject } = this.pending.get(msg.id);
        this.pending.delete(msg.id);
        if (msg.error) reject(new Error(msg.error.message));
        else resolve(msg.result);
      }
    });
  }
  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  close() {
    this.ws.close();
  }
}

async function main() {
  const chapters = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf8'));
  const totalDuration = chapters.reduce((acc, c) => acc + c.duration, 0);

  console.log(`Launching headless Chrome on port ${CDP_PORT}...`);
  const chromeProc = spawn(CHROME_PATH, [
    '--headless=new',
    `--remote-debugging-port=${CDP_PORT}`,
    '--window-size=1920,1080',
    '--hide-scrollbars',
    '--mute-audio',
    '--no-first-run',
    '--no-default-browser-check',
    `--user-data-dir=${path.join(VIDEO_BUILD_DIR, 'chrome_profile_beginner')}`,
    STAGE_URL
  ], { stdio: 'ignore' });

  try {
    const wsUrl = await getPageWsUrl(CDP_PORT);
    const cdp = new CDPClient(wsUrl);
    await cdp.connect();
    await cdp.send('Runtime.enable');

    for (let i = 0; i < 60; i++) {
      const check = await cdp.send('Runtime.evaluate', {
        expression: 'Boolean(typeof window.renderBroadcastFrame === "function" && window.allAssetsReady)',
        returnByValue: true
      });
      if (check?.result?.value === true) break;
      await sleep(100);
    }
    console.log('Full-screen 1080p Beginner 3D Stage Ready!');

    let globalElapsed = 0;
    const segmentFiles = [];
    const t0 = Date.now();

    for (let chIdx = 0; chIdx < chapters.length; chIdx++) {
      const ch = chapters[chIdx];
      const chFramesDir = path.join(FRAMES_DIR, ch.id);
      fs.mkdirSync(chFramesDir, { recursive: true });

      const numFrames = Math.max(8, Math.ceil(ch.duration * FPS));
      console.log(`Rendering Beginner Step ${chIdx + 1}/${chapters.length} [${ch.id}] (${ch.duration}s -> ${numFrames} frames)...`);

      for (let f = 0; f < numFrames; f++) {
        const tNorm = numFrames > 1 ? f / (numFrames - 1) : 0;
        const curGlobal = globalElapsed + tNorm * ch.duration;

        const evalRes = await cdp.send('Runtime.evaluate', {
          expression: `window.renderBroadcastFrame(${chIdx}, ${tNorm.toFixed(4)}, ${curGlobal.toFixed(2)}, ${totalDuration.toFixed(2)})`,
          returnByValue: true
        });

        const dataUrl = evalRes?.result?.value;
        if (!dataUrl || !dataUrl.startsWith('data:image/jpeg;base64,')) {
          throw new Error(`Invalid frame data returned at chapter ${chIdx} frame ${f}`);
        }
        const b64 = dataUrl.slice('data:image/jpeg;base64,'.length);
        const framePath = path.join(chFramesDir, `frame_${String(f).padStart(4, '0')}.jpg`);
        fs.writeFileSync(framePath, Buffer.from(b64, 'base64'));
      }

      globalElapsed += ch.duration;

      const segMp4 = path.join(SEGMENTS_DIR, `${ch.id}.mp4`);
      execFileSync('ffmpeg', [
        '-y',
        '-framerate', String(FPS),
        '-i', path.join(chFramesDir, 'frame_%04d.jpg'),
        '-i', ch.audio_file,
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-r', '30',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', '44100',
        '-shortest',
        segMp4
      ], { stdio: 'ignore' });

      segmentFiles.push(segMp4);
      const elapsedSec = ((Date.now() - t0) / 1000).toFixed(1);
      console.log(`  -> Encoded ${path.basename(segMp4)} (${elapsedSec}s elapsed)`);
    }

    cdp.close();

    const concatListPath = path.join(VIDEO_BUILD_DIR, 'concat_beginner_list.txt');
    const concatTxt = segmentFiles.map(p => `file '${p}'`).join('\n') + '\n';
    fs.writeFileSync(concatListPath, concatTxt);

    console.log('Concatenating all 9 chapters into modular_couch_beginner_video.mp4...');
    execFileSync('ffmpeg', [
      '-y',
      '-f', 'concat',
      '-safe', '0',
      '-i', concatListPath,
      '-c:v', 'copy',
      '-c:a', 'aac',
      '-b:a', '192k',
      '-movflags', '+faststart',
      OUTPUT_MP4
    ], { stdio: 'ignore' });

    const stat = fs.statSync(OUTPUT_MP4);
    console.log(`\nSUCCESS! Created ${OUTPUT_MP4} (${(stat.size / (1024 * 1024)).toFixed(2)} MB)`);
  } finally {
    chromeProc.kill('SIGKILL');
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
