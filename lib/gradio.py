from lib.core import *

def build_interface(args:dict)->gr.Blocks:
    from lib.classes.tts_engines.common.preset_loader import load_engine_presets
    try:
        script_mode = args['script_mode']
        is_gui_process = args['is_gui_process']
        is_gui_shared = args['share']
        title = 'Ebook2Audiobook'
        gr_glassmask_msg = 'Initialization, please wait…'
        models = None
        language_options = [
            (
                f"{details['name']} - {details['native_name']}" if details['name'] != details['native_name'] else details['name'],
                lang
            )
            for lang, details in language_mapping.items()
        ]
        voice_options = []
        tts_engine_options = []
        custom_model_options = []
        fine_tuned_options = []
        audiobook_options = []
        options_output_split_hours = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        page_size = 15
        visible_gr_tab_xtts_params = interface_component_options['gr_tab_xtts_params']
        visible_gr_tab_bark_params = interface_component_options['gr_tab_bark_params']
        visible_gr_group_voice_file = interface_component_options['gr_group_voice_file']
        visible_gr_group_custom_model = interface_component_options['gr_group_custom_model']
        js_hide_elements = 'document.querySelector("#ebook_textarea_toolbar")?.remove();'
        js_show_elements = 'window.gr_ebook_textarea_counter();'
        theme = gr.themes.Origin(
            primary_hue='green',
            secondary_hue='amber',
            neutral_hue='gray',
            radius_size='lg',
            font_mono=['JetBrains Mono', 'monospace', 'Consolas', 'Menlo', 'Liberation Mono']
        )
        header_css = '''
            <style>
                /* Global Scrollbar Customization */
                /* The entire scrollbar */
                ::-webkit-scrollbar {
                    width: 6px !important;
                    height: 6px !important;
                    cursor: pointer !important;;
                }
                /* The scrollbar track (background) */
                ::-webkit-scrollbar-track {
                    background: none transparent !important;
                    border-radius: 6px !important;
                }
                /* The scrollbar thumb (scroll handle) */
                ::-webkit-scrollbar-thumb {
                    background: #c09340 !important;
                    border-radius: 6px !important;
                }
                /* The scrollbar thumb on hover */
                ::-webkit-scrollbar-thumb:hover {
                    background: #ff8c00 !important;
                }
                /* Firefox scrollbar styling */
                html {
                    scrollbar-width: thin !important;
                    scrollbar-color: #c09340 none !important;
                }
                button:disabled {
                    pointer-events: none;
                }
                button div.wrap span {
                    display: none !important;
                }
                button div.wrap::after {
                    content: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231E90FF' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/><polyline points='17 8 12 3 7 8'/><line x1='12' y1='3' x2='12' y2='15'/></svg>") !important;
                    width: 24px !important;
                    height: 24px !important;
                    display: inline-block !important;
                    vertical-align: middle !important;
                }
                body:has(#gr_convert_btn:disabled) table.file-preview button.label-clear-button {
                    display: none !important;
                }
                span[data-testid="block-info"] {
                    font-size: 12px !important;
                }
                /////////////////////
                .wrap-inner {
                    border: 1px solid #666666;
                }
                .no-wrap {
                    flex-wrap: nowrap !important;
                }
                .selected {
                    color: var(--secondary-500) !important;
                    text-shadow: 0.3px 0.3px 0.3px #303030;
                }
                .overflow-menu {
                    display: none !important;
                }
                .gr-glass-mask {
                    z-index: 9999 !important;
                    position: fixed !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100vw !important; 
                    height: 100vh !important;
                    background: rgba(0,0,0,0.5) !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    font-size: 1.2rem !important;
                    color: #ffffff !important;
                    text-align: center !important;
                    border: none !important;
                    opacity: 1;
                    pointer-events: all !important;
                }
                .gr-glass-mask.hide {
                    animation: fadeOut 2s ease-out 2s forwards !important;
                }
                .small-btn{
                    background: var(--block-background-fill) !important;
                    font-size: 22px !important;
                    width: 60px !important;
                    height: 100% !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                .small-btn:hover {
                    background: var(--button-primary-background-fill-hover) !important;
                    font-size: 28px !important;
                }
                .small-btn-red{
                    background: var(--block-background-fill) !important;
                    font-size: 22px !important;
                    width: 60px !important;
                    height: 60px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                .small-btn-red:hover {
                    background-color: #ff5050 !important;
                    font-size: 28px !important;
                }
                .small-btn-lock{
                    background: var(--block-background-fill) !important;
                    font-size: 18px !important;
                    width: 60px !important;
                    height: 60px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                }
                .small-btn-lock:hover {
                    background-color: #752eb2 !important;
                    font-size: 20px !important;
                }
                .small-btn-lock:active {
                    background: var(--body-text-color) !important;
                    font-size: 20px !important;
                    color: var(--body-background-fill) !important;
                }
                .small-btn:active, .small-btn-red:active {
                    background: var(--body-text-color) !important;
                    font-size: 30px !important;
                    color: var(--body-background-fill) !important;
                }
                .micro-btn{
                    font-size: 16px !important;
                    background: var(--block-background-fill) !important;
                    width: 26px !important;
                    height: 26px !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    border-radius: var(--radius-full) !important;
                }
                .micro-btn:hover {
                    background-color: #ff5050 !important;
                }
                .micro-btn:active {
                    background: var(--body-text-color) !important;
                    color: var(--body-background-fill) !important;
                }
                .file-preview-holder {
                    height: 116px !important;
                    overflow: auto !important;
                }
                .progress-bar.svelte-ls20lj {
                    background: var(--secondary-500) !important;
                }
                .file-preview-holder {
                    height: auto !important;
                    min-height: 0 !important;
                    max-height: none !important;
                }
                ///////////////////
                .gr-tab {
                    padding: 0 3px 0 3px !important;
                    margin: 0 !important;
                    border: none !important;
                }
                .gr-col {
                    padding: 0 6px 0 6px !important;
                    margin: 0 !important;
                    border: none !important;
                }
                .gr-group-main > div {
                    background: none !important;
                    border-radius: var(--radius-md) !important;
                }
                .gr-group > div {
                    background: none !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    border-radius: 0 var(--radius-md) var(--radius-md) var(--radius-md) !important;
                }
                .gr-group-sides-padded{
                    background: none !important;
                    margin: 0 var(--size-2) 0 var(--size-2)!important;;
                    border-radius: 0 var(--radius-md) var(--radius-md) var(--radius-md) !important;
                }
                .gr-group-convert-btn{
                    margin: var(--size-2) !important;;
                    border-radius: var(--radius-md) !important;
                }
                .gr-label textarea[data-testid="textbox"]{
                    padding: 0 0 0 3px !important;
                    margin: 0 !important;
                    text-align: left !important;
                    font-weight: normal !important;
                    height: auto !important;
                    font-size: 12px !important;
                    border: none !important;
                    overflow-y: hidden !important;
                    line-height: 12px !important;
                }
                .gr-markdown p {
                    margin-top: 8px !important;
                    width: 90px !important;
                    padding: 0 !important;
                    border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
                    background: var(--block-background-fill) !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    text-align: center !important;
                }
                .gr-markdown-span {
                    margin-top: 8px !important;
                    width: 90px !important;
                    padding: 0 !important;
                    border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
                    background: var(--block-background-fill) !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    text-align: center !important;            
                }
                .gr-markdown-output-split-hours {
                    overflow: hidden !important;
                    background: var(--block-background-fill) !important;
                    border-radius: 0 !important; 
                    font-size: 12px !important;
                    text-align: center !important;
                    vertical-align: middle !important;
                    padding-top: 4px !important;
                    padding-bottom: 4px !important;
                    white-space: nowrap !important;
                }
                .gr-voice-player {
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 60px !important;
                    height: 60px !important;
                    background: var(--block-background-fill) !important;
                }
                .play-pause-button:hover svg {
                    fill: #ffab00 !important;
                    stroke: #ffab00 !important;
                    transform: scale(1.2) !important;
                }
                .gr-convert-btn {
                    font-size: 30px !important;
                }
                .gr-convert-btn:hover { background-color: #34d058 !important; }
                .gr-convert-btn:active, .button-red:active {
                    background: var(--body-text-color) !important;
                    color: var(--body-background-fill) !important;
                }
                [id^="block_"]:has(input[type="checkbox"]:checked) {
                    border-left: 3px solid #22c55e !important;
                }
                [id^="block_"]:has(input[type="checkbox"]:checked) > div {
                    background-color: rgba(34, 197, 94, 0.08) !important;
                }
                [id^="block_"]:has(input[type="checkbox"]:not(:checked)) {
                    border-left: 3px solid #ef4444 !important;
                }
                [id^="block_"]:has(input[type="checkbox"]:not(:checked)) > div {
                    background-color: rgba(239, 68, 68, 0.08) !important;
                }
                ////////////////////
                #gr_ebook_textarea {
                    height: auto !important;
                    min-height: 55px !important;
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: center !important;
                    justify-content: center !important;
                }
                #gr_ebook_textarea label, #gr_custom_model_file label {
                    background: none !important;
                    border: none !important;
                }
                #gr_audiobook_player label {
                    display: none !important;
                }
                #gr_ebook_src, #gr_custom_model_file, #gr_voice_file {
                    height: auto !important;
                    min-height: 100px !important;
                    display: flex !important;
                    flex-direction: column !important;
                    align-items: center !important;
                    justify-content: center !important;
                }
                #gr_ebook_src button>div, #gr_ebook_textarea button>div, #gr_custom_model_file button>div, #gr_voice_file button>div {
                    font-size: 12px !important;
                }
                #gr_ebook_src .empty, #gr_ebook_textarea .empty, #gr_custom_model_file .empty, #gr_voice_file .empty,
                #gr_ebook_src .wrap, #gr_ebook_textarea .wrap, #gr_custom_model_file .wrap, #gr_voice_file .wrap {
                    height: 100% !important;
                    min-height: 100px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                }
                #gr_ebook_src button[aria-label="common.upload"], #gr_ebook_textarea  button[aria-label="common.upload"], #gr_custom_model_file button[aria-label="common.upload"], #gr_voice_file button[aria-label="common.upload"] {
                    display: none !important;
                }
                #gr_ebook_src .file-preview-holder {
                    padding-top: 16px !important;
                }
                .gr-voice-highlight-css { display: none !important; }
                #gr_ebook_src table.file-preview tbody > tr.file:hover {
                    background: var(--color-accent-soft) !important;
                }
                #gr_voice_selected_filename {
                    display: flex !important;
                    align-items: center !important;
                    margin: auto !important;
                    padding-left: 6px;
                    overflow: hidden !important;
                    text-overflow: ellipsis !important;
                    white-space: nowrap !important;
                    background: var(--block-background-fill) !important;
                    width: 100% !important;
                    height: 100% !important;
                }
                #gr_voice_selected_filename p {
                    margin: auto !important;
                    vertical-align: middle !important;
                    overflow: hidden !important;
                    text-overflow: ellipsis !important;
                    background: var(--block-background-fill) !important;
                    width: 100% !important;
                    height: 100% !important;
                }
                #gr_custom_model_file [aria-label="Clear"], #gr_voice_file [aria-label="Clear"] {
                    display: none !important;
                }               
                #gr_fine_tuned_list {
                    height: 95px !important;
                }
                #gr_voice_list {
                    height: 60px !important;
                }
                #gr_output_format_list {
                    height: 103px !important;
                }
                #gr_row_output_split_hours {
                    border-radius: 0 !important;
                }
                #gr_progress .progress-bar {
                    background: #ff7b00 !important;
                }
                #gr_audiobook_sentence textarea{
                    margin: auto !important;
                    text-align: center !important;
                }
                #gr_session textarea, #gr_progress textarea {
                    overflow: hidden !important;
                    overflow-y: auto !important;
                    scrollbar-width: none !important;
                }
                #gr_session textarea::-webkit-scrollbar, #gr_progress textarea::-webkit-scrollbar {
                    display: none !important; 
                }
                #gr_ebook_mode span[data-testid="block-info"],
                #gr_language span[data-testid="block-info"],
                #gr_voice_list span[data-testid="block-info"],
                #gr_device span[data-testid="block-info"],
                #gr_tts_engine_list span[data-testid="block-info"],
                #gr_output_split_hours span[data-testid="block-info"],
                #gr_session span[data-testid="block-info"],
                #gr_custom_model_list span[data-testid="block-info"],
                #gr_audiobook_sentence span[data-testid="block-info"],
                #gr_audiobook_list span[data-testid="block-info"],
                #gr_progress span[data-testid="block-info"]{
                    display: none !important;
                }
                #gr_row_ebook_mode { align-items: center !important; }
                #gr_blocks_preview {
                    align-self: center !important; 
                    overflow: visible !important;
                    padding: 20px 0 20px 10px !important;
                }
                #gr_group_output_split {
                    border-radius: 0 !important;
                }
                #gr_tts_rating {
                    overflow: hidden !important;
                }
                #gr_row_voice_player, #gr_row_custom_model_list, #gr_row_session, #gr_row_audiobook_list {
                    height: 60px !important;
                }
                #gr_audiobook_player :is(.volume, .empty, .source-selection, .control-wrapper, .settings-wrapper, label), #gr_audiobook_files label[data-testid="block-label"] {
                    display: none !important;
                }
                #gr_audiobook_player audio {
                    width: 100% !important;
                    padding-top: 10px !important;
                    padding-bottom: 10px !important;
                    border-radius: 0px !important;
                    background-color: #ebedf0 !important;
                    color: #ffffff !important;
                }
                #gr_audiobook_player audio::-webkit-media-controls-panel {
                    width: 100% !important;
                    padding-top: 10px !important;
                    padding-bottom: 10px !important;
                    border-radius: 0px !important;
                    background-color: #ebedf0 !important;
                    color: #ffffff !important;
                }
                #gr_voice_player_hidden {
                    z-index: -100 !important;
                    position: absolute !important;
                    overflow: hidden !important;
                    margin: 0 !important;
                    padding: 0 !important;
                    width: 60px !important;
                    height: 60px !important;
                }
                #gr_session_update, #gr_restore_session, #gr_save_session,
                #gr_audiobook_vtt, #gr_playback_time {
                    display: none !important;
                }
                #gr_blocks_nav {
                    overflow:hidden !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                }
                #gr_blocks_nav p {
                    white-space:nowrap !important;
                    overflow:hidden !important;
                    font-size: 16px !important;
                    text-align: center !important;
                }
                #gr_row_buttons {
                    justify-content: center !important;
                    gap: 100px !important;
                }
                #gr_blocks_markdown {
                    background: var(--body-background-fill) !important;
                    width: 100% !important;
                    text-align: center !important;
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    padding-bottom: 20px !important;
                }
                #gr_blocks_markdown p {
                    background: var(--body-background-fill) !important;
                    width: 100% !important;
                    font-size: 18px !important;
                    font-weight: bold !important;
                }
                ///////////
                .fade-in {
                    animation: fadeIn 1s ease-in !important;
                    display: inline-block !important;
                }
                @keyframes fadeIn {
                    from {
                        opacity: 0;
                        visibility: visible !important;
                    }
                    to {
                        opacity: 1;
                    }
                }
                @keyframes fadeOut {
                    from {
                        opacity: 1;
                    }
                    to {
                        opacity: 0;
                        visibility: hidden;
                        pointer-events: none;
                    }
                }
                //////////
                #custom-gr-modal-container,
                #custom-gr-modal-container .gr-modal {
                    position: fixed !important;
                }
                .hide-elem {
                    z-index: -1 !important;
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                }
                .gr-modal {
                    position: fixed !important;
                    top: 0 !important; left: 0 !important;
                    width: 100% !important; height: 100% !important;
                    background-color: rgba(0, 0, 0, 0.5) !important;
                    z-index: 9999 !important;
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                }
                .gr-modal-content {
                    background-color: #333 !important;
                    padding: 20px !important;
                    border-radius: 9px !important;
                    text-align: center !important;
                    max-width: 300px !important;
                    height: auto !important;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5) !important;
                    border: 2px solid #FFA500 !important;
                    color: white !important;
                    position: relative !important;
                }
                .gr-modal-content p {
                    overflow-wrap: break-word;
                    word-break: break-word;
                    white-space: normal;
                }
                .confirm-buttons {
                    display: flex !important;
                    justify-content: space-evenly !important;
                    margin-top: 20px !important;
                }
                .confirm-buttons button {
                    padding: 10px 20px !important;
                    border: none !important;
                    border-radius: 6px !important;
                    font-size: 16px !important;
                    cursor: pointer !important;
                }
                .accordion-block-even > button, .accordion-block-odd > button {
                    padding: 10px 0 10px 0 !important;
                }
                .accordion-block-even, .accordion-block-even div label textarea, .accordion-block-even .wrap {
                    background: var(--table-even-background-fill) !important;
                }
                .accordion-block-odd, .accordion-block-odd div label textarea, .accordion-block-odd .wrap {
                    background: var(--table-odd-background-fill) !important;
                }
                .accordion-block-even:hover,
                .accordion-block-odd:hover {
                    background: rgba(255, 200, 50, 0.3) !important;
                }
                .accordion-block-voice-list {
                    margin: auto !important;
                    padding: 0 16px 0 0 !important;
                }
                .gr-blocks-buttons {
                    display: flex !important;
                    justify-content: space-evenly !important;
                    margin-top: 12px !important;
                    margin-bottom: 12px !important;
                }
                .gr-blocks-buttons button {
                    padding: 12px !important;
                    border: none !important;
                    border-radius: 9px !important;
                    font-size: 16px !important;
                    cursor: pointer !important;
                }
                .gr-blocks-buttons:hover { background-color: #34d058 !important; }
                .gr-blocks-buttons:active, .button-red:active {
                    background: var(--body-text-color) !important;
                    color: var(--body-background-fill) !important;
                }
                .accordion-block-keep, .accordion-block-keep .wrap{
                    background: none !important;
                }
                .accordion-block-reset {
                    margin-left: 30px !important;
                    margin-right: 30px !important;
                    border-radius: 9px !important;
                }
                .button-green { background-color: #28a745 !important; color: white !important; }
                .button-green:hover { background-color: #34d058 !important; }
                .button-green:active, .button-red:active {
                    background: var(--body-text-color) !important;
                    color: var(--body-background-fill) !important;
                }
                .button-red  {background-color: #dc3545 !important; color: white !important; }
                .button-red:hover  { background-color: #ff6f71 !important; }
                .button-green:active, .button-red:active {
                    background: var(--body-text-color) !important;
                    color: var(--body-background-fill) !important;
                }
                .spinner {
                    margin: 15px auto !important;
                    border: 4px solid rgba(255, 255, 255, 0.2) !important;
                    border-top: 4px solid #FFA500 !important;
                    border-radius: 50% !important;
                    width: 30px !important;
                    height: 30px !important;
                    animation: spin 1s linear infinite !important;
                }
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        '''
        
        with gr.Blocks(theme=theme, title=title, css=header_css, delete_cache=(604800, 86400)) as app:
            with gr.Group(visible=True, elem_id='gr_group_main', elem_classes='gr-group-main') as gr_group_main:
                with gr.Tabs(elem_id='gr_tabs') as gr_tabs:
                    with gr.Tab('Dashboard', elem_id='gr_tab_main', elem_classes='gr-tab') as gr_tab_main:
                        with gr.Row(elem_id='gr_row_tab_main'):
                            with gr.Column(elem_id='gr_col_1', elem_classes=['gr-col'], scale=3):
                                with gr.Group(elem_id='gr_group_ebook_src', elem_classes=['gr-group']):
                                    gr_import_markdown = gr.Markdown(elem_id='gr_import_markdown', elem_classes=['gr-markdown'], value='Import')
                                    gr_ebook_src = gr.File(show_label=False, label='-', elem_id='gr_ebook_src', visible=True, file_types=ebook_formats, file_count=ebook_modes['SINGLE'], allow_reordering=True, height=100)
                                    gr_voice_highlight_css = gr.HTML(value='', elem_classes=['gr-voice-highlight-css'])
                                    gr_ebook_textarea = gr.Textbox(show_label=True, label='Text Prompt', elem_id='gr_ebook_textarea', visible=False, lines=8, max_length=max_ebook_textarea_length)
                                    with gr.Row(elem_id='gr_row_ebook_mode') as gr_row_ebook_mode:
                                        gr_ebook_mode = gr.Dropdown(label='', elem_id='gr_ebook_mode', choices=[('File',ebook_modes['SINGLE']), ('Directory',ebook_modes['DIRECTORY']), ('Text',ebook_modes['TEXT'])], interactive=True, scale=2)
                                        gr_blocks_preview = gr.Checkbox(label='Chapters Preview', elem_id='gr_blocks_preview', value=False, interactive=True, scale=1)
                                with gr.Group(elem_id='gr_group_language', elem_classes=['gr-group']):
                                    gr_language_markdown = gr.Markdown(elem_id='gr_language_markdown', elem_classes=['gr-markdown'], value='Language')
                                    gr_language = gr.Dropdown(label='', elem_id='gr_language', choices=language_options, value=default_language_code, type='value', interactive=True)
                                gr_group_voice_file = gr.Group(elem_id='gr_group_voice_file', elem_classes=['gr-group'], visible=visible_gr_group_voice_file)
                                with gr_group_voice_file:
                                    gr_voice_markdown = gr.Markdown(elem_id='gr_voice_markdown', elem_classes=['gr-markdown'], value='Voices')
                                    gr_voice_file = gr.File(show_label=False, label='Upload Voice', elem_id='gr_voice_file', file_types=voice_formats, value=None, height=100)
                                    with gr.Row(elem_id='gr_row_voice_player') as gr_row_voice_player:
                                        gr_voice_player_hidden = gr.Audio(elem_id='gr_voice_player_hidden', type='filepath', interactive=False, waveform_options=gr.WaveformOptions(show_recording_waveform=False), show_download_button=False, container=False, visible='hidden', show_share_button=True, show_label=False, scale=0, min_width=60)
                                        gr_voice_play = gr.Button('▶', elem_id='gr_voice_play', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                        gr_voice_list = gr.Dropdown(label='Voices', elem_id='gr_voice_list', choices=voice_options, type='value', interactive=True, scale=2)
                                        gr_voice_selected_filename = gr.Markdown(value='', elem_id='gr_voice_selected_filename', elem_classes=['gr-markdown'], visible=False)
                                        gr_voice_del_btn = gr.Button('🗑', elem_id='gr_voice_del_btn', elem_classes=['small-btn-red'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                with gr.Group(elem_id='gr_group_device', elem_classes=['gr-group']):
                                    gr_device_markdown = gr.Markdown(elem_id='gr_device_markdown', elem_classes=['gr-markdown'], value='Processor')
                                    gr_device = gr.Dropdown(label='', elem_id='gr_device', choices=[(k, v['proc']) for k, v in devices.items()], type='value', value=default_device, interactive=True)
                            with gr.Column(elem_id='gr_col_2', elem_classes=['gr-col'], scale=3):
                                with gr.Group(elem_id='gr_group_tts_engine', elem_classes=['gr-group']):
                                    gr_tts_rating = gr.Markdown(elem_id='gr_tts_rating', elem_classes=['gr-markdown'], value='TTS Engine')
                                    gr_tts_engine_list = gr.Dropdown(label='', elem_id='gr_tts_engine_list', choices=tts_engine_options, type='value', interactive=True)
                                with gr.Group(elem_id='gr_group_models', elem_classes=['gr-group']):
                                    gr_models_markdown = gr.Markdown(elem_id='gr_models_markdown', elem_classes=['gr-markdown'], value='Models')
                                    gr_fine_tuned_list = gr.Dropdown(label='Fine Tuned Preset Models', elem_id='gr_fine_tuned_list', choices=fine_tuned_options, type='value', interactive=True)
                                    gr_group_custom_model = gr.Group(visible=False)
                                    with gr_group_custom_model:
                                        gr_custom_model_label = gr.Textbox(label='', elem_id='gr_custom_model_label', elem_classes=['gr-label'], interactive=False)
                                        gr_custom_model_file = gr.File(show_label=True, label=f"Upload ZIP File", elem_id='gr_custom_model_file', value=None, file_types=['.zip'], height=100)
                                        gr_row_custom_model_list = gr.Row(elem_id='gr_row_custom_model_list')
                                        with gr_row_custom_model_list:
                                            gr_custom_model_list = gr.Dropdown(label='', elem_id='gr_custom_model_list', choices=custom_model_options, type='value', interactive=True, scale=2)
                                            gr_custom_model_train_link = gr.Markdown(value='<a href="" target="_blank">Create My Own Model</a>', elem_id='gr_custom_model_train_link', elem_classes=['gr-markdown'], visible=True)
                                            gr_custom_model_del_btn = gr.Button('🗑', elem_id='gr_custom_model_del_btn', elem_classes=['small-btn-red'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                with gr.Group(elem_id='gr_group_output_format'):
                                    gr_output_markdown = gr.Markdown(elem_id='gr_output_markdown', elem_classes=['gr-markdown'], value='Output')
                                    with gr.Row(elem_id='gr_row_output_format'):
                                        gr_output_format_list = gr.Dropdown(label='Format', elem_id='gr_output_format_list', choices=output_formats, type='value', value=default_output_format, interactive=True, scale=1)
                                        gr_output_channel_list = gr.Dropdown(label='Channel', elem_id='gr_output_channel_list', choices=['mono', 'stereo'], type='value', value=default_output_channel, interactive=True, scale=1)
                                        with gr.Group(elem_id='gr_group_output_split'):
                                            gr_output_split = gr.Checkbox(label='Split File', elem_id='gr_output_split', value=default_output_split, interactive=True)
                                            gr_row_output_split_hours = gr.Row(elem_id='gr_row_output_split_hours', visible=False)
                                            with gr_row_output_split_hours:
                                                gr_output_split_hours_markdown = gr.Markdown(elem_id='gr_output_split_hours_markdown',elem_classes=['gr-markdown-output-split-hours'], value='Hours<br/>/ Part')
                                                gr_output_split_hours = gr.Dropdown(label='', elem_id='gr_output_split_hours', choices=options_output_split_hours, type='value', value=default_output_split_hours, interactive=True, scale=1)
                                with gr.Group(elem_id='gr_group_session', elem_classes=['gr-group']):
                                    gr_session_markdown = gr.Markdown(elem_id='gr_session_markdown', elem_classes=['gr-markdown'], value='Session')
                                    gr_session_switch_disable_state = gr.State(None)
                                    gr_session_switch_enable_state = gr.State(None)
                                    with gr.Row(elem_id='gr_row_session'):
                                        gr_session = gr.Textbox(label='', elem_id='gr_session', interactive=False)
                                        gr_session_switch_btn = gr.Button('🔒︎', elem_id='gr_session_switch_btn', elem_classes=['small-btn-lock'], variant='secondary', visible=True, interactive=True, scale=0, min_width=60)
                    with gr.Tab('XTTSv2 Settings', elem_id='gr_tab_xtts_params', elem_classes='gr-tab', visible=False) as gr_tab_xtts_params:
                        with gr.Group(elem_id='gr_group_xtts_params', elem_classes=['gr-group']):
                            gr_xtts_temperature = gr.Slider(
                                label='Temperature',
                                minimum=0.05,
                                maximum=5.0,
                                step=0.05,
                                value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['temperature']),
                                elem_id='gr_xtts_temperature',
                                info='Higher values lead to more creative, unpredictable outputs. Lower values make it more monotone.'
                            )
                            gr_xtts_length_penalty = gr.Slider(
                                label='Length Penalty',
                                minimum=0.3,
                                maximum=5.0,
                                step=0.1,
                                value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['length_penalty']),
                                elem_id='gr_xtts_length_penalty',
                                info='Adjusts how much longer sequences are preferred. Higher values encourage the model to produce longer and more natural speech.',
                                visible=False
                            )
                            gr_xtts_num_beams = gr.Slider(
                                label='Number Beams',
                                minimum=1,
                                maximum=10,
                                step=1,
                                value=int(default_engine_settings[TTS_ENGINES['XTTSv2']]['num_beams']),
                                elem_id='gr_xtts_num_beams',
                                info='Controls how many alternative sequences the model explores. Higher values improve speech coherence and pronunciation but increase inference time.',
                                visible=False
                            )
                            gr_xtts_repetition_penalty = gr.Slider(
                                label='Repetition Penalty',
                                minimum=1.0,
                                maximum=5.0,
                                step=0.1,
                                value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['repetition_penalty']),
                                elem_id='gr_xtts_repetition_penalty',
                                info='Penalizes repeated phrases. Higher values reduce repetition.'
                            )
                            gr_xtts_top_k = gr.Slider(
                                label='Top-k Sampling',
                                minimum=10,
                                maximum=100,
                                step=1,
                                value=int(default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k']),
                                elem_id='gr_xtts_top_k',
                                info='Lower values restrict outputs to more likely words and increase speed at which audio generates.'
                            )
                            gr_xtts_top_p = gr.Slider(
                                label='Top-p Sampling',
                                minimum=0.1,
                                maximum=1.0, 
                                step=0.01,
                                value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['top_p']),
                                elem_id='gr_xtts_top_p',
                                info='Controls cumulative probability for word selection. Lower values make the output more predictable and increase speed at which audio generates.'
                            )
                            gr_xtts_speed = gr.Slider(
                                label='Speed', 
                                minimum=0.5, 
                                maximum=3.0, 
                                step=0.1, 
                                value=float(default_engine_settings[TTS_ENGINES['XTTSv2']]['speed']),
                                elem_id='gr_xtts_speed',
                                info='Adjusts how fast the narrator will speak.'
                            )
                            gr_xtts_enable_text_splitting = gr.Checkbox(
                                label='Enable Text Splitting', 
                                value=default_engine_settings[TTS_ENGINES['XTTSv2']]['enable_text_splitting'],
                                elem_id='gr_xtts_enable_text_splitting',
                                info='Coqui-tts builtin text splitting. Can help against hallucinations bu can also be worse.',
                                visible=False
                            )      
                    with gr.Tab('Bark Settings', elem_id='gr_tab_bark_params', elem_classes='gr-tab', visible=False) as gr_tab_bark_params:
                        gr.Markdown(
                            elem_id='gr_markdown_tab_bark_params',
                            value='''
                            ### Customize BARK Parameters
                            Adjust the settings below to influence how the audio is generated, emotional and voice behavior random or more conservative
                            '''
                        )
                        with gr.Group(elem_id='gr_group_bark_params', elem_classes=['gr-group']):
                            gr_bark_text_temp = gr.Slider(
                                label='Text Temperature', 
                                minimum=0.0,
                                maximum=1.0,
                                step=0.01,
                                value=float(default_engine_settings[TTS_ENGINES['BARK']]['text_temp']),
                                elem_id='gr_bark_text_temp',
                                info='Higher values lead to more creative, unpredictable outputs. Lower values make it more conservative.'
                            )
                            gr_bark_waveform_temp = gr.Slider(
                                label='Waveform Temperature', 
                                minimum=0.0,
                                maximum=1.0,
                                step=0.01,
                                value=float(default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp']),
                                elem_id='gr_bark_waveform_temp',
                                info='Higher values lead to more creative, unpredictable outputs. Lower values make it more conservative.'
                            )
                
                with gr.Group(elem_id='gr_group_progress', elem_classes=['gr-group-sides-padded']):
                    gr_progress_markdown = gr.Markdown(elem_id='gr_progress_markdown', elem_classes=['gr-markdown'], value='Status')
                    gr_progress = gr.Textbox(elem_id='gr_progress', label='', interactive=False, visible=True)

                with gr.Group(elem_id='gr_group_audiobook_list', elem_classes=['gr-group-sides-padded'], visible=True) as gr_group_audiobook_list:
                    gr_audiobook_markdown = gr.Markdown(elem_id='gr_audiobook_markdown', elem_classes=['gr-markdown'], value='Audiobook')
                    gr_audiobook_vtt = gr.Textbox(elem_id='gr_audiobook_vtt', label='', interactive=False, visible='hidden')
                    gr_playback_time = gr.Number(elem_id="gr_playback_time", label='', interactive=False, visible='hidden', value=0.0)
                    gr_audiobook_sentence = gr.Textbox(elem_id='gr_audiobook_sentence', label='', value='…', interactive=False, lines=3, max_lines=3)
                    gr_audiobook_player = gr.Audio(elem_id='gr_audiobook_player', label='', type='filepath', autoplay=False, interactive=False, waveform_options=gr.WaveformOptions(show_recording_waveform=False), show_download_button=False, show_share_button=False, container=True, visible=True)
                    with gr.Row(elem_id='gr_row_audiobook_list', visible=True) as gr_row_audiobook_list:
                        gr_audiobook_download_btn = gr.Button(elem_id='gr_audiobook_download_btn', value='↧', elem_classes=['small-btn'], variant='secondary', interactive=True, scale=0, min_width=60)
                        gr_audiobook_list = gr.Dropdown(elem_id='gr_audiobook_list', label='', choices=audiobook_options, type='value', interactive=True, scale=2)
                        gr_audiobook_del_btn = gr.Button(elem_id='gr_audiobook_del_btn', value='🗑', elem_classes=['small-btn-red'], variant='secondary', interactive=True, scale=0, min_width=60)
                    gr_audiobook_files = gr.Files(label='', elem_id='gr_audiobook_files', visible=False)
                    gr_audiobook_files_state = gr.State(False)
                with gr.Group(elem_id='gr_group_convert_btn', elem_classes=['gr-group-convert-btn']) as gr_group_convert_btn:
                    gr_convert_btn = gr.Button(elem_id='gr_convert_btn', value='📚', elem_classes='gr-convert-btn', variant='primary', interactive=False)

            gr_blocks_page = gr.Number(value=0, visible=False, precision=0)
            gr_blocks_data = gr.State([])
            gr_blocks_expands = gr.State([False] * page_size)

            with gr.Group(visible=False, elem_id='gr_group_blocks', elem_classes='gr-group-main') as gr_group_blocks:
                gr_blocks_markdown = gr.Markdown(elem_id='gr_blocks_markdown', elem_classes=['gr-markdown'], value='')
                with gr.Row(elem_id='gr_blocks_nav') as gr_blocks_nav:
                    gr_blocks_back_btn = gr.Button('◀', elem_id='gr_blocks_back_btn', interactive=False, scale=1)
                    gr_blocks_header = gr.Markdown('', elem_id='gr_blocks_header')
                    gr_blocks_next_btn = gr.Button('▶', elem_id='gr_blocks_next_btn', interactive=False, scale=1)

                block_components = []
                with gr.Column(elem_id='gr_column_blocks', elem_classes=['gr-col']):
                    for i in range(page_size):
                        acc_class = 'accordion-block-even' if i % 2 == 0 else 'accordion-block-odd'
                        with gr.Accordion(
                            f'Block {i}',
                            elem_id=f'block_{i}',
                            elem_classes=[acc_class],
                            visible=False,
                            open=False
                        ) as acc:
                            with gr.Row(elem_id=f'block_options_row_{i}', elem_classes=[acc_class, 'no-wrap']) as block_options_row:
                                acc_keep = gr.Checkbox(
                                    label='',
                                    elem_id=f'block_keep_{i}',
                                    elem_classes=['accordion-block-keep'],
                                    value=True,
                                    interactive=True,
                                    scale=0,
                                    visible=True
                                )
                                acc_voice_list = gr.Dropdown(
                                    show_label=False,
                                    elem_id=f'block_voice_{i}',
                                    elem_classes=['accordion-block-voice-list'],
                                    choices=voice_options,
                                    type='value',
                                    interactive=True,
                                    scale=1
                                )
                                acc_reset_btn = gr.Button(
                                    '↺',
                                    elem_id=f'block_reset_{i}',
                                    elem_classes=['accordion-block-reset'],
                                    variant='secondary',
                                    interactive=True,
                                    scale=0,
                                    min_width=40
                                )
                            acc_text = gr.Textbox(
                                show_label=False,
                                elem_id=f'block_text_{i}',
                                lines=18,
                                max_lines=18,
                                container=False,
                                interactive=True
                            )
                            acc_reset_btn.click(
                                fn=lambda session, _i=i: click_reset_block(session, _i),
                                inputs=[gr_session],
                                outputs=[acc_text]
                            )
                        acc.expand(
                            fn=lambda expands, _i=i: [
                                expands[j] if j != _i else True
                                for j in range(page_size)
                            ],
                            inputs=[gr_blocks_expands],
                            outputs=[gr_blocks_expands]
                        )
                        acc.collapse(
                            fn=lambda expands, _i=i: [
                                expands[j] if j != _i else False
                                for j in range(page_size)
                            ],
                            inputs=[gr_blocks_expands],
                            outputs=[gr_blocks_expands]
                        )
                        block_components.append((acc, acc_keep, acc_voice_list, acc_text))

                with gr.Row(elem_id='gr_row_buttons', visible=True) as gr_row_buttons:
                    gr_blocks_cancel_btn = gr.Button('🡄', elem_classes=['gr-blocks-buttons'], variant='stop', scale=0, size='md')
                    gr_blocks_confirm_btn = gr.Button('🡆', elem_classes=['gr-blocks-buttons'], variant='primary', scale=0, size='md')

            blocks_components_flat = [comp for quad in block_components for comp in quad]
            blocks_keeps = [c[1] for c in block_components]
            blocks_voices = [c[2] for c in block_components]
            blocks_texts = [c[3] for c in block_components]

            gr_version_markdown = gr.Markdown(elem_id='gr_version_markdown', value=f'''
                <div style="right:0;margin:auto;padding:10px;text-align:center">
                    <a href="https://github.com/DrewThomasson/ebook2audiobook" style="text-decoration:none;font-size:14px" target="_blank">
                    <b>{title}</b>&nbsp;<b style="color:orange; text-shadow: 0.3px 0.3px 0.3px #303030">{prog_version}</b></a>
                </div>
                '''
            )

            gr_modal = gr.HTML(visible=False)
            gr_glassmask = gr.HTML(gr_glassmask_msg, elem_id='gr_glassmask', elem_classes=['gr-glass-mask'])
            gr_data_field_hidden = gr.Textbox(elem_id='gr_data_field_hidden', visible=False)
            
            gr_deletion_cancel_btn = gr.Button(elem_id='gr_deletion_cancel_btn', elem_classes=['hide-elem'], value='🡄', variant='stop', visible=True, scale=0, size='sm',  min_width=0)
            gr_deletion_confirm_btn = gr.Button(elem_id='gr_deletion_confirm_btn', elem_classes=['hide-elem'], value='🡆', variant='primary', visible=True, scale=0, size='sm', min_width=0)
            
            gr_override_cancel_btn = gr.Button(elem_id='gr_override_cancel_btn', elem_classes=['hide-elem'], value='🡄', variant='stop', visible=True, scale=0, size='sm',  min_width=0)
            gr_override_confirm_btn = gr.Button(elem_id='gr_override_confirm_btn', elem_classes=['hide-elem'], value='🡆', variant='primary', visible=True, scale=0, size='sm', min_width=0)
            
            gr_restore_session = gr.JSON(elem_id='gr_restore_session', visible='hidden')
            gr_session_update = gr.State({'hash': None})
            gr_save_session = gr.JSON(elem_id='gr_save_session', visible='hidden')
            
            gr_event = gr.Number(value=0, visible=False, precision=0)
            gr_blocks_event = gr.Number(value=0, visible=False, precision=0)
            gr_end_event = gr.Number(value=0, visible=False, precision=0)
            
            gr_backup_session = gr.State(value=None)
            gr_dummy_bool = gr.State(value=False)
            
            ############## End of Gradio Components creation

            def disable_components(session_id:str, exceptions:list|None=None)->tuple:
                if session_id is None:
                    outputs = tuple(gr.update() for _ in range(20))
                else:
                    if exceptions is None:
                        exceptions = []
                    if 'gr_session_switch_btn' in exceptions:
                        outputs = tuple(gr.update(interactive=False) for _ in range(19)) + (gr.update(interactive=True),)
                    else:
                        outputs = tuple(gr.update(interactive=False) for _ in range(20))
                return outputs

            def enable_components(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session['status'] in [status_tags['READY'], status_tags['END']]:
                            session['status'] = status_tags['READY']
                            session['cancellation_requested'] = False
                            outputs = list(gr.update(interactive=True) for _ in range(20))
                            visible_custom_model_del_btn = True if session['custom_model'] is not None else False
                            enabled_convert_btn = False
                            if session['ebook_mode'] == ebook_modes['DIRECTORY']:
                                if session.get('ebook_list'):
                                    enabled_convert_btn = True
                            elif session['ebook_mode'] == ebook_modes['SINGLE']:
                                if session.get('ebook_src'):
                                    enabled_convert_btn = True
                            elif session['ebook_mode'] == ebook_modes['TEXT']:
                                enabled_convert_btn = True
                            return tuple(outputs) + (gr.update(interactive=True, visible=visible_custom_model_del_btn), gr.update(value=''), gr.update(interactive=enabled_convert_btn))
                except Exception as e:
                    error = f'enable_components(): {e}'
                    exception_alert(session_id, error)
                outputs = tuple(gr.update() for _ in range(23))
                return outputs

            def disable_on_voice_upload()->tuple:
                outputs = tuple([gr.update(interactive=False) for _ in range(10)])
                return outputs + (gr.update(visible='hidden'), gr.update(visible='hidden'))

            def enable_on_voice_upload(session_id:str)->tuple:
                session = context.get_session(session_id)
                visible_buttons = 'hidden'
                enabled_convert_btn = False
                outputs = tuple([gr.update(interactive=True) for _ in range(9)])
                if session and session.get('id', False):
                    enabled_convert_btn = True if session['ebook'] is not None else enabled_convert_btn
                    visible_buttons = True if session['voice'] is not None else visible_buttons
                return outputs + (gr.update(interactive=enabled_convert_btn), gr.update(visible=visible_buttons), gr.update(visible=visible_buttons))

            def disable_on_custom_upload()->tuple:
                outputs = tuple([gr.update(interactive=False) for _ in range(11)])
                return outputs + (gr.update(visible=False), gr.update(visible='hidden'))

            def enable_on_custom_upload(custom_model:str|None, ebook_data:any, ebook_textarea:any)->tuple:
                outputs = tuple([gr.update(interactive=True) for _ in range(10)])
                enabled_convert_btn = True if ebook_data or ebook_textarea else False
                visible_custom_model_del_btn = True if custom_model is not None else False
                return outputs + (gr.update(interactive=enabled_convert_btn), gr.update(visible=True), gr.update(visible=visible_custom_model_del_btn))

            def show_gr_modal(type:str, msg:str)->str:
                return f'''
                <div id="custom-gr_modal" class="gr-modal">
                    <div class="gr-modal-content">
                        <p style="color:#ffffff">{msg}</p>            
                        {show_gr_modal_buttons(type)}
                    </div>
                </div>
                '''

            def show_gr_modal_buttons(type:str)->str:
                if type in [status_tags['DELETION'], status_tags['OVERRIDE']]:
                    cancel_btn = f'#gr_{type}_cancel_btn'
                    confirm_btn = f'#gr_{type}_confirm_btn'
                    return f'''
                    <div class="confirm-buttons">
                        <button class="button-red" style="width:50px; height:50px" onclick="document.querySelector('{cancel_btn}').click()">✖</button>
                        <button class="button-green" style="width:50px; height:50px" onclick="document.querySelector('{confirm_btn}').click()">✔</button>
                    </div>
                    '''
                else:
                    return '<div class="spinner"></div>'

            def yellow_stars(n:int):
                return "".join(
                    "<span style='color:#f0bc00; font-size:12px'>★</span>" for _ in range(n)
                )

            def color_box(value:int)->str:
                if value <= 4:
                    color = "#4CAF50"  # Green = low
                elif value <= 8:
                    color = "#FF9800"  # Orange = medium
                else:
                    color = "#F44336"  # Red = high
                return f"<span style='background:{color};color:white; padding: 0 3px 0 3px; border-radius:3px; font-size:11px; white-space: nowrap'>{str(value)} GB</span>"

            def show_rating(tts_engine:str)->str:
                rating = default_engine_settings[tts_engine]['rating']
                return f'''
                    <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                        <span class="gr-markdown-span">TTS Engine</span>
                        <table style="
                            display:inline-block;
                            border-collapse:collapse;
                            border:none;
                            margin:0;
                            padding:0;
                            font-size:12px;
                            line-height:1.2;   /* compact, but no clipping */
                        ">
                          <tr style="border:none; vertical-align:bottom;">
                            <td style="padding:0 5px 0 2.5px; border:none; vertical-align:bottom;">
                              <b>VRAM:</b> {color_box(int(rating['VRAM']))}
                            </td>
                            <td style="padding:0 5px 0 2.5px; border:none; vertical-align:bottom;">
                              <b>CPU:</b> {yellow_stars(int(rating['CPU']))}
                            </td>
                            <td style="padding:0 5px 0 2.5px; border:none; vertical-align:bottom;">
                              <b>RAM:</b> {color_box(int(rating['RAM']))}
                            </td>
                            <td style="padding:0 5px 0 2.5px; border:none; vertical-align:bottom;">
                              <b>Realism:</b> {yellow_stars(int(rating['Realism']))}
                            </td>
                          </tr>
                        </table>
                    </div>
                '''

            def is_valid_gradio_cache(path):
                if not path or not os.path.isfile(path):
                    return False
                path = os.path.normpath(path)
                parent = os.path.dirname(path)
                return (
                    parent.startswith(gradio_cache_dir) and
                    len(os.path.basename(parent)) >= 32
                )

            def restore_interface(session_id:str, req:gr.Request)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        socket_hash = str(req.session_hash)
                        if not session.get(socket_hash):
                            outputs = tuple([gr.update() for _ in range(22)])
                            return outputs
                        ebook_data = None
                        ebook_textarea = None
                        upload_mode = session['ebook_mode']
                        ebook_file_count = ebook_modes['SINGLE']
                        visible_ebook_src = False
                        visible_ebook_textarea = False
                        enabled_convert_btn = False
                        if session.get('ebook_mode') == ebook_modes['TEXT']:
                            ebook_textarea = session['ebook_textarea']
                            visible_ebook_textarea = True
                            enabled_convert_btn = True
                        elif session.get('ebook_mode') == ebook_modes['DIRECTORY']:
                            ebook_file_count = ebook_modes['DIRECTORY']
                            if session.get('ebook_list', None) is not None:
                                if len(session['ebook_list']) > 0:
                                    ebook_data = [f for f in session['ebook_list'] if is_valid_gradio_cache(f)]
                                if ebook_data:
                                    enabled_convert_btn = True
                                else:
                                    ebook_data = None
                                visible_ebook_src = True
                        elif session.get('ebook_mode') == ebook_modes['SINGLE']:
                            if is_valid_gradio_cache(session['ebook_src']):
                                ebook_data = session['ebook_src']
                            if ebook_data:
                                enabled_convert_btn = True
                            visible_ebook_src = True
                        visible_row_split_hours = True if session['output_split'] else False
                        visible_group_custom_model = visible_gr_group_custom_model if session['fine_tuned'] == 'internal' and session['tts_engine'] in tts_engines_with_custom_model else False
                        visible_voice_buttons = True if session.get('voice') is not None else False
                        visible_custom_model_del_btn = True if session['custom_model'] is not None else False
                        voice_file = session.get('voice')
                        return (
                            gr.update(visible=visible_ebook_src, value=ebook_data, file_count=ebook_file_count),
                            gr.update(visible=visible_ebook_textarea, value=ebook_textarea),
                            gr.update(value=session['ebook_mode']),
                            gr.update(value=bool(session['blocks_preview'])),
                            gr.update(value=session['device']),
                            gr.update(value=session['language']),
                            update_gr_voice_list(session_id),
                            update_gr_tts_engine_list(session_id),
                            update_gr_custom_model_list(session_id),
                            update_gr_fine_tuned_list(session_id),
                            gr.update(value=session['output_format']),
                            gr.update(value=session['output_channel']),
                            gr.update(value=bool(session['output_split'])),
                            gr.update(value=session['output_split_hours']),
                            gr.update(visible=visible_row_split_hours),
                            update_gr_audiobook_list(session_id),
                            gr.update(visible=visible_group_custom_model),
                            gr.update(interactive=enabled_convert_btn),
                            gr.update(value=voice_file),
                            gr.update(visible=visible_voice_buttons),
                            gr.update(visible=visible_voice_buttons),
                            gr.update(visible=visible_custom_model_del_btn)
                        )
                except Exception as e:
                    error = f'restore_interface(): {e}'
                    exception_alert(session_id, error)
                outputs = tuple([gr.update() for _ in range(22)])
                return outputs

            def restore_audiobook_player(session_id:str, audiobook:str|None)->tuple:
                try:
                    visible = True if audiobook is not None else False
                    return gr.update(visible=visible), gr.update(value=audiobook), gr.update(active=True)
                except Exception as e:
                    error = f'restore_audiobook_player(): {e}'
                    exception_alert(session_id, error)
                    outputs = tuple([gr.update() for _ in range(3)])
                    return outputs

            def refresh_interface(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session['cancellation_requested']:
                            session['status'] = status_tags['READY']
                        if session['status'] in [status_tags['READY'], status_tags['END']]:
                            visible_main = True
                            visible_xtts = False
                            visible_bark = False
                            visible_ebook_src = False
                            visible_ebook_textarea = False
                            enabled_convert_btn = False
                            ebook_data = None
                            ebook_textarea = None
                            if session['tts_engine'] == TTS_ENGINES['XTTSv2']:
                                visible_xtts = visible_gr_tab_xtts_params
                            elif session['tts_engine'] == TTS_ENGINES['BARK']:
                                visible_bark = visible_gr_tab_bark_params
                            if session['ebook_mode'] == ebook_modes['DIRECTORY']:
                                visible_ebook_src = True
                                ebook_data = session['ebook_list']
                            elif session['ebook_mode'] == ebook_modes['SINGLE']:
                                visible_ebook_src = True
                                ebook_data = session['ebook_src']
                            elif session['ebook_mode'] == ebook_modes['TEXT']:
                                visible_ebook_textarea = True
                                ebook_textarea = session['ebook_textarea']
                            enabled_convert_btn = True if session['ebook_mode'] == ebook_modes['TEXT'] or ebook_data is not None else False
                            return (
                                gr.update(value='', visible=False), gr.update(visible=visible_main),
                                gr.update(visible=visible_xtts), gr.update(visible=visible_bark),
                                gr.update(interactive=enabled_convert_btn), gr.update(visible=visible_ebook_src, value=ebook_data), gr.update(visible=visible_ebook_textarea, value=ebook_textarea),
                                gr.update(value=session['device']), gr.update(value=session['audiobook']), update_gr_audiobook_list(session_id),
                                update_gr_voice_list(session_id), gr.update(''), gr.update(value='')
                            )
                        elif session['status'] in [status_tags['CONVERTING']]:
                            return (
                                gr.update(), gr.update(), gr.update(),
                                gr.update(), gr.update(), gr.update(visible=True, value=session['ebook_list']), gr.update(),
                                gr.update(), gr.update(), gr.update(),
                                gr.update(), gr.update(), gr.update()
                            )
                except Exception as e:
                    error = f'refresh_interface(): {e}'
                    exception_alert(session_id, error)
                outputs = tuple([gr.update() for _ in range(13)])
                return outputs

            def change_gr_audiobook_list(session_id:str, selected:str|None)->dict:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get('audiobook') != selected:
                            session['audiobook'] = selected
                        visible = session['audiobook'] is not None
                        return gr.update(visible=visible)
                except Exception as e:
                    error = f'change_gr_audiobook_list(): {e}'
                    exception_alert(session_id, error)
                return gr.update(visible=False)

            def update_gr_audiobook_player(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session['audiobook'] is not None: 
                            vtt = Path(session['audiobook']).with_suffix('.vtt')
                            if not os.path.exists(session['audiobook']) or not os.path.exists(vtt):
                                error = f"{Path(session['audiobook']).name} does not exist!"
                                exception_alert(session_id, error)
                                return gr.update(value=0.0), gr.update(value=None), gr.update(value=None)
                            audio_info = mediainfo(session['audiobook'])
                            duration = audio_info.get('duration', False)
                            if duration:
                                session['duration'] = float(audio_info['duration'])
                                with open(vtt, "r", encoding="utf-8-sig", errors="replace") as f:
                                    vtt_content = f.read()
                                return gr.update(value=0.0), gr.update(value=session['audiobook']), gr.update(value=vtt_content)
                            else:
                                error = f"{Path(session['audiobook']).name} corrupted or not encoded!"
                                exception_alert(session_id, error)
                except Exception as e:
                    error = f'update_gr_audiobook_player(): {e}'
                    exception_alert(session_id, error)
                return gr.update(value=0.0), gr.update(value=None), gr.update(value=None)

            def update_gr_glassmask(str:str=gr_glassmask_msg, attr:list=['gr-glass-mask'])->dict:
                return gr.update(value=str, elem_id='gr_glassmask', elem_classes=attr)

            def build_voice_highlight_css(row_index:int|None)->str:
                """Emit a <style> block highlighting tr.file:nth-child(N+1) inside #gr_ebook_src, or '' to clear."""
                if row_index is None:
                    return ''
                return (
                    f'<style>#gr_ebook_src table.file-preview tbody > tr.file:nth-child({row_index + 1}) '
                    f'{{ background: var(--color-accent-soft) !important; '
                    f'box-shadow: inset 4px 0 0 var(--color-accent) !important; '
                    f'font-weight: 600; }}</style>'
                )

            def voice_player_visible(session)->bool:
                """gr_row_voice_player hides only in DIRECTORY mode with no row currently selected."""
                if not session:
                    return True
                if session.get('ebook_mode') != ebook_modes['DIRECTORY']:
                    return True
                return bool(session.get('ebook_selected'))

            def upload_gr_ebook_src(session_id:str, ebook_mode:str)->None:
                if ebook_mode == ebook_modes['DIRECTORY']:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        session['ebook_selected'] = None
                        session['voice_map'] = {}
                        msg = 'Click on each file in the list to set its voice individually.'
                        show_alert(session_id, {
                            'type': 'info',
                            'msg': msg
                        })

            def change_gr_ebook_src(session_id:str, ebook_mode:str, data:any)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if (session.get('ebook_src') == data and ebook_mode == ebook_modes['SINGLE']) or (session.get('ebook_list') == data and ebook_mode == ebook_modes['DIRECTORY']):
                            return gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
                        if ebook_mode == ebook_modes['SINGLE']:
                            session['ebook_src'] = data
                            # since ebook_textarea override ebook_src during the conversion
                            # so it needs to save the current real ebook_src to get it back after the textarea conversion.
                            session['ebook_src_notextarea'] = data
                        elif ebook_mode == ebook_modes['DIRECTORY']:
                            session['ebook_list'] = data
                            files = data or []
                            abs_files = [os.path.abspath(f) for f in files] if isinstance(files, list) else []
                            prev_map = dict(session.get('voice_map') or {})  # read once
                            default_voice = session.get('voice')
                            new_map = {p: (prev_map[p] if p in prev_map else default_voice) for p in abs_files}
                            session['voice_map'] = new_map
                            prev_selected = session.get('ebook_selected')
                            if prev_selected and prev_selected in abs_files:
                                new_row = abs_files.index(prev_selected)
                                if data is None:
                                    session['cancellation_requested'] = True
                                else:
                                    session['cancellation_requested'] = False
                                return (
                                    gr.update(),
                                    gr.update(value=build_voice_highlight_css(new_row)),
                                    gr.update(),
                                    gr.update(visible=True),
                                    gr.update(value=Path(prev_selected).name, visible=True),
                                )
                            else:
                                session['ebook_selected'] = None
                                voice_update = gr.update(value=session.get('voice')) if prev_selected else gr.update()
                                if data is None and session.get('status', None) in [status_tags['EDIT'], status_tags['CONVERTING']]:
                                    session['cancellation_requested'] = True
                                    msg = 'Cancellation requested, please wait…'
                                    return gr.update(value=show_gr_modal('wait', msg), visible=True), gr.update(value=''), voice_update, gr.update(visible=False), gr.update(value='', visible=False)
                                session['cancellation_requested'] = False
                                return gr.update(), gr.update(value=''), voice_update, gr.update(visible=False), gr.update(value='', visible=False)
                        if data is None:
                            if session.get('status', None) in [status_tags['EDIT'], status_tags['CONVERTING']]:
                                session['cancellation_requested'] = True
                                msg = 'Cancellation requested, please wait…'
                                return gr.update(value=show_gr_modal('wait', msg), visible=True), gr.update(value=''), gr.update(), gr.update(), gr.update()
                        session['cancellation_requested'] = False
                except Exception as e:
                    error = f'change_gr_ebook_src(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), gr.update(value=''), gr.update(), gr.update(), gr.update()

            def select_gr_ebook_src(session_id:str, ebook_mode:str, ebook_src:list|None, evt:gr.SelectData)->tuple:
                try:
                    session = context.get_session(session_id)
                    if not (session and session.get('id', False)):
                        return gr.update(), gr.update(), gr.update(), gr.update()
                    if ebook_mode != ebook_modes['DIRECTORY'] or evt.index is None:
                        return gr.update(), gr.update(value=''), gr.update(), gr.update(value='', visible=False)
                    if session.get('status') != status_tags['READY']:
                        return gr.update(), gr.update(), gr.update(), gr.update()
                    # evt.index can be int or (row, col) tuple — normalise.
                    row = evt.index[0] if isinstance(evt.index, (list, tuple)) else evt.index
                    live_list = ebook_src if isinstance(ebook_src, list) and ebook_src else None
                    ebook_list = live_list if live_list is not None else (session.get('ebook_list') or [])
                    if not isinstance(ebook_list, list) or row < 0 or row >= len(ebook_list):
                        return gr.update(), gr.update(value=''), gr.update(), gr.update(value='', visible=False)
                    abs_path = os.path.abspath(ebook_list[row])
                    session['ebook_selected'] = abs_path
                    if live_list is not None and session.get('ebook_list') != live_list:
                        session['ebook_list'] = live_list
                    voice_map = session.get('voice_map') or {}
                    assigned_voice = voice_map[abs_path] if abs_path in voice_map else session.get('voice')
                    style = build_voice_highlight_css(row)
                    filename = Path(abs_path).name
                    return (
                        gr.update(value=assigned_voice, label='Voices'),
                        gr.update(value=style),
                        gr.update(visible=True),
                        gr.update(value=filename, visible=True),
                    )
                except Exception as e:
                    error = f'select_gr_ebook_src(): {e}'
                    exception_alert(session_id, error)
                    return gr.update(), gr.update(), gr.update(), gr.update()

            def change_gr_ebook_textarea(session_id:str, ebook_textarea:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('ebook_textarea') != ebook_textarea:
                        session['ebook_textarea'] = ebook_textarea
                return

            def change_gr_ebook_mode(session_id:str, val:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get('ebook_mode') == val:
                            return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
                        session['ebook_mode'] = val
                        css_update = gr.update() if val == ebook_modes['DIRECTORY'] else gr.update(value='')
                        if val != ebook_modes['DIRECTORY']:
                            session['ebook_selected'] = None
                        row_visible = voice_player_visible(session)
                        if val == ebook_modes['DIRECTORY'] and session.get('ebook_selected'):
                            filename_update = gr.update(value=Path(session['ebook_selected']).name, visible=True)
                        else:
                            filename_update = gr.update(value='', visible=False)
                        enabled_convert_btn = False
                        if val == ebook_modes['SINGLE']:
                            if session.get('ebook_src'):
                                enabled_convert_btn = True
                            return gr.update(visible=True, label='-', file_count=ebook_modes['SINGLE'], value=session['ebook_src']), gr.update(visible=False), gr.update(interactive=enabled_convert_btn), css_update, gr.update(visible=row_visible), filename_update
                        elif val == ebook_modes['DIRECTORY']:
                            if session.get('ebook_list'):
                                enabled_convert_btn = True
                            return gr.update(visible=True, label='-', file_count=ebook_modes['DIRECTORY'], value=session['ebook_list']), gr.update(visible=False), gr.update(interactive=enabled_convert_btn), css_update, gr.update(visible=row_visible), filename_update
                        elif val == ebook_modes['TEXT']:
                            return gr.update(visible=False), gr.update(visible=True, value=session['ebook_textarea']), gr.update(interactive=True), css_update, gr.update(visible=row_visible), filename_update
                except Exception as e:
                    error = f'change_gr_ebook_mode(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

            def change_gr_voice_file(session_id:str, f:str|None)->tuple:
                try:
                    state = {}
                    if f is not None:
                        if len(voice_options) > max_custom_voices:
                            error = f'You are allowed to upload a max of {max_custom_voices} voices'
                            state['type'] = 'warning'
                            state['msg'] = error
                        elif os.path.splitext(f.name)[1] not in voice_formats:
                            error = f'The audio file format selected is not valid.'
                            state['type'] = 'warning'
                            state['msg'] = error
                        else:                  
                            session = context.get_session(session_id)
                            if session and session.get('id', False):
                                voice_name = os.path.splitext(os.path.basename(f))[0].replace('&', 'And')
                                voice_name = get_sanitized(voice_name)
                                final_voice_file = os.path.join(session['voice_dir'], f'{voice_name}.wav')
                                extractor = VoiceExtractor(session, f, voice_name)
                                status, msg = extractor.extract_voice()
                                if status:
                                    session['voice'] = final_voice_file
                                    msg = f'Voice {voice_name} added to the voices list'
                                    state['type'] = 'success'
                                    state['msg'] = msg
                                    show_alert(session_id, state)
                                    return update_gr_voice_list(session_id)
                                else:
                                    error = 'failed! Check if you audio file is compatible.'
                                    state['type'] = 'warning'
                                    state['msg'] = error
                        show_alert(session_id, state)
                except Exception as e:
                    error = f'change_gr_voice_file(): {e}'
                    exception_alert(session_id, error)
                return gr.update()

            def change_gr_voice_list(session_id:str, selected:str|None)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if not voice_options or selected is None:
                            new_voice = None
                        else:
                            voice_value = voice_options[0][1]
                            new_voice = next(
                                (value for label, value in voice_options if value == selected),
                                voice_value,
                            )
                        if session.get('ebook_mode') == ebook_modes['DIRECTORY'] and session.get('ebook_selected'):
                            voice_map = dict(session.get('voice_map') or {})
                            voice_map[session['ebook_selected']] = new_voice
                            session['voice_map'] = voice_map
                        else:
                            session['voice'] = new_voice
                        visible_voice_buttons = new_voice is not None
                        return gr.update(value=new_voice), gr.update(visible=visible_voice_buttons), gr.update(visible=visible_voice_buttons)
                except Exception as e:
                    error = f'change_gr_voice_list(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), gr.update(), gr.update()

            def click_gr_voice_del_btn(session_id:str, selected:str)->tuple:
                try:
                    if selected is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            speaker_path = os.path.abspath(selected)
                            speaker = re.sub(r'\.wav$|\.npz|\.pth$', '', os.path.basename(selected))
                            builtin_root = os.path.join(voices_dir, session['language'])
                            is_in_builtin = os.path.commonpath([speaker_path, os.path.abspath(builtin_root)]) == os.path.abspath(builtin_root)
                            is_in_models = os.path.commonpath([speaker_path, os.path.abspath(session['custom_model_dir'])]) == os.path.abspath(session['custom_model_dir'])
                            is_builtin = any(
                                speaker in settings.get('voices', {})
                                for settings in (default_engine_settings[engine] for engine in TTS_ENGINES.values())
                            )
                            if is_builtin and is_in_builtin:
                                error = f'Voice file {speaker} is a builtin voice and cannot be deleted.'
                                show_alert(session_id, {"type": "warning", "msg": error})
                                return gr.update(visible=False), gr.update()
                            if is_in_models:
                                error = f'Voice file {speaker} is a voice of one of your custom model and cannot be deleted.'
                                show_alert(session_id, {"type": "warning", "msg": error})
                                return gr.update(visible=False), gr.update()                          
                            try:
                                selected_path = Path(selected).resolve()
                                parent_path = Path(session['voice_dir']).parent.resolve()
                                if parent_path in selected_path.parents:
                                    session['status'] = status_tags['DELETION']
                                    msg = f'Are you sure to delete {speaker}?'
                                    return (
                                        gr.update(value=show_gr_modal(session['status'], msg), visible=True),
                                        gr.update(value='confirm_voice_del')
                                    )
                                else:
                                    error = f'{speaker} is part of the global voices directory. Only your own custom uploaded voices can be deleted!'
                                    show_alert(session_id, {"type": "warning", "msg": error})
                                    return gr.update(visible=False), gr.update()
                            except Exception as e:
                                error = f'Could not delete the voice file {selected}!\n{e}'
                                exception_alert(session_id, error)
                                return gr.update(visible=False), gr.update()
                    return gr.update(visible=False), gr.update()
                except Exception as e:
                    error = f'click_gr_voice_del_btn(): {e}'
                    exception_alert(session_id, error)
                    return gr.update(visible=False), gr.update()

            def click_gr_custom_model_del_btn(session_id:str, selected:str)->tuple:
                try:
                    if selected is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            selected_name = os.path.basename(selected)
                            session['status'] = status_tags['DELETION']
                            msg = f'Are you sure to delete {selected_name}?'
                            return gr.update(value=show_gr_modal(session['status'], msg), visible=True), gr.update(value='confirm_custom_model_del')
                except Exception as e:
                    error = f'Could not delete the custom model {selected_name}!'
                    exception_alert(session_id, error)
                return gr.update(visible=False), gr.update()

            def click_gr_audiobook_del_btn(session_id:str, selected:str)->tuple:
                try:
                    if selected is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            selected_name = Path(selected).stem
                            session['status'] = status_tags['DELETION']
                            msg = f'Are you sure to delete {selected_name}?'
                            return gr.update(value=show_gr_modal(session['status'], msg), visible=True), gr.update(value='confirm_audiobook_del')
                except Exception as e:
                    error = f'Could not delete the audiobook {selected_name}!'
                    exception_alert(session_id, error)
                return gr.update(visible=False), gr.update()

            def click_gr_deletion(session_id:str, voice_path:str, custom_model:str, audiobook:str, method:str|None=None)->tuple:
                try:
                    nonlocal models, voice_options
                    if method is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            if session['status'] == status_tags['DELETION']:
                                session['status'] = status_tags['READY']
                                models = load_engine_presets(session['tts_engine'])
                                if method == 'confirm_voice_del':
                                    selected_name = Path(voice_path).stem
                                    pattern = re.sub(r'\.wav$', '*.wav', voice_path)
                                    files2remove = glob(pattern)
                                    for file in files2remove:
                                        try:
                                            os.remove(file)
                                        except FileNotFoundError:
                                            pass
                                    shutil.rmtree(os.path.join(os.path.dirname(voice_path), 'bark', selected_name), ignore_errors=True)
                                    deleted_voice = session['voice']
                                    fallback = None if session['tts_engine'] in tts_engines_with_inner_speaker else default_engine_settings[session['tts_engine']]['voice']
                                    blocks_current = session.get('blocks_current') or {}
                                    changed = False
                                    for block in blocks_current.get('blocks', []):
                                        if block.get('voice') == deleted_voice:
                                            block['voice'] = fallback
                                            changed = True
                                    if blocks_current.get('voice') == deleted_voice:
                                        blocks_current['voice'] = fallback
                                        changed = True
                                    if changed:
                                        session['blocks_current'] = blocks_current
                                        save_db_blocks(session_id)
                                    session['voice'] = fallback
                                    voice_options[:] = [(i, v) for i, v in voice_options if v != deleted_voice]
                                    msg = f'Voice file {re.sub(r".wav$", "", selected_name)} deleted!'
                                    show_alert(session_id, {'type': 'info', 'msg': msg})
                                    return gr.update(value='', visible=False), gr.update(), gr.update(), update_gr_voice_list(session_id)
                                elif method == 'confirm_custom_model_del':
                                    selected_name = os.path.basename(custom_model)
                                    shutil.rmtree(custom_model, ignore_errors=True)                           
                                    msg = f'Custom model {selected_name} deleted!'
                                    if session['custom_model'] is not None and session['voice'] is not None:
                                        if session['custom_model'] in session['voice']:
                                            session['voice'] = models[session['fine_tuned']]['voice']
                                    session['custom_model'] = None
                                    show_alert(session_id, {"type": "info", "msg": msg})
                                    return gr.update(value='', visible=False), update_gr_custom_model_list(session_id), gr.update(),  gr.update()
                                elif method == 'confirm_audiobook_del':
                                    selected_name = Path(audiobook).stem
                                    base_selected_name = re.sub(r'_part\d+$', '', selected_name)
                                    count_files = sum(1 for f, _ in audiobook_options if re.sub(r'_part\d+$', '', Path(f).stem) == base_selected_name)
                                    if os.path.isdir(audiobook):
                                        shutil.rmtree(audiobook, ignore_errors=True)
                                    else:
                                        try:
                                            os.remove(audiobook)
                                        except FileNotFoundError:
                                            pass
                                    if count_files <= 1:
                                        vtt_path = Path(audiobook).with_suffix('.vtt')
                                        if os.path.exists(vtt_path):
                                            os.remove(vtt_path)
                                        process_dir = os.path.join(session['session_dir'], f"{hashlib.md5(os.path.join(session['audiobooks_dir'], base_selected_name).encode()).hexdigest()}")
                                        shutil.rmtree(process_dir, ignore_errors=True)
                                    msg = f'Audiobook {selected_name} deleted!'
                                    session['audiobook'] = None
                                    show_alert(session_id, {"type": "info", "msg": msg})
                                    return gr.update(value='', visible=False), gr.update(), update_gr_audiobook_list(session_id), gr.update()
                except Exception as e:
                    error = f'click_gr_deletion(): {e}!'
                    exception_alert(session_id, error)
                return  gr.update(value='', visible=False), gr.update(), gr.update(), gr.update()

            def update_gr_voice_list(session_id:str)->dict:
                try:
                    nonlocal models, voice_options
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        models = load_engine_presets(session['tts_engine'])
                        lang_dir = session['language'] if session['language'] != 'con' else 'con-'  # Bypass Windows CON reserved name
                        file_pattern = "*.wav"
                        eng_options = []
                        bark_options = []
                        builtin_dir = Path(os.path.join(voices_dir, lang_dir))
                        builtin_options = [
                            (base, str(f))
                            for f in builtin_dir.rglob(file_pattern)
                            for base in [os.path.splitext(f.name)[0]]
                        ]
                        builtin_names = {t[0]: None for t in builtin_options}
                        if session['language'] in default_engine_settings[TTS_ENGINES['XTTSv2']].get('languages', {}):
                            eng_dir = Path(os.path.join(voices_dir, "eng"))
                            eng_options = [
                                (base, str(f))
                                for f in eng_dir.rglob(file_pattern)
                                for base in [os.path.splitext(f.name)[0]]
                                if base not in builtin_names
                            ]
                        if session['tts_engine'] == TTS_ENGINES['BARK']:
                            lang_dict = Lang(session['language'])
                            if lang_dict:
                                lang_iso1 = lang_dict.pt1
                                lang = lang_iso1.lower()
                                speakers_path = Path(default_engine_settings[TTS_ENGINES['BARK']]['speakers_path'])
                                pattern_speaker = re.compile(r"^.*?_speaker_(\d+)$")
                                bark_options = [
                                    (pattern_speaker.sub(r"Speaker \1", f.stem), str(f.with_suffix(".wav")))
                                    for f in speakers_path.rglob(f"{lang}_speaker_*.npz")
                                ]
                        voice_options = builtin_options + eng_options + bark_options
                        session['voice_dir'] = os.path.join(voices_dir, '__sessions', f'voice-{session_id}', session['language'])
                        os.makedirs(session['voice_dir'], exist_ok=True)
                        if session['voice_dir'] is not None:
                            session_voice_dir = Path(session['voice_dir'])
                            voice_options += [
                                (os.path.splitext(f.name)[0], str(f))
                                for f in session_voice_dir.rglob(file_pattern)
                                if f.is_file()
                            ]
                        if session.get('custom_model_dir'):
                            voice_options.extend(
                                (f.stem, str(f))
                                for f in Path(session['custom_model_dir']).rglob('*.wav')
                                if f.is_file()
                            )
                        if session['tts_engine'] in tts_engines_with_inner_speaker:
                            voice_options = [('Default', None)] + sorted(voice_options, key=lambda x: x[0].lower())
                        else:
                            voice_options = sorted(voice_options, key=lambda x: x[0].lower())
                        if session['voice'] is not None and isinstance(session.get('voice'), str):
                            if session['voice_dir'] not in session['voice']:
                                if not any(v[1] == session['voice'] for v in voice_options):
                                    voice_path = Path(session['voice'])
                                    parts = list(voice_path.parts)
                                    if "voices" in parts:
                                        idx = parts.index("voices")
                                        if idx + 1 < len(parts):
                                            parts[idx + 1] = session['language']
                                            new_voice_path = str(Path(*parts))
                                            if os.path.exists(new_voice_path) and any(v[1] == new_voice_path for v in voice_options):
                                                session['voice'] = new_voice_path
                                            else:
                                                parts[idx + 1] = 'eng'
                                                new_voice_path = str(Path(*parts))
                                                if os.path.exists(new_voice_path) and any(v[1] == new_voice_path for v in voice_options):
                                                    session['voice'] = new_voice_path
                                                else:
                                                    session['voice'] = voice_options[0][1]
                        else:
                            if voice_options and voice_options[0][1] is not None:
                                new_voice_path = models[session['fine_tuned']]['voice']
                                if os.path.exists(new_voice_path) and any(v[1] == new_voice_path for v in voice_options):
                                    session['voice'] = new_voice_path
                                else:
                                    session['voice'] = voice_options[0][1]
                        return gr.update(choices=voice_options, value=session['voice'])
                except Exception as e:
                    error = f'update_gr_voice_list(): {e}!'
                    exception_alert(session_id, error)
                return gr.update()

            def update_gr_tts_engine_list(session_id:str)->dict:
                try:
                    nonlocal tts_engine_options
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        tts_engine_options = get_compatible_tts_engines(session['language'])
                        session['tts_engine'] = session['tts_engine'] if session['tts_engine'] in tts_engine_options else tts_engine_options[0]
                        return gr.update(choices=tts_engine_options, value=session['tts_engine'])
                except Exception as e:
                    error = f'update_gr_tts_engine_list(): {e}!'
                    exception_alert(session_id, error)              
                return gr.update()

            def update_gr_custom_model_list(session_id:str)->dict:
                try:
                    nonlocal custom_model_options
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        custom_model_tts_dir = check_custom_model_tts(session['custom_model_dir'], session['tts_engine'])
                        custom_model_options = [('None', None)] + [
                            (
                                str(dir),
                                os.path.join(custom_model_tts_dir, dir)
                            )
                            for dir in os.listdir(custom_model_tts_dir)
                            if os.path.isdir(os.path.join(custom_model_tts_dir, dir))
                        ]
                        session['custom_model'] = session['custom_model'] if session['custom_model'] in [option[1] for option in custom_model_options] else custom_model_options[0][1]
                        model_paths = {v[1] for v in custom_model_options}
                        return gr.update(choices=custom_model_options, value=session['custom_model'])
                except Exception as e:
                    error = f'update_gr_custom_model_list(): {e}!'
                    exception_alert(session_id, error)
                return gr.update()

            def update_gr_fine_tuned_list(session_id:str)->dict:
                try:
                    nonlocal fine_tuned_options
                    nonlocal models
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        models = load_engine_presets(session['tts_engine'])
                        fine_tuned_options = [
                            name
                            for name, details in models.items()
                            if details.get("lang") in ("multi", session['language'])
                        ]
                        if session['fine_tuned'] in fine_tuned_options:
                            fine_tuned = session['fine_tuned']
                        else:
                            fine_tuned = default_fine_tuned
                        session['fine_tuned'] = fine_tuned
                        return gr.update(choices=fine_tuned_options, value=session['fine_tuned'])
                except Exception as e:
                    error = f'update_gr_fine_tuned_list(): {e}!'
                    exception_alert(session_id, error)              
                return gr.update()

            def change_gr_device(session_id:str, selected:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('device') != selected:
                        session['device'] = selected
                return

            def change_gr_language(session_id:str, selected:str)->tuple:
                if selected:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get('language') != selected:
                            prev = session['language']      
                            session['language'] = selected
                            return (
                                gr.update(value=session['language']),
                                update_gr_tts_engine_list(session_id),
                                update_gr_custom_model_list(session_id),
                                update_gr_fine_tuned_list(session_id)
                            )
                return gr.update(), gr.update(), gr.update(), gr.update()

            def check_custom_model_tts(custom_model_dir:str, tts_engine:str)->str|None:
                dir_path = None
                if custom_model_dir is not None and tts_engine is not None:
                    dir_path = os.path.join(custom_model_dir, tts_engine)
                    if not os.path.isdir(dir_path):
                        os.makedirs(dir_path, exist_ok=True)
                return dir_path

            def change_gr_custom_model_file(session_id:str, custom_file:str|None, tts_engine:str)->tuple:
                try:
                    nonlocal models
                    if custom_file is not None:
                        state = {}
                        if len(custom_model_options) > max_custom_model:
                            error = f'You are allowed to upload a max of {max_custom_model} models'
                            state['type'] = 'warning'
                            state['msg'] = error
                        else:
                            session = context.get_session(session_id)
                            if session and session.get('id', False):
                                models = load_engine_presets(session['tts_engine'])
                                session['tts_engine'] = tts_engine
                                if analyze_uploaded_file(custom_file, models['internal']['files']):
                                    session['custom_model'] = custom_file
                                    model = extract_custom_model(session_id)
                                    if model is not None:
                                        session['custom_model'] = model
                                        if session['tts_engine'] not in tts_engines_with_inner_speaker:
                                            session['voice'] = os.path.join(model, f'{os.path.basename(os.path.normpath(model))}.wav')
                                        msg = f'{os.path.basename(model)} added to the custom models list'
                                        state['type'] = 'success'
                                        state['msg'] = msg
                                        show_alert(session_id, state)
                                        return gr.update(value=None), update_gr_custom_model_list(session_id)
                                    else:
                                        error = f'Cannot extract custom model zip file {os.path.basename(custom_file)}'
                                        state['type'] = 'warning'
                                        state['msg'] = error
                                else:
                                    error = f'{os.path.basename(custom_file)} is not a valid model or some required files are missing'
                                    state['type'] = 'warning'
                                    state['msg'] = error
                        show_alert(session_id, state)
                except Exception as e:
                    error = f'change_gr_custom_model_file(): {e}'
                    exception_alert(session_id, error)
                return gr.update(value=None), gr.update()

            def change_gr_custom_model_list(session_id:str, selected:str|None)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        session['custom_model'] = selected
                        if selected is not None and session['tts_engine'] not in tts_engines_with_inner_speaker:
                            session['voice'] = os.path.join(selected, f'{os.path.basename(selected)}.wav')
                        visible_fine_tuned = True if session['custom_model'] is None else False
                        visible_del_btn = True if session['custom_model'] is not None else False
                        return gr.update(visible=visible_fine_tuned), update_gr_voice_list(session_id), gr.update(visible=visible_del_btn)
                except Exception as e:
                    error = f'change_gr_custom_model_list(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), gr.update(), gr.update()

            def change_gr_tts_engine_list(session_id:str, engine:str)->tuple:
                try:
                    nonlocal models
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get('tts_engine') != engine:
                            models = load_engine_presets(engine)
                            session['voice'] = None if session['voice'] == default_engine_settings[session['tts_engine']]['voice'] else session['voice']
                            session['tts_engine'] = engine
                            session['fine_tuned'] = default_fine_tuned
                            visible_xtts = visible_gr_tab_xtts_params if session['tts_engine'] == TTS_ENGINES['XTTSv2'] else False
                            visible_bark = visible_gr_tab_bark_params if session['tts_engine'] == TTS_ENGINES['BARK'] else False
                            supports_custom = session['tts_engine'] in tts_engines_with_custom_model
                            visible_custom_model = supports_custom and session['fine_tuned'] == 'internal'
                            if supports_custom:
                                file_label = f"Upload {session['tts_engine']} ZIP file (Mandatory: {', '.join(models[default_fine_tuned]['files'])})"
                                custom_model_list_update = update_gr_custom_model_list(session_id)
                                custom_model_label_value = f"My {session['tts_engine']} Custom Models"
                            else:
                                file_label = f"*Upload Custom Model not available for {session['tts_engine']}"
                                custom_model_list_update = gr.update()
                                custom_model_label_value = ''
                            return (
                                gr.update(value=show_rating(session['tts_engine'])),
                                gr.update(visible=visible_xtts),
                                gr.update(visible=visible_bark),
                                gr.update(visible=visible_custom_model),
                                update_gr_fine_tuned_list(session_id),
                                gr.update(label=file_label),
                                custom_model_list_update,
                                gr.update(value=custom_model_label_value)
                            )
                except Exception as e:
                    error = f'change_gr_tts_engine_list(): {e}'
                    exception_alert(session_id, error)
                return tuple(gr.update() for _ in range(8))

            def change_gr_fine_tuned_list(session_id:str, selected:str)->dict:
                try:
                    if selected:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            if session.get('fine_tuned') != selected:
                                session['fine_tuned'] = selected
                                if selected == 'internal':
                                    visible_custom_model = visible_gr_group_custom_model if session['fine_tuned'] == 'internal' and session['tts_engine'] in tts_engines_with_custom_model else False
                                else:
                                    visible_custom_model = False
                                    session['voice'] = models[session['fine_tuned']]['voice']
                                return gr.update(visible=visible_custom_model)
                except Exception as e:
                    error = f'change_gr_fine_tuned_list(): {e}'
                    exception_alert(session_id, error)
                return gr.update()

            def change_gr_output_format_list(session_id:str, val:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('output_format') != val:
                        session['output_format'] = val
                return

            def change_gr_output_channel_list(session_id:str, val:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('output_channel') != val:
                        session['output_channel'] = val
                return
    
            def change_gr_output_split(session_id:str, val:str)->dict:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['output_split'] = val
                return gr.update(visible=val)

            def click_gr_session_switch_btn(session_id:str, backup_session_id:str|None)->tuple:
                try:
                    if backup_session_id is not None:
                        back_id = backup_session_id
                        new_id = session_id
                    else:
                        back_id = session_id
                        new_id = None
                    session = context.get_session(back_id)
                    if session and session.get('id', False):
                        if session['status'] == status_tags['READY']:
                            session['status'] = status_tags['SWITCH']
                            msg = 'Backup your current session ID before to start with a new one!'
                            show_alert(back_id, {"type": "warning", "msg": msg})
                            return gr.update(), gr.update(interactive=True), back_id, gr.update(value='🔑︎'), back_id, None
                        elif session['status'] == status_tags['SWITCH']:
                            if new_id is None or not new_id.strip():
                                msg = 'Session ID cannot be empty'
                                show_alert(back_id, {"type": "warning", "msg": msg})
                                return gr.update(), gr.update(), backup_session_id, gr.update(), None, None
                            new_session_id = new_id.strip()
                            session['status'] = status_tags['READY']
                            if new_session_id == back_id:
                                return gr.update(), gr.update(interactive=False), back_id, gr.update(value='🔒︎'), None, back_id
                            new_session_dir = os.path.join(tmp_dir, f'proc-{new_session_id}')
                            new_session = context.get_session(new_session_id)
                            if os.path.exists(new_session_dir) or new_session:
                                if not new_session:
                                    new_session = context.set_session(new_session_id)
                                new_session['status'] = status_tags['READY']
                                return gr.update(value=json.dumps(new_session, cls=JSONDictProxyEncoder)), gr.update(interactive=False), None, gr.update(value='🔒︎'), None, new_session_id
                            else:
                                session['status'] = status_tags['SWITCH']
                                msg = 'Session not found!'
                                show_alert(back_id, {"type": "warning", "msg": msg})
                except Exception as e:
                    error = f'click_gr_session_switch_btn(): {e}'
                    exception_alert(back_id, error)
                return gr.update(), gr.update(), backup_session_id, gr.update(), None, None

            def change_gr_playback_time(session_id:str, time:float)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('playback_time') != time:
                        session['playback_time'] = time
                return

            def toggle_audiobook_files(session_id:str, audiobook:str, is_visible:bool, refresh_only:bool=False)->tuple:
                try:
                    if not audiobook:
                        error = 'No audiobook selected.'
                        show_alert(session_id, {"type": "error", "msg": error})
                        return gr.update(), False
                    if is_visible and not refresh_only:
                        return gr.update(visible=False, value=None), False
                    file = Path(audiobook)
                    if not file.exists():
                        error = f'Audio not found: {file}'
                        show_alert(session_id, {"type": "error", "msg": error})
                        return gr.update(visible=False, value=None), False
                    files = [str(file)]
                    vtt = file.with_suffix('.vtt')
                    if vtt.exists():
                        files.append(str(vtt))
                    return gr.update(visible=True, value=files), True
                except Exception as e:
                    error = f'toggle_audiobook_files(): {e}!'
                    exception_alert(session_id, error)
                return gr.update(), False

            def change_param(key:str, session_id:str, val:Any, val2:Any=None)->None:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get(key) != val:
                            session[key] = val
                            state = {}
                            if key == 'xtts_length_penalty':
                                if val2 is not None:
                                    if float(val) > float(val2):
                                        error = 'Length penalty must be always lower than num beams if greater than 1.0 or equal if 1.0'   
                                        state['type'] = 'warning'
                                        state['msg'] = error
                                        show_alert(session_id, state)
                            elif key == 'xtts_num_beams':
                                if val2 is not None:
                                    if float(val) < float(val2):
                                        error = 'Num beams must be always higher than length penalty or equal if its value is 1.0'   
                                        state['type'] = 'warning'
                                        state['msg'] = error
                                        show_alert(session_id, state)
                except Exception as e:
                    error = f'change_param(): {e}'
                    exception_alert(session_id, error)
                return

            def start_conversion(
                    session_id:str, device:str, ebook_mode:str, ebook_src:str|list|None, ebook_textarea:str|None, blocks_preview:bool, tts_engine:str, language:str, voice:str, custom_model:str, fine_tuned:str, output_format:str, output_channel:str, xtts_temperature:float, 
                    xtts_length_penalty:int, xtts_num_beams:int, xtts_repetition_penalty:float, xtts_top_k:int, xtts_top_p:float, xtts_speed:float, xtts_enable_text_splitting:bool, bark_text_temp:float, bark_waveform_temp:float,
                    output_split:bool, output_split_hours:str
                )->tuple:
                error = None
                try:
                    session = context.get_session(session_id)
                    reset_ebook_session(session_id, force=True, filter_keys=False)
                    if session and session.get('id', False):
                        args = {
                            "id": session_id,
                            "is_gui_process": session['is_gui_process'],
                            "script_mode": script_mode,
                            "blocks_preview": blocks_preview,
                            "device": device,
                            "tts_engine": tts_engine,
                            "ebook": None,
                            "ebook_mode": ebook_mode,
                            "ebook_src": ebook_src if ebook_mode == ebook_modes['SINGLE'] else session['ebook_src'],
                            "ebook_list": ebook_src if ebook_mode == ebook_modes['DIRECTORY'] else session['ebook_list'],
                            "ebook_textarea": ebook_textarea if ebook_mode == ebook_modes['TEXT'] else session['ebook_textarea'],
                            "voice": voice,
                            "language": language,
                            "custom_model": custom_model,
                            "fine_tuned": fine_tuned,
                            "output_format": output_format,
                            "output_channel": output_channel,
                            "xtts_temperature": float(xtts_temperature),
                            "xtts_length_penalty": float(xtts_length_penalty),
                            "xtts_num_beams":int(session['xtts_num_beams']),
                            "xtts_repetition_penalty": float(xtts_repetition_penalty),
                            "xtts_top_k":int(xtts_top_k),
                            "xtts_top_p": float(xtts_top_p),
                            "xtts_speed": float(xtts_speed),
                            "xtts_enable_text_splitting":bool(xtts_enable_text_splitting),
                            "bark_text_temp": float(bark_text_temp),
                            "bark_waveform_temp": float(bark_waveform_temp),
                            "output_split":bool(output_split),
                            "output_split_hours": output_split_hours
                        }
                        if args['ebook_mode'] == ebook_modes['DIRECTORY']:
                            if isinstance(args['ebook_list'], list):
                                if not args['ebook_list']:
                                    error = 'A directory with ebook files is required.'
                        elif args['ebook_mode'] == ebook_modes['SINGLE']:
                            if not args['ebook_src']:
                                error = 'An ebook file is required.'
                        elif args['ebook_mode'] == ebook_modes['TEXT']:
                            if not args['ebook_textarea']:
                                error = 'Textarea is empty.'
                            elif len(args['ebook_textarea']) < 10:
                                error = 'Textarea must be > 10 chars.'
                            else:
                                args['ebook_textarea'] = args['ebook_textarea'].strip()
                                if len(args['ebook_textarea']) < 10:
                                    error = 'Textarea must be > 10 chars.'                     
                        #elif args['xtts_num_beams'] < args['xtts_length_penalty']:
                        #    error = 'num beams must be greater or equal than length penalty.'               
                        if error is None:
                            session['ticker'] = len(audiobook_options)
                            if args['ebook_mode'] == ebook_modes['DIRECTORY']:
                                if args['ebook_list']:
                                    if isinstance(args['ebook_list'], list):
                                        default_voice = session.get('voice')
                                        voice_map = dict(session.get('voice_map') or {})
                                        clean_list = sorted([
                                            f for f in args['ebook_list']
                                            if any(f.endswith(ext) for ext in ebook_formats)
                                        ])
                                        for skipped in [f for f in args['ebook_list'] if f not in clean_list]:
                                            show_alert(session_id, {
                                                "type": "warning",
                                                "msg": f'{Path(skipped).name} has not a supported format! skipping'
                                            })
                                        ebook_list_full = copy.deepcopy(clean_list)
                                        args['ebook_list'] = ebook_list_full
                                        queue = list(ebook_list_full)
                                        while queue:
                                            file = queue.pop(0)
                                            args['ebook_src'] = file
                                            abs_file = os.path.abspath(file)
                                            if abs_file in voice_map:
                                                override = voice_map[abs_file]
                                            elif os.path.basename(file) in voice_map:
                                                override = voice_map[os.path.basename(file)]
                                            else:
                                                override = default_voice
                                            if override is not None and not os.path.exists(override):
                                                msg = f'Voice override for {Path(file).name} not found, using default.'
                                                show_alert(session_id, {
                                                    "type": "warning",
                                                    "msg": msg
                                                })
                                                override = default_voice
                                            args['voice'] = override
                                            progress_status, passed = convert_ebook(args)
                                            if passed:
                                                return gr.update(value=progress_status)
                                            else:
                                                error = progress_status
                                                break
                            elif args['ebook_mode'] == ebook_modes['SINGLE']:
                                progress_status, passed = convert_ebook(args)
                                if passed:
                                    return gr.update(value=progress_status)
                                else:
                                    error = progress_status
                            elif args['ebook_mode'] == ebook_modes['TEXT']:
                                progress_status, passed = convert_ebook(args)
                                if passed:
                                    return gr.update(value=progress_status)
                                else:
                                    error = progress_status
                        if error is not None:
                            if session['ebook_mode'] == ebook_modes['TEXT']:
                                session['ebook_src'] = session['ebook_src_notextarea']
                            show_alert(session_id, {"type": "warning", "msg": error})
                            if session['cancellation_requested'] and session['status'] == status_tags['DISCONNECTED']:
                                context_tracker.end_session(session_id, session['socket_hash'])
                                return gr.update()
                            session['status'] = status_tags['END']
                        return gr.update(value=error)
                except Exception as e:
                    session['status'] = status_tags['END']
                    error = f'start_conversion(): {e}'
                    exception_alert(session_id, error)
                    return gr.update(value=error)

            def update_gr_audiobook_list(session_id:str)->dict:
                try:
                    nonlocal audiobook_options
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session['audiobooks_dir'] is not None:
                            audiobook_options = [
                                (f, os.path.join(session['audiobooks_dir'], str(f)))
                                for f in os.listdir(session['audiobooks_dir'])
                                if not f.lower().endswith(".vtt")
                            ]
                        if len(audiobook_options) > 0:
                            audiobook_options.sort(
                                key=lambda x: os.path.getmtime(x[1]),
                                reverse=True
                            )
                            session['audiobook'] = (
                                session['audiobook']
                                if session['audiobook'] in [option[1] for option in audiobook_options]
                                else None
                            )
                            if session['audiobook'] is None:
                                session['audiobook'] = audiobook_options[0][1]
                        else:
                            session['audiobook'] = None
                        return gr.update(choices=audiobook_options, value=session['audiobook'])
                except Exception as e:
                    error = f'update_gr_audiobook_list(): {e}!'
                    exception_alert(session_id, error)              
                return gr.update()

            def check_override_ebook(session_id:str, ebook_mode:str, ebook_data:any, ebook_textarea:str, blocks_preview:bool, event:int)->tuple:
                try:
                    session = context.get_session(session_id)
                    source = None
                    error = None
                    if session and session.get('id', False):
                        if not session['cancellation_requested']:
                            if not session['status'] in [status_tags['SKIP'], status_tags['END']]:
                                if session['status'] in [status_tags['EDIT']]:
                                    return gr.update(), event
                                elif session['status'] in [status_tags['OVERRIDE'], status_tags['CONVERTING']]:
                                    if ebook_mode == ebook_modes['DIRECTORY']:
                                        if isinstance(session['ebook_list'], list):
                                            if len(session['ebook_list']) > 0:
                                                source = session['ebook_list'][0]
                                    elif ebook_mode == ebook_modes['SINGLE']:
                                        source = session['ebook_src']
                                else:
                                    if ebook_mode == ebook_modes['DIRECTORY']:
                                        if not ebook_data:
                                            error = 'A directory with ebook files is required.'
                                        else:
                                            source = ebook_data[0]
                                    elif ebook_mode == ebook_modes['SINGLE']:
                                        if not ebook_data:
                                            error = 'An ebook file is required.'
                                        else:
                                            source = ebook_data
                                    elif ebook_mode == ebook_modes['TEXT']:
                                        if not ebook_textarea:
                                            error = 'Textarea is empty.'
                                        elif len(ebook_textarea) < 10:
                                            error = 'Textarea must be > 10 chars.'
                                        else:
                                            ebook_textarea = ebook_textarea.strip()
                                            if len(ebook_textarea) < 10:
                                                error = 'Textarea must be > 10 chars.'
                                            else:
                                                source = ebook_textarea
                                if error is None:
                                    if source is not None:
                                        if ebook_mode == ebook_modes['TEXT']:
                                            session['status'] = status_tags['SKIP']
                                            return gr.update(), (event + 1)
                                        else:
                                            session['ebook_src'] = source
                                            final_name = f"{get_sanitized(Path(source).stem)}.{session['output_format']}"
                                            process_dir = os.path.join(session['session_dir'], f"{hashlib.md5(os.path.join(session['audiobooks_dir'], Path(final_name).stem).encode()).hexdigest()}")
                                            chapters_dir = os.path.join(process_dir, 'chapters')
                                            sentences_dir = os.path.join(chapters_dir, 'sentences')
                                            pre_name = f"{get_sanitized(Path(source).stem)}{'_part1.' if session['output_split'] else '.'}{default_audio_proc_format}"
                                            pre_file = os.path.join(process_dir, pre_name)
                                            final_file = os.path.join(session['audiobooks_dir'], final_name)
                                            audio_sentences_exist = False
                                            if os.path.exists(sentences_dir):
                                                audio_sentences_exist = any(Path(sentences_dir).rglob(f'*.{default_audio_proc_format}'))
                                            if os.path.exists(pre_file) or audio_sentences_exist:
                                                session['status'] = status_tags['OVERRIDE']
                                                session['audiobook_overridden'] = final_file
                                                msg = f"Warning! audio sentences or final file {final_name} of this conversion already exists. If you continue resume will restart from the last sentence converted!"
                                                return gr.update(value=show_gr_modal(session['status'], msg), visible=True), event
                                            else:
                                                session['status'] = status_tags['SKIP']
                                                return gr.update(), (event + 1)
                                else:
                                    show_alert(session_id, {"type": "warning", "msg": error})
                                session['status'] = status_tags['END']
                except Exception as e:
                    error = f'check_override_ebook(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), event

            def click_gr_override_cancel_btn(session_id:str)->dict:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['status'] = status_tags['END']
                    session['audiobook_overridden'] = None
                return gr.update(value='', visible=False)

            def click_gr_override_confirm_btn(session_id:str, event:int, audiobook_files_state:bool)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        file_converting = session['audiobook_overridden']
                        files_update = gr.update()
                        files_state_update = gr.update()
                        if file_converting:
                            idx = next((i for i, t in enumerate(audiobook_options) if t[1] == file_converting), -1)
                            new_list = [t for t in audiobook_options if t[1] != file_converting]
                            if session['audiobook'] == file_converting or not new_list:
                                print('click_gr_override_confirm_btn():  select audiobook is the converting file')
                                new_selected = None
                                if new_list:
                                    new_idx = max(0, idx - 1)
                                    new_selected = new_list[new_idx][1]
                                session['audiobook'] = new_selected
                                if audiobook_files_state and new_selected is not None:
                                    files_update, files_state_update = toggle_audiobook_files(session_id, new_selected, False)
                                else:
                                    files_update = gr.update(visible=False, value=None)
                                    files_state_update = False
                                return gr.update(value='', visible=False), (event + 1), gr.update(choices=new_list, value=new_selected), files_update, files_state_update
                        return gr.update(value='', visible=False), (event + 1), gr.update(), files_update, files_state_update
                except Exception as e:
                    error = f'click_gr_override_confirm_btn(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), event, gr.update(), gr.update(), gr.update()

            def populate_page(session_id:str, page:int, blocks:list[dict])->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session['status'] in [status_tags['EDIT']]:
                        start = int(page) * page_size
                        updates = []
                        expands = []
                        for i in range(page_size):
                            idx = start + i
                            if idx < len(blocks):
                                b = blocks[idx]
                                exp = b.get('expand', False)
                                expands.append(exp)
                                updates.append(gr.update(label=f'Block {idx}', visible=True, open=exp))
                                updates.append(gr.update(value=b['keep']))
                                updates.append(gr.update(value=b.get('voice'), choices=voice_options))
                                updates.append(gr.update(value=b['text']))
                            else:
                                expands.append(False)
                                updates.append(gr.update(visible=False))
                                updates.append(gr.update())
                                updates.append(gr.update())
                                updates.append(gr.update())
                        end = min(start + page_size, len(blocks))
                        header = gr.update(value=f'Blocks {start}–{end-1} of {len(blocks)-1}')
                        return (*updates, header, expands)

            def navigate(session_id:str, page:int, blocks:list[dict], direction:int, *args)->tuple:
                new_blocks = collect_page(page, blocks, *args)
                max_page = max((len(new_blocks) - 1) // page_size, 0)
                new_page = max(0, min(int(page) + direction, max_page))
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        blocks_current = session['blocks_current']
                        if blocks_current.get('page') != new_page:
                            blocks_current['page'] = new_page
                            session['blocks_current'] = blocks_current
                            save_db_stamp(session_id)
                except Exception as e:
                    error = f'navigate(): {e}'
                    exception_alert(session_id, error)
                return (
                    new_blocks,
                    new_page,
                    gr.update(interactive=new_page > 0),
                    gr.update(interactive=new_page < max_page),
                )

            def update_blocks_header(page:int, blocks:list[dict])->str:
                start = int(page) * page_size
                end = min(start + page_size, len(blocks))
                return gr.update(value=f'Blocks {start}–{end-1} of {len(blocks)-1}')

            def edit_blocks(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if not session['cancellation_requested']:
                            if session['status'] in [status_tags['EDIT']]:
                                visible_main = False
                                visible_blocks = True
                                ebook_name = Path(session['ebook']).stem
                                blocks_current = session['blocks_current']
                                blocks = blocks_current['blocks']
                                max_page = max((len(blocks) - 1) // page_size, 0)
                                page = max(0, min(int(blocks_current.get('page', 0)), max_page))
                                page_updates = list(populate_page(session_id, page, blocks))
                                if session['cancellation_requested']:
                                    visible_main = True
                                    visible_blocks = False
                                result = (
                                    gr.update(value=ebook_name),
                                    gr.update(visible=visible_main), gr.update(visible=visible_blocks),
                                    blocks, page,
                                    gr.update(interactive=page > 0),
                                    gr.update(interactive=page < max_page),
                                    gr.update(interactive=True),
                                    gr.update(interactive=True),
                                    *page_updates
                                )
                                return result
                except Exception as e:
                    error = f'edit_blocks(): {e}'
                    exception_alert(session_id, error)
                n = len(blocks_components_flat) + 1
                return tuple(gr.update() for _ in range(9 + n + 1))

            def click_reset_block(session_id:str, block_id:int)->dict:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    text = session['blocks_orig']['blocks'][block_id]['text']
                    return gr.update(value=text)
                return gr.update()

            def collect_page(page:int, blocks:list[dict], *args)->list[dict]:
                expands = args[0]
                keeps = args[1:page_size + 1]
                voices = args[page_size + 1:2 * page_size + 1]
                texts = args[2 * page_size + 1:]
                new_blocks = [dict(b) for b in blocks]
                start = int(page) * page_size
                for i in range(page_size):
                    idx = start + i
                    if idx < len(new_blocks):
                        new_blocks[idx]['expand'] = expands[i] if i < len(expands) else False
                        new_blocks[idx]['keep'] = keeps[i]
                        new_blocks[idx]['voice'] = voices[i]
                        new_blocks[idx]['text'] = texts[i]
                return new_blocks

            def change_current_blocks(session_id:str, page:int, blocks:list[dict], *args)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    new_blocks = collect_page(page, blocks, *args)
                    blocks_current = session['blocks_current']
                    old_blocks = blocks_current['blocks']
                    for idx, b in enumerate(new_blocks):
                        if 'voice' not in b:
                            b['voice'] = session.get('voice')
                        if 'tts_engine' not in b:
                            b['tts_engine'] = session.get('tts_engine', '')
                        if 'fine_tuned' not in b:
                            b['fine_tuned'] = session.get('fine_tuned', '')
                        old_b = old_blocks[idx] if idx < len(old_blocks) else None
                        if 'id' not in b and old_b is not None:
                            b['id'] = old_b.get('id')
                        if old_b and old_b.get('text', '').strip() != b.get('text', '').strip():
                            b['sentences'] = []
                    blocks_current['blocks'] = new_blocks
                    session['blocks_current'] = blocks_current
                    save_db_blocks(session_id)

            def click_gr_blocks_cancel_btn(session_id:str, page:int, blocks:list[dict], *args)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session['status'] in [status_tags['EDIT']]:
                        session['status'] = status_tags['READY']
                        change_current_blocks(session_id, page, blocks, *args)
                        if session['ebook_mode'] == ebook_modes['TEXT']:
                            blocks_current = session['blocks_current']
                            blocks = blocks_current['blocks']
                            session['ebook_textarea'] = ' '.join(block['text'] for block in blocks)
                return gr.update(interactive=True), gr.update(visible=True), update_gr_audiobook_list(session_id), gr.update(visible=False), session['blocks_current']['blocks'], gr.update(value=session['ebook_textarea'])

            def click_gr_blocks_confirm_btn(session_id:str, event:int, page:int, blocks:list[dict], *args)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session['status'] in [status_tags['EDIT']]:
                        if not any(b['keep'] and b['text'].strip() for b in blocks):
                            error = 'At least one block must be kept.'
                            show_alert(session_id, {'type': 'warning', 'msg': error})
                            return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
                        change_current_blocks(session_id, page, blocks, *args)
                        if session['ebook_mode'] == ebook_modes['TEXT']:
                            blocks_current = session['blocks_current']
                            blocks = blocks_current['blocks']
                            session['ebook_textarea'] = ' '.join(block['text'] for block in blocks)
                        return gr.update(interactive=False), gr.update(interactive=False), gr.update(visible=True), gr.update(visible=False), update_gr_audiobook_list(session_id), gr.update(value=session['ebook_textarea']), (event + 1)
                return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()

            def change_gr_restore_session(data:DictProxy|None, state:dict, req:gr.Request)->tuple:
                try:
                    nonlocal models
                    msg = 'Error while loading saved session. Please try to delete your cookies and refresh the page'
                    if not data.get('id', False):
                        session = context.set_session(str(uuid.uuid4()))
                    else:
                        session = context.set_session(data.get('id'))
                    if len(active_sessions) == 0 or (data and data.get('status') in (None, status_tags['READY'])):
                        restore_session_from_data(
                            data, session,
                            force=bool(data and data.get('status') == status_tags['READY']),
                            filter_keys=True,
                        )
                    if not context_tracker.start_session(session['id']):
                        error = "Your session is already active.<br>If it's not the case please close your browser and relaunch it."
                        return gr.update(), gr.update(), gr.update(value=''), update_gr_glassmask(str=error)
                    else:
                        active_sessions.add(req.session_hash)
                        session[req.session_hash] = req.session_hash
                        session['cancellation_requested'] = False
                    if isinstance(session.get('ebook'), str):
                        if not os.path.exists(session['ebook']):
                            session['ebook'] = session['ebook_src'] = None
                    if isinstance(session.get('voice'), str):
                        if not os.path.exists(session['voice']):
                            session['voice'] = session['ebook_src'] = None
                    if isinstance(session.get('custom_model'), str):
                        custom_model_dir = session.get('custom_model_dir')
                        if isinstance(custom_model_dir, str) and not os.path.exists(custom_model_dir):
                            session['custom_model'] = None
                    if isinstance(session.get('tts_engine'), str):
                        models = load_engine_presets(session['tts_engine'])
                        if models:
                            if session['fine_tuned'] not in models.keys():
                                session['fine_tuned'] = default_fine_tuned
                        else:
                            session['tts_engine'] = default_tts_engine
                            session['fine_tuned'] = default_fine_tuned
                    if isinstance(session.get('audiobook'), str):
                        if not os.path.exists(session['audiobook']):
                            session['audiobook'] = None
                    session['status'] = status_tags['READY']
                    session['is_gui_process'] = is_gui_process
                    session['system'] = DEVICE_SYSTEM
                    session['session_dir'] = os.path.join(tmp_dir, f"proc-{session['id']}")
                    session['custom_model_dir'] = os.path.join(models_dir, '__sessions', f"model-{session['id']}")
                    session['voice_dir'] = os.path.join(voices_dir, '__sessions', f"voice-{session['id']}", session['language'])
                    os.makedirs(session['custom_model_dir'], exist_ok=True)
                    os.makedirs(session['voice_dir'], exist_ok=True)     
                    if is_gui_shared:
                        msg = f' Note: access limit time: {interface_shared_tmp_expire} days'
                        session['audiobooks_dir'] = os.path.join(audiobooks_gradio_dir, f"web-{session['id']}")
                        delete_unused_tmp_dirs(session['id'], audiobooks_gradio_dir, interface_shared_tmp_expire)
                    else:
                        msg = f' Note: if no activity is detected after {tmp_expire} days, your session will be cleaned up. '
                        session['audiobooks_dir'] = os.path.join(audiobooks_host_dir, f"web-{session['id']}")
                        delete_unused_tmp_dirs(session['id'], audiobooks_host_dir, tmp_expire)
                    msg += 'Your browser needs cookies enabled to resume the conversions.'
                    if not os.path.exists(session['audiobooks_dir']):
                        os.makedirs(session['audiobooks_dir'], exist_ok=True)
                    previous_hash = state['hash']
                    new_hash = hash_proxy_dict(MappingProxyType(session))
                    state['hash'] = new_hash
                    show_alert(session['id'], {"type": "info", "msg": msg})
                    return gr.update(value=json.dumps(session, cls=JSONDictProxyEncoder)), gr.update(value=state), gr.update(value=session['id']), gr.update()
                except Exception as e:
                    error = f'change_gr_restore_session(): {e}'
                    exception_alert(None, error)
                    return gr.update(), gr.update(), gr.update(), gr.update()

            async def update_gr_save_session(session_id:str, state:dict)->tuple:
                try:
                    session = context.get_session(session_id)
                    if not session or (session and not session.get('id', False)):
                        yield gr.update(), gr.update(), gr.update()
                        return
                    previous_hash = state.get("hash")
                    if session.get('status', None) == status_tags['CONVERTING']:
                        try:
                            if session.get('ticker') != len(audiobook_options):
                                session['ticker'] = len(audiobook_options)
                                new_hash = hash_proxy_dict(MappingProxyType(session))
                                state['hash'] = new_hash
                                session_filtered = {k: v for k, v in session.items() if k not in save_session_keys_except}
                                session_dict = json.dumps(session_filtered, cls=JSONDictProxyEncoder)
                                yield (
                                    gr.update(value=session_dict),
                                    gr.update(value=state),
                                    update_gr_audiobook_list(session_id),
                                )
                            else:
                                yield gr.update(), gr.update(), gr.update()
                        except NameError:
                            new_hash = hash_proxy_dict(MappingProxyType(session))
                            state['hash'] = new_hash
                            session_filtered = {k: v for k, v in session.items() if k not in save_session_keys_except}
                            session_dict = json.dumps(session_filtered, cls=JSONDictProxyEncoder)
                            yield (
                                gr.update(value=session_dict),
                                gr.update(value=state),
                                gr.update(),
                            )
                    elif session.get('status', None) != status_tags['SKIP']:
                        if session.get('status', None) == status_tags['EDIT']:
                            save_db_blocks(session_id)
                        new_hash = hash_proxy_dict(MappingProxyType(session))
                        if previous_hash == new_hash:
                            yield gr.update(), gr.update(), gr.update()
                        else:
                            state['hash'] = new_hash
                            session_filtered = {k: v for k, v in session.items() if k not in save_session_keys_except}
                            session_dict = json.dumps(session_filtered, cls=JSONDictProxyEncoder)
                            yield (
                                gr.update(value=session_dict),
                                gr.update(value=state),
                                gr.update(),
                            )
                    yield gr.update(), gr.update(), gr.update()
                except Exception as e:
                    error = f'update_gr_save_session(): {e}!'
                    exception_alert(session_id, error)
                    yield gr.update(), gr.update(value=e), gr.update()

            ################## Events Section

            def chain_check_override(event):
                return event.then(
                    fn=check_override_ebook,
                    inputs=[gr_session, gr_ebook_mode, gr_ebook_src, gr_ebook_textarea, gr_blocks_preview, gr_event],
                    outputs=[gr_modal, gr_event],
                    show_progress_on=[gr_progress]
                )

            def chain_refresh(event):
                return event.then(
                    fn=refresh_interface,
                    inputs=[gr_session],
                    outputs=outputs_refresh_interface,
                    show_progress_on=[gr_progress]
                )

            def chain_enable(event, always=False):
                if always:
                    return event.then(
                        fn=lambda s: (
                            list(enable_components(s)) + [
                                1 if context.get_session(s).get('ebook_mode') == ebook_modes['TEXT']
                                else 0
                            ]
                        ),
                        inputs=[gr_session],
                        outputs=outputs_enable_components + [gr_end_event],
                        show_progress_on=[gr_progress]
                    ).then(
                        fn=None,
                        inputs=[gr_end_event],
                        outputs=None,
                        js=f'(gr_end_event)=>{{if(gr_end_event){{{js_show_elements}}}}}'
                    )
                else:
                    return event.then(
                        fn=lambda s: (
                            enable_components(s) + (1,)
                            if context.get_session(s)['status'] in [status_tags['END'], status_tags['READY']]
                            and context.get_session(s)['ebook_mode'] == ebook_modes['TEXT']
                            else (
                                enable_components(s) + (0,)
                                if context.get_session(s)['status'] in [status_tags['END'], status_tags['READY']]
                                else [gr.update()] * len(outputs_enable_components) + [0]
                            )
                        ),
                        inputs=[gr_session],
                        outputs=outputs_enable_components + [gr_end_event],
                        show_progress_on=[gr_progress]
                    ).then(
                        fn=None,
                        inputs=[gr_end_event],
                        outputs=None,
                        js=f'(gr_end_event)=>{{if(gr_end_event){{{js_show_elements}}}}}'
                    )

            ######## grouped tuples

            inputs_start_conversion = [
                gr_session, gr_device, gr_ebook_mode, gr_ebook_src, gr_ebook_textarea, gr_blocks_preview, gr_tts_engine_list, gr_language, gr_voice_list,
                gr_custom_model_list, gr_fine_tuned_list, gr_output_format_list, gr_output_channel_list,
                gr_xtts_temperature, gr_xtts_length_penalty, gr_xtts_num_beams, gr_xtts_repetition_penalty, gr_xtts_top_k, gr_xtts_top_p, gr_xtts_speed, gr_xtts_enable_text_splitting,
                gr_bark_text_temp, gr_bark_waveform_temp, gr_output_split, gr_output_split_hours
            ]
            outputs_disable_components = [
                gr_ebook_textarea, gr_ebook_mode, gr_blocks_preview, gr_language, gr_voice_file, gr_voice_list,
                gr_device, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file,
                gr_custom_model_list, gr_output_format_list, gr_output_channel_list, gr_output_split, gr_output_split_hours,
                gr_convert_btn, gr_voice_play, gr_voice_del_btn, gr_custom_model_del_btn, gr_session_switch_btn
            ]
            outputs_enable_components = [
                gr_ebook_textarea, gr_ebook_mode, gr_blocks_preview, gr_language, gr_voice_file, gr_voice_list,
                gr_device, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file,
                gr_custom_model_list, gr_output_format_list, gr_output_channel_list, gr_output_split, gr_output_split_hours,
                gr_voice_play, gr_voice_del_btn, gr_session_switch_btn, gr_blocks_cancel_btn, gr_blocks_confirm_btn, gr_custom_model_del_btn, gr_modal, gr_convert_btn
            ]
            outputs_edit_blocks = [
                gr_blocks_markdown, gr_group_main, gr_group_blocks,
                gr_blocks_data, gr_blocks_page,
                gr_blocks_back_btn, gr_blocks_next_btn,
                gr_blocks_cancel_btn, gr_blocks_confirm_btn,
                *blocks_components_flat, gr_blocks_header, gr_blocks_expands
            ]
            outputs_restore_interface = [
                gr_ebook_src, gr_ebook_textarea, gr_ebook_mode, gr_blocks_preview, gr_device, gr_language, gr_voice_list,
                gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list, gr_output_format_list, gr_output_channel_list,
                gr_output_split, gr_output_split_hours, gr_row_output_split_hours, gr_audiobook_list, gr_group_custom_model, gr_convert_btn,
                gr_voice_player_hidden, gr_voice_play, gr_voice_del_btn, gr_custom_model_del_btn
            ]
            outputs_refresh_interface = [
                gr_modal, gr_group_main, gr_tab_xtts_params, gr_tab_bark_params, gr_convert_btn,
                gr_ebook_src, gr_ebook_textarea, gr_device, gr_audiobook_player, gr_audiobook_list,
                gr_voice_list, gr_voice_highlight_css, gr_progress
            ]
            outputs_on_voice_upload = [
                gr_ebook_src, gr_ebook_textarea, gr_ebook_mode, gr_language, gr_tts_engine_list,
                gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list, gr_session_switch_btn,
                gr_convert_btn, gr_voice_play, gr_voice_del_btn
            ]
            outputs_on_custom_upload = [
                gr_ebook_src, gr_ebook_textarea, gr_ebook_mode, gr_language, gr_tts_engine_list,
                gr_fine_tuned_list, gr_voice_file, gr_session_switch_btn,
                gr_voice_play, gr_voice_del_btn, gr_convert_btn, gr_custom_model_label, gr_custom_model_del_btn
            ]
            
            ######### event triggers
            
            gr_ebook_src.upload(
                fn=upload_gr_ebook_src,
                inputs=[gr_session, gr_ebook_mode],
                outputs=None
            )
            chain_enable(
                gr_ebook_src.change(
                    fn=change_gr_ebook_src,
                    inputs=[gr_session, gr_ebook_mode, gr_ebook_src],
                    outputs=[gr_modal, gr_voice_highlight_css, gr_voice_list, gr_row_voice_player, gr_voice_selected_filename],
                    show_progress_on=[gr_ebook_src]
                ),
                always=True
            )
            gr_ebook_src.select(
                fn=select_gr_ebook_src,
                inputs=[gr_session, gr_ebook_mode, gr_ebook_src],
                outputs=[gr_voice_list, gr_voice_highlight_css, gr_row_voice_player, gr_voice_selected_filename],
                show_progress='hidden'
            )
            gr_ebook_textarea.change(
                fn=change_gr_ebook_textarea,
                inputs=[gr_session, gr_ebook_textarea],
                outputs=None
            )
            gr_ebook_mode.change(
                fn=change_gr_ebook_mode,
                inputs=[gr_session, gr_ebook_mode],
                outputs=[gr_ebook_src, gr_ebook_textarea, gr_convert_btn, gr_voice_highlight_css, gr_row_voice_player, gr_voice_selected_filename],
                show_progress_on=[gr_progress]
            ).then(
                fn=None,
                inputs=[gr_ebook_mode],
                outputs=None,
                js=f'''(mode)=>{{if(mode === "{ebook_modes['TEXT']}"){{window.gr_ebook_textarea_counter();}}}}'''
            )
            gr_blocks_preview.select(
                fn=lambda session_id, val: change_param('blocks_preview', session_id, bool(val)),
                inputs=[gr_session, gr_blocks_preview],
                outputs=None
            )
            gr_voice_file.upload(
                fn=disable_on_voice_upload,
                inputs=None,
                outputs=outputs_on_voice_upload,
                show_progress_on=[gr_voice_file]
            ).then(
                fn=change_gr_voice_file,
                inputs=[gr_session, gr_voice_file],
                outputs=[gr_voice_list],
                show_progress_on=[gr_voice_list]
            ).then(
                fn=lambda: gr.update(value=None),
                inputs=None,
                outputs=[gr_voice_file],
                show_progress_on=[gr_voice_list]
            ).then(
                fn=enable_on_voice_upload,
                inputs=[gr_session],
                outputs=outputs_on_voice_upload,
                show_progress_on=[gr_voice_list]
            )
            gr_voice_list.change(
                fn=change_gr_voice_list,
                inputs=[gr_session, gr_voice_list],
                outputs=[gr_voice_player_hidden, gr_voice_play, gr_voice_del_btn],
                show_progress_on=[gr_progress]
            )
            gr_voice_del_btn.click(
                fn=click_gr_voice_del_btn,
                inputs=[gr_session, gr_voice_list],
                outputs=[gr_modal, gr_data_field_hidden],
                show_progress_on=[gr_progress]
            )
            gr_device.change(
                fn=change_gr_device,
                inputs=[gr_session, gr_device],
                outputs=None
            )
            gr_language.change(
                fn=change_gr_language,
                inputs=[gr_session, gr_language],
                outputs=[gr_language, gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list],
                show_progress_on=[gr_progress]
            ).then(
                fn=update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_tts_engine_list.change(
                fn=change_gr_tts_engine_list,
                inputs=[gr_session, gr_tts_engine_list],
                outputs=[gr_tts_rating, gr_tab_xtts_params, gr_tab_bark_params, gr_group_custom_model, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list, gr_custom_model_label],
                show_progress_on=[gr_progress]
            ).then(
                fn=update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_fine_tuned_list.change(
                fn=change_gr_fine_tuned_list,
                inputs=[gr_session, gr_fine_tuned_list],
                outputs=[gr_group_custom_model],
                show_progress_on=[gr_progress]
            ).then(
                fn=update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_custom_model_file.upload(
                fn=disable_on_custom_upload,
                inputs=None,
                outputs=outputs_on_custom_upload,
                show_progress_on=[gr_custom_model_file]
            ).then(
                fn=change_gr_custom_model_file,
                inputs=[gr_session, gr_custom_model_file, gr_tts_engine_list],
                outputs=[gr_custom_model_file, gr_custom_model_list],
                show_progress_on=[gr_custom_model_list]
            ).then(
                fn=update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list],
                show_progress_on=[gr_custom_model_list]
            ).then(
                fn=enable_on_custom_upload,
                inputs=[gr_custom_model_list, gr_ebook_src, gr_ebook_textarea],
                outputs=outputs_on_custom_upload,
                show_progress_on=[gr_custom_model_list]
            )
            gr_custom_model_list.change(
                fn=change_gr_custom_model_list,
                inputs=[gr_session, gr_custom_model_list],
                outputs=[gr_fine_tuned_list, gr_voice_list, gr_custom_model_del_btn],
                show_progress_on=[gr_progress]
            )
            gr_custom_model_del_btn.click(
                fn=click_gr_custom_model_del_btn,
                inputs=[gr_session, gr_custom_model_list],
                outputs=[gr_modal, gr_data_field_hidden],
                show_progress_on=[gr_progress]
            )
            gr_output_format_list.change(
                fn=change_gr_output_format_list,
                inputs=[gr_session, gr_output_format_list],
                outputs=None
            )
            gr_output_channel_list.change(
                fn=change_gr_output_channel_list,
                inputs=[gr_session, gr_output_channel_list],
                outputs=None
            )
            gr_output_split.select(
                fn=change_gr_output_split,
                inputs=[gr_session, gr_output_split],
                outputs=[gr_row_output_split_hours],
                show_progress_on=[gr_progress]
            )
            gr_output_split_hours.change(
                fn=lambda session_id, val: change_param('output_split_hours', session_id, str(val)),
                inputs=[gr_session, gr_output_split_hours],
                outputs=None
            )
            gr_session_switch_btn.click(
                fn=click_gr_session_switch_btn,
                inputs=[gr_session, gr_backup_session],
                outputs=[gr_restore_session, gr_session, gr_backup_session, gr_session_switch_btn, gr_session_switch_disable_state, gr_session_switch_enable_state],
                show_progress_on=[gr_session_switch_btn]
            )
            gr_session_switch_disable_state.change(
                fn=lambda session_id: disable_components(session_id, exceptions=['gr_session_switch_btn']),
                inputs=[gr_session_switch_disable_state],
                outputs=outputs_disable_components,
                show_progress_on=[gr_session_switch_btn],
                queue=False
            ).then(
                fn=lambda: None,
                inputs=None,
                outputs=[gr_session_switch_disable_state],
                js=f'''
                    ()=>{{
                        const elem = document.querySelector("#gr_session textarea");
                        if(elem){{
                            elem.select();
                        }}
                        {js_hide_elements}
                    }}
                '''
            )
            gr_session_switch_enable_state.change(
                fn=enable_components,
                inputs=[gr_session_switch_enable_state],
                outputs=outputs_enable_components,
                show_progress_on=[gr_session_switch_btn]
            ).then(
                fn=lambda: None,
                inputs=None,
                outputs=[gr_session_switch_enable_state],
                js=f'''
                    ()=>{{
                        const elem = document.querySelector("#gr_session textarea");
                        if(elem){{
                            elem.setSelectionRange(0, 0);
                        }}
                        {js_show_elements}
                    }}
                '''
)
            gr_progress.change(
                fn=None,
                inputs=[gr_progress],
                js=r'''
                    (filename)=>{
                        if(filename){
                            const gr_root = (window.gradioApp && window.gradioApp()) || document;
                            const gr_ebook_src = gr_root.querySelector("#gr_ebook_src");
                            if(!gr_ebook_src){
                                return;
                            }
                            function normalizeForGradio(name){
                                return name
                                    .normalize("NFC")
                                    // Remove chars not supported by OS paths
                                    .replace(/[<>:"/\\|?*\x00-\x1F]/g, "")
                                    // Remove Gradio-sanitized odd punctuation (including quotes)
                                    .replace(/[!(){}\[\]']/g, "")
                                    // Collapse multiple dots/spaces before extension
                                    .replace(/\s+\./g, ".")
                                    // Strip trailing spaces/dots (Windows forbids)
                                    .replace(/[. ]+$/, "")
                                    // Remove Arabic tatweel/harakat
                                    .replace(/[\u0640\u0651\u064B-\u065F]/g, "")
                                    .trim();
                            }
                            const rows = gr_ebook_src.querySelectorAll("table.file-preview tr.file");
                            rows.forEach((row, idx) => {
                                const filenameCell = row.querySelector("td.filename");
                                if (filenameCell) {
                                    const rowName = normalizeForGradio(filenameCell.getAttribute("aria-label"));
                                    filename = filename.split("/")[0].trim();
                                    if (rowName === filename) {
                                        row.style.display = "none";
                                    }
                                }
                            });
                        }
                    }
                '''
            )
            gr_playback_time.change(
                fn=change_gr_playback_time,
                inputs=[gr_session, gr_playback_time],
                js='''
                    (time)=>{
                        try{
                            window.session_storage.playback_time = Number(time);
                        }catch(e){
                            console.warn("gr_playback_time.change error: "+e);
                        }
                    }
                '''
            )
            gr_audiobook_download_btn.click(
                fn=toggle_audiobook_files,
                inputs=[gr_session, gr_audiobook_list, gr_audiobook_files_state],
                outputs=[gr_audiobook_files, gr_audiobook_files_state],
                show_progress_on=[gr_audiobook_list]
            )
            gr_audiobook_list.change(
                fn=change_gr_audiobook_list,
                inputs=[gr_session, gr_audiobook_list],
                outputs=[gr_group_audiobook_list],
                show_progress_on=[gr_audiobook_list]
            ).then(
                fn=update_gr_audiobook_player,
                inputs=[gr_session],
                outputs=[gr_playback_time, gr_audiobook_player, gr_audiobook_vtt],
                show_progress_on=[gr_audiobook_list]
            ).then(
                fn=lambda: (gr.update(visible=False, value=None), False),
                inputs=None,
                outputs=[gr_audiobook_files, gr_audiobook_files_state],
                show_progress_on=[gr_audiobook_list],
                js='()=>{window.load_vtt();}'
            )
            gr_audiobook_del_btn.click(
                fn=click_gr_audiobook_del_btn,
                inputs=[gr_session, gr_audiobook_list],
                outputs=[gr_modal, gr_data_field_hidden],
                show_progress_on=[gr_audiobook_list]
            )

            ########### XTTSv2 Params

            gr_tab_xtts_params.select(
                fn=None,
                inputs=None,
                outputs=None,
                js='''
                () => {
                    if (!window._xtts_sliders_initialized) {
                        const checkXttsExist = setInterval(() => {
                            const slider = document.querySelector("#gr_xtts_speed input[type=range]");
                            if(slider){
                                clearInterval(checkXttsExist);
                                window._xtts_sliders_initialized = true;
                                init_xtts_sliders();
                            }
                        }, 500);
                    }
                }
                '''
            )
            gr_xtts_temperature.change(
                fn=lambda session_id, val: change_param('xtts_temperature', session_id, float(val)),
                inputs=[gr_session, gr_xtts_temperature],
                outputs=None
            )
            gr_xtts_length_penalty.change(
                fn=lambda session_id, val, val2: change_param('xtts_length_penalty', session_id, int(val), int(val2)),
                inputs=[gr_session, gr_xtts_length_penalty, gr_xtts_num_beams],
                outputs=None,
            )
            gr_xtts_num_beams.change(
                fn=lambda session_id, val, val2: change_param('xtts_num_beams', session_id, int(val), int(val2)),
                inputs=[gr_session, gr_xtts_num_beams, gr_xtts_length_penalty],
                outputs=None,
            )
            gr_xtts_repetition_penalty.change(
                fn=lambda session_id, val: change_param('xtts_repetition_penalty', session_id, float(val)),
                inputs=[gr_session, gr_xtts_repetition_penalty],
                outputs=None
            )
            gr_xtts_top_k.change(
                fn=lambda session_id, val: change_param('xtts_top_k', session_id, int(val)),
                inputs=[gr_session, gr_xtts_top_k],
                outputs=None
            )
            gr_xtts_top_p.change(
                fn=lambda session_id, val: change_param('xtts_top_p', session_id, float(val)),
                inputs=[gr_session, gr_xtts_top_p],
                outputs=None
            )
            gr_xtts_speed.change(
                fn=lambda session_id, val: change_param('xtts_speed', session_id, float(val)),
                inputs=[gr_session, gr_xtts_speed],
                outputs=None
            )
            gr_xtts_enable_text_splitting.select(
                fn=lambda session_id, val: change_param('xtts_enable_text_splitting', session_id, bool(val)),
                inputs=[gr_session, gr_xtts_enable_text_splitting],
                outputs=None
            )

            ########### BARK Params

            gr_tab_bark_params.select(
                fn=None,
                inputs=None,
                outputs=None,
                js='''
                    ()=>{
                        if (!window._bark_sliders_initialized) {
                            const checkBarkExist = setInterval(() => {
                                const slider = document.querySelector("#gr_bark_waveform_temp input[type=range]");
                                if(slider){
                                    clearInterval(checkBarkExist);
                                    window._bark_sliders_initialized = true;
                                    init_bark_sliders();
                                }
                            }, 500);
                        }
                    }
                '''
            )
            gr_bark_text_temp.change(
                fn=lambda session_id, val: change_param('bark_text_temp', session_id, float(val)),
                inputs=[gr_session, gr_bark_text_temp],
                outputs=None
            )
            gr_bark_waveform_temp.change(
                fn=lambda session_id, val: change_param('bark_waveform_temp', session_id, float(val)),
                inputs=[gr_session, gr_bark_waveform_temp],
                outputs=None
            )

            ############ Timer to save session to localStorage

            gr_timer = gr.Timer(9, active=False)
            gr_timer.tick(
                fn=update_gr_save_session,
                inputs=[gr_session, gr_session_update],
                outputs=[gr_save_session, gr_session_update, gr_audiobook_list]
            )

            ########### Main chains

            chain_enable(
                chain_check_override(
                    gr_convert_btn.click(
                        fn=disable_components,
                        inputs=[gr_session],
                        outputs=outputs_disable_components,
                        show_progress_on=[gr_progress],
                        queue=False
                    )
                ),
                always=False
            ).then(
                js=f'()=>{{{js_hide_elements}}}'
            )
            chain_enable(
                gr_override_cancel_btn.click(
                    fn=click_gr_override_cancel_btn,
                    inputs=[gr_session],
                    outputs=[gr_modal],
                    show_progress_on=[gr_progress]
                ),
                always=True
            )
            gr_override_confirm_btn.click(
                fn=click_gr_override_confirm_btn,
                inputs=[gr_session, gr_event, gr_audiobook_files_state],
                outputs=[gr_modal, gr_event, gr_audiobook_list, gr_audiobook_files, gr_audiobook_files_state],
                show_progress_on=[gr_progress]
            )
            chain_enable(
                chain_check_override(
                    chain_refresh(
                        gr_event.change(
                            fn=disable_components,
                            inputs=[gr_session],
                            outputs=outputs_disable_components,
                            show_progress_on=[gr_progress],
                            queue=False
                        ).then(
                            fn=lambda: None,
                            js=f'()=>{{{js_hide_elements}}}'
                        ).then(
                            fn=start_conversion,
                            inputs=inputs_start_conversion,
                            outputs=[gr_progress],
                            show_progress_on=[gr_progress],
                        ).then(
                            fn=edit_blocks,
                            inputs=[gr_session],
                            outputs=outputs_edit_blocks,
                            show_progress_on=[gr_progress]
                        )
                    )
                ),
                always=False
            )
            chain_enable(
                gr_blocks_cancel_btn.click(
                    fn=lambda: (gr.update(interactive=False), gr.update(interactive=False)),
                    outputs=[gr_blocks_cancel_btn, gr_blocks_confirm_btn],
                    show_progress_on=[gr_progress],
                    queue=False
                ).then(
                    fn=click_gr_blocks_cancel_btn,
                    inputs=[gr_session, gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                    outputs=[gr_convert_btn, gr_group_main, gr_audiobook_list, gr_group_blocks, gr_blocks_data, gr_ebook_textarea],
                    show_progress_on=[gr_progress]
                ),
                always=True
            )
            chain_enable(
                gr_blocks_confirm_btn.click(
                    fn=lambda page, blocks, expands, *args: collect_page(page, blocks, expands, *args),
                    inputs=[gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                    outputs=[gr_blocks_data],
                    show_progress_on=[gr_progress]
                ).then(
                    fn=click_gr_blocks_confirm_btn,
                    inputs=[gr_session, gr_blocks_event, gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                    outputs=[gr_blocks_cancel_btn, gr_blocks_confirm_btn, gr_group_main, gr_group_blocks, gr_audiobook_list, gr_ebook_textarea, gr_blocks_event],
                    show_progress_on=[gr_progress]
                )
            )
            chain_enable(
                chain_check_override(
                    chain_refresh(
                        gr_blocks_event.change(
                            fn=finalize_audiobook,
                            inputs=[gr_session],
                            outputs=[gr_progress, gr_dummy_bool],
                            show_progress_on=[gr_progress],
                        )
                    )
                ),
                always=True
            ).then(
                fn=None,
                inputs=None,
                outputs=None,
                js='()=>{window.load_vtt();}'
            )
            ###########
            gr_blocks_back_btn.click(
                fn=lambda session_id, page, blocks, *args: navigate(session_id, page, blocks, -1, *args),
                inputs=[gr_session, gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                outputs=[gr_blocks_data, gr_blocks_page, gr_blocks_back_btn, gr_blocks_next_btn],
                show_progress_on=[gr_blocks_nav]
            ).then(
                fn=populate_page,
                inputs=[gr_session, gr_blocks_page, gr_blocks_data],
                outputs=[*blocks_components_flat, gr_blocks_header, gr_blocks_expands],
                show_progress_on=[gr_blocks_nav]
            )
            gr_blocks_next_btn.click(
                fn=lambda session_id, page, blocks, *args: navigate(session_id, page, blocks, 1, *args),
                inputs=[gr_session, gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                outputs=[gr_blocks_data, gr_blocks_page, gr_blocks_back_btn, gr_blocks_next_btn],
                show_progress_on=[gr_blocks_nav]
            ).then(
                fn=populate_page,
                inputs=[gr_session, gr_blocks_page, gr_blocks_data],
                outputs=[*blocks_components_flat, gr_blocks_header, gr_blocks_expands],
                show_progress_on=[gr_blocks_nav]
            )
            #############
            gr_save_session.change(
                fn=None,
                inputs=[gr_save_session],
                js='''
                    (data)=>{
                        try{
                            if(data){
                                localStorage.clear();
                                data.playback_time = Number(window.session_storage.playback_time);
                                data.playback_volume = parseFloat(window.session_storage.playback_volume);
                                localStorage.setItem("data", JSON.stringify(data));
                            }
                        }catch(e){
                            console.warn("gr_save_session.change error: "+e);
                        }
                    }
                '''
            )       
            gr_restore_session.change(
                fn=change_gr_restore_session,
                inputs=[gr_restore_session, gr_session_update],
                outputs=[gr_save_session, gr_session_update, gr_session, gr_glassmask],
                show_progress_on=[gr_progress]
            ).then(
                fn=restore_interface,
                inputs=[gr_session],
                outputs=outputs_restore_interface,
                show_progress_on=[gr_progress]
            ).then(
                fn=restore_audiobook_player,
                inputs=[gr_session, gr_audiobook_list],
                outputs=[gr_group_audiobook_list, gr_audiobook_player, gr_timer],
                show_progress_on=[gr_progress]
            ).then(
                fn=lambda session: update_gr_glassmask(attr=['gr-glass-mask', 'hide']) if session else gr.update(),
                inputs=[gr_session],
                outputs=[gr_glassmask],
                show_progress_on=[gr_progress]
            ).then(
                fn=None,
                inputs=None,
                js='()=>{window.init_interface();}'
            )
            gr_deletion_confirm_btn.click(
                fn=click_gr_deletion,
                inputs=[gr_session, gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_data_field_hidden],
                outputs=[gr_modal, gr_custom_model_list, gr_audiobook_list, gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_deletion_cancel_btn.click(
                fn=click_gr_deletion,
                inputs=[gr_session, gr_voice_list, gr_custom_model_list, gr_audiobook_list],
                outputs=[gr_modal, gr_custom_model_list, gr_audiobook_list, gr_voice_list],
                show_progress_on=[gr_progress]
            )
            ############
            app.load(
                fn=None,
                js=r'''
                    ()=>{
                        try{
                            let gr_root = (window.gradioApp && window.gradioApp()) || document;
                            let gr_checkboxes;
                            let gr_radios;
                            let gr_voice_player_hidden;
                            let gr_audiobook_vtt;
                            let gr_audiobook_sentence;
                            let gr_audiobook_player;
                            let gr_playback_time;
                            let gr_progress;
                            let gr_voice_play;
                            let gr_ebook_textarea;
                            let tabs_open = false;
                            let init_elements_timeout;
                            let init_audiobook_player_timeout;
                            let audio_filter = "";
                            let cues = [];
                            if(typeof window.onElementAvailable !== "function"){
                                window.onElementAvailable = (selector, callback, { root = (window.gradioApp && window.gradioApp()) || document, once = false } = {})=> {
                                    const seen = new WeakSet();
                                    const fireFor = (context) => {
                                        context.querySelectorAll(selector).forEach((el) => {
                                            if (seen.has(el)) return;
                                            const success = callback(el);
                                            if (success !== false) {
                                                // Mark as seen only if callback succeeded
                                                seen.add(el);
                                                if (once) return;
                                            } else {
                                                // Retry check later (in case conditions weren’t met yet)
                                                setTimeout(() => fireFor(root), 300);
                                            }
                                        });
                                    };
                                    fireFor(root);
                                    const observer = new MutationObserver((mutations) => {
                                        for (const m of mutations) {
                                            for (const n of m.addedNodes) {
                                                if (n.nodeType !== 1) continue;
                                                if (n.matches?.(selector)) {
                                                    if (!seen.has(n)) {
                                                        const success = callback(n);
                                                        if (success !== false) {
                                                            seen.add(n);
                                                            if (once) {
                                                                observer.disconnect();
                                                                return;
                                                            }
                                                        } else {
                                                            setTimeout(() => fireFor(root), 300);
                                                        }
                                                    }
                                                } else {
                                                    fireFor(n);
                                                }
                                            }
                                        }
                                    });
                                    observer.observe(root, { childList: true, subtree: true });
                                    return () => observer.disconnect();
                                }
                            }
                            if(typeof window.init_interface !== "function"){
                                window.init_interface = ()=>{
                                    try {
                                        gr_root = (window.gradioApp && window.gradioApp()) || document;
                                        gr_progress = (gr_root) ? gr_root.querySelector("#gr_progress") : undefined;
                                        if(!gr_root || !gr_progress){
                                            clearTimeout(init_elements_timeout);
                                            console.warn("Components not ready… retrying");
                                            init_elements_timeout = setTimeout(init_interface, 1000);
                                            return;
                                        }
                                        // Function to apply theme borders
                                        function applyThemeBorders(){
                                            const url = new URL(window.location);
                                            const theme = url.searchParams.get("__theme");
                                            let elColor = "#666666";
                                            if(theme == "dark"){
                                                elColor = "#fff";
                                            }else if(!theme){
                                                const osTheme = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
                                                if(osTheme){
                                                    elColor = "#fff";
                                                }
                                            }
                                            gr_root.querySelectorAll("input[type='checkbox'], input[type='radio']")
                                                .forEach(cb => cb.style.border = "1px solid " + elColor);
                                        }
                                        // Run once on init
                                        applyThemeBorders();
                                        // Re-run when DOM changes (tabs, redraws, etc.)
                                        new MutationObserver(applyThemeBorders).observe(gr_root, {
                                            childList: true,
                                            subtree: true
                                        });
                                        // Keep your progress observer
                                        new MutationObserver(tab_progress).observe(gr_progress, {
                                            attributes: true,
                                            childList: true,
                                            subtree: true,
                                            characterData: true
                                        });
                                        // new MutationObserver(tab_progress).observe(gr_progress.parentElement, { ... });
                                        // gr_progress.addEventListener("change", tab_progress);
                                        if(!window._tab_progress_interval){
                                            window._tab_progress_interval = setInterval(tab_progress, 500);
                                        }
                                        window.gr_ebook_textarea_counter();
                                    }catch(e){
                                        console.warn("init_interface error:", e);
                                    }
                                };
                            }
                            if(typeof(window._restoreSlider) !== "function"){
                                window._restoreSlider = (slider, parseFn = parseFloat)=>{
                                    if(!slider) return;
                                    const container = slider.closest("div[id]");
                                    if(!container) return;
                                    const key = container.id.replace(/^gr_/, "");
                                    const saved = window.session_storage?.[key];
                                    if(saved === undefined || saved === null || saved === ""){
                                        return;
                                    }
                                    const parsed = parseFn(saved);
                                    if(!Number.isFinite(parsed)){
                                        return;
                                    }
                                    slider.value = parsed;
                                    slider.dispatchEvent(new Event("input", { bubbles: true }));
                                };
                            }
                            if(typeof(window.init_xtts_sliders) !== "function"){
                                window.init_xtts_sliders = ()=>{
                                    try{
                                        const q = (id) => gr_root.querySelector(`#gr_${id} input[type=number]`);
                                        window._restoreSlider(q("xtts_temperature"));
                                        window._restoreSlider(q("xtts_repetition_penalty"));
                                        window._restoreSlider(q("xtts_top_k"), (v) => parseInt(v, 10));
                                        window._restoreSlider(q("xtts_top_p"));
                                        window._restoreSlider(q("xtts_speed"));
                                    }catch(e){
                                        console.warn("init_xtts_sliders error:", e);
                                    }
                                };
                            }
                            if(typeof(window.init_bark_sliders) !== "function"){
                                window.init_bark_sliders = ()=>{
                                    try{
                                        const q = (id) => gr_root.querySelector(`#gr_${id} input[type=number]`);
                                        window._restoreSlider(q("bark_text_temp"));
                                        window._restoreSlider(q("bark_waveform_temp"));
                                    }catch(e){
                                        console.warn("init_bark_sliders error:", e);
                                    }
                                };
                            }
                            if(typeof window.init_voice_player_hidden !== "function"){
                                window.init_voice_player_hidden = ()=>{
                                    try{
                                        const gr_voice_player_hidden = gr_root.querySelector("#gr_voice_player_hidden audio");
                                        const gr_voice_play = gr_root.querySelector("#gr_voice_play");
                                        if(gr_voice_player_hidden && gr_voice_play){
                                            if(gr_voice_play.dataset.bound === "true") return;
                                            gr_voice_play.dataset.bound = "true";
                                            gr_voice_player_hidden.addEventListener("loadeddata", ()=>{
                                                gr_voice_play.textContent = "▶";
                                            });
                                            gr_voice_play.addEventListener("click", ()=>{
                                                if(gr_voice_player_hidden.paused){
                                                    gr_voice_player_hidden.play().then(()=>{
                                                        gr_voice_play.textContent = "⏸";
                                                    }).catch(err => console.warn("Play failed:", err));
                                                }else{
                                                    gr_voice_player_hidden.pause();
                                                    gr_voice_play.textContent = "▶";
                                                }
                                            });
                                            gr_voice_player_hidden.addEventListener("pause", ()=>{
                                                gr_voice_play.textContent = "▶";
                                            });
                                            gr_voice_player_hidden.addEventListener("ended", ()=>{
                                                gr_voice_play.textContent = "▶";
                                            });
                                            gr_voice_player_hidden.addEventListener("play", ()=>{
                                                const v = window.session_storage?.playback_volume ?? 1;
                                                gr_voice_player_hidden.volume = v;
                                            });
                                            return true;
                                        }else{
                                            console.warn("Voice player not found yet, retrying…");
                                            setTimeout(window.init_voice_player_hidden, 500);
                                        }
                                    }catch(e){
                                        console.warn("init_voice_player_hidden error:", e);
                                    }
                                    return false;
                                };
                            }
                            if(typeof(window.init_audiobook_player) !== "function"){
                                window.init_audiobook_player = ()=>{
                                    try{
                                        if(gr_root){
                                            gr_audiobook_player = gr_root.querySelector("#gr_audiobook_player audio");
                                            gr_audiobook_sentence = gr_root.querySelector("#gr_audiobook_sentence textarea");
                                            gr_playback_time = gr_root.querySelector("#gr_playback_time input");
                                            let lastCue = null;
                                            let fade_timeout = null;
                                            let last_time = 0;
                                            if(gr_audiobook_player && gr_audiobook_sentence && gr_playback_time){
                                                function trackPlayback(){
                                                    try {
                                                        window.session_storage.playback_time = parseFloat(gr_audiobook_player.currentTime);
                                                        const cue = findCue(window.session_storage.playback_time);
                                                        if(cue && cue !== lastCue){
                                                            if(fade_timeout){
                                                                gr_audiobook_sentence.style.opacity = "1";
                                                            }else{
                                                                gr_audiobook_sentence.style.opacity = "0";
                                                            }
                                                            gr_audiobook_sentence.style.transition = "none";
                                                            gr_audiobook_sentence.value = cue.text;
                                                            clearTimeout(fade_timeout);
                                                            fade_timeout = setTimeout(() => {
                                                                gr_audiobook_sentence.style.transition = "opacity 0.15s ease-in";
                                                                gr_audiobook_sentence.style.opacity = "1";
                                                                fade_timeout = null;
                                                            }, 33);
                                                            lastCue = cue;
                                                        }else if(!cue && lastCue !== null){
                                                            lastCue = null;
                                                        }
                                                        const now = performance.now();
                                                        if(now - last_time > 1000){
                                                            gr_playback_time.value = String(window.session_storage.playback_time);
                                                            gr_playback_time.dispatchEvent(new Event("input", {bubbles: true}));
                                                            last_time = now;
                                                        }
                                                    }catch(e){
                                                        console.warn("gr_audiobook_player tracking error:", e);
                                                    }
                                                    if(!gr_audiobook_player.ended){
                                                        requestAnimationFrame(trackPlayback);
                                                    }
                                                }
                                                gr_audiobook_player.addEventListener("loadeddata", ()=>{
                                                    gr_audiobook_player.style.transition = "filter 1s ease";
                                                    gr_audiobook_player.style.filter = audio_filter;
                                                    gr_audiobook_player.currentTime = parseFloat(window.session_storage?.playback_time) || 0;
                                                    gr_audiobook_player.volume = window.session_storage.playback_volume;
                                                });
                                                gr_audiobook_player.addEventListener("play", ()=>{
                                                    requestAnimationFrame(trackPlayback);
                                                });
                                                gr_audiobook_player.addEventListener("seeked", ()=>{
                                                    window.session_storage.playback_time = gr_audiobook_player.currentTime;
                                                    requestAnimationFrame(trackPlayback);
                                                });
                                                gr_audiobook_player.addEventListener("ended", ()=>{
                                                    gr_audiobook_sentence.value = "…";
                                                    window.session_storage.playback_time = 0;
                                                    lastCue = null;
                                                });
                                                gr_audiobook_player.addEventListener("volumechange", ()=>{
                                                    window.session_storage.playback_volume = gr_audiobook_player.volume;
                                                    gr_voice_player_hidden = gr_root.querySelector("#gr_voice_player_hidden audio");
                                                    if(gr_voice_player_hidden){
                                                        gr_voice_player_hidden.volume = gr_audiobook_player.volume;
                                                        gr_voice_player_hidden.dispatchEvent(new Event("volumechange", { bubbles: true }));
                                                    }
                                                });
                                                const themURL = new URL(window.location);
                                                const theme = themURL.searchParams.get("__theme");
                                                let osTheme;
                                                if(theme){
                                                    if(theme == "dark"){
                                                        audio_filter = "invert(1) hue-rotate(180deg)";
                                                    }
                                                }else{
                                                    osTheme = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
                                                    if(osTheme){
                                                        audio_filter = "invert(1) hue-rotate(180deg)";
                                                    }
                                                }
                                                gr_audiobook_player.style.transition = "filter 1s ease";
                                                gr_audiobook_player.style.filter = audio_filter;
                                                gr_audiobook_player.volume = window.session_storage.playback_volume;
                                                return true;
                                            }
                                        }
                                    }catch(e){
                                        console.warn("init_audiobook_player error:", e);
                                    }
                                    return false;
                                };
                            }
                            if(typeof window.gr_ebook_textarea_counter !== "function"){
                                const max_ebook_textarea_length = __max_ebook_textarea_length__;
                                window.gr_ebook_textarea_counter = function(){
                                    const container = document.querySelector("#gr_ebook_textarea");
                                    if(container){
                                        const textarea = container.querySelector("textarea");
                                        const ebook_textarea_toolbar = document.querySelector("#ebook_textarea_toolbar");
                                        document.querySelector("#ebook_textarea_toolbar")?.remove();
                                        container.style.position = "relative";
                                        const toolbar = document.createElement("div");
                                        toolbar.id = toolbar.name = "ebook_textarea_toolbar";
                                        toolbar.style.cssText = "position:absolute;top:4px;right:8px;display:flex;align-items:center;gap:6px;z-index:1;";
                                        const counter = document.createElement("span");
                                        counter.style.cssText = "font-size:0.85em;color:var(--body-text-color);";
                                        counter.textContent = textarea.value.length + " / " + max_ebook_textarea_length;
                                        toolbar.appendChild(counter);
                                        const btn = document.createElement("button");
                                        btn.textContent = "🗑";
                                        btn.id = btn.name = "clear_ebook_textarea";
                                        btn.className = "micro-btn";
                                        btn.addEventListener("click", ()=>{
                                            textarea.value = "";
                                            textarea.dispatchEvent(new Event("input", {bubbles: true}));
                                            counter.textContent = "0 / " + max_ebook_textarea_length;
                                            counter.style.color = "var(--body-text-color)";
                                        });
                                        textarea.addEventListener("input", ()=>{
                                            const len = textarea.value.length;
                                            counter.textContent = len + " / " + max_ebook_textarea_length;
                                            counter.style.color = len >= max_ebook_textarea_length ? "red" : "var(--body-text-color)";
                                        });
                                        toolbar.appendChild(btn);
                                        container.appendChild(toolbar);
                                    }
                                };
                            }
                            if(typeof(window.tab_progress) !== "function"){
                                window.tab_progress = ()=>{
                                    try{
                                        const gr_root = (window.gradioApp && window.gradioApp()) || document;
                                        const el = gr_root.querySelector("#gr_progress");
                                        const val = el?.value || el?.textContent || "";
                                        const valArray = splitAtLastDash(val);
                                        if(valArray[1]){
                                            const title = valArray[0].trim().split(/ (.*)/)[1].trim();
                                            const percentage = valArray[1].trim();
                                            const titleShort = title.length >= 20 ? title.slice(0, 20).trimEnd() + "…" : title;
                                            document.title = titleShort + ": " + percentage;
                                        }else{
                                            document.title = "Ebook2Audiobook";
                                        }
                                    }catch(e){
                                        console.warn("tab_progress error:", e);
                                    }
                                };
                            }
                            if(typeof(splitAtLastDash) !== "function"){
                                function splitAtLastDash(s){
                                    const idx = s.lastIndexOf("-");
                                    if(idx === -1){
                                        return [s];
                                    }
                                    return [s.slice(0, idx).trim(), s.slice(idx + 1).trim()];
                                }
                            }
                            if(typeof(window.load_vtt) !== "function"){
                                window.load_vtt = ()=>{
                                    try{
                                        gr_audiobook_vtt = gr_root.querySelector("#gr_audiobook_vtt textarea");
                                        gr_audiobook_sentence = gr_root.querySelector("#gr_audiobook_sentence textarea");
                                        if(gr_audiobook_sentence){
                                            gr_audiobook_sentence.style.fontSize = "14px";
                                            gr_audiobook_sentence.style.fontWeight = "bold";
                                            gr_audiobook_sentence.style.width = "100%";
                                            gr_audiobook_sentence.style.height = "auto";
                                            gr_audiobook_sentence.style.textAlign = "center";
                                            gr_audiobook_sentence.style.margin = "0";
                                            gr_audiobook_sentence.style.padding = "7px 0 7px 0";
                                            gr_audiobook_sentence.style.lineHeight = "14px";
                                            const txt = gr_audiobook_vtt.value;
                                            if(txt == ""){
                                                gr_audiobook_sentence.value = "…";
                                            }else{
                                                parseVTT(txt);
                                            }
                                        }
                                    }catch(e){
                                        console.warn("load_vtt error:", e);
                                    }
                                };
                            }
                            if(typeof(window.parseVTT) !== "function"){
                                 window.parseVTT = (vtt)=>{
                                    function pushCue(){
                                        if(start !== null && end !== null && textBuffer.length){
                                            cues.push({ start, end, text: textBuffer.join("\n") });
                                        }
                                        start = end = null;
                                        textBuffer.length = 0;
                                    }
                                    const lines = vtt.split(/\r?\n/);
                                    const timePattern = /(\d{2}:)?\d{2}:\d{2}\.\d{3}/;
                                    let start = null, end = null;
                                    cues = [];
                                    textBuffer = [];
                                    for(let i = 0, len = lines.length; i < len; i++){
                                        const line = lines[i];
                                        if(!line.trim()){ pushCue(); continue; }
                                        if(line.includes("-->")){
                                            const [s, e] = line.split("-->").map(l => l.trim().split(" ")[0]);
                                            if(timePattern.test(s) && timePattern.test(e)){
                                                start = toSeconds(s);
                                                end = toSeconds(e);
                                            }
                                        }else if(!timePattern.test(line)){
                                            textBuffer.push(line);
                                        }
                                    }
                                    pushCue();
                                }
                            }
                            if(typeof(toSeconds) !== "function"){
                                function toSeconds(ts){
                                    const parts = ts.split(":");
                                    if(parts.length === 3){
                                        return parseInt(parts[0], 10) * 3600 +
                                               parseInt(parts[1], 10) * 60 +
                                               parseFloat(parts[2]);
                                    }
                                    return parseInt(parts[0], 10) * 60 + parseFloat(parts[1]);
                                }
                            }
                            if(typeof(findCue) !== "function"){
                                function findCue(time){
                                    let lo = 0, hi = cues.length - 1;
                                    while(lo <= hi){
                                        const mid = (lo + hi) >> 1;
                                        const cue = cues[mid];
                                        if(time < cue.start){
                                            hi = mid - 1;
                                        }else if(time >= cue.end){
                                            lo = mid + 1;
                                        }else{
                                            return cue;
                                        }
                                    }
                                    return null;
                                }
                            }
                            if(typeof(splitAtLastDash) !== "function"){
                                function splitAtLastDash(s){
                                    const idx = s.lastIndexOf("-");
                                    if(idx === -1){
                                        return [s];
                                    }
                                    return [s.slice(0, idx).trim(), s.slice(idx + 1).trim()];
                                }
                            }
                            if(typeof(show_glassmask) !== "function"){
                                function show_glassmask(msg){
                                    let glassmask = document.querySelector("#gr_glassmask");
                                    if(!glassmask){
                                        glassmask = document.createElement("div");
                                        glassmask.id = "gr_glassmask";
                                        document.body.appendChild(glassmask);
                                    }
                                    glassmask.className = "gr-glass-mask";
                                    glassmask.innerHTML = `${msg}`;
                                }
                            }
                            if(typeof(create_uuid) !== "function"){
                                function create_uuid(){
                                    try{
                                        return crypto.randomUUID();
                                    }catch(e){
                                        return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c =>{
                                            const r = Math.random() * 16 | 0;
                                            const v = c === "x" ? r : (r & 0x3 | 0x8);
                                            return v.toString(16);
                                        });
                                    }
                                }
                            }
                            //////////////////////
                            const bc = new BroadcastChannel("E2A-channel");
                            const tab_id = create_uuid();
                            bc.onmessage = (event)=>{
                                try{
                                    const msg = event.data;
                                    if(!msg || msg.senderId === tab_id){
                                        return;
                                    }
                                    switch (msg.type){
                                        case "check-existing":
                                            bc.postMessage({ type: "already-open", senderId: tab_id });
                                            break;
                                        case "already-open":
                                            tabs_open = true;
                                            break;
                                        case "new-tab-open":
                                            show_glassmask(msg.text);
                                            break;
                                    }
                                }catch(e){
                                    console.warn("bc.onmessage error:", e);
                                }
                            };
                            window.addEventListener("beforeunload", ()=>{
                                try{
                                    const newStorage = JSON.parse(localStorage.getItem("data") || "{}");
                                    if(newStorage.tab_id == window.tab_id || !newStorage.tab_id){
                                        delete newStorage.tab_id;
                                        delete newStorage.status;
                                        newStorage.playback_time = Number(window.session_storage.playback_time);
                                        newStorage.playback_volume = parseFloat(window.session_storage.playback_volume);
                                        localStorage.setItem("data", JSON.stringify(newStorage));
                                    }
                                }catch(e){
                                    console.warn("Error updating status on unload:", e);
                                }
                            });
                            window.onElementAvailable("#gr_voice_player_hidden audio", (el)=>{
                                window.init_voice_player_hidden();
                            }, {once: false});
                            window.onElementAvailable("#gr_audiobook_player audio", (el)=>{
                                window.init_audiobook_player();
                            }, {once: false});
                            if (!window._fetch_patched) {
                                const originalFetch = window.fetch;
                                window._original_fetch = window._original_fetch || originalFetch;
                                window.fetch = async function(url, options) {
                                    if (typeof url === "string" && url.includes("/upload") && options?.body instanceof FormData){
                                        let has_files = false;
                                        for(const [, value] of options.body.entries()){
                                            if(value instanceof File && value.size > 0){
                                                has_files = true;
                                                break;
                                            }
                                        }
                                        if(!has_files){
                                            console.warn("Blocked empty folder upload");
                                            return new Response(JSON.stringify([]), {
                                                status: 200,
                                                headers: {"Content-Type": "application/json"},
                                            });
                                        }
                                    }
                                    return window._original_fetch.apply(this, arguments);
                                };
                                window._fetch_patched = true;
                            }
                            try{
                                bc.postMessage({ type: "check-existing", senderId: tab_id });
                                setTimeout(()=>{
                                    if(tabs_open){
                                        bc.postMessage({
                                            type: "new-tab-open",
                                            text: "Session expired.<br/>You can close this window",
                                            senderId: tab_id
                                        });
                                    }
                                }, 250);
                            }catch(e){
                                console.warn("bc.postMessage error:", e);
                            }
                            const currentStorage = localStorage.getItem("data");
                            if(currentStorage){
                                window.session_storage = JSON.parse(currentStorage);
                                window.session_storage.tab_id = tab_id;
                                if(window.session_storage.playback_volume === 0){
                                    window.session_storage.playback_volume = 1.0;
                                }
                            }else{
                                window.session_storage = {};
                                window.session_storage.playback_time = 0;
                                window.session_storage.playback_volume = 1.0;
                            }
                            return window.session_storage;
                        }catch(e){
                            console.warn("gr_raed_data js error:", e);
                        }
                        return null;
                    }
                '''.replace('__max_ebook_textarea_length__', str(max_ebook_textarea_length)),
                outputs=[gr_restore_session],
            )
            app.unload(on_unload)
            all_ips = get_all_ip_addresses()
            msg = f'IPs available for connection:\n{all_ips}\nNote: 0.0.0.0 is not the IP to connect. Instead use an IP above to connect and port {interface_port}'
            show_alert(None, {"type": "info", "msg": msg})
            os.environ['no_proxy'] = ' ,'.join(all_ips)
            return app
    except Exception as e:
        error = f'An unexpected error occurred: {e}'
        exception_alert(None, error)
    return None
