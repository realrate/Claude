import puppeteer from '/Users/amnehqaljawi/.npm-global/lib/node_modules/puppeteer/lib/esm/puppeteer/puppeteer.js';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));

const slides = [
  { file: 'insight1_barfresh.html',     out: 'insight1_barfresh.png' },
  { file: 'insight2_kraft_heinz.html',  out: 'insight2_kraft_heinz.png' },
];

const browser = await puppeteer.launch({ headless: true });

for (const { file, out } of slides) {
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1080, deviceScaleFactor: 2 });
  await page.goto(`file://${join(__dirname, file)}`, { waitUntil: 'networkidle0' });
  await page.screenshot({ path: join(__dirname, out), type: 'png' });
  await page.close();
  console.log(`Exported: ${out}`);
}

await browser.close();
console.log('Done.');
