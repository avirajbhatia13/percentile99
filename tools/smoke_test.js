/*
 * Headless load test: parses the REAL index.html with the current mocks.json inside
 * jsdom and confirms the app boots, every mock loads, and every answer/ctx is valid.
 *
 *   npm i jsdom        # once
 *   node tools/smoke_test.js
 *
 * Expect "REAL ERRORS: 0". A single "localStorage is not available for opaque origins"
 * line is a jsdom quirk and is filtered out.
 */
const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

const ROOT = path.dirname(__dirname);
let html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8')
  .replace(/<script[^>]*src=["']https?:\/\/[^"']*["'][^>]*><\/script>/g, ''); // drop CDN scripts
const mocks = fs.readFileSync(path.join(ROOT, 'mocks.json'), 'utf8');
const errs = [];

const dom = new JSDOM(html, {
  runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://localhost/',
  beforeParse(w) {
    w.matchMedia = () => ({ matches: false, addEventListener() {}, removeEventListener() {}, addListener() {}, removeListener() {} });
    w.scrollTo = () => {};
    w.supabase = { createClient: () => ({ auth: { getSession: () => Promise.resolve({ data: { session: null } }), onAuthStateChange: () => ({ data: { subscription: { unsubscribe() {} } } }) }, from: () => ({ select: () => ({ eq: () => Promise.resolve({ data: [], error: null }) }) }) }) };
    w.fetch = u => ('' + u).includes('mocks.json')
      ? Promise.resolve({ ok: true, json: () => Promise.resolve(JSON.parse(mocks)) })
      : Promise.resolve({ ok: false, json: () => Promise.resolve([]) });
    w.addEventListener('error', e => errs.push('ERR: ' + (e.error && e.error.stack || e.message)));
  },
});
process.on('unhandledRejection', e => errs.push('REJ: ' + (e && e.stack || e)));

setTimeout(() => {
  const w = dom.window;
  const M = JSON.parse(mocks);
  let q = 0;
  M.forEach(m => m.sections.forEach(s => s.qs.forEach(x => {
    q++;
    const t = `${m.id}/${s.name}/Q${x.n}`;
    if (x.type === 'mcq' && !(Number.isInteger(x.ans) && x.ans >= 0 && x.ans < 4 && (x.opts || []).length === 4)) errs.push('BAD mcq ' + t);
    if (x.type === 'tita' && typeof x.ans !== 'string') errs.push('BAD tita ' + t);
    if (x.c != null && !(x.c >= 0 && x.c < m.ctxs.length)) errs.push('BAD ctx ' + t);
    if (!x.sub) errs.push('NO sub ' + t);
  })));
  console.log('MOCKS in file :', M.length, '| questions:', q);
  console.log('App __MOCKS   :', (w.__MOCKS || []).length);
  const homeMetrics = w.document.getElementById('metricbar');
  console.log('Home rendered :', !!(homeMetrics && homeMetrics.children.length));
  const real = errs.filter(e => !e.includes('opaque origins'));
  console.log('REAL ERRORS   :', real.length);
  real.slice(0, 12).forEach(e => console.log('  ' + e.slice(0, 200)));
  process.exit(real.length ? 1 : 0);
}, 2000);
