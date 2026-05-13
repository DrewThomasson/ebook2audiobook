#!/usr/bin/env python3
"""Command-line interface for SML Book Dialog Extractor."""

import argparse
import json
import os
import sys
from pathlib import Path

from sml_extractor.core import (
    check_booknlp_installation,
    convert_ebook_to_txt,
    extract_characters,
    load_booknlp_output,
    run_booknlp,
)
from sml_extractor.sml_generator import generate_sml_macros, generate_sml_output
from sml_extractor.voice_matcher import (
    auto_assign_voices,
    get_voice_display_name,
    scan_custom_voices,
    scan_voice_library,
)


def main():
    parser = argparse.ArgumentParser(
        description="SML Book Dialog Extractor - Convert books to SML format for ebook2audiobook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - process a book and generate SML output
  python cli.py input_book.txt --e2a-path /path/to/ebook2audiobook

  # With custom output directory
  python cli.py input_book.txt --e2a-path ~/ebook2audiobook -o output/

  # Process an epub file (requires Calibre)
  python cli.py mybook.epub --e2a-path ~/ebook2audiobook

  # Use pre-existing BookNLP output
  python cli.py --booknlp-dir existing_output/ --book-id mybook --e2a-path ~/ebook2audiobook -o sml_output/

  # Launch web GUI instead
  python cli.py --gui
        """,
    )

    parser.add_argument(
        "input_file",
        nargs="?",
        help="Input book file (.txt, .epub, .mobi, .pdf, etc.)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output",
        help="Output directory (default: output/)",
    )
    parser.add_argument(
        "--model",
        choices=["small", "big"],
        default="small",
        help="BookNLP model size (default: small)",
    )
    default_e2a_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    if not os.path.isdir(os.path.join(default_e2a_path, "voices")) and os.path.isdir("/ebook2audiobook/voices"):
        default_e2a_path = "/ebook2audiobook"

    parser.add_argument(
        "--e2a-path",
        default=default_e2a_path,
        help="Path to ebook2audiobook repository (required for voice assignment). "
        "Defaults to the parent directory of this tool.",
    )
    parser.add_argument(
        "--voices-dir",
        help="Path to custom voice files directory",
    )
    parser.add_argument(
        "--language",
        default="eng",
        help="Language code for voice selection (default: eng)",
    )
    parser.add_argument(
        "--booknlp-dir",
        help="Use existing BookNLP output directory instead of running BookNLP",
    )
    parser.add_argument(
        "--book-id",
        help="Book ID for loading existing BookNLP output (used with --booknlp-dir)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch web GUI instead of CLI mode",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host for web GUI (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port for web GUI (default: 7860)",
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio share link",
    )

    args = parser.parse_args()

    # Expand ~ in all path arguments
    if args.e2a_path:
        args.e2a_path = os.path.expanduser(args.e2a_path)
    if args.output_dir:
        args.output_dir = os.path.expanduser(args.output_dir)
    if args.voices_dir:
        args.voices_dir = os.path.expanduser(args.voices_dir)
    if args.booknlp_dir:
        args.booknlp_dir = os.path.expanduser(args.booknlp_dir)
    if args.input_file:
        args.input_file = os.path.expanduser(args.input_file)

    if args.gui:
        _launch_gui(args)
        return

    if not args.input_file and not args.booknlp_dir:
        parser.error("Either input_file or --booknlp-dir is required (or use --gui)")



    if not os.path.isdir(args.e2a_path):
        parser.error(f"ebook2audiobook path not found: {args.e2a_path}")

    voices_dir = os.path.join(args.e2a_path, "voices")
    if not os.path.isdir(voices_dir):
        parser.error(
            f"No 'voices/' directory found in {args.e2a_path}. "
            "Make sure this is the ebook2audiobook repository root."
        )

    _run_headless(args)


def _run_headless(args):
    """Run in headless/CLI mode."""

    def progress(msg, pct=0):
        print(f"[{pct:3d}%] {msg}")

    # Check BookNLP installation before starting
    if not args.booknlp_dir:
        ok, msg = check_booknlp_installation()
        if not ok:
            print(f"Error: {msg}")
            sys.exit(1)
        print("✓ BookNLP installation verified.\n")

    output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Get text file
    if args.booknlp_dir:
        booknlp_dir = os.path.abspath(args.booknlp_dir)
        book_id = args.book_id
        if not book_id:
            # Try to detect book_id from files in the directory
            for f in os.listdir(booknlp_dir):
                if f.endswith(".tokens"):
                    book_id = Path(f).stem
                    break
            if not book_id:
                print("Error: Could not determine book_id. Use --book-id.")
                sys.exit(1)
        progress(f"Loading existing BookNLP output for '{book_id}'...", 50)
    else:
        input_file = os.path.abspath(args.input_file)
        if not os.path.exists(input_file):
            print(f"Error: Input file not found: {input_file}")
            sys.exit(1)

        progress(f"Processing: {input_file}", 0)

        # Convert if needed
        txt_file = convert_ebook_to_txt(input_file, output_dir)
        progress(f"Text file: {txt_file}", 5)

        booknlp_dir = os.path.join(output_dir, "booknlp")
        result = run_booknlp(txt_file, booknlp_dir, args.model, progress)
        book_id = result["book_id"]

    # Step 2: Load BookNLP data
    booknlp_data = load_booknlp_output(booknlp_dir, book_id)
    progress("BookNLP data loaded.", 65)

    # Step 3: Extract characters
    characters = extract_characters(booknlp_data)
    progress(f"Found {len(characters)} characters.", 70)

    # Print character summary
    print("\n--- Characters Found ---")
    for i, char in enumerate(characters):
        gender = char.get("inferred_gender", "unknown")
        age = char.get("inferred_age_category", "unknown")
        name = char.get("normalized_name", f"Character{i}")
        print(f"  {i + 1}. {name} (gender: {gender}, age: {age})")
    print()

    # Step 4: Auto-assign voices from ebook2audiobook voice library
    voice_assignments = {}
    progress("Scanning ebook2audiobook voice library...", 75)
    voice_library = scan_voice_library(args.e2a_path, args.language)
    custom_voices = (
        scan_custom_voices(args.voices_dir) if args.voices_dir else None
    )
    voice_assignments = auto_assign_voices(
        characters, voice_library, custom_voices
    )
    progress(f"Auto-assigned {len(voice_assignments)} voices.", 80)

    print("--- Voice Assignments ---")
    for name, voice in voice_assignments.items():
        print(f"  {name} -> {get_voice_display_name(voice)}")
    print()

    # Step 5: Generate SML output (macro-based: voice tags use character names)
    if not booknlp_data.get("tokens") and "book_txt" not in booknlp_data:
        print("Error: No token data or book.txt found in BookNLP output. Cannot generate SML.")
        sys.exit(1)

    sml_output_path = os.path.join(output_dir, f"{book_id}.sml.txt")
    generate_sml_output(
        booknlp_data, characters, sml_output_path, voice_assignments, use_macros=True
    )
    progress(f"SML output written to: {sml_output_path}", 88)

    # Step 6: Generate deprecated SML output (path-based: voice tags use raw file paths)
    deprecated_sml_path = os.path.join(output_dir, f"{book_id}.deprecated.sml.txt")
    generate_sml_output(
        booknlp_data, characters, deprecated_sml_path, voice_assignments, use_macros=False
    )
    progress(f"Deprecated SML (path-based) written to: {deprecated_sml_path}", 92)

    # Step 7: Generate SML macros JSON
    macros_json_path = os.path.join(output_dir, f"{book_id}.sml.json")
    generate_sml_macros(characters, macros_json_path, voice_assignments)
    progress(f"SML Macros JSON written to: {macros_json_path}", 97)

    progress("Done!", 100)

    print(f"\n=== Output Files ===")
    print(f"  SML text (macro):      {sml_output_path}")
    print(f"  SML text (deprecated): {deprecated_sml_path}")
    print(f"  SML Macros JSON:       {macros_json_path}")
    if voice_assignments:
        print(f"\n  Voice assignments are embedded in the SML output.")
        print(f"  Use the SML file with ebook2audiobook for multi-speaker audiobook generation.")
    else:
        print(f"\n  No voices were matched from {args.e2a_path}.")
        print(f"  Check that voices/{args.language}/ contains voice files.")


def _launch_gui(args):
    """Launch the web GUI."""
    try:
        import gradio as gr
        from web_gui import create_app

        app = create_app(default_e2a_path=args.e2a_path or "")
        app.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            theme=gr.themes.Soft(),
        )
    except ImportError as e:
        print(f"Error: Could not launch GUI. Make sure gradio is installed: {e}")
        print("  pip install gradio")
        sys.exit(1)


if __name__ == "__main__":
    main()
