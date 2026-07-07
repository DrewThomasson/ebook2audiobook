import zipfile, re

src = r"C:\Users\roela\Downloads\[Pendergast 1] Preston, Douglas _ - libgen.li.epub"
with zipfile.ZipFile(src) as z:
    opf_name = next(n for n in z.namelist() if n.endswith(".opf"))
    opf = z.read(opf_name).decode()
    itemrefs = re.findall(r'<itemref[^>]*idref=["\']([^"\']+)["\']', opf)
    manifest = dict(
        re.findall(
            r'<item[^>]*id=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)["\']', opf
        )
    )

    print("Spine order:")
    for i, ref in enumerate(itemrefs[:15]):
        f = manifest.get(ref, "?")
        print(f"  {i}: {ref} -> {f}")

    html = [n for n in z.namelist() if n.endswith((".html", ".xhtml", ".htm"))]
    print(f"\nAll HTML files ({len(html)}):")
    for h in html:
        data = z.read(h)
        # extract first part of text content
        text = re.sub(r"<[^>]+>", "", data.decode("utf-8", errors="replace"))[
            :80
        ].strip()
        print(f"  {h} ({len(data):>6} bytes) - {text}")
