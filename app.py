import argparse, socket, shutil, multiprocessing, sys, uuid, copy, warnings

from pathlib import Path

from lib.conf import *
from lib.conf_lang import default_language_code
from lib.conf_models import TTS_ENGINES, default_fine_tuned, default_engine_settings

warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='jieba._compat')

def init_multiprocessing():
    try:
        multiprocessing.set_start_method('spawn')
    except RuntimeError:
        pass

def check_virtual_env(script_mode:str)->bool:
    current_version=sys.version_info[:2]  # (major, minor)
    search_python_env = str(os.path.basename(sys.prefix))
    if search_python_env == 'python_env' or script_mode == FULL_DOCKER or current_version >= min_python_version and current_version <= max_python_version:
        return True
    error=f'''***********
Wrong launch! ebook2audiobook must run in its own virtual environment!
NOTE: If you are running a Docker so you are probably using an old version of ebook2audiobook.
To solve this issue go to download the new version at https://github.com/DrewThomasson/ebook2audiobook
If the directory python_env does not exist in the ebook2audiobook root directory,
run your command with "./ebook2audiobook.command" for Linux and Mac or "ebook2audiobook.cmd" for Windows
to install it all automatically.
{install_info}
***********'''
    print(error)
    return False

def check_python_version()->bool:
    current_version = sys.version_info[:2]  # (major, minor)
    if current_version < min_python_version or current_version > max_python_version:
        error = f'''***********
Wrong launch: Your OS Python version is not compatible! (current: {current_version[0]}.{current_version[1]})
In order to install and/or use ebook2audiobook correctly you must delete completly the folder python_env
and run "./ebook2audiobook.command" for Linux and Mac or "ebook2audiobook.cmd" for Windows.
{install_info}
***********'''
        print(error)
        return False
    else:
        return True

def is_port_in_use(port:int)->bool:
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0',port))==0

def kill_previous_instances(script_name: str):
    current_pid = os.getpid()
    this_script_path = os.path.realpath(script_name)
    import psutil
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if not cmdline:
                continue
            # unify case and absolute paths for comparison
            joined_cmd = ' '.join(cmdline).lower()
            if this_script_path.lower().endswith(script_name.lower()) and \
               (script_name.lower() in joined_cmd) and \
               proc.info['pid'] != current_pid:
                print(f"[WARN] Found running instance PID={proc.info['pid']} -> killing it.")
                proc.kill()
                proc.wait(timeout=3)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

#def register_dlls()->str|bool:
#    candidates = [
#        Path(os.environ['USERPROFILE']) / 'scoop' / 'apps' / 'ffmpeg-shared' / 'current' / 'bin',
#        Path(os.environ.get('PROGRAMFILES', r'C:\Program Files')) / 'ffmpeg' / 'bin',
#        Path(os.environ.get('LOCALAPPDATA', '')) / 'Microsoft' / 'WinGet' / 'Links',
#    ]
#    found = shutil.which('ffmpeg')
#    if found:
#        candidates.append(Path(found).parent)
#    for p in candidates:
#        if p and p.is_dir() and any(p.glob('avcodec-*.dll')):
#            os.add_dll_directory(str(p))
#            return str(p)
#    return False

