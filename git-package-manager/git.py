#!/usr/bin/env python3
# -*- coding: utf8 -*-

import subprocess
from subprocess import PIPE
import re

import sys

# This should be a static class to collect all git method
class Git(object):

    def git_helper(argv):

        remotename = argv[1]
        url = argv[2]
        url = re.sub(r'^gpm:', 'git:', url)

        refs = Git.list_remote(url)
        print(refs, file=sys.stderr)

    def _exec(cmd, *args, **kwargs):
        pass

    def list_remote(url):
        proc = subprocess.Popen(['git', 'ls-remote', url], stdout=PIPE, stderr=PIPE, stdin=PIPE)
        stdout, stderr = proc.communicate()
        outs = stdout.decode('utf-8').split('\n')
        refs = {}
        for line in outs:
            # split into dict
            if not line:
                continue
            print(repr(line), file=sys.stderr)
            print(repr(line.split("\t")), file=sys.stderr)
            sha1, branch = line.split("\t")
            refs[sha1] = branch

        return refs
