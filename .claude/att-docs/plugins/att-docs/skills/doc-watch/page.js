// Runs inside the SharePoint library page with the signed-in session. docwatch.py fills the
// placeholders, and the whole printed text is passed to javascript_tool. The scan runs in the
// background and writes its report into <main><pre id="docwatch">, which get_page_text reads
// back once window.DW.done is true.
(() => {
  // The libraries walked, as [key, web, library path], filled in from docwatch.py. The
  // first library's folders are written as they sit in it; another library's folders
  // carry its key and a colon, a character SharePoint allows in no folder name.
  const LIBRARIES = __LIBRARIES__;
  const SITE = LIBRARIES[0][1];
  const MODE = '__MODE__';
  const VERSION = '__VERSION__';
  // Folder table rows: [library-relative prefix, suite, "track" or "skip"], longest first.
  const FOLDERS = __FOLDERS__;
  // The extensions the converter reads, filled in from its own routing table. A diagram
  // or a project plan under a walked folder has no path to Markdown, so it is counted
  // by format rather than offered as a new document.
  const FORMATS = new Set(__FORMATS__);
  // One entry per indexed document: 8 hex hash of the file stem, suite code, index into
  // the date list. Null when the page is expected to hold this version already.
  const PACKED = __INDEX__;
  // Lookup mode only: 8 hex hashes of the stems to report, whether indexed or not.
  const NAMES = new Set(__NAMES__);
  // sources.tsv as [stem hash, library folders its converted files came from]. A stem
  // with an entry is compared only against its copies under those folders.
  const SOURCES = new Map(__SOURCES__);
  const HEADERS = { Accept: 'application/json;odata=nometadata' };
  const STORE = 'docwatch-index';
  // Revision copies and archives sit beside the current document and are never new.
  const SIDE_FOLDER = /revision ?history|^archive/i;
  const SIDE_NAME = /_Rev(ision)?\s*\d+(\.\d+)*\s*\.[^.]+$|RevisionHistory/i;

  const state = { done: false, walked: false, folders: 0, files: 0 };
  window.DW = state;
  const lines = [];
  // get_page_text turns tabs into spaces and may fold runs of them, and file names here
  // carry double spaces, so every field is URI-encoded and joined with a bar, which
  // SharePoint does not allow in a name.
  const emit = (...fields) => lines.push(fields.map((f) => encodeURIComponent(f)).join('|'));
  const report = () => {
    document.body.innerHTML = '';
    const main = document.createElement('main');
    const pre = document.createElement('pre');
    pre.id = 'docwatch';
    pre.textContent = ['DOCWATCH-BEGIN', ...lines, 'DOCWATCH-END'].join('\n');
    main.appendChild(pre);
    document.body.appendChild(main);
    // A links report runs to one row per converted document, too long to copy out of
    // the page, so the page saves it to the downloads folder instead. A scan that
    // stopped short saves nothing, so the file in Downloads is always a whole walk.
    if (MODE === 'links' && state.walked) {
      const save = document.createElement('a');
      save.href = URL.createObjectURL(new Blob([pre.textContent], { type: 'text/plain' }));
      save.download = 'docwatch-links.txt';
      document.body.appendChild(save);
      save.click();
    }
    state.done = true;
  };

  const fnv = (text) => {
    let hash = 0x811c9dc5;
    for (const ch of text.toLowerCase()) {
      hash ^= ch.codePointAt(0);
      hash = Math.imul(hash, 0x01000193) >>> 0;
    }
    return hash.toString(16).padStart(8, '0');
  };
  let packed = PACKED;
  if (packed) {
    // The index is pasted into the call by hand, so a slip shows up here, not as a gap.
    if (fnv(packed.entries) !== packed.check) {
      emit('INDEX', 'corrupt', fnv(packed.entries));
      report();
      return 'index corrupt';
    }
    localStorage.setItem(STORE, JSON.stringify({ version: VERSION, packed }));
  } else {
    const stored = JSON.parse(localStorage.getItem(STORE) || '{}');
    if (stored.version !== VERSION) {
      emit('INDEX', 'stale', stored.version || 'none');
      report();
      return 'index stale';
    }
    packed = stored.packed;
  }
  const index = new Map();
  for (const entry of packed.entries.split(' ')) {
    index.set(entry.slice(0, 8), { suite: entry[8], day: packed.days[Number(entry.slice(9))] });
  }
  // A .doc and a .pdf of one title are one document, so the stem is the key. A trailing
  // date is dropped as well, since a document published under a new dated name at each
  // revision is one document; the pattern is docwatch.py's DATE_SUFFIX.
  const DATE_SUFFIX = new RegExp(__DATE_SUFFIX__);
  const stemHash = (name) => fnv(name.replace(/\.[^.]*$/, '').replace(DATE_SUFFIX, ''));
  // A name with no dot has no extension, which reads as the empty format.
  const extOf = (name) => (name.match(/\.([^.]*)$/) || ['', ''])[1].toLowerCase();
  // A library root, `Key:`, holds every folder that starts with it.
  const under = (folder, prefix) => folder === prefix
    || folder.startsWith(prefix.endsWith(':') ? prefix : `${prefix}/`);
  // A sources.tsv row naming a library root means the files at the root, not its folders.
  const fromSource = (folder, source) => (source.endsWith(':')
    ? folder === source : under(folder, source));
  const ruleOf = (folder) => {
    for (const [prefix, rule] of FOLDERS) {
      if (under(folder, prefix)) return rule;
    }
    return null;
  };
  const enc = (path) => encodeURIComponent(path.replace(/'/g, "''"));
  const qualify = (key, path) => (key ? `${key}:${path}` : path);
  // The library a scan folder sits in, and the folder inside that library.
  const libraryOf = (folder) => {
    const at = folder.indexOf(':');
    const key = at < 0 ? '' : folder.slice(0, at);
    const [, web, lib] = LIBRARIES.find(([k]) => k === key);
    return { key, web, lib, inside: folder.slice(at + 1) };
  };
  // A request digest belongs to one site, so each web fetches its own, once.
  const digests = new Map();
  const digestOf = async (web) => {
    if (!digests.has(web)) {
      const context = await fetch(`${web}/_api/contextinfo`, { method: 'POST', headers: HEADERS });
      digests.set(web, (await context.json()).FormDigestValue);
    }
    return digests.get(web);
  };

  // Every file under one folder, 5000 rows a page. A filtered list query on this library
  // trips the view threshold, and the search index leaves documents out, so the walk goes
  // folder by folder through RenderListDataAsStream. A library root lists only the files
  // in it, since its folders carry rows of their own in the folder table.
  const walk = async (folder) => {
    const { key, web, lib, inside } = libraryOf(folder);
    const digest = await digestOf(web);
    const url = `${web}/_api/web/GetList(@l)/RenderListDataAsStream?@l='${enc(lib)}'`;
    const scope = inside ? 'RecursiveAll' : 'FilesOnly';
    const view = `<View Scope="${scope}"><Query><Where><Eq>`
      + '<FieldRef Name="FSObjType"/><Value Type="Integer">0</Value></Eq></Where></Query>'
      + '<ViewFields><FieldRef Name="FileRef"/><FieldRef Name="Modified"/>'
      + '<FieldRef Name="File_x0020_Size"/></ViewFields>'
      + '<RowLimit Paged="TRUE">5000</RowLimit></View>';
    const rows = [];
    let paging;
    do {
      const parameters = {
        RenderOptions: 2, ViewXml: view, DatesInUtc: true,
        FolderServerRelativeUrl: inside ? `${lib}/${inside}` : lib, Paging: paging,
      };
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          ...HEADERS,
          'Content-Type': 'application/json;odata=nometadata',
          'X-RequestDigest': digest,
        },
        body: JSON.stringify({ parameters }),
      });
      const body = await response.json();
      if (body['odata.error']) throw new Error(body['odata.error'].message.value);
      for (const row of body.Row) {
        const path = qualify(key, row.FileRef.slice(lib.length + 1));
        rows.push([path, row.Modified, row.File_x0020_Size]);
      }
      paging = body.NextHref ? body.NextHref.replace(/^\?/, '') : undefined;
    } while (paging);
    return rows;
  };

  (async () => {
    try {
      const me = await fetch(`${SITE}/_api/web/currentuser?$select=Title`, { headers: HEADERS });
      if (!me.ok || !(me.headers.get('content-type') || '').includes('json')) {
        emit('SESSION', 'expired', me.status);
        return;
      }
      emit('SESSION', 'ok', (await me.json()).Title);
      const tops = [];
      for (const [key, web, lib] of LIBRARIES) {
        const libUrl = `${web}/_api/web/GetFolderByServerRelativePath(decodedurl='${enc(lib)}')`;
        try {
          const listed = await fetch(`${libUrl}/Folders?$select=Name`, { headers: HEADERS });
          const names = (await listed.json()).value.map((f) => f.Name);
          tops.push(...names.filter((name) => name !== 'Forms').map((n) => qualify(key, n)));
        } catch (error) {
          emit('ERROR', qualify(key, '-'), error.message);
        }
      }
      for (const top of tops) {
        if (!FOLDERS.some(([prefix]) => prefix.split('/')[0] === top)) {
          emit('UNMAPPED', top);
        }
      }
      // A survey walks every top folder, so the table can be built from where sources live.
      const walked = FOLDERS.filter(([, rule]) => rule !== 'skip').map(([prefix]) => prefix);
      // A root walk holds none of its folders, so each walked folder under it is a root too.
      const rootFiles = walked.filter((prefix) => prefix.endsWith(':'));
      const roots = MODE === 'survey' ? [...tops, ...rootFiles] : walked.filter(
        (prefix) => !walked.some((other) => other !== prefix && !other.endsWith(':')
          && under(prefix, other)),
      );
      const seen = new Set();
      const survey = new Map();
      const unreadable = new Map();
      // Every indexed file found, by stem hash, held until the walk ends so that copies
      // of one name in different folders are weighed together.
      const found = new Map();
      let unchanged = 0;
      const classify = ([folder, name, modified, size], day) => {
        if (modified.slice(0, 10) > day) {
          emit('CHANGED', folder, name, modified, size);
        } else {
          unchanged += 1;
        }
      };
      for (const root of roots) {
        let rows = [];
        try {
          rows = await walk(root);
        } catch (error) {
          emit('ERROR', root, error.message);
        }
        state.folders += 1;
        for (const [path, modified, size] of rows) {
          state.files += 1;
          // The library key stays on the folder, so a file at a library root has `Key:`.
          const at = path.indexOf(':') + 1;
          const parts = path.slice(at).split('/');
          const name = parts.pop();
          const folder = path.slice(0, at) + parts.join('/');
          const hash = stemHash(name);
          const hit = index.get(hash);
          const side = parts.some((part) => SIDE_FOLDER.test(part)) || SIDE_NAME.test(name);
          // The folder a document belongs to: a revision folder, an archive, or a
          // "<name>.doc File" folder of attachments sits under the document's own folder.
          const stop = parts.findIndex((p) => SIDE_FOLDER.test(p) || / file$/i.test(p));
          const own = parts.slice(0, stop < 0 ? parts.length : stop);
          const home = path.slice(0, at) + own.join('/');
          if (MODE === 'survey') {
            if (!hit) continue;
            const key = JSON.stringify([hit.suite, home]);
            survey.set(key, (survey.get(key) || 0) + 1);
            continue;
          }
          const rule = ruleOf(folder);
          if (rule === 'skip') continue;
          // A lookup reports the exact Modified time of the named documents' current
          // copies, indexed or not, and nothing else.
          if (MODE === 'lookup') {
            if (NAMES.has(hash)) emit('LOOKUP', folder, name, modified, size, rule || '', side ? 'side' : '');
            continue;
          }
          if (hit) {
            if (!found.has(hash)) found.set(hash, []);
            found.get(hash).push({ row: [folder, name, modified, size], home, side });
          } else if (!side && rule !== 'track') {
            const ext = extOf(name);
            if (FORMATS.has(ext)) {
              emit('NEW', folder, name, modified, size, rule);
            } else {
              unreadable.set(ext, (unreadable.get(ext) || 0) + 1);
            }
          }
        }
      }
      for (const [key, count] of [...survey].sort()) emit('SURVEY', ...JSON.parse(key), count);
      if (MODE !== 'survey' && MODE !== 'lookup') {
        // One name in the home folders of two or more documents is either one document
        // copied, when each home holds the same files at the same sizes, or different
        // documents. Different documents are held back until sources.tsv says which folder
        // the converted copy came from, since only that copy can say whether the conversion
        // is current. A home's own files are weighed ahead of its revision copies, and a
        // copied document is compared once, through the home whose files are newest.
        // A copy under a Revision History or Archive folder is an earlier revision of the
        // current file, so it drops out whenever a current copy was found.
        for (const [hash, all] of found) {
          const current = all.filter(({ side }) => !side);
          const hits = current.length ? current : all;
          const { day } = index.get(hash);
          const sources = SOURCES.get(hash);
          const rows = hits.map(({ row }) => row);
          const homes = new Map();
          for (const { row, home } of hits) {
            const [folder, name, modified, size] = row;
            const entry = homes.get(home) || { own: [], all: [], rows: [], newest: '' };
            const file = `${name.toLowerCase()}|${size}`;
            entry.all.push(file);
            entry.rows.push(row);
            if (modified > entry.newest) entry.newest = modified;
            if (folder === home) entry.own.push(file);
            homes.set(home, entry);
          }
          const contents = [...homes.values()]
            .map(({ own, all }) => (own.length ? own : all).sort().join(' '));
          const copied = contents.length > 1 && new Set(contents).size === 1;
          let kept = rows;
          let held = false;
          if (sources) {
            kept = rows.filter(([folder]) => sources.some((source) => fromSource(folder, source)));
          } else if (copied) {
            kept = [...homes.values()].sort((a, b) => (a.newest < b.newest ? 1 : -1))[0].rows;
          } else {
            held = contents.length > 1;
          }
          if (contents.length > 1) {
            const kind = (sources && 'resolved') || (held && 'conflict') || 'copy';
            for (const row of rows) emit('SAMENAME', kind, ...row);
          }
          // A home folder that no longer holds the file leaves the stem not listed.
          if (kept.length) seen.add(hash);
          if (!held) kept.forEach((row) => classify(row, day));
          // The links scan names the library file behind each converted one, which is
          // what its SharePoint line links to. A name found only as a revision copy
          // has no current file to link to.
          if (MODE === 'links' && !held && current.length) {
            kept.forEach(([folder, name]) => emit('FOUND', folder, name));
          }
        }
        emit('UNCHANGED', unchanged);
        for (const [ext, count] of [...unreadable].sort()) {
          emit('UNREADABLE', ext || '(none)', count);
        }
        const missing = [...index.keys()].filter((hash) => !seen.has(hash));
        emit('MISSING', missing.join(' '));
      }
      emit('WALKED', state.folders, state.files);
      state.walked = true;
    } catch (error) {
      emit('ERROR', '-', error.message);
    } finally {
      report();
    }
  })();
  return 'started';
})();
