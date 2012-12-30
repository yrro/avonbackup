import argparse
parser = argparse.ArgumentParser ()
parser.add_argument ("--temp-mount", help='Path to temporary mount point used during backup', default='/mnt')
parser.add_argument ('repository', help='Path to the target obnam repository')
args = parser.parse_args ()

import unshare
unshare.unshare (unshare.CLONE_NEWNS)

import ctypes
libc = ctypes.cdll.LoadLibrary ('libc.so.6')

def check_libc_mount (r):
	if r:
		raise OSError (ctypes.get_errno ())
mount = ctypes.CFUNCTYPE (check_libc_mount, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_void_p, use_errno=True) (('mount', libc))
MS_MGC_VAL = 0xc0ed0000
MS_BIND = 4096
mount ('/', args.temp_mount, None, MS_MGC_VAL | MS_BIND, None)

import subprocess
subprocess.check_call (['obnam',
	'-r', args.repository,
	'--one-file-system',
	'backup',
	args.temp_mount])

# vim: ts=4 sts=4 sw=4 noet
