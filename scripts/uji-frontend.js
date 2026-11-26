// scripts/uji-frontend.js — regresi frontend portabel untuk CI (4.1).
// Adaptasi dari harness lokal uji-2.3.js: fixtures backend/tests/fixtures/
// ada dan bisa dibaca, dan pemeriksa JS di index.html memberi
// skor/lulus/kode sesuai manifest.json (plus bisa dibuat ulang identik
// dari seed).
//
// Dijalankan:  node scripts/uji-frontend.js
//   (dari root repo; butuh SheetJS: npm install --no-save xlsx@0.18.5)
// Keluar 0 bila semua cek lolos; 1 bila ada yang gagal.
//
// Catatan: regresi penuh 1055 cek (harness lokal ~/workspace/oq-test/)
// tetap dijalankan lokal sebelum dorong; yang di CI adalah inti
// pemeriksa ini (138 cek).
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const XLSX = require('xlsx');
globalThis.XLSX = XLSX;
const store = new Map();
globalThis.localStorage = { getItem: (k) => (store.has(k) ? store.get(k) : null), setItem: (k, v) => store.set(k, String(v)), removeItem: (k) => store.delete(k), clear: () => store.clear() };
let lebarHP = false;
const registry = new Set();
function elStub() {
  const cls = new Set(); const attrs = new Map(); const handlers = {};
  const el = { classList: { add: (...n) => n.forEach((x) => cls.add(x)), remove: (...n) => n.forEach((x) => cls.delete(x)), toggle: (n, f) => { if (f === undefined) { cls.has(n) ? cls.delete(n) : cls.add(n); } else if (f) cls.add(n); else cls.delete(n); }, contains: (n) => cls.has(n) }, style: {}, dataset: {}, children: [], textContent: '', value: '', hidden: false, disabled: false, scrollTop: 0, scrollHeight: 0, offsetWidth: 0, offsetHeight: 0, setAttribute: (k, v) => attrs.set(k, String(v)), getAttribute: (k) => (attrs.has(k) ? attrs.get(k) : null), removeAttribute: (k) => attrs.delete(k), appendChild(c) { this.children.push(c); return c; }, append() {}, querySelector: () => elStub(), querySelectorAll: () => [], addEventListener(type, fn) { (handlers[type] = handlers[type] || []).push(fn); }, removeEventListener() {}, focus() {}, click() {}, scrollIntoView() {}, closest: () => null, contains: () => false, remove() {}, getBoundingClientRect: () => ({ left: 0, top: 0, right: 0, bottom: 0, width: 0, height: 0 }), _handlers: handlers };
  registry.add(el); return el;
}
const byId = new Map(); const bodyCls = new Set();
globalThis.document = { body: { classList: { add: (...n) => n.forEach((x) => bodyCls.add(x)), remove: (...n) => n.forEach((x) => bodyCls.delete(x)), toggle: (n, f) => { if (f === undefined) { bodyCls.has(n) ? bodyCls.delete(n) : bodyCls.add(n); } else if (f) bodyCls.add(n); else bodyCls.delete(n); }, contains: (n) => bodyCls.has(n) } }, activeElement: null, getElementById: (id) => { if (!byId.has(id)) byId.set(id, elStub()); return byId.get(id); }, querySelector: () => elStub(), querySelectorAll: () => [], createElement: () => elStub(), addEventListener() {} };
globalThis.window = globalThis;
globalThis.matchMedia = (q) => ({ matches: false, addEventListener() {}, removeEventListener() {} });
globalThis.addEventListener = () => {};
globalThis.location = { hash: '', pathname: '/office-quest/', search: '' };
globalThis.navigator = {};
globalThis.setTimeout = (fn) => { fn(); return 0; };
const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)];
let src = scripts[scripts.length - 1][1];
src = src.replace(/^\s*init\(\);\s*$/m, '');
src += `\nglobalThis.__g = { state, DATA_TUGAS, periksaFileXlsx, buatFileUji, HASIL_UJI_DIHARAPKAN };`;
eval(src);
const G = globalThis.__g;

let lolos = 0, gagal = 0; const gagalApa = [];
function cek(nama, kondisi, info) {
  if (kondisi) { lolos++; }
  else { gagal++; gagalApa.push(nama + (info ? ' — ' + info : '')); console.log('  GAGAL:', nama, info ? '(' + info + ')' : ''); }
}

const DIR = path.join(ROOT, 'backend', 'tests', 'fixtures');
const manifes = JSON.parse(fs.readFileSync(path.join(DIR, 'manifest.json'), 'utf8'));
cek('manifest punya seed', typeof manifes.seed === 'string' && manifes.seed.length > 0, manifes.seed);
cek('manifest punya 15 entri', Array.isArray(manifes.fixtures) && manifes.fixtures.length === 15, 'dapat ' + (manifes.fixtures || []).length);
const TUGAS = ['rekap_penjualan', 'absensi', 'penilaian_magang'];
const VARIAN = ['benar', 'nilai-salah', 'manual', 'error', 'data-diubah'];
cek('semua kombinasi tugas x varian ada', TUGAS.every((t) => VARIAN.every((v) => manifes.fixtures.some((f) => f.tugas === t && f.varian === v))));
G.state.seed = manifes.seed;
manifes.fixtures.forEach((f) => {
  const p = `${f.file}: `;
  const filePath = path.join(DIR, f.file);
  cek(p + 'file ada', fs.existsSync(filePath));
  if (!fs.existsSync(filePath)) return;
  const bytes = fs.readFileSync(filePath);
  cek(p + 'bukan file kosong', bytes.length > 1000, bytes.length + ' byte');
  let wb = null;
  try { wb = XLSX.read(bytes, { type: 'buffer', cellFormula: true }); cek(p + 'bisa dibaca SheetJS', true); }
  catch (e) { cek(p + 'bisa dibaca SheetJS', false, e.message); }
  if (wb) cek(p + 'punya sheet Data', !!wb.Sheets.Data, Object.keys(wb.Sheets).join(','));
  const hasil = G.periksaFileXlsx(new Uint8Array(bytes), manifes.seed, G.DATA_TUGAS[f.tugas].checks);
  cek(p + 'skor sesuai manifes', hasil.skor === f.skor, `dapat ${hasil.skor}, manifes ${f.skor}`);
  cek(p + 'lulus sesuai manifes', hasil.lulus === f.lulus, `dapat ${hasil.lulus}, manifes ${f.lulus}`);
  cek(p + 'kode sesuai manifes', hasil.kode.join(',') === f.kode.join(','), `dapat [${hasil.kode}], manifes [${f.kode}]`);
  const diharap = G.HASIL_UJI_DIHARAPKAN[f.tugas][VARIAN.indexOf(f.varian)];
  cek(p + 'manifes cocok HASIL_UJI_DIHARAPKAN', f.skor === diharap.skor && f.lulus === diharap.lulus && f.kode.join(',') === diharap.kode.join(','));
  const ulang = G.buatFileUji(f.tugas, f.varian);
  cek(p + 'bisa dibuat ulang identik dari seed', Buffer.compare(Buffer.from(ulang), bytes) === 0, `panjang ulang ${ulang.length} vs file ${bytes.length}`);
});
console.log(`\nHASIL uji-frontend: ${lolos} lolos, ${gagal} gagal`);
if (gagal > 0) { console.log('Yang gagal:'); gagalApa.forEach((g) => console.log(' -', g)); process.exit(1); }
