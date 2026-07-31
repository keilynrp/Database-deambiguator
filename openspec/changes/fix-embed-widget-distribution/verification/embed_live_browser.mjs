// Task 4.4 — load the customer page in a real browser and record what a visitor
// sees. The point is not that the snippet strings are correct (unit tests pin
// that); it is that a browser on a third-party origin executes them.
// A bare Windows path is not a valid ESM specifier — it must be a file:// URL.
import { chromium } from 'file:///D:/universal-knowledge-intelligence-platform/frontend/node_modules/playwright-core/index.mjs';

const PAGE = 'http://localhost:8899/customer_page.html';

const browser = await chromium.launch({ channel: 'chrome', headless: true });
const ctx = await browser.newContext({ viewport: { width: 1280, height: 1100 } });
const page = await ctx.newPage();

const console_errors = [];
const failed = [];
const responses = [];

page.on('console', (m) => {
  if (m.type() === 'error') console_errors.push(m.text().slice(0, 220));
});
page.on('requestfailed', (r) =>
  failed.push(`${r.method()} ${r.url().slice(0, 90)} — ${r.failure()?.errorText}`)
);
page.on('response', (r) => {
  const u = r.url();
  if (u.includes('/embed/')) responses.push(`${r.status()} ${u.slice(0, 95)}`);
});

await page.goto(PAGE, { waitUntil: 'networkidle', timeout: 45000 });
// The JS snippet renders on a promise; the iframe loads its own bundle.
await page.waitForTimeout(6000);

const text = await page.evaluate(() => document.body.innerText);
const divs = await page.$$eval('div[id^="ukip-widget-"]', (ns) =>
  ns.map((n) => ({ id: n.id, text: n.innerText.replace(/\s+/g, ' ').trim().slice(0, 160) }))
);

const frames = [];
for (const f of page.frames()) {
  if (f === page.mainFrame()) continue;
  let body = '(unreadable)';
  try {
    body = (await f.evaluate(() => document.body.innerText)).replace(/\s+/g, ' ').trim().slice(0, 220);
  } catch (e) {
    body = `(error: ${e.message.slice(0, 80)})`;
  }
  frames.push({ url: f.url().slice(0, 90), body });
}

console.log('=== JS-snippet containers (what the customer site renders inline) ===');
for (const d of divs) console.log(`  #${d.id}\n    ${d.text || '(empty)'}`);

console.log('\n=== iframes (what the customer site frames) ===');
for (const f of frames) console.log(`  ${f.url}\n    ${f.body}`);

console.log('\n=== requests to /embed/* observed by the browser ===');
for (const r of [...new Set(responses)]) console.log('  ' + r);

console.log('\n=== console errors ===');
console.log(console_errors.length ? console_errors.map((e) => '  ' + e).join('\n') : '  (none)');

console.log('\n=== failed requests ===');
console.log(failed.length ? failed.map((e) => '  ' + e).join('\n') : '  (none)');

await page.screenshot({ path: 'customer_page.png', fullPage: true });
console.log('\n[ok] screenshot -> customer_page.png');
console.log('\n=== page text (first 700 chars) ===\n' + text.slice(0, 700));

await browser.close();
