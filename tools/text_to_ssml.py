#!/usr/bin/env python3
"""Simple Markdown→SSML preprocessor prototype for audiobook/podcast pipeline.

Usage:
  py -3.11 tools/text_to_ssml.py input.txt --out run/scripts/converted_chunk1.ssml --lexicon run/lexicon.json

This prototype applies heuristic mappings:
 - italics (*text* or _text_) -> inner thought (soft prosody)
 - bold (**text**) -> strong emphasis
 - "quoted text" -> quote -> voice switch (guest) or prosody change
 - ellipsis (...) / … -> <break time>
 - parentheses -> softer prosody
 - em-dash (— or --) -> short break
 - ALLCAPS words -> emphasis
 - numbers -> <say-as interpret-as="cardinal">
 - lexicon lookup -> <phoneme>

This is intentionally dependency-free and conservative.
"""

from __future__ import annotations
import argparse
import json
import re
from pathlib import Path


def load_lexicon(path: Path | None) -> dict[str, str]:
    if not path:
        return {}
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return {k: v for k, v in data.items() if isinstance(v, str)}
    except Exception:
        return {}


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def apply_lexicon(text: str, lexicon: dict[str, str]) -> str:
    if not lexicon:
        return text
    # word boundary aware replacement (simple)
    def repl(m):
        word = m.group(0)
        key = word
        ph = lexicon.get(key) or lexicon.get(key.lower())
        if ph:
            return f"<phoneme alphabet=\"ipa\" ph=\"{escape_xml(ph)}\">{escape_xml(word)}</phoneme>"
        return escape_xml(word)

    pattern = re.compile(r"\b([A-Za-z0-9_\-]+)\b")
    return pattern.sub(repl, text)


def apply_lexicon_to_ssml(ssml_text: str, lexicon: dict[str, str]) -> str:
    """Apply lexicon phoneme replacements only to text nodes (leave tags intact)."""
    if not lexicon:
        return ssml_text
    parts = re.split(r'(<[^>]+>)', ssml_text)
    out = []
    for p in parts:
        if not p:
            continue
        if p.startswith('<') and p.endswith('>'):
            out.append(p)
        else:
            # p is plain text content; apply lexicon which will escape xml and insert <phoneme/>
            out.append(apply_lexicon(p, lexicon))
    return ''.join(out)


