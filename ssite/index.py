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
import itertools
import os
import os.path
import re

import bs4
import dateutil.parser
import jinja2


NON_TEXT_TAGS = frozenset(['script', 'style'])


def calculate_absolute_url(prefix, root, content_path, target_path):
    # Already absolute?
    if '://' in target_path:
        return target_path

    # Already site-relative?
    if target_path.startswith('/'):
        return f'{prefix}{target_path[1:]}'

    fs_target_path = os.path.join(os.path.dirname(content_path), target_path)
    relative_path = os.path.relpath(fs_target_path, start=root)
    if target_path.endswith('/'):
        relative_path += '/'
    return f'{prefix}{relative_path}'


def replace_urls_with_absolute(soup, prefix, root, content_path):
    for link in soup.find_all('a'):
        link['href'] = calculate_absolute_url(
            prefix, root, content_path, link['href'])

    for img in soup.find_all('img'):
        img['src'] = calculate_absolute_url(
            prefix, root, content_path, img['src'])
    return str(soup)


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
    # Match all files in the subdirectory to see if they match the pattern for
    # blog posts.
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


HEntry = collections.namedtuple(
    'HEntry', ['name', 'published', 'path', 'content', 'summary', 'photos'])


def summary_from_path(site_root, index_root, path, date):
    filepath = os.path.join(index_root, path)
    with open(filepath, 'r', encoding='utf-8') as fb:
        return extract_summary(site_root, index_root, filepath, date, fb)


def extract_summary(site_root, index_root, path, date, markup):
    doc = bs4.BeautifulSoup(markup, 'html5lib')
    replace_urls_with_absolute(doc, '/', site_root, path)

    # Find the first h-entry.
    # Getting just the first h-entry skips any inline replies.
    entry = doc.find(class_='h-entry')
    if not entry:
        print(f'Skipping {path} because missing h-entry')
        return None

    title_elem = entry.find(class_='p-name')
    if not title_elem:
        print(f'Skipping {path} because missing title')
        return None

    title = None
    if (
        'e-content' not in title_elem['class']
        and 'p-content' not in title_elem['class']
    ):
        title = title_elem.string

    # It there is a published element, parse the datetime from that, otherwise,
    # use the datetime from the filepath.
    published_elem = entry.find(class_='dt-published')
    published = None
    if published_elem:
        if published_elem.has_attr('datetime'):
            published = dateutil.parser.parse(published_elem['datetime'])
        else:
            published = dateutil.parser.parse(published_elem.string)

    if published and published.date() != date.date():
        print(f'Warning: {path} path date doesn\'t match {published}.')
    date = published or date

    content = None
    content_elem = entry.find(class_='e-content')
    if content_elem:
        content = ''.join(map(str, content_elem.children))
    else:
        content_elem = entry.find(class_='p-content')
        if content_elem:
            content = content_elem.string

    if content is None:
        print(f'Skipping {path} because has no e-content or p-content')
        return None

    summary = None
    summary_elem = (
        entry.find(class_='e-summary') or entry.find(class_='p-summary')
    )
    if summary_elem:
        summary = ''.join(map(str, summary_elem.children))

    photo_elems_root = entry.find_all(
        class_='u-photo',
        # Find only direct children so as not to pick up photos from the
        # h-card.
        recursive=False)
    photo_elems_content = content_elem.find_all(class_='u-photo')
    photos = []
    for photo_elem in itertools.chain(photo_elems_root, photo_elems_content):
        photos.append({
            'id': photo_elem.attrs.get('id'),
            'src': photo_elem['src'],
            'alt': photo_elem.attrs.get('alt', ''),
            'is_pixel_art': 'u-pixel-art' in photo_elem['class'],
        })

    relative_path = os.path.relpath(path, start=index_root)
    return HEntry(
        title, date, f'{os.path.dirname(relative_path)}/', content,
        summary=summary, photos=photos)


def summaries_from_paths(site_root, index_root, paths):
    for path in paths:
        summary = summary_from_path(site_root, index_root, *path)
        if summary is not None:
            yield summary


def load_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as ft:
        return jinja2.Template(''.join(ft.readlines()))


def split_region(contents, region_name):
    """Split `contents` by region with `region_name`.

    Returns:
        Tuple[str, str, str]:
            A tuple containing the start block, region block, and end block.
            Start block contains the start region line. End block contains
            the end region line.

    Raises:
        ValueError:
            If could not find region with `region_name` or found duplicate
            region definitions of `region_name`.
    """
    start_line = f'<!--START {region_name}-->'
    end_line = f'<!--END {region_name}-->'
    start_lines = []
    region_lines = []
    end_lines = []
    found_start = False
    found_end = False

    for line_no, line in enumerate(contents.split('\n')):
        line_stripped = line.strip()

        # Detect found_end first, so that the end line is added to end_lines.
        if line_stripped == end_line:
            if found_end:
                raise ValueError(
                    f'Found duplicate end line "{end_line}" at line '
                    f'{line_no + 1}.')
            found_end = True

        if not found_start:
            start_lines.append(line)
        elif not found_end:
            region_lines.append(line)
        else:
            end_lines.append(line)

        # Detect found_start last, so that the start line is added to
        # start_lines.
        if line_stripped == start_line:
            if found_start:
                raise ValueError(
                    f'Found duplicate start line "{start_line}" at line '
                    f'{line_no + 1}.')
            found_start = True

    # Couldn't find the region, so raise an error.
    if not found_start:
        raise ValueError(f'Could not find start line "{start_line}".')
    if not found_end:
        raise ValueError(f'Could not find end line "{end_line}".')

    start_block = '\n'.join(start_lines) + '\n'

    # If there are no lines in the region block, use the empty string.
    region_block = ('\n'.join(region_lines) + '\n') if region_lines else ''

    # No need to append '\n' at the end for end_block. If the original content
    # ends in a newline, end_lines ends with an empty line.
    end_block = '\n'.join(end_lines)
    return start_block, region_block, end_block


def replace_region(contents, region_name, body):
    split_content = split_region(contents, region_name)
    return f'{split_content[0]}{body}{split_content[2]}'


def main(args):
    indexed_dir = args.indexed_dir
    index_path = args.index
    if index_path is None:
        index_path = os.path.join(indexed_dir, 'index.html')

    template_path = args.template
    if template_path is None:
        template_path = '{}.jinja2'.format(index_path)

    jinja_template = load_template(template_path)
    blog_paths = blogfiles(flatten_dir(indexed_dir))
    entries = [
        entry
        for entry in summaries_from_paths(
            os.getcwd(), indexed_dir, blog_paths)
    ]

    # Sort the entries by date.
    # I reverse it because I want most-recent posts to appear first.
    entries.sort(key=lambda entry: entry.published, reverse=True)

    # Update the index file by replacing the <!--START/END INDEX--> region.
    with open(index_path, 'r+', encoding='utf-8') as index_file:
        original_content = index_file.read()
        new_index = jinja_template.render(entries=entries) + '\n'
        new_content = replace_region(original_content, 'INDEX', new_index)
        index_file.seek(0)
        index_file.truncate(0)  # Delete existing contents.
        index_file.write(new_content)


def add_cli_args(parser):
    parser.add_argument(
        '--index',
        help=(
            'path to the index file to be updated. '
            'Default is index.html, relative to the indexed directory.'))
    parser.add_argument(
        '-t',
        '--template',
        help=(
            'path to index body template. Default is index.jinja2.html, '
            'relative to the indexed directory.'))
    parser.add_argument(
        'indexed_dir', help='path to root of a directory to be indexed')
