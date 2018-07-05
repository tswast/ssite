#!/usr/bin/env python
# coding: utf-8

# Copyright 2013, The Ssite Authors.
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

"""Create an index of time-ordered posts.

A post in the indexed directory is expected to have a path of the form:

    year/month/day/title/index.html

Content in a block with id="content-header" is not included in the preview
text. The title element of the HTML document is used as the the title of the
post.
"""

from __future__ import print_function

import collections
import datetime
import os
import re

import bs4
import jinja2


NON_TEXT_TAGS = frozenset(['script', 'style'])


def is_text_tag(tag):
    if isinstance(tag, bs4.Comment):
        return False
    return tag.parent.name not in NON_TEXT_TAGS


def flatten_dir(initial_path):
    """Return a flattened list of files in ``initial_path`` directory.

    Output paths are relative to ``initial_path``.
    """

    for root, dirs, files in os.walk(initial_path):
        # We can modify "dirs" in-place to skip paths that don't
        # match the expected pattern.
        # http://docs.python.org/2/library/os.html#os.walk
        # Use this to filter out version-control directories.
        dirs_set = set(dirs)
        ignored_dirs = ['.hg', '.git', '.svn']
        for ignored_dir in ignored_dirs:
            if ignored_dir in dirs_set:
                dirs.remove(ignored_dir)

        for file_path in files:
            relative_root = root[len(initial_path) + 1:]
            yield os.path.join(relative_root, file_path)


def blogfiles(filepaths):
    # Avoid premature optimization: match all files in the
    # subdirectory to see if they match.
    pattern = re.compile(r'([0-9]+)/([0-9]+)/([0-9]+)/.*/index.html$')

    for filepath in filepaths:
        # Try to match the pattern to find blog posts.
        match = pattern.match(filepath)
        if match:
            year, month, day = match.groups()
            yield (
                    filepath,
                    datetime.datetime(
                        int(year, base=10),
                        int(month, base=10),
                        int(day, base=10))
            )


Summary = collections.namedtuple(
    'Summary', ['title', 'date', 'path', 'description'])


def summary_from_path(root, path, date):
    filepath = os.path.join(root, path)
    with open(filepath, 'r', encoding='utf-8') as fb:
        return extract_summary(path, date, fb)


def extract_summary(path, date, markup):
    doc = bs4.BeautifulSoup(markup, 'html5lib')
    if doc.title is None:
        print(f'Skipping {path} because missing title')
        return None
    title = doc.title.string
    if doc.body is None:
        print(f'Skipping {path} because has no body')
        return None

    # Destroy the header from the parse tree,
    # since we don't want it in the summary.
    header = doc.body.find(
            attrs={'id': lambda s: s == 'content-header'})
    if header is not None:
        header.decompose()
    description = ' '.join((
        s.string
        for s in
        doc.body.find_all(text=is_text_tag)
        ))[:512]
    return Summary(title, date, f'{os.path.dirname(path)}/', description)


def summaries_from_paths(root, paths):
    for path in paths:
        summary = summary_from_path(root, *path)
        if summary is not None:
            yield summary


def load_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as ft:
        return jinja2.Template(''.join(ft.readlines()))


def main(args):
    indexed_dir = args.indexed_dir
    template_path = args.template
    if template_path is None:
        template_path = os.path.join(indexed_dir, 'index.jinja2.html')
    output_path = args.output
    if output_path is None:
        output_path = os.path.join(indexed_dir, 'index.html')

    t = load_template(template_path)
    blog_paths = blogfiles(flatten_dir(indexed_dir))
    posts = [
        summary
        for summary in summaries_from_paths(indexed_dir, blog_paths)
    ]

    # Sort the posts by date.
    # I reverse it because I want most-recent posts to appear first.
    posts.sort(key=lambda p: p.date, reverse=True)

    # Create the index!
    with open(output_path, 'w', encoding='utf-8') as fo:
        fo.write(t.render(posts=posts))


def add_cli_args(parser):
    parser.add_argument(
        '-o',
        '--output',
        help=(
            'path to write the index. '
            'Default is index.html, relative to the indexed directory.'))
    parser.add_argument(
        '-t',
        '--template',
        help=(
            'path to index template. Default is index.jinja2.html, '
            'relative to the indexed directory.'))
    parser.add_argument(
        'indexed_dir', help='path to root of a directory to be indexed')
