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

"""Commands to syndicate content to other platforms."""

from . import rss


def _module_help(module):
    return module.__doc__.split("\n")[0]


def add_cli_args(parser):
    subparsers = parser.add_subparsers(title="syndication commands", dest="syndicate")
    rss_parser = subparsers.add_parser("rss", help=_module_help(rss))
    rss.add_cli_args(rss_parser)


def main(args):
    rss.main(args)
