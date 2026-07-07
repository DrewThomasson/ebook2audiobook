"""Extract first chapter of an epub into a minimal test epub."""

import re, os, sys, zipfile

src = r"C:\Users\roela\Downloads\[Pendergast 1] Preston, Douglas _ - libgen.li.epub"
dst = r"C:\Users\roela\ebook2audiobook\ebooks\pendergast_ch1_test.epub"

with zipfile.ZipFile(src, "r") as zin:
    names = zin.namelist()
    opf_name = next(n for n in names if n.endswith(".opf"))
    opf_data = zin.read(opf_name)
    opf = opf_data.decode("utf-8")

    itemrefs = re.findall(r'<itemref[^>]*idref=["\']([^"\']+)["\']', opf)
    manifest = dict(
        re.findall(
            r'<item[^>]*id=["\']([^"\']+)["\'][^>]*href=["\']([^"\']+)["\']', opf
        )
    )

    # skip titlepage/toc/cover
    first_file = None
    for ref in itemrefs:
        f = manifest.get(ref, "")
        if (
            f
            and "titlepage" not in f.lower()
            and "toc" not in f.lower()
            and "nav" not in f.lower()
        ):
            first_file = f
            break
    if not first_file:
        html = [
            n
            for n in names
            if n.endswith((".html", ".xhtml", ".htm"))
            and "toc" not in n.lower()
            and "nav" not in n.lower()
        ]
        first_file = html[0] if html else None
    if not first_file:
        print("No content file found", file=sys.stderr)
        sys.exit(1)

    print(f"First content file: {first_file}")
    content = zin.read(first_file).decode("utf-8")

    # trim to first ~15KB of body
    body_m = re.search(r"(<body[^>]*>)(.*)", content, re.DOTALL | re.IGNORECASE)
    if body_m:
        content = body_m.group(1) + body_m.group(2)[:15000] + "</body></html>"

    print(f"Content: {len(content)} chars")

    # collect non-html resources
    keep = []
    for n in names:
        if (
            n.startswith("META-INF/")
            or n.endswith(".css")
            or n.endswith(".jpg")
            or n.endswith(".jpeg")
            or n.endswith(".png")
            or n.endswith(".gif")
            or n.endswith(".svg")
        ):
            keep.append(n)

    resources = []
    for n in names:
        if (
            n not in (opf_name, first_file, "mimetype")
            and not n.startswith("META-INF/")
            and not n.endswith((".html", ".xhtml", ".htm"))
        ):
            resources.append(n)

    with zipfile.ZipFile(dst, "w") as out:
        out.writestr(
            "mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED
        )
        for n in keep:
            out.writestr(n, zin.read(n))
        for n in resources:
            out.writestr(n, zin.read(n))
        out.writestr(first_file, content.encode("utf-8"))
        out.writestr(opf_name, opf_data)

print(f"Created: {dst} ({os.path.getsize(dst)} bytes)")
