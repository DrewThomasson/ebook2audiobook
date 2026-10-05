from lib.core import *

theme = gr.themes.Origin(
    primary_hue='green',
    secondary_hue='amber',
    neutral_hue='gray',
    radius_size='lg',
    font_mono=['JetBrains Mono', 'monospace', 'Consolas', 'Menlo', 'Liberation Mono']
)
header_css = os.path.join(root_dir, 'header.css')
progress_bar = gr.Progress(track_tqdm=False)

def build_interface(args:dict)->gr.Blocks:
    from lib.classes.tts_engines.common.preset_loader import load_engine_presets
    try:
        script_mode = args['script_mode']
        is_gui_process = args['is_gui_process']
        is_gui_shared = args['share']
        title = 'Ebook2Audiobook'
        header_js = Path(root_dir, 'header.js').read_text(encoding='utf-8')
        gr_glassmask_msg = legends['gr_glassmask']
        models = None
        language_options = [
            (
                f"{details['name']} - {details['native_name']}" if details['name'] != details['native_name'] else details['name'],
                lang
            )
            for lang, details in language_mapping.items()
        ]
        translate_options = []
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
        visible_gr_tab_abs_params = interface_component_options['gr_tab_abs_params']
        js_hide_elements = 'document.querySelector("#ebook_textarea_toolbar")?.remove();'
        js_show_elements = 'window.gr_ebook_textarea_counter();'

        gr_blocks_kwargs = {"title": title, "delete_cache": (604800, 86400)}
        with gr.Blocks(**gr_blocks_kwargs) as app:
            with gr.Group(visible=True, elem_id='gr_group_main', elem_classes='gr-group-main') as gr_group_main:
                with gr.Tabs(elem_id='gr_tabs') as gr_tabs:
                    with gr.Tab(legends['gr_tab_main'], elem_id='gr_tab_main', elem_classes='gr-tab') as gr_tab_main:
                        with gr.Row(elem_id='gr_row_tab_main'):
                            with gr.Column(elem_id='gr_col_1', elem_classes=['gr-col'], scale=3):
                                with gr.Group(elem_id='gr_group_ebook_src', elem_classes=['gr-group']):
                                    gr_import_markdown = gr.Markdown(elem_id='gr_import_markdown', elem_classes=['gr-markdown'], value=legends['gr_import_markdown'])
                                    gr_ebook_src = gr.File(show_label=False, label='-', elem_id='gr_ebook_src', visible=True, file_types=ebook_formats, file_count=ebook_modes['SINGLE'], allow_reordering=True, height=100)
                                    gr_voice_highlight_css = gr.HTML(value='', elem_classes=['gr-voice-highlight-css'])
                                    gr_ebook_textarea = gr.Textbox(show_label=True, label=legends['gr_ebook_textarea'], elem_id='gr_ebook_textarea', visible=False, lines=8, max_length=max_ebook_textarea_length)
                                    with gr.Row(elem_id='gr_row_ebook_mode') as gr_row_ebook_mode:
                                        gr_ebook_mode = gr.Dropdown(label='', elem_id='gr_ebook_mode', choices=[(legends['gr_ebook_mode_file'],ebook_modes['SINGLE']), (legends['gr_ebook_mode_directory'],ebook_modes['DIRECTORY']), (legends['gr_ebook_mode_text'],ebook_modes['TEXT'])], interactive=True, scale=2)
                                        gr_blocks_preview = gr.Checkbox(label=legends['gr_blocks_preview'], elem_id='gr_blocks_preview', value=False, interactive=True, scale=1)
                                        gr_interlude_enabled = gr.Checkbox(label=legends['gr_interlude_enabled'], elem_id='gr_interlude_enabled', value=False, interactive=True, scale=1)
                                with gr.Group(elem_id='gr_group_language', elem_classes=['gr-group']):
                                    gr_language_markdown = gr.Markdown(elem_id='gr_language_markdown', elem_classes=['gr-markdown'], value=legends['gr_language_markdown'])
                                    with gr.Row(elem_id='gr_row_language') as gr_row_language:
                                        gr_language = gr.Dropdown(show_label=False, elem_id='gr_language', choices=language_options, value=default_language_code, type='value', interactive=True, scale=2)
                                        gr_translate_enabled = gr.Checkbox(label=legends['gr_translate_enabled'], elem_id='gr_translate_enabled', value=False, interactive=True, scale=1, min_width=120)
                                        gr_translate = gr.Dropdown(show_label=False, elem_id='gr_translate', choices=[], value=None, type='value', interactive=True, visible=False, scale=2)
                                gr_group_voice_file = gr.Group(elem_id='gr_group_voice_file', elem_classes=['gr-group'], visible=visible_gr_group_voice_file)
                                with gr_group_voice_file:
                                    gr_voice_markdown = gr.Markdown(elem_id='gr_voice_markdown', elem_classes=['gr-markdown'], value=legends['gr_voice_markdown'])
                                    gr_voice_file = gr.File(show_label=False, label=legends['gr_voice_file'], elem_id='gr_voice_file', file_types=voice_formats, value=None, height=100)
                                    with gr.Row(elem_id='gr_row_voice_player') as gr_row_voice_player:
                                        gr_voice_player_hidden = gr.Audio(elem_id='gr_voice_player_hidden', type='filepath', interactive=False, waveform_options=gr.WaveformOptions(show_recording_waveform=False), container=False, visible=True, show_label=False, scale=0, min_width=60)
                                        gr_voice_play = gr.Button('▶', elem_id='gr_voice_play', elem_classes=['small-btn-green'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                        gr_voice_list = gr.Dropdown(label=legends['gr_voice_list'], elem_id='gr_voice_list', choices=voice_options, type='value', interactive=True, scale=2)
                                        gr_voice_selected_filename = gr.Markdown(value='', elem_id='gr_voice_selected_filename', elem_classes=['gr-markdown'], visible=False)
                                        gr_voice_del_btn = gr.Button('🗑', elem_id='gr_voice_del_btn', elem_classes=['small-btn-red'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                with gr.Group(elem_id='gr_group_device', elem_classes=['gr-group']):
                                    gr_device_markdown = gr.Markdown(elem_id='gr_device_markdown', elem_classes=['gr-markdown'], value=legends['gr_device_markdown'])
                                    gr_device = gr.Dropdown(label='', elem_id='gr_device', choices=[(k, v['proc']) for k, v in devices.items()], type='value', value=default_device, interactive=True)
                            with gr.Column(elem_id='gr_col_2', elem_classes=['gr-col'], scale=3):
                                with gr.Group(elem_id='gr_group_tts_engine', elem_classes=['gr-group']):
                                    gr_tts_rating = gr.Markdown(elem_id='gr_tts_rating', elem_classes=['gr-markdown'], value=legends['gr_tts_rating'])
                                    gr_tts_engine_list = gr.Dropdown(label='', elem_id='gr_tts_engine_list', choices=tts_engine_options, type='value', interactive=True)
                                with gr.Group(elem_id='gr_group_models', elem_classes=['gr-group']):
                                    gr_models_markdown = gr.Markdown(elem_id='gr_models_markdown', elem_classes=['gr-markdown'], value=legends['gr_models_markdown'])
                                    gr_fine_tuned_list = gr.Dropdown(label=legends['gr_fine_tuned_list'], elem_id='gr_fine_tuned_list', choices=fine_tuned_options, type='value', interactive=True)
                                    gr_group_custom_model = gr.Group(visible=False)
                                    with gr_group_custom_model:
                                        gr_custom_model_file = gr.File(show_label=True, label=legends['gr_custom_model_file'], elem_id='gr_custom_model_file', value=None, file_types=['.zip'], height=100)
                                        gr_row_custom_model_list = gr.Row(elem_id='gr_row_custom_model_list')
                                        with gr_row_custom_model_list:
                                            gr_custom_model_list = gr.Dropdown(label='', elem_id='gr_custom_model_list', choices=custom_model_options, type='value', interactive=True, scale=2)
                                            gr_custom_model_del_btn = gr.Button('🗑', elem_id='gr_custom_model_del_btn', elem_classes=['small-btn-red'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                with gr.Group(elem_id='gr_group_output_format'):
                                    gr_output_markdown = gr.Markdown(elem_id='gr_output_markdown', elem_classes=['gr-markdown'], value=legends['gr_output_markdown'])
                                    with gr.Row(elem_id='gr_row_output_format'):
                                        gr_output_format_list = gr.Dropdown(label=legends['gr_output_format_list'], elem_id='gr_output_format_list', choices=output_formats, type='value', value=default_output_format, interactive=True, scale=1)
                                        gr_output_channel_list = gr.Dropdown(label=legends['gr_output_channel_list'], elem_id='gr_output_channel_list', choices=[(legends['gr_output_channel_mono'], 'mono'), (legends['gr_output_channel_stereo'], 'stereo')], type='value', value=default_output_channel, interactive=True, scale=1)
                                        with gr.Group(elem_id='gr_group_output_split'):
                                            gr_output_split = gr.Checkbox(label=legends['gr_output_split'], elem_id='gr_output_split', value=default_output_split, interactive=True)
                                            gr_row_output_split_hours = gr.Row(elem_id='gr_row_output_split_hours', visible=False)
                                            with gr_row_output_split_hours:
                                                gr_output_split_hours_markdown = gr.Markdown(elem_id='gr_output_split_hours_markdown',elem_classes=['gr-markdown-output-split-hours'], value=legends['gr_output_split_hours_markdown'])
                                                gr_output_split_hours = gr.Dropdown(label='', elem_id='gr_output_split_hours', choices=options_output_split_hours, type='value', value=default_output_split_hours, interactive=True, scale=1)
                                with gr.Group(elem_id='gr_group_session', elem_classes=['gr-group']):
                                    gr_session_markdown = gr.Markdown(elem_id='gr_session_markdown', elem_classes=['gr-markdown'], value=legends['gr_session_markdown'])
                                    gr_session_switch_disable_state = gr.State(None)
                                    gr_session_switch_enable_state = gr.State(None)
                                    with gr.Row(elem_id='gr_row_session'):
                                        gr_session = gr.Textbox(label='', elem_id='gr_session', interactive=False)
                                        gr_session_switch_btn = gr.Button('🔒︎', elem_id='gr_session_switch_btn', elem_classes=['small-btn-purple'], variant='secondary', visible=True, interactive=True, scale=0, min_width=60)

                        with gr.Group(elem_id='gr_group_progress', elem_classes=['gr-group-no-col']):
                            gr_progress_markdown = gr.Markdown(elem_id='gr_progress_markdown', elem_classes=['gr-markdown'], value=legends['gr_progress_markdown'])
                            gr_progress = gr.Textbox(elem_id='gr_progress', label='', interactive=False, visible=True)
                            gr_progress_bar = gr.Progress(track_tqdm=True)

                        with gr.Group(elem_id='gr_group_audiobook_list', elem_classes=['gr-group-no-col'], visible=True) as gr_group_audiobook_list:
                            gr_audiobook_markdown = gr.Markdown(elem_id='gr_audiobook_markdown', elem_classes=['gr-markdown'], value=legends['gr_audiobook_markdown'])
                            gr_audiobook_vtt = gr.Textbox(elem_id='gr_audiobook_vtt', label='', interactive=False, visible=True)
                            gr_playback_time = gr.Number(elem_id="gr_playback_time", label='', interactive=False, visible=True, value=0.0)
                            gr_audiobook_sentence = gr.Textbox(elem_id='gr_audiobook_sentence', label='', value='…', interactive=False, lines=3, max_lines=3, max_length=500)
                            with gr.Row(elem_id='gr_row_audiobook_edit', visible=False) as gr_row_audiobook_edit:
                                gr_audiobook_edit_preview_btn = gr.Button(elem_id='gr_audiobook_edit_preview_btn', value='◉', elem_classes=['small-btn-green'], variant='secondary', interactive=True, scale=0, min_width=60)
                                gr_audio_edit_kwargs = {"elem_id": "gr_audiobook_edit_player", "label": "", "type": "filepath", "autoplay": True, "interactive": False, "buttons": None, "waveform_options": gr.WaveformOptions(show_recording_waveform=False), "container": True, "visible": True, "scale": 2}
                                gr_audiobook_edit_player = gr.Audio(**gr_audio_edit_kwargs)
                                gr_audiobook_edit_save_btn = gr.Button(elem_id='gr_audiobook_edit_save_btn', value='✔', elem_classes=['small-btn-green'], variant='secondary', interactive=False, scale=0, min_width=60)
                                gr_audiobook_edit_cancel_btn = gr.Button(elem_id='gr_audiobook_edit_cancel_btn', value='✖', elem_classes=['small-btn-red'], variant='secondary', interactive=True, scale=0, min_width=60)
                            gr_audio_kwargs = {"elem_id": "gr_audiobook_player", "label": "", "type": "filepath", "autoplay": False, "interactive": False, "buttons": None, "waveform_options": gr.WaveformOptions(show_recording_waveform=False), "container": True, "visible": True}
                            gr_audiobook_player = gr.Audio(**gr_audio_kwargs)
                            with gr.Row(elem_id='gr_row_audiobook_list', visible=True) as gr_row_audiobook_list:
                                gr_audiobook_download_btn = gr.Button(elem_id='gr_audiobook_download_btn', value='↧', elem_classes=['small-btn-blue'], variant='secondary', interactive=True, scale=0, min_width=60)
                                gr_audiobook_edit_btn = gr.Button(elem_id='gr_audiobook_edit_btn', value='✎', elem_classes=['small-btn-orange'], variant='secondary', interactive=True, scale=0, min_width=60)
                                gr_audiobook_list = gr.Dropdown(elem_id='gr_audiobook_list', label='', choices=audiobook_options, type='value', interactive=True, scale=2)
                                gr_audiobook_export_btn = gr.Button(elem_id='gr_audiobook_export_btn', value='⇄', elem_classes=['small-btn-purple'], variant='secondary', interactive=True, visible=False, scale=0, min_width=60)
                                gr_audiobook_del_btn = gr.Button(elem_id='gr_audiobook_del_btn', value='🗑', elem_classes=['small-btn-red'], variant='secondary', interactive=True, scale=0, min_width=60)
                            gr_audiobook_files = gr.Files(label='', elem_id='gr_audiobook_files', visible=False)
                            gr_audiobook_files_state = gr.State(False)

                        with gr.Group(elem_id='gr_group_convert_btn', elem_classes=['gr-group-convert-btn']) as gr_group_convert_btn:
                            gr_convert_btn = gr.Button(elem_id='gr_convert_btn', value='📚', elem_classes='gr-convert-btn', variant='primary', interactive=False)

                    with gr.Tab(legends['gr_tab_xtts_params'], elem_id='gr_tab_xtts_params', elem_classes='gr-tab', visible=False) as gr_tab_xtts_params:
                        with gr.Group(elem_id='gr_group_xtts_params', elem_classes=['gr-group']):
                            gr_xtts_temperature = gr.Slider(
                                label=legends['gr_xtts_temperature'],
                                minimum=0.05,
                                maximum=5.0,
                                step=0.05,
                                value=float(default_engine_settings[TTS_ENGINES['XTTS']]['temperature']),
                                elem_id='gr_xtts_temperature',
                                info=legends['gr_xtts_temperature_info']
                            )
                            gr_xtts_length_penalty = gr.Slider(
                                label=legends['gr_xtts_length_penalty'],
                                minimum=0.3,
                                maximum=5.0,
                                step=0.1,
                                value=float(default_engine_settings[TTS_ENGINES['XTTS']]['length_penalty']),
                                elem_id='gr_xtts_length_penalty',
                                info=legends['gr_xtts_length_penalty_info'],
                                visible=False
                            )
                            gr_xtts_num_beams = gr.Slider(
                                label=legends['gr_xtts_num_beams'],
                                minimum=1,
                                maximum=10,
                                step=1,
                                value=int(default_engine_settings[TTS_ENGINES['XTTS']]['num_beams']),
                                elem_id='gr_xtts_num_beams',
                                info=legends['gr_xtts_num_beams_info'],
                                visible=False
                            )
                            gr_xtts_repetition_penalty = gr.Slider(
                                label=legends['gr_xtts_repetition_penalty'],
                                minimum=1.0,
                                maximum=5.0,
                                step=0.1,
                                value=float(default_engine_settings[TTS_ENGINES['XTTS']]['repetition_penalty']),
                                elem_id='gr_xtts_repetition_penalty',
                                info=legends['gr_xtts_repetition_penalty_info']
                            )
                            gr_xtts_top_k = gr.Slider(
                                label=legends['gr_xtts_top_k'],
                                minimum=10,
                                maximum=100,
                                step=1,
                                value=int(default_engine_settings[TTS_ENGINES['XTTS']]['top_k']),
                                elem_id='gr_xtts_top_k',
                                info=legends['gr_xtts_top_k_info']
                            )
                            gr_xtts_top_p = gr.Slider(
                                label=legends['gr_xtts_top_p'],
                                minimum=0.1,
                                maximum=1.0, 
                                step=0.01,
                                value=float(default_engine_settings[TTS_ENGINES['XTTS']]['top_p']),
                                elem_id='gr_xtts_top_p',
                                info=legends['gr_xtts_top_p_info']
                            )
                            gr_xtts_speed = gr.Slider(
                                label=legends['gr_xtts_speed'], 
                                minimum=0.5, 
                                maximum=3.0, 
                                step=0.1, 
                                value=float(default_engine_settings[TTS_ENGINES['XTTS']]['speed']),
                                elem_id='gr_xtts_speed',
                                info=legends['gr_xtts_speed_info']
                            )
                            gr_xtts_enable_text_splitting = gr.Checkbox(
                                label=legends['gr_xtts_enable_text_splitting'], 
                                value=default_engine_settings[TTS_ENGINES['XTTS']]['enable_text_splitting'],
                                elem_id='gr_xtts_enable_text_splitting',
                                info=legends['gr_xtts_enable_text_splitting_info'],
                                visible=False
                            )      
                    with gr.Tab(legends['gr_tab_bark_params'], elem_id='gr_tab_bark_params', elem_classes='gr-tab', visible=False) as gr_tab_bark_params:
                        gr_markdown_tab_bark_params = gr.Markdown(
                            elem_id='gr_markdown_tab_bark_params',
                            value=f"### {legends['gr_markdown_tab_bark_params_title']}\n{legends['gr_markdown_tab_bark_params_desc']}"
                        )
                        with gr.Group(elem_id='gr_group_bark_params', elem_classes=['gr-group']):
                            gr_bark_text_temp = gr.Slider(
                                label=legends['gr_bark_text_temp'], 
                                minimum=0.0,
                                maximum=1.0,
                                step=0.01,
                                value=float(default_engine_settings[TTS_ENGINES['BARK']]['text_temp']),
                                elem_id='gr_bark_text_temp',
                                info=legends['gr_bark_text_temp_info']
                            )
                            gr_bark_waveform_temp = gr.Slider(
                                label=legends['gr_bark_waveform_temp'], 
                                minimum=0.0,
                                maximum=1.0,
                                step=0.01,
                                value=float(default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp']),
                                elem_id='gr_bark_waveform_temp',
                                info=legends['gr_bark_waveform_temp_info']
                            )
                    with gr.Tab(legends['gr_tab_abs_params'], elem_id='gr_tab_abs_params', elem_classes='gr-tab', visible=visible_gr_tab_abs_params) as gr_tab_abs_params:
                        with gr.Row(elem_id='gr_row1_abs'):
                            gr_abs_url = gr.Textbox(label=legends['gr_abs_url'], elem_id='gr_abs_url', value=default_abs_url, placeholder='http://localhost:13378', lines=1, max_lines=1, interactive=True, scale=2)
                            gr_abs_api_token = gr.Textbox(label=legends['gr_abs_api_token'], elem_id='gr_abs_api_token', value=default_abs_api_token, type='password', placeholder='eyJ...', lines=1, max_lines=1, interactive=True, scale=1)
                        with gr.Row(elem_id='gr_row2_abs'):
                            gr_abs_library = gr.Dropdown(label='', elem_id='gr_abs_library', choices=[], value=default_abs_library or None, interactive=True)
                            gr_abs_search_btn = gr.Button('🔍', elem_id='gr_abs_search_btn', elem_classes=['gr-abs-search-btn'], variant='', visible=True, interactive=True, scale=0, min_width=60)
                        with gr.Group(elem_id='gr_group_abs_upload_btn', elem_classes=['gr-group-abs-upload-btn']):
                            gr_abs_audiobook = gr.Textbox(elem_id='gr_abs_audiobook', label=legends['gr_abs_audiobook'], lines=1, max_lines=1, interactive=False, visible=True)
                            gr_abs_status = gr.Textbox(elem_id='gr_abs_status', label=legends['gr_abs_status'], lines=1, max_lines=1, interactive=False, visible=True)
                            gr_abs_upload_btn = gr.Button(elem_id='gr_abs_upload_btn', value='🡅', elem_classes=['gr-abs-upload-btn'], variant='secondary', interactive=False)

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
                            legends['block_label'].format(idx=i),
                            elem_id=f'block_{i}',
                            elem_classes=[acc_class],
                            visible=False,
                            open=False
                        ) as acc:
                            with gr.Row(elem_id=f'block_options_row_{i}', elem_classes=[acc_class, 'no-wrap']) as block_options_row:
                                acc_keep = gr.Checkbox(
                                    show_label=False,
                                    elem_id=f'block_keep_{i}',
                                    elem_classes=['accordion-block-keep'],
                                    value=True,
                                    interactive=True,
                                    visible=True,
                                    scale=0,
                                    min_width=20
                                )
                                acc_voice_list = gr.Dropdown(
                                    show_label=False,
                                    elem_id=f'block_voice_{i}',
                                    elem_classes=['accordion-block-voice-list'],
                                    choices=voice_options,
                                    type='value',
                                    interactive=True,
                                    scale=3,
                                    min_width=100
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
                                fn=lambda session, _i=i: _click_reset_block(session, _i),
                                inputs=[gr_session],
                                outputs=[acc_text]
                            )
                        acc.expand(
                            fn=lambda expands, _i=i: (
                                [
                                    expands[j] if j != _i else True
                                    for j in range(page_size)
                                ],
                                gr.Accordion(open=True)
                            ),
                            inputs=[gr_blocks_expands],
                            outputs=[gr_blocks_expands, acc],
                            show_progress='hidden'
                        )
                        acc.collapse(
                            fn=lambda expands, _i=i: (
                                [
                                    expands[j] if j != _i else False
                                    for j in range(page_size)
                                ],
                                gr.Accordion(open=False)
                            ),
                            inputs=[gr_blocks_expands],
                            outputs=[gr_blocks_expands, acc],
                            show_progress='hidden'
                        )
                        block_components.append((acc, acc_keep, acc_voice_list, acc_text))

                with gr.Row(elem_id='gr_row_buttons', visible=True) as gr_row_buttons:
                    gr_blocks_cancel_btn = gr.Button('🡄', elem_classes=['gr-blocks-buttons'], variant='stop', scale=0, size='md')
                    gr_blocks_confirm_btn = gr.Button('🡆', elem_classes=['gr-blocks-buttons'], variant='primary', scale=0, size='md')

            blocks_components_flat = [comp for quad in block_components for comp in quad]
            blocks_keeps = [c[1] for c in block_components]
            blocks_voices = [c[2] for c in block_components]
            blocks_texts = [c[3] for c in block_components]

            with gr.Row(elem_id='gr_row_ui_language'):
                gr_ui_language = gr.Dropdown(label=legends['gr_ui_language'], elem_id='gr_ui_language', choices=[(legends['gr_ui_language_auto'], 'auto')] + sorted([(language_mapping[lang]['native_name'] if lang in language_mapping else lang, lang) for lang in legends_langs]), value='auto', type='value', interactive=True, scale=0, min_width=150)
                gr_version_markdown = gr.Markdown(elem_id='gr_version_markdown', value=f'''
                    <div style="right:0;margin:auto;padding:10px;text-align:center">
                        <a href="https://github.com/DrewThomasson/ebook2audiobook" style="text-decoration:none;font-size:14px" target="_blank">
                        <b>{title}</b>&nbsp;<b style="color:orange; text-shadow: 0.3px 0.3px 0.3px #303030">{prog_version}</b></a>
                    </div>
                    ''', scale=1
                )
                gr_button_balloons = gr.Checkbox(label='buttons help', elem_id='gr_button_balloons', value=False, interactive=True, scale=0, min_width=150)

            gr_modal = gr.HTML(visible=False)
            gr_glassmask = gr.HTML(gr_glassmask_msg, elem_id='gr_glassmask', elem_classes=['gr-glass-mask'])
            gr_data_field_hidden = gr.Textbox(elem_id='gr_data_field_hidden', visible=False)
            gr_audiobook_edit_cue = gr.Textbox(elem_id='gr_audiobook_edit_cue', visible=False)
            
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

            def _disable_components(session_id:str, exceptions:list|None=None)->tuple:
                if session_id is None:
                    outputs = tuple([gr.update() for _ in range(len(outputs_disable_components))])
                else:
                    if exceptions is None:
                        exceptions = []
                    outputs = [gr.update(interactive=False) for _ in range(len(outputs_disable_components))]
                    if 'gr_session_switch_btn' in exceptions:
                        outputs[outputs_disable_components.index(gr_session_switch_btn)] = gr.update(interactive=True)
                    # a conversion supersedes the sentence editor: close it, drop its preview and give back
                    # the audiobook list/delete button it had locked (✎ and 📦 stay disabled until _enable_components())
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        preview_file = session.get('audiobook_edit_preview')
                        if preview_file and os.path.exists(preview_file):
                            os.unlink(preview_file)
                        session['audiobook_edit_block_id'] = None
                        session['audiobook_edit_sentence_idx'] = None
                        session['audiobook_edit_interlude'] = None
                        session['audiobook_edit_preview'] = None
                        session['audiobook_edit_preview_text'] = None
                    outputs[outputs_disable_components.index(gr_row_audiobook_edit)] = gr.update(visible=False)
                    outputs[outputs_disable_components.index(gr_audiobook_edit_player)] = gr.update(value=None)
                    outputs[outputs_disable_components.index(gr_audiobook_list)] = gr.update(interactive=True)
                    outputs[outputs_disable_components.index(gr_audiobook_del_btn)] = gr.update(interactive=True)
                    outputs[outputs_disable_components.index(gr_audiobook_player)] = gr.update(visible=True)
                return outputs

            def _enable_components(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session['status'] in [status_tags['READY'], status_tags['END']]:
                            session['status'] = status_tags['READY']
                            session['cancellation_requested'] = False
                            outputs = list(gr.update(interactive=True) for _ in range(len(outputs_enable_components)))
                            outputs[23] = gr.update()
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
                            outputs[24] = gr.update(interactive=enabled_convert_btn)
                            audiobook = session.get('audiobook')
                            enabled_upload_btn = bool(
                                audiobook
                                and os.path.isfile(str(audiobook))
                                and session.get('abs_url')
                                and session.get('abs_api_token')
                                and session.get('abs_library')
                            )
                            outputs[25] = gr.update(interactive=enabled_upload_btn)
                            enabled_edit_btn = bool(audiobook) and session.get('audiobook_edit_block_id') is None
                            visible_export_btn = False
                            if audiobook and os.path.isfile(str(audiobook)) and session.get('session_dir'):
                                base_name = Path(audiobook).stem
                                process_dir = os.path.join(session['session_dir'], hashlib.md5(base_name.encode()).hexdigest())
                                if not os.path.isdir(process_dir):
                                    part_match = re.match(r'^(.*)_part(\d+)$', base_name)
                                    if part_match:
                                        base_name = part_match.group(1)
                                        process_dir = os.path.join(session['session_dir'], hashlib.md5(base_name.encode()).hexdigest())
                                visible_export_btn = os.path.exists(os.path.join(process_dir, f"__edit_pending_{base_name}{Path(audiobook).suffix.lower()}"))
                            outputs[26] = gr.update(interactive=enabled_edit_btn)
                            outputs[27] = gr.update(visible=visible_export_btn, interactive=enabled_edit_btn)
                            visible_custom_model_del_btn = True if session['custom_model'] is not None else False
                            return tuple(outputs)
                except Exception as e:
                    error = f'_enable_components(): {e}'
                    exception_alert(session_id, error)
                outputs = tuple(gr.update() for _ in range(len(outputs_enable_components)))
                return outputs

            def _disable_on_voice_upload()->tuple:
                outputs = tuple([gr.update(interactive=False) for _ in range(10)])
                return outputs + (gr.update(visible='hidden'), gr.update(visible='hidden'))

            def _enable_on_voice_upload(session_id:str, ebook_src:str, ebook_textarea:str, ebook_mode:str)->tuple:
                visible_buttons = 'hidden'
                enabled_convert_btn = False
                session = context.get_session(session_id)
                outputs = tuple([gr.update(interactive=False) for _ in range(9)])
                if session and session.get('id', False):
                    outputs = tuple([gr.update(interactive=True) for _ in range(9)])
                    enabled_convert_btn = True if (ebook_src and ebook_mode != ebook_modes['TEXT']) or (ebook_textarea and ebook_mode == ebook_modes['TEXT']) else enabled_convert_btn
                    visible_buttons = True if session['voice'] is not None else visible_buttons
                return outputs + (gr.update(interactive=enabled_convert_btn), gr.update(visible=visible_buttons), gr.update(visible=visible_buttons))

            def _disable_on_custom_upload()->tuple:
                outputs = tuple([gr.update(interactive=False) for _ in range(11)])
                return outputs + (gr.update(visible='hidden'),)

            def _enable_on_custom_upload(custom_model:str|None, ebook_data:any, ebook_textarea:any)->tuple:
                outputs = tuple([gr.update(interactive=True) for _ in range(10)])
                enabled_convert_btn = True if ebook_data or ebook_textarea else False
                visible_custom_model_del_btn = True if custom_model is not None else False
                return outputs + (gr.update(interactive=enabled_convert_btn), gr.update(visible=visible_custom_model_del_btn))

            def _show_gr_modal(type:str, msg:str)->str:
                return f'''
                <div id="custom-gr_modal" class="gr-modal">
                    <div class="gr-modal-content">
                        <p style="color:#ffffff">{msg}</p>            
                        {_show_gr_modal_buttons(type)}
                    </div>
                </div>
                '''

            def _show_gr_modal_buttons(type:str)->str:
                if type in [status_tags['DELETION'], status_tags['OVERRIDE']]:
                    cancel_btn = f'#gr_{type}_cancel_btn'
                    confirm_btn = f'#gr_{type}_confirm_btn'
                    return f'''
                    <style>
                        .confirm-buttons .btn {{
                            display: inline-flex;
                            align-items: center;
                            justify-content: center;
                            width: 50px;
                            height: 50px;
                            border: none;
                            border-radius: 6px;
                            font-size: 20px;
                            cursor: pointer;
                            user-select: none;
                        }}
                        .confirm-buttons .btn-red {{ background-color: #dc3545; color: white; }}
                        .confirm-buttons .btn-red:hover {{ background-color: #ff6f71; }}
                        .confirm-buttons .btn-green {{ background-color: #28a745; color: white; }}
                        .confirm-buttons .btn-green:hover {{ background-color: #34d058; }}
                        .confirm-buttons .btn:active {{
                            background: var(--body-text-color) !important;
                            color: var(--body-background-fill) !important;
                        }}
                    </style>
                    <div class="confirm-buttons">
                        <div class="btn btn-red" onclick="document.querySelector('{cancel_btn}').click()">✖</div>
                        <div class="btn btn-green" onclick="document.querySelector('{confirm_btn}').click()">✔</div>
                    </div>
                    '''
                else:
                    return '<div class="spinner"></div>'

            def _yellow_stars(n:int):
                return "".join(
                    "<span style='color:#f0bc00; font-size:12px'>★</span>" for _ in range(n)
                )

            def _color_box(value:int)->str:
                if value <= 4:
                    color = "#4CAF50"  # Green = low
                elif value <= 8:
                    color = "#FF9800"  # Orange = medium
                else:
                    color = "#F44336"  # Red = high
                return f"<span style='background:{color};color:white; padding: 0 3px 0 3px; border-radius:3px; font-size:11px; white-space: nowrap'>{str(value)} GB</span>"

            def _show_rating(tts_engine:str)->str:
                rating = default_engine_settings[tts_engine]['rating']
                return f'''
                    <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                        <span class="gr-markdown-span">{legends['gr_tts_rating']}</span>
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
                              <b>VRAM:</b> {_color_box(int(rating['VRAM']))}
                            </td>
                            <td style="padding:0 5px 0 2.5px; border:none; vertical-align:bottom;">
                              <b>CPU:</b> {_yellow_stars(int(rating['CPU']))}
                            </td>
                            <td style="padding:0 5px 0 2.5px; border:none; vertical-align:bottom;">
                              <b>RAM:</b> {_color_box(int(rating['RAM']))}
                            </td>
                            <td style="padding:0 5px 0 2.5px; border:none; vertical-align:bottom;">
                              <b>{legends['gr_tts_rating_realism']}:</b> {_yellow_stars(int(rating['Realism']))}
                            </td>
                          </tr>
                        </table>
                    </div>
                '''

            def _is_valid_gradio_cache(path):
                if not path or not os.path.isfile(path):
                    return False
                path = os.path.normpath(path)
                parent = os.path.dirname(path)
                return (
                    parent.startswith(gradio_cache_dir) and
                    len(os.path.basename(parent)) >= 32
                )
                
            def _build_translate_targets(lang:str)->list:
                try:
                    if not lang:
                        return []
                    return ArgosTranslator().get_target_options(lang)
                except Exception as e:
                    error = f'_build_translate_targets() error: {e}'
                    print(error)
                    return []

            def _restore_interface(session_id:str, req:gr.Request)->tuple:
                try:
                    nonlocal translate_options
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        socket_hash = str(req.session_hash)
                        if not session.get(socket_hash):
                            outputs = tuple([gr.update() for _ in range(len(outputs_restore_interface))])
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
                                    ebook_data = [f for f in session['ebook_list'] if _is_valid_gradio_cache(f)]
                                if ebook_data:
                                    enabled_convert_btn = True
                                else:
                                    ebook_data = None
                            visible_ebook_src = True
                        elif session.get('ebook_mode') == ebook_modes['SINGLE']:
                            if _is_valid_gradio_cache(session['ebook_src']):
                                ebook_data = session['ebook_src']
                            if ebook_data:
                                enabled_convert_btn = True
                            visible_ebook_src = True
                        visible_row_split_hours = True if session['output_split'] else False
                        abs_upload_enabled = (
                            session.get('audiobook') is not None
                            and session.get('status') not in ['converting', 'edit']
                            and session.get('abs_url')
                            and session.get('abs_api_token')
                            and session.get('abs_library')
                        )
                        visible_xtts = False
                        visible_bark = False
                        if session['tts_engine'] == TTS_ENGINES['XTTS']:
                            visible_xtts = visible_gr_tab_xtts_params
                        elif session['tts_engine'] == TTS_ENGINES['BARK']:
                            visible_bark = visible_gr_tab_bark_params
                        visible_group_custom_model = visible_gr_group_custom_model if session['fine_tuned'] == 'internal' and session['tts_engine'] in tts_engines_with_custom_model else False
                        visible_voice_buttons = True if session.get('voice') is not None else False
                        visible_row_voice_player = _row_voice_player_visible(session.get('ebook_mode'), False)
                        visible_custom_model_del_btn = True if session['custom_model'] is not None else False
                        voice_file = session.get('voice')
                        translate_enabled_state = bool(session.get('translate_enabled'))
                        language = session.get('language')
                        translate = session.get('translate')
                        translate_options = _build_translate_targets(language) if language else []
                        translate_codes = {o[1] for o in translate_options}
                        if translate not in translate_codes:
                            translate = translate_options[0][1] if translate_options else None
                            session['translate'] = translate
                            try:
                                session['translate_iso1'] = Lang(translate).pt1
                            except Exception:
                                session['translate_iso1'] = None
                        translate_visible = translate_enabled_state and bool(translate_options)
                        return (
                            gr.update(visible=visible_xtts),
                            gr.update(visible=visible_bark),
                            gr.update(visible=visible_ebook_src, value=ebook_data, file_count=ebook_file_count),
                            gr.update(visible=visible_ebook_textarea, value=ebook_textarea),
                            gr.update(value=session['ebook_mode']),
                            gr.update(value=bool(session['blocks_preview'])),
                            gr.update(value=bool(session.get('interlude_enabled', False))),
                            gr.update(value=session['device']),
                            gr.update(value=session['language']),
                            gr.update(value=translate_enabled_state),
                            gr.update(visible=translate_visible, choices=translate_options, value=translate),
                            _update_gr_voice_list(session_id),
                            _update_gr_tts_engine_list(session_id),
                            gr.update(value=_show_rating(session['tts_engine'])),
                            _update_gr_custom_model_list(session_id),
                            _update_gr_fine_tuned_list(session_id),
                            gr.update(value=session['output_format']),
                            gr.update(value=session['output_channel']),
                            gr.update(value=bool(session['output_split'])),
                            gr.update(value=session['output_split_hours']),
                            gr.update(visible=visible_row_split_hours),
                            _update_gr_audiobook_list(session_id),
                            gr.update(visible=visible_group_custom_model),
                            gr.update(interactive=enabled_convert_btn),
                            gr.update(value=voice_file),
                            gr.update(visible=visible_voice_buttons),
                            gr.update(visible=visible_voice_buttons),
                            gr.update(visible=visible_row_voice_player),
                            gr.update(label=legends['gr_custom_model_file_engine'].format(engine=session['tts_engine'].upper(), files=', '.join(models[default_fine_tuned]['files']))),
                            gr.update(visible=visible_custom_model_del_btn),
                            gr.update(value=session.get('abs_url', '')),
                            gr.update(value=session.get('abs_api_token', '')),
                            _search_abs_libraries(session_id, session.get('abs_url', ''), session.get('abs_api_token', '')),
                            gr.update(interactive=abs_upload_enabled),
                            gr.update(value=''),
                        )
                except Exception as e:
                    error = f'_restore_interface(): {e}'
                    exception_alert(session_id, error)
                outputs = tuple([gr.update() for _ in range(len(outputs_restore_interface))])
                return outputs

            def _change_gr_ui_language(session_id:str, choice:str, req:gr.Request)->None:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        session['ui_language_choice'] = None if choice in (None, 'auto') else choice
                        session['ui_language'] = session['ui_language_choice'] or next((legends_iso1[tag.split(';')[0].strip().split('-')[0].lower()] for tag in req.headers.get('accept-language', '').split(',') if tag.split(';')[0].strip().split('-')[0].lower() in legends_iso1), system_language)
                        ui_language.set(session['ui_language'])
                except Exception as e:
                    error = f'_change_gr_ui_language(): {e}'
                    exception_alert(session_id, error)

            def _restore_ui_language(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        return (
                            gr.update(label=legends['gr_tab_main']),
                            gr.update(label=legends['gr_tab_xtts_params']),
                            gr.update(label=legends['gr_tab_bark_params']),
                            gr.update(label=legends['gr_tab_abs_params']),
                            gr.update(value=legends['gr_import_markdown']),
                            gr.update(label=legends['gr_ebook_textarea']),
                            gr.update(choices=[(legends['gr_ebook_mode_file'],ebook_modes['SINGLE']), (legends['gr_ebook_mode_directory'],ebook_modes['DIRECTORY']), (legends['gr_ebook_mode_text'],ebook_modes['TEXT'])]),
                            gr.update(label=legends['gr_blocks_preview']),
                            gr.update(label=legends['gr_interlude_enabled']),
                            gr.update(value=legends['gr_language_markdown']),
                            gr.update(label=legends['gr_translate_enabled']),
                            gr.update(value=legends['gr_voice_markdown']),
                            gr.update(label=legends['gr_voice_file']),
                            _update_gr_voice_list(session_id),
                            gr.update(value=legends['gr_device_markdown']),
                            gr.update(value=_show_rating(session['tts_engine'])),
                            gr.update(value=legends['gr_models_markdown']),
                            gr.update(label=legends['gr_fine_tuned_list']),
                            gr.update(label=legends['gr_custom_model_file_engine'].format(engine=session['tts_engine'].upper(), files=', '.join(models[default_fine_tuned]['files']))),
                            gr.update(value=legends['gr_output_markdown']),
                            gr.update(label=legends['gr_output_format_list']),
                            gr.update(label=legends['gr_output_channel_list'], choices=[(legends['gr_output_channel_mono'], 'mono'), (legends['gr_output_channel_stereo'], 'stereo')]),
                            gr.update(label=legends['gr_output_split']),
                            gr.update(value=legends['gr_output_split_hours_markdown']),
                            gr.update(value=legends['gr_session_markdown']),
                            gr.update(value=legends['gr_progress_markdown']),
                            gr.update(value=legends['gr_audiobook_markdown']),
                            gr.update(label=legends['gr_xtts_temperature'], info=legends['gr_xtts_temperature_info']),
                            gr.update(label=legends['gr_xtts_length_penalty'], info=legends['gr_xtts_length_penalty_info']),
                            gr.update(label=legends['gr_xtts_num_beams'], info=legends['gr_xtts_num_beams_info']),
                            gr.update(label=legends['gr_xtts_repetition_penalty'], info=legends['gr_xtts_repetition_penalty_info']),
                            gr.update(label=legends['gr_xtts_top_k'], info=legends['gr_xtts_top_k_info']),
                            gr.update(label=legends['gr_xtts_top_p'], info=legends['gr_xtts_top_p_info']),
                            gr.update(label=legends['gr_xtts_speed'], info=legends['gr_xtts_speed_info']),
                            gr.update(label=legends['gr_xtts_enable_text_splitting'], info=legends['gr_xtts_enable_text_splitting_info']),
                            gr.update(value=f"### {legends['gr_markdown_tab_bark_params_title']}\n{legends['gr_markdown_tab_bark_params_desc']}"),
                            gr.update(label=legends['gr_bark_text_temp'], info=legends['gr_bark_text_temp_info']),
                            gr.update(label=legends['gr_bark_waveform_temp'], info=legends['gr_bark_waveform_temp_info']),
                            gr.update(label=legends['gr_abs_url']),
                            gr.update(label=legends['gr_abs_api_token']),
                            gr.update(label=legends['gr_abs_audiobook']),
                            gr.update(label=legends['gr_abs_status']),
                            gr.update(label=legends['gr_ui_language'], choices=[(legends['gr_ui_language_auto'], 'auto')] + sorted([(language_mapping[lang]['native_name'] if lang in language_mapping else lang, lang) for lang in legends_langs]), value=session.get('ui_language_choice') or 'auto'),
                        )
                except Exception as e:
                    error = f'_restore_ui_language(): {e}'
                    exception_alert(session_id, error)
                return tuple([gr.update() for _ in range(len(outputs_ui_language))])

            def _restore_audiobook_player(session_id:str, audiobook:str|None)->tuple:
                try:
                    visible = True if audiobook is not None else False
                    return gr.update(visible=visible), gr.update(value=audiobook), gr.update(active=True)
                except Exception as e:
                    error = f'_restore_audiobook_player(): {e}'
                    exception_alert(session_id, error)
                    outputs = tuple([gr.update() for _ in range(3)])
                    return outputs

            def _change_gr_abs_library(session_id:str, url:str, api_token:str, library:str)->None:
                session = context.get_session(session_id)
                if session:
                    session['abs_library'] = library
                    session['abs_url'] = url
                    session['abs_api_token'] = api_token
                
            def _search_abs_libraries(session_id:str, url:str, api_token:str)->gr.update:
                from lib.classes.audiobookshelf import fetch_libraries
                if not url or not api_token:
                    return gr.update(choices=[('Enter URL + API Token to load libraries', '')], value=None)
                session = context.get_session(session_id)
                if not session or not session.get('id', False):
                    return gr.update(interactive=False)
                libs = fetch_libraries(url, api_token)
                if libs:
                    current = session.get('abs_library', '')
                    selected = current if any(v == current for _, v in libs) else libs[0][1]
                    session['abs_library'] = selected
                    session['abs_url'] = url
                    session['abs_api_token'] = api_token
                    return gr.update(choices=libs, value=selected)
                return gr.update(choices=[('No libraries found - check URL/API token', '')])

            def _click_gr_abs_upload_btn(session_id:str, audiobook:str, url:str, api_token:str, library_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if not session or not session.get('id', False):
                        return (gr.update(interactive=True), 'Session not found')
                    if not audiobook:
                        return (gr.update(interactive=True), 'No audiobook file to upload!')
                    elif not os.path.isfile(str(audiobook)):
                        return (gr.update(interactive=True), 'Audiobook file does not exist!')
                    from lib.classes.audiobookshelf import upload_to_abs
                    from urllib.parse import urlparse
                    title = Path(audiobook).stem
                    author = str(session.get('metadata', {}).get('creator') or '')
                    if not url or not api_token or not library_id:
                        return (gr.update(interactive=True), 'Configure ABS settings first')
                    parsed = urlparse(url)
                    if not parsed.scheme or not parsed.netloc:
                        return (gr.update(interactive=True), 'Invalid server URL')
                    ok, msg = upload_to_abs([audiobook], title, author, url, api_token, library_id)
                    if ok:
                        return (gr.update(interactive=True), f'{msg}')
                    else:
                        return (gr.update(interactive=True), f'Error: {msg}')
                except Exception as e:
                    return (gr.update(interactive=True), f'Error: {e}')

            def _abs_upload_enabled(session_id:str)->gr.update:
                session = context.get_session(session_id)
                if not session or not session.get('id', False):
                    return gr.update(interactive=False)
                if session.get('status') == status_tags['SWITCH']:
                    return gr.update(interactive=False)
                audiobook = session.get('audiobook')
                if not audiobook or not os.path.isfile(str(audiobook)):
                    return gr.update(interactive=False)
                if not (session.get('abs_url') and session.get('abs_api_token') and session.get('abs_library')):
                    return gr.update(interactive=False)
                return gr.update(interactive=True)

            def _refresh_interface(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session['cancellation_requested']:
                            session['status'] = status_tags['READY']
                        if session['status'] in [status_tags['READY'], status_tags['END']]:
                            visible_main = True
                            visible_xtts = False
                            visible_bark = False
                            visible_abs = visible_gr_tab_abs_params
                            visible_ebook_src = False
                            visible_ebook_textarea = False
                            enabled_convert_btn = False
                            ebook_data = None
                            ebook_textarea = None
                            if session['tts_engine'] == TTS_ENGINES['XTTS']:
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
                                gr.update(visible=visible_xtts), gr.update(visible=visible_bark), gr.update(visible=visible_abs),
                                gr.update(interactive=enabled_convert_btn), gr.update(visible=visible_ebook_src, value=ebook_data), gr.update(visible=visible_ebook_textarea, value=ebook_textarea),
                                gr.update(value=session['device']), gr.update(value=session['audiobook']), _update_gr_audiobook_list(session_id),
                                _update_gr_voice_list(session_id), gr.update(''), gr.update(value='')
                            )
                        elif session['status'] in [status_tags['CONVERTING']]:
                            return (
                                gr.update(), gr.update(), gr.update(), gr.update(),
                                gr.update(), gr.update(), gr.update(visible=True, value=session['ebook_list']), gr.update(),
                                gr.update(), gr.update(), gr.update(),
                                gr.update(), gr.update(), gr.update(value='')
                            )
                except Exception as e:
                    error = f'_refresh_interface(): {e}'
                    exception_alert(session_id, error)
                outputs = tuple([gr.update() for _ in range(14)])
                return outputs

            def _change_gr_audiobook_list(session_id:str, selected:str|None)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get('audiobook') != selected:
                            session['audiobook'] = selected
                        visible = session['audiobook'] is not None
                        audiobook = selected if selected else ''
                        return gr.update(visible=visible), gr.update(value=audiobook)
                except Exception as e:
                    error = f'_change_gr_audiobook_list(): {e}'
                    exception_alert(session_id, error)
                return gr.update(visible=False), gr.update(value='')

            def _update_gr_audiobook_player(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session['audiobook'] is not None: 
                            vtt = Path(session['audiobook']).with_suffix('.vtt')
                            if not os.path.exists(session['audiobook']) or not os.path.exists(vtt):
                                error = legends['error_file_not_found'].format(name=Path(session['audiobook']).name)
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
                                error = legends['error_audiobook_corrupted'].format(name=Path(session['audiobook']).name)
                                exception_alert(session_id, error)
                except Exception as e:
                    error = f'_update_gr_audiobook_player(): {e}'
                    exception_alert(session_id, error)
                return gr.update(value=0.0), gr.update(value=None), gr.update(value=None)

            def _update_gr_glassmask(str:str=gr_glassmask_msg, attr:list=['gr-glass-mask'])->dict:
                return gr.update(value=str, elem_id='gr_glassmask', elem_classes=attr)

            def _build_voice_highlight_css(row_index:int|None)->str:
                """Emit a <style> block highlighting tr.file:nth-child(N+1) inside #gr_ebook_src, or '' to clear."""
                if row_index is None:
                    return ''
                return (
                    f'<style>#gr_ebook_src table.file-preview tbody > tr.file:nth-child({row_index + 1}) '
                    f'{{ background: var(--color-accent-soft) !important; '
                    f'box-shadow: inset 4px 0 0 var(--color-accent) !important; '
                    f'font-weight: 600; }}</style>'
                )

            def _row_voice_player_visible(ebook_mode, selected)->bool:
                if ebook_mode != ebook_modes['DIRECTORY']:
                    return True
                return bool(selected)

            def _upload_gr_ebook_src(session_id:str, ebook_mode:str)->None:
                try:
                    if ebook_mode == ebook_modes['DIRECTORY']:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            session['ebook_selected'] = None
                            session['voice_map'] = {}
                            msg = legends['msg_click_each_file']
                            show_alert(session_id, {
                                'type': 'info',
                                'msg': msg
                            })
                except Exception as e:
                    error = f'_upload_gr_ebook_src(): {e}'
                    exception_alert(session_id, error)

            def _change_gr_ebook_src(session_id:str, ebook_mode:str, data:any)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if (session.get('ebook_src') == data and ebook_mode == ebook_modes['SINGLE']) or (session.get('ebook_list') == data and ebook_mode == ebook_modes['DIRECTORY']):
                            return gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(value='')
                        if ebook_mode == ebook_modes['SINGLE']:
                            session['ebook_src'] = data
                        elif ebook_mode == ebook_modes['DIRECTORY']:
                            session['ebook_list'] = data
                            files = data or []
                            ebook_files = [os.path.abspath(f) for f in files] if isinstance(files, list) else []
                            prev_map = dict(session.get('voice_map') or {})  # read once
                            default_voice = session.get('voice')
                            new_map = {p: (prev_map[p] if p in prev_map else default_voice) for p in ebook_files}
                            session['voice_map'] = new_map
                            prev_selected = session.get('ebook_selected')
                            if prev_selected and prev_selected in ebook_files:
                                new_row = ebook_files.index(prev_selected)
                                if data is None:
                                    session['cancellation_requested'] = True
                                else:
                                    session['cancellation_requested'] = False
                                return (
                                    gr.update(),
                                    gr.update(value=_build_voice_highlight_css(new_row)),
                                    gr.update(),
                                    gr.update(visible=True),
                                    gr.update(value=Path(prev_selected).name, visible=True),
                                    gr.update()
                                )
                            else:
                                session['ebook_selected'] = None
                                voice_update = gr.update(value=session.get('voice')) if prev_selected else gr.update()
                                if data is None and session.get('status', None) in [status_tags['EDIT'], status_tags['CONVERTING']]:
                                    session['cancellation_requested'] = True
                                    msg = legends['msg_cancellation_requested']
                                    return gr.update(value=_show_gr_modal('wait', msg), visible=True), gr.update(value=''), voice_update, gr.update(visible=False), gr.update(value='', visible=False), gr.update(value='')
                                session['cancellation_requested'] = False
                                return gr.update(), gr.update(value=''), voice_update, gr.update(visible=False), gr.update(value='', visible=False), gr.update(value='')
                        if data is None:
                            if session.get('status', None) in [status_tags['EDIT'], status_tags['CONVERTING']]:
                                session['cancellation_requested'] = True
                                msg = legends['msg_cancellation_requested']
                                return gr.update(value=_show_gr_modal('wait', msg), visible=True), gr.update(value=''), gr.update(), gr.update(), gr.update(), gr.update(value='')
                        session['cancellation_requested'] = False
                except Exception as e:
                    error = f'_change_gr_ebook_src(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), gr.update(value=''), gr.update(), gr.update(), gr.update(), gr.update()

            def _select_gr_ebook_src(session_id:str, ebook_mode:str, ebook_src:list|None, evt:gr.SelectData)->tuple:
                try:
                    session = context.get_session(session_id)
                    if not (session and session.get('id', False)):
                        return tuple(gr.update() for _ in range(4))
                    if ebook_mode != ebook_modes['DIRECTORY'] or evt.index is None:
                        return gr.update(), gr.update(value=''), gr.update(), gr.update(value='', visible=False)
                    if session.get('status') != status_tags['READY']:
                        return tuple(gr.update() for _ in range(4))
                    # evt.index can be int or (row, col) tuple — normalise.
                    row = evt.index[0] if isinstance(evt.index, (list, tuple)) else evt.index
                    live_list = ebook_src if isinstance(ebook_src, list) and ebook_src else None
                    ebook_list = live_list if live_list is not None else (session.get('ebook_list') or [])
                    if not isinstance(ebook_list, list) or row < 0 or row >= len(ebook_list):
                        return gr.update(), gr.update(value=''), gr.update(), gr.update(value='', visible=False)
                    ebook_path = os.path.abspath(ebook_list[row])
                    session['ebook_selected'] = ebook_path
                    if live_list is not None and session.get('ebook_list') != live_list:
                        session['ebook_list'] = live_list
                    voice_map = session.get('voice_map') or {}
                    assigned_voice = voice_map[ebook_path] if ebook_path in voice_map else session.get('voice')
                    style = _build_voice_highlight_css(row)
                    filename = Path(ebook_path).name
                    return (
                        gr.update(value=assigned_voice, label=legends['gr_voice_list']),
                        gr.update(value=style),
                        gr.update(visible=True),
                        gr.update(value=filename, visible=True),
                    )
                except Exception as e:
                    error = f'_select_gr_ebook_src(): {e}'
                    exception_alert(session_id, error)
                    return tuple(gr.update() for _ in range(4))

            def _change_gr_ebook_textarea(session_id:str, ebook_textarea:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('ebook_textarea') != ebook_textarea:
                        session['ebook_textarea'] = ebook_textarea
                return

            def _change_gr_ebook_mode(session_id:str, val:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get('ebook_mode') == val:
                            return tuple(gr.update() for _ in range(6))
                        session['ebook_mode'] = val
                        css_update = gr.update() if val == ebook_modes['DIRECTORY'] else gr.update(value='')
                        if val != ebook_modes['DIRECTORY']:
                            session['ebook_selected'] = None
                        row_visible = _row_voice_player_visible(session.get('ebook_mode'), session.get('ebook_selected'))
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
                    error = f'_change_gr_ebook_mode(): {e}'
                    exception_alert(session_id, error)
                return tuple(gr.update() for _ in range(6))

            def _change_gr_voice_file(session_id:str, f:str|None)->tuple:
                try:
                    state = {}
                    if f is not None:
                        if len(voice_options) > max_custom_voices:
                            error = legends['error_max_custom_voices'].format(max=max_custom_voices)
                            state['type'] = 'warning'
                            state['msg'] = error
                        elif os.path.splitext(f.name)[1] not in voice_formats:
                            error = legends['error_audio_format_invalid']
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
                                    if session.get('ebook_mode') == ebook_modes['DIRECTORY'] and session.get('ebook_selected'):
                                        voice_map = dict(session.get('voice_map') or {})
                                        voice_map[session['ebook_selected']] = final_voice_file
                                        session['voice_map'] = voice_map
                                    msg = legends['msg_voice_added'].format(name=voice_name)
                                    state['type'] = 'success'
                                    state['msg'] = msg
                                    show_alert(session_id, state)
                                    return _update_gr_voice_list(session_id)
                                else:
                                    error = legends['error_voice_upload_failed']
                                    state['type'] = 'warning'
                                    state['msg'] = error
                        show_alert(session_id, state)
                except Exception as e:
                    error = f'_change_gr_voice_file(): {e}'
                    exception_alert(session_id, error)
                return gr.update()

            def _change_gr_voice_list(session_id:str, selected:str|None)->tuple:
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
                    error = f'_change_gr_voice_list(): {e}'
                    exception_alert(session_id, error)
                return tuple(gr.update() for _ in range(3))

            def _click_gr_voice_del_btn(session_id:str, selected:str)->tuple:
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
                                error = legends['error_voice_builtin'].format(name=speaker)
                                show_alert(session_id, {"type": "warning", "msg": error})
                                return gr.update(visible=False), gr.update()
                            if is_in_models:
                                error = legends['error_voice_custom_model'].format(name=speaker)
                                show_alert(session_id, {"type": "warning", "msg": error})
                                return gr.update(visible=False), gr.update()                          
                            try:
                                selected_path = Path(selected).resolve()
                                parent_path = Path(session['voice_dir']).parent.resolve()
                                if parent_path in selected_path.parents:
                                    session['status'] = status_tags['DELETION']
                                    msg = legends['msg_confirm_delete'].format(name=speaker)
                                    return (
                                        gr.update(value=_show_gr_modal(session['status'], msg), visible=True),
                                        gr.update(value='confirm_voice_del')
                                    )
                                else:
                                    error = legends['error_voice_global'].format(name=speaker)
                                    show_alert(session_id, {"type": "warning", "msg": error})
                                    return gr.update(visible=False), gr.update()
                            except Exception as e:
                                error = legends['error_voice_delete_failed'].format(name=selected, e=e)
                                exception_alert(session_id, error)
                                return gr.update(visible=False), gr.update()
                    return gr.update(visible=False), gr.update()
                except Exception as e:
                    error = f'_click_gr_voice_del_btn(): {e}'
                    exception_alert(session_id, error)
                    return gr.update(visible=False), gr.update()

            def _click_gr_custom_model_del_btn(session_id:str, selected:str)->tuple:
                try:
                    if selected is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            selected_name = os.path.basename(selected)
                            session['status'] = status_tags['DELETION']
                            msg = legends['msg_confirm_delete'].format(name=selected_name)
                            return gr.update(value=_show_gr_modal(session['status'], msg), visible=True), gr.update(value='confirm_custom_model_del')
                except Exception as e:
                    error = legends['error_custom_model_delete_failed'].format(name=selected_name)
                    exception_alert(session_id, error)
                return gr.update(visible=False), gr.update()

            def _click_gr_audiobook_del_btn(session_id:str, selected:str)->tuple:
                try:
                    if selected is not None:
                        session = context.get_session(session_id)
                        if session and session.get('id', False):
                            selected_name = Path(selected).stem
                            session['status'] = status_tags['DELETION']
                            msg = legends['msg_confirm_delete'].format(name=selected_name)
                            return gr.update(value=_show_gr_modal(session['status'], msg), visible=True), gr.update(value='confirm_audiobook_del')
                except Exception as e:
                    error = legends['error_audiobook_delete_failed'].format(name=selected_name)
                    exception_alert(session_id, error)
                return gr.update(visible=False), gr.update()

            def _change_gr_audiobook_edit_btns(session_id:str, selected:str|None)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        busy = session['status'] in [status_tags['CONVERTING'], status_tags['EDIT']]
                        enabled = bool(selected) and not busy
                        pending = False
                        if selected and os.path.isfile(str(selected)) and session.get('session_dir'):
                            base_name = Path(selected).stem
                            process_dir = os.path.join(session['session_dir'], hashlib.md5(base_name.encode()).hexdigest())
                            if not os.path.isdir(process_dir):
                                part_match = re.match(r'^(.*)_part(\d+)$', base_name)
                                if part_match:
                                    base_name = part_match.group(1)
                                    process_dir = os.path.join(session['session_dir'], hashlib.md5(base_name.encode()).hexdigest())
                            pending = os.path.exists(os.path.join(process_dir, f"__edit_pending_{base_name}{Path(selected).suffix.lower()}"))
                        return gr.update(visible=pending, interactive=enabled), gr.update(interactive=enabled)
                except Exception as e:
                    error = f'_change_gr_audiobook_edit_btns(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), gr.update()

            def _update_audiobook_edit_lock(session_id:str)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get('audiobook_edit_block_id') is not None:
                            return tuple(gr.update(interactive=False) for _ in range(len(outputs_audiobook_edit_lock)))
                        enabled = _enable_components(session_id)
                        enabled_index = {id(component): i for i, component in enumerate(outputs_enable_components)}
                        return tuple(
                            enabled[enabled_index[id(component)]] if id(component) in enabled_index else gr.update(interactive=True)
                            for component in outputs_audiobook_edit_lock
                        )
                except Exception as e:
                    error = f'_update_audiobook_edit_lock(): {e}'
                    exception_alert(session_id, error)
                return tuple(gr.update() for _ in range(len(outputs_audiobook_edit_lock)))

            def _update_audiobook_edit_input(session_id:str)->tuple:
                # chained after ◉ and ✔, it also runs when they failed (gradio's .then): while an edit is still open the
                # sentence box and the editor buttons are usable again, ✔ only once a preview exists
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False) and session.get('audiobook_edit_block_id') is not None:
                        preview_file = session.get('audiobook_edit_preview')
                        return gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=bool(preview_file and os.path.exists(preview_file))), gr.update(interactive=True)
                except Exception as e:
                    error = f'_update_audiobook_edit_input(): {e}'
                    print(error)
                return gr.update(), gr.update(), gr.update(), gr.update()

            def _click_gr_audiobook_edit_btn(session_id:str, audiobook:str|None, cue:str|None)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        error = None
                        if session['status'] not in [status_tags['READY'], status_tags['END']]:
                            error = legends['error_editor_unavailable']
                        elif not audiobook or not os.path.exists(audiobook):
                            error = legends['error_no_audiobook_selected']
                        else:
                            cue_data = json.loads(cue) if cue else {}
                            cue_idx = int(cue_data['idx']) if cue_data.get('idx') is not None else -1
                            cue_text = ''.join(str(cue_data.get('text', '')).split())
                            # interlude cues carry the WebVTT id "interlude <block index>", see combine_audio_chapters()
                            interlude = int(cue_data['interlude']) if cue_data.get('interlude') is not None else None
                            if cue_idx < 0 and interlude is None:
                                error = legends['error_no_sentence_at_position']
                            else:
                                stem = Path(audiobook).stem
                                ext = Path(audiobook).suffix.lstrip('.').lower()
                                base_name = stem
                                cue_offset = 0
                                process_dir = os.path.join(session['session_dir'], hashlib.md5(stem.encode()).hexdigest())
                                if not os.path.isdir(process_dir):
                                    part_match = re.match(r'^(.*)_part(\d+)$', stem)
                                    if part_match:
                                        base_name = part_match.group(1)
                                        process_dir = os.path.join(session['session_dir'], hashlib.md5(base_name.encode()).hexdigest())
                                        part_width = len(part_match.group(2))
                                        for part_num in range(1, int(part_match.group(2))):
                                            part_vtt = Path(audiobook).with_name(f'{base_name}_part{part_num:0{part_width}d}.vtt')
                                            if not part_vtt.exists():
                                                error = legends['error_vtt_missing'].format(name=part_vtt.name)
                                                break
                                            with open(part_vtt, 'r', encoding='utf-8-sig', errors='replace') as f:
                                                part_lines = f.read().splitlines()
                                            # sentence cues only: interlude cues (id "interlude <block index>") are not sentences
                                            cue_offset += sum(1 for line in part_lines if '-->' in line) - sum(1 for line in part_lines if re.match(r'^interlude \d+$', line.strip()))
                                if error is None and not os.path.isdir(process_dir):
                                    error = legends['error_conversion_data_not_found'].format(stem=stem)
                                if error is None:
                                    audio_tags = {str(k).lower(): v for k, v in (mediainfo(audiobook).get('TAG') or {}).items()}
                                    if session.get('audiobook_edit_target') != audiobook or session.get('process_dir') != process_dir or not session.get('blocks_current'):
                                        saved_json = glob(os.path.join(process_dir, f"{file_prefixes['saved']}*.json"))
                                        current_db = glob(os.path.join(process_dir, f"{file_prefixes['current']}*.db"))
                                        blocks_saved = load_json_blocks(saved_json[0]) if saved_json else {}
                                        filename_noext = Path(saved_json[0]).stem[len(file_prefixes['saved']):] if blocks_saved.get('blocks') else None
                                        if filename_noext is None and current_db:
                                            blocks_saved = load_db_blocks(current_db[0])
                                            filename_noext = Path(current_db[0]).stem[len(file_prefixes['current']):]
                                        kept = [b for b in blocks_saved.get('blocks', []) if b['keep'] and b['text'].strip()]
                                        if not kept or not all(b.get('sentences') for b in kept):
                                            error = legends['error_conversion_data_incomplete_edit'].format(stem=stem)
                                        else:
                                            epub_path = os.path.join(process_dir, f'__{filename_noext}.epub')
                                            metadata = {key: None for key in session['metadata'].keys()}
                                            if os.path.exists(epub_path):
                                                epubBook = epub.read_epub(epub_path, {'ignore_ncx': True})
                                                for key in metadata.keys():
                                                    data = epubBook.get_metadata('DC', key)
                                                    if data:
                                                        for value, attributes in data:
                                                            metadata[key] = value
                                            metadata['language'] = audio_tags.get('language') or metadata['language']
                                            metadata['title'] = metadata['title'] or base_name.replace('_', ' ')
                                            metadata['creator'] = False if not metadata['creator'] or metadata['creator'] == 'Unknown' else metadata['creator']
                                            cover_path = os.path.join(process_dir, f'{filename_noext}.jpg')
                                            session['process_dir'] = process_dir
                                            session['chapters_dir'] = os.path.join(process_dir, 'chapters')
                                            session['sentences_dir'] = os.path.join(process_dir, 'chapters', 'sentences')
                                            session['interludes_dir'] = os.path.join(process_dir, 'chapters', 'interludes')
                                            session['filename_noext'] = filename_noext
                                            session['epub_path'] = epub_path
                                            session['blocks_orig_json'] = os.path.join(process_dir, f"{file_prefixes['clone']}{filename_noext}.json")
                                            session['blocks_saved_json'] = os.path.join(process_dir, f"{file_prefixes['saved']}{filename_noext}.json")
                                            session['blocks_current_db'] = os.path.join(process_dir, f"{file_prefixes['current']}{filename_noext}.db")
                                            session['final_name'] = f'{base_name}.{ext}'
                                            session['metadata'] = metadata
                                            session['cover'] = cover_path if os.path.exists(cover_path) else None
                                            session['blocks_saved'] = blocks_saved
                                            session['blocks_current'] = copy.deepcopy(blocks_saved)
                                            session['audiobook_edit_target'] = audiobook
                                    if error is None and interlude is not None:
                                        blocks = session['blocks_saved'].get('blocks', [])
                                        interlude_file = os.path.join(session['chapters_dir'], 'interludes', f'{interlude}-{interlude + 1}.{default_audio_proc_format}')
                                        session['audiobook_edit_pending'] = os.path.exists(os.path.join(session['process_dir'], f"__edit_pending_{session['final_name']}"))
                                        if not (0 <= interlude < len(blocks)) or not os.path.exists(interlude_file):
                                            error = legends['error_interlude_audio_not_found']
                                        else:
                                            # the prompt that made it (sidecar <name>.json), else the subtitle text without its ♪
                                            prompt = re.sub(r'^\s*♪\s*', '', str(cue_data.get('text', ''))).strip() or 'Interlude'
                                            try:
                                                with open(f'{os.path.splitext(interlude_file)[0]}.json', 'r', encoding='utf-8') as f:
                                                    prompt = ' '.join(str(json.load(f).get('prompt') or prompt).split())
                                            except (OSError, ValueError):
                                                pass
                                            session['audiobook_edit_block_id'] = blocks[interlude]['id']
                                            session['audiobook_edit_sentence_idx'] = None
                                            session['audiobook_edit_interlude'] = interlude
                                            session['audiobook_edit_preview'] = None
                                            session['audiobook_edit_preview_text'] = None
                                            if session['audiobook_edit_pending']:
                                                msg = legends['msg_unexported_edits'].format(name=Path(audiobook).name)
                                                show_alert(session_id, {"type": "info", "msg": msg})
                                            return (
                                                gr.update(value=prompt, interactive=True), gr.update(visible=True), gr.update(value=None),
                                                gr.update(interactive=True), gr.update(interactive=False), gr.update(interactive=True),
                                                gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False),
                                                gr.update(visible=session['audiobook_edit_pending'], interactive=False), gr.update(interactive=False),
                                                gr.update(visible='hidden')
                                            )
                                    if error is None:
                                        blocks_saved = session['blocks_saved']
                                        target_idx = cue_offset + cue_idx
                                        cue_count = 0
                                        block_id = None
                                        sentence_idx = None
                                        sentence = None
                                        for block in blocks_saved.get('blocks', []):
                                            if block_id is not None:
                                                break
                                            if not (block['keep'] and block['text'].strip()):
                                                continue
                                            for j, s in enumerate(block.get('sentences', [])):
                                                if not any(c.isalnum() for c in str(s)):
                                                    continue
                                                if cue_count == target_idx:
                                                    block_id, sentence_idx, sentence = block['id'], j, str(s)
                                                    break
                                                cue_count += 1
                                        session['audiobook_edit_pending'] = os.path.exists(os.path.join(session['process_dir'], f"__edit_pending_{session['final_name']}"))
                                        if block_id is None:
                                            error = legends['error_sentence_not_found']
                                        elif cue_text and ''.join(SML_TAG_PATTERN.sub('', sentence).split()) != cue_text:
                                            error = legends['error_vtt_out_of_sync']
                                        elif not os.path.exists(os.path.join(session['sentences_dir'], block_id, f'{sentence_idx}.{default_audio_proc_format}')):
                                            error = legends['error_sentence_audio_not_found']
                                        else:
                                            session['audiobook_edit_block_id'] = block_id
                                            session['audiobook_edit_sentence_idx'] = sentence_idx
                                            session['audiobook_edit_interlude'] = None
                                            session['audiobook_edit_preview'] = None
                                            session['audiobook_edit_preview_text'] = None
                                            final_language = session['translate'] if session.get('translate_enabled') and session.get('translate') else session['language']
                                            if audio_tags.get('language') and audio_tags['language'] != final_language:
                                                msg = legends['msg_language_differs_audiobook'].format(selected=final_language, other=audio_tags['language'])
                                                show_alert(session_id, {"type": "warning", "msg": msg})
                                            if session['audiobook_edit_pending']:
                                                msg = legends['msg_unexported_sentence_edits'].format(name=Path(audiobook).name)
                                                show_alert(session_id, {"type": "info", "msg": msg})
                                            return (
                                                gr.update(value=sentence, interactive=True), gr.update(visible=True), gr.update(value=None),
                                                gr.update(interactive=True), gr.update(interactive=False), gr.update(interactive=True),
                                                gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False),
                                                gr.update(visible=session['audiobook_edit_pending'], interactive=False), gr.update(interactive=False),
                                                gr.update(visible='hidden')
                                            )
                        if error is not None:
                            show_alert(session_id, {"type": "warning", "msg": error})
                except Exception as e:
                    error = f'_click_gr_audiobook_edit_btn(): {e}'
                    exception_alert(session_id, error)
                return tuple(gr.update() for _ in range(12))

            def _click_gr_audiobook_edit_sentence_btn(session_id:str, text:str|None)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False) and session.get('audiobook_edit_interlude') is not None:
                        # interlude: the text is its MusicGen prompt, ◉ generates a new take (unchanged prompt = another variation)
                        error = None
                        prompt = ' '.join(str(text or '').split())
                        interlude = session['audiobook_edit_interlude']
                        interlude_file = os.path.join(session['chapters_dir'], 'interludes', f'{interlude}-{interlude + 1}.{default_audio_proc_format}') if session.get('chapters_dir') else ''
                        if session['status'] not in [status_tags['READY'], status_tags['END']]:
                            error = legends['error_conversion_running']
                        elif not session.get('process_dir') or not os.path.exists(interlude_file):
                            error = legends['error_edit_context_lost']
                        elif len(prompt) > 500:
                            error = legends['error_interlude_prompt_limit']
                        elif not any(c.isalnum() for c in prompt):
                            error = legends['error_interlude_prompt_empty']
                        else:
                            preview_file = os.path.join(session['process_dir'], f'__edit_preview_interlude.{default_audio_proc_format}')
                            for f in (preview_file, f'{os.path.splitext(preview_file)[0]}.json'):
                                if os.path.exists(f):
                                    os.unlink(f)
                            session['audiobook_edit_preview'] = None
                            # same length and channel count as the interlude it replaces
                            interlude_info = mediainfo(interlude_file)
                            duration = int(min(interlude_duration_range[1], max(interlude_duration_range[0], round(float(interlude_info.get('duration') or 30)))))
                            channels = 1 if int(interlude_info.get('channels') or 2) == 1 else 2
                            from lib.classes.interlude_generator import InterludeGenerator
                            generator = None
                            session['status'] = status_tags['CONVERTING']
                            session['cancellation_requested'] = False
                            try:
                                msg = legends['msg_generating_interlude'].format(prompt=prompt)
                                print(msg)
                                progress_bar(0.0, desc=msg)
                                generator = InterludeGenerator(session['device'], channels, progress_bar)
                                if generator.generate_interlude(prompt, preview_file, duration=duration, samplerate=default_audio_proc_samplerate, desc='Interlude', is_cancelled=lambda: session['cancellation_requested']):
                                    session['audiobook_edit_preview'] = preview_file
                                    session['audiobook_edit_preview_text'] = prompt
                                    msg = legends['msg_interlude_generated']
                                    print(msg)
                                    progress_bar(1.0, desc=msg)
                                    return gr.update(value=preview_file), gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True)
                                error = legends['error_interlude_generation_failed']
                            finally:
                                # MusicGen runs in this process: release it right away
                                generator = None
                                import gc
                                gc.collect()
                                try:
                                    import torch
                                    if torch.cuda.is_available():
                                        torch.cuda.empty_cache()
                                except Exception:
                                    pass
                                session['status'] = status_tags['READY']
                        show_alert(session_id, {"type": "warning", "msg": error})
                        return gr.update(), gr.update(interactive=True), gr.update(interactive=bool(session.get('audiobook_edit_preview'))), gr.update(interactive=True)
                    if session and session.get('id', False):
                        error = None
                        raw_text = ' '.join(str(text or '').split())
                        res, text = normalize_sml_tags(raw_text)
                        block_id = session.get('audiobook_edit_block_id')
                        blocks_saved = session.get('blocks_saved') or {}
                        block = next((b for b in blocks_saved.get('blocks', []) if b['id'] == block_id), None)
                        lang = session['language']
                        if session.get('translate_enabled') and session.get('translate'):
                            lang = session['translate']
                        max_chars = int(language_mapping[lang]['max_chars'] / 1.5)
                        sentence_len = len(' '.join(SML_TAG_PATTERN.sub('', text).split()))
                        if session['status'] not in [status_tags['READY'], status_tags['END']]:
                            error = legends['error_conversion_running']
                        elif block is None or not session.get('process_dir'):
                            error = legends['error_edit_context_lost']
                        elif len(raw_text) > 500:
                            error = legends['error_sentence_field_limit']
                        elif res is False:
                            error = text
                        elif not any(c.isalnum() for c in text):
                            error = legends['error_sentence_no_alnum']
                        elif sentence_len > max_chars:
                            error = legends['error_sentence_too_long'].format(lang=lang, length=sentence_len, max=max_chars)
                        else:
                            # a duration normalize_sml_tags() could not read falls back to the default one: say so
                            dropped = (
                                sum(1 for m in SML_TAG_PATTERN.finditer(raw_text) if not TTS_SML.get(m.group('tag'), {}).get('paired') and (m.group('value') or '').strip())
                                - sum(1 for m in SML_TAG_PATTERN.finditer(text) if not TTS_SML.get(m.group('tag'), {}).get('paired') and (m.group('value') or '').strip())
                            )
                            if dropped > 0:
                                msg = legends['msg_sml_duration_dropped'].format(count=dropped)
                                show_alert(session_id, {"type": "warning", "msg": msg})
                            preview_file = os.path.join(session['process_dir'], f'__edit_preview.{default_audio_proc_format}')
                            if os.path.exists(preview_file):
                                os.unlink(preview_file)
                            session['audiobook_edit_preview'] = None
                            # the edit must be spoken by the engine the book was converted with, or the
                            # sentence files would not share the same stream params for the concat demuxer
                            engine_backup = (session['tts_engine'], session['fine_tuned'], session['model_cache'])
                            session['tts_engine'] = block.get('tts_engine') or session['tts_engine']
                            session['fine_tuned'] = block.get('fine_tuned') or session['fine_tuned']
                            session['model_cache'] = f"{session['tts_engine']}-{session['fine_tuned']}"
                            session['status'] = status_tags['CONVERTING']
                            session['cancellation_requested'] = False
                            tts_manager = None
                            converted = False
                            try:
                                msg = legends['msg_converting_edited_sentence'].format(engine=session['tts_engine'], text=text)
                                print(msg)
                                progress_bar(0.0, desc=msg)
                                tts_manager = TTSManager(session)
                                block_voice = block.get('voice') or session.get('voice')
                                converted, error = tts_manager.convert_sentence2audio(preview_file, text, block_voice=block_voice)
                                if converted and not os.path.exists(preview_file):
                                    converted, error = False, f'{Path(preview_file).name} was not created!'
                                if converted:
                                    session['audiobook_edit_preview'] = preview_file
                                    session['audiobook_edit_preview_text'] = text
                                    msg = legends['msg_edited_sentence_converted']
                                    print(msg)
                                    progress_bar(1.0, desc=msg)
                                    return gr.update(value=preview_file), gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True)
                            finally:
                                if not converted:
                                    unload_tts_manager(tts_manager)
                                session['tts_engine'], session['fine_tuned'], session['model_cache'] = engine_backup
                                session['status'] = status_tags['READY']
                        if error is not None:
                            show_alert(session_id, {"type": "warning", "msg": error})
                        return gr.update(), gr.update(interactive=True), gr.update(interactive=bool(session.get('audiobook_edit_preview'))), gr.update(interactive=True)
                except Exception as e:
                    error = f'_click_gr_audiobook_edit_sentence_btn(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), gr.update(interactive=True), gr.update(interactive=False), gr.update(interactive=True)

            def _click_gr_audiobook_edit_save_btn(session_id:str, text:str|None)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False) and session.get('audiobook_edit_interlude') is not None:
                        error = None
                        prompt = ' '.join(str(text or '').split())
                        interlude = session['audiobook_edit_interlude']
                        preview_file = session.get('audiobook_edit_preview')
                        interlude_file = os.path.join(session['chapters_dir'], 'interludes', f'{interlude}-{interlude + 1}.{default_audio_proc_format}') if session.get('chapters_dir') else ''
                        if session['status'] not in [status_tags['READY'], status_tags['END']]:
                            error = legends['error_conversion_running']
                        elif not os.path.exists(interlude_file):
                            error = legends['error_edit_context_lost']
                        elif not preview_file or not os.path.exists(preview_file):
                            error = legends['error_interlude_generate_first']
                        elif prompt != session.get('audiobook_edit_preview_text'):
                            error = legends['error_interlude_prompt_changed']
                        else:
                            interlude_json = f'{os.path.splitext(interlude_file)[0]}.json'
                            previous = {}
                            try:
                                with open(interlude_json, 'r', encoding='utf-8') as f:
                                    previous = json.load(f)
                            except (OSError, ValueError):
                                pass
                            os.replace(preview_file, interlude_file)
                            preview_json = f'{os.path.splitext(preview_file)[0]}.json'
                            if os.path.exists(preview_json):
                                os.replace(preview_json, interlude_json)
                                # same prompt, new take: it keeps its "mood · genre" label and origin
                                if previous.get('prompt') == prompt and previous.get('label'):
                                    with open(interlude_json, 'r', encoding='utf-8') as f:
                                        interlude_data = json.load(f)
                                    interlude_data.update({k: previous[k] for k in ('mood', 'family', 'genre', 'emotion', 'percussion', 'instruments', 'label') if k in previous})
                                    with open(interlude_json, 'w', encoding='utf-8') as f:
                                        json.dump(interlude_data, f, ensure_ascii=False)
                            Path(os.path.join(session['process_dir'], f"__edit_pending_{session['final_name']}")).touch()
                            session['audiobook_edit_pending'] = True
                            session['audiobook_edit_block_id'] = None
                            session['audiobook_edit_sentence_idx'] = None
                            session['audiobook_edit_interlude'] = None
                            session['audiobook_edit_preview'] = None
                            session['audiobook_edit_preview_text'] = None
                            msg = legends['msg_interlude_replaced']
                            print(msg)
                            show_alert(session_id, {"type": "success", "msg": msg})
                            enabled_convert_btn = (
                                session['ebook_mode'] == ebook_modes['TEXT']
                                or (session['ebook_mode'] == ebook_modes['SINGLE'] and bool(session.get('ebook_src')))
                                or (session['ebook_mode'] == ebook_modes['DIRECTORY'] and bool(session.get('ebook_list')))
                            )
                            shown = prompt
                            if previous.get('prompt') == prompt and previous.get('label'):
                                details = ' — '.join(str(previous[k]) for k in ('emotion', 'percussion', 'instruments') if previous.get(k)) or re.sub(r',\s*instrumental\s*$', '', prompt)
                                shown = f"{previous['label']} — {details}" if details else str(previous['label'])
                            return (
                                gr.update(value=f'♪ {shown}', interactive=False), gr.update(visible=False), gr.update(value=None),
                                gr.update(interactive=True), gr.update(interactive=False), gr.update(interactive=True),
                                gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True),
                                gr.update(visible=True, interactive=True), gr.update(interactive=enabled_convert_btn),
                                gr.update(visible=True)
                            )
                        show_alert(session_id, {"type": "warning", "msg": error})
                        return (
                            gr.update(), gr.update(), gr.update(),
                            gr.update(interactive=True), gr.update(interactive=bool(session.get('audiobook_edit_preview'))), gr.update(interactive=True),
                            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
                        )
                    if session and session.get('id', False):
                        error = None
                        text = ' '.join(str(text or '').split())
                        res, text = normalize_sml_tags(text)
                        block_id = session.get('audiobook_edit_block_id')
                        sentence_idx = session.get('audiobook_edit_sentence_idx')
                        preview_file = session.get('audiobook_edit_preview')
                        blocks_saved = session.get('blocks_saved') or {}
                        block = next((b for b in blocks_saved.get('blocks', []) if b['id'] == block_id), None)
                        if session['status'] not in [status_tags['READY'], status_tags['END']]:
                            error = legends['error_conversion_running']
                        elif block is None or sentence_idx is None or sentence_idx >= len(block.get('sentences', [])):
                            error = legends['error_edit_context_lost']
                        elif not preview_file or not os.path.exists(preview_file):
                            error = legends['error_sentence_convert_first']
                        elif res is False or text != session.get('audiobook_edit_preview_text'):
                            error = legends['error_sentence_text_changed']
                        else:
                            sentence_count = len(block['sentences'])
                            sentence_file = os.path.join(session['sentences_dir'], block_id, f'{sentence_idx}.{default_audio_proc_format}')
                            backup_file = f'{sentence_file}.bak'
                            chapter_file = os.path.join(session['chapters_dir'], f'{block_id}.{default_audio_proc_format}')
                            session['status'] = status_tags['CONVERTING']
                            session['cancellation_requested'] = False
                            try:
                                msg = legends['msg_replacing_sentence'].format(sentence=sentence_idx, block=block_id)
                                print(msg)
                                progress_bar(0.0, desc=msg)
                                os.replace(sentence_file, backup_file)
                                os.replace(preview_file, sentence_file)
                                session['audiobook_edit_preview'] = None
                                if combine_audio_sentences(session_id, chapter_file, block_id, sentence_count):
                                    # block_hash() covers the sentences: current and saved must get the very same
                                    # edit, or the next resume sees a changed block and reconverts it
                                    blocks_current = session['blocks_current']
                                    for blocks_data in (blocks_saved, blocks_current):
                                        for b in blocks_data.get('blocks', []):
                                            if b['id'] == block_id:
                                                sentences = list(b.get('sentences', []))
                                                if sentence_idx < len(sentences):
                                                    old_sentence = sentences[sentence_idx]
                                                    sentences[sentence_idx] = text
                                                    b['sentences'] = sentences
                                                    if old_sentence and b.get('text', '').count(old_sentence) == 1:
                                                        b['text'] = b['text'].replace(old_sentence, text, 1)
                                                break
                                    session['blocks_saved'] = blocks_saved
                                    session['blocks_current'] = blocks_current
                                    save_db_blocks(session_id)
                                    save_json_blocks(session_id, 'blocks_saved')
                                    os.unlink(backup_file)
                                else:
                                    os.replace(backup_file, sentence_file)
                                    combine_audio_sentences(session_id, chapter_file, block_id, sentence_count)
                                    error = 'combine_audio_sentences() failed! original sentence restored.'
                            finally:
                                session['status'] = status_tags['READY']
                            if error is None:
                                Path(os.path.join(session['process_dir'], f"__edit_pending_{session['final_name']}")).touch()
                                session['audiobook_edit_pending'] = True
                                session['audiobook_edit_block_id'] = None
                                session['audiobook_edit_sentence_idx'] = None
                                session['audiobook_edit_preview_text'] = None
                                msg = legends['msg_sentence_replaced']
                                print(msg)
                                show_alert(session_id, {"type": "success", "msg": msg})
                                enabled_convert_btn = (
                                    session['ebook_mode'] == ebook_modes['TEXT']
                                    or (session['ebook_mode'] == ebook_modes['SINGLE'] and bool(session.get('ebook_src')))
                                    or (session['ebook_mode'] == ebook_modes['DIRECTORY'] and bool(session.get('ebook_list')))
                                )
                                return (
                                    gr.update(value=re.sub(r'\s+', ' ', SML_TAG_PATTERN.sub('', text)).strip() or '…', interactive=False), gr.update(visible=False), gr.update(value=None),
                                    gr.update(interactive=True), gr.update(interactive=False), gr.update(interactive=True),
                                    gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True),
                                    gr.update(visible=True, interactive=True), gr.update(interactive=enabled_convert_btn),
                                    gr.update(visible=True)
                                )
                        show_alert(session_id, {"type": "warning", "msg": error})
                        return (
                            gr.update(), gr.update(), gr.update(),
                            gr.update(interactive=True), gr.update(interactive=bool(session.get('audiobook_edit_preview'))), gr.update(interactive=True),
                            gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update()
                        )
                except Exception as e:
                    error = f'_click_gr_audiobook_edit_save_btn(): {e}'
                    exception_alert(session_id, error)
                return (gr.update(), gr.update(), gr.update(), gr.update(interactive=True), gr.update(interactive=False), gr.update(interactive=True), gr.update(), gr.update(), gr.update(), gr.update(), gr.update(), gr.update())

            def _click_gr_audiobook_edit_cancel_btn(session_id:str)->tuple:
                sentence_update = gr.update(interactive=False)
                enabled_convert_btn = False
                pending = False
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        preview_file = session.get('audiobook_edit_preview')
                        if preview_file and os.path.exists(preview_file):
                            os.unlink(preview_file)
                        if preview_file and os.path.exists(f'{os.path.splitext(preview_file)[0]}.json'):
                            os.unlink(f'{os.path.splitext(preview_file)[0]}.json')
                        block_id = session.get('audiobook_edit_block_id')
                        sentence_idx = session.get('audiobook_edit_sentence_idx')
                        blocks_saved = session.get('blocks_saved') or {}
                        block = next((b for b in blocks_saved.get('blocks', []) if b['id'] == block_id), None)
                        if block is not None and sentence_idx is not None and sentence_idx < len(block.get('sentences', [])):
                            sentence_update = gr.update(value=re.sub(r'\s+', ' ', SML_TAG_PATTERN.sub('', str(block['sentences'][sentence_idx]))).strip() or '…', interactive=False)
                        interlude = session.get('audiobook_edit_interlude')
                        if interlude is not None and session.get('chapters_dir'):
                            prompt = 'Interlude'
                            try:
                                with open(os.path.join(session['chapters_dir'], 'interludes', f'{interlude}-{interlude + 1}.json'), 'r', encoding='utf-8') as f:
                                    interlude_data = json.load(f)
                                # same text as its subtitle cue (see combine_audio_chapters()): "mood · genre — emotion — percussion — instruments",
                                # or the prompt typed in the editor
                                prompt = str(interlude_data.get('prompt') or prompt)
                                if interlude_data.get('label'):
                                    details = ' — '.join(str(interlude_data[k]) for k in ('emotion', 'percussion', 'instruments') if interlude_data.get(k)) or re.sub(r',\s*instrumental\s*$', '', prompt)
                                    prompt = f"{interlude_data['label']} — {details}" if details else str(interlude_data['label'])
                                prompt = ' '.join(prompt.split())
                            except (OSError, ValueError):
                                pass
                            sentence_update = gr.update(value=f'♪ {prompt}', interactive=False)
                        session['audiobook_edit_block_id'] = None
                        session['audiobook_edit_sentence_idx'] = None
                        session['audiobook_edit_interlude'] = None
                        session['audiobook_edit_preview'] = None
                        session['audiobook_edit_preview_text'] = None
                        pending = bool(session.get('audiobook_edit_pending'))
                        if not pending and session['status'] in [status_tags['READY'], status_tags['END']]:
                            reset_ebook_session(session_id, force=True, filter_keys=False)
                        enabled_convert_btn = (
                            session['ebook_mode'] == ebook_modes['TEXT']
                            or (session['ebook_mode'] == ebook_modes['SINGLE'] and bool(session.get('ebook_src')))
                            or (session['ebook_mode'] == ebook_modes['DIRECTORY'] and bool(session.get('ebook_list')))
                        )
                except Exception as e:
                    error = f'_click_gr_audiobook_edit_cancel_btn(): {e}'
                    exception_alert(session_id, error)
                return (
                    sentence_update, gr.update(visible=False), gr.update(value=None),
                    gr.update(interactive=True), gr.update(interactive=False), gr.update(interactive=True),
                    gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True),
                    gr.update(visible=pending, interactive=True), gr.update(interactive=enabled_convert_btn),
                    gr.update(visible=True)
                )

            def _click_gr_audiobook_export_btn(session_id:str, audiobook:str|None)->tuple:
                convert_update = gr.update()
                visible_export = False
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        error = None
                        target = audiobook
                        if session['status'] not in [status_tags['READY'], status_tags['END']]:
                            error = legends['error_conversion_running']
                        elif not target or not os.path.exists(target):
                            error = legends['error_no_audiobook_selected']
                        elif Path(target).suffix.lstrip('.').lower() not in output_formats:
                            error = legends['error_output_format_unsupported'].format(ext=Path(target).suffix)
                        else:
                            stem = Path(target).stem
                            ext = Path(target).suffix.lstrip('.').lower()
                            base_name = stem
                            process_dir = os.path.join(session['session_dir'], hashlib.md5(stem.encode()).hexdigest())
                            if not os.path.isdir(process_dir):
                                part_match = re.match(r'^(.*)_part(\d+)$', stem)
                                if part_match:
                                    base_name = part_match.group(1)
                                    process_dir = os.path.join(session['session_dir'], hashlib.md5(base_name.encode()).hexdigest())
                            chapters_dir = os.path.join(process_dir, 'chapters')
                            pending_marker = os.path.join(process_dir, f'__edit_pending_{base_name}.{ext}')
                            visible_export = os.path.exists(pending_marker)
                            audio_info = mediainfo(target)
                            if not visible_export:
                                error = legends['error_nothing_to_export']
                            elif session.get('audiobook_edit_target') != target or session.get('process_dir') != process_dir or not session.get('blocks_current'):
                                # 📦 without ✎ first (other audiobook edited meanwhile, reload, restart): attach the conversion data
                                saved_json = glob(os.path.join(process_dir, f"{file_prefixes['saved']}*.json"))
                                current_db = glob(os.path.join(process_dir, f"{file_prefixes['current']}*.db"))
                                blocks_saved = load_json_blocks(saved_json[0]) if saved_json else {}
                                filename_noext = Path(saved_json[0]).stem[len(file_prefixes['saved']):] if blocks_saved.get('blocks') else None
                                if filename_noext is None and current_db:
                                    blocks_saved = load_db_blocks(current_db[0])
                                    filename_noext = Path(current_db[0]).stem[len(file_prefixes['current']):]
                                kept = [b for b in blocks_saved.get('blocks', []) if b['keep'] and b['text'].strip()]
                                if not kept or not all(b.get('sentences') for b in kept):
                                    error = legends['error_conversion_data_incomplete_export'].format(stem=stem)
                                else:
                                    audio_tags = {str(k).lower(): v for k, v in (audio_info.get('TAG') or {}).items()}
                                    epub_path = os.path.join(process_dir, f'__{filename_noext}.epub')
                                    metadata = {key: None for key in session['metadata'].keys()}
                                    if os.path.exists(epub_path):
                                        epubBook = epub.read_epub(epub_path, {'ignore_ncx': True})
                                        for key in metadata.keys():
                                            data = epubBook.get_metadata('DC', key)
                                            if data:
                                                for value, attributes in data:
                                                    metadata[key] = value
                                    metadata['language'] = audio_tags.get('language') or metadata['language']
                                    metadata['title'] = metadata['title'] or base_name.replace('_', ' ')
                                    metadata['creator'] = False if not metadata['creator'] or metadata['creator'] == 'Unknown' else metadata['creator']
                                    cover_path = os.path.join(process_dir, f'{filename_noext}.jpg')
                                    session['process_dir'] = process_dir
                                    session['chapters_dir'] = chapters_dir
                                    session['sentences_dir'] = os.path.join(chapters_dir, 'sentences')
                                    session['interludes_dir'] = os.path.join(chapters_dir, 'interludes')
                                    session['filename_noext'] = filename_noext
                                    session['epub_path'] = epub_path
                                    session['blocks_orig_json'] = os.path.join(process_dir, f"{file_prefixes['clone']}{filename_noext}.json")
                                    session['blocks_saved_json'] = os.path.join(process_dir, f"{file_prefixes['saved']}{filename_noext}.json")
                                    session['blocks_current_db'] = os.path.join(process_dir, f"{file_prefixes['current']}{filename_noext}.db")
                                    session['final_name'] = f'{base_name}.{ext}'
                                    session['metadata'] = metadata
                                    session['cover'] = cover_path if os.path.exists(cover_path) else None
                                    session['blocks_saved'] = blocks_saved
                                    session['blocks_current'] = copy.deepcopy(blocks_saved)
                                    session['audiobook_edit_target'] = target
                            if error is None:
                                # rebuild with the audiobook's own format, channels and split mode, not the current UI settings
                                is_split = Path(target).stem != Path(session['final_name']).stem
                                channels = int(audio_info.get('channels') or (2 if session['output_channel'] == 'stereo' else 1))
                                output_backup = (session['output_format'], session['output_channel'], session['output_split'], session.get('interlude_enabled', False))
                                session['output_format'] = ext
                                session['output_channel'] = 'stereo' if channels >= 2 else 'mono'
                                session['output_split'] = is_split
                                # interludes too: kept if this audiobook has them (interlude cues in its subtitles), whatever Music Interlude says now
                                target_vtt = Path(target).with_suffix('.vtt')
                                if target_vtt.exists():
                                    session['interlude_enabled'] = bool(re.search(r'(?m)^interlude \d+\s*$', target_vtt.read_text(encoding='utf-8', errors='replace')))
                                else:
                                    interludes_dir = os.path.join(session['chapters_dir'], 'interludes')
                                    session['interlude_enabled'] = os.path.isdir(interludes_dir) and any(f.endswith(f'.{default_audio_proc_format}') and not f.startswith('__') for f in os.listdir(interludes_dir))
                                session['status'] = status_tags['CONVERTING']
                                session['cancellation_requested'] = False
                                exported_files = None
                                try:
                                    msg = legends['msg_rebuilding_audiobook'].format(name=Path(session['final_name']).name)
                                    print(msg)
                                    progress_bar(0.0, desc=msg)
                                    exported_files = combine_audio_chapters(session_id)
                                finally:
                                    session['output_format'], session['output_channel'], session['output_split'], session['interlude_enabled'] = output_backup
                                    session['status'] = status_tags['READY']
                                if not exported_files:
                                    error = 'combine_audio_chapters() failed!'
                                else:
                                    if is_split:
                                        part_pattern = re.compile(rf"^{re.escape(Path(session['final_name']).stem)}_part\d+\.{re.escape(ext)}$")
                                        for f in os.listdir(session['audiobooks_dir']):
                                            part_file = os.path.join(session['audiobooks_dir'], f)
                                            if part_pattern.match(f) and part_file not in exported_files:
                                                os.remove(part_file)
                                                part_vtt = Path(part_file).with_suffix('.vtt')
                                                if part_vtt.exists():
                                                    os.remove(part_vtt)
                                    session['audiobook'] = target if target in exported_files else exported_files[0]
                                    if os.path.exists(pending_marker):
                                        os.unlink(pending_marker)
                                    reset_ebook_session(session_id, force=True, filter_keys=False)
                                    visible_export = False
                                    msg = legends['msg_audiobook_rebuilt'].format(name=Path(session['audiobook']).name)
                                    print(msg)
                                    show_alert(session_id, {"type": "success", "msg": msg})
                        if error is not None:
                            show_alert(session_id, {"type": "warning", "msg": error})
                        if session['status'] in [status_tags['READY'], status_tags['END']]:
                            convert_update = gr.update(interactive=(
                                session['ebook_mode'] == ebook_modes['TEXT']
                                or (session['ebook_mode'] == ebook_modes['SINGLE'] and bool(session.get('ebook_src')))
                                or (session['ebook_mode'] == ebook_modes['DIRECTORY'] and bool(session.get('ebook_list')))
                            ))
                        list_update = _update_gr_audiobook_list(session_id)
                        list_update['interactive'] = True
                        return (
                            gr.update(visible=visible_export, interactive=True),
                            gr.update(interactive=True), list_update, gr.update(interactive=True), convert_update
                        )
                except Exception as e:
                    error = f'_click_gr_audiobook_export_btn(): {e}'
                    exception_alert(session_id, error)
                return gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True), gr.update(interactive=True), convert_update

            def _click_gr_deletion(session_id:str, voice_path:str, custom_model:str, audiobook:str, method:str|None=None)->tuple:
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
                                    msg = legends['msg_voice_deleted'].format(name=re.sub(r".wav$", "", selected_name))
                                    show_alert(session_id, {'type': 'info', 'msg': msg})
                                    return gr.update(value='', visible=False), gr.update(), gr.update(), _update_gr_voice_list(session_id)
                                elif method == 'confirm_custom_model_del':
                                    selected_name = os.path.basename(custom_model)
                                    shutil.rmtree(custom_model, ignore_errors=True)                           
                                    msg = legends['msg_custom_model_deleted'].format(name=selected_name)
                                    if session['custom_model'] is not None and session['voice'] is not None:
                                        if session['custom_model'] in session['voice']:
                                            session['voice'] = models[session['fine_tuned']]['voice']
                                    session['custom_model'] = None
                                    show_alert(session_id, {"type": "info", "msg": msg})
                                    return gr.update(value='', visible=False), _update_gr_custom_model_list(session_id), gr.update(),  gr.update()
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
                                        language = session['translate'] if session['translate_enabled'] and session['translate'] is not None else session['language']
                                        process_dir = os.path.join(session['session_dir'], hashlib.md5((selected_name).encode()).hexdigest())
                                        shutil.rmtree(process_dir, ignore_errors=True)
                                    msg = legends['msg_audiobook_deleted'].format(name=selected_name)
                                    session['audiobook'] = None
                                    show_alert(session_id, {"type": "info", "msg": msg})
                                    return gr.update(value='', visible=False), gr.update(), _update_gr_audiobook_list(session_id), gr.update()
                except Exception as e:
                    error = f'_click_gr_deletion(): {e}!'
                    exception_alert(session_id, error)
                return  gr.update(value='', visible=False), gr.update(), gr.update(), gr.update()

            def _update_gr_voice_list(session_id:str)->dict:
                try:
                    nonlocal models, voice_options
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        models = load_engine_presets(session['tts_engine'])
                        language = session['translate'] if session['translate_enabled'] and session['translate'] is not None else session['language']
                        lang_dir = language if language != 'con' else 'con-'  # Bypass Windows CON reserved name
                        file_pattern = "*.wav"
                        eng_options = []
                        bark_options = []
                        piper_options = []
                        builtin_dir = Path(os.path.join(voices_dir, lang_dir))
                        builtin_options = [
                            (base, str(f))
                            for f in builtin_dir.rglob(file_pattern)
                            for base in [os.path.splitext(f.name)[0]]
                        ]
                        builtin_names = {t[0]: None for t in builtin_options}
                        if language in default_engine_settings[TTS_ENGINES['XTTS']].get('languages', {}):
                            eng_dir = Path(os.path.join(voices_dir, "eng"))
                            eng_options = [
                                (base, str(f))
                                for f in eng_dir.rglob(file_pattern)
                                for base in [os.path.splitext(f.name)[0]]
                                if base not in builtin_names
                            ]
                        if session['tts_engine'] == TTS_ENGINES['BARK']:
                            lang_dict = Lang(language)
                            if lang_dict:
                                lang_iso1 = lang_dict.pt1
                                lang = lang_iso1.lower()
                                speakers_path = Path(default_engine_settings[TTS_ENGINES['BARK']]['speakers_path'])
                                pattern_speaker = re.compile(r"^.*?_speaker_(\d+)$")
                                bark_options = [
                                    (pattern_speaker.sub(r"Speaker \1", f.stem), str(f.with_suffix(".wav")))
                                    for f in speakers_path.rglob(f"{lang}_speaker_*.npz")
                                ]
                        elif session['tts_engine'] == TTS_ENGINES['PIPER']:
                            engine_config = default_engine_settings[TTS_ENGINES['PIPER']]
                            lang_piper = engine_config['languages'][language]  # e.g., "en_GB"
                            speakers_path = Path(engine_config['speakers_path'])
                            voices_map = engine_config['voices']
                            for f in speakers_path.iterdir():
                                if f.name.startswith(lang_piper):
                                    file_stem = f.stem
                                    display_name = f'Speaker {voices_map.get(file_stem, file_stem)}'
                                    wav_path = str(f.with_suffix('.wav'))
                                    piper_options.append((display_name, wav_path))
                        voice_options = builtin_options + eng_options + bark_options + piper_options
                        session['voice_dir'] = os.path.join(voices_dir, '__sessions', f'voice-{session_id}', language)
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
                            voice_options = [(legends['gr_voice_list_default'], None)] + sorted(voice_options, key=lambda x: x[0].lower())
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
                                            parts[idx + 1] = language
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
                        if session['status'] in [status_tags['READY'], status_tags['END']]:
                            voice_values = {v[1] for v in voice_options}
                            blocks_current = session.get('blocks_current') or {}
                            blocks_changed = False
                            for block in blocks_current.get('blocks') or []:
                                if 'voice' in block and block['voice'] not in voice_values:
                                    block['voice'] = session['voice']
                                    blocks_changed = True
                                if 'tts_engine' in block and block['tts_engine'] != session['tts_engine']:
                                    block['tts_engine'] = session['tts_engine']
                                    blocks_changed = True
                                if 'fine_tuned' in block and block['fine_tuned'] != session['fine_tuned']:
                                    block['fine_tuned'] = session['fine_tuned']
                                    blocks_changed = True
                            if 'voice' in blocks_current and blocks_current['voice'] not in voice_values:
                                blocks_current['voice'] = session['voice']
                                blocks_changed = True
                            if blocks_changed:
                                session['blocks_current'] = blocks_current
                                save_db_blocks(session_id)
                            voice_map = dict(session.get('voice_map') or {})
                            voice_map_changed = False
                            for ebook_path, ebook_voice in voice_map.items():
                                if ebook_voice not in voice_values:
                                    voice_map[ebook_path] = session['voice']
                                    voice_map_changed = True
                            if voice_map_changed:
                                session['voice_map'] = voice_map
                        selected_voice = session['voice']
                        if session.get('ebook_mode') == ebook_modes['DIRECTORY'] and session.get('ebook_selected'):
                            selected_voice = (session.get('voice_map') or {}).get(session['ebook_selected'], session['voice'])
                        return gr.update(choices=voice_options, value=selected_voice, label=legends['gr_voice_list'])
                except Exception as e:
                    error = f'_update_gr_voice_list(): {e}!'
                    exception_alert(session_id, error)
                return gr.update()

            def _update_gr_translate_list(session_id:str)->dict:
                session = context.get_session(session_id)
                if not session or not session.get('id', False):
                    return gr.update()
                lang = session.get('language')
                translate = session.get('translate')
                translate_iso1 = session['translate_iso1']
                translate_options = _build_translate_targets(lang)
                if translate_options:
                    lang_order = {val: i for i, (_, val) in enumerate(language_options)}
                    translate_options.sort(key=lambda item: lang_order.get(item[1], len(language_options)))
                    if not translate or not any(translate == val for _, val in translate_options):
                        translate = translate_options[0][1]
                    try:
                        translate_iso1 = Lang(translate).pt1
                    except Exception:
                        translate_iso1 = None
                else:
                    msg = legends['msg_no_translate_languages']
                    translate = None
                    translate_iso1 = None
                    translate_options.append((msg, None))
                session['translate'] = translate
                session['translate_iso1'] = translate_iso1
                visible_gr_translate = True if session.get('translate_enabled') else False
                return gr.update(visible=visible_gr_translate, choices=translate_options, value=translate)

            def _update_gr_tts_engine_list(session_id:str)->dict:
                try:
                    nonlocal tts_engine_options
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        language = session['language']
                        if session.get('translate_enabled') and session.get('translate'):
                            language = session['translate']
                        tts_engine_options = get_compatible_tts_engines(language)
                        if session['tts_engine'] not in tts_engine_options:
                            session['tts_engine'] = tts_engine_options[0]
                        return gr.update(choices=tts_engine_options, value=session['tts_engine'])
                except Exception as e:
                    error = f'_update_gr_tts_engine_list(): {e}!'
                    exception_alert(session_id, error)              
                return gr.update()

            def _update_gr_custom_model_list(session_id:str)->dict:
                try:
                    nonlocal custom_model_options
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        custom_model_tts_dir = _check_custom_model_tts(session['custom_model_dir'], session['tts_engine'])
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
                    error = f'_update_gr_custom_model_list(): {e}!'
                    exception_alert(session_id, error)
                return gr.update()

            def _update_gr_fine_tuned_list(session_id:str)->dict:
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
                        return gr.update(choices=fine_tuned_options, value=session['fine_tuned'], label=legends['gr_fine_tuned_list'])
                except Exception as e:
                    error = f'_update_gr_fine_tuned_list(): {e}!'
                    exception_alert(session_id, error)              
                return gr.update()

            def _change_gr_device(session_id:str, selected:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('device') != selected:
                        session['device'] = selected
                return

            def _change_gr_language(session_id:str, selected:str)->tuple:
                session = context.get_session(session_id)
                if not session or not session.get('id', False):
                    return tuple(gr.update() for _ in range(4))
                if session.get('language') != selected:
                    session['language'] = selected
                    return (
                        _update_gr_translate_list(session_id),
                        _update_gr_tts_engine_list(session_id),
                        _update_gr_custom_model_list(session_id),
                        _update_gr_fine_tuned_list(session_id)
                    )
                return tuple(gr.update() for _ in range(4))

            def _click_gr_translate_enabled(session_id:str, checked:bool)->tuple:
                session = context.get_session(session_id)
                if not session or not session.get('id', False):
                    return tuple(gr.update() for _ in range(5))
                if session['translate_enabled'] != checked:
                    session['translate_enabled'] = checked
                    return (
                        _update_gr_translate_list(session_id),
                        _update_gr_tts_engine_list(session_id),
                        _update_gr_custom_model_list(session_id),
                        _update_gr_fine_tuned_list(session_id),
                        _update_gr_voice_list(session_id)
                    )
                return tuple(gr.update() for _ in range(5))

            def _change_gr_translate(session_id:str, translate:str)->tuple:
                session = context.get_session(session_id)
                if not session or not session.get('id', False):
                    return tuple(gr.update() for _ in range(3))
                if translate != session['translate']:
                    session['translate'] = translate
                    try:
                        session['translate_iso1'] = Lang(translate).pt1
                    except Exception:
                        session['translate_iso1'] = None
                    return (
                        _update_gr_tts_engine_list(session_id),
                        _update_gr_custom_model_list(session_id),
                        _update_gr_fine_tuned_list(session_id)
                    )
                return tuple(gr.update() for _ in range(3))

            def _check_custom_model_tts(custom_model_dir:str, tts_engine:str)->str|None:
                dir_path = None
                if custom_model_dir is not None and tts_engine is not None:
                    dir_path = os.path.join(custom_model_dir, tts_engine)
                    if not os.path.isdir(dir_path):
                        os.makedirs(dir_path, exist_ok=True)
                return dir_path

            def _change_gr_custom_model_file(session_id:str, custom_file:str|None, tts_engine:str)->tuple:
                try:
                    nonlocal models
                    if custom_file is not None:
                        state = {}
                        if len(custom_model_options) > max_custom_model:
                            error = legends['error_max_custom_models'].format(max=max_custom_model)
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
                                        msg = legends['msg_custom_model_added'].format(name=os.path.basename(model))
                                        state['type'] = 'success'
                                        state['msg'] = msg
                                        show_alert(session_id, state)
                                        return gr.update(value=None), _update_gr_custom_model_list(session_id)
                                    else:
                                        error = legends['error_custom_model_extract_failed'].format(name=os.path.basename(custom_file))
                                        state['type'] = 'warning'
                                        state['msg'] = error
                                else:
                                    error = legends['error_custom_model_invalid'].format(name=os.path.basename(custom_file))
                                    state['type'] = 'warning'
                                    state['msg'] = error
                        show_alert(session_id, state)
                except Exception as e:
                    error = f'_change_gr_custom_model_file(): {e}'
                    exception_alert(session_id, error)
                return gr.update(value=None), gr.update()

            def _change_gr_custom_model_list(session_id:str, selected:str|None)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        session['custom_model'] = selected
                        if selected is not None and session['tts_engine'] not in tts_engines_with_inner_speaker:
                            session['voice'] = os.path.join(selected, f'{os.path.basename(selected)}.wav')
                        visible_fine_tuned = True if session['custom_model'] is None else False
                        visible_del_btn = True if session['custom_model'] is not None else False
                        return gr.update(visible=visible_fine_tuned), _update_gr_voice_list(session_id), gr.update(visible=visible_del_btn)
                except Exception as e:
                    error = f'_change_gr_custom_model_list(): {e}'
                    exception_alert(session_id, error)
                return tuple(gr.update() for _ in range(3))

            def _change_gr_tts_engine_list(session_id:str, engine:str)->tuple:
                try:
                    nonlocal models
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get('tts_engine') != engine or session.get('translate_enabled'):
                            models = load_engine_presets(engine)
                            session['voice'] = None if session['voice'] == default_engine_settings[session['tts_engine']]['voice'] else session['voice']
                            session['tts_engine'] = engine
                            session['fine_tuned'] = default_fine_tuned
                            visible_xtts = visible_gr_tab_xtts_params if session['tts_engine'] == TTS_ENGINES['XTTS'] else False
                            visible_bark = visible_gr_tab_bark_params if session['tts_engine'] == TTS_ENGINES['BARK'] else False
                            supports_custom = session['tts_engine'] in tts_engines_with_custom_model
                            visible_custom_model = supports_custom and session['fine_tuned'] == 'internal'
                            if supports_custom:
                                file_label = legends['gr_custom_model_file_engine'].format(engine=session['tts_engine'].upper(), files=', '.join(models[default_fine_tuned]['files']))
                                custom_model_list_update = _update_gr_custom_model_list(session_id)
                            else:
                                file_label = legends['gr_custom_model_file_unavailable'].format(engine=session['tts_engine'])
                                custom_model_list_update = gr.update()
                            return (
                                gr.update(value=_show_rating(session['tts_engine'])),
                                gr.update(visible=visible_xtts),
                                gr.update(visible=visible_bark),
                                gr.update(visible=visible_custom_model),
                                _update_gr_fine_tuned_list(session_id),
                                gr.update(label=file_label),
                                custom_model_list_update
                            )
                except Exception as e:
                    error = f'_change_gr_tts_engine_list(): {e}'
                    exception_alert(session_id, error)
                return tuple(gr.update() for _ in range(7))

            def _change_gr_fine_tuned_list(session_id:str, selected:str)->dict:
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
                    error = f'_change_gr_fine_tuned_list(): {e}'
                    exception_alert(session_id, error)
                return gr.update()

            def _change_gr_output_format_list(session_id:str, val:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('output_format') != val:
                        session['output_format'] = val
                return

            def _change_gr_output_channel_list(session_id:str, val:str)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('output_channel') != val:
                        session['output_channel'] = val
                return
    
            def _change_gr_output_split(session_id:str, val:str)->dict:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['output_split'] = val
                return gr.update(visible=val)

            def _click_gr_session_switch_btn(session_id:str, backup_session_id:str|None)->tuple:
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
                            msg = legends['msg_backup_session_id']
                            show_alert(back_id, {"type": "warning", "msg": msg})
                            return gr.update(), gr.update(interactive=True), back_id, gr.update(value='🔑︎'), back_id, None
                        elif session['status'] == status_tags['SWITCH']:
                            if new_id is None or not new_id.strip():
                                msg = legends['msg_session_id_empty']
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
                                msg = legends['msg_session_not_found']
                                show_alert(back_id, {"type": "warning", "msg": msg})
                except Exception as e:
                    error = f'_click_gr_session_switch_btn(): {e}'
                    exception_alert(back_id, error)
                return gr.update(), gr.update(), backup_session_id, gr.update(), None, None

            def _change_gr_playback_time(session_id:str, time:float)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session.get('playback_time') != time:
                        session['playback_time'] = time
                return

            def _toggle_audiobook_files(session_id:str, audiobook:str, is_visible:bool, refresh_only:bool=False)->tuple:
                try:
                    if not audiobook:
                        error = legends['error_no_audiobook_selected']
                        show_alert(session_id, {"type": "error", "msg": error})
                        return gr.update(), False
                    if is_visible and not refresh_only:
                        return gr.update(visible=False, value=None), False
                    file = Path(audiobook)
                    if not file.exists():
                        error = legends['error_audio_not_found'].format(file=file)
                        show_alert(session_id, {"type": "error", "msg": error})
                        return gr.update(visible=False, value=None), False
                    files = [str(file)]
                    vtt = file.with_suffix('.vtt')
                    if vtt.exists():
                        files.append(str(vtt))
                    return gr.update(visible=True, value=files), True
                except Exception as e:
                    error = f'_toggle_audiobook_files(): {e}!'
                    exception_alert(session_id, error)
                return gr.update(), False

            def _change_param(key:str, session_id:str, val:Any, val2:Any=None)->None:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        if session.get(key) != val:
                            session[key] = val
                            state = {}
                            if key == 'xtts_length_penalty':
                                if val2 is not None:
                                    if float(val) > float(val2):
                                        error = legends['error_length_penalty_rule']   
                                        state['type'] = 'warning'
                                        state['msg'] = error
                                        show_alert(session_id, state)
                            elif key == 'xtts_num_beams':
                                if val2 is not None:
                                    if float(val) < float(val2):
                                        error = legends['error_num_beams_rule']   
                                        state['type'] = 'warning'
                                        state['msg'] = error
                                        show_alert(session_id, state)
                except Exception as e:
                    error = f'_change_param(): {e}'
                    exception_alert(session_id, error)
                return

            def _start_conversion(
                    session_id:str, device:str, ebook_mode:str, ebook_src:str|list|None, ebook_textarea:str|None, blocks_preview:bool, interlude_enabled:bool, tts_engine:str, language:str, voice:str, custom_model:str, fine_tuned:str, output_format:str, output_channel:str, xtts_temperature:float, 
                    xtts_length_penalty:int, xtts_num_beams:int, xtts_repetition_penalty:float, xtts_top_k:int, xtts_top_p:float, xtts_speed:float, xtts_enable_text_splitting:bool, bark_text_temp:float, bark_waveform_temp:float,
                    output_split:bool, output_split_hours:str,
                    translate_enabled:bool, translate_target:str|None
                )->tuple:
                error = None
                try:
                    session = context.get_session(session_id)
                    reset_ebook_session(session_id, force=True, filter_keys=False)
                    if session and session.get('id', False):
                        if not session['cancellation_requested']:
                            args = {
                                "id": session_id,
                                "is_gui_process": session['is_gui_process'],
                                "script_mode": script_mode,
                                "blocks_preview": blocks_preview,
                                "interlude_enabled": interlude_enabled,
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
                                "output_split_hours": output_split_hours,
                                "translate_enabled": bool(translate_enabled),
                                "translate": translate_target if translate_enabled else None,
                                "translate_iso1": (Lang(translate_target).pt1 if (translate_enabled and translate_target) else None)
                            }
                            if args['ebook_mode'] == ebook_modes['DIRECTORY']:
                                if isinstance(args['ebook_list'], list):
                                    if not args['ebook_list']:
                                        error = legends['error_directory_required']
                            elif args['ebook_mode'] == ebook_modes['SINGLE']:
                                if not args['ebook_src']:
                                    error = legends['error_ebook_required']
                            elif args['ebook_mode'] == ebook_modes['TEXT']:
                                if not args['ebook_textarea']:
                                    error = legends['error_textarea_empty']
                                elif len(args['ebook_textarea']) < 10:
                                    error = legends['error_textarea_too_short']
                                else:
                                    args['ebook_textarea'] = args['ebook_textarea'].strip()
                                    if len(args['ebook_textarea']) < 10:
                                        error = legends['error_textarea_too_short']                                
                            if error is None:
                                session['ticker'] = len(audiobook_options)
                                if args['ebook_mode'] == ebook_modes['DIRECTORY']:
                                    if args['ebook_list']:
                                        if isinstance(args['ebook_list'], list):
                                            default_voice = session.get('voice')
                                            voice_map = dict(session.get('voice_map') or {})
                                            clean_list = [
                                                f for f in args['ebook_list']
                                                if any(f.endswith(ext) for ext in ebook_formats)
                                            ]
                                            clean_list.sort(key=natural_sort_key)
                                            for skipped in [f for f in args['ebook_list'] if f not in clean_list]:
                                                show_alert(session_id, {
                                                    "type": "warning",
                                                    "msg": legends['msg_unsupported_format_skipping'].format(name=Path(skipped).name)
                                                })
                                            ebook_list_full = copy.deepcopy(clean_list)
                                            args['ebook_list'] = ebook_list_full
                                            queue = list(ebook_list_full)
                                            if args['blocks_preview']:
                                                selected = session.get('ebook_selected')
                                                ebook_map = {os.path.abspath(p): p for p in ebook_list_full}
                                                if selected and selected in ebook_map:
                                                    queue = [ebook_map[selected]]
                                                else:
                                                    queue = ebook_list_full[:1]
                                            last_progress_status = None
                                            while queue:
                                                file = queue.pop(0)
                                                args['ebook_src'] = file
                                                ebook_file = os.path.abspath(file)
                                                if ebook_file in voice_map:
                                                    override = voice_map[ebook_file]
                                                elif os.path.basename(file) in voice_map:
                                                    override = voice_map[os.path.basename(file)]
                                                else:
                                                    override = default_voice
                                                if override is not None and override != default_voice and not os.path.exists(override):
                                                    msg = legends['msg_voice_override_not_found'].format(name=Path(file).name)
                                                    show_alert(session_id, {
                                                        "type": "warning",
                                                        "msg": msg
                                                    })
                                                    override = default_voice
                                                args['voice'] = override
                                                progress_status, passed = convert_ebook(args)
                                                if not passed:
                                                    error = progress_status or legends['error_conversion_failed'].format(name=ebook_name)
                                                    break
                                                last_progress_status = progress_status
                                                if args['blocks_preview']:
                                                    break
                                            if error is None:
                                                return gr.update(value=last_progress_status)                         
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
                                if session['cancellation_requested']:
                                    msg = legends['msg_conversion_cancelled']
                                    show_alert(session_id, {"type": "warning", "msg": msg})
                                    if session['status'] == status_tags['DISCONNECTED']:
                                        context_tracker.end_session(session_id, session['socket_hash'])
                                        return gr.update()
                                else:
                                    show_alert(session_id, {"type": "warning", "msg": error})
                                session['status'] = status_tags['END']
                            return gr.update(value=error)
                        else:
                            return gr.update()
                except Exception as e:
                    session['status'] = status_tags['END']
                    error = f'_start_conversion(): {e}'
                    exception_alert(session_id, error)
                    return gr.update(value=error)

            def _update_gr_audiobook_list(session_id:str)->dict:
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
                    error = f'_update_gr_audiobook_list(): {e}!'
                    exception_alert(session_id, error)              
                return gr.update()

            def _check_override_ebook(session_id:str, ebook_mode:str, ebook_data:any, ebook_textarea:str, blocks_preview:bool, event:int, translate_enabled:bool, translate_target:str|None)->tuple:
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
                                            error = legends['error_directory_required']
                                        else:
                                            source = ebook_data[0]
                                    elif ebook_mode == ebook_modes['SINGLE']:
                                        if not ebook_data:
                                            error = legends['error_ebook_required']
                                        else:
                                            source = ebook_data
                                    elif ebook_mode == ebook_modes['TEXT']:
                                        if not ebook_textarea:
                                            error = legends['error_textarea_empty']
                                        elif len(ebook_textarea) < 10:
                                            error = legends['error_textarea_too_short']
                                        else:
                                            ebook_textarea = ebook_textarea.strip()
                                            if len(ebook_textarea) < 10:
                                                error = legends['error_textarea_too_short']
                                            else:
                                                source = ebook_textarea
                                if error is None:
                                    if source is not None:
                                        if ebook_mode == ebook_modes['TEXT']:
                                            session['status'] = status_tags['SKIP']
                                            session['ebook_textarea'] = source
                                            return gr.update(), (event + 1)
                                        else:
                                            session['ebook_src'] = source
                                            stem_base = get_sanitized(Path(source).stem)
                                            if translate_enabled and translate_target and translate_target != session.get('language'):
                                                language = translate_target
                                                ebook_name = f"{stem_base}_{translate_target}"
                                            else:
                                                language = session.get('language')
                                                ebook_name = stem_base
                                            final_name = f"{ebook_name}.{session['output_format']}"
                                            process_dir = os.path.join(session['session_dir'], hashlib.md5((ebook_name).encode()).hexdigest())
                                            chapters_dir = os.path.join(process_dir, 'chapters')
                                            sentences_dir = os.path.join(chapters_dir, 'sentences')
                                            pre_name = f"{ebook_name}{'_part1.' if session['output_split'] else '.'}{default_audio_proc_format}"
                                            pre_file = os.path.join(process_dir, pre_name)
                                            final_file = os.path.join(session['audiobooks_dir'], final_name)
                                            audio_sentences_exist = False
                                            if os.path.exists(sentences_dir):
                                                audio_sentences_exist = any(Path(sentences_dir).rglob(f'*.{default_audio_proc_format}'))
                                            if os.path.exists(pre_file) or audio_sentences_exist:
                                                session['status'] = status_tags['OVERRIDE']
                                                session['audiobook_overridden'] = final_file
                                                msg = legends['msg_resume_warning'].format(name=final_name)
                                                # audio exists, so the previous global voice matters: if it differs from
                                                # the one selected now, the blocks that follow the global voice will be
                                                # reconverted. warn in the same modal rather than a second one.
                                                if ebook_mode == ebook_modes['DIRECTORY']:
                                                    voice_map = dict(session.get('voice_map') or {})
                                                    current_voice = voice_map.get(os.path.abspath(source),
                                                                    voice_map.get(os.path.basename(source), session.get('voice')))
                                                else:
                                                    current_voice = session.get('voice')
                                                voice_note = build_voice_change_note(process_dir, current_voice)
                                                if voice_note:
                                                    msg += voice_note
                                                return gr.update(value=_show_gr_modal(session['status'], msg), visible=True), event
                                            else:
                                                session['status'] = status_tags['SKIP']
                                                return gr.update(), (event + 1)
                                else:
                                    show_alert(session_id, {"type": "warning", "msg": error})
                                session['status'] = status_tags['END']
                except Exception as e:
                    error = f'_check_override_ebook(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), event

            def _click_gr_override_cancel_btn(session_id:str)->dict:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    session['status'] = status_tags['END']
                    session['audiobook_overridden'] = None
                return gr.update(value='', visible=False)

            def _click_gr_override_confirm_btn(session_id:str, event:int, audiobook_files_state:bool)->tuple:
                try:
                    session = context.get_session(session_id)
                    if session and session.get('id', False):
                        file_converting = session['audiobook_overridden']
                        files_update = gr.update()
                        files_state_update = gr.update()
                        if file_converting:
                            idx = next((i for i, t in enumerate(audiobook_options) if t[1] == file_converting), -1)
                            new_list = [t for t in audiobook_options if t[1] != file_converting]
                            if session['audiobook'] == file_converting or session['audiobook'] in new_list:
                                print('_click_gr_override_confirm_btn():  select audiobook is the converting file')
                                new_selected = None
                                if new_list:
                                    new_idx = max(0, idx - 1)
                                    new_selected = new_list[new_idx][1]
                                session['audiobook'] = new_selected
                                if audiobook_files_state and new_selected is not None:
                                    files_update, files_state_update = _toggle_audiobook_files(session_id, new_selected, False)
                                else:
                                    files_update = gr.update(visible=False, value=None)
                                    files_state_update = False
                                return gr.update(value='', visible=False), (event + 1), gr.update(choices=new_list, value=new_selected), files_update, files_state_update
                        return gr.update(value='', visible=False), (event + 1), gr.update(), files_update, files_state_update
                except Exception as e:
                    error = f'_click_gr_override_confirm_btn(): {e}'
                    exception_alert(session_id, error)
                return gr.update(), event, gr.update(), gr.update(), gr.update()

            def _populate_page(session_id:str, page:int, blocks:list[dict], with_open:bool=True)->tuple:
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
                                if with_open:
                                    updates.append(gr.update(label=legends['block_label'].format(idx=idx), visible=True, open=exp))
                                else:
                                    updates.append(gr.update(label=legends['block_label'].format(idx=idx), visible=True))
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
                        header = gr.update(value=legends['gr_blocks_header'].format(start=start, end=end-1, total=len(blocks)-1))
                        return (*updates, header, expands)
                return tuple(gr.update() for _ in range(len(blocks_components_flat) + 2))

            def _navigate(session_id:str, page:int, blocks:list[dict], direction:int, *args)->tuple:
                new_blocks = _collect_page(page, blocks, *args)
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
                    error = f'_navigate(): {e}'
                    exception_alert(session_id, error)
                return (
                    new_blocks,
                    new_page,
                    gr.update(interactive=new_page > 0),
                    gr.update(interactive=new_page < max_page),
                )

            def _edit_blocks(session_id:str)->tuple:
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
                                page_updates = list(_populate_page(session_id, page, blocks, with_open=False))
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
                    error = f'_edit_blocks(): {e}'
                    exception_alert(session_id, error)
                n = len(blocks_components_flat) + 1
                return tuple(gr.update() for _ in range(9 + n + 1))

            def _click_reset_block(session_id:str, block_id:int)->dict:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    text = session['blocks_orig']['blocks'][block_id]['text']
                    return gr.update(value=text)
                return gr.update()

            def _collect_page(page:int, blocks:list[dict], *args)->list[dict]:
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

            def _change_current_blocks(session_id:str, page:int, blocks:list[dict], *args)->None:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    new_blocks = _collect_page(page, blocks, *args)
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

            def _click_gr_blocks_cancel_btn(session_id:str, page:int, blocks:list[dict], *args)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session['status'] in [status_tags['EDIT']]:
                        session['status'] = status_tags['READY']
                        _change_current_blocks(session_id, page, blocks, *args)
                return gr.update(interactive=True), gr.update(visible=True), _update_gr_audiobook_list(session_id), gr.update(visible=False), session['blocks_current']['blocks']

            def _click_gr_blocks_confirm_btn(session_id:str, event:int, page:int, blocks:list[dict], *args)->tuple:
                session = context.get_session(session_id)
                if session and session.get('id', False):
                    if session['status'] in [status_tags['EDIT']]:
                        if not any(b['keep'] and b['text'].strip() for b in blocks):
                            error = legends['error_keep_one_block']
                            show_alert(session_id, {'type': 'warning', 'msg': error})
                            return tuple(gr.update() for _ in range(6))
                        _change_current_blocks(session_id, page, blocks, *args)
                        return gr.update(interactive=False), gr.update(interactive=False), gr.update(visible=True), gr.update(visible=False), _update_gr_audiobook_list(session_id), (event + 1)
                return tuple(gr.update() for _ in range(6))

            def _change_gr_restore_session(data:DictProxy|None, state:dict, req:gr.Request)->tuple:
                try:
                    nonlocal models
                    msg = legends['msg_session_load_error']
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
                        error = legends['error_session_already_active']
                        return gr.update(), gr.update(), gr.update(value=''), _update_gr_glassmask(str=error)
                    else:
                        active_sessions.add(req.session_hash)
                        session[req.session_hash] = req.session_hash
                        session['cancellation_requested'] = False
                        session['ui_language'] = session.get('ui_language_choice') or next((legends_iso1[tag.split(';')[0].strip().split('-')[0].lower()] for tag in req.headers.get('accept-language', '').split(',') if tag.split(';')[0].strip().split('-')[0].lower() in legends_iso1), system_language)
                        ui_language.set(session['ui_language'])
                    if isinstance(session.get('ebook'), str):
                        if not os.path.exists(session['ebook']):
                            session['ebook'] = session['ebook_src'] = None
                    if isinstance(session.get('voice'), str):
                        if not os.path.exists(session['voice']):
                            session['voice'] = None
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
                    if session.get('translate_enabled'):
                        translate_target = session.get('translate')
                        if not translate_target or translate_target not in language_mapping:
                            session['translate_enabled'] = False
                            session['translate'] = None
                            session['translate_iso1'] = None
                    effective_lang = session.get('language')
                    if session.get('translate_enabled') and session.get('translate'):
                        effective_lang = session['translate']
                    if effective_lang:
                        compatible = get_compatible_tts_engines(effective_lang)
                        if compatible and session.get('tts_engine') not in compatible:
                            session['tts_engine'] = compatible[0]
                            session['fine_tuned'] = default_fine_tuned
                            models = load_engine_presets(session['tts_engine'])
                    if isinstance(session.get('audiobook'), str):
                        if not os.path.exists(session['audiobook']):
                            session['audiobook'] = None
                    if session.get('audiobook_edit_preview') and os.path.exists(session['audiobook_edit_preview']):
                        os.unlink(session['audiobook_edit_preview'])
                    session['audiobook_edit_block_id'] = None
                    session['audiobook_edit_sentence_idx'] = None
                    session['audiobook_edit_interlude'] = None
                    session['audiobook_edit_preview'] = None
                    session['audiobook_edit_preview_text'] = None
                    session['status'] = status_tags['READY']
                    session['is_gui_process'] = is_gui_process
                    session['system'] = DEVICE_SYSTEM
                    session['session_dir'] = os.path.join(tmp_dir, f"proc-{session['id']}")
                    session['custom_model_dir'] = os.path.join(models_dir, '__sessions', f"model-{session['id']}")
                    session['voice_dir'] = os.path.join(voices_dir, '__sessions', f"voice-{session['id']}", session['language'])
                    os.makedirs(session['custom_model_dir'], exist_ok=True)
                    os.makedirs(session['voice_dir'], exist_ok=True)     
                    if is_gui_shared:
                        msg = legends['msg_shared_access_limit'].format(days=interface_shared_tmp_expire)
                        session['audiobooks_dir'] = os.path.join(audiobooks_gradio_dir, f"web-{session['id']}")
                        delete_unused_tmp_dirs(session['id'], audiobooks_gradio_dir, interface_shared_tmp_expire)
                    else:
                        msg = legends['msg_session_cleanup_notice'].format(days=tmp_expire)
                        session['audiobooks_dir'] = os.path.join(audiobooks_host_dir, f"web-{session['id']}")
                        delete_unused_tmp_dirs(session['id'], audiobooks_host_dir, tmp_expire)
                    msg += legends['msg_cookies_required']
                    if not os.path.exists(session['audiobooks_dir']):
                        os.makedirs(session['audiobooks_dir'], exist_ok=True)
                    previous_hash = state['hash']
                    new_hash = hash_proxy_dict(MappingProxyType(session))
                    state['hash'] = new_hash
                    show_alert(session['id'], {"type": "info", "msg": msg})
                    return gr.update(value=json.dumps(session, cls=JSONDictProxyEncoder)), gr.update(value=state), gr.update(value=session['id']), gr.update()
                except Exception as e:
                    error = f'_change_gr_restore_session(): {e}'
                    exception_alert(None, error)
                    return tuple(gr.update() for _ in range(4))

            async def _update_gr_save_session(session_id:str, state:dict)->tuple:
                try:
                    session = context.get_session(session_id)
                    if not session or (session and not session.get('id', False)):
                        yield tuple(gr.update() for _ in range(3))
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
                                    _update_gr_audiobook_list(session_id),
                                )
                            else:
                                yield tuple(gr.update() for _ in range(3))
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
                            yield tuple(gr.update() for _ in range(3))
                        else:
                            state['hash'] = new_hash
                            session_filtered = {k: v for k, v in session.items() if k not in save_session_keys_except}
                            session_dict = json.dumps(session_filtered, cls=JSONDictProxyEncoder)
                            yield (
                                gr.update(value=session_dict),
                                gr.update(value=state),
                                gr.update(),
                            )
                    yield tuple(gr.update() for _ in range(3))
                except Exception as e:
                    error = f'_update_gr_save_session(): {e}!'
                    exception_alert(session_id, error)
                    yield gr.update(), gr.update(value=e), gr.update()

            ################## Events Section

            def _chain_check_override(event):
                return event.then(
                    fn=_check_override_ebook,
                    inputs=[gr_session, gr_ebook_mode, gr_ebook_src, gr_ebook_textarea, gr_blocks_preview, gr_event, gr_translate_enabled, gr_translate],
                    outputs=[gr_modal, gr_event],
                    show_progress_on=[gr_progress]
                )

            def _chain_refresh(event):
                return event.then(
                    fn=_refresh_interface,
                    inputs=[gr_session],
                    outputs=outputs_refresh_interface,
                    show_progress_on=[gr_progress]
                )

            def _chain_enable(event, always=False):
                if always:
                    return event.then(
                        fn=lambda s: (
                            list(_enable_components(s)) + [
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
                            _enable_components(s) + (1,)
                            if context.get_session(s)['status'] in [status_tags['END'], status_tags['READY']]
                            and context.get_session(s)['ebook_mode'] == ebook_modes['TEXT']
                            else (
                                _enable_components(s) + (0,)
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
                gr_session, gr_device, gr_ebook_mode, gr_ebook_src, gr_ebook_textarea, gr_blocks_preview, gr_interlude_enabled, gr_tts_engine_list, gr_language, gr_voice_list,
                gr_custom_model_list, gr_fine_tuned_list, gr_output_format_list, gr_output_channel_list,
                gr_xtts_temperature, gr_xtts_length_penalty, gr_xtts_num_beams, gr_xtts_repetition_penalty, gr_xtts_top_k, gr_xtts_top_p, gr_xtts_speed, gr_xtts_enable_text_splitting,
                gr_bark_text_temp, gr_bark_waveform_temp, gr_output_split, gr_output_split_hours,
                gr_translate_enabled, gr_translate
            ]
            outputs_disable_components = [
                gr_ebook_textarea, gr_ebook_mode, gr_blocks_preview, gr_interlude_enabled, gr_language, gr_voice_file, gr_voice_list,
                gr_device, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file,
                gr_custom_model_list, gr_output_format_list, gr_output_channel_list, gr_output_split, gr_output_split_hours,
                gr_translate_enabled, gr_translate,
                gr_convert_btn, gr_voice_play, gr_voice_del_btn, gr_custom_model_del_btn, gr_session_switch_btn,
                gr_abs_upload_btn,
                gr_audiobook_edit_btn, gr_audiobook_export_btn, gr_audiobook_sentence, gr_row_audiobook_edit, gr_audiobook_edit_player,
                gr_audiobook_list, gr_audiobook_del_btn, gr_audiobook_player
            ]
            outputs_enable_components = [
                gr_ebook_textarea, gr_ebook_mode, gr_blocks_preview, gr_language, gr_voice_file, gr_voice_list,
                gr_device, gr_tts_engine_list, gr_fine_tuned_list, gr_custom_model_file,
                gr_custom_model_list, gr_output_format_list, gr_output_channel_list, gr_output_split, gr_output_split_hours,
                gr_translate_enabled, gr_translate,
                gr_voice_play, gr_voice_del_btn, gr_session_switch_btn, gr_blocks_cancel_btn, gr_blocks_confirm_btn, gr_custom_model_del_btn, gr_modal, gr_convert_btn,
                gr_abs_upload_btn,
                gr_audiobook_edit_btn, gr_audiobook_export_btn,
                # kept last: _enable_components() addresses the items above by position
                gr_interlude_enabled
            ]
            outputs_edit_blocks = [
                gr_blocks_markdown, gr_group_main, gr_group_blocks,
                gr_blocks_data, gr_blocks_page,
                gr_blocks_back_btn, gr_blocks_next_btn,
                gr_blocks_cancel_btn, gr_blocks_confirm_btn,
                *blocks_components_flat, gr_blocks_header, gr_blocks_expands
            ]
            outputs_restore_interface = [
                gr_tab_xtts_params, gr_tab_bark_params, gr_ebook_src, gr_ebook_textarea, gr_ebook_mode, gr_blocks_preview, gr_interlude_enabled, gr_device, gr_language,
                gr_translate_enabled, gr_translate, gr_voice_list, gr_tts_engine_list, gr_tts_rating,
                gr_custom_model_list, gr_fine_tuned_list, gr_output_format_list, gr_output_channel_list,
                gr_output_split, gr_output_split_hours, gr_row_output_split_hours, gr_audiobook_list, gr_group_custom_model, gr_convert_btn,
                gr_voice_player_hidden, gr_voice_play, gr_voice_del_btn, gr_row_voice_player, gr_custom_model_file, gr_custom_model_del_btn,
                gr_abs_url, gr_abs_api_token, gr_abs_library, gr_abs_upload_btn, gr_abs_audiobook
            ]
            outputs_ui_language = [
                gr_tab_main, gr_tab_xtts_params, gr_tab_bark_params, gr_tab_abs_params, gr_import_markdown, gr_ebook_textarea,
                gr_ebook_mode, gr_blocks_preview, gr_interlude_enabled, gr_language_markdown, gr_translate_enabled, gr_voice_markdown,
                gr_voice_file, gr_voice_list, gr_device_markdown, gr_tts_rating, gr_models_markdown, gr_fine_tuned_list,
                gr_custom_model_file, gr_output_markdown, gr_output_format_list, gr_output_channel_list, gr_output_split,
                gr_output_split_hours_markdown, gr_session_markdown, gr_progress_markdown, gr_audiobook_markdown,
                gr_xtts_temperature, gr_xtts_length_penalty, gr_xtts_num_beams, gr_xtts_repetition_penalty, gr_xtts_top_k,
                gr_xtts_top_p, gr_xtts_speed, gr_xtts_enable_text_splitting, gr_markdown_tab_bark_params, gr_bark_text_temp,
                gr_bark_waveform_temp, gr_abs_url, gr_abs_api_token, gr_abs_audiobook, gr_abs_status, gr_ui_language
            ]
            outputs_refresh_interface = [
                gr_modal, gr_group_main, gr_tab_xtts_params, gr_tab_bark_params, gr_tab_abs_params, gr_convert_btn,
                gr_ebook_src, gr_ebook_textarea, gr_device, gr_audiobook_player, gr_audiobook_list,
                gr_voice_list, gr_voice_highlight_css, gr_progress
            ]
            outputs_audiobook_edit = [
                gr_audiobook_sentence, gr_row_audiobook_edit, gr_audiobook_edit_player,
                gr_audiobook_edit_preview_btn, gr_audiobook_edit_save_btn, gr_audiobook_edit_cancel_btn,
                gr_audiobook_edit_btn, gr_audiobook_list, gr_audiobook_del_btn, gr_audiobook_export_btn, gr_convert_btn,
                gr_audiobook_player
            ]
            outputs_audiobook_edit_lock = [
                gr_ebook_src, gr_ebook_textarea, gr_ebook_mode, gr_blocks_preview, gr_interlude_enabled, gr_language, gr_translate_enabled, gr_translate,
                gr_voice_file, gr_voice_play, gr_voice_list, gr_voice_del_btn, gr_device, gr_tts_engine_list, gr_fine_tuned_list,
                gr_custom_model_file, gr_custom_model_list, gr_custom_model_del_btn,
                gr_output_format_list, gr_output_channel_list, gr_output_split, gr_output_split_hours,
                gr_session_switch_btn, gr_audiobook_download_btn,
                gr_abs_url, gr_abs_api_token, gr_abs_library, gr_abs_search_btn, gr_abs_upload_btn,
                gr_xtts_temperature, gr_xtts_length_penalty, gr_xtts_num_beams, gr_xtts_repetition_penalty, gr_xtts_top_k, gr_xtts_top_p, gr_xtts_speed, gr_xtts_enable_text_splitting,
                gr_bark_text_temp, gr_bark_waveform_temp
            ]
            outputs_on_voice_upload = [
                gr_ebook_src, gr_ebook_textarea, gr_ebook_mode, gr_language, gr_tts_engine_list,
                gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list, gr_session_switch_btn,
                gr_convert_btn, gr_voice_play, gr_voice_del_btn
            ]
            outputs_on_custom_upload = [
                gr_ebook_src, gr_ebook_textarea, gr_ebook_mode, gr_language, gr_tts_engine_list,
                gr_fine_tuned_list, gr_voice_file, gr_session_switch_btn,
                gr_voice_play, gr_voice_del_btn, gr_convert_btn, gr_custom_model_del_btn
            ]
            
            ######### event triggers
            
            gr_ebook_src.upload(
                fn=_upload_gr_ebook_src,
                inputs=[gr_session, gr_ebook_mode],
                outputs=None,
                show_progress_on=[gr_ebook_src]
            )
            _chain_enable(
                gr_ebook_src.change(
                    fn=_change_gr_ebook_src,
                    inputs=[gr_session, gr_ebook_mode, gr_ebook_src],
                    outputs=[gr_modal, gr_voice_highlight_css, gr_voice_list, gr_row_voice_player, gr_voice_selected_filename, gr_progress],
                    show_progress_on=[gr_ebook_src]
                ),
                always=True
            )
            gr_ebook_src.select(
                fn=_select_gr_ebook_src,
                inputs=[gr_session, gr_ebook_mode, gr_ebook_src],
                outputs=[gr_voice_list, gr_voice_highlight_css, gr_row_voice_player, gr_voice_selected_filename],
                show_progress='hidden'
            )
            gr_ebook_textarea.change(
                fn=_change_gr_ebook_textarea,
                inputs=[gr_session, gr_ebook_textarea],
                outputs=None
            )
            gr_ebook_mode.change(
                fn=_change_gr_ebook_mode,
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
                fn=lambda session_id, val: _change_param('blocks_preview', session_id, bool(val)),
                inputs=[gr_session, gr_blocks_preview],
                outputs=None
            )
            gr_interlude_enabled.select(
                fn=lambda session_id, val: _change_param('interlude_enabled', session_id, bool(val)),
                inputs=[gr_session, gr_interlude_enabled],
                outputs=None
            )
            gr_voice_file.upload(
                fn=_disable_on_voice_upload,
                inputs=None,
                outputs=outputs_on_voice_upload,
                show_progress_on=[gr_voice_file]
            ).then(
                fn=_change_gr_voice_file,
                inputs=[gr_session, gr_voice_file],
                outputs=[gr_voice_list],
                show_progress_on=[gr_voice_list]
            ).then(
                fn=lambda: gr.update(value=None),
                inputs=None,
                outputs=[gr_voice_file],
                show_progress_on=[gr_voice_list]
            ).then(
                fn=_enable_on_voice_upload,
                inputs=[gr_session, gr_ebook_src, gr_ebook_textarea, gr_ebook_mode],
                outputs=outputs_on_voice_upload,
                show_progress_on=[gr_voice_list]
            )
            gr_voice_list.change(
                fn=_change_gr_voice_list,
                inputs=[gr_session, gr_voice_list],
                outputs=[gr_voice_player_hidden, gr_voice_play, gr_voice_del_btn],
                show_progress_on=[gr_progress]
            )
            gr_voice_del_btn.click(
                fn=_click_gr_voice_del_btn,
                inputs=[gr_session, gr_voice_list],
                outputs=[gr_modal, gr_data_field_hidden],
                show_progress_on=[gr_progress]
            )
            gr_device.change(
                fn=_change_gr_device,
                inputs=[gr_session, gr_device],
                outputs=None
            )
            gr_language.change(
                fn=_change_gr_language,
                inputs=[gr_session, gr_language],
                outputs=[gr_translate, gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list],
                show_progress_on=[gr_progress]
            ).then(
                fn=_update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_translate_enabled.change(
                fn=_click_gr_translate_enabled,
                inputs=[gr_session, gr_translate_enabled],
                outputs=[gr_translate, gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list, gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_translate.change(
                fn=_change_gr_translate,
                inputs=[gr_session, gr_translate],
                outputs=[gr_tts_engine_list, gr_custom_model_list, gr_fine_tuned_list],
                show_progress_on=[gr_progress]
            ).then(
                fn=_change_gr_tts_engine_list,
                inputs=[gr_session, gr_tts_engine_list],
                outputs=[gr_tts_rating, gr_tab_xtts_params, gr_tab_bark_params, gr_group_custom_model, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list],
                show_progress_on=[gr_progress]
            ).then(
                fn=_update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_tts_engine_list.change(
                fn=_change_gr_tts_engine_list,
                inputs=[gr_session, gr_tts_engine_list],
                outputs=[gr_tts_rating, gr_tab_xtts_params, gr_tab_bark_params, gr_group_custom_model, gr_fine_tuned_list, gr_custom_model_file, gr_custom_model_list],
                show_progress_on=[gr_progress]
            ).then(
                fn=_update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_fine_tuned_list.change(
                fn=_change_gr_fine_tuned_list,
                inputs=[gr_session, gr_fine_tuned_list],
                outputs=[gr_group_custom_model],
                show_progress_on=[gr_progress]
            ).then(
                fn=_update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_custom_model_file.upload(
                fn=_disable_on_custom_upload,
                inputs=None,
                outputs=outputs_on_custom_upload,
                show_progress_on=[gr_custom_model_file]
            ).then(
                fn=_change_gr_custom_model_file,
                inputs=[gr_session, gr_custom_model_file, gr_tts_engine_list],
                outputs=[gr_custom_model_file, gr_custom_model_list],
                show_progress_on=[gr_custom_model_list]
            ).then(
                fn=_update_gr_voice_list,
                inputs=[gr_session],
                outputs=[gr_voice_list],
                show_progress_on=[gr_custom_model_list]
            ).then(
                fn=_enable_on_custom_upload,
                inputs=[gr_custom_model_list, gr_ebook_src, gr_ebook_textarea],
                outputs=outputs_on_custom_upload,
                show_progress_on=[gr_custom_model_list]
            )
            gr_custom_model_list.change(
                fn=_change_gr_custom_model_list,
                inputs=[gr_session, gr_custom_model_list],
                outputs=[gr_fine_tuned_list, gr_voice_list, gr_custom_model_del_btn],
                show_progress_on=[gr_progress]
            )
            gr_custom_model_del_btn.click(
                fn=_click_gr_custom_model_del_btn,
                inputs=[gr_session, gr_custom_model_list],
                outputs=[gr_modal, gr_data_field_hidden],
                show_progress_on=[gr_progress]
            )
            gr_output_format_list.change(
                fn=_change_gr_output_format_list,
                inputs=[gr_session, gr_output_format_list],
                outputs=None
            )
            gr_output_channel_list.change(
                fn=_change_gr_output_channel_list,
                inputs=[gr_session, gr_output_channel_list],
                outputs=None
            )
            gr_output_split.select(
                fn=_change_gr_output_split,
                inputs=[gr_session, gr_output_split],
                outputs=[gr_row_output_split_hours],
                show_progress_on=[gr_progress]
            )
            gr_output_split_hours.change(
                fn=lambda session_id, val: _change_param('output_split_hours', session_id, str(val)),
                inputs=[gr_session, gr_output_split_hours],
                outputs=None
            )
            gr_session_switch_btn.click(
                fn=_click_gr_session_switch_btn,
                inputs=[gr_session, gr_backup_session],
                outputs=[gr_restore_session, gr_session, gr_backup_session, gr_session_switch_btn, gr_session_switch_disable_state, gr_session_switch_enable_state],
                show_progress_on=[gr_session_switch_btn]
            )
            gr_session_switch_disable_state.change(
                fn=lambda session_id: _disable_components(session_id, exceptions=['gr_session_switch_btn']),
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
                fn=_enable_components,
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
            gr_audiobook_download_btn.click(
                fn=_toggle_audiobook_files,
                inputs=[gr_session, gr_audiobook_list, gr_audiobook_files_state],
                outputs=[gr_audiobook_files, gr_audiobook_files_state],
                show_progress_on=[gr_audiobook_list]
            )
            gr_audiobook_list.change(
                fn=_change_gr_audiobook_list,
                inputs=[gr_session, gr_audiobook_list],
                outputs=[gr_group_audiobook_list, gr_abs_audiobook],
                show_progress_on=[gr_audiobook_list]
            ).then(
                fn=_update_gr_audiobook_player,
                inputs=[gr_session],
                outputs=[gr_playback_time, gr_audiobook_player, gr_audiobook_vtt],
                show_progress_on=[gr_audiobook_list]
            ).then(
                fn=lambda: (gr.update(visible=False, value=None), False),
                inputs=None,
                outputs=[gr_audiobook_files, gr_audiobook_files_state],
                show_progress_on=[gr_audiobook_list],
                js='()=>{window.load_vtt();}'
            ).then(
                fn=_change_gr_audiobook_edit_btns,
                inputs=[gr_session, gr_audiobook_list],
                outputs=[gr_audiobook_export_btn, gr_audiobook_edit_btn],
                show_progress_on=[gr_audiobook_list]
            )
            gr_audiobook_del_btn.click(
                fn=_click_gr_audiobook_del_btn,
                inputs=[gr_session, gr_audiobook_list],
                outputs=[gr_modal, gr_data_field_hidden],
                show_progress_on=[gr_audiobook_list]
            )
            gr_audiobook_edit_btn.click(
                fn=_click_gr_audiobook_edit_btn,
                inputs=[gr_session, gr_audiobook_list, gr_audiobook_edit_cue],
                outputs=outputs_audiobook_edit,
                show_progress_on=[gr_audiobook_list],
                js='''
                    (session_id, audiobook, cue)=>{
                        try{
                            const gr_root = (window.gradioApp && window.gradioApp()) || document;
                            const player = gr_root.querySelector("#gr_audiobook_player audio");
                            const sentence = gr_root.querySelector("#gr_audiobook_sentence textarea");
                            let time = 0;
                            if(player){
                                player.pause();
                                time = parseFloat(player.currentTime) || 0;
                            }
                            const found = window.findCue(time);
                            if(found && sentence){
                                sentence.value = found.text;
                                sentence.dispatchEvent(new Event("input", {bubbles: true}));
                            }
                            cue = JSON.stringify(found ? {idx: (found.sentence_idx ?? found.idx), text: found.text, interlude: (found.interlude ?? null)} : {idx: -1, text: "", interlude: null});
                        }catch(e){
                            console.warn("gr_audiobook_edit_btn error:", e);
                        }
                        return [session_id, audiobook, cue];
                    }
                '''
            ).then(
                fn=_update_audiobook_edit_lock,
                inputs=[gr_session],
                outputs=outputs_audiobook_edit_lock,
                show_progress_on=[gr_audiobook_list]
            )
            gr_audiobook_edit_preview_btn.click(
                fn=lambda: (gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)),
                inputs=None,
                outputs=[gr_audiobook_sentence, gr_audiobook_edit_preview_btn, gr_audiobook_edit_save_btn, gr_audiobook_edit_cancel_btn],
                queue=False
            ).then(
                fn=_click_gr_audiobook_edit_sentence_btn,
                inputs=[gr_session, gr_audiobook_sentence],
                outputs=[gr_audiobook_edit_player, gr_audiobook_edit_preview_btn, gr_audiobook_edit_save_btn, gr_audiobook_edit_cancel_btn],
                show_progress_on=[gr_progress]
            ).then(
                fn=_update_audiobook_edit_input,
                inputs=[gr_session],
                outputs=[gr_audiobook_sentence, gr_audiobook_edit_preview_btn, gr_audiobook_edit_save_btn, gr_audiobook_edit_cancel_btn],
                queue=False
            )
            gr_audiobook_edit_save_btn.click(
                fn=lambda: (gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False), gr.update(interactive=False)),
                inputs=None,
                outputs=[gr_audiobook_sentence, gr_audiobook_edit_preview_btn, gr_audiobook_edit_save_btn, gr_audiobook_edit_cancel_btn],
                queue=False
            ).then(
                fn=_click_gr_audiobook_edit_save_btn,
                inputs=[gr_session, gr_audiobook_sentence],
                outputs=outputs_audiobook_edit,
                show_progress_on=[gr_progress]
            ).then(
                fn=_update_audiobook_edit_input,
                inputs=[gr_session],
                outputs=[gr_audiobook_sentence, gr_audiobook_edit_preview_btn, gr_audiobook_edit_save_btn, gr_audiobook_edit_cancel_btn],
                queue=False
            ).then(
                fn=_update_audiobook_edit_lock,
                inputs=[gr_session],
                outputs=outputs_audiobook_edit_lock,
                show_progress_on=[gr_audiobook_list]
            )
            gr_audiobook_edit_cancel_btn.click(
                fn=_click_gr_audiobook_edit_cancel_btn,
                inputs=[gr_session],
                outputs=outputs_audiobook_edit,
                show_progress_on=[gr_audiobook_list]
            ).then(
                fn=_update_audiobook_edit_lock,
                inputs=[gr_session],
                outputs=outputs_audiobook_edit_lock,
                show_progress_on=[gr_audiobook_list]
            )
            gr_audiobook_export_btn.click(
                fn=lambda: tuple(gr.update(interactive=False) for _ in range(5)),
                inputs=None,
                outputs=[gr_audiobook_export_btn, gr_audiobook_edit_btn, gr_audiobook_list, gr_audiobook_del_btn, gr_convert_btn],
                queue=False
            ).then(
                fn=_click_gr_audiobook_export_btn,
                inputs=[gr_session, gr_audiobook_list],
                outputs=[gr_audiobook_export_btn, gr_audiobook_edit_btn, gr_audiobook_list, gr_audiobook_del_btn, gr_convert_btn],
                show_progress_on=[gr_progress]
            ).then(
                fn=_update_gr_audiobook_player,
                inputs=[gr_session],
                outputs=[gr_playback_time, gr_audiobook_player, gr_audiobook_vtt],
                show_progress_on=[gr_audiobook_list]
            ).then(
                fn=None,
                inputs=None,
                outputs=None,
                js='()=>{window.load_vtt();}'
            )

            ########### XTTS Params

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
                fn=lambda session_id, val: _change_param('xtts_temperature', session_id, float(val)),
                inputs=[gr_session, gr_xtts_temperature],
                outputs=None
            )
            gr_xtts_length_penalty.change(
                fn=lambda session_id, val, val2: _change_param('xtts_length_penalty', session_id, int(val), int(val2)),
                inputs=[gr_session, gr_xtts_length_penalty, gr_xtts_num_beams],
                outputs=None,
            )
            gr_xtts_num_beams.change(
                fn=lambda session_id, val, val2: _change_param('xtts_num_beams', session_id, int(val), int(val2)),
                inputs=[gr_session, gr_xtts_num_beams, gr_xtts_length_penalty],
                outputs=None,
            )
            gr_xtts_repetition_penalty.change(
                fn=lambda session_id, val: _change_param('xtts_repetition_penalty', session_id, float(val)),
                inputs=[gr_session, gr_xtts_repetition_penalty],
                outputs=None
            )
            gr_xtts_top_k.change(
                fn=lambda session_id, val: _change_param('xtts_top_k', session_id, int(val)),
                inputs=[gr_session, gr_xtts_top_k],
                outputs=None
            )
            gr_xtts_top_p.change(
                fn=lambda session_id, val: _change_param('xtts_top_p', session_id, float(val)),
                inputs=[gr_session, gr_xtts_top_p],
                outputs=None
            )
            gr_xtts_speed.change(
                fn=lambda session_id, val: _change_param('xtts_speed', session_id, float(val)),
                inputs=[gr_session, gr_xtts_speed],
                outputs=None
            )
            gr_xtts_enable_text_splitting.select(
                fn=lambda session_id, val: _change_param('xtts_enable_text_splitting', session_id, bool(val)),
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
                fn=lambda session_id, val: _change_param('bark_text_temp', session_id, float(val)),
                inputs=[gr_session, gr_bark_text_temp],
                outputs=None
            )
            gr_bark_waveform_temp.change(
                fn=lambda session_id, val: _change_param('bark_waveform_temp', session_id, float(val)),
                inputs=[gr_session, gr_bark_waveform_temp],
                outputs=None
            )

            ############ Timer to save session to localStorage

            gr_timer = gr.Timer(9, active=False)
            gr_timer.tick(
                fn=_update_gr_save_session,
                inputs=[gr_session, gr_session_update],
                outputs=[gr_save_session, gr_session_update, gr_audiobook_list]
            )

            ########### Main chains

            _chain_enable(
                _chain_check_override(
                    gr_convert_btn.click(
                        fn=_disable_components,
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
            _chain_enable(
                gr_override_cancel_btn.click(
                    fn=_click_gr_override_cancel_btn,
                    inputs=[gr_session],
                    outputs=[gr_modal],
                    show_progress_on=[gr_progress]
                ),
                always=True
            )
            gr_override_confirm_btn.click(
                fn=_click_gr_override_confirm_btn,
                inputs=[gr_session, gr_event, gr_audiobook_files_state],
                outputs=[gr_modal, gr_event, gr_audiobook_list, gr_audiobook_files, gr_audiobook_files_state],
                show_progress_on=[gr_progress]
            )
            _chain_enable(
                _chain_check_override(
                    _chain_refresh(
                        gr_event.change(
                            fn=_disable_components,
                            inputs=[gr_session],
                            outputs=outputs_disable_components,
                            show_progress_on=[gr_progress],
                            queue=False
                        ).then(
                            fn=lambda: None,
                            js=f'()=>{{{js_hide_elements}}}'
                        ).then(
                            fn=_start_conversion,
                            inputs=inputs_start_conversion,
                            outputs=[gr_progress],
                            show_progress_on=[gr_progress],
                        ).then(
                            fn=_edit_blocks,
                            inputs=[gr_session],
                            outputs=outputs_edit_blocks,
                            show_progress_on=[gr_progress]
                        ).then(
                            fn=_populate_page,
                            inputs=[gr_session, gr_blocks_page, gr_blocks_data],
                            outputs=[*blocks_components_flat, gr_blocks_header, gr_blocks_expands],
                            show_progress_on=[gr_progress]
                        )
                    )
                ),
                always=False
            )
            _chain_enable(
                gr_blocks_cancel_btn.click(
                    fn=lambda: (gr.update(interactive=False), gr.update(interactive=False)),
                    outputs=[gr_blocks_cancel_btn, gr_blocks_confirm_btn],
                    show_progress_on=[gr_progress],
                    queue=False
                ).then(
                    fn=_click_gr_blocks_cancel_btn,
                    inputs=[gr_session, gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                    outputs=[gr_convert_btn, gr_group_main, gr_audiobook_list, gr_group_blocks, gr_blocks_data],
                    show_progress_on=[gr_progress]
                ),
                always=True
            )
            _chain_enable(
                gr_blocks_confirm_btn.click(
                    fn=lambda page, blocks, expands, *args: _collect_page(page, blocks, expands, *args),
                    inputs=[gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                    outputs=[gr_blocks_data],
                    show_progress_on=[gr_progress]
                ).then(
                    fn=_click_gr_blocks_confirm_btn,
                    inputs=[gr_session, gr_blocks_event, gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                    outputs=[gr_blocks_cancel_btn, gr_blocks_confirm_btn, gr_group_main, gr_group_blocks, gr_audiobook_list, gr_blocks_event],
                    show_progress_on=[gr_progress]
                )
            )
            _chain_enable(
                _chain_check_override(
                    _chain_refresh(
                        gr_blocks_event.change(
                            fn=finalize_audiobook,
                            inputs=[gr_session],
                            outputs=[gr_progress, gr_dummy_bool],
                            show_progress_on=[gr_progress]
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
                fn=lambda session_id, page, blocks, *args: _navigate(session_id, page, blocks, -1, *args),
                inputs=[gr_session, gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                outputs=[gr_blocks_data, gr_blocks_page, gr_blocks_back_btn, gr_blocks_next_btn],
                show_progress_on=[gr_blocks_nav]
            ).then(
                fn=_populate_page,
                inputs=[gr_session, gr_blocks_page, gr_blocks_data],
                outputs=[*blocks_components_flat, gr_blocks_header, gr_blocks_expands],
                show_progress_on=[gr_blocks_nav]
            )
            gr_blocks_next_btn.click(
                fn=lambda session_id, page, blocks, *args: _navigate(session_id, page, blocks, 1, *args),
                inputs=[gr_session, gr_blocks_page, gr_blocks_data, gr_blocks_expands, *blocks_keeps, *blocks_voices, *blocks_texts],
                outputs=[gr_blocks_data, gr_blocks_page, gr_blocks_back_btn, gr_blocks_next_btn],
                show_progress_on=[gr_blocks_nav]
            ).then(
                fn=_populate_page,
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
            gr_ui_language.input(
                fn=_change_gr_ui_language,
                inputs=[gr_session, gr_ui_language],
                outputs=None
            ).then(
                fn=_restore_ui_language,
                inputs=[gr_session],
                outputs=outputs_ui_language
            )
            gr_restore_session.change(
                fn=_change_gr_restore_session,
                inputs=[gr_restore_session, gr_session_update],
                outputs=[gr_save_session, gr_session_update, gr_session, gr_glassmask],
                show_progress_on=[gr_progress]
            ).then(
                fn=_restore_interface,
                inputs=[gr_session],
                outputs=outputs_restore_interface,
                show_progress_on=[gr_progress]
            ).then(
                fn=_restore_ui_language,
                inputs=[gr_session],
                outputs=outputs_ui_language
            ).then(
                fn=_restore_audiobook_player,
                inputs=[gr_session, gr_audiobook_list],
                outputs=[gr_group_audiobook_list, gr_audiobook_player, gr_timer],
                show_progress_on=[gr_progress]
            ).then(
                fn=lambda session: _update_gr_glassmask(attr=['gr-glass-mask', 'hide']) if session else gr.update(),
                inputs=[gr_session],
                outputs=[gr_glassmask],
                show_progress_on=[gr_progress]
            ).then(
                fn=None,
                inputs=None,
                js='()=>{window.init_interface();}'
            )
            gr_deletion_confirm_btn.click(
                fn=_click_gr_deletion,
                inputs=[gr_session, gr_voice_list, gr_custom_model_list, gr_audiobook_list, gr_data_field_hidden],
                outputs=[gr_modal, gr_custom_model_list, gr_audiobook_list, gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_deletion_cancel_btn.click(
                fn=_click_gr_deletion,
                inputs=[gr_session, gr_voice_list, gr_custom_model_list, gr_audiobook_list],
                outputs=[gr_modal, gr_custom_model_list, gr_audiobook_list, gr_voice_list],
                show_progress_on=[gr_progress]
            )
            gr_abs_library.change(
                fn=_change_gr_abs_library,
                inputs=[gr_session, gr_abs_url, gr_abs_api_token, gr_abs_library],
                outputs=None
            ).then(
                fn=_abs_upload_enabled,
                inputs=[gr_session],
                outputs=gr_abs_upload_btn
            )
            gr_abs_search_btn.click(
                fn=_search_abs_libraries,
                inputs=[gr_session, gr_abs_url, gr_abs_api_token], 
                outputs=gr_abs_library
            ).then(
                fn=_abs_upload_enabled,
                inputs=[gr_session],
                outputs=gr_abs_upload_btn
            )
            gr_abs_upload_btn.click(
                fn=lambda: gr.update(interactive=False),
                inputs=None,
                outputs=[gr_abs_upload_btn],
                show_progress_on=[gr_progress],
                queue=False
            ).then(
                fn=_click_gr_abs_upload_btn,
                inputs=[gr_session, gr_abs_audiobook, gr_abs_url, gr_abs_api_token, gr_abs_library],
                outputs=[gr_abs_upload_btn, gr_abs_status],
                show_progress_on=[gr_abs_status]
            )
            ############
            app.load(
                fn=None,
                js=header_js,
                outputs=[gr_restore_session],
            )
            app.unload(on_unload)
            all_ips = get_all_ip_addresses()
            msg = legends['msg_ips_available'].format(ips=all_ips, port=interface_port)
            show_alert(None, {"type": "info", "msg": msg})
            os.environ['no_proxy'] = ' ,'.join(all_ips)
            return app
    except Exception as e:
        traceback.print_exc()
        error = legends['error_unexpected'].format(e=e)
        exception_alert(None, error)
    return None
