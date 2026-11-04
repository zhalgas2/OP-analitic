// Rasterises the master SVG illustrations to WebP (320px and 640px).
// Usage: node tools/render_webp.mjs
import { createRequire } from 'module';
import { readFileSync, writeFileSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const dir = join(dirname(fileURLToPath(import.meta.url)), '..', 'assets', 'illustrations');

const browser = await chromium.launch();
const page = await browser.newPage();
for (const name of ['alippe', 'iqro', 'tajweed', 'quran']) {
  const svg = readFileSync(join(dir, `${name}.svg`), 'utf8');
  for (const size of [320, 640]) {
    const dataUrl = await page.evaluate(async ({ svg, size }) => {
      const img = new Image();
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg);
      await img.decode();
      const c = document.createElement('canvas');
      c.width = c.height = size;
      c.getContext('2d').drawImage(img, 0, 0, size, size);
      return c.toDataURL('image/webp', 0.9);
    }, { svg, size });
    const out = join(dir, `${name}-${size}.webp`);
    writeFileSync(out, Buffer.from(dataUrl.split(',')[1], 'base64'));
    console.log('wrote', out);
  }
}
await browser.close();
