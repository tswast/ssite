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

from . import clean
from . import header
from . import index
from . import note
from . import rmblock
import ssite.syndicate.cli


def _module_help(module):
    return module.__doc__.split("\n")[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(title="commands", dest="command")

    index_parser = subparsers.add_parser("index", help=_module_help(index))
    index.add_cli_args(index_parser)

    clean_parser = subparsers.add_parser("clean", help=_module_help(clean))
    clean.add_cli_args(clean_parser)

    note_parser = subparsers.add_parser("note", help=_module_help(note))
    note.add_cli_args(note_parser)

    rmblock_parser = subparsers.add_parser("beta_rmblock", help=_module_help(rmblock))
    rmblock.add_cli_args(rmblock_parser)

    header_parser = subparsers.add_parser("header", help=_module_help(header))
    header.add_cli_args(header_parser)

    syndicate_parser = subparsers.add_parser(
        "syndicate", help=_module_help(ssite.syndicate.cli)
    )
    ssite.syndicate.cli.add_cli_args(syndicate_parser)

    args = parser.parse_args()
    if args.command == "clean":
        clean.main(args)
    elif args.command == "index":
        index.main(args)
    elif args.command == "note":
        note.main(args)
    elif args.command == "header":
        header.main(args)
    elif args.command == "syndicate":
        ssite.syndicate.cli.main(args)
    elif args.command == "beta_rmblock":
        rmblock.main(args)
    else:
        print('Got unknown command "{}".'.format(args.command), file=sys.stderr)
        parser.print_help()
