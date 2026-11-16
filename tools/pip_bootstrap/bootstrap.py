# The ebook2audiobook command of a pip/pipx install, and of the Nix package (nix/package.nix) which runs it in an FHS env.
# e2a reads and writes everything next to app.py (models, voices, tmp, audiobooks, python_env) and is installed by
# its launcher, so it cannot run from site-packages. The wheel ships the app files in app_tree: this command copies
# them to a user folder (~/ebook2audiobook, or E2A_HOME) then hands over to the launcher of that folder, exactly as
# if the user ran ./e2a.sh or e2a.cmd there. Standard library only, and python 3.8 syntax: it runs on whatever
# python ran pip, e2a itself runs in the python_env the launcher installs.
import os, sys, json, stat, shlex, shutil, signal, hashlib, subprocess

from typing import Optional

app_name = 'ebook2audiobook'
home_env = 'E2A_HOME'
marker_file = '.pip_managed'
posix_launcher = 'ebook2audiobook.command'
windows_launcher = 'ebook2audiobook.cmd'
# options taking a file or folder: the launcher moves to its own folder before app.py reads them, so a relative
# path is made absolute here from the folder the command was typed in. --output_dir always (it may not exist yet),
# the others only when they exist there, so a path relative to the e2a folder (voices/...) keeps working
path_options = ['--ebook', '--ebooks_dir', '--voice', '--voice_map', '--custom_model', '--output_dir']
# the launchers refuse to start inside another venv or conda env, and python_env's own python would read
# PYTHONHOME/PYTHONPATH: none of them belongs to the python that ran pip any more once the launcher runs
foreign_env_vars = ['VIRTUAL_ENV', 'CONDA_PREFIX', 'PYTHONHOME', 'PYTHONPATH', '__PYVENV_LAUNCHER__']
# what uninstall.sh/.command/.cmd leaves in the folder it empties: the script it runs, which it cannot delete
uninstall_leftovers = ['uninstall.sh', 'uninstall.command', 'uninstall.cmd']
# pip and uv run no package code when they uninstall: this option of the command itself runs the folder's
# uninstaller then removes the folder, and tells how to remove the command last. Never passed to the launcher
uninstall_option = '--uninstall'

def print_error(msg:str)->None:
    # flushed: exec replaces this process right after, and python < 3.9 block-buffers a piped stderr
    print(f"{app_name}: {msg}", file=sys.stderr, flush=True)

def get_package_dir()->str:
    return os.path.dirname(os.path.abspath(__file__))

def get_launcher(app_dir:str)->str:
    return os.path.join(app_dir, windows_launcher if os.name == 'nt' else posix_launcher)

def is_app_dir(path:str)->bool:
    return os.path.isfile(get_launcher(path)) and os.path.isfile(os.path.join(path, 'app.py'))

def is_empty_dir(path:str)->bool:
    # a folder holding only its uninstaller after an uninstall counts as empty: a reinstall starts afresh there
    return os.path.isdir(path) and all(name in uninstall_leftovers for name in os.listdir(path))

def get_source_dir()->Optional[str]:
    app_tree = os.path.join(get_package_dir(), 'app_tree')
    return app_tree if os.path.isdir(app_tree) else None

def get_checkout_dir()->Optional[str]:
    # editable install (pip install -e .): this package is tools/pip_bootstrap of a checkout, run in place
    checkout = os.path.dirname(os.path.dirname(get_package_dir()))
    return checkout if is_app_dir(checkout) else None

def get_home()->str:
    home = os.environ.get(home_env, '').strip()
    if not home:
        home = os.path.join(os.path.expanduser('~'), app_name)
    return os.path.abspath(os.path.expanduser(home))

def read_text(path:str)->str:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except OSError:
        return ''

def read_marker(home:str)->Optional[dict]:
    path = os.path.join(home, marker_file)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            marker = json.load(f)
    except (OSError, ValueError):
        marker = None
    # an unreadable marker still means the folder is pip's: it is synced again, from scratch
    return marker if isinstance(marker, dict) else {}

