import puppeteer from 'puppeteer';
import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { readdirSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));

const files = process.argv.slice(2).length
  ? process.argv.slice(2)
  : readdirSync(__dirname).filter(f => f.endsWith('.html'));

const browser = await puppeteer.launch();

for (const file of files) {
  const htmlPath = resolve(__dirname, file);
  const pngPath = htmlPath.replace(/\.html$/, '.png');

  const page = await browser.newPage();
  await page.setViewport({ width: 1200, height: 1200, deviceScaleFactor: 2 });
  await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });
  await page.screenshot({ path: pngPath, clip: { x: 0, y: 0, width: 1200, height: 1200 } });
  await page.close();

  console.log(`Exported: ${pngPath}`);
}

await browser.close();
