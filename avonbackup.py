from __future__ import print_function

import subprocess

def main ():
	args = parse ()

	with lock (args.lockfile):
		unshare ()
		bind_mount ('/', args.temp_mount)
		obnam (args.repository, args.temp_mount)
	print('Backup complete.')

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
	subprocess.check_call (['mount', '--make-rprivate', '/'])

def bind_mount (source, target):
	subprocess.check_call (['mount', '--bind', source, target])
	subprocess.check_call (['mount', '-o', 'bind,remount,ro', target])

def obnam (repository, source):
	import re
	excludes = [
		r'^{}/tmp/.',
		r'^{}/var/tmp/.',
		r'^{}/var/cache/apt/.*\.bin$',
		r'^{}/var/cache/apt/archives/.*\.deb$',
		r'^{}/var/cache/apt/archives/partial/.',
		r'^{}/home/[^/]/\.cache/.',
	]
	obnam_args = ['obnam',
		'--no-default-configs',
		'--log={}.log'.format(repository),
		'--log-max=1Mi',
		'--log-level=debug',
		'--keep=12m,10y',
		'--exclude-caches',
		'-r', repository]
	for e in excludes:
		obnam_args.extend(['--exclude', e.format((re.escape(source)),)])
	subprocess.check_call (obnam_args + ['force-lock', source])
	subprocess.check_call (obnam_args + ['backup', source])

if __name__ == '__main__':
	main ()

# vim: ts=4 sts=4 sw=4 noet