def annotation_to_ssml(annotation: dict) -> str:
    """Map a single annotation (emotion/intensity/focus) to an SSML fragment.

    Expected annotation format (prototype):
      {"text": "word or phrase", "emotion": "sad", "intensity": 0.8}
    or
      {"text": "word", "overrides": {"rate":0.9, "pitch":"-2st", "volume":"-3dB", "pause_ms":200}}

    This function returns an SSML snippet (string) that can be substituted
    in the generated SSML. It's intentionally conservative and engine‑agnostic.
    """
    text = annotation.get('text', '')
    if not text:
        return ''

    # base mapping for common emotions — tuned conservatively
    emotion_map = {
        'anger': {'rate': 1.12, 'pitch': '+2st', 'volume': '+3dB', 'emphasis': 'strong', 'pause_ms': 60},
        'joy': {'rate': 1.08, 'pitch': '+1.5st', 'volume': '+2dB', 'emphasis': 'moderate', 'pause_ms': 40},
        'sad': {'rate': 0.88, 'pitch': '-2st', 'volume': '-3dB', 'emphasis': 'none', 'pause_ms': 200},
        'neutral': {'rate': 1.0, 'pitch': '0st', 'volume': '0dB', 'emphasis': 'none', 'pause_ms': 0},
        'surprise': {'rate': 1.15, 'pitch': '+4st', 'volume': '+4dB', 'emphasis': 'strong', 'pause_ms': 80},
        'fear': {'rate': 1.05, 'pitch': '+2.5st', 'volume': '+1dB', 'emphasis': 'moderate', 'pause_ms': 60},
    }

    overrides = {}
    # explicit overrides take precedence
    if 'overrides' in annotation and isinstance(annotation['overrides'], dict):
        overrides.update(annotation['overrides'])

    # emotion mapping
    emo = annotation.get('emotion') or annotation.get('mood')
    intensity = float(annotation.get('intensity', 1.0)) if annotation.get('intensity') is not None else 1.0
    if emo and emo in emotion_map:
        base = emotion_map[emo].copy()
        # scale magnitude by intensity (0..1)
        # rate: move slightly towards base depending on intensity
        # intensity scaling: values >1 can amplify, <1 reduce
        try:
            intensity = float(intensity)
        except Exception:
            intensity = 1.0
        if intensity != 1.0:
            # rate scaling (lerp between 1.0 and base rate)
            base['rate'] = 1.0 + (base['rate'] - 1.0) * max(0.0, min(1.0, intensity))
            # pitch scaling: convert semitone like '+2st' -> numeric, scale
            try:
                if isinstance(base.get('pitch',''), str) and base['pitch'].endswith('st'):
                    st = float(base['pitch'][:-2])
                    base['pitch'] = f"{(st * max(0.0, min(1.5, intensity))):+.1f}st"
            except Exception:
                pass
            # volume scaling: keep simple dB adjustments
            try:
                if isinstance(base.get('volume',''), str) and base['volume'].endswith('dB'):
                    db = float(base['volume'][:-2])
                    base['volume'] = f"{(db * max(0.0, min(1.5, intensity))):+.1f}dB"
            except Exception:
                pass
        overrides = {**base, **overrides}

    # support explicit micro_contour and formant_preserve flags in overrides
    formant_preserve = bool(overrides.get('formant_preserve') or overrides.get('preserve_formants'))
    micro_contour = bool(overrides.get('micro_contour'))

    # defaults
    rate = overrides.get('rate', 1.0)
    pitch = overrides.get('pitch', '0st')
    volume = overrides.get('volume', '0dB')
    emphasis = overrides.get('emphasis', 'none')
    pause_ms = int(overrides.get('pause_ms', overrides.get('pause', 0) or 0))

    # format rate as percent when numeric
    if isinstance(rate, (int, float)):
        rate_pct = f"{int(rate*100)}%"
    else:
        rate_pct = str(rate)

    # build SSML fragment
    pre = f'<break time="{pause_ms}ms"/>' if pause_ms else ''
    post = f'<break time="{pause_ms}ms"/>' if pause_ms else ''
    emph_start = ''
    emph_end = ''
    if emphasis in ('strong', 'moderate'):
        level = 'strong' if emphasis == 'strong' else 'moderate'
        emph_start = f'<emphasis level="{level}">'
        emph_end = '</emphasis>'

    # Use conservative volume markers when dB-like
    vol_attr = str(volume)

    # If micro_contour is requested, create a conservative pitch spike
    if micro_contour:
        # simple single-word spike with pre/post small breaks
        spike_pitch = overrides.get('spike_pitch', overrides.get('pitch', '+3st'))
        spike_rate = overrides.get('spike_rate', overrides.get('rate', 1.0))
        if isinstance(spike_rate, (int, float)):
            spike_rate_pct = f"{int(spike_rate*100)}%"
        else:
            spike_rate_pct = str(spike_rate)
        spike_pre = f'<break time="{max(20, int(pause_ms/2))}ms"/>'
        spike_post = f'<break time="{max(40, int(pause_ms))}ms"/>'
        formant_comment = '<!--E2A:formant_preserve=1-->' if formant_preserve else ''
        fragment = (
            f"{spike_pre}{formant_comment}<prosody rate=\"{spike_rate_pct}\" pitch=\"{spike_pitch}\" volume=\"{vol_attr}\">"
            f"{emph_start}{escape_xml(text)}{emph_end}</prosody>{spike_post}"
        )
        return fragment

    formant_comment = '<!--E2A:formant_preserve=1-->' if formant_preserve else ''
    fragment = (
        f"{pre}{formant_comment}<prosody rate=\"{rate_pct}\" pitch=\"{pitch}\" volume=\"{vol_attr}\">"
        f"{emph_start}{escape_xml(text)}{emph_end}</prosody>{post}"
    )
    return fragment


def apply_annotations_to_ssml(ssml: str, annotations: list[dict]) -> str:
    """Apply a list of annotations to an SSML string by replacing the first
    matching plain text occurrence with the SSML fragment from
    `annotation_to_ssml`.

    This is a pragmatic, best-effort substitution useful for preprocessed
    chunks; for production use, prefer token offsets or forced‑alignment.
    """
    if not annotations:
        return ssml
    s = ssml
    for ann in annotations:
        txt = ann.get('text')
        if not txt:
            continue
        esc = escape_xml(txt)
        fragment = annotation_to_ssml(ann)
        if esc in s:
            s = s.replace(esc, fragment, 1)
        else:
            # fallback: try unescaped plain substring
            if txt in s:
                s = s.replace(txt, fragment, 1)
            else:
                print(f"Warning: annotation text not found in SSML: '{txt}'")
    return s


