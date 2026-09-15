import argparse, json, socket, shutil, multiprocessing, sys, uuid, copy, warnings, os
from pathlib import Path
from lib.conf import *
from lib.conf_lang import default_language_code, language_mapping, install_info
from lib.conf_models import TTS_ENGINES, default_fine_tuned, default_engine_settings

warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='jieba._compat')

def init_multiprocessing():
    try: multiprocessing.set_start_method('spawn')
    except RuntimeError: pass

def check_virtual_env(script_mode:str)->bool:
    current_version=sys.version_info[:2]
    search_python_env = str(os.path.basename(sys.prefix))
    if script_mode == FULL_DOCKER:
        return True
    if search_python_env == 'python_env':
        pyvenv_cfg = os.path.join(sys.prefix, 'pyvenv.cfg')
        conda_meta = os.path.join(sys.prefix, 'conda-meta')
        if os.path.isdir(conda_meta):
            print(f'***********\nWrong launch: {search_python_env} was created by conda/Miniforge3, not uv!\nPlease remove the \'{search_python_env}\' directory and re-run the installer.\n{install_info}\n***********')
            return False
        if not os.path.isfile(pyvenv_cfg):
            print(f'***********\nWrong launch: {search_python_env} does not appear to be a valid virtual environment.\nPlease remove the \'{search_python_env}\' directory and re-run the installer.\n{install_info}\n***********')
            return False
        is_uv_venv = False
        try:
            with open(pyvenv_cfg, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('uv'):
                        is_uv_venv = True
                        break
        except OSError: pass
        if not is_uv_venv:
            print(f'***********\nWrong launch: {search_python_env} was not created by uv!\nPlease remove the \'{search_python_env}\' directory and re-run the installer.\n{install_info}\n***********')
            return False
        if not shutil.which('uv'):
            print(f'***********\nWrong launch: uv binary not found in PATH.\nThe application requires uv to manage Python packages.\nPlease install uv: https://docs.astral.sh/uv/getting-started/installation/\n{install_info}\n***********')
            return False
        return True
    if current_version >= min_python_version and current_version <= max_python_version:
        return True
    print(f'***********\nWrong launch! ebook2audiobook must run in its own virtual environment!\n{install_info}\n***********')
    return False

def check_python_version(script_mode:str)->bool:
    if script_mode == BUILD_DOCKER: return True
    current_version = sys.version_info[:2]
    if current_version < min_python_version or current_version > max_python_version:
        print(f'***********\nWrong launch: Your OS Python version is not compatible! (current: {current_version[0]}.{current_version[1]})\n{install_info}\n***********')
        return False
    return True

def is_running_in_container()->bool: return os.environ.get("IN_DOCKER") == "1"
def is_port_in_use(port:int)->bool:
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s: return s.connect_ex(('0.0.0.0',port))==0

def kill_previous_instances(script_name: str):
    current_pid = os.getpid()
    this_script_path = os.path.realpath(script_name)
    import psutil
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if not cmdline: continue
            joined_cmd = ' '.join(cmdline).lower()
            if this_script_path.lower().endswith(script_name.lower()) and (script_name.lower() in joined_cmd) and proc.info['pid'] != current_pid:
                print(f"[WARN] Found running instance PID={proc.info['pid']} -> killing it.")
                proc.kill()
                proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess): continue

