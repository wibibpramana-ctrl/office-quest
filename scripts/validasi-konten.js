#!/usr/bin/env node
// scripts/validasi-konten.js — validasi file JSON di content/ (Tahap 2, Langkah 1.6).
// Acuan: docs/skema-konten.md (Langkah 1.1).
//
// Pakai:
//   node scripts/validasi-konten.js [folder-repo]
//   Tanpa argumen: folder saat ini (harus berisi content/).
//   Folder lain: node scripts/validasi-konten.js /jalan/ke/repo
//
// Keluar 0 bila semua file lolos; 1 bila ada yang gagal.
// Peringatan (mis. foto masih data URI = utang migrasi) tidak menggagalkan.
//
// Yang diperiksa:
//   - Umum: JSON bisa di-parse; semua id huruf kecil + garis bawah;
//     teks memakai tanda baca tipografis (’ “ ”, bukan ' ");
//     tidak ada rumus jawaban lengkap (mis. =SUM(D2:D11)).
//   - karakter.json: nama/peran/avatar tidak kosong; foto/sapaan/ucapan
//     (baru/dikerjakan/selesai) wajib kecuali placeholder:true dan kamu.
//   - feedback.json: tepat 9 kode, masing-masing 3 variasi, tanpa kode lain.
//   - tugas/<id>.json: id cocok nama file; hint/trik masing-masing tepat 3;
//     tanpa checks; placeholder brief hanya {{nama}} {{jumlah}} {{deadline}}.
//   - toko.json (bila ada; dibuat Fase 8.2): kategori pertama "semua";
//     id barang cocok kunci; kategori ada; harga bulat >= 0.
//   - wawancara.json (bila ada; dipakai Fase 5): tiap soal punya
//     id/teks/skill/jawaban; id tidak dobel.

const fs = require("fs");
const path = require("path");

const root = process.argv[2] ? path.resolve(process.argv[2]) : process.cwd();
const dirKonten = path.join(root, "content");

const PLACEHOLDER_DIIZINKAN = ["nama", "jumlah", "deadline"];
const KODE_FEEDBACK = ["altered", "nocache", "err", "rowval", "sum", "hard", "ok90", "ok70", "fail"];
const FUNGSI_CEK = ["SUM", "AVERAGE", "COUNTIF", "IF", "SUMIF", "COUNT", "MAX", "MIN"];

let jumlahLolos = 0;
let jumlahGagal = 0;
let jumlahPeringatan = 0;
const pesanGagal = [];

function gagal(file, pesan) {
  jumlahGagal++;
  pesanGagal.push(file + ": " + pesan);
  console.log("  GAGAL " + file + " — " + pesan);
}

function peringatan(file, pesan) {
  jumlahPeringatan++;
  console.log("  PERINGATAN " + file + " — " + pesan);
}

function lolos(file) {
  jumlahLolos++;
  console.log("  LULUS " + file);
}

// Kumpulkan semua nilai string beserta jalurnya (untuk cek umum).
function kumpulkanTeks(obj, jalur, keluar) {
  if (typeof obj === "string") { keluar.push([jalur, obj]); return; }
  if (Array.isArray(obj)) { obj.forEach((v, i) => kumpulkanTeks(v, jalur + "[" + i + "]", keluar)); return; }
  if (obj && typeof obj === "object") {
    for (const k of Object.keys(obj)) kumpulkanTeks(obj[k], jalur + "." + k, keluar);
  }
}

function idValid(id) {
  return typeof id === "string" && /^[a-z][a-z0-9_]*$/.test(id);
}

// Cek umum: tanda baca tipografis + rumus jawaban lengkap + placeholder.
function cekUmum(file, data, lewatiRumus) {
  const teks = [];
  kumpulkanTeks(data, file, teks);
  for (const [jalur, s] of teks) {
    if (s.includes("'")) gagal(file, jalur + " memakai apostrof lurus (') — pakai ’");
    if (s.includes('"')) gagal(file, jalur + ' memakai kutip lurus (") — pakai “ ”');
  }
  if (!lewatiRumus) {
    for (const [jalur, s] of teks) {
      if (s.startsWith("data:")) continue; // data URI foto: '=' di dalamnya bukan rumus
      if (/=\s*[A-Za-z]+\s*\(/.test(s)) gagal(file, jalur + " mengandung rumus jawaban (fungsi setelah '='): " + JSON.stringify(s.slice(0, 80)));
      else if (/=\s*[A-Z]{1,3}\d{1,7}\b/.test(s)) gagal(file, jalur + " mengandung rumus jawaban (sel setelah '='): " + JSON.stringify(s.slice(0, 80)));
      else {
        for (const fn of FUNGSI_CEK) {
          if (new RegExp("\\b" + fn + "\\s*\\([^)]*[A-Z]{1,3}\\d{1,7}").test(s)) {
            gagal(file, jalur + " mengandung rumus jawaban (" + fn + " dengan sel): " + JSON.stringify(s.slice(0, 80)));
            break;
          }
        }
      }
    }
  }
  // Placeholder: hanya yang diizinkan; tidak boleh ada {{ atau }} yatim.
  for (const [jalur, s] of teks) {
    const cocok = s.match(/\{\{[^}]*\}\}/g) || [];
    for (const ph of cocok) {
      const nama = ph.slice(2, -2).trim();
      if (!PLACEHOLDER_DIIZINKAN.includes(nama)) gagal(file, jalur + " memakai placeholder tidak dikenal " + ph);
    }
    const tanpaPasangan = s.replace(/\{\{[^}]*\}\}/g, "");
    if (tanpaPasangan.includes("{{") || tanpaPasangan.includes("}}")) {
      gagal(file, jalur + " ada kurung placeholder tanpa pasangan: " + JSON.stringify(s.slice(0, 80)));
    }
  }
}

