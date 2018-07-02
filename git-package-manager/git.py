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

        # communicate with Git via stdin and stdout

        while True:
            try:
                line = sys.stdin.readline()
                print(repr(line), file=sys.stderr)
                if line == "capabilities\n":
                    sys.stdout.write("fetch\n\n")
                    sys.stdout.flush()
                elif line == "list\n":
                    for branch in refs:
                        sys.stdout.write("{} {}\n".format(refs[branch], branch))
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                elif line.startswith('fetch'):

                    _, sha1, name = line.split(' ')
                    if name.endswith("\n"):
                        name = name.rstrip()
                    #print(line, file=sys.stderr)
                    print(repr(sha1), file=sys.stderr)
                    print(repr(name), file=sys.stderr)
                    # TODO Fetch
                    # DO FETCH and DO CHECKOUT

                    sys.stdout.write("\n")
                else:
                    sys.stdout.write("\n")
                    break
            except EOFError:
                break

    def _exec(cmd, *args, **kwargs):
        proc = subprocess.Popen(cmd, *args, **kwargs)
        return proc.communicate()

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
            refs[branch] = sha1

        return refs