def main()->None:
    wsl_cmd = ''
    wsl_extra = ''
    if os.environ.get('DOCKER_IN_WSL', '0') == '1' and os.environ.get('DOCKER_DESKTOP', '0') == '0' and os.environ.get('PODMAN_DESKTOP', '0') == '0':
        wsl_cmd = 'wsl --user root --'
    if wsl_cmd:
        wsl_extra = 'DEVICE_TAG=cu128'
    else:
        wsl_extra = 'DEVICE_TAG=cu128 &&'
    # Argument parser to handle optional parameters with descriptions
    parser = argparse.ArgumentParser(
        description='Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.',
        epilog=f'''
Example usage:    
Windows native mode:
    Gradio/GUI:
    ebook2audiobook.cmd
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file' --language eng
Linux/Mac natvie mode:
    Gradio/GUI:
    ./ebook2audiobook.command
    Headless mode:
    ./ebook2audiobook.command --headless --ebook '/path/to/file' --language eng
Docker build image:
    Windows:
        Docker:
            ebook2audiobook.cmd --script_mode build_docker
        Docker Compose:
            ebook2audiobook.cmd --script_mode build_docker --docker_mode compose
        Podman Compose:
            ebook2audiobook.cmd --script_mode build_docker --docker_mode podman
    Linux/Mac
        Docker:
            ./ebook2audiobook.command --script_mode build_docker
        Docker Compose
            ./ebook2audiobook.command --script_mode build_docker --docker_mode compose
        Podman Compose:
            ./ebook2audiobook.command --script_mode build_docker --docker_mode podman
Docker run image:
    Gradio/GUI:
        CPU:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cpu
        CUDA:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" --gpus all --rm -it -p 7860:7860 athomasson2/ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" --device=/dev/dri --rm -it -p 7860:7860 athomasson2/ebook2audiobook:xpu
        JETSON:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" --runtime nvidia  --rm -it -p 7860:7860 athomasson2/ebook2audiobook:jetson[51/60/61 etc...]
    Headless mode:
        CPU:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --rm -it -p 7860:7860 ebook2audiobook:cpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --gpus all --rm -it -p 7860:7860 ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:rocm[6.0/6.1/6.4 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:xpu --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
         {wsl_cmd} docker run -v "./ebooks:/app/ebooks" -v "./audiobooks:/app/audiobooks" -v "./models:/app/models" -v "./voices:/app/voices" -v "/my/real/ebooks/folder/absolute/path:/app/another_ebook_folder" --runtime nvidia --rm -it -p 7860:7860 ebook2audiobook:jetson[51/60/61 etc.] --headless --ebook "/app/another_ebook_folder/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
Docker Compose (i.e. cuda 12.8:
        Run Gradio GUI:
             {wsl_cmd} {wsl_extra} docker compose --profile gpu up --no-log-prefix
        Run Headless mode:
             {wsl_cmd} {wsl_extra} docker compose --profile gpu run --rm ebook2audiobook --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
Podman Compose (i.e. cuda 12.8:
        Run Gradio GUI:
             {wsl_cmd} {wsl_extra} podman-compose -f podman-compose.yml --profile gpu up
        Run Headless mode:
             {wsl_cmd} {wsl_extra} podman-compose -f podman-compose.yml --profile gpu run --rm ebook2audiobook-gpu --headless --ebook "/app/ebooks/myfile.pdf" --voice /app/voices/eng/adult/female/some_voice.wav etc..
SML tags available:
        [break] — silence (random range **0.3–0.6 sec.**)
        [pause] — silence (random range **1.0–1.6 sec.**)
        [pause:N] — fixed pause (**N sec.**)
        [voice:/path/to/voice/file]...[/voice] — switch voice from default or selected voice from GUI/CLI
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    tts_engine_list_keys = [k for k in TTS_ENGINES.keys()]
    tts_engine_list_values = [k for k in TTS_ENGINES.values()]
    all_group = parser.add_argument_group('**** The following options are for container only', 'Optional')
    all_group.add_argument(cli_options[0], type=str, help='Mandatory to build a container. The only value is: build_docker.')
    all_group.add_argument(cli_options[1], type=str, help='Optional. The only values are: podman and compose. without this option standard docker buildx is used.')
    parser.add_argument(cli_options[2], type=str, help='Session to resume the conversion in case of interruption, crash, or reuse of custom models and custom cloning voices.')
    gui_group = parser.add_argument_group('**** The following option are for gradio/gui mode only', 'Optional')
    gui_group.add_argument(cli_options[3], action='store_true', help='''Enable a public shareable Gradio link.''')
    headless_group = parser.add_argument_group('**** The following cli_options are for --headless mode only')
    headless_group.add_argument(cli_options[4], action='store_true', help='''Run the script in headless mode''')
    headless_group.add_argument(cli_options[5], type=str, help='''Path to the ebook file for conversion. Cannot be used when --ebooks_dir or --text is present.''')
    headless_group.add_argument(cli_options[6], type=str, help=f'''Relative or absolute path of the directory containing the files to convert. 
    Cannot be used when --ebook or --text is present.''')
    headless_group.add_argument(cli_options[7], type=str, help='''Raw text for conversion. Cannot be used when --ebook or --ebooks_dir is present.''')
    headless_group.add_argument(cli_options[8], type=str, default=default_language_code, help=f'''Language of the e-book. Default language is set 
    in ./lib/lang.py sed as default if not present. All compatible language codes are in ./lib/lang.py''')
    headless_optional_group = parser.add_argument_group('optional parameters')
    headless_optional_group.add_argument(cli_options[9], type=str, default=None, help='''(Optional) Path to the voice cloning file for TTS engine. 
    Uses the default voice if not present.''')
    headless_optional_group.add_argument(cli_options[10], type=str, default=default_device, choices=list(devices.keys())+[k.lower() for k in devices.keys()], help=f'''(Optional) Processor unit type for the conversion.
    Default is set in ./lib/conf.py if not present. Fall back to CPU if CUDA or MPS is not available.''')
    headless_optional_group.add_argument(cli_options[11], type=str, default=None, choices=tts_engine_list_keys+tts_engine_list_values, help=f'''(Optional) Preferred TTS engine (available are: {tts_engine_list_keys+tts_engine_list_values}.
    Default depends on the selected language. The tts engine should be compatible with the chosen language''')
    headless_optional_group.add_argument(cli_options[12], type=str, default=None, help=f'''(Optional) Path to the custom model zip file cntaining mandatory model files. 
    Please refer to ./lib/models.py''')
    headless_optional_group.add_argument(cli_options[13], type=str, default=default_fine_tuned, help='''(Optional) Fine tuned model path. Default is builtin model.''')
    headless_optional_group.add_argument(cli_options[14], type=str, default=default_output_format, help=f'''(Optional) Output audio format. Default is {default_output_format} set in ./lib/conf.py''')
    headless_optional_group.add_argument(cli_options[15], type=str, default=default_output_channel, help=f'''(Optional) Output audio channel. Default is {default_output_channel} set in ./lib/conf.py''')
    headless_optional_group.add_argument(cli_options[16], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['temperature'], help=f"""(xtts only, optional) Temperature for the model. 
    Default to config.json model. Higher temperatures lead to more creative outputs.""")
    headless_optional_group.add_argument(cli_options[17], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['length_penalty'], help=f"""(xtts only, optional) A length penalty applied to the autoregressive decoder. 
    Default to config.json model. Not applied to custom models.""")
    headless_optional_group.add_argument(cli_options[18], type=int, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['num_beams'], help=f"""(xtts only, optional) Controls how many alternative sequences the model explores. Must be equal or greater than length penalty. 
    Default to config.json model.""")
    headless_optional_group.add_argument(cli_options[19], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['repetition_penalty'], help=f"""(xtts only, optional) A penalty that prevents the autoregressive decoder from repeating itself. 
    Default to config.json model.""")
    headless_optional_group.add_argument(cli_options[20], type=int, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k'], help=f"""(xtts only, optional) Top-k sampling. 
    Lower values mean more likely outputs and increased audio generation speed. 
    Default to config.json model.""")
    headless_optional_group.add_argument(cli_options[21], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['top_p'], help=f"""(xtts only, optional) Top-p sampling. 
    Lower values mean more likely outputs and increased audio generation speed. Default to config.json model.""")
    headless_optional_group.add_argument(cli_options[22], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['speed'], help=f"""(xtts only, optional) Speed factor for the speech generation. 
    Default to config.json model.""")
    headless_optional_group.add_argument(cli_options[23], action='store_true', help=f"""(xtts only, optional) Enable TTS text splitting. This option is known to not be very efficient. 
    Default to config.json model.""")
    headless_optional_group.add_argument(cli_options[24], type=float, default=default_engine_settings[TTS_ENGINES['BARK']]['text_temp'], help=f"""(bark only, optional) Text Temperature for the model. 
    Default to config.json model.""")
    headless_optional_group.add_argument(cli_options[25], type=float, default=default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp'], help=f"""(bark only, optional) Waveform Temperature for the model. 
    Default to config.json model.""")
    headless_optional_group.add_argument(cli_options[26], type=str, help=f'''(Optional) Path to the output directory. Default is set in ./lib/conf.py''')
    headless_optional_group.add_argument(cli_options[27], action='version', version=f'ebook2audiobook version {prog_version}', help='''Show the version of the script and exit''')
    headless_optional_group.add_argument(cli_options[28], action='store_true', help=argparse.SUPPRESS)
    headless_optional_group.add_argument(cli_options[29], action='store_true', help=argparse.SUPPRESS)

    for arg in sys.argv:
        if arg.startswith('--') and arg not in cli_options:
            error = f'Error: Unrecognized option "{arg}"'
            print(error)
            sys.exit(1)

    args = vars(parser.parse_args())

    if not 'help' in args:
        if not check_virtual_env(args['script_mode']):
            sys.exit(1)
        if not check_python_version():
            sys.exit(1)
        # Check if the port is already in use to prevent multiple launches
        if not args['headless'] and is_port_in_use(interface_port):
            error = f'Error: Port {interface_port} is already in use. The web interface may already be running.'
            print(error)
            sys.exit(1)
        args['script_mode'] = args['script_mode'] if args['script_mode'] else NATIVE
        args['share'] =  args['share'] if args['share'] else False
        args['ebook_mode'] = 'single'
        args['ebook_list'] = None

        print(f"v{prog_version} {args['script_mode']} mode")
        
        from lib.classes.device_installer import DeviceInstaller
        manager = DeviceInstaller()
        device_info_str = manager.check_device_info(args['script_mode'])
        if manager.install_device_packages(device_info_str) == 1:
            error = f'Error: Could not installed device packages!'
            print(error)
            sys.exit(1)
        result = manager.install_python_packages()
        if result == 1:
            sys.exit(1)
        #if DEVICE_SYSTEM == systems['WINDOWS'] and not register_dlls():
        #    error = 'WARNING: shared DLLs not found. aborting…'
        #    print(error)
        #    sys.exit(1)

        import lib.core as c

        c.context = c.SessionContext() if c.context is None else c.context
        c.context_tracker = c.SessionTracker() if c.context_tracker is None else c.context_tracker
        c.active_sessions = set() if c.active_sessions is None else c.active_sessions
        error = ''
        if args['headless']:
            args['id'] = args['workflow'] if args['workflow'] else args['session'] if args['session'] else str(uuid.uuid4())
            if args['id'] == workflow_id or not args['session']:
                session = c.context.set_session(args['id'])
            else:
                session_dir = os.path.join(tmp_dir, f"proc-{args['id']}")
                session = c.context.get_session(args['id'])
                if not os.path.exists(session_dir) and not session or (session and not session.get('id', False)):
                    error = 'Session expired or does not exist!'
                    print(error)
                    sys.exit(1)
                session = c.context.set_session(args['id'])
            if not c.context_tracker.start_session(args['id']):
                error = 'Session could not start!'
                print(error)
                sys.exit(1)
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
            engine_setting_keys = {engine: list(settings.keys()) for engine, settings in default_engine_settings.items()}
            valid_model_keys = engine_setting_keys.get(args['tts_engine'], [])
            renamed_args = {}
            for key in valid_model_keys:
                if key in args:
                    renamed_args[f"{args['tts_engine']}_{key}"] = args.pop(key)
            args.update(renamed_args)
            specified_input = sum(
                args.get(k, None) is not None
                for k in ('ebook', 'ebooks_dir', 'text')
            )
            if specified_input > 1:
                error = 'Error: You can only specify one of --ebook, --ebooks_dir, or --text in headless mode.'
            else:
                if args.get('voice', None) is not None:
                    if os.path.exists(args['voice']):
                        args['voice'] = os.path.abspath(args['voice'])
                if args.get('custom_model', None) is not None:
                    if os.path.exists(args['custom_model']):
                        args['custom_model'] = os.path.abspath(args['custom_model'])
                if args.get('output_dir', None) is not None and not os.path.exists(args['output_dir']):
                    error = 'Error: --output_dir path does not exist.'              
                elif args.get('ebooks_dir', None) is not None:
                    args['ebook_mode'] = 'directory'
                    args['ebooks_dir'] = os.path.abspath(args['ebooks_dir'])
                    if not os.path.exists(args['ebooks_dir']):
                        error = f"Error: The provided --ebooks_dir {args['ebooks_dir']} does not exist."                 
                    else:
                        args['ebook_list'] = [
                            os.path.abspath(os.path.join(args['ebooks_dir'], file))
                            for file in os.listdir(args['ebooks_dir'])
                        ]
                        ebook_list = copy.deepcopy(args['ebook_list'])
                        skipped_ebooks = []
                        conversions_ran = 0
                        for i, file in enumerate(ebook_list):
                            if not any(file.endswith(ext) for ext in ebook_formats):
                                warning_msg = f'{Path(file).name} has not a supported format! skipping'
                                print(warning_msg)
                                skipped_ebooks.append(file)
                                if file in args['ebook_list']:
                                    args['ebook_list'].remove(file)
                                continue
                            c.context.sessions[args['id']]['status'] = c.status_tags['READY']
                            c.reset_ebook_session(args['id'], force=True, filter_keys=False)
                            args['ebook_src'] = file
                            progress_status, passed = c.convert_ebook(args)
                            conversions_ran += 1
                            if passed:
                                args['ebook_list'].remove(file)
                            else:
                                error = progress_status
                                break
                        if conversions_ran == 0:
                            error = 'Error: No supported ebook files found in --ebooks_dir.'
                elif args.get('ebook', None) is not None:
                    args['ebook_mode'] = 'single'
                    args['ebook_src'] = os.path.abspath(args['ebook'])
                    if not os.path.exists(args['ebook_src']):
                        error = f"Error: The provided --ebook {args['ebook_src']} does not exist."
                    else:
                        progress_status, passed = c.convert_ebook(args)
                        c.context.sessions[args['id']]['status'] = c.status_tags['READY']
                        c.reset_ebook_session(args['id'], force=True, filter_keys=False)
                        if not passed:
                            error = progress_status
                elif args.get('text', None) is not None:
                    args['ebook_mode'] = 'text'
                    args['ebook_textarea'] = args['text'].strip()
                    if not args['ebook_textarea']:
                        error = f'Error: The --text is empty.'
                    elif len(args['ebook_textarea']) > max_ebook_textarea_length:
                        error = f'Error: --text input exceeds {max_ebook_textarea_length} characters.'
                    else:
                        progress_status, passed = c.convert_ebook(args)
                        c.context.sessions[args['id']]['status'] = c.status_tags['READY']
                        c.reset_ebook_session(args['id'], force=True, filter_keys=False)
                        if not passed:
                            error = progress_status
                else:
                    error = 'Error: In headless mode, you must specify either an ebook file using --ebook, ebook directory using --ebooks_dir or a raw text using --text.'
        else:
            args['is_gui_process'] = True
            passed_arguments = sys.argv[1:]
            allowed_arguments = {'--share', '--script_mode'}
            passed_args_set = {arg for arg in passed_arguments if arg.startswith('--')}
            if passed_args_set.issubset(allowed_arguments):
                try:
                    from lib.gradio import build_interface
                    c.progress_bar = c.gr.Progress(track_tqdm=False)
                    app = build_interface(args)
                    if app is not None:
                        app.queue(
                            default_concurrency_limit=interface_concurrency_limit
                        ).launch(
                            debug=bool(int(os.environ.get('GRADIO_DEBUG', '0'))),
                            show_error=debug_mode, favicon_path='./favicon.ico', 
                            server_name=interface_host, 
                            server_port=interface_port, 
                            share= args['share'], 
                            max_file_size=max_upload_size
                        )
                except OSError as e:
                    error = f'Connection error: {e}'
                    c.exception_alert(None, error)
                except socket.error as e:
                    error = f'Socket error: {e}'
                    c.exception_alert(None, error)
                except KeyboardInterrupt:
                    error = 'Server interrupted by user. Shutting down...'
                    c.exception_alert(None, error)
                except Exception as e:
                    error = f'An unexpected error occurred: {e}'
                    c.exception_alert(None, error)
            else:
                error = 'Error: In GUI mode, no option or only --share can be passed'
        if error:
            print(error)
            sys.exit(1)

if __name__ == '__main__':
    init_multiprocessing()
    main()