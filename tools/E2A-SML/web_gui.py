#!/usr/bin/env python3
"""Web GUI for SML Book Dialog Extractor using Gradio."""

import json
import os
import tempfile
from pathlib import Path

import gradio as gr

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
    get_voice_category_info,
    get_voice_display_name,
    scan_voice_library,
)

# Global state for the current session
_session_state = {}


def _get_file_path(file_obj) -> str:
    """Extract file path from a Gradio file object or string."""
    return file_obj.name if hasattr(file_obj, "name") else str(file_obj)


def _get_all_voice_paths(voice_library: dict) -> list:
    """Collect all voice file paths from the voice library into a flat list."""
    paths = []
    for age in voice_library:
        for gender in voice_library.get(age, {}):
            paths.extend(voice_library[age][gender])
    return sorted(paths)


def _voice_display_label(voice_path: str) -> str:
    """Create a human-readable label from a voice path, e.g. 'AlexandraHisakawa (adult/female)'."""
    info = get_voice_category_info(voice_path)
    name = info["name"]
    age = info["age"]
    gender = info["gender"]
    if age != "unknown" and gender != "unknown":
        return f"{name} ({age}/{gender})"
    return name


def process_book(
    input_file,
    model_size,
    e2a_path,
    progress=gr.Progress(),
):
    """Process a book file through BookNLP and extract characters."""
    if input_file is None:
        raise gr.Error("Please upload a book file.")

    # Validate ebook2audiobook path
    if not e2a_path or not e2a_path.strip():
        raise gr.Error(
            "Please provide the path to your ebook2audiobook folder.\n"
            "This is required for voice auto-assignment."
        )

    e2a_path = os.path.expanduser(e2a_path.strip())

    if not os.path.isdir(e2a_path):
        raise gr.Error(f"ebook2audiobook folder not found: {e2a_path}")

    voices_dir = os.path.join(e2a_path, "voices")
    if not os.path.isdir(voices_dir):
        raise gr.Error(
            f"No 'voices/' directory found in {e2a_path}.\n"
            "Make sure this is the ebook2audiobook repository root."
        )

    progress(0.05, desc="Preparing...")

    # Create temp working directory
    work_dir = tempfile.mkdtemp(prefix="sml_extractor_")
    _session_state["work_dir"] = work_dir

    input_path = _get_file_path(input_file)

    # Convert to txt if needed
    progress(0.1, desc="Converting to text...")
    try:
        txt_path = convert_ebook_to_txt(input_path, work_dir)
    except RuntimeError as e:
        raise gr.Error(str(e))

    # Run BookNLP
    booknlp_dir = os.path.join(work_dir, "booknlp")
    progress(0.12, desc="Checking BookNLP installation...")

    ok, msg = check_booknlp_installation()
    if not ok:
        raise gr.Error(f"BookNLP is not properly installed:\n{msg}")

    progress(0.15, desc=f"Running BookNLP ({model_size} model)... This may take a while.")

    try:
        result = run_booknlp(txt_path, booknlp_dir, model_size)
    except Exception as e:
        raise gr.Error(f"BookNLP processing failed: {e}")

    book_id = result["book_id"]
    _session_state["book_id"] = book_id
    _session_state["booknlp_dir"] = booknlp_dir

    progress(0.6, desc="Loading results...")

    # Load data
    booknlp_data = load_booknlp_output(booknlp_dir, book_id)
    _session_state["booknlp_data"] = booknlp_data

    # Extract characters
    characters = extract_characters(booknlp_data)
    _session_state["characters"] = characters

    progress(0.7, desc="Scanning voice library...")

    # Scan voice library from ebook2audiobook
    voice_library = scan_voice_library(e2a_path)
    _session_state["voice_library"] = voice_library
    _session_state["e2a_path"] = e2a_path

    # Auto-assign voices based on each character's inferred gender and age
    voice_assignments = {}
    if voice_library:
        voice_assignments = auto_assign_voices(characters, voice_library)
    _session_state["voice_assignments"] = voice_assignments

    progress(0.8, desc="Preparing character editor...")

    # Build character table for display
    char_table = _build_character_table(characters, voice_assignments)

    # Build available voices dropdown choices
    char_names = [c.get("normalized_name", "Unknown") for c in characters]
    voice_choices = _build_voice_choices(voice_library)

    # Get preview of book text
    book_txt = booknlp_data.get("book_txt", "")
    preview = book_txt[:3000] + ("..." if len(book_txt) > 3000 else "")

    progress(1.0, desc="Done!")

    num_voices = len(voice_assignments)
    status_msg = (
        f"✅ Processed successfully!\n"
        f"📚 Book ID: {book_id}\n"
        f"👥 Characters found: {len(characters)}\n"
        f"🎤 Voices auto-assigned: {num_voices}"
    )

    # Update character dropdown choices
    char_dropdown_update = gr.update(choices=char_names, value=char_names[0] if char_names else None)
    voice_dropdown_update = gr.update(choices=voice_choices, value=None)

    return (
        status_msg,                         # status_output
        char_table,                         # char_table
        preview,                            # book_preview
        gr.update(visible=True),            # char_voice_section
        gr.update(visible=True),            # generate_btn
        char_dropdown_update,               # char_selector
        voice_dropdown_update,              # voice_selector
        _format_char_detail(characters, voice_assignments, char_names[0] if char_names else None),
    )


