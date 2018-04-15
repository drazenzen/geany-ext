#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  runtest.py
#
# Simple approach to run python test(s) on current cursor position in a file.
#


import sys
import os
import re
import subprocess


DEBUG = False
RE_DEF = re.compile(r'^\s+def\s+(.*)\(')
RE_CLASS = re.compile(r'^class\s+(.*)\(')
TEST_CMD = "cd .. ; python devmanage.py test {}"  # Adjust as appropriate


class TempTest(object):
    """Test class for module itself.

    Put cursor somewhere in the class and run module
    with filepath and cursor position arguments.
    """

    def test_something(self):
        # code here
        pass


def get_scope(lines):
    """Tries to find current scope from lines.

    Lines are looped in reversed order (bottom top)

    :param list lines: lines from source code file
    :return: def and/or class name as tuple of strings if founded
    :rtype: tuple
    """
    _def = None
    _class = None
    for line in reversed(lines):
        if _def is None:
            match = re.match(RE_DEF, line)
            if match:
                _def = match.groups()[0]
        if _class is None:
            match = re.match(RE_CLASS, line)
            if match:
                _class = match.groups()[0]
                break
    return (_class, _def)


def run_test(arg):
    """Runs test.
    """
    cmd = TEST_CMD.format(arg)
    try:
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        raise e


def main(args):
    """Main function.

    Two args are needed:
    1. path to python source file
    2. position of cursor in a file

    From script args test argument is created and passed to `run_test` function
    """

    if len(args) != 3:
        sys.exit("Wrong num of args. Got={}".format(args))

    path = os.path.join(os.getcwd(), args[1])
    if not os.path.exists(path):
        sys.exit("File does not exists={}".format(path))

    app = os.path.split(os.path.dirname(path))[1]
    module = os.path.basename(path).split('.')[0]

    position = args[2]
    try:
        position = int(position)
    except (ValueError, TypeError):
        sys.exit("Position could not be loaded={}".format(position))

    if DEBUG: print("::", path, app, module, position)  # noqa

    with open(path, 'r') as f:
        lines = f.readlines()

    _class, _def = get_scope(lines[0:position])

    if DEBUG: print("{}.{}.{}.{}".format(app, module, _class, _def))  # noqa

    arg = "{}.{}".format(app, module)
    if _class:
        arg = "{}.{}".format(arg, _class)
    if _def:
        arg = "{}.{}".format(arg, _def)

    if DEBUG: print("\n\t{}\n".format(arg))  # noqa
    run_test(arg)

    return 0


if __name__ == '__main__':
    main(sys.argv)
