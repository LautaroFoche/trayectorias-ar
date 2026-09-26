// Verificación del DOM en memoria; no abre un navegador ni solicita recursos remotos.
const fs=require('node:fs');
const assert=require('node:assert/strict');
const {JSDOM,VirtualConsole}=require('jsdom');
const release=process.argv[2] || 'reports/current';
const html=fs.readFileSync(release+'/dashboard.html','utf8');
const errors=[];
const vc=new VirtualConsole();vc.on('jsdomError',error=>errors.push(error));
const dom=new JSDOM(html,{runScripts:'dangerously',virtualConsole:vc,url:'https://example.invalid/'});
const d=dom.window.document;
assert.deepEqual(errors,[]);
const select=(id,value)=>{d.getElementById(id).value=value;d.getElementById(id).dispatchEvent(new dom.window.Event('change'));assert.deepEqual(errors,[])};
for(const button of d.querySelectorAll('.navbtn')){button.click();assert.equal(d.querySelectorAll('.panel:not([hidden])').length,1);assert.equal(d.querySelector('.panel:not([hidden])').id,button.dataset.panel)}
assert.equal(d.querySelectorAll('#table tr').length,24);
for(const level of ['primaria','secundaria']){select('level',level);for(const option of d.querySelectorAll('#geo option'))select('geo',option.value)}
select('country','ARG');select('metric','SE.PRM.ENRL.TC.ZS');select('contextYear','2024');
assert.match(d.getElementById('wdiValue').textContent,/Sin dato/);
assert.match(d.getElementById('freshness').textContent,/2008/);
for(const option of d.querySelectorAll('#metric option')){select('metric',option.value);for(const country of ['ARG','BRA','CHL','URY'])select('country',country)}
select('pisaCountry','ARG');assert.match(d.getElementById('coefficientNote').textContent,/incluye cero/);
for(const country of ['ARG','BRA','CHL','URY','OECD']){select('pisaCountry',country);select('purpose','matematica_aprendizaje');select('purpose','matematica_ocio')}
assert.equal(d.querySelectorAll('#kidsTable tr').length,22);
assert.equal(d.querySelectorAll('#sourceTable tr').length,16);
assert.equal(d.querySelectorAll('#digitalCards .card').length,4);
for(const a of d.querySelectorAll('a[href]')){const href=a.getAttribute('href');if(!/^https?:/.test(href))assert.ok(fs.existsSync(release+'/'+href),href)}
assert.ok(!d.body.textContent.includes('__PAYLOAD__'));
assert.deepEqual(errors,[]);
console.log('PASS: 5 secciones; 24 provincias; filtros educativos, 8 series × 4 países, 5 países PISA; nulos, rezago, denominadores y enlaces locales.');
dom.window.close();
