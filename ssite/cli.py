# Copyright 2018, The Ssite Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import argparse
import sys

from . import blogindex
from . import cleanhtml


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(title='commands', dest='command')

    blogindex_parser = subparsers.add_parser(
        'blogindex', help=blogindex.__doc__)
    blogindex.add_cli_args(blogindex_parser)

    cleanhtml_parser = subparsers.add_parser(
        'cleanhtml', help=cleanhtml.__doc__)
    cleanhtml.add_cli_args(cleanhtml_parser)

    args = parser.parse_args()
    if args.command == 'cleanhtml':
        cleanhtml.main(args)
    elif args.command == 'blogindex':
        blogindex.main(args)
    else:
        print(
            'Got unknown command "{}".'.format(args.command),
            file=sys.stderr)
        parser.print_help()
