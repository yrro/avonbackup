def main ():
	args = parse ()

	with lock (args.lockfile):
		unshare ()
		bind_mount ('/', args.temp_mount)
		obnam (args.repository, args.temp_mount)

class lock (object):
	def __init__ (self, lockfile):
		self.lockfile = lockfile
		self.lfd = None

	def __enter__ (self):
		if not self.lockfile:
			return
		import os
		self.lfd = os.open (self.lockfile, os.O_WRONLY | os.O_CREAT)
		os.fchmod (self.lfd, 0666)
		import fcntl
		fcntl.lockf (self.lfd, fcntl.LOCK_EX | fcntl.LOCK_NB)

	def __exit__ (self, *exc):
		if (self.lfd):
			import os
			os.close (self.lfd)

def parse ():
	import argparse
	parser = argparse.ArgumentParser ()
	parser.add_argument ('--lockfile', help='Prevent concurrent instances from running by locking this file')
	parser.add_argument ('--temp-mount', help='Path to temporary mount point used during backup', default='/mnt')
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
	obnam_args = (['obnam', '-r', repository])
	import subprocess
	subprocess.check_call (obnam_args + ['force-lock', source])
	subprocess.check_call (obnam_args + ['backup', source])

if __name__ == '__main__':
	main ()

# vim: ts=4 sts=4 sw=4 noet