function bacaJson(relatif) {
  const p = path.join(dirKonten, relatif);
  if (!fs.existsSync(p)) return { ada: false };
  try {
    return { ada: true, data: JSON.parse(fs.readFileSync(p, "utf8")) };
  } catch (e) {
    return { ada: true, rusak: true, galat: e.message };
  }
}

function cekKarakter() {
  const file = "content/karakter.json";
  const r = bacaJson("karakter.json");
  if (!r.ada) { gagal(file, "file tidak ada"); return; }
  if (r.rusak) { gagal(file, "JSON tidak bisa di-parse: " + r.galat); return; }
  const data = r.data;
  const gagalSebelum = jumlahGagal;
  for (const id of Object.keys(data)) {
    if (!idValid(id)) { gagal(file, "id karakter tidak valid: " + id); }
    const k = data[id];
    for (const f of ["nama", "peran", "avatar"]) {
      if (!k[f] || typeof k[f] !== "string" || !k[f].trim()) { gagal(file, id + ": " + f + " kosong/tidak ada"); }
    }
    const bebas = k.placeholder === true || id === "kamu";
    if (!bebas) {
      if (!k.foto || typeof k.foto !== "string" || !k.foto.trim()) { gagal(file, id + ": foto kosong/tidak ada"); }
      if (!k.sapaan || typeof k.sapaan !== "string" || !k.sapaan.trim()) { gagal(file, id + ": sapaan kosong/tidak ada"); }
      if (!k.ucapan || typeof k.ucapan !== "object") { gagal(file, id + ": ucapan kosong/tidak ada"); }
      else {
        for (const kunci of ["baru", "dikerjakan", "selesai"]) {
          if (!k.ucapan[kunci] || typeof k.ucapan[kunci] !== "string" || !k.ucapan[kunci].trim()) {
            gagal(file, id + ": ucapan." + kunci + " kosong/tidak ada");
          }
        }
      }
    }
    if (typeof k.foto === "string" && k.foto.startsWith("data:")) {
      peringatan(file, id + ": foto masih data URI (utang migrasi, lihat skema §8)");
    }
    if (k.placeholder !== undefined && typeof k.placeholder !== "boolean") {
      gagal(file, id + ": placeholder harus boolean");
    }
  }
  cekUmum(file, data, true);
  if (jumlahGagal === gagalSebelum) lolos(file);
}

function cekFeedback() {
  const file = "content/feedback.json";
  const r = bacaJson("feedback.json");
  if (!r.ada) { gagal(file, "file tidak ada"); return; }
  if (r.rusak) { gagal(file, "JSON tidak bisa di-parse: " + r.galat); return; }
  const data = r.data;
  const gagalSebelum = jumlahGagal;
  for (const kode of KODE_FEEDBACK) {
    if (!Array.isArray(data[kode])) { gagal(file, "kode " + kode + " tidak ada"); }
    else if (data[kode].length !== 3) { gagal(file, "kode " + kode + " harus tepat 3 variasi (ada " + data[kode].length + ")"); }
    else if (data[kode].some((v) => typeof v !== "string" || !v.trim())) { gagal(file, "kode " + kode + " ada variasi kosong"); }
  }
  for (const kode of Object.keys(data)) {
    if (!KODE_FEEDBACK.includes(kode)) { gagal(file, "kode tidak dikenal: " + kode); }
  }
  cekUmum(file, data, false);
  if (jumlahGagal === gagalSebelum) lolos(file);
}

