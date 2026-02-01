import argparse, socket, multiprocessing, sys, warnings

from lib.conf import *
from lib.conf_lang import default_language_code
from lib.conf_models import TTS_ENGINES, default_fine_tuned, default_engine_settings

warnings.filterwarnings('ignore', category=SyntaxWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='jieba._compat')

def init_multiprocessing():
    if sys.platform == systems['MACOS']:
        try:
            multiprocessing.set_start_method('spawn')
        except RuntimeError:
            pass
    elif sys.platform == systems['LINUX']:
        try:
            multiprocessing.set_start_method('fork')
        except RuntimeError:
            pass
    else:
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

def main()->None:
    # Argument parser to handle optional parameters with descriptions
    parser = argparse.ArgumentParser(
        description='Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.',
        epilog='''
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
    ebook2audiobook.cmd --script_mode build_docker
    Linux/Mac
    ./ebook2audiobook.command --script_mode build_docker
Docker run image:
    Gradio/GUI:
        CPU:
        docker run --rm -it -p 7860:7860 ebook2audiobook:cpu
        CUDA:
        docker run --gpus all --rm -it -p 7860:7860 ebook2audiobook:cu[118/122/124/126 etc..]
        ROCM:
        docker run --device=/dev/kfd --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:rocm[6.0/6.1/6.4 etc..]
        XPU:
        docker run --device=/dev/dri --rm -it -p 7860:7860 ebook2audiobook:xpu
        JETSON:
        docker run --runtime nvidia  --rm -it -p 7860:7860 ebook2audiobook:jetson[60/61 etc...]
    Headless mode:
        CPU:
        docker run --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:cpu --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        CUDA:
        docker run --gpus all --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:cu[118/122/124/126 etc..] --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        ROCM:
        docker run --device=/dev/kfd --device=/dev/dri --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:rocm[6.0/6.1/6.4 etc..] --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        XPU:
        docker run --device=/dev/dri --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:xpu --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
        JETSON:
        docker run --runtime nvidia --rm -it -v "/my/real/ebooks/folder/absolute/path:/app/ebooks" -v "/my/real/output/folder/absolute/path:/app/audiobooks" -p 7860:7860 ebook2audiobook:jetson[51/60/61 etc...] --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]

Docker Compose (i.e. cuda 12.8:
        Build
            DEVICE_TAG=cu128 docker compose --progress plain --profile gpu up -d --build
        Run Gradio GUI:
            DEVICE_TAG=cu128 docker compose --profile gpu up -d
        Run Headless mode:
            DEVICE_TAG=cu128 docker compose --profile gpu run --rm ebook2audiobook --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]

Podman Compose (i.e. cuda 12.8:
        Build
            DEVICE_TAG=cu128 podman-compose -f podman-compose.yml up -d --build
        Run Gradio GUI:
            DEVICE_TAG=cu128 podman-compose -f podman-compose.yml up -d
        Run Headless mode:
            DEVICE_TAG=cu128 podman-compose -f podman-compose.yml run --rm ebook2audiobook --headless --ebook "/app/ebooks/myfile.pdf" [--voice /app/my/voicepath/voice.mp3 etc..]
    
SML tags available:
        [break]` — silence (random range **0.3–0.6 sec.**)
        [pause]` — silence (random range **1.0–1.6 sec.**)
        [pause:N]` — fixed pause (**N sec.**)
        [voice:/path/to/voice/file]...[/voice]` — switch voice from default or selected voice from GUI/CLI
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    options = [
        '--script_mode', '--session', '--share', '--headless', 
        '--ebook', '--ebooks_dir', '--language', '--voice', '--device', '--tts_engine', 
        '--custom_model', '--fine_tuned', '--output_format', '--output_channel',
        '--temperature', '--length_penalty', '--num_beams', '--repetition_penalty', 
        '--top_k', '--top_p', '--speed', '--enable_text_splitting',
        '--text_temp', '--waveform_temp',
        '--output_dir', '--version', '--workflow', '--help'
    ]
    tts_engine_list_keys = [k for k in TTS_ENGINES.keys()]
    tts_engine_list_values = [k for k in TTS_ENGINES.values()]
    all_group = parser.add_argument_group('**** The following options are for all modes', 'Optional')
    all_group.add_argument(options[0], type=str, help=argparse.SUPPRESS)
    parser.add_argument(options[1], type=str, help='''Session to resume the conversion in case of interruption, crash, 
    or reuse of custom models and custom cloning voices.''')
    gui_group = parser.add_argument_group('**** The following option are for gradio/gui mode only', 'Optional')
    gui_group.add_argument(options[2], action='store_true', help='''Enable a public shareable Gradio link.''')
    headless_group = parser.add_argument_group('**** The following options are for --headless mode only')
    headless_group.add_argument(options[3], action='store_true', help='''Run the script in headless mode''')
    headless_group.add_argument(options[4], type=str, help='''Path to the ebook file for conversion. Cannot be used when --ebooks_dir is present.''')
    headless_group.add_argument(options[5], type=str, help=f'''Relative or absolute path of the directory containing the files to convert. 
    Cannot be used when --ebook is present.''')
    headless_group.add_argument(options[6], type=str, default=default_language_code, help=f'''Language of the e-book. Default language is set 
    in ./lib/lang.py sed as default if not present. All compatible language codes are in ./lib/lang.py''')
    headless_optional_group = parser.add_argument_group('optional parameters')
    headless_optional_group.add_argument(options[7], type=str, default=None, help='''(Optional) Path to the voice cloning file for TTS engine. 
    Uses the default voice if not present.''')
    headless_optional_group.add_argument(options[8], type=str, default=default_device, choices=list(devices.keys()), help=f'''(Optional) Processor unit type for the conversion.
    Default is set in ./lib/conf.py if not present. Fall back to CPU if CUDA or MPS is not available.''')
    headless_optional_group.add_argument(options[9], type=str, default=None, choices=tts_engine_list_keys+tts_engine_list_values, help=f'''(Optional) Preferred TTS engine (available are: {tts_engine_list_keys+tts_engine_list_values}.
    Default depends on the selected language. The tts engine should be compatible with the chosen language''')
    headless_optional_group.add_argument(options[10], type=str, default=None, help=f'''(Optional) Path to the custom model zip file cntaining mandatory model files. 
    Please refer to ./lib/models.py''')
    headless_optional_group.add_argument(options[11], type=str, default=default_fine_tuned, help='''(Optional) Fine tuned model path. Default is builtin model.''')
    headless_optional_group.add_argument(options[12], type=str, default=default_output_format, help=f'''(Optional) Output audio format. Default is {default_output_format} set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[13], type=str, default=default_output_channel, help=f'''(Optional) Output audio channel. Default is {default_output_channel} set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[14], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['temperature'], help=f"""(xtts only, optional) Temperature for the model. 
    Default to config.json model. Higher temperatures lead to more creative outputs.""")
    headless_optional_group.add_argument(options[15], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['length_penalty'], help=f"""(xtts only, optional) A length penalty applied to the autoregressive decoder. 
    Default to config.json model. Not applied to custom models.""")
    headless_optional_group.add_argument(options[16], type=int, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['num_beams'], help=f"""(xtts only, optional) Controls how many alternative sequences the model explores. Must be equal or greater than length penalty. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[17], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['repetition_penalty'], help=f"""(xtts only, optional) A penalty that prevents the autoregressive decoder from repeating itself. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[18], type=int, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['top_k'], help=f"""(xtts only, optional) Top-k sampling. 
    Lower values mean more likely outputs and increased audio generation speed. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[19], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['top_p'], help=f"""(xtts only, optional) Top-p sampling. 
    Lower values mean more likely outputs and increased audio generation speed. Default to config.json model.""")
    headless_optional_group.add_argument(options[20], type=float, default=default_engine_settings[TTS_ENGINES['XTTSv2']]['speed'], help=f"""(xtts only, optional) Speed factor for the speech generation. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[21], action='store_true', help=f"""(xtts only, optional) Enable TTS text splitting. This option is known to not be very efficient. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[22], type=float, default=default_engine_settings[TTS_ENGINES['BARK']]['text_temp'], help=f"""(bark only, optional) Text Temperature for the model. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[23], type=float, default=default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp'], help=f"""(bark only, optional) Waveform Temperature for the model. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[24], type=str, help=f'''(Optional) Path to the output directory. Default is set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[25], action='version', version=f'ebook2audiobook version {prog_version}', help='''Show the version of the script and exit''')
    headless_optional_group.add_argument(options[26], action='store_true', help=argparse.SUPPRESS)
    
    for arg in sys.argv:
        if arg.startswith('--') and arg not in options:
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
        args['ebook_list'] = None

        print(f"v{prog_version} {args['script_mode']} mode")
        from lib.classes.device_installer import DeviceInstaller
        manager = DeviceInstaller()
        result = manager.install_python_packages()
        if result == 0:
            device_info_str = manager.check_device_info(args['script_mode'])
            if manager.install_device_packages(device_info_str) == 1:
                error = f'Error: Could not installed device packages!'
                print(error)
                sys.exit(1)
        import lib.core as c
        c.context = c.SessionContext() if c.context is None else c.context
        c.context_tracker = c.SessionTracker() if c.context_tracker is None else c.context_tracker
        c.active_sessions = set() if c.active_sessions is None else c.active_sessions
        if args['headless']:
            args['id'] = 'ba800d22-ee51-11ef-ac34-d4ae52cfd9ce' if args['workflow'] else args['session'] if args['session'] else None
            args['is_gui_process'] = False
            args['chapters_preview'] = False
            args['event'] = ''
            args['audiobooks_dir'] = os.path.abspath(args['output_dir']) if args['output_dir'] else audiobooks_cli_dir
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
            # Condition to stop if both --ebook and --ebooks_dir are provided
            if args['ebook'] and args['ebooks_dir']:
                error = 'Error: You cannot specify both --ebook and --ebooks_dir in headless mode.'
                print(error)
                sys.exit(1)
            # convert in absolute path voice, custom_model if any
            if args['voice']:
                if os.path.exists(args['voice']):
                    args['voice'] = os.path.abspath(args['voice'])
            if args['custom_model'] is not None:
                if os.path.exists(args['custom_model']):
                    args['custom_model'] = os.path.abspath(args['custom_model'])
            if not os.path.exists(args['audiobooks_dir']):
                error = 'Error: --output_dir path does not exist.'
                print(error)
                sys.exit(1)                
            if args['ebooks_dir']:
                args['ebooks_dir'] = os.path.abspath(args['ebooks_dir'])
                if not os.path.exists(args['ebooks_dir']):
                    error = f"Error: The provided --ebooks_dir {args['ebooks_dir']} does not exist."
                    print(error)
                    sys.exit(1)                   
                args['ebook_list'] = []
                for file in os.listdir(args['ebooks_dir']):
                    if any(file.endswith(ext) for ext in ebook_formats):
                        full_path = os.path.abspath(os.path.join(args['ebooks_dir'], file))
                        args['ebook_list'].append(full_path)
                progress_status, passed = c.convert_ebook_batch(args)
                if passed is False:
                    error = f'Conversion failed: {progress_status}'
                    print(error)
                    sys.exit(1)
            elif args['ebook']:
                args['ebook'] = os.path.abspath(args['ebook'])
                if not os.path.exists(args['ebook']):
                    error = f"Error: The provided --ebook {args['ebook']} does not exist."
                    print(error)
                    sys.exit(1) 
                progress_status, passed = c.convert_ebook(args)
                if passed is False:
                    error = f'Conversion failed: {progress_status}'
                    print(error)
                    sys.exit(1)
            else:
                error = 'Error: In headless mode, you must specify either an ebook file using --ebook or an ebook directory using --ebooks_dir.'
                print(error)
                sys.exit(1)       
        else:
            args['is_gui_process'] = True
            passed_arguments = sys.argv[1:]
            allowed_arguments = {'--share', '--script_mode'}
            passed_args_set = {arg for arg in passed_arguments if arg.startswith('--')}
            if passed_args_set.issubset(allowed_arguments):
                try:
                    from lib.gradio import build_interface
                    app, theme, header_css = build_interface(args)
                    if app is not None:
                        app.queue(
                            default_concurrency_limit=interface_concurrency_limit
                        ).launch(
                        	theme=theme,
                            css=header_css,
                            debug=bool(int(os.environ.get('GRADIO_DEBUG', '0'))),
                            show_error=debug_mode, favicon_path='./favicon.ico', 
                            server_name=interface_host, 
                            server_port=interface_port, 
                            share= args['share'], 
                            max_file_size=max_upload_size,
                            footer_links=['settings'],
                            allowed_paths=[
                                os.path.join(root_dir, 'voices'),
                                os.path.join(root_dir, 'audiobooks'),
                                os.path.join(root_dir, 'models'),
                                os.path.join(root_dir, 'tmp'),
                                os.path.join(root_dir, 'ebooks')
                            ]
                        )
                except OSError as e:
                    error = f'Connection error: {e}'
                    c.alert_exception(error, None)
                except socket.error as e:
                    error = f'Socket error: {e}'
                    c.alert_exception(error, None)
                except KeyboardInterrupt:
                    error = 'Server interrupted by user. Shutting down...'
                    c.alert_exception(error, None)
                except Exception as e:
                    error = f'An unexpected error occurred: {e}'
                    c.alert_exception(error, None)
            else:
                error = 'Error: In GUI mode, no option or only --share can be passed'
                print(error)
                sys.exit(1)

if __name__ == '__main__':
    init_multiprocessing()
    main()