def _build_character_table(characters, voice_assignments):
    """Build a list-of-lists table for the character editor."""
    rows = []
    for char in characters:
        name = char.get("normalized_name", "Unknown")
        gender = char.get("inferred_gender", "unknown")
        age = char.get("inferred_age_category", "unknown")
        voice = voice_assignments.get(name, "")
        voice_display = _voice_display_label(voice) if voice else "(none)"
        rows.append([name, gender, age, voice_display])
    return rows


def _build_voice_choices(voice_library):
    """Build dropdown choices as (label, value) for available voices."""
    choices = [("(none)", "")]
    all_voices = _get_all_voice_paths(voice_library)
    for v in all_voices:
        choices.append((_voice_display_label(v), v))
    return choices


def _format_char_detail(characters, voice_assignments, selected_name):
    """Format detail text for the currently selected character."""
    if not selected_name:
        return "No character selected."

    for char in characters:
        if char.get("normalized_name") == selected_name:
            gender = char.get("inferred_gender", "unknown")
            age = char.get("inferred_age_category", "unknown")
            voice = voice_assignments.get(selected_name, "")
            voice_label = _voice_display_label(voice) if voice else "(none)"
            return (
                f"**{selected_name}**\n"
                f"  • Inferred gender: {gender}\n"
                f"  • Inferred age category: {age}\n"
                f"  • Assigned voice: {voice_label}"
            )
    return f"Character '{selected_name}' not found."


def on_char_selected(char_name):
    """Called when the user selects a character from the dropdown."""
    characters = _session_state.get("characters", [])
    voice_assignments = _session_state.get("voice_assignments", {})

    detail = _format_char_detail(characters, voice_assignments, char_name)

    # Pre-select the currently assigned voice in the voice dropdown
    current_voice = voice_assignments.get(char_name, "")
    return detail, gr.update(value=current_voice)


def reassign_voice(char_name, voice_path):
    """Reassign a voice to a character and refresh the table."""
    if not char_name:
        return "Please select a character first.", gr.update(), ""

    if "voice_assignments" not in _session_state:
        _session_state["voice_assignments"] = {}

    if voice_path and voice_path.strip():
        _session_state["voice_assignments"][char_name] = voice_path.strip()
        voice_label = _voice_display_label(voice_path)
    else:
        _session_state["voice_assignments"].pop(char_name, None)
        voice_label = "(none)"

    characters = _session_state.get("characters", [])
    voice_assignments = _session_state["voice_assignments"]

    char_table = _build_character_table(characters, voice_assignments)
    detail = _format_char_detail(characters, voice_assignments, char_name)

    return (
        char_table,
        f"✅ {char_name} → {voice_label}",
        detail,
    )


def generate_output(progress=gr.Progress()):
    """Generate the SML output files."""
    if "booknlp_data" not in _session_state:
        raise gr.Error("Please process a book first.")

    booknlp_data = _session_state["booknlp_data"]
    characters = _session_state.get("characters", [])
    voice_assignments = _session_state.get("voice_assignments", {})
    book_id = _session_state.get("book_id", "book")
    work_dir = _session_state.get("work_dir", tempfile.mkdtemp(prefix="sml_extractor_"))

    book_txt = booknlp_data.get("book_txt", "")
    has_tokens = bool(booknlp_data.get("tokens"))
    if not book_txt and not has_tokens:
        raise gr.Error("No book text data found. BookNLP may not have generated output files.")

    progress(0.3, desc="Generating SML output...")

    output_dir = os.path.join(work_dir, "sml_output")
    os.makedirs(output_dir, exist_ok=True)

    # Generate SML text with macro-based voice tags (character names)
    sml_path = os.path.join(output_dir, f"{book_id}.sml.txt")
    generate_sml_output(booknlp_data, characters, sml_path, voice_assignments, use_macros=True)

    progress(0.5, desc="Generating deprecated SML (path-based)...")

    # Generate deprecated SML with raw voice file paths in tags
    deprecated_sml_path = os.path.join(output_dir, f"{book_id}.deprecated.sml.txt")
    generate_sml_output(booknlp_data, characters, deprecated_sml_path, voice_assignments, use_macros=False)

    progress(0.75, desc="Generating SML macros JSON...")

    # Generate SML macros JSON
    macros_path = os.path.join(output_dir, f"{book_id}.sml.json")
    generate_sml_macros(characters, macros_path, voice_assignments)

    progress(0.9, desc="Preparing download...")

    # Read generated content for preview
    with open(sml_path, "r", encoding="utf-8") as f:
        sml_content = f.read()

    sml_preview = sml_content[:5000] + ("..." if len(sml_content) > 5000 else "")

    progress(1.0, desc="Done!")

    return (
        f"✅ Generated successfully!\n\nFiles:\n  - {sml_path}\n  - {deprecated_sml_path}\n  - {macros_path}",
        sml_preview,
        sml_path,
        deprecated_sml_path,
        macros_path,
    )


