/* Reads the index of a game.pak (see tools/make_pak.py). Works on any Blob/File. */
async function readPakIndex(blob) {
  const dec = new TextDecoder();
  const size = blob.size;
  if (size < 32) throw new Error('الملف صغير جداً');
  const head = new Uint8Array(await blob.slice(0, 8).arrayBuffer());
  if (dec.decode(head) !== 'VCPAK001') throw new Error('ليس ملف game.pak صحيحاً');
  const tail = await blob.slice(size - 16, size).arrayBuffer();
  if (dec.decode(new Uint8Array(tail, 8, 8)) !== 'VCPAKEND') throw new Error('الملف ناقص أو لم يكتمل رفعه');
  const idxOff = Number(new DataView(tail).getBigUint64(0, true));
  const json = dec.decode(await blob.slice(idxOff, size - 16).arrayBuffer());
  return JSON.parse(json).files;   // [[path, offset, size], ...]
}
if (typeof module !== 'undefined') module.exports = { readPakIndex };
if (typeof self !== 'undefined') self.readPakIndex = readPakIndex;
