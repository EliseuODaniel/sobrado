const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const {chromium} = require('/home/edann/.npm/_npx/9833c18b2d85bc59/node_modules/playwright');
(async () => {
  const report = path.resolve('relatorios/industrial-v06');
  const model = JSON.parse(fs.readFileSync(path.join(report, 'modelo.json')));
  const delivery = JSON.parse(fs.readFileSync(path.join(report, 'validacao-entrega.json')));
  assert(delivery.all_passed);
  const browser = await chromium.launch({headless: true, executablePath: '/home/edann/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome', args: ['--no-sandbox']});
  const checks = [], errors = [], requests = [];
  try {
    const page = await browser.newPage({viewport: {width: 1440, height: 1100}});
    page.on('pageerror', error => errors.push(String(error)));
    page.on('response', response => {if (response.status() >= 400) requests.push({url: response.url(), status: response.status()});});
    await page.goto('http://127.0.0.1:8057/renders/industrial-v06/galeria.html', {waitUntil: 'networkidle'});
    assert.equal(await page.locator('figure').count(), 31);
    // Carregar também miniaturas abaixo da dobra, sem baixar os PNGs 4K.
    await page.locator('img').evaluateAll(images => images.forEach(image => image.loading = 'eager'));
    await page.waitForFunction(() => [...document.images].every(image => image.complete && image.naturalWidth > 0));
    checks.push({name: '31 cards and all thumbnails decode', passed: true, images: await page.locator('img').count()});
    const counts = {ambientes: 19, 'dia-noite': 6, plantas: 4, exteriores: 2, todos: 31};
    for (const [kind, count] of Object.entries(counts)) {
      await page.locator(`[data-filter="${kind}"]`).click();
      assert.equal(await page.locator('figure:visible').count(), count);
      assert.equal(await page.locator('[data-filter][aria-pressed="true"]').count(), 1);
      checks.push({name: `filter ${kind}`, passed: true, count});
    }
    const ranges = page.locator('.pair input[type=range]');
    assert.equal(await ranges.count(), 3);
    for (let i = 0; i < 3; i++) {
      const range = ranges.nth(i);
      await range.focus(); await range.press('Home');
      assert.equal(await range.inputValue(), '0');
      assert.match(await range.locator('xpath=ancestor::section').locator('.day').getAttribute('style'), /inset\(0(?:px)? 100%/);
      await range.press('End');
      assert.equal(await range.inputValue(), '100');
      assert.match(await range.locator('xpath=ancestor::section').locator('.day').getAttribute('style'), /inset\(0(?:px)? 0%/);
      await range.evaluate(input => {input.value = '50'; input.dispatchEvent(new Event('input', {bubbles: true}));});
    }
    checks.push({name: 'three accessible day/night sliders respond at both ends', passed: true});
    const links = await page.locator('a[href]').evaluateAll(links => [...new Set(links.map(link => link.href))]);
    for (const url of links) {
      const response = await page.request.head(url);
      assert.equal(response.status(), 200, url);
    }
    checks.push({name: 'all gallery links respond to HEAD', passed: true, count: links.length});
    await page.evaluate(() => window.scrollTo(0, 0));
    await page.screenshot({path: path.join(report, 'galeria-final-desktop.png')});
    for (const width of [1440, 390]) {
      await page.setViewportSize({width, height: width === 390 ? 844 : 1100});
      assert(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
      checks.push({name: `no horizontal overflow at ${width}px`, passed: true});
    }
    await page.evaluate(() => {document.activeElement.blur(); window.scrollTo(0, 0);});
    await page.screenshot({path: path.join(report, 'galeria-final-mobile.png')});
    assert.deepEqual(errors, []); assert.deepEqual(requests, []);
    checks.push({name: 'no page errors or HTTP failures', passed: true});
    fs.writeFileSync(path.join(report, 'browser-final.json'), JSON.stringify({timestamp_utc: new Date().toISOString(), blend_sha256: model.blend_sha256, checks, all_passed: true, errors, requests, scope: 'Galeria local final em Chromium, filtros, sliders, miniaturas, links e desktop/mobile.'}, null, 2) + '\n');
    console.log('PHOTO6_BROWSER', checks.length, 'PASSED');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
