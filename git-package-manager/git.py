#!/usr/bin/env python3
# -*- coding: utf8 -*-

import subprocess
from subprocess import PIPE
from pathlib import Path
from collections import deque

import hashlib
import re
import os
import sys
import zlib
import github3

# This should be a static class to collect all git method
class Git(object):

    def git_helper(argv):

        remotename = argv[1]
        url = argv[2]
        url = re.sub(r'^gpm:', 'git:', url)
        url = url.rstrip('/')

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

                    GIT_DIR = os.environ['GIT_DIR']
                    GIT_WORK_TREE = Path(GIT_DIR).parent
                    GIT_WORK_TREE = os.environ.get('GIT_WORK_TREE', GIT_WORK_TREE)
                    print(GIT_DIR, file=sys.stderr)
                    print(GIT_WORK_TREE, file=sys.stderr)

                    # get commit and tree from github api
                    # TODO we need a interface
                    # for now only support Github
                    assert 'github.com' in url

                    github = github3.GitHub()

                    # find username and repo name
                    username, reponame = re.search(r'.*://[^/]*/([^/]*)/([^/]*)/?', url).group(1, 2)
                    repo = github.repository(username, reponame)
                    commit = repo.git_commit(sha1)
                    print(repr(commit), file=sys.stderr)
                    print(repr(commit.tree.sha), file=sys.stderr)
                    print(repr(commit.author), file=sys.stderr)
                    #tree = repo.tree(commit.tree.sha)

                    # now we found the tree
                    # MUST check the tree existed in .git/
                    # walk for all tree node and if not existed and download it
                    # we need to pack the tree to git object format
                    # TODO we don't care 'truncated', that will be a problem
                    def dfs(path, tree_sha):
                        # check if tree_sha existed
                        # TODO for now we assume we have no tree

                        tree = repo.tree(tree_sha).tree
                        # save tree object
                        os.makedirs(os.path.join(GIT_DIR, 'objects', tree_sha[:2]), exist_ok=True)
                        frame = bytearray()
                        for node in tree:
                            print(node.path, file=sys.stderr)
                            frame.extend(node.mode.encode('ascii'))
                            frame.extend(b' ')
                            frame.extend(node.path.encode('utf-8'))
                            frame.append(0)
                            frame.extend(bytearray.fromhex(node.sha))

                        print(repr(os.path.join(GIT_DIR, 'objects', tree_sha[:2], tree_sha[2:])), file=sys.stderr)
                        tree_object = Path(os.path.join(GIT_DIR, 'objects', tree_sha[:2], tree_sha[2:]))

                        print(tree_sha, file=sys.stderr)

                        frame = b'tree ' + str(len(frame)).encode('ascii') + b'\x00' + frame
                        print(repr(frame), file=sys.stderr)
                        print(hashlib.sha1(frame).hexdigest(), file=sys.stderr)

                        with tree_object.open('wb') as f:
                            f.write(zlib.compress(frame, level=1))

                        for node in tree:
                            # if tree, dfs
                            if node.type == 'tree':
                                #print(path, file=sys.stderr)
                                dfs("{}/{}".format(path, node.path), node.sha)
                            else:
                                #print("{} {}/{}".format(node.sha, path, node.path), file=sys.stderr)
                                pass

                    tree_sha = commit.tree.sha
                    dfs('.', tree_sha)

                    # TODO write commit object!

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
