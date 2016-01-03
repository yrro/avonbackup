#!/bin/bash

# This file should be symlinked to .autorun a the root of the volume, as per
# <http://standards.freedesktop.org/autostart-spec/>.

set -eu

base=$(dirname "${BASH_SOURCE[0]}")
target=$base/avonbackup/avonbackup.py
repository=$base/backup

exec xterm \
	-title Backup \
	-hold \
	-e pkexec python "$target" --lockfile="$repository.lock" "$repository"
