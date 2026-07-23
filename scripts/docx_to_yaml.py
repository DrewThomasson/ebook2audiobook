#!/usr/bin/env python3
"""
Convert a .docx file to a YAML representation.

Usage:
    python scripts/docx_to_yaml.py input.docx output.yaml

If output path is omitted, prints YAML to stdout.
"""
import sys
import os
from docx import Document
import yaml
from datetime import datetime


def extract_docx(path):
    doc = Document(path)
    props = doc.core_properties
    metadata = {
        'title': props.title if props.title else None,
        'author': props.author if props.author else None,
        'created': props.created.strftime('%Y-%m-%dT%H:%M:%S') if getattr(props, 'created', None) else None,
        'modified': props.modified.strftime('%Y-%m-%dT%H:%M:%S') if getattr(props, 'modified', None) else None,
        'subject': props.subject if getattr(props, 'subject', None) else None,
    }
    content = []
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        style = p.style.name if p.style is not None else ''
        if style and style.lower().startswith('heading'):
            # try to parse heading level from style name e.g. 'Heading 1'
            level = None
            parts = style.split()
            for part in parts[::-1]:
                try:
                    level = int(part)
                    break
                except Exception:
                    continue
            content.append({'type': 'heading', 'level': level, 'style': style, 'text': text})
        else:
            content.append({'type': 'paragraph', 'style': style, 'text': text})
    return {'metadata': metadata, 'content': content}


def main():
    if len(sys.argv) < 2:
        print('Usage: python scripts/docx_to_yaml.py input.docx [output.yaml]')
        sys.exit(2)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    if not os.path.exists(inp):
        print(f'Error: input file does not exist: {inp}', file=sys.stderr)
        sys.exit(1)
    try:
        data = extract_docx(inp)
    except Exception as e:
        print(f'Error reading docx: {e}', file=sys.stderr)
        sys.exit(1)
    yaml_text = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    if out:
        with open(out, 'w', encoding='utf-8') as f:
            f.write(yaml_text)
        print(f'Wrote YAML to {out}')
    else:
        print(yaml_text)


if __name__ == '__main__':
    main()
