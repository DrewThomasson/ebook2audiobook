import os
import sys
import unittest
from unittest.mock import patch, mock_open

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.classes.device_installer import DeviceInstaller


class TestDetectDeviceCudaBranch(unittest.TestCase):
    """detect_device() used to crash on a plain CUDA machine because
    _normalize_version() was only defined inside the ROCm elif branch.
    """

    def test_cuda_branch_does_not_raise_unbound_local_error(self):
        installer = DeviceInstaller()
        installer.system = 'linux'
        installer.arch = 'x86_64'

        def fake_which(cmd):
            return f'/usr/bin/{cmd}' if cmd in ('nvidia-smi', 'lspci') else None

        def fake_check_output(cmd, shell=False, stderr=None):
            if 'nvidia-smi -L' in cmd:
                return b'GPU 0: Tesla T4\n'
            if 'lspci' in cmd:
                return b'01:00.0 3D controller [0302]: NVIDIA Corporation [10de:1eb8]\n'
            return b''

        def fake_exists(path):
            return path == '/usr/local/cuda/version.txt'

        with patch('shutil.which', side_effect=fake_which), \
             patch('subprocess.check_output', side_effect=fake_check_output), \
             patch('os.path.exists', side_effect=fake_exists), \
             patch('builtins.open', mock_open(read_data='CUDA Version 12.4')):
            name, tag, msg = installer.detect_device()

        self.assertEqual(name, 'cuda')
        self.assertEqual(tag, 'cu124')


if __name__ == '__main__':
    unittest.main()
