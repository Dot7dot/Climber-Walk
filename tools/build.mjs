// Build: src/game.html -> index.html (single self-contained, minified)
// usage: npm run build   (needs devDependency "terser")
import { readFileSync, writeFileSync } from 'node:fs';
import { gzipSync } from 'node:zlib';
import { minify } from 'terser';

const src = readFileSync(new URL('../src/game.html', import.meta.url), 'utf8');
const m = src.match(/<script type="module">([\s\S]*?)<\/script>/);
if (!m) throw new Error('module script not found');
let js = m[1];

// 1) minify WGSL template literals tagged with /*wgsl*/
js = js.replace(/\/\*wgsl\*\/`([\s\S]*?)`/g, (_, w) => {
  w = w.replace(/\/\/[^\n]*/g, '').replace(/\s+/g, ' ');
  w = w.replace(/\s*([{}()\[\];,:<>=+\-*\/@.!&|%?])\s*/g, '$1');
  // restore spaces required after attributes like @builtin(position) <ident> are handled by ')' boundary
  return '`' + w.trim() + '`';
});

// 2) terser
const out = await minify(js, {
  module: true,
  ecma: 2022,
  compress: { passes: 3, unsafe_arrows: true, pure_getters: true },
  mangle: { toplevel: true },
  format: { comments: false },
});

// 3) CSS + HTML
let html = src.replace(m[0], () => '<script type="module">' + out.code + '</script>');
html = html.replace(/<style>([\s\S]*?)<\/style>/, (_, c) => '<style>' + c
  .replace(/\/\*[\s\S]*?\*\//g, '')
  .replace(/\s+/g, ' ')
  .replace(/\s*([{};:,>])\s*/g, '$1')
  .replace(/;}/g, '}')
  .trim() + '</style>');
const [head, rest] = html.split('<script type="module">');
const scriptPart = '<script type="module">' + rest;
const headMin = head.replace(/>\s+</g, '><').replace(/\n\s*/g, '');
html = headMin + scriptPart.replace(/<\/script>\s*<\/body>\s*<\/html>\s*$/, '</script></body></html>');

writeFileSync(new URL('../index.html', import.meta.url), html);
const raw = Buffer.byteLength(html), gz = gzipSync(html, { level: 9 }).length;
console.log(`index.html: ${raw} bytes (${(raw / 1024).toFixed(1)} KiB), gzip ${gz} bytes (${(gz / 1024).toFixed(1)} KiB)`);
console.log(`source: ${Buffer.byteLength(src)} bytes`);
