from lib.core import *
from lib.classes.tts_engines.common.preset_loader import load_engine_presets

def build_interface(args:dict)->gr.Blocks:
    try:
        script_mode = args['script_mode']
        is_gui_process = args['is_gui_process']
        is_gui_shared = args['share']
        title = 'Ebook2Audiobook'
        gr_glassmask_msg = 'Initialization, please wait...'
        models = None
        ebook_src = None
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
        src_label_file = 'Upload File'
        src_label_dir = 'Select a Directory'
        confirm_blocks = 'confirm_blocks'
        page_size = 15
        visible_gr_tab_xtts_params = interface_component_options['gr_tab_xtts_params']
        visible_gr_tab_bark_params = interface_component_options['gr_tab_bark_params']
        visible_gr_group_custom_model = interface_component_options['gr_group_custom_model']
        visible_gr_group_voice_file = interface_component_options['gr_group_voice_file']
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
                .small-btn:active, .small-btn-red:active {
                    background: var(--body-text-color) !important;
                    font-size: 30px !important;
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
                ////////////////////
                #gr_ebook_file, #gr_custom_model_file, #gr_voice_file {
                    height: 100px !important;
                    min-height: 100px !important;
                    max-height: 100px !important;
                    display: flex  !important;
                    align-items: center !important;
                    justify-content: center !important;
                }
                #gr_ebook_file label, #gr_custom_model_file label, #gr_voice_file label {
                    background: none !important;
                    border: none !important;
                }
                #gr_audiobook_player label {
                    display: none !important;
                }
                #gr_ebook_file button>div, #gr_custom_model_file button>div, #gr_voice_file button>div {
                    font-size: 12px !important;
                }
                #gr_ebook_file .empty, #gr_custom_model_file .empty, #gr_voice_file .empty,
                #gr_ebook_file .wrap, #gr_custom_model_file .wrap, #gr_voice_file .wrap {
                    height: 100% !important;
                    min-height: 100px !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
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
                #gr_chapters_preview {
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
                #gr_row_voice_player, #gr_row_custom_model_list, #gr_row_audiobook_list {
                    height: 60px !important;
                }
                #gr_audiobook_player :is(.volume, .empty, .source-selection, .control-wrapper, .settings-wrapper, label) {
                    display: none !important;
                }
                #gr_audiobook_files label[data-testid="block-label"] {
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
                #gr_blocks_nav button.nav-btn {
                    width: 44px !important;
                    min-width: 44px !important;
                    max-width: 44px !important;
                    padding: 0 !important;
                }
                #gr_blocks_nav .nav-header {
                    text-align: center;
                    margin: 0;
                    padding-top: 6px;
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
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5) !important;
                    border: 2px solid #FFA500 !important;
                    color: white !important;
                    position: relative !important;
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
                with gr.Tabs(elem_id='gr_tabs'):
                    gr_tab_main = gr.Tab('Dashboard', elem_id='gr_tab_main', elem_classes='gr-tab')
                    with gr_tab_main:
                        with gr.Row(elem_id='gr_row_tab_main'):
                            with gr.Column(elem_id='gr_col_1', elem_classes=['gr-col'], scale=3):
                                with gr.Group(elem_id='gr_group_ebook_file', elem_classes=['gr-group']):
                                    gr_import_markdown = gr.Markdown(elem_id='gr_import_markdown', elem_classes=['gr-markdown'], value='Import')
                                    gr_ebook_file = gr.File(label=src_label_file, elem_id='gr_ebook_file', file_types=ebook_formats, file_count='single', allow_reordering=True, height=100)
                                    gr_row_ebook_mode = gr.Row(elem_id='gr_row_ebook_mode')
                                    with gr_row_ebook_mode:
                                        gr_ebook_mode = gr.Dropdown(label='', elem_id='gr_ebook_mode', choices=[('File','single'), ('Directory','directory')], interactive=True, scale=2)
                                        gr_chapters_preview = gr.Checkbox(label='Chapters Preview', elem_id='gr_chapters_preview', value=False, interactive=True, scale=1)
                                with gr.Group(elem_id='gr_group_language', elem_classes=['gr-group']):
                                    gr_language_markdown = gr.Markdown(elem_id='gr_language_markdown', elem_classes=['gr-markdown'], value='Language')
                                    gr_language = gr.Dropdown(label='', elem_id='gr_language', choices=language_options, value=default_language_code, type='value', interactive=True)
                                gr_group_voice_file = gr.Group(elem_id='gr_group_voice_file', elem_classes=['gr-group'], visible=visible_gr_group_voice_file)
                                with gr_group_voice_file:
                                    gr_voice_markdown = gr.Markdown(elem_id='gr_voice_markdown', elem_classes=['gr-markdown'], value='Voices')
                                    gr_voice_file = gr.File(label='Upload Voice', elem_id='gr_voice_file', file_types=voice_formats, value=None, height=100)
                                    gr_row_voice_player = gr.Row(elem_id='gr_row_voice_player')
                                    with gr_row_voice_player:
                                        gr_voice_player_hidden = gr.Audio(elem_id='gr_voice_player_hidden', type='filepath', interactive=False, waveform_options=gr.WaveformOptions(show_recording_waveform=False), show_download_button=False, container=False, visible='hidden', show_share_button=True, show_label=False, scale=0, min_width=60)
                                        gr_voice_play = gr.Button('▶', elem_id='gr_voice_play', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                        gr_voice_list = gr.Dropdown(label='Voices', elem_id='gr_voice_list', choices=voice_options, type='value', interactive=True, scale=2)
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
                                        gr_custom_model_file = gr.File(label=f"Upload ZIP File", elem_id='gr_custom_model_file', value=None, file_types=['.zip'], height=100)
                                        gr_row_custom_model_list = gr.Row(elem_id='gr_row_custom_model_list')
                                        with gr_row_custom_model_list:
                                            gr_custom_model_list = gr.Dropdown(label='', elem_id='gr_custom_model_list', choices=custom_model_options, type='value', interactive=True, scale=2)
                                            gr_custom_model_del_btn = gr.Button('🗑', elem_id='gr_custom_model_del_btn', elem_classes=['small-btn'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
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
                                    gr_session = gr.Textbox(label='', elem_id='gr_session', interactive=False)
                            
                    gr_tab_xtts_params = gr.Tab('XTTSv2 Settings', elem_id='gr_tab_xtts_params', elem_classes='gr-tab', visible=visible_gr_tab_xtts_params)           
                    with gr_tab_xtts_params:
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
                    gr_tab_bark_params = gr.Tab('Bark Settings', elem_id='gr_tab_bark_params', elem_classes='gr-tab', visible=visible_gr_tab_bark_params)           
                    with gr_tab_bark_params:
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
                gr_group_audiobook_list = gr.Group(elem_id='gr_group_audiobook_list', elem_classes=['gr-group-sides-padded'], visible=True)
                with gr_group_audiobook_list:
                    gr_audiobook_markdown = gr.Markdown(elem_id='gr_audiobook_markdown', elem_classes=['gr-markdown'], value='Audiobook')
                    gr_audiobook_vtt = gr.Textbox(elem_id='gr_audiobook_vtt', label='', interactive=False, visible='hidden')
                    gr_playback_time = gr.Number(elem_id="gr_playback_time", label='', interactive=False, visible='hidden', value=0.0)
                    gr_audiobook_sentence = gr.Textbox(elem_id='gr_audiobook_sentence', label='', value='...', interactive=False, lines=3, max_lines=3)
                    gr_audiobook_player = gr.Audio(elem_id='gr_audiobook_player', label='', type='filepath', autoplay=False, interactive=False, waveform_options=gr.WaveformOptions(show_recording_waveform=False), show_download_button=False, show_share_button=False, container=True, visible=True)
                    gr_row_audiobook_list = gr.Row(elem_id='gr_row_audiobook_list', visible=True)
                    with gr_row_audiobook_list:
                        gr_audiobook_download_btn = gr.Button(elem_id='gr_audiobook_download_btn', value='↧', elem_classes=['small-btn'], variant='secondary', interactive=True, scale=0, min_width=60)
                        gr_audiobook_list = gr.Dropdown(elem_id='gr_audiobook_list', label='', choices=audiobook_options, type='value', interactive=True, scale=2)
                        gr_audiobook_del_btn = gr.Button(elem_id='gr_audiobook_del_btn', value='🗑', elem_classes=['small-btn-red'], variant='secondary', interactive=True, scale=0, min_width=60)
                    gr_audiobook_files = gr.Files(label='', elem_id='gr_audiobook_files', visible=False)
                    gr_audiobook_files_toggled = gr.State(False)
                with gr.Group(elem_id='gr_convert_btn', elem_classes=['gr-group-convert-btn']):
                    gr_convert_btn = gr.Button(elem_id='gr_convert_btn', value='📚', elem_classes='gr-convert-btn', variant='primary', interactive=False)

            gr_version_markdown = gr.Markdown(elem_id='gr_version_markdown', value=f'''
                <div style="right:0;margin:auto;padding:10px;text-align:center">
                    <a href="https://github.com/DrewThomasson/ebook2audiobook" style="text-decoration:none;font-size:14px" target="_blank">
                    <b>{title}</b>&nbsp;<b style="color:orange; text-shadow: 0.3px 0.3px 0.3px #303030">{prog_version}</b></a>
                </div>
                '''
            )

            gr_blocks_page = gr.State(0)
            gr_blocks_data = gr.State([])
            gr_blocks_keep = gr.State({})
            gr_blocks_text = gr.State({})
            gr_blocks_open = gr.State({})
            gr_blocks_panel = gr.Column(visible=False)
            with gr_blocks_panel:
                gr_blocks_nav = gr.Row(elem_id='gr_blocks_nav')
                with gr_blocks_nav:
                    gr_blocks_prev = gr.Button('◀', elem_classes=['nav-btn'], scale=0, min_width=44)
                    gr_blocks_header = gr.Markdown('', elem_classes=['nav-header'])
                    gr_blocks_next = gr.Button('▶', elem_classes=['nav-btn'], scale=0, min_width=44)
                gr_blocks_cancel = gr.Button('✖', variant='stop')
                gr_blocks_continue = gr.Button('✔', variant='primary')

            gr_modal = gr.HTML(visible=False)
            gr_glassmask = gr.HTML(gr_glassmask_msg, elem_id='gr_glassmask', elem_classes=['gr-glass-mask'])
            gr_confirm_deletion_field_hidden = gr.Textbox(elem_id='confirm_hidden', visible=False)
            gr_confirm_deletion_no_btn = gr.Button(elem_id='gr_confirm_deletion_no_btn', elem_classes=['hide-elem'], value='✖', variant='stop', visible=True, scale=0, size='sm',  min_width=0)
            gr_confirm_deletion_yes_btn = gr.Button(elem_id='gr_confirm_deletion_yes_btn', elem_classes=['hide-elem'], value='✔', variant='primary', visible=True, scale=0, size='sm', min_width=0)
            gr_session_update = gr.State(value={'hash': None})
            gr_restore_session = gr.JSON(elem_id='gr_restore_session', visible='hidden')
            gr_save_session = gr.JSON(elem_id='gr_save_session', visible='hidden')

            def disable_components()->tuple:
                outputs = tuple([gr.update(interactive=False) for _ in range(12)])
                return outputs
            
            def enable_components(session_id:str)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    outputs = tuple([gr.update(interactive=True) for _ in range(12)])
                    return outputs
                outputs = tuple([gr.update() for _ in range(12)])
                return outputs
                
            def disable_on_voice_upload()->tuple:
                return (
                    gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False),
                    gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False),
                    gr.update(visible='hidden'),
                    gr.update(visible='hidden')
                )
            
            def enable_on_voice_upload(session_id: str) -> tuple:
                session = context.get_session(session_id)
                outputs = tuple([gr.update(interactive=False) for _ in range(10)])
                if session and session.get('id', False):
                    visible = True if session['voice'] is not None else 'hidden'
                    convert_btn_enabled = True if session['ebook'] is not None else False
                    return (
                        gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True),
                        gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=convert_btn_enabled),
                        gr.update(visible=visible),
                        gr.update(visible=visible)
                    )
                return outputs

            def disable_on_custom_upload()->tuple:
                return (
                    gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False),
                    gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False), gr.update(visible='hidden')
                )
            
            def enable_on_custom_upload(session_id:str)->tuple:
                session = context.get_session(session_id)
                outputs = tuple([gr.update(interactive=False) for _ in range(8)])
                if session and session.get('id', False):
                    convert_btn_enabled = True if session['ebook'] is not None else False
                    custom_del_btn_visible = True if session['custom_model'] is not None else 'hidden'
                    return (
                        gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True),
                        gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=convert_btn_enabled), gr.update(visible=custom_del_btn_visible)
                    )
                return outputs

            def show_gr_modal(type:str, msg:str)->str:
                return f'''
                <div id="custom-gr_modal" class="gr-modal">
                    <div class="gr-modal-content">
                        <p style="color:#ffffff">{msg[:70]}...</p>            
                        {show_confirm_buttons(type)}
                    </div>
                </div>
                '''

            def show_confirm_buttons(mode:str)->str:
                if mode in ['confirm_deletion']:
                    button_yes = f'#gr_{mode}_yes_btn'
                    button_no = f'#gr_{mode}_no_btn'
                    return f'''
                    <div class="confirm-buttons">
                        <button class="button-red" style="width:50px; height:50px" onclick="document.querySelector('{button_no}').click()">⨉</button>
                        <button class="button-green" style="width:50px; height:50px" onclick="document.querySelector('{button_yes}').click()">✔</button>
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
                gradio_cache_root = os.path.normpath(os.path.join(tmp_dir, 'gradio'))
                if not path or not os.path.isfile(path):
                    return False
                path = os.path.normpath(path)
                parent = os.path.dirname(path)
                return (
                    parent.startswith(gradio_cache_root) and
                    len(os.path.basename(parent)) >= 32
                )

            def restore_interface(session_id:str, req:gr.Request)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        socket_hash = str(req.session_hash)
                        if not session.get(socket_hash):
                            outputs = tuple([gr.update() for _ in range(16)])
                            return outputs
                        ebook_data = None
                        file_count = session['ebook_mode']
                        if session['ebook_list'] is not None and file_count == 'directory':
                            session['ebook'] = None
                            ebook_data = [f for f in session['ebook_list'] if os.path.exists(f)]
                            if not ebook_data:
                                ebook_data = None
                        elif isinstance(session['ebook'], str) and file_count == 'single':
                            if os.path.exists(session['ebook']):
                                ebook_data = session['ebook']
                            else:
                                ebook_data = session['ebook'] = None
                        else:
                            ebook_data = session['ebook'] = None
                        if ebook_data is not None:
                            if isinstance(ebook_data, list):
                                ebook_data = [f for f in ebook_data if is_valid_gradio_cache(f)]
                                if not ebook_data:
                                    ebook_data = None
                            else:
                                if not is_valid_gradio_cache(ebook_data):
                                    ebook_data = None
                        session['ebook'] = ebook_data
                        visible_gr_row_split_hours = True if session['output_split'] else False
                        visible_gr_group_custom_model = True if session['fine_tuned'] == 'internal' and session['tts_engine'] in [TTS_ENGINES['XTTSv2']] else False
                        return (
                            gr.update(value=session['ebook']),
                            gr.update(value=session['ebook_mode']),
                            gr.update(value=bool(session['chapters_preview'])),
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
                            gr.update(visible=visible_gr_row_split_hours),
                            update_gr_audiobook_list(session_id),
                            gr.update(visible=visible_gr_group_custom_model)
                        )
                except Exception as e:
                    error = f'restore_interface(): {e}'
                    alert_exception(error, session_id)
                outputs = tuple([gr.update() for _ in range(16)])
                return outputs

            def restore_audiobook_player(audiobook:str|None)->tuple:
                try:
                    visible = True if audiobook is not None else False
                    return gr.update(visible=visible), gr.update(value=audiobook), gr.update(active=True)
                except Exception as e:
                    error = f'restore_audiobook_player(): {e}'
                    alert_exception(error, None)
                    outputs = tuple([gr.update() for _ in range(3)])
                    return outputs

            def refresh_interface(session_id:str)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    return (
                        gr.update(interactive=False), gr.update(value=session['ebook']), gr.update(value=session['device']), update_gr_audiobook_list(session_id), 
                        gr.update(value=session['audiobook']), gr.update(visible=False), update_gr_voice_list(session_id), gr.update(value='')
                    )
                outputs = tuple([gr.update() for _ in range(8)])
                return outputs

            def change_gr_audiobook_list(selected:str|None, session_id:str)->dict:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        session['audiobook'] = selected
                        group_visible = True if session['audiobook'] else False
                        return gr.update(visible=group_visible)
                except Exception as e:
                    error = f'change_gr_audiobook_list(): {e}'
                    alert_exception(error, session_id)
                return gr.update(visible=False)

            def update_gr_audiobook_player(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session['audiobook'] is not None: 
                            vtt = Path(session['audiobook']).with_suffix('.vtt')
                            if not os.path.exists(session['audiobook']) or not os.path.exists(vtt):
                                error = f"{Path(session['audiobook']).name} does not exist!"
                                print(error)
                                alert_exception(error, session_id)
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
                                print(error)
                                alert_exception(error, session_id)
                except Exception as e:
                    error = f'update_gr_audiobook_player(): {e}'
                    print(error)
                    alert_exception(error, session_id)
                return gr.update(value=0.0), gr.update(value=None), gr.update(value=None)

            def update_gr_glassmask(str:str=gr_glassmask_msg, attr:list=['gr-glass-mask'])->dict:
                return gr.update(value=str, elem_id='gr_glassmask', elem_classes=attr)

            def change_convert_btn(upload_file:str|None=None, upload_file_mode:str|None=None, custom_model_file:str|None=None, session:DictProxy=None)->dict:
                try:
                    if session is None:
                        return gr.update(variant='primary', interactive=False)
                    else:
                        if hasattr(upload_file, 'name') and not hasattr(custom_model_file, 'name'):
                            return gr.update(variant='primary', interactive=True)
                        elif isinstance(upload_file, list) and len(upload_file) > 0 and upload_file_mode == 'directory' and not hasattr(custom_model_file, 'name'):
                            return gr.update(variant='primary', interactive=True)
                        else:
                            return gr.update(variant='primary', interactive=False)
                except Exception as e:
                    error = f'change_convert_btn(): {e}'
                    alert_exception(error, None)
                    gr.update()

            def change_gr_ebook_file(data:str|None, session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        session['ebook'] = None
                        session['ebook_list'] = None
                        if data is None:
                            if session.get("status") == "converting":
                                session['cancellation_requested'] = True
                                msg = "Cancellation requested, please wait..."
                                yield gr.update(value=show_gr_modal("wait", msg), visible=True)
                                return
                        if isinstance(data, list):
                            ebook_list = []
                            for f in data:
                                path = f.get("path") if isinstance(f, dict) else str(f)
                                ebook_list.append(path)
                            session['ebook_list'] = ebook_list
                        else:
                            session['ebook'] = data
                        session['cancellation_requested'] = False
                        return gr.update(value='', visible=False)
                except Exception as e:
                    error = f'change_gr_ebook_file(): {e}'
                    alert_exception(error, session_id)
                return gr.update(value='', visible=False)

            def change_gr_ebook_mode(val:str, session_id:str)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['ebook_mode'] = val
                    if val == 'single':
                        return gr.update(label=src_label_file, file_count='single'), gr.update(visible=True)
                    else:
                        return gr.update(label=src_label_dir, file_count='directory'), gr.update(visible=False)
                return gr.update(), gr.update()

            def change_gr_voice_file(f:str|None, session_id:str)->tuple:
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
                                show_alert(state)
                                return update_gr_voice_list(session_id)
                            else:
                                error = 'failed! Check if you audio file is compatible.'
                                state['type'] = 'warning'
                                state['msg'] = error
                    show_alert(state)
                return gr.update()

            def change_gr_voice_list(selected:str|None, session_id:str)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if not voice_options:
                        session['voice'] = None
                    else:
                        voice_value = voice_options[0][1]
                        session['voice'] = next(
                            (value for label, value in voice_options if value == selected),
                            voice_value,
                        )
                    visible = session['voice'] is not None
                    return gr.update(value=session['voice']), gr.update(visible=visible), gr.update(visible=visible)
                return gr.update(), gr.update(), gr.update()
                
            def click_gr_voice_del_btn(selected:str, session_id:str)->tuple:
                try:
                    if selected is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            speaker_path = os.path.abspath(selected)
                            speaker = re.sub(r'\.wav$|\.npz|\.pth$', '', os.path.basename(selected))
                            builtin_root = os.path.join(voices_dir, session['language'])
                            is_in_builtin = os.path.commonpath([speaker_path, os.path.abspath(builtin_root)]) == os.path.abspath(builtin_root)
                            is_in_models = os.path.commonpath([speaker_path, os.path.abspath(session['custom_model_dir'])]) == os.path.abspath(session['custom_model_dir'])
                            # Check if voice is built-in
                            is_builtin = any(
                                speaker in settings.get('voices', {})
                                for settings in (default_engine_settings[engine] for engine in TTS_ENGINES.values())
                            )
                            if is_builtin and is_in_builtin:
                                error = f'Voice file {speaker} is a builtin voice and cannot be deleted.'
                                show_alert({"type": "warning", "msg": error})
                                return gr.update(), gr.update(visible=False)
                            if is_in_models:
                                error = f'Voice file {speaker} is a voice of one of your custom model and cannot be deleted.'
                                show_alert({"type": "warning", "msg": error})
                                return gr.update(), gr.update(visible=False)                          
                            try:
                                selected_path = Path(selected).resolve()
                                parent_path = Path(session['voice_dir']).parent.resolve()
                                if parent_path in selected_path.parents:
                                    msg = f'Are you sure to delete {speaker}...'
                                    return (
                                        gr.update(value='confirm_voice_del'),
                                        gr.update(value=show_gr_modal('confirm_deletion', msg), visible=True)
                                    )
                                else:
                                    error = f'{speaker} is part of the global voices directory. Only your own custom uploaded voices can be deleted!'
                                    show_alert({"type": "warning", "msg": error})
                                    return gr.update(), gr.update(visible=False)
                            except Exception as e:
                                error = f'Could not delete the voice file {selected}!\n{e}'
                                alert_exception(error, session_id)
                                return gr.update(), gr.update(visible=False)
                    # Fallback/default return if not selected or after errors
                    return gr.update(), gr.update(visible=False)
                except Exception as e:
                    error = f'click_gr_voice_del_btn(): {e}'
                    alert_exception(error, session_id)
                    return gr.update(), gr.update(visible=False)

            def click_gr_custom_model_del_btn(selected:str, session_id:str)->tuple:
                try:
                    if selected is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            selected_name = os.path.basename(selected)
                            msg = f'Are you sure to delete {selected_name}...'
                            return gr.update(value='confirm_custom_model_del'), gr.update(value=show_gr_modal('confirm_deletion', msg), visible=True)
                except Exception as e:
                    error = f'Could not delete the custom model {selected_name}!'
                    alert_exception(error, session_id)
                return gr.update(), gr.update(visible=False)

            def click_gr_audiobook_del_btn(selected:str, session_id:str)->tuple:
                try:
                    if selected is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            selected_name = Path(selected).stem
                            msg = f'Are you sure to delete {selected_name}...'
                            return gr.update(value='confirm_audiobook_del'), gr.update(value=show_gr_modal('confirm_deletion', msg), visible=True)
                except Exception as e:
                    error = f'Could not delete the audiobook {selected_name}!'
                    alert_exception(error, session_id)
                return gr.update(), gr.update(visible=False), gr.update(visible=False)

            def confirm_deletion(voice_path:str, custom_model:str, audiobook:str, session_id:str, method:str|None=None)->tuple:
                try:
                    nonlocal models
                    if method is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            models = load_engine_presets(session['tts_engine'])
                            if method == 'confirm_voice_del':
                                selected_name = Path(voice_path).stem
                                pattern = re.sub(r'\.wav$', '*.wav', voice_path)
                                files2remove = glob(pattern)
                                for file in files2remove:
                                    os.remove(file)
                                shutil.rmtree(os.path.join(os.path.dirname(voice_path), 'bark', selected_name), ignore_errors=True)
                                msg = f"Voice file {re.sub(r'.wav$', '', selected_name)} deleted!"
                                session['voice'] = None
                                show_alert({"type": "warning", "msg": msg})
                                return gr.update(), gr.update(), gr.update(value='', visible=False), update_gr_voice_list(session_id)
                            elif method == 'confirm_custom_model_del':
                                selected_name = os.path.basename(custom_model)
                                shutil.rmtree(custom_model, ignore_errors=True)                           
                                msg = f'Custom model {selected_name} deleted!'
                                if session['custom_model'] is not None and session['voice'] is not None:
                                    if session['custom_model'] in session['voice']:
                                        session['voice'] = models[session['fine_tuned']]['voice']
                                session['custom_model'] = None
                                show_alert({"type": "warning", "msg": msg})
                                return update_gr_custom_model_list(session_id), gr.update(), gr.update(value='', visible=False), gr.update()
                            elif method == 'confirm_audiobook_del':
                                selected_name = Path(audiobook).stem
                                if os.path.isdir(audiobook):
                                    shutil.rmtree(selected, ignore_errors=True)
                                elif os.path.exists(audiobook):
                                    os.remove(audiobook)
                                vtt_path = Path(audiobook).with_suffix('.vtt')
                                if os.path.exists(vtt_path):
                                    os.remove(vtt_path)
                                process_dir = os.path.join(session['session_dir'], f"{hashlib.md5(os.path.join(session['audiobooks_dir'], audiobook).encode()).hexdigest()}")
                                shutil.rmtree(process_dir, ignore_errors=True)
                                msg = f'Audiobook {selected_name} deleted!'
                                session['audiobook'] = None
                                show_alert({"type": "warning", "msg": msg})
                                return gr.update(), update_gr_audiobook_list(session_id), gr.update(value='', visible=False), gr.update()
                except Exception as e:
                    error = f'confirm_deletion(): {e}!'
                    alert_exception(error, session_id)
                return gr.update(), gr.update(), gr.update(value='', visible=False), gr.update()

            def update_gr_voice_list(session_id:str)->dict:
                try:
                    nonlocal voice_options
                    nonlocal models
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
                        session['voice_dir'] = os.path.join(voices_dir, '__sessions', f"voice-{session['id']}", session['language'])
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
                        if session['tts_engine'] in [TTS_ENGINES['VITS'], TTS_ENGINES['FAIRSEQ'], TTS_ENGINES['TACOTRON2'], TTS_ENGINES['YOURTTS']]:
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
                    alert_exception(error, session_id)
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
                    alert_exception(error, session_id)              
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
                    alert_exception(error, session_id)
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
                    alert_exception(error, session_id)              
                return gr.update()

            def change_gr_device(selected:str, session_id:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['device'] = selected

            def change_gr_language(selected:str, session_id:str)->tuple:
                if selected:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
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

            def change_gr_custom_model_file(custom_file:str|None, tts_engine:str, session_id:str)->tuple:
                nonlocal models
                if custom_file is not None:
                    state = {}
                    if len(custom_model_options) > max_custom_model:
                        error = f'You are allowed to upload a max of {max_custom_models} models'   
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
                                    session['voice'] = os.path.join(model, f'{os.path.basename(os.path.normpath(model))}.wav')
                                    msg = f'{os.path.basename(model)} added to the custom models list'
                                    state['type'] = 'success'
                                    state['msg'] = msg
                                    show_alert(state)
                                    return gr.update(value=None), update_gr_custom_model_list(session_id)
                                else:
                                    error = f'Cannot extract custom model zip file {os.path.basename(custom_file)}'
                                    state['type'] = 'warning'
                                    state['msg'] = error
                            else:
                                error = f'{os.path.basename(custom_file)} is not a valid model or some required files are missing'
                                state['type'] = 'warning'
                                state['msg'] = error
                    show_alert(state)
                return gr.update(value=None), gr.update()

            def change_gr_tts_engine_list(engine:str, session_id:str)->tuple:
                nonlocal models
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    models = load_engine_presets(engine)
                    session['tts_engine'] = engine
                    session['fine_tuned'] = default_fine_tuned
                    session['voice'] = None if engine not in [TTS_ENGINES['XTTSv2'], TTS_ENGINES['BARK']] else session['voice']
                    visible_bark = False
                    visible_xtts = False
                    if session['tts_engine'] == TTS_ENGINES['XTTSv2']:
                        visible_custom_model = True if session['fine_tuned'] == 'internal' else False
                        visible_xtts = visible_gr_tab_xtts_params
                        return (
                            gr.update(value=show_rating(session['tts_engine'])), 
                            gr.update(visible=visible_xtts),
                            gr.update(visible=False),
                            gr.update(visible=visible_custom_model),
                            update_gr_fine_tuned_list(session_id),
                            gr.update(label=f"Upload {session['tts_engine']} ZIP file (Mandatory: {', '.join(models[default_fine_tuned]['files'])})"),
                            gr.update(value=f"My {session['tts_engine']} Custom Models")
                        )
                    else:
                        if session['tts_engine'] == TTS_ENGINES['BARK']:
                            visible_bark = visible_gr_tab_bark_params
                        return (
                            gr.update(value=show_rating(session['tts_engine'])),
                            gr.update(visible=False),
                            gr.update(visible=visible_bark), 
                            gr.update(visible=False),
                            update_gr_fine_tuned_list(session_id),
                            gr.update(label=f"*Upload Custom Model not available for {session['tts_engine']}"),
                            gr.update(value='')
                        )
                outputs = tuple([gr.update(interactive=False) for _ in range(7)])
                return outputs

            def change_gr_fine_tuned_list(selected:str, session_id:str)->tuple:
                if selected:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        session['fine_tuned'] = selected
                        if selected == 'internal':
                            visible_custom_model = visible_gr_group_custom_model
                        else:
                            visible_custom_model = False
                            session['voice'] = models[session['fine_tuned']]['voice']
                        return gr.update(visible=visible_custom_model)
                return gr.update()

            def change_gr_custom_model_list(selected:str|None, session_id:str)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['custom_model'] = selected
                    if selected is not None:
                        session['voice'] = os.path.join(selected, f"{os.path.basename(selected)}.wav")
                    visible_fine_tuned = True if selected is None else False
                    visible_del_btn = False if selected is None else True
                    return gr.update(visible=visible_fine_tuned), gr.update(visible=visible_del_btn), update_gr_voice_list(session_id)
                return gr.update(), gr.update(), gr.update()

            def change_gr_output_format_list(val:str, session_id:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['output_format'] = val
                return

            def change_gr_output_channel_list(val:str, session_id:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['output_channel'] = val
                return
                
            def change_gr_output_split(val:str, session_id:str)->dict:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['output_split'] = val
                return gr.update(visible=val)

            def change_gr_playback_time(time:float, session_id:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['playback_time'] = time
                return

            def toggle_audiobook_files(audiobook:str, is_visible:bool)->tuple:
                if not audiobook:
                    error = 'No audiobook selected.'
                    alert_exception(error, None)
                    return gr.update(), False
                if is_visible:
                    return gr.update(visible=False, value=None), False
                p = Path(audiobook)
                if not p.exists():
                    error = f'Audio not found: {p}'
                    alert_exception(error, None)
                    return gr.update(), False
                files = [str(p)]
                vtt = p.with_suffix(".vtt")
                if vtt.exists():
                    files.append(str(vtt))
                return gr.update(visible=True, value=files), True

            def change_param(key:str, val:Any, session_id:str, val2:Any=None)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session[key] = val
                    state = {}
                    if key == "chapters_preview":
                        msg = 'Chapters preview feature will be available to the next version'   
                        state['type'] = 'info'
                        state['msg'] = msg
                        show_alert(state)
                    elif key == 'xtts_length_penalty':
                        if val2 is not None:
                            if float(val) > float(val2):
                                error = 'Length penalty must be always lower than num beams if greater than 1.0 or equal if 1.0'   
                                state['type'] = 'warning'
                                state['msg'] = error
                                show_alert(state)
                    elif key == 'xtts_num_beams':
                        if val2 is not None:
                            if float(val) < float(val2):
                                error = 'Num beams must be always higher than length penalty or equal if its value is 1.0'   
                                state['type'] = 'warning'
                                state['msg'] = error
                                show_alert(state)

            def submit_convert_btn(
                    session_id:str, device:str, ebook_file:str, chapters_preview:bool, tts_engine:str, language:str, voice:str, custom_model:str, fine_tuned:str, output_format:str, output_channel:str, xtts_temperature:float, 
                    xtts_length_penalty:int, xtts_num_beams:int, xtts_repetition_penalty:float, xtts_top_k:int, xtts_top_p:float, xtts_speed:float, xtts_enable_text_splitting:bool, bark_text_temp:float, bark_waveform_temp:float,
                    output_split:bool, output_split_hours:str
                )->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        args = {
                            "id": session_id,
                            "is_gui_process": session['is_gui_process'],
                            "script_mode": script_mode,
                            "chapters_preview": chapters_preview,
                            "device": device,
                            "tts_engine": tts_engine,
                            "ebook": ebook_file if isinstance(ebook_file, str) else None,
                            "ebook_list": ebook_file if isinstance(ebook_file, list) else None,
                            "audiobooks_dir": session['audiobooks_dir'],
                            "voice": voice,
                            "language": language,
                            "custom_model": custom_model,
                            "fine_tuned": fine_tuned,
                            "output_format": output_format,
                            "output_channel": output_channel,
                            "xtts_temperature": float(xtts_temperature),
                            "xtts_length_penalty": float(xtts_length_penalty),
                            "xtts_num_beams": int(session['xtts_num_beams']),
                            "xtts_repetition_penalty": float(xtts_repetition_penalty),
                            "xtts_top_k": int(xtts_top_k),
                            "xtts_top_p": float(xtts_top_p),
                            "xtts_speed": float(xtts_speed),
                            "xtts_enable_text_splitting": bool(xtts_enable_text_splitting),
                            "bark_text_temp": float(bark_text_temp),
                            "bark_waveform_temp": float(bark_waveform_temp),
                            "output_split": bool(output_split),
                            "output_split_hours": output_split_hours,
                            "event": None
                        }
                        error = None
                        if args['ebook'] is None and args['ebook_list'] is None:
                            error = 'Error: a file or directory is required.'
                            show_alert({"type": "warning", "msg": error})
                        elif args['xtts_num_beams'] < args['xtts_length_penalty']:
                            error = 'Error: num beams must be greater or equal than length penalty.'
                            show_alert({"type": "warning", "msg": error})                   
                        else:
                            session['status'] = 'converting'
                            session['ticker'] = len(audiobook_options)
                            if isinstance(args['ebook_list'], list):
                                args['chapters_preview'] = None
                                ebook_list = args['ebook_list'][:]
                                for file in ebook_list:
                                    if any(file.endswith(ext) for ext in ebook_formats):
                                        print(f'Processing eBook file: {os.path.basename(file)}')
                                        args['ebook'] = file
                                        progress_status, passed = convert_ebook(args)
                                        if passed is False:
                                            if session['status'] == 'converting':
                                                error = 'Conversion cancelled.'
                                                break
                                            else:
                                                error = 'Conversion failed.'
                                                break
                                        else:
                                            show_alert({"type": "success", "msg": progress_status})
                                            args['ebook_list'].remove(file)
                                            reset_session(args['id'])
                                            count_file = len(args['ebook_list'])
                                            if count_file > 0:
                                                msg = f"{os.path.basename(file)} / converted. {len(args['ebook_list'])} ebook(s) conversion remaining..."
                                                yield gr.update(value=msg)
                                            else:
                                                msg = 'Conversion successful!'
                                                session['ebook'] = None
                                                session['ebook_list'] = None
                                                session['status'] = 'ready'
                                                return gr.update(value=msg)
                            else:
                                print(f"Processing eBook file: {os.path.basename(args['ebook'])}")
                                progress_status, passed = convert_ebook(args)
                                if passed is False:
                                    if session['status'] == 'converting':
                                        error = 'Conversion cancelled.'
                                    else:
                                        error = 'Conversion failed.'
                                else:
                                    if progress_status == confirm_blocks:
                                        session['status'] = progress_status
                                        msg = 'Select the blocks to convert'
                                        print(msg)
                                        return gr.update(value=msg)
                                    else:
                                        show_alert({"type": "success", "msg": progress_status})
                                        reset_session(args['id'])
                                        session['ebook'] = None
                                        session['status'] = 'ready'
                                        msg = 'Conversion successful!'
                                        return gr.update(value=msg)
                        if error is not None:
                            show_alert({"type": "warning", "msg": error})
                        session['status'] = 'ready'
                except Exception as e:
                    error = f'submit_convert_btn(): {e}'
                    alert_exception(error, session_id)
                    session['status'] = 'ready'
                return gr.update()

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
                        audiobook_options.sort(
                            key=lambda x: os.path.getmtime(x[1]),
                            reverse=True
                        )
                        session['audiobook'] = (
                            session['audiobook']
                            if session['audiobook'] in [option[1] for option in audiobook_options]
                            else None
                        )
                        if len(audiobook_options) > 0:
                            if session['audiobook'] is not None:
                                return gr.update(choices=audiobook_options, value=session['audiobook'])
                            else:
                                return gr.update(choices=audiobook_options, value=audiobook_options[0][1])
                        else:
                            return gr.update(choices=audiobook_options, value=None)
                except Exception as e:
                    error = f'update_gr_audiobook_list(): {e}!'
                    alert_exception(error, session_id)              
                return gr.update()

            @gr.render(inputs=[gr_blocks_data, gr_blocks_page, gr_blocks_keep, gr_blocks_text, gr_blocks_open])
            def render_blocks(blocks:list[str], page:int, keep_map:dict[int,bool], text_map:dict[int,str], open_map:dict[int,bool])->None:
                start = page * page_size
                end = min(start + page_size, len(blocks))
                with gr.Column():
                    for i in range(start, end):
                        with gr.Accordion(f'Block {i}', open=open_map.get(i, False)) as acc:
                            acc.expand(
                                lambda idx=i, m=open_map: {**m, idx: True},
                                outputs=gr_blocks_open
                            )
                            acc.collapse(
                                lambda idx=i, m=open_map: {**m, idx: False},
                                outputs=gr_blocks_open
                            )
                            keep = gr.Checkbox(
                                value=keep_map.get(i, True),
                                label="Keep block"
                            )
                            txt = gr.Textbox(
                                value=text_map.get(i, blocks[i]),
                                lines=18,
                                max_lines=18,
                                show_label=False,
                                container=False
                            )
                            keep.change(
                                lambda v, idx=i, km=keep_map: {**km, idx: v},
                                inputs=keep,
                                outputs=gr_blocks_keep
                            )
                            txt.change(
                                lambda v, idx=i, tm=text_map: {**tm, idx: v},
                                inputs=txt,
                                outputs=gr_blocks_text
                            )

            def save_page_state(blocks:list[str], page:int, keep_map:bool, text_map:str, *values):
                start = page * page_size
                index = 0
                for i in range(start, min(start + page_size, len(blocks))):
                    keep_map[i] = values[index]
                    text_map[i] = values[index + 1]
                    index += 2
                return keep_map, text_map

            def prev_page(page:int)->int:
                new_page = max(page - 1, 0)
                return new_page, gr.update(visible=new_page > 0), gr.update(visible=True)

            def next_page(page:int, blocks:list[str])->int:
                max_page = (len(blocks) - 1) // page_size
                new_page = min(page + 1, max_page)
                return new_page, gr.update(visible=new_page < max_page), gr.update(visible=True)

            def update_blocks_header(page:int, blocks:list[str])->str:
                start = page * page_size
                end = min(start + page_size, len(blocks))
                if not blocks:
                    return ''
                return gr.update(value=f'Blocks {start}–{end-1} of {len(blocks) - 1}')

            def edit_blocks(session_id:str)->tuple:
                session = context.get_session(session_id)
                if session and session['status'] == confirm_blocks:
                    return (
                        gr.update(visible=True), update_blocks_header(0, session['blocks']), session['blocks'], 0, {}, {},
                        gr.update(visible=False), gr.update(visible=len(session['blocks']) > page_size)
                    )
                return tuple(gr.update(visible=False) for _ in range(8))

            def cancel_blocks(session_id:str)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session["status"] = 'ready'
                return gr.update(visible=False), [], 0, {}, {}

            def continue_blocks(blocks:list[str], keep_map:dict[int,bool], text_map:dict[int,str])->list[str]:
                result = []
                for i, block in enumerate(blocks):
                    if keep_map.get(i, True):
                        result.append(text_map.get(i, block))
                return result

            def change_gr_restore_session(data:DictProxy|None, state:dict, req:gr.Request)->tuple:
                try:
                    nonlocal models
                    msg = 'Error while loading saved session. Please try to delete your cookies and refresh the page'
                    if not data.get('id', False):
                        session = context.set_session(str(uuid.uuid4()))
                    else:
                        session = context.set_session(data.get('id'))
                    if len(active_sessions) == 0 or (data and data.get('status', None) is None):
                        restore_session_from_data(data, session)
                        session['status'] = None
                    if not context_tracker.start_session(session['id']):
                        error = "Your session is already active.<br>If it's not the case please close your browser and relaunch it."
                        return gr.update(), gr.update(), gr.update(value=''), update_gr_glassmask(str=error)
                    else:
                        active_sessions.add(req.session_hash)
                        session[req.session_hash] = req.session_hash
                        session['cancellation_requested'] = False
                    if isinstance(session.get('ebook'), str):
                        if not os.path.exists(session['ebook']):
                            session['ebook'] = None
                    if isinstance(session.get('voice'), str):
                        if not os.path.exists(session['voice']):
                            session['voice'] = None
                    if isinstance(session.get('custom_model'), str):
                        custom_model_dir = session.get('custom_model_dir')
                        if isinstance(custom_model_dir, str) and not os.path.exists(custom_model_dir):
                            session['custom_model'] = None
                    if isinstance(session.get('fine_tuned'), str):
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
                    if session['status'] == 'converting':
                        session['status'] = 'ready'
                    session['is_gui_process'] = is_gui_process
                    session['system'] = sys.platform
                    session['session_dir'] = os.path.join(tmp_dir, f"proc-{session['id']}")
                    session['custom_model_dir'] = os.path.join(models_dir, '__sessions', f"model-{session['id']}")
                    session['voice_dir'] = os.path.join(voices_dir, '__sessions', f"voice-{session['id']}", session['language'])
                    os.makedirs(session['custom_model_dir'], exist_ok=True)
                    os.makedirs(session['voice_dir'], exist_ok=True)     
                    if is_gui_shared:
                        msg = f' Note: access limit time: {interface_shared_tmp_expire} days'
                        session['audiobooks_dir'] = os.path.join(audiobooks_gradio_dir, f"web-{session['id']}")
                        delete_unused_tmp_dirs(audiobooks_gradio_dir, interface_shared_tmp_expire, session['id'])
                    else:
                        msg = f' Note: if no activity is detected after {tmp_expire} days, your session will be cleaned up.'
                        session['audiobooks_dir'] = os.path.join(audiobooks_host_dir, f"web-{session['id']}")
                        delete_unused_tmp_dirs(audiobooks_host_dir, tmp_expire, session['id'])
                    if not os.path.exists(session['audiobooks_dir']):
                        os.makedirs(session['audiobooks_dir'], exist_ok=True)
                    previous_hash = state['hash']
                    new_hash = hash_proxy_dict(MappingProxyType(session))
                    state['hash'] = new_hash
                    show_alert({"type": "info", "msg": msg})
                    return gr.update(value=json.dumps(session, cls=JSONDictProxyEncoder)), gr.update(value=state), gr.update(value=session['id']), gr.update()
                except Exception as e:
                    error = f'change_gr_restore_session(): {e}'
                    alert_exception(error, None)
                    return gr.update(), gr.update(), gr.update(), gr.update()

            async def update_gr_save_session(session_id:str, state:dict)->tuple:
                try:
                    session = context.get_session(session_id)
                    if not session or (session and not session.get('id', False)):
                        yield gr.update(), gr.update(), gr.update()
                        return
                    previous_hash = state.get("hash")
                    if session.get("status") == "converting":
                        try:
                            if session.get('ticker') != len(audiobook_options):
                                session['ticker'] = len(audiobook_options)
                                new_hash = hash_proxy_dict(MappingProxyType(session))
                                state['hash'] = new_hash
                                session_dict = json.dumps(session, cls=JSONDictProxyEncoder)
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
                            session_dict = json.dumps(session, cls=JSONDictProxyEncoder)
                            yield (
                                gr.update(value=session_dict),
                                gr.update(value=state),
                                gr.update(),
                            )
                    else:
                        new_hash = hash_proxy_dict(MappingProxyType(session))
                        if previous_hash == new_hash:
                            yield gr.update(), gr.update(), gr.update()
                        else:
                            state['hash'] = new_hash
                            session_dict = json.dumps(session, cls=JSONDictProxyEncoder)
                            yield (
                                gr.update(value=session_dict),
                                gr.update(value=state),
                                gr.update(),
                            )
                except Exception as e:
                    error = f'update_gr_save_session(): {e}!'
                    alert_exception(error, session_id)
                    yield gr.update(), gr.update(value=e), gr.update()
            
            def clear_event(session_id:str)->None:
                if session_id:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        session['event'] = None

            gr_ebook_file.change(
                fn=change_convert_btn,
                inputs=[gr_ebook_file, gr_ebook_mode, gr_custom_model_file, gr_session],
                outputs=[gr_convert_btn]
            ).then(
                fn=change_gr_ebook_file,
                inputs=[gr_ebook_file, gr_session],
                outputs=[gr_modal]
            )
            gr_ebook_mode.change(
                fn=change_gr_ebook_mode,
                inputs=[gr_ebook_mode, gr_session],
                outputs=[gr_ebook_file, gr_chapters_preview]
            )
            gr_chapters_preview.select(
                fn=lambda val, session_id: change_param('chapters_preview', bool(val), session_id),
                inputs=[gr_chapters_preview, gr_session],
                outputs=None
            )
            gr_voice_file.upload(
                fn=disable_on_voice_upload,
                inputs=None,
                outputs=[gr_ebook_file, gr_ebook_mode, gr_language, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list, gr_convert_btn, gr_voice_play, gr_voice_del_btn]
            ).then(
                fn=change_gr_voice_file,
                inputs=[gr_voice_file, gr_session],
                outputs=[gr_voice_list]
            ).then(
                fn=lambda: gr.update(value=None),
                inputs=None,
                outputs=[gr_voice_file]
            ).then(
                fn=enable_on_voice_upload,
                inputs=[gr_session],
                outputs=[gr_ebook_file, gr_ebook_mode, gr_language, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list, gr_convert_btn, gr_voice_play, gr_voice_del_btn]
            )
            gr_voice_list.change(
                fn=change_gr_voice_list,
                inputs=[gr_voice_list, gr_session],
                outputs=[gr_voice_player_hidden, gr_voice_play, gr_voice_del_btn]
            )
            gr_voice_del_btn.click(
                fn=click_gr_voice_del_btn,
                inputs=[gr_voice_list, gr_session],
                outputs=[gr_confirm_deletion_field_hidden, gr_modal]
            )
            gr_device.change(
                fn=change_gr_device,
                inputs=[gr_device, gr_session],
                outputs=None
            )
            gr_language.change(
                fn=change_gr_language,
                inputs=[gr_language, gr_session],
                outputs=[gr_language, gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list]
            ).then(
                fn=update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list]
            )
            gr_tts_engine_list.change(
                fn=change_gr_tts_engine_list,
                inputs=[gr_tts_engine_list, gr_session],
                outputs=[gr_tts_rating, gr_tab_xtts_params, gr_tab_bark_params, gr_group_custom_model, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_label]
            ).then(
                fn=update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list]
            )
            gr_fine_tuned_list.change(
                fn=change_gr_fine_tuned_list,
                inputs=[gr_fine_tuned_list, gr_session],
                outputs=[gr_group_custom_model]
            ).then(
                fn=update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list]
            )
            gr_custom_model_file.upload(
                fn=disable_on_custom_upload,
                inputs=None,
                outputs=[gr_ebook_file, gr_ebook_mode, gr_language, gr_tts_engine_list, gr_fine_tuned_list, gr_voice_file, gr_convert_btn, gr_custom_model_del_btn]
            ).then(
                fn=change_gr_custom_model_file,
                inputs=[gr_custom_model_file, gr_tts_engine_list, gr_session],
                outputs=[gr_custom_model_file, gr_custom_model_list],
                show_progress_on=[gr_custom_model_list]
            ).then(
                fn=update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list]
            ).then(
                fn=enable_on_custom_upload,
                inputs=[gr_session],
                outputs=[gr_ebook_file, gr_ebook_mode, gr_language, gr_tts_engine_list, gr_fine_tuned_list, gr_voice_file, gr_convert_btn, gr_custom_model_del_btn]
            )
            gr_custom_model_list.change(
                fn=change_gr_custom_model_list,
                inputs=[gr_custom_model_list, gr_session],
                outputs=[gr_fine_tuned_list, gr_custom_model_del_btn, gr_voice_list]
            )
            gr_custom_model_del_btn.click(
                fn=click_gr_custom_model_del_btn,
                inputs=[gr_custom_model_list, gr_session],
                outputs=[gr_confirm_deletion_field_hidden, gr_modal]
            )
            gr_output_format_list.change(
                fn=change_gr_output_format_list,
                inputs=[gr_output_format_list, gr_session],
                outputs=None
            )
            gr_output_channel_list.change(
                fn=change_gr_output_channel_list,
                inputs=[gr_output_channel_list, gr_session],
                outputs=None
            )
            gr_output_split.select(
                fn=change_gr_output_split,
                inputs=[gr_output_split, gr_session],
                outputs=[gr_row_output_split_hours]
            )
            gr_output_split_hours.change(
                fn=lambda val, session_id: change_param('output_split_hours', str(val), session_id),
                inputs=[gr_output_split_hours, gr_session],
                outputs=None
            )
            gr_progress.change(
                fn=None,
                inputs=[gr_progress],
                js=r'''
                    (filename)=>{
                        const gr_root = (window.gradioApp && window.gradioApp()) || document;
                        const gr_ebook_file = gr_root.querySelector("#gr_ebook_file");
                        if(!gr_ebook_file){
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
                        const rows = gr_ebook_file.querySelectorAll("table.file-preview tr.file");
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
                '''
            )
            gr_playback_time.change(
                fn=change_gr_playback_time,
                inputs=[gr_playback_time, gr_session],
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
                inputs=[gr_audiobook_list, gr_audiobook_files_toggled],
                outputs=[gr_audiobook_files, gr_audiobook_files_toggled],
                show_progress="minimal",
            )
            gr_audiobook_list.change(
                fn=change_gr_audiobook_list,
                inputs=[gr_audiobook_list, gr_session],
                outputs=[gr_group_audiobook_list]
            ).then(
                fn=update_gr_audiobook_player,
                inputs=[gr_session],
                outputs=[gr_playback_time, gr_audiobook_player, gr_audiobook_vtt]
            ).then(
                fn=None,
                inputs=None,
                js='()=>{window.load_vtt();}'
            )
            gr_audiobook_del_btn.click(
                fn=click_gr_audiobook_del_btn,
                inputs=[gr_audiobook_list, gr_session],
                outputs=[gr_confirm_deletion_field_hidden, gr_modal]
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
                fn=lambda val, session_id: change_param('xtts_temperature', float(val), session_id),
                inputs=[gr_xtts_temperature, gr_session],
                outputs=None
            )
            gr_xtts_length_penalty.change(
                fn=lambda val, session_id, val2: change_param('xtts_length_penalty', int(val), session_id, int(val2)),
                inputs=[gr_xtts_length_penalty, gr_session, gr_xtts_num_beams],
                outputs=None,
            )
            gr_xtts_num_beams.change(
                fn=lambda val, session_id, val2: change_param('xtts_num_beams', int(val), session_id, int(val2)),
                inputs=[gr_xtts_num_beams, gr_session, gr_xtts_length_penalty],
                outputs=None,
            )
            gr_xtts_repetition_penalty.change(
                fn=lambda val, session_id: change_param('xtts_repetition_penalty', float(val), session_id),
                inputs=[gr_xtts_repetition_penalty, gr_session],
                outputs=None
            )
            gr_xtts_top_k.change(
                fn=lambda val, session_id: change_param('xtts_top_k', int(val), session_id),
                inputs=[gr_xtts_top_k, gr_session],
                outputs=None
            )
            gr_xtts_top_p.change(
                fn=lambda val, session_id: change_param('xtts_top_p', float(val), session_id),
                inputs=[gr_xtts_top_p, gr_session],
                outputs=None
            )
            gr_xtts_speed.change(
                fn=lambda val, session_id: change_param('xtts_speed', float(val), session_id),
                inputs=[gr_xtts_speed, gr_session],
                outputs=None
            )
            gr_xtts_enable_text_splitting.select(
                fn=lambda val, session_id: change_param('xtts_enable_text_splitting', bool(val), session_id),
                inputs=[gr_xtts_enable_text_splitting, gr_session],
                outputs=None
            )
            ########### BARK Params
            gr_tab_bark_params.select(
                fn=None,
                inputs=None,
                outputs=None,
                js='''
                () => {
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
                fn=lambda val, session_id: change_param('bark_text_temp', float(val), session_id),
                inputs=[gr_bark_text_temp, gr_session],
                outputs=None
            )
            gr_bark_waveform_temp.change(
                fn=lambda val, session_id: change_param('bark_waveform_temp', float(val), session_id),
                inputs=[gr_bark_waveform_temp, gr_session],
                outputs=None
            )
            ############ Timer to save session to localStorage
            gr_timer = gr.Timer(9, active=False)
            gr_timer.tick(
                fn=update_gr_save_session,
                inputs=[gr_session, gr_session_update],
                outputs=[gr_save_session, gr_session_update, gr_audiobook_list]
            ).then(
                fn=clear_event,
                inputs=[gr_session],
                outputs=None
            )
            gr_convert_btn.click(
                fn=change_convert_btn,
                inputs=None,
                outputs=[gr_convert_btn]
            ).then(
                fn=disable_components,
                inputs=None,
                outputs=[gr_ebook_mode, gr_chapters_preview, gr_language, gr_voice_file, gr_voice_list, gr_device, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list, gr_output_format_list, gr_output_channel_list]
            ).then(
                fn=submit_convert_btn,
                inputs=[
                    gr_session, gr_device, gr_ebook_file, gr_chapters_preview, gr_tts_engine_list, gr_language, gr_voice_list,
                    gr_custom_model_list, gr_fine_tuned_list, gr_output_format_list, gr_output_channel_list,
                    gr_xtts_temperature, gr_xtts_length_penalty, gr_xtts_num_beams, gr_xtts_repetition_penalty, gr_xtts_top_k, gr_xtts_top_p, gr_xtts_speed, gr_xtts_enable_text_splitting,
                    gr_bark_text_temp, gr_bark_waveform_temp, gr_output_split, gr_output_split_hours
                ],
                outputs=[gr_progress]
            ).then(
                fn=edit_blocks,
                inputs=[gr_session],
                outputs=[
                    gr_blocks_panel, gr_blocks_header, gr_blocks_data, gr_blocks_page, gr_blocks_keep,
                    gr_blocks_text, gr_blocks_prev, gr_blocks_next
                ]
            ).then(
                fn=enable_components,
                inputs=[gr_session],
                outputs=[gr_ebook_mode, gr_chapters_preview, gr_language, gr_voice_file, gr_voice_list, gr_device, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list, gr_output_format_list, gr_output_channel_list]
            ).then(
                fn=refresh_interface,
                inputs=[gr_session],
                outputs=[gr_convert_btn, gr_ebook_file, gr_device, gr_audiobook_list, gr_audiobook_player, gr_modal, gr_voice_list, gr_progress]
            )
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
                outputs=[gr_save_session, gr_session_update, gr_session, gr_glassmask]
            ).then(
                fn=restore_interface,
                inputs=[gr_session],
                outputs=[
                    gr_ebook_file, gr_ebook_mode, gr_chapters_preview, gr_device, gr_language, gr_voice_list,
                    gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list, gr_output_format_list, gr_output_channel_list,
                    gr_output_split, gr_output_split_hours, gr_row_output_split_hours, gr_audiobook_list, gr_group_custom_model
                ]
            ).then(
                fn=restore_audiobook_player,
                inputs=[gr_audiobook_list],
                outputs=[
                    gr_group_audiobook_list, gr_audiobook_player, gr_timer
                ]
            ).then(
                fn=lambda session: update_gr_glassmask(attr=['gr-glass-mask', 'hide']) if session else gr.update(),
                inputs=[gr_session],
                outputs=[gr_glassmask]
            ).then(
                fn=None,
                inputs=None,
                js='()=>{init_interface();}'
            )
            gr_confirm_deletion_yes_btn.click(
                fn=confirm_deletion,
                inputs=[gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_session, gr_confirm_deletion_field_hidden],
                outputs=[gr_custom_model_list, gr_audiobook_list, gr_modal, gr_voice_list]
            )
            gr_confirm_deletion_no_btn.click(
                fn=confirm_deletion,
                inputs=[gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_session],
                outputs=[gr_custom_model_list, gr_audiobook_list, gr_modal, gr_voice_list]
            )
            gr_blocks_prev.click(
                fn=prev_page,
                inputs=[gr_blocks_page],
                outputs=[gr_blocks_page, gr_blocks_prev, gr_blocks_next]
            ).then(
                fn=update_blocks_header,
                inputs=[gr_blocks_page, gr_blocks_data],
                outputs=[gr_blocks_header]
            )
            gr_blocks_next.click(
                fn=next_page,
                inputs=[gr_blocks_page,gr_blocks_data],
                outputs=[gr_blocks_page, gr_blocks_next, gr_blocks_prev]
            ).then(
                fn=update_blocks_header,
                inputs=[gr_blocks_page, gr_blocks_data],
                outputs=[gr_blocks_header]
            )
            gr_blocks_cancel.click(
                fn=cancel_blocks,
                inputs=[gr_session],
                outputs=[gr_blocks_panel, gr_blocks_data, gr_blocks_page, gr_blocks_keep, gr_blocks_text]
            )
            gr_blocks_continue.click(
                fn=continue_blocks,
                inputs=[gr_blocks_data, gr_blocks_keep, gr_blocks_text],
                outputs=[gr_blocks_data]
            ).then(
                fn=finalize_audiobook,
                inputs=[gr_session],
                outputs=[gr_progress]
            ).then(
                fn=enable_components,
                inputs=[gr_session],
                outputs=[gr_ebook_mode, gr_chapters_preview, gr_language, gr_voice_file, gr_voice_list, gr_device, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list, gr_output_format_list, gr_output_channel_list]
            ).then(
                fn=refresh_interface,
                inputs=[gr_session],
                outputs=[gr_convert_btn, gr_ebook_file, gr_device, gr_audiobook_list, gr_audiobook_player, gr_modal, gr_voice_list, gr_progress]
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
                            let tabs_opened = false;
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
                                        gr_progress = gr_root.querySelector("#gr_progress");
                                        if(!gr_root || !gr_progress){
                                            clearTimeout(init_elements_timeout);
                                            console.warn("Components not ready... retrying");
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
                                        // Keep your progress observer too
                                        new MutationObserver(tab_progress).observe(gr_progress, {
                                            attributes: true,
                                            childList: true,
                                            subtree: true,
                                            characterData: true
                                        });
                                        gr_progress.addEventListener("change", tab_progress);
                                    }catch(e){
                                        console.warn("init_interface error:", e);
                                    }
                                };
                            }
                            if(typeof(window.init_xtts_sliders) !== "function"){
                                window.init_xtts_sliders = ()=>{
                                    try{
                                        const gr_xtts_temperature           = gr_root.querySelector("#gr_xtts_temperature input[type=number]");
                                        const gr_xtts_repetition_penalty    = gr_root.querySelector("#gr_xtts_repetition_penalty input[type=number]");
                                        const gr_xtts_top_k                 = gr_root.querySelector("#gr_xtts_top_k input[type=number]");
                                        const gr_xtts_top_p                 = gr_root.querySelector("#gr_xtts_top_p input[type=number]");
                                        const gr_xtts_speed                 = gr_root.querySelector("#gr_xtts_speed input[type=number]");
                                        const sliders = [
                                            gr_xtts_temperature,
                                            gr_xtts_repetition_penalty,
                                            gr_xtts_top_k,
                                            gr_xtts_top_p,
                                            gr_xtts_speed
                                        ];
                                        sliders.forEach(slider => {
                                            if(!slider) return;
                                            const key = slider.closest("div[id]").id.replace(/^gr_/, "");
                                            const saved = window.session_storage[key];
                                            slider.value = (slider === gr_xtts_top_k) ? parseInt(saved) : parseFloat(saved);
                                            slider.dispatchEvent(new Event("input", { bubbles: true }));
                                        });
                                    }catch(e){
                                        console.warn("init_xtts_sliders error:", e);
                                    }
                                };
                            }
                            if(typeof(window.init_bark_sliders) !== "function"){
                                window.init_bark_sliders = ()=>{
                                    try{
                                        const gr_bark_text_temp_slider       = gr_root.querySelector("#gr_bark_text_temp input[type=number]");
                                        const gr_bark_waveform_temp_slider   = gr_root.querySelector("#gr_bark_waveform_temp input[type=number]");
                                        const sliders = [
                                            gr_bark_text_temp_slider,
                                            gr_bark_waveform_temp_slider
                                        ];
                                        sliders.forEach(slider => {
                                            if(!slider) return;
                                            const key = slider.closest("div[id]").id.replace(/^gr_/, "");
                                            const saved = window.session_storage[key];
                                            slider.value = parseFloat(saved);
                                            slider.dispatchEvent(new Event("input", { bubbles: true }));
                                        });
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
                                            console.warn("Voice player not found yet, retrying...");
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
                                                    gr_audiobook_player.currentTime = parseFloat(window.session_storage.playback_time);
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
                                                    gr_audiobook_sentence.value = "...";
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
                            if(typeof(window.tab_progress) !== "function"){
                                window.tab_progress = ()=>{
                                    try{
                                        const val = gr_progress?.value || gr_progress?.textContent || "";
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
                                                gr_audiobook_sentence.value = "...";
                                            }else{
                                                parseVTT(txt);
                                            }
                                        }
                                    }catch(e){
                                        console.warn("load_vtt error:", e);
                                    }
                                };
                            }
                            if(typeof(parseVTT) !== "function"){
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
                                        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c =>{
                                            const r = Math.random() * 16 | 0;
                                            const v = c === 'x' ? r : (r & 0x3 | 0x8);
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
                                            tabs_opened = true;
                                            break;
                                        case "new-tab-opened":
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
                            window.onElementAvailable("#gr_voice_player_hidden audio", (el)=>{
                                window.init_voice_player_hidden();
                            }, {once: false});
                            window.onElementAvailable("#gr_audiobook_player audio", (el)=>{
                                window.init_audiobook_player();
                            }, {once: false});
                            try{
                                bc.postMessage({ type: "check-existing", senderId: tab_id });
                                setTimeout(()=>{
                                    if(tabs_opened){
                                        bc.postMessage({
                                            type: "new-tab-opened",
                                            text: "Session expired.<br/>You can close this window",
                                            senderId: tab_id
                                        });
                                    }
                                }, 250);
                            }catch(e){
                                console.warn("bc.postMessage error:", e);
                            }
                            return window.session_storage;
                        }catch(e){
                            console.warn("gr_raed_data js error:", e);
                        }
                        return null;
                    }
                ''',
                outputs=[gr_restore_session],
            )
            app.unload(cleanup_session)
            all_ips = get_all_ip_addresses()
            msg = f'IPs available for connection:\n{all_ips}\nNote: 0.0.0.0 is not the IP to connect. Instead use an IP above to connect and port {interface_port}'
            show_alert({"type": "info", "msg": msg})
            os.environ['no_proxy'] = ' ,'.join(all_ips)
            return app
    except Exception as e:
        error = f'An unexpected error occurred: {e}'
        alert_exception(error, None)
    return None