#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from .git import Git

def do_clone(argv):

    # DONT checkout, so we need to use `--no-checkout` to avoid it
    # gpm:// will handle the checkout part

    if not argv:
        print('clone failed', file=sys.stderr)
    # TODO for now we assume we only have `url`
    url = argv[0]
    stdout, stderr = Git._exec(['git', 'clone', '--no-checkout', '--depth=1', url])

    pass

def do_pull(argv):

    # use `git fetch` to do pull
    # in gpm:// fetch will do the checkout

    pass

def main(argv):

    # we only provide 'clone' and 'pull'
    # clone for first mirror
    # pull for update mirror
    caps = {
        'clone': do_clone,
        'pull': do_pull,
    }

    if len(argv) <= 1:
        print('argv!', file=sys.stderr)
        return

    print(repr(argv), file=sys.stderr)

    cmd = argv[1]
    if cmd not in caps:
        print('unknown cmd', file=sys.stderr)
        return

    caps[cmd](argv[2:])

    pass

if __name__ == '__main__':
    main(sys.argv)
