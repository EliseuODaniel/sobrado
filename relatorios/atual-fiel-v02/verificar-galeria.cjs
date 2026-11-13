const {chromium}=require('/home/edann/.npm/_npx/9833c18b2d85bc59/node_modules/playwright');
const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/home/edann/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome'});const checks=[];const check=(name,ok)=>{checks.push({check:name,passed:!!ok});if(!ok)throw Error(name)};
 for(const viewport of [{width:1440,height:1000},{width:390,height:844}]){
  const page=await browser.newPage({viewport});const bad=[];page.on('pageerror',e=>bad.push(e.message));page.on('response',r=>{if(r.status()>=400)bad.push(r.url()+': '+r.status())});
  await page.goto('http://127.0.0.1:8058/renders/atual/galeria.html',{waitUntil:'networkidle'});
  await page.locator('footer').scrollIntoViewIfNeeded();await page.waitForTimeout(1000);
  await page.evaluate(async()=>{for(const i of document.images){i.loading='eager';await i.decode()}});
  check('Sem erros de recursos '+viewport.width,bad.length===0);check('Sem transbordar a tela '+viewport.width,await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  check('26 cartões de vistas '+viewport.width,await page.locator('#imagens article').count()===26);check('16 comparações '+viewport.width,await page.locator('#comparacoes article').count()===16);
  check('Imagens carregadas '+viewport.width,await page.evaluate(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0)));
  const links=await page.locator('a').evaluateAll(list=>[...new Set(list.map(a=>a.href))].filter(h=>!h.includes('#')));let failures=[];
  for(const link of links){const r=await page.request.head(link);if(!r.ok())failures.push({link,status:r.status()});await r.dispose()}
  check('Links funcionais '+viewport.width,failures.length===0);
  await page.screenshot({path:'relatorios/atual-fiel-v02/galeria-'+viewport.width+'.png',fullPage:false});await page.close();
 }
 await browser.close();fs.writeFileSync('relatorios/atual-fiel-v02/navegador-validacao.json',JSON.stringify({passed:true,checks,total:checks.length},null,2)+'\n');console.log('CURRENT2_BROWSER_OK',checks.length);
})().catch(e=>{console.error(e);process.exit(1)});
