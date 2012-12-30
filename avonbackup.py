def main ():
	args = parse ()

	unshare ()
	bind_mount ('/', args.temp_mount)
	obnam (args.repository, args.temp_mount)

	if args.sleep:
		import time
		while True:
			time.sleep (86400)

def parse ():
	import argparse
	parser = argparse.ArgumentParser ()
	parser.add_argument ('--temp-mount', help='Path to temporary mount point used during backup', default='/mnt')
	parser.add_argument ('--sleep', help='Sleep when done', action='store_true')
	parser.add_argument ('repository', help='Path to the target obnam repository')
	return parser.parse_args ()

def unshare ():
	import unshare as u
	u.unshare (u.CLONE_NEWNS)

def bind_mount (source, target):
	import ctypes as c
	libc = c.cdll.LoadLibrary ('libc.so.6')
	def check_libc_mount (r):
		if r: raise OSError (c.get_errno ())
	mount = c.CFUNCTYPE (check_libc_mount, c.c_char_p, c.c_char_p, c.c_char_p, c.c_ulong, c.c_void_p, use_errno=True) (('mount', libc))
	MS_MGC_VAL = 0xc0ed0000
	MS_BIND = 4096
	mount (source, target, None, MS_MGC_VAL | MS_BIND, None)

def obnam (repository, source):
	import subprocess
	subprocess.check_call (['obnam',
		'-r', repository,
		'--one-file-system',
		'backup',
		source])

if __name__ == '__main__':
	main ()

# vim: ts=4 sts=4 sw=4 noet