def create_app(default_e2a_path: str = ""):
    """Create the Gradio web application.

    Args:
        default_e2a_path: Default value for the ebook2audiobook path field.
    """

    with gr.Blocks(
        title="SML Book Dialog Extractor",
    ) as app:

        gr.Markdown(
            """
            # 📚 SML Book Dialog Extractor

            Convert books to **SML format** for multi-speaker audiobook generation with
            [ebook2audiobook](https://github.com/DrewThomasson/ebook2audiobook).

            This tool uses [BookNLP](https://github.com/DrewThomasson/booknlp) to analyze books,
            identify characters and their dialog, then generates SML-tagged output with voice assignments.

            ### How it works:
            1. **Upload** a book file (.txt, .epub, .mobi, etc.)
            2. **Analyze** - BookNLP identifies characters, dialog, and narration
            3. **Assign voices** - Auto-assign from ebook2audiobook library
            4. **Generate** - Download SML output ready for ebook2audiobook
            """
        )

        with gr.Tab("📖 Process Book"):
            with gr.Row():
                with gr.Column(scale=2):
                    input_file = gr.File(
                        label="📁 Upload Book File",
                        file_types=[".txt", ".epub", ".mobi", ".pdf", ".html", ".fb2", ".azw", ".azw3"],
                        type="filepath",
                    )
                with gr.Column(scale=1):
                    model_size = gr.Radio(
                        ["small", "big"],
                        value="small",
                        label="🧠 BookNLP Model",
                        info="'big' is more accurate but slower and requires more RAM/GPU",
                    )
                    e2a_path = gr.Textbox(
                        label="📂 ebook2audiobook Path (required)",
                        placeholder="/path/to/ebook2audiobook",
                        value=default_e2a_path,
                        info="Full path to your local ebook2audiobook folder (supports ~/)",
                    )

            process_btn = gr.Button("🔍 Analyze Book", variant="primary", size="lg")
            status_output = gr.Textbox(label="Status", interactive=False)

        with gr.Tab("👥 Characters & Voices"):
            gr.Markdown(
                "After analyzing a book, all detected characters are listed below with their "
                "**inferred gender** and **age category** from BookNLP. Voices are auto-assigned "
                "from the ebook2audiobook voice library. Select any character to change its voice."
            )

            char_table = gr.Dataframe(
                headers=["Character", "Gender", "Age", "Assigned Voice"],
                datatype=["str", "str", "str", "str"],
                label="📋 Detected Characters",
                interactive=False,
            )

            with gr.Group(visible=False) as char_voice_section:
                gr.Markdown("### 🎤 Reassign Voice")
                with gr.Row():
                    with gr.Column(scale=1):
                        char_selector = gr.Dropdown(
                            label="Select Character",
                            choices=[],
                            interactive=True,
                        )
                        char_detail = gr.Markdown("Select a character to see details.")

                    with gr.Column(scale=1):
                        voice_selector = gr.Dropdown(
                            label="Select Voice",
                            choices=[],
                            interactive=True,
                            info="Pick a voice from the ebook2audiobook library",
                        )
                        assign_btn = gr.Button("🎤 Assign Selected Voice", variant="primary")
                        assign_status = gr.Textbox(label="Status", interactive=False)

        with gr.Tab("📝 Preview & Generate"):
            book_preview = gr.Textbox(
                label="📖 Book Text Preview (BookNLP tagged)",
                lines=15,
                interactive=False,
            )

            generate_btn = gr.Button(
                "🎵 Generate SML Output",
                variant="primary",
                size="lg",
                visible=False,
            )

            gen_status = gr.Textbox(label="Generation Status", interactive=False)
            sml_preview = gr.Textbox(
                label="📄 SML Output Preview",
                lines=15,
                interactive=False,
            )

            with gr.Row():
                sml_download = gr.File(label="📥 Download SML Text (macro)", interactive=False)
                deprecated_sml_download = gr.File(label="📥 Download Deprecated SML (path-based)", interactive=False)
                macros_download = gr.File(label="📥 Download SML Macros JSON", interactive=False)

        # --- Wire up events ---

        # Process book → populate character table, dropdowns, and preview
        process_btn.click(
            fn=process_book,
            inputs=[input_file, model_size, e2a_path],
            outputs=[
                status_output,
                char_table,
                book_preview,
                char_voice_section,
                generate_btn,
                char_selector,
                voice_selector,
                char_detail,
            ],
        )

        # Selecting a character → show details and current voice
        char_selector.change(
            fn=on_char_selected,
            inputs=[char_selector],
            outputs=[char_detail, voice_selector],
        )

        # Assign voice from dropdown → update table and detail
        assign_btn.click(
            fn=reassign_voice,
            inputs=[char_selector, voice_selector],
            outputs=[char_table, assign_status, char_detail],
        )

        # Generate SML output
        generate_btn.click(
            fn=generate_output,
            outputs=[gen_status, sml_preview, sml_download, deprecated_sml_download, macros_download],
        )

    return app


if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="127.0.0.1", server_port=7860, theme=gr.themes.Soft())