def text_to_ssml(
    text: str,
    lexicon: dict[str, str],
    prefer_guest_voice: bool = True,
    comma_ms: int = 80,
    period_ms: int = 220,
    ellipsis_ms: int = 400,
    breath_ms: int = 80,
    annotations: list[dict] | None = None,
) -> str:
    # Normalize unicode ellipsis
    text = text.replace("…", "...")

    # Convert explicit [voice:role]...[/voice] spans into safe comment markers
    # so downstream TTS converter doesn't try to interpret them as voice file paths.
    def _voice_span_repl(m):
        role = (m.group(1) or "").strip()
        inner = m.group(2) or ""
        # use unique placeholders to avoid XML escaping issues; we'll convert later
        return f"___VOICE_START_{role}___" + inner + "___VOICE_END___"

    text = re.sub(r"\[voice:([^\]]+)\](.*?)\[/voice\]", _voice_span_repl, text, flags=re.DOTALL)

    # Escape xml special chars for safety (later we re-insert tags)
    # We'll operate on a working copy, then post-process
    orig = text

    # Convert strong emphasis **text** -> internal marker
    text = re.sub(r"\*\*(.+?)\*\*", lambda m: f"<emph_strong>{m.group(1)}</emph_strong>", text)

    # Convert italics *text* or _text_ -> thought marker
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", lambda m: f"<thought>{m.group(1)}</thought>", text)
    text = re.sub(r"_(.+?)_", lambda m: f"<thought>{m.group(1)}</thought>", text)

    # Quotes "..." -> QUOTE markers
    text = re.sub(r'"(.+?)"', lambda m: f"<quote>{m.group(1)}</quote>", text)

    # Ellipses -> placeholder
    text = re.sub(r"\.\.\.", "<ellipsis/>", text)

    # Em-dash
    text = text.replace("—", " <emdash/> ")
    text = text.replace("--", " <emdash/> ")

    # Comma/period placeholders (we will turn into <break/> later)
    text = re.sub(r",\s+", ",<comma/> ", text)
    text = re.sub(r"\.\s+", ".<period/> ", text)

    # Parentheses -> markers
    text = re.sub(r"\(([^)]+)\)", lambda m: f"<paren>{m.group(1)}</paren>", text)

    # ALLCAPS words -> emphasis
    text = re.sub(r"\b([A-ZÄÖÜ]{2,})\b", lambda m: f"<allcaps>{m.group(1)}</allcaps>", text)

    # Numbers -> say-as
    text = re.sub(r"\b(\d[\d.,:/-]*)\b", lambda m: f"<num>{m.group(1)}</num>", text)

    # Now escape remaining XML-sensitive chars
    text = escape_xml(text)

    # Reinstate markers with SSML
    # Thoughts -> softer prosody
    text = text.replace("&lt;thought&gt;", "<thought>").replace("&lt;/thought&gt;", "</thought>")
    text = text.replace("&lt;quote&gt;", "<quote>").replace("&lt;/quote&gt;", "</quote>")
    text = text.replace("&lt;ellipsis/&gt;", "<ellipsis/>")
    text = text.replace("&lt;emdash/&gt;", "<emdash/>")
    text = text.replace("&lt;paren&gt;", "<paren>").replace("&lt;/paren&gt;", "</paren>")
    text = text.replace("&lt;emph_strong&gt;", "<emph_strong>").replace("&lt;/emph_strong&gt;", "</emph_strong>")
    text = text.replace("&lt;allcaps&gt;", "<allcaps>").replace("&lt;/allcaps&gt;", "</allcaps>")
    text = text.replace("&lt;num&gt;", "<num>").replace("&lt;/num&gt;", "</num>")

    # Insert SSML for markers
    # Quoted blocks -> voice switch if short; otherwise prosody change
    if prefer_guest_voice:
        quote_open = '<voice name="guest_de_1"><prosody rate="102%">'
        quote_close = '</prosody></voice>'
    else:
        quote_open = '<prosody rate="102%" pitch="+1st">'
        quote_close = '</prosody>'
    text = text.replace('<quote>', quote_open).replace('</quote>', quote_close)

    # Thoughts
    text = text.replace('<thought>', '<prosody rate="90%" pitch="-3st" volume="soft">')
    text = text.replace('</thought>', '</prosody>')

    # Ellipsis -> break
    text = text.replace('<ellipsis/>', f'<break time="{ellipsis_ms}ms"/>')

    # Em dash -> short break
    text = text.replace('<emdash/>', '<break time="120ms"/>' )

    # Comma/period -> micro breaks
    text = text.replace('<comma/>', f'<break time="{comma_ms}ms"/>')
    text = text.replace('<period/>', f'<break time="{period_ms}ms"/>')

    # Insert small breathing markers around explicit voice spans that were converted to comments
    def _add_breaths(m):
        role = m.group(1)
        inner = m.group(2)
        # convert placeholder into safe comment markers with small breaths before/after
        return f'<!--VOICE:{role}--><break time="{breath_ms}ms"/>' + inner + f'<break time="{breath_ms}ms"/><!--/VOICE-->'

    text = re.sub(r"___VOICE_START_([^_]+)___(.*?)___VOICE_END___", _add_breaths, text, flags=re.DOTALL)

    # Parenthetical
    text = text.replace('<paren>', '<prosody volume="x-soft" rate="90%">').replace('</paren>', '</prosody>')

    # Strong emphasis
    text = text.replace('<emph_strong>', '<emphasis level="strong">').replace('</emph_strong>', '</emphasis>')

    # ALLCAPS
    text = text.replace('<allcaps>', '<emphasis level="strong">').replace('</allcaps>', '</emphasis>')

    # Numbers
    text = text.replace('<num>', '<say-as interpret-as="cardinal">').replace('</num>', '</say-as>')

    # Now build final SSML wrapper
    ssml = '<speak xml:lang="de-DE">\n  <voice name="podcast_conversational_de">\n    <p>\n      '
    ssml += text
    ssml += '\n    </p>\n  </voice>\n</speak>\n'

    # Optionally apply annotations (emotion/focus overrides) before lexicon
    if annotations:
        ssml = apply_annotations_to_ssml(ssml, annotations)

    # Now apply lexicon phoneme replacements only to text parts
    ssml = apply_lexicon_to_ssml(ssml, lexicon)
    return ssml