def register_dlls()->str|bool:
    candidates = [Path(os.environ['USERPROFILE']) / 'scoop' / 'apps' / 'ffmpeg-shared' / 'current' / 'bin', Path(os.environ.get('PROGRAMFILES', r'C:\Program Files')) / 'ffmpeg' / 'bin', Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft' / 'WinGet' / 'Links']
    found = shutil.which('ffmpeg')
    if found: candidates.append(Path(found).parent)
    for p in candidates:
        if p and p.is_dir() and any(p.glob('avcodec-*.dll')):
            os.add_dll_directory(str(p))
            return str(p)
    return False

def main()->None:
    wsl_cmd = ''
    wsl_extra = ''
    if os.environ.get('DOCKER_IN_WSL', '0') == '1' and os.environ.get('DOCKER_DESKTOP', '0') == '0' and os.environ.get('PODMAN_DESKTOP', '0') == '0': 
        wsl_cmd = 'wsl --user root --'
    if wsl_cmd: wsl_extra = f'DEVICE_TAG=cu128'
    else: wsl_extra = f'DEVICE_TAG=cu128  & &'

    parser = argparse.ArgumentParser(description='Convert eBooks to Audiobooks using a Text-to-Speech model.', epilog=f'''Example usage: ...''', formatter_class=argparse.RawTextHelpFormatter)
    tts_engine_list_keys = [*TTS_ENGINES]
    tts_engine_list_values = list(TTS_ENGINES.values())
    
    # Argument definitions (abbreviated for brevity, logic remains identical to original)
    all_group = parser.add_argument_group('**** The following options are for container only', 'Optional')
    all_group.add_argument(cli_options[0], type=str, help='Mandatory to build a container.')
    all_group.add_argument(cli_options[1], type=str, help='Optional. podman or compose.')
    parser.add_argument(cli_options[2], type=str, help='Session ID.')
    gui_group = parser.add_argument_group('**** GUI mode', 'Optional')
    gui_group.add_argument(cli_options[3], action='store_true', help='Enable public Gradio link.')
    headless_group = parser.add_argument_group('**** Headless mode')
    headless_group.add_argument(cli_options[4], action='store_true', help='Run in headless mode')
    headless_group.add_argument(cli_options[5], type=str, help='Ebook file path')
    headless_group.add_argument(cli_options[6], type=str, help='Ebook directory path')
    headless_group.add_argument(cli_options[7], type=str, help='Raw text')
    headless_group.add_argument(cli_options[8], type=str, default=default_language_code, help='Language')
    headless_optional_group = parser.add_argument_group('optional parameters')
    headless_optional_group.add_argument(cli_options[9], type=str, default=None, metavar='ISO3', help='Translate to ISO3')
    headless_optional_group.add_argument(cli_options[10], type=str, default=None, help='Voice cloning file')
    headless_optional_group.add_argument(cli_options[11], type=str, default=None, help='Voice map JSON')
    headless_optional_group.add_argument(cli_options[12], type=str, default=default_device, choices=list(devices.keys())+[k.lower() for k in devices.keys()], help='Device')
    headless_optional_group.add_argument(cli_options[13], type=str, default=TTS_ENGINES['XTTS'], choices=tts_engine_list_keys+tts_engine_list_values, help='TTS Engine')
    headless_optional_group.add_argument(cli_options[14], type=str, default=None, help='Custom model zip')
    headless_optional_group.add_argument(cli_options[15], type=str, default=default_fine_tuned, help='Fine tuned model')
    headless_optional_group.add_argument(cli_options[16], type=str, default=default_output_format, help='Output format')
    headless_optional_group.add_argument(cli_options[17], type=str, default=default_output_channel, help='Output channel')
    headless_optional_group.add_argument(cli_options[18], type=float, default=default_engine_settings[TTS_ENGINES['XTTS']]['temperature'], help='XTTS Temp')
    headless_optional_group.add_argument(cli_options[19], type=float, default=default_engine_settings[TTS_ENGINES['XTTS']]['length_penalty'], help='XTTS Length Penalty')
    headless_optional_group.add_argument(cli_options[20], type=int, default=default_engine_settings[TTS_ENGINES['XTTS']]['num_beams'], help='XTTS Num Beams')
    headless_optional_group.add_argument(cli_options[21], type=float, default=default_engine_settings[TTS_ENGINES['XTTS']]['repetition_penalty'], help='XTTS Repetition Penalty')
    headless_optional_group.add_argument(cli_options[22], type=int, default=default_engine_settings[TTS_ENGINES['XTTS']]['top_k'], help='XTTS Top K')
    headless_optional_group.add_argument(cli_options[23], type=float, default=default_engine_settings[TTS_ENGINES['XTTS']]['top_p'], help='XTTS Top P')
    headless_optional_group.add_argument(cli_options[24], type=float, default=default_engine_settings[TTS_ENGINES['XTTS']]['speed'], help='XTTS Speed')
    headless_optional_group.add_argument(cli_options[25], action='store_true', help='XTTS Enable Text Splitting')
    headless_optional_group.add_argument(cli_options[26], type=float, default=default_engine_settings[TTS_ENGINES['BARK']]['text_temp'], help='Bark Text Temp')
    headless_optional_group.add_argument(cli_options[27], type=float, default=default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp'], help='Bark Waveform Temp')
    headless_optional_group.add_argument(cli_options[28], type=str, help='Output Dir')
    headless_optional_group.add_argument(cli_options[29], type=str, default='', help='ABS URL')
    headless_optional_group.add_argument(cli_options[30], type=str, default='', help='ABS Token')
    headless_optional_group.add_argument(cli_options[31], type=str, default='', help='ABS Library ID')
    headless_optional_group.add_argument(cli_options[32], action='version', version=f'ebook2audiobook version {prog_version}', help='Version')
    internal_group = parser.add_argument_group(argparse.SUPPRESS)
    internal_group.add_argument(cli_options[33], type=str, default=None, help=argparse.SUPPRESS)
    internal_group.add_argument(cli_options[34], type=str, default=None, help=argparse.SUPPRESS)

    for arg in sys.argv:
         if arg.startswith('--') and arg not in cli_options:
             print(f'Error: Unrecognized option "{arg}"')
             sys.exit(1)

    args = vars(parser.parse_args())

    if not 'help' in args:
        args['script_mode'] = args['script_mode'] if args['script_mode'] else NATIVE
        args['share'] =  args['share'] if args['share'] else False
        args['ebook_mode'] = 'single'
        args['ebook_list'] = None

        if args['script_mode'] == FULL_DOCKER and not is_running_in_container():
            print(f'{FULL_DOCKER} is only an internal option for the docker itself.')
            sys.exit(1)
        elif (not check_virtual_env(args['script_mode'])) or (not check_python_version(args['script_mode'])):
            sys.exit(1)
        elif args.get('headless', False) and args.get('share', False):
            print('--share option is only allowed in non-headless mode.')
            sys.exit(1)
        elif not args.get('headless', False) and is_port_in_use(interface_port):
            print(f'Error: Port {interface_port} is already in use.')
            sys.exit(1)

        print(f"v{prog_version} {args['script_mode']} mode")

        from lib.classes.device_installer import DeviceInstaller
        manager = DeviceInstaller()
        device_info_str = manager.check_device_info(args['script_mode'])
        if args['script_mode'] == NATIVE:
            if manager.install_device_packages(device_info_str) == 1:
                print('Error: Could not installed device packages!')
                sys.exit(1)
            result = manager.install_python_packages()
            if result == 1: sys.exit(1)
        elif args['script_mode'] == FULL_DOCKER:
            if manager.check_voices() == 1:
                print('Error: Could not download voices!')
                sys.exit(1)

        if DEVICE_SYSTEM == systems['WINDOWS'] and not register_dlls():
            print('WARNING: shared DLLs not found. aborting…')
            sys.exit(1)

        import lib.core as c
        c.context = c.SessionContext() if c.context is None else c.context
        c.context_tracker = c.SessionTracker() if c.context_tracker is None else c.context_tracker
        c.active_sessions = set() if c.active_sessions is None else c.active_sessions
        error = ''

        # Headless/GUI Logic (Preserved from original)
        if args.get('headless', False):
            args['id'] = args['workflow'] if args['workflow'] else args['session'] if args['session'] else str(uuid.uuid4())
            if args['id'] == workflow_id or not args['session']: session = c.context.set_session(args['id'])
            else:
                session_dir = os.path.join(tmp_dir, f"proc-{args['id']}")
                session = c.context.get_session(args['id'])
                if not os.path.exists(session_dir) and not session or (session and not session.get('id', False)):
                    print('Session expired or does not exist!')
                    sys.exit(1)
                session = c.context.set_session(args['id'])
            if not c.context_tracker.start_session(args['id']):
                print('Session could not start!')
                sys.exit(1)
            
            # Setup args (abbreviated)
            args['is_gui_process'] = False
            args['blocks_preview'] = False
            args['device'] = devices.get(args['device'].upper(), {}).get('proc') or devices['CPU']['proc']
            args['tts_engine'] = TTS_ENGINES[args['tts_engine']] if args['tts_engine'] in TTS_ENGINES.keys() else args['tts_engine'] if args['tts_engine'] in TTS_ENGINES.values() else None
            args['output_split'] = default_output_split
            args['output_split_hours'] = default_output_split_hours
            args['xtts_temperature'] = args['temperature']
            args['xtts_length_penalty'] = args['length_penalty']
            args['xtts_num_beams'] = args['num_beams']
            args['xtts_repetition_penalty'] = args['repetition_penalty']
            args['xtts_top_k'] = args['top_k']
            args['xtts_top_p'] = args['top_p']
            args['xtts_speed'] = args['speed']
            args['xtts_enable_text_splitting'] = False
            args['bark_text_temp'] = args['text_temp']
            args['bark_waveform_temp'] = args['waveform_temp']
            args['translate_enabled'] = False
            _user_translate_raw = args.get('translate')
            args['translate'] = None
            args['translate_iso1'] = None
            if _user_translate_raw:
                from iso639 import Lang
                tgt = str(_user_translate_raw).strip().lower()
                try:
                    if len(tgt) in (2, 3):
                        ld = Lang(tgt)
                        if ld: tgt = ld.pt3
                except Exception: pass
                if not tgt or tgt not in language_mapping.keys():
                    print(f"Error: --translate target '{_user_translate_raw}' is not a supported language.")
                    sys.exit(1)
                if tgt == args.get('language'): print(f"[translate] target equals source ({tgt}), translation skipped.")
                else:
                    try: tgt_iso1 = Lang(tgt).pt1
                    except Exception: tgt_iso1 = None
                    if not tgt_iso1:
                        print(f"Error: --translate target '{tgt}' has no iso639-1 mapping.")
                        sys.exit(1)
                    args['translate_enabled'] = True
                    args['translate'] = tgt
                    args['translate_iso1'] = tgt_iso1

            specified_input = sum(args.get(k, None) is not None for k in ('ebook', 'ebooks_dir', 'text'))
            if specified_input > 1: error = 'Error: You can only specify one of --ebook, --ebooks_dir, or --text in headless mode.'
            else:
                if args.get('voice'):
                    if os.path.exists(args['voice']): args['voice'] = os.path.abspath(args['voice'])
                if args.get('custom_model', None) is not None:
                    if os.path.exists(args['custom_model']): args['custom_model'] = os.path.abspath(args['custom_model'])
                if args.get('output_dir', None) is not None and not os.path.exists(args['output_dir']): error = 'Error: --output_dir path does not exist.'
                elif args.get('ebooks_dir', None) is not None:
                    args['ebook_mode'] = 'directory'
                    args['ebooks_dir'] = os.path.abspath(args['ebooks_dir'])
                    if not os.path.exists(args['ebooks_dir']): error = f"Error: The provided --ebooks_dir {args['ebooks_dir']} does not exist."
                    else:
                        voice_map:dict = {}
                        if args.get('voice_map'):
                            voice_map_path = os.path.abspath(args['voice_map'])
                            if not os.path.exists(voice_map_path): error = f'Error: The provided --voice_map {voice_map_path} does not exist.'
                            else:
                                try:
                                    with open(voice_map_path, 'r', encoding='utf-8') as f: raw = json.load(f)
                                    if not isinstance(raw, dict): error = 'Error: --voice_map JSON must be an object.'
                                    else:
                                        voice_map = {}
                                        for k, v in raw.items():
                                            normalized_key = os.path.abspath(k) if os.path.isabs(k) else k
                                            voice_map[normalized_key] = os.path.abspath(v) if v else None
                                except Exception as e: error = f'Error: Failed to parse --voice_map: {e}'
                        if not error:
                            c.context.sessions[args['id']]['voice_map'] = voice_map
                            default_voice = args.get('voice')
                            all_entries = sorted(os.listdir(args['ebooks_dir']), key=c.natural_sort_key)
                            args['ebook_list'] = []
                            for name in all_entries:
                                ebook_dir_path = os.path.abspath(os.path.join(args['ebooks_dir'], name))
                                if not os.path.isfile(ebook_dir_path): continue
                                if not any(name.endswith(ext) for ext in ebook_formats):
                                    print(f'{name} skipped (unsupported format)')
                                    continue
                                args['ebook_list'].append(ebook_dir_path)
                            if not args['ebook_list']: error = 'Error: No supported ebook files found in --ebooks_dir.'
                            else:
                                ebook_list = copy.deepcopy(args['ebook_list'])
                                for file in ebook_list:
                                    c.context.sessions[args['id']]['status'] = c.status_tags['READY']
                                    c.reset_ebook_session(args['id'], force=True, filter_keys=False)
                                    args['ebook_src'] = file
                                    override = voice_map.get(file) or voice_map.get(os.path.basename(file))
                                    if override and not os.path.exists(override):
                                        print(f'--voice_map: override for {Path(file).name} ({override}) not found, falling back to --voice')
                                        override = None
                                    args['voice'] = override or default_voice
                                    progress_status, passed = c.convert_ebook(args)
                                    if passed: args['ebook_list'].remove(file)
                                    else: error = progress_status; break
                elif args.get('ebook', None) is not None:
                    args['ebook_mode'] = 'single'
                    args['ebook_src'] = os.path.abspath(args['ebook'])
                    if not os.path.exists(args['ebook_src']): error = f"Error: The provided --ebook {args['ebook_src']} does not exist."
                    else:
                        progress_status, passed = c.convert_ebook(args)
                        c.context.sessions[args['id']]['status'] = c.status_tags['READY']
                        c.reset_ebook_session(args['id'], force=True, filter_keys=False)
                        if not passed: error = progress_status
                elif args.get('text', None) is not None:
                    args['ebook_mode'] = 'text'
                    args['ebook_textarea'] = args['text'].strip()
                    if not args['ebook_textarea']: error = f'Error: The --text is empty.'
                    elif len(args['ebook_textarea']) > max_ebook_textarea_length: error = f'Error: --text input exceeds {max_ebook_textarea_length} characters.'
                    else:
                        progress_status, passed = c.convert_ebook(args)
                        c.context.sessions[args['id']]['status'] = c.status_tags['READY']
                        c.reset_ebook_session(args['id'], force=True, filter_keys=False)
                        if not passed: error = progress_status
                else: error = 'Error: In headless mode, you must specify either an ebook file using --ebook, ebook directory using --ebooks_dir or a raw text using --text.'
        else:
            args['is_gui_process'] = True
            passed_arguments = sys.argv[1:]
            allowed_arguments = {'--share', '--script_mode'}
            passed_args_set = {arg for arg in passed_arguments if arg.startswith('--')}
            if passed_args_set.issubset(allowed_arguments):
                try:
                    from lib.gradio import theme, header_css, build_interface
                    c.progress_bar = c.gr.Progress(track_tqdm=False)
                    app = build_interface(args)
                    if app is not None:
                        gr_blocks_kwargs = {"debug": bool(int(os.environ.get('GRADIO_DEBUG', '0'))), "show_error": debug_mode, "favicon_path": "./favicon.ico", "server_name": interface_host, "server_port": interface_port, "share": args['share'], "max_file_size": max_upload_size, "theme": theme, "css": header_css, "footer_links": ["settings"]}
                        app.queue(default_concurrency_limit=interface_concurrency_limit).launch(**gr_blocks_kwargs)
                except OSError as e: error = f'Connection error: {e}'; c.exception_alert(None, error)
                except socket.error as e: error = f'Socket error: {e}'; c.exception_alert(None, error)
                except KeyboardInterrupt: error = 'Server interrupted by user. Shutting down...'; c.exception_alert(None, error)
                except Exception as e: error = f'An unexpected error occurred: {e}'; c.exception_alert(None, error)
            else: error = 'Error: In GUI mode, no option or only --share can be passed'
        if error:
            print(error)
            sys.exit(1)

if __name__ == '__main__':
    init_multiprocessing()
    main()