def write_marker(home:str, version:str, tree_id:str, files:list)->None:
    path = os.path.join(home, marker_file)
    with open(f"{path}.tmp", 'w', encoding='utf-8') as f:
        json.dump({"version": version, "tree_id": tree_id, "files": files}, f, indent=1)
    os.replace(f"{path}.tmp", path)

def list_tree(root:str)->list:
    files = []
    for dir_path, dir_names, file_names in os.walk(root):
        # pip byte-compiles the wheel's .py files: its __pycache__ is not part of the app
        dir_names[:] = sorted(d for d in dir_names if d != '__pycache__')
        for name in sorted(file_names):
            if not name.endswith('.pyc'):
                files.append(os.path.relpath(os.path.join(dir_path, name), root).replace(os.sep, '/'))
    return files

def get_tree_id(source:str, files:list)->str:
    # the content decides an update, not VERSION.txt: a reinstall from a newer commit with the same version updates too
    digest = hashlib.sha256()
    for rel in files:
        digest.update(rel.encode('utf-8') + b'\0')
        with open(os.path.join(source, rel), 'rb') as f:
            digest.update(f.read())
        digest.update(b'\0')
    return digest.hexdigest()

def is_inside(path:str, root:str)->bool:
    path = os.path.normcase(os.path.realpath(path))
    root = os.path.normcase(os.path.realpath(root))
    return path.startswith(root + os.sep)

def copy_file(src:str, dst:str)->None:
    # the content only, never the mode and mtime of the source: a Nix store file is read-only with mtime 1, so its
    # copy could not be overwritten by the next update, and the newer-than check of the launcher (sitecustomize.py)
    # would never see it change. A copy left read-only by an older bootstrap is made writable again first
    if os.path.isfile(dst) and not os.access(dst, os.W_OK):
        os.chmod(dst, stat.S_IMODE(os.stat(dst).st_mode) | stat.S_IWUSR)
    shutil.copyfile(src, dst)
    if os.name != 'nt' and os.stat(src).st_mode & 0o111:
        mode = stat.S_IMODE(os.stat(dst).st_mode)
        # executable for whoever can read it, as chmod +x under the user's umask
        os.chmod(dst, mode | (mode & 0o444) >> 2)

