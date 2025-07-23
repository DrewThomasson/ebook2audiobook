import argparse
import filecmp
import importlib.util
import os
import shutil
import socket
import subprocess
import sys
import tempfile

from pathlib import Path
from lib import *

def check_virtual_env(script_mode):
    current_version = sys.version_info[:2]  # (major, minor)
    if str(os.path.basename(sys.prefix)) == 'python_env' or script_mode == FULL_DOCKER or current_version >= min_python_version and current_version <= max_python_version:
        return True  
    error = f'''***********
Wrong launch! ebook2audiobook must run in its own virtual environment!
NOTE: If you are running a Docker so you are probably using an old version of ebook2audiobook.
To solve this issue go to download the new version at https://github.com/DrewThomasson/ebook2audiobook
If the directory python_env does not exist in the ebook2audiobook root directory,
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
        error = f'Warning: File {file_path} not found. Skipping package check.'
        print(error)
        return False
    try:
        from importlib.metadata import version, PackageNotFoundError
        try:
            from packaging.specifiers import SpecifierSet
        except ImportError:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--no-cache-dir', 'packaging'])
            from packaging.specifiers import SpecifierSet
        import regex as re
        from tqdm import tqdm
        with open(file_path, 'r') as f:
            contents = f.read().replace('\r', '\n')
            packages = [
                pkg.strip()
                for pkg in contents.splitlines()
                if pkg.strip() and re.search(r'[a-zA-Z0-9]', pkg)
            ]
        missing_packages = []
        for package in packages:
            # remove extras so '[lang]==x.y' becomes 'pkg==x.y'
            clean_pkg = re.sub(r'\[.*?\]', '', package)
            pkg_name  = re.split(r'[<>=]', clean_pkg, 1)[0].strip()
            try:
                installed_version = version(pkg_name)
            except PackageNotFoundError:
                error = f'{package} is missing.'
                print(error)
                missing_packages.append(package)
            else:
                # get specifier from clean_pkg, not from the raw string
                spec_str = clean_pkg[len(pkg_name):].strip()
                if spec_str:
                    spec = SpecifierSet(spec_str)
                    if installed_version not in spec:
                        error = (f'{pkg_name} (installed {installed_version}) does not satisfy "{spec_str}".')
                        print(error)
                        missing_packages.append(package)
        if missing_packages:
            msg = '\nInstalling missing or upgrade packages...\n'
            print(msg)
            tmp_dir = tempfile.mkdtemp()
            os.environ['TMPDIR'] = tmp_dir
            result = subprocess.call([sys.executable, '-m', 'pip', 'cache', 'purge'])
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
            with tqdm(total=len(packages),
                      desc='Installation 0.00%',
                      bar_format='{desc}: {n_fmt}/{total_fmt} ',
                      unit='step') as t:
                for package in tqdm(missing_packages, desc="Installing", unit="pkg"):
                    try:
                        subprocess.check_call([
                            sys.executable, '-m', 'pip', 'install',
                            '--no-cache-dir', '--use-pep517', package
                        ])
                        t.update(1)
                    except subprocess.CalledProcessError as e:
                        error = f'Failed to install {package}: {e}'
                        print(error)
                        return False
            msg = '\nAll required packages are installed.'
            print(msg)
        return True
    except Exception as e:
        error = f'check_and_install_requirements() error: {e}'
        raise SystemExit(error)
        return False
       
def check_dictionary():
    import unidic
    unidic_path = unidic.DICDIR
    dicrc = os.path.join(unidic_path, 'dicrc')
    if not os.path.exists(dicrc) or os.path.getsize(dicrc) == 0:
        try:
            error = 'UniDic dictionary not found or incomplete. Downloading now...'
            print(error)
            subprocess.run(['python', '-m', 'unidic', 'download'], check=True)
        except subprocess.CalledProcessError as e:
            error = f'Failed to download UniDic dictionary. Error: {e}. Unable to continue without UniDic. Exiting...'
            raise SystemExit(error)
            return False
    return True

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('0.0.0.0', port)) == 0

def main():
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
    
Tip: to add of silence (1.4 seconds) into your text just use "###" or "[pause]".
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    options = [
        '--script_mode', '--session', '--share', '--headless', 
        '--ebook', '--ebooks_dir', '--language', '--voice', '--device', '--tts_engine', 
        '--custom_model', '--fine_tuned', '--output_format',
        '--temperature', '--length_penalty', '--num_beams', '--repetition_penalty', '--top_k', '--top_p', '--speed', '--enable_text_splitting',
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
    headless_optional_group.add_argument(options[8], type=str, default=default_device, choices=device_list, help=f'''(Optional) Pprocessor unit type for the conversion. 
    Default is set in ./lib/conf.py if not present. Fall back to CPU if GPU not available.''')
    headless_optional_group.add_argument(options[9], type=str, default=None, choices=tts_engine_list_keys+tts_engine_list_values, help=f'''(Optional) Preferred TTS engine (available are: {tts_engine_list_keys+tts_engine_list_values}.
    Default depends on the selected language. The tts engine should be compatible with the chosen language''')
    headless_optional_group.add_argument(options[10], type=str, default=None, help=f'''(Optional) Path to the custom model zip file cntaining mandatory model files. 
    Please refer to ./lib/models.py''')
    headless_optional_group.add_argument(options[11], type=str, default=default_fine_tuned, help='''(Optional) Fine tuned model path. Default is builtin model.''')
    headless_optional_group.add_argument(options[12], type=str, default=default_output_format, help=f'''(Optional) Output audio format. Default is set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[13], type=float, default=None, help=f"""(xtts only, optional) Temperature for the model. 
    Default to config.json model. Higher temperatures lead to more creative outputs.""")
    headless_optional_group.add_argument(options[14], type=float, default=None, help=f"""(xtts only, optional) A length penalty applied to the autoregressive decoder. 
    Default to config.json model. Not applied to custom models.""")
    headless_optional_group.add_argument(options[15], type=int, default=None, help=f"""(xtts only, optional) Controls how many alternative sequences the model explores. Must be equal or greater than length penalty. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[16], type=float, default=None, help=f"""(xtts only, optional) A penalty that prevents the autoregressive decoder from repeating itself. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[17], type=int, default=None, help=f"""(xtts only, optional) Top-k sampling. 
    Lower values mean more likely outputs and increased audio generation speed. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[18], type=float, default=None, help=f"""(xtts only, optional) Top-p sampling. 
    Lower values mean more likely outputs and increased audio generation speed. Default to config.json model.""")
    headless_optional_group.add_argument(options[19], type=float, default=None, help=f"""(xtts only, optional) Speed factor for the speech generation. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[20], action='store_true', help=f"""(xtts only, optional) Enable TTS text splitting. This option is known to not be very efficient. 
    Default to config.json model.""")
    headless_optional_group.add_argument(options[21], type=float, default=None, help=f"""(bark only, optional) Text Temperature for the model. 
    Default to {default_engine_settings[TTS_ENGINES['BARK']]['text_temp']}. Higher temperatures lead to more creative outputs.""")
    headless_optional_group.add_argument(options[22], type=float, default=None, help=f"""(bark only, optional) Waveform Temperature for the model. 
    Default to {default_engine_settings[TTS_ENGINES['BARK']]['waveform_temp']}. Higher temperatures lead to more creative outputs.""")
    headless_optional_group.add_argument(options[23], type=str, help=f'''(Optional) Path to the output directory. Default is set in ./lib/conf.py''')
    headless_optional_group.add_argument(options[24], action='version', version=f'ebook2audiobook version {prog_version}', help='''Show the version of the script and exit''')
    headless_optional_group.add_argument(options[25], action='store_true', help=argparse.SUPPRESS)
    
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
        args['session'] = 'ba800d22-ee51-11ef-ac34-d4ae52cfd9ce' if args['workflow'] else args['session'] if args['session'] else None
        args['share'] =  args['share'] if args['share'] else False
        args['ebook_list'] = None

        print(f"v{prog_version} {args['script_mode']} mode")

        if args['script_mode'] == NATIVE:
            check_pkg = check_and_install_requirements(requirements_file)
            if check_pkg:
                if not check_dictionary():
                    sys.exit(1)
            else:
                error = 'Some packages could not be installed'
                print(error)
                sys.exit(1)

        from lib.functions import SessionContext, convert_ebook_batch, convert_ebook, web_interface
        ctx = SessionContext()
        # Conditions based on the --headless flag
        if args['headless']:
            args['is_gui_process'] = False
            args['audiobooks_dir'] = os.path.abspath(args['output_dir']) if args['output_dir'] else audiobooks_cli_dir
            args['device'] = 'cuda' if args['device'] == 'gpu' else args['device']
            args['tts_engine'] = TTS_ENGINES[args['tts_engine']] if args['tts_engine'] in TTS_ENGINES.keys() else args['tts_engine'] if args['tts_engine'] in TTS_ENGINES.values() else None
            # Condition to stop if both --ebook and --ebooks_dir are provided
            if args['ebook'] and args['ebooks_dir']:
                error = 'Error: You cannot specify both --ebook and --ebooks_dir in headless mode.'
                print(error)
                sys.exit(1)
            # convert in absolute path voice, custom_model if any
            if args['voice']:
                if os.path.exists(args['voice']):
                    args['voice'] = os.path.abspath(args['voice'])
            if args['custom_model']:
                if os.path.exists(args['custom_model']):
                    args['custom_model'] = os.path.abspath(args['custom_model'])
            if not os.path.exists(args['audiobooks_dir']):
                error = 'Error: --output_dir path does not exist.'
                print(error)
                sys.exit(1)                
            if args['ebooks_dir']:
                args['ebooks_dir'] = os.path.abspath(args['ebooks_dir'])
                if not os.path.exists(args['ebooks_dir']):
                    error = f'Error: The provided --ebooks_dir "{args["ebooks_dir"]}" does not exist.'
                    print(error)
                    sys.exit(1)                   
                args['ebook_list'] = []
                for file in os.listdir(args['ebooks_dir']):
                    if any(file.endswith(ext) for ext in ebook_formats):
                        full_path = os.path.abspath(os.path.join(args['ebooks_dir'], file))
                        args['ebook_list'].append(full_path)
                progress_status, passed = convert_ebook_batch(args, ctx)
                if passed is False:
                    error = f'Conversion failed: {progress_status}'
                    print(error)
                    sys.exit(1)
            elif args['ebook']:
                args['ebook'] = os.path.abspath(args['ebook'])
                if not os.path.exists(args['ebook']):
                    error = f'Error: The provided --ebook "{args["ebook"]}" does not exist.'
                    print(error)
                    sys.exit(1) 
                progress_status, passed = convert_ebook(args, ctx)
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
                 web_interface(args, ctx)
            else:
                error = 'Error: In non-headless mode, no option or only --share can be passed'
                print(error)
                sys.exit(1)
if __name__ == '__main__':
    main()