def main() -> int:
    ap = argparse.ArgumentParser(description="Prototype text -> SSML preprocessor")
    ap.add_argument("input", help="Input text file")
    ap.add_argument("--out", help="Output SSML file", required=True)
    ap.add_argument("--lexicon", help="Optional lexicon JSON file", default="")
    ap.add_argument("--annotations", help="Optional annotations JSON file (list of {text,emotion,intensity,overrides})", default="")
    ap.add_argument("--guest-voice", action="store_true", help="Prefer guest voice for quotes")
    ap.add_argument("--comma-ms", type=int, default=120, help="Comma pause in ms")
    ap.add_argument("--period-ms", type=int, default=350, help="Period/full-stop pause in ms")
    ap.add_argument("--ellipsis-ms", type=int, default=400, help="Ellipsis pause in ms")
    ap.add_argument("--breath-ms", type=int, default=120, help="Breath pause around voice spans in ms")
    args = ap.parse_args()

    inp = Path(args.input)
    out = Path(args.out)
    lex = Path(args.lexicon) if args.lexicon else None
    ann = Path(args.annotations) if args.annotations else None
    lexicon = load_lexicon(lex)
    annotations = []
    if ann and ann.exists():
        try:
            with ann.open('r', encoding='utf-8') as f:
                annotations = json.load(f)
        except Exception:
            annotations = []

    text = inp.read_text(encoding="utf-8")
    ssml = text_to_ssml(
        text,
        lexicon,
        prefer_guest_voice=bool(args.guest_voice),
        comma_ms=args.comma_ms,
        period_ms=args.period_ms,
        ellipsis_ms=args.ellipsis_ms,
        breath_ms=args.breath_ms,
        annotations=annotations,
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(ssml, encoding="utf-8")
    # write an annotated debug file
    (out.parent / (out.stem + ".annotated.txt")).write_text("Preprocessor applied\n", encoding="utf-8")
    print(f"Wrote: {out}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
