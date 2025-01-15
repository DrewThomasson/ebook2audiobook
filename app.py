import argparse
import os
import re
import socket
import subprocess
import sys

from lib.conf import *
from lib.lang import install_info, default_language_code
from lib.models import tts_engines, default_fine_tuned

def check_virtual_env(script_mode):
    if str(os.path.basename(sys.prefix)) == 'python_env' or script_mode == FULL_DOCKER:
        return True  
    error = f'''***********
Wrong launch! ebook2audiobook must run in its own virtual environment!
NOTE: If you are running a Docker so you are probably using an old version of ebook2audiobook.
To solve this issue go to download the new version at https://github.com/DrewThomasson/ebook2audiobook
If the folder python_env does not exist in the ebook2audiobook root folder,
run your command with "./ebook2audiobook.sh" for Linux and Mac or "ebook2audiobook.cmd" for Windows
to install it all automatically.
{install_info}
***********'''
    print(error)
    return False

def check_python_version():
    current_version = sys.version_info[:2]  # (major, minor)
    if current_version < min_python_version or current_version > max_python_version:
        error = f'''***********
Wrong launch: Your OS Python version is not compatible! (current: {current_version[0]}.{current_version[1]})
In order to install and/or use ebook2audiobook correctly you must run 
"./ebook2audiobook.sh" for Linux and Mac or "ebook2audiobook.cmd" for Windows.
{install_info}
***********'''
        print(error)
        return False
    else:
        return True
        
def check_and_install_requirements(file_path):
    if not os.path.exists(file_path):
        print(f'Warning: File {file_path} not found. Skipping package check.')
    try:
        from importlib.metadata import version, PackageNotFoundError
        with open(file_path, 'r') as f:
            contents = f.read().replace('\r', '\n')
            packages = [pkg.strip() for pkg in contents.splitlines() if pkg.strip()]

        missing_packages = []
        for package in packages:
            # Extract package name without version specifier
            pkg_name = re.split(r'[<>=]', package)[0].strip()
            try:
                installed_version = version(pkg_name)
            except PackageNotFoundError:
                print(f'{package} is missing.')
                missing_packages.append(package)
                pass

        if missing_packages:
            print('\nInstalling missing packages...')
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'] + missing_packages)
            except subprocess.CalledProcessError as e:
                print(f'Failed to install packages: {e}')
                return False

        return True
    except Exception as e:
        raise SystemExit(f'An error occurred: {e}')  
        
