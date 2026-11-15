// What ALM can store of a piece of text. It imports nothing, so the record
// helpers can use it without loading the ALM session and its dependencies.

/**
 * A character ALM cannot store. ALM keeps text in Windows-1252, so it saves
 * any character that code page lacks as `?`: the arrow 🡪 and the circle ⚫
 * both read back that way, while curly quotes and dashes come through. The
 * class is ASCII, Latin-1 from 0xA0, and the 27 characters Windows-1252
 * places in 0x80-0x9F. The C1 controls U+0080-U+009F are not among them.
 */
export const ALM_UNSTORABLE = new RegExp('[^\\u0000-\\u007f\\u00a0-\\u00ff'
  + '\\u0152\\u0153\\u0160\\u0161\\u0178\\u017d\\u017e\\u0192\\u02c6\\u02dc'
  + '\\u2013\\u2014\\u2018\\u2019\\u201a\\u201c\\u201d\\u201e\\u2020\\u2021'
  + '\\u2022\\u2026\\u2030\\u2039\\u203a\\u20ac\\u2122]', 'u');

/**
 * HTML with every character ALM cannot store written as a numeric entity,
 * which it keeps, so the arrow a document draws as 🡪 reads back as itself
 * rather than as `?`.
 */
export function almEntities(html) {
  return html.replace(new RegExp(ALM_UNSTORABLE.source, 'gu'),
    (ch) => `&#${ch.codePointAt(0)};`);
}

/**
 * Why a plain text field would lose a character in ALM, as the clause that
 * follows the field's name, or null. A plain field has no entities, so the
 * character would be saved as `?`.
 */
export function unstorableProblem(value) {
  const unstorable = ALM_UNSTORABLE.exec(value ?? '');
  return unstorable ? `holds ${unstorable[0]}, which ALM stores as ?` : null;
}
