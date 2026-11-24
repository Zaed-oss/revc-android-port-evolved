/* Copies the files inside game.pak into the browser's private storage (OPFS) using sync access handles. */
importScripts('pak-reader.js');
const CHUNK = 8 * 1024 * 1024;
self.onmessage = async (e) => {
  const { file } = e.data;
  try {
    const files = await readPakIndex(file);
    const root = await navigator.storage.getDirectory();
    const total = files.reduce((s, f) => s + f[2], 0);
    const dirs = new Map([['', root]]);
    async function dirFor(parts) {
      let key = '', cur = root;
      for (const p of parts) {
        key += '/' + p;
        if (!dirs.has(key)) dirs.set(key, await cur.getDirectoryHandle(p, { create: true }));
        cur = dirs.get(key);
      }
      return cur;
    }
    let done = 0;
    for (let i = 0; i < files.length; i++) {
      const [path, off, size] = files[i];
      const parts = path.split('/'); const name = parts.pop();
      const dir = await dirFor(parts);
      const fh = await dir.getFileHandle(name, { create: true });
      let existing = -1;
      try { existing = (await fh.getFile()).size; } catch (_) {}
      if (existing === size) { done += size; self.postMessage({ type: 'progress', done, total, file: path, skipped: true, i, n: files.length }); continue; }
      const h = await fh.createSyncAccessHandle();
      try {
        h.truncate(0);
        for (let p = 0; p < size; p += CHUNK) {
          const n = Math.min(CHUNK, size - p);
          const buf = await file.slice(off + p, off + p + n).arrayBuffer();
          h.write(new Uint8Array(buf), { at: p });
          done += n;
          self.postMessage({ type: 'progress', done, total, file: path, i, n: files.length });
        }
        h.flush();
      } finally { h.close(); }
    }
    self.postMessage({ type: 'done', total, count: files.length });
  } catch (err) {
    self.postMessage({ type: 'error', message: String(err && err.message || err) });
  }
};
