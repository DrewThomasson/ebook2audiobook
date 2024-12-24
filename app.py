import argparse
import os
import regex as re
import socket
import subprocess
import sys
import unidic

from lib.conf import *
from lib.lang import language_mapping, default_language_code

def check_python_version():
    current_version = sys.version_info[:2]  # (major, minor)
    if current_version < min_python_version or current_version > max_python_version:
        error = f'''********** Error: Your OS Python version is not compatible! (current: {current_version[0]}.{current_version[1]})
        Please create a virtual python environment verrsion {min_python_version[0]}.{min_python_version[1]} or {max_python_version[0]}.{max_python_version[1]} 
        with conda or python -v venv **********'''
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
        raise(f'An error occurred: {e}')  
        
def check_dictionary():
    unidic_path = unidic.DICDIR
    dicrc = os.path.join(unidic_path, 'dicrc')
    if not os.path.exists(dicrc) or os.path.getsize(dicrc) == 0:
        try:
            print('UniDic dictionary not found or incomplete. Downloading now...')
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

    # Convert the list of languages to a string to display in the help text
    lang_list_str = ', '.join(list(language_mapping.keys()))

    # Argument parser to handle optional parameters with descriptions
    parser = argparse.ArgumentParser(
        description='Convert eBooks to Audiobooks using a Text-to-Speech model. You can either launch the Gradio interface or run the script in headless mode for direct conversion.',
        epilog='''
Example usage:    
Windows:
    headless:
    ebook2audiobook.cmd --headless --ebook 'path_to_ebook'
    Graphic Interface:
    ebook2audiobook.cmd
Linux/Mac:
    headless:
    ./ebook2audiobook.sh --headless --ebook 'path_to_ebook'
    Graphic Interface:
    ./ebook2audiobook.sh
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    options = [
        '--script_mode', '--share', '--headless', 
        '--session', '--ebook', '--ebooks_dir',
        '--voice', '--language', '--device', '--custom_model',
        '--temperature', '--length_penalty', '--repetition_penalty', 
        '--top_k', '--top_p', '--speed',
        '--enable_text_splitting', '--fine_tuned',
        '--version', '--help'
    ]
    parser.add_argument(options[0], type=str,
                        help='Force the script to run in NATIVE or DOCKER_UTILS')
    parser.add_argument(options[1], action='store_true',
                        help='Enable a public shareable Gradio link. Default to False.')
    parser.add_argument(options[2], nargs='?', const=True, default=False,
                        help='Run in headless mode. Default to True if the flag is present without a value, False otherwise.')
    parser.add_argument(options[3], type=str,
                        help='Session to reconnect in case of interruption (headless mode only)')
    parser.add_argument(options[4], type=str,
                        help='Path to the ebook file for conversion. Required in headless mode.')
    parser.add_argument(options[5], nargs='?', const='default', type=str,
                        help=f'Path to the directory containing ebooks for batch conversion. Default to "{os.path.basename(ebooks_dir)}" if "default" is provided.')
    parser.add_argument(options[6], type=str, default=None,
                        help='Path to the target voice file for TTS. Optional, must be 24khz for XTTS and 16khz for fairseq models, uses a default voice if not provided.')
    parser.add_argument(options[7], type=str, default=default_language_code,
                        help=f'Language for the audiobook conversion. Options: {lang_list_str}. Default to English (eng).')
    parser.add_argument(options[8], type=str, default='cpu', choices=['cpu', 'gpu'],
                        help=f'Type of processor unit for the audiobook conversion. If not specified: check first if gpu available, if not cpu is selected.')
    parser.add_argument(options[9], type=str,
                        help=f'Path to the custom model (.zip file containing {default_model_files}). Required if using a custom model.')
    parser.add_argument(options[10], type=float, default=0.65,
                        help='Temperature for the model. Default to 0.65. Higher temperatures lead to more creative outputs.')
    parser.add_argument(options[11], type=float, default=1.0,
                        help='A length penalty applied to the autoregressive decoder. Default to 1.0. Not applied to custom models.')
    parser.add_argument(options[12], type=float, default=2.5,
                        help='A penalty that prevents the autoregressive decoder from repeating itself. Default to 2.5')
    parser.add_argument(options[13], type=int, default=50,
                        help='Top-k sampling. Lower values mean more likely outputs and increased audio generation speed. Default to 50')
    parser.add_argument(options[14], type=float, default=0.8,
                        help='Top-p sampling. Lower values mean more likely outputs and increased audio generation speed. Default to 0.8')
    parser.add_argument(options[15], type=float, default=1.0,
                        help='Speed factor for the speech generation. Default to 1.0')
    parser.add_argument(options[16], action='store_true',
                        help='Enable splitting text into sentences. Default to False.')                     
    parser.add_argument(options[17], type=str, default=default_fine_tuned,
                        help='Name of the fine tuned model. Optional, uses the standard model according to the TTS engine and language.')
    parser.add_argument(options[18], action='version',version=f'ebook2audiobook version {version}',
                        help='Show the version of the script and exit')

    for arg in sys.argv:
        if arg.startswith('--') and arg not in options:
            print(f'Error: Unrecognized option "{arg}"')
            sys.exit(1)
            
    args = vars(parser.parse_args())

    # Check if the port is already in use to prevent multiple launches
    if not args['headless'] and is_port_in_use(interface_port):
        print(f'Error: Port {interface_port} is already in use. The web interface may already be running.')
        sys.exit(1)
    
    args['script_mode'] = args['script_mode'] if args['script_mode'] else NATIVE
    args['share'] =  args['share'] if args['share'] else False
    
    if args['script_mode'] == NATIVE:
        check_pkg = check_and_install_requirements(requirements_file)
        if check_pkg:
            print('Package requirements ok')
            if check_dictionary():
                print ('Dictionary ok')
            else:
                sys.exit(1)
        else:
            print('Some packages could not be installed')
            sys.exit(1)
    
    from lib.functions import web_interface, convert_ebook

    # Conditions based on the --headless flag
    if args['headless']:
        args['is_gui_process'] = False
        args['audiobooks_dir'] = audiobooks_cli_dir

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
    if not check_python_version():
        sys.exit(1)
    else:
        main()