function cekTugas() {
  const dirTugas = path.join(dirKonten, "tugas");
  if (!fs.existsSync(dirTugas)) { gagal("content/tugas/", "folder tidak ada"); return; }
  const files = fs.readdirSync(dirTugas).filter((f) => f.endsWith(".json")).sort();
  if (files.length === 0) { gagal("content/tugas/", "tidak ada file tugas"); return; }
  for (const namaFile of files) {
    const file = "content/tugas/" + namaFile;
    const idHarap = namaFile.replace(/\.json$/, "");
    let data;
    try {
      data = JSON.parse(fs.readFileSync(path.join(dirTugas, namaFile), "utf8"));
    } catch (e) {
      gagal(file, "JSON tidak bisa di-parse: " + e.message);
      continue;
    }
    const gagalSebelum = jumlahGagal;
    if (data.id !== idHarap) { gagal(file, "id '" + data.id + "' tidak cocok dengan nama file '" + idHarap + "'"); }
    if (!idValid(data.id)) { gagal(file, "id tidak valid: " + data.id); }
    for (const f of ["judul", "dari", "brief", "ringkas"]) {
      if (!data[f] || (typeof data[f] === "string" && !data[f].trim()) || (Array.isArray(data[f]) && data[f].length === 0)) {
        gagal(file, f + " kosong/tidak ada");
      }
    }
    if (data.deadline !== undefined && (typeof data.deadline !== "string" || !data.deadline.trim())) {
      gagal(file, "deadline ada tapi kosong");
    }
    if (!Array.isArray(data.skill) || data.skill.length === 0) { gagal(file, "skill harus array tidak kosong"); }
    if (!data.lampiran || !data.lampiran.nama) { gagal(file, "lampiran.nama kosong/tidak ada"); }
    for (const f of ["hint", "trik"]) {
      if (!Array.isArray(data[f]) || data[f].length !== 3) {
        gagal(file, f + " harus tepat 3 entri (ada " + (Array.isArray(data[f]) ? data[f].length : "bukan array") + ")");
      } else if (data[f].some((v) => typeof v !== "string" || !v.trim())) {
        gagal(file, f + " ada entri kosong");
      }
    }
    if ("checks" in data) { gagal(file, "field checks dilarang di content/ (pindah ke backend/rules/)"); }
    cekUmum(file, data, false);
    if (jumlahGagal === gagalSebelum) lolos(file);
  }
}

function cekToko() {
  const file = "content/toko.json";
  const r = bacaJson("toko.json");
  if (!r.ada) { console.log("  LEWATI " + file + " — belum ada (dibuat Fase 8.2)"); return; }
  if (r.rusak) { gagal(file, "JSON tidak bisa di-parse: " + r.galat); return; }
  const data = r.data;
  const gagalSebelum = jumlahGagal;
  if (!Array.isArray(data.kategori) || data.kategori.length === 0) { gagal(file, "kategori harus array tidak kosong"); }
  else if (data.kategori[0].id !== "semua") { gagal(file, "kategori pertama harus 'semua'"); }
  const idKategori = Array.isArray(data.kategori) ? data.kategori.map((k) => k.id) : [];
  if (!data.barang || typeof data.barang !== "object") { gagal(file, "barang kosong/tidak ada"); }
  else {
    for (const [kunci, b] of Object.entries(data.barang)) {
      if (b.id !== kunci) { gagal(file, "barang '" + kunci + "': id '" + b.id + "' tidak cocok dengan kuncinya"); }
      if (!b.nama) { gagal(file, "barang '" + kunci + "': nama kosong"); }
      if (!idKategori.includes(b.kategori)) { gagal(file, "barang '" + kunci + "': kategori '" + b.kategori + "' tidak ada di daftar"); }
      if (!Number.isInteger(b.harga) || b.harga < 0) { gagal(file, "barang '" + kunci + "': harga harus bilangan bulat >= 0"); }
      if (!b.emoji) { gagal(file, "barang '" + kunci + "': emoji kosong"); }
    }
  }
  cekUmum(file, data, false);
  if (jumlahGagal === gagalSebelum) lolos(file);
}

function cekWawancara() {
  const file = "content/wawancara.json";
  const r = bacaJson("wawancara.json");
  if (!r.ada) { console.log("  LEWATI " + file + " — belum ada (dipakai Fase 5)"); return; }
  if (r.rusak) { gagal(file, "JSON tidak bisa di-parse: " + r.galat); return; }
  const data = r.data;
  const gagalSebelum = jumlahGagal;
  if (!Array.isArray(data.soal)) { gagal(file, "soal harus array"); }
  else {
    const ids = new Set();
    for (const s of data.soal) {
      for (const f of ["id", "teks", "skill", "jawaban"]) {
        if (!s[f] || typeof s[f] !== "string" || !s[f].trim()) { gagal(file, "soal '" + (s.id || "?") + "': " + f + " kosong/tidak ada"); }
      }
      if (s.id) {
        if (ids.has(s.id)) { gagal(file, "id soal dobel: " + s.id); }
        ids.add(s.id);
      }
    }
  }
  // 5.6: soal wawancara memang berisi rumus (=SUM, =AVERAGE) —
  // itu isi soalnya, bukan kebocoran jawaban — jadi cek rumus
  // dilewati; cek apostrof/kutip/placeholder tetap jalan.
  cekUmum(file, data, true);
  if (jumlahGagal === gagalSebelum) lolos(file);
}

console.log("Validasi konten: " + dirKonten);
cekKarakter();
cekFeedback();
cekTugas();
cekToko();
cekWawancara();
console.log("\nHASIL: " + jumlahLolos + " file lolos, " + jumlahGagal + " gagal, " + jumlahPeringatan + " peringatan");
if (jumlahGagal > 0) {
  console.log("Yang gagal:");
  pesanGagal.forEach((p) => console.log(" - " + p));
  process.exit(1);
}