def sync_tree(source:str, home:str, marker:Optional[dict], version:str, tree_id:str, files:list)->None:
    old_files = marker.get('files', []) if marker else []
    old_files = [rel for rel in old_files if isinstance(rel, str)] if isinstance(old_files, list) else []
    # no tree_id until every file is copied: an interrupted sync is done again at the next start, and the
    # previous file list is kept so its stale files are still removed then
    write_marker(home, version, '', sorted(set(files) | set(old_files)))
    for rel in files:
        dst = os.path.join(home, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        copy_file(os.path.join(source, rel), dst)
        if os.name != 'nt' and rel.endswith(('.sh', '.command')):
            os.chmod(dst, os.stat(dst).st_mode | 0o755)
    # files the previous version shipped and this one does not. Only listed files are ever removed: models,
    # voices, audiobooks, python_env, the tts engines venvs and anything else the user or e2a wrote stay
    for rel in sorted(set(old_files) - set(files)):
        path = os.path.join(home, rel)
        if is_inside(path, home) and os.path.isfile(path):
            try:
                os.remove(path)
            except OSError:
                pass
    write_marker(home, version, tree_id, files)

def is_running(home:str)->bool:
    # files replaced under a running ebook2audiobook leave it half old, half new (same check as uninstall.sh).
    # SCRIPT_DIR of the launcher is a resolved path, so is the one searched in the command lines
    real_home = os.path.realpath(home)
    needles = [os.path.join(real_home, 'app.py').lower(), (os.path.join(real_home, 'python_env') + os.sep).lower()]
    if os.name == 'nt':
        cmd = ['powershell', '-NoProfile', '-NonInteractive', '-Command', 'Get-CimInstance Win32_Process | ForEach-Object { $_.CommandLine }']
    else:
        cmd = ['ps', '-A', '-ww', '-o', 'args=']
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, universal_newlines=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return False
    for line in result.stdout.splitlines():
        line = line.lower()
        if any(needle in line for needle in needles):
            return True
    return False

def resolve_path_args(args:list, cwd:str)->list:
    resolved = list(args)
    for i in range(len(resolved) - 1):
        if resolved[i] in path_options and not resolved[i + 1].startswith('--'):
            value = os.path.expanduser(resolved[i + 1])
            if os.path.isabs(value):
                resolved[i + 1] = value
                continue
            candidate = os.path.join(cwd, value)
            if resolved[i] == '--output_dir' or os.path.exists(candidate):
                resolved[i + 1] = os.path.abspath(candidate)
    return resolved

def get_launch_env()->dict:
    env = dict(os.environ)
    for key in foreign_env_vars:
        env.pop(key, None)
    return env

def run_launcher(app_dir:str, args:list)->None:
    launcher = get_launcher(app_dir)
    env = get_launch_env()
    os.chdir(app_dir)
    if os.name == 'nt':
        # no exec on Windows: cmd.exe runs the launcher as a child and its exit code is passed on.
        # /s strips exactly the outer quotes, so a launcher path or arguments with spaces stay quoted. /d skips AutoRun
        cmd_line = subprocess.list2cmdline([launcher] + args)
        comspec = os.environ.get('COMSPEC', 'cmd.exe')
        # Ctrl+C reaches the whole console: the launcher handles it, this process only waits for it
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        sys.exit(subprocess.call(f'"{comspec}" /d /s /c "{cmd_line}"', env=env))
    # the launcher replaces this process: terminal, sudo prompts, signals and exit code are its own
    os.execvpe('bash', ['bash', launcher] + args, env)

def get_remove_command()->str:
    # how this command was installed decides how it is removed: the Nix package runs it from the store,
    # uv tool and pipx leave a receipt in their venv
    if get_package_dir().startswith('/nix/store/'):
        return f"nix profile remove {app_name}, or remove it from the Nix configuration that installed it"
    if os.path.isfile(os.path.join(sys.prefix, 'uv-receipt.toml')):
        return f"uv tool uninstall {app_name}"
    if os.path.isfile(os.path.join(sys.prefix, 'pipx_metadata.json')):
        return f"pipx uninstall {app_name}"
    python = subprocess.list2cmdline([sys.executable]) if os.name == 'nt' else shlex.quote(sys.executable)
    installer = ''
    try:
        from importlib import metadata
        installer = (metadata.distribution(app_name).read_text('INSTALLER') or '').strip()
    except Exception:
        pass
    if installer == 'uv':
        return f"uv pip uninstall --python {python} {app_name}"
    return f"{python} -m pip uninstall {app_name}"

def read_installed(home:str)->list:
    entries = []
    for line in read_text(os.path.join(home, '.installed')).splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            entries.append(line)
    return entries

def count_audiobooks(home:str)->int:
    count = 0
    for dir_path, dir_names, file_names in os.walk(os.path.join(home, 'audiobooks')):
        count += sum(1 for name in file_names if name != '.gitkeep')
    return count

def run_uninstaller(uninstaller:str, home:str)->int:
    env = get_launch_env()
    # uninstall.cmd kills every ebook2audiobook.exe, which on Windows is this pip command too
    env['E2A_PIP_UNINSTALL'] = '1'
    if os.name == 'nt':
        cmd_line = subprocess.list2cmdline([uninstaller])
        comspec = os.environ.get('COMSPEC', 'cmd.exe')
        proc = subprocess.Popen(f'"{comspec}" /d /s /c "{cmd_line}"', env=env, cwd=home)
    else:
        proc = subprocess.Popen(['bash', uninstaller], env=env, cwd=home)
    # Ctrl+C reaches the uninstaller too, which decides: wait for its exit code whatever happens here
    while True:
        try:
            return proc.wait()
        except KeyboardInterrupt:
            continue

def uninstall()->None:
    remove_msg = f"Last step, remove the {app_name} command itself: {get_remove_command()}"
    if get_source_dir() is None:
        print_error('this is an editable install: it runs its checkout, which it never uninstalls.')
        print(remove_msg)
        sys.exit(1)
    home = get_home()
    marker = read_marker(home)
    if not os.path.isdir(home) or (marker is None and is_empty_dir(home)):
        # never started, or only the uninstaller left by a previous uninstall
        if os.path.isdir(home):
            shutil.rmtree(home, ignore_errors=True)
        print(f"No ebook2audiobook folder to remove in {home}.")
        print(remove_msg)
        return
    if marker is None:
        print_error(f"{home} was not installed by pip, so it is left as is: remove it with its own uninstaller.")
        print(remove_msg)
        sys.exit(1)
    if is_running(home):
        print_error(f"ebook2audiobook is still running from {home}. Quit it first, then run {app_name} {uninstall_option} again.")
        sys.exit(1)
    uninstaller = os.path.join(home, 'uninstall.cmd' if os.name == 'nt' else 'uninstall.command')
    if not os.path.isfile(uninstaller):
        print_error(f"{uninstaller} is missing: start {app_name} once to restore the folder, then run {app_name} {uninstall_option} again.")
        sys.exit(1)
    installed = read_installed(home)
    audiobooks = count_audiobooks(home)
    print(f"Uninstalling ebook2audiobook from {home}, all of it is deleted:")
    print('  python_env, models, voices and the tts engines venvs')
    if installed:
        print(f"  the programs it installed (listed in .installed): {', '.join(installed)}")
    if audiobooks:
        print(f"  your {audiobooks} file(s) in {os.path.join(home, 'audiobooks')}: move the ones to keep out first")
    print(flush=True)
    rc = run_uninstaller(uninstaller, home)
    if rc != 0 or not is_empty_dir(home):
        print_error(f"the uninstaller stopped before the end (exit code {rc}): {home} is kept. Run {app_name} {uninstall_option} again to finish.")
        sys.exit(1)
    try:
        shutil.rmtree(home)
        print(f"ebook2audiobook and {home} are removed.")
    except OSError as e:
        print_error(f"ebook2audiobook is uninstalled but {home} could not be removed ({e}): delete it by hand.")
    print(remove_msg)

def main()->None:
    if uninstall_option in sys.argv[1:]:
        if len(sys.argv) != 2:
            print_error(f"{uninstall_option} takes no other option.")
            sys.exit(1)
        uninstall()
        return
    args = resolve_path_args(sys.argv[1:], os.getcwd())
    source = get_source_dir()
    if source is None:
        checkout = get_checkout_dir()
        if checkout is None:
            print_error('the app files are missing from this install. Reinstall it with pip.')
            sys.exit(1)
        run_launcher(checkout, args)
    version = read_text(os.path.join(source, 'VERSION.txt'))
    home = get_home()
    if os.path.exists(home) and not os.path.isdir(home):
        print_error(f"{home} is a file. Set {home_env} to the folder ebook2audiobook must be installed in.")
        sys.exit(1)
    marker = read_marker(home)
    if marker is None and os.path.isdir(home) and not is_empty_dir(home):
        if is_app_dir(home):
            # a git clone or a downloaded copy: the user's own, started as it is and never changed by pip
            home_version = read_text(os.path.join(home, 'VERSION.txt'))
            if home_version != version:
                print_error(f"{home} was not installed by pip, so it stays at version {home_version or '?'} (pip has {version}). Update it as you installed it (git pull, new download), or set {home_env} to another folder.")
            run_launcher(home, args)
        print_error(f"{home} is not empty and is not an ebook2audiobook folder. Set {home_env} to a new or empty folder.")
        sys.exit(1)
    files = list_tree(source)
    tree_id = get_tree_id(source, files)
    if marker is None or marker.get('tree_id') != tree_id:
        if marker is not None and is_running(home):
            print_error(f"ebook2audiobook is still running from {home}. Quit it first, then run this command again to update it to {version}.")
            sys.exit(1)
        print(f"{'Installing' if marker is None else 'Updating'} ebook2audiobook {version} in {home}", flush=True)
        os.makedirs(home, exist_ok=True)
        sync_tree(source, home, marker, version, tree_id, files)
    run_launcher(home, args)

if __name__ == '__main__':
    main()
