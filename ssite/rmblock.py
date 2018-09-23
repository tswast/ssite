#!/usr/bin/env python
# coding: utf-8

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

"""Remove specified text blocks from the contents of files. (Beta)"""

import re


def remove_blocks(contents, start_regex, end_regex):
    output_lines = []
    start_prog = re.compile(start_regex)
    end_prog = re.compile(end_regex)
    block_started = False

    for line in contents.split("\n"):
        if block_started:
            # Stop skipping lines when the end is reached.
            if end_prog.search(line):
                block_started = False
            # Skip lines if inside a block.
            continue

        if start_prog.search(line):
            block_started = True
            continue

        output_lines.append(line)

    return "\n".join(output_lines)


def main(args):
    content_paths = args.content_path
    for content_path in content_paths:
        with open(content_path, "r", encoding="utf-8") as in_file:
            content = in_file.read()
        content = remove_blocks(content, args.start_regex, args.end_regex)
        with open(content_path, "w", encoding="utf-8") as out_file:
            out_file.write(content)


def add_cli_args(parser):
    parser.add_argument("start_regex", help="regex indicating start of a block")
    parser.add_argument("end_regex", help="regex indicating end of a block")
    parser.add_argument("content_path", help="path file(s) to update", nargs="+")
