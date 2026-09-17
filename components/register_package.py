import os
import shutil
import subprocess
import sys


def read_version(repo_root: str) -> str:
    with open(os.path.join(repo_root, 'VERSION.txt'), encoding='utf-8') as f:
        return f.read().strip()


def register_package(repo_root: str) -> int:
    version_str = read_version(repo_root)
    print(f'Registering ebook2audiobook {version_str}...')

    # Prefer uv if available, otherwise fall back to pip
    uv_bin = shutil.which('uv')
    if uv_bin:
        cmd = [uv_bin, 'pip', 'install', '-e', repo_root, '--no-deps']
    else:
        print('Warning: uv not found, falling back to pip')
        cmd = [
            sys.executable, '-m', 'pip', 'install',
            '-e', repo_root, '--no-deps', '--root-user-action=ignore'
        ]

    result = subprocess.run(cmd)
    if result.returncode != 0:
        print('FAILED: pyproject.toml/setup.py did not build. Fix before pushing.')
        return 1
    print(f'OK: ebook2audiobook {version_str} registered. Safe to push.')
    return 0


if __name__ == '__main__':
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(register_package(repo_root))