def check_dictionary():
    import unidic
    unidic_path = unidic.DICDIR
    dicrc = os.path.join(unidic_path, 'dicrc')
    if not os.path.exists(dicrc) or os.path.getsize(dicrc) == 0:
        try:
            print('UniDic dictionary not found or incomplete. Downloading now...')
            subprocess.run(['python', '-m', 'pip', 'cache', 'purge'], check=True)
            subprocess.run(['python', '-m', 'unidic', 'download'], check=True)
        except subprocess.CalledProcessError as e:
            print(f'Failed to download UniDic dictionary. Error: {e}')
            raise SystemExit('Unable to continue without UniDic. Exiting...')
    return True

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def main():
    global is_gui_process

    # Argument parser to handle optional parameters with descriptions
    parser = argparse.ArgumentParser(
        description='Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.',
        epilog='''
Example usage:    
Windows:
    Gradio/GUI:
    ebook2audiobook.cmd
    Headless mode:
    ebook2audiobook.cmd --headless --ebook '/path/to/file'
Linux/Mac:
    Gradio/GUI:
    ./ebook2audiobook.sh
    Headless mode:
    ./ebook2audiobook.sh --headless --ebook '/path/to/file'
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    options = [
        '--script_mode', '--session', '--share', '--headless', 
        '--ebook', '--ebooks_dir', '--language', '--voice', '--device', '--tts_engine', 
        '--custom_model', '--fine_tuned', '--output_format',
        '--temperature', '--length_penalty', '--repetition_penalty', 
        '--top_k', '--top_p', '--speed', '--enable_text_splitting', 
        '--output_dir',
        '--version', '--help'
    ]
    all_group = parser.add_argument_group('**** The following options are for all modes', 'Optional')
    all_group.add_argument(options[0], type=str, help='''Mode the script will run. Accepted values are "native", "docker_utils", "full_docker". 
Default mode is "native". "docker_utils" use a docker for ffmpeg and calibre. 
"full_docker" cannot be used without a docker command.''')
    parser.add_argument(options[1], type=str, help='''Session to resume the conversion in case of interruption, crash, 
    or reuse of custom models and custom cloning voices.''')
    gui_group = parser.add_argument_group('**** The following option are for gradio/gui mode only', 'Optional')
    gui_group.add_argument(options[2], action='store_true', help='''Enable a public shareable Gradio link.''')
    headless_group = parser.add_argument_group('**** The following options are for --headless mode only')
    headless_group.add_argument(options[3], action='store_true', help='''Run the script in headless mode''')
    headless_group.add_argument(options[4], type=str, help='''Path to the ebook file for conversion. Cannot be used when --ebooks_dir is present.''')
    headless_group.add_argument(options[5], type=str, help=f'''Path to the directory containing ebooks for batch conversion. 
    Cannot be used when --ebook is present. Default to "{os.path.basename(ebooks_dir)}" if this option is not present.''')
    headless_group.add_argument(options[6], type=str, default=default_language_code, help=f'''Language of the e-book. Default language is set 
    in ./lib/lang.py sed as default if not present. All compatible language codes are in ./lib/lang.py''')
    headless_optional_group = parser.add_argument_group('optional parameters')
    headless_optional_group.add_argument(options[7], type=str, default=None, help='''(Optional) Path to the voice cloning file for TTS engine. 
    Uses the default voice if not present.''')
    headless_optional_group.add_argument(options[8], type=str, default=default_device, choices=device_list, help=f'''(Optional) Pprocessor unit type for the conversion. 
    Default is set in ./lib/conf.py if not present. Fall back to CPU if GPU not available.''')
    headless_optional_group.add_argument(options[9], type=str, default=None, choices=tts_engines, help=f'''(Optional) Preferred TTS engine (available are:{tts_engines}). 
    Default depends on the selected language. The tts engine should be compatible with the chosen language''')
    headless_optional_group.add_argument(options[10], type=str, default=None, help=f'''(Optional) Path to the custom model zip file cntaining mandatory model files. 
    Please refer to ./lib/models.py''')
    headless_optional_group.add_argument(options[11], type=str, default=default_fine_tuned, help='''(Optional) Fine tuned model path. Default to "std" (builtin) if not present.''')
    headless_optional_group.add_argument(options[12], type=str, default=default_output_format, help=f'''(Optional) Output audio format. Default is set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[13], type=float, default=tts_default_settings['temperature'], help=f"""(xtts only, optional) Temperature for the model. 
    Default to {tts_default_settings['temperature']}. Higher temperatures lead to more creative outputs.""")
    headless_optional_group.add_argument(options[14], type=float, default=tts_default_settings['length_penalty'], help=f"""(xtts only, optional) A length penalty applied to the autoregressive decoder. 
    Default to {tts_default_settings['length_penalty']}. Not applied to custom models.""")
    headless_optional_group.add_argument(options[15], type=float, default=tts_default_settings['repetition_penalty'], help=f"""(xtts only, optional) A penalty that prevents the autoregressive decoder from repeating itself. 
    Default to {tts_default_settings['repetition_penalty']}""")
    headless_optional_group.add_argument(options[16], type=int, default=tts_default_settings['top_k'], help=f"""(xtts only, optional) Top-k sampling. 
    Lower values mean more likely outputs and increased audio generation speed. 
    Default to {tts_default_settings['top_k']}""")
    headless_optional_group.add_argument(options[17], type=float, default=tts_default_settings['top_p'], help=f"""(xtts only, optional) Top-p sampling. 
    Lower values mean more likely outputs and increased audio generation speed. Default to {tts_default_settings['top_p']}""")
    headless_optional_group.add_argument(options[18], type=float, default=tts_default_settings['speed'], help=f"""(xtts only, optional) Speed factor for the speech generation. 
    Default to {tts_default_settings['speed']}""")
    headless_optional_group.add_argument(options[19], action='store_true', help=f"""(xtts only, optional) Enable TTS text splitting. This option is known to not be very efficient. 
    Default is set to {tts_default_settings['enable_text_splitting']}""")                     
    headless_optional_group.add_argument(options[20], type=str, help=f'''(Optional) Path to the output directory. Default is set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[21], action='version',version=f'ebook2audiobook version {version}', help='''Show the version of the script and exit''')

    for arg in sys.argv:
        if arg.startswith('--') and arg not in options:
            print(f'Error: Unrecognized option "{arg}"')
            sys.exit(1)

    args = vars(parser.parse_args())

    if not 'help' in args:
        if not check_virtual_env(args['script_mode']):
            sys.exit(1)

        if not check_python_version():
            sys.exit(1)

        # Check if the port is already in use to prevent multiple launches
        if not args['headless'] and is_port_in_use(interface_port):
            print(f'Error: Port {interface_port} is already in use. The web interface may already be running.')
            sys.exit(1)

        args['script_mode'] = args['script_mode'] if args['script_mode'] else NATIVE
        args['share'] =  args['share'] if args['share'] else False

        if args['script_mode'] == NATIVE:
            check_pkg = check_and_install_requirements(requirements_file)
            if check_pkg:
                if not check_dictionary():
                    sys.exit(1)
            else:
                print('Some packages could not be installed')
                sys.exit(1)

        from lib.functions import web_interface, convert_ebook

        # Conditions based on the --headless flag
        if args['headless']:
            args['is_gui_process'] = False
            args['audiobooks_dir'] = args['output_dir'] if args['output_dir'] else audiobooks_cli_dir
            args['device'] = 'cuda' if args['device'] == 'gpu' else args['device']

            # Condition to stop if both --ebook and --ebooks_dir are provided
            if args['ebook'] and args['ebooks_dir']:
                print('Error: You cannot specify both --ebook and --ebooks_dir in headless mode.')
                sys.exit(1)

            # Condition 1: If --ebooks_dir exists, check value and set 'ebooks_dir'
            if args['ebooks_dir']:
                new_ebooks_dir = None
                if args['ebooks_dir'] == 'default':
                    print(f'Using the default ebooks_dir: {ebooks_dir}')
                    new_ebooks_dir =  os.path.abspath(ebooks_dir)
                else:
                    # Check if the directory exists
                    if os.path.exists(args['ebooks_dir']):
                        new_ebooks_dir = os.path.abspath(args['ebooks_dir'])
                    else:
                        print(f'Error: The provided --ebooks_dir "{args["ebooks_dir"]}" does not exist.')
                        sys.exit(1)

                if os.path.exists(new_ebooks_dir):
                    for file in os.listdir(new_ebooks_dir):
                        # Process files with supported ebook formats
                        if any(file.endswith(ext) for ext in ebook_formats):
                            full_path = os.path.join(new_ebooks_dir, file)
                            print(f'Processing eBook file: {full_path}')
                            args['ebook'] = full_path
                            progress_status, audiobook_file = convert_ebook(args)
                            if audiobook_file is None:
                                print(f'Conversion failed: {progress_status}')
                                sys.exit(1)
                else:
                    print(f'Error: The directory {new_ebooks_dir} does not exist.')
                    sys.exit(1)

            elif args['ebook']:
                progress_status, audiobook_file = convert_ebook(args)
                if audiobook_file is None:
                    print(f'Conversion failed: {progress_status}')
                    sys.exit(1)

            else:
                print('Error: In headless mode, you must specify either an ebook file using --ebook or an ebook directory using --ebooks_dir.')
                sys.exit(1)       
        else:
            args['is_gui_process'] = True
            passed_arguments = sys.argv[1:]
            allowed_arguments = {'--share', '--script_mode'}
            passed_args_set = {arg for arg in passed_arguments if arg.startswith('--')}
            if passed_args_set.issubset(allowed_arguments):
                 web_interface(args)
            else:
                print('Error: In non-headless mode, no option or only --share can be passed')
                sys.exit(1)

if __name__ == '__main__':
    main()