// How a file or folder is named under the documents root. No name there holds
// a space: each run of spaces, with any hyphens touching it, becomes one
// hyphen, and a hyphen left in front of the extension is dropped. The wiki
// shows a hyphen as a space, so `ACT 4.0 - Activity Entry.md` is
// `ACT-4.0-Activity-Entry.md` and still titled `ACT 4.0 Activity Entry`. The
// convert-docs skill's path helpers write the same rule.

/** One name, without its folder, as it is written under the documents root. */
export function hyphenated(name) {
  if (!/\s/.test(name)) return name;
  return name.trim().replace(/[\s-]*\s[\s-]*/g, '-').replace(/-(\.[A-Za-z0-9]+)$/, '$1');
}

/** A slash-separated path with every part written as it is under the root. */
export function hyphenatedPath(rel) {
  return rel.split('/').map(hyphenated).join('/');
}
