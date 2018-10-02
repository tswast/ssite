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
import os.path
import re

import bs4
import jinja2

import ssite.blog
import ssite.hentry


def replace_urls_with_absolute(soup, prefix, root, content_path):
    for link in soup.find_all("a"):
        link["href"] = ssite.blog.calculate_absolute_url(
            prefix, root, content_path, link["href"]
        )

    for img in soup.find_all("img"):
        img["src"] = ssite.blog.calculate_absolute_url(
            prefix, root, content_path, img["src"]
        )

    # Video embeds.
    for source in soup.find_all("source"):
        source["src"] = ssite.blog.calculate_absolute_url(
            prefix, root, content_path, source["src"]
        )
    for video in soup.find_all("video"):
        video["poster"] = ssite.blog.calculate_absolute_url(
            prefix, root, content_path, video["poster"]
        )
    return str(soup)


def summary_from_path(site_root, index_root, path, path_date):
    filepath = os.path.join(index_root, path)
    with open(filepath, "r", encoding="utf-8") as fb:
        return extract_summary(site_root, index_root, filepath, path_date, fb)


def extract_summary(site_root, index_root, path, path_date, markup):
    doc = bs4.BeautifulSoup(markup, "html5lib")
    replace_urls_with_absolute(doc, "/", site_root, path)
    relative_path = os.path.relpath(path, start=index_root)
    relative_path = f"{os.path.dirname(relative_path)}/"
    return ssite.hentry.extract_hentry(relative_path, path_date, doc)


def summaries_from_paths(site_root, index_root, paths):
    for path, path_date in paths:
        summary = summary_from_path(site_root, index_root, path, path_date)
        if summary is not None:
            yield summary


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
    start_line = f"<!--START {region_name}-->"
    end_line = f"<!--END {region_name}-->"
    start_lines = []
    region_lines = []
    end_lines = []
    found_start = False
    found_end = False

    for line_no, line in enumerate(contents.split("\n")):
        line_stripped = line.strip()

        # Detect found_end first, so that the end line is added to end_lines.
        if line_stripped == end_line:
            if found_end:
                raise ValueError(
                    f'Found duplicate end line "{end_line}" at line ' f"{line_no + 1}."
                )
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
                    f"{line_no + 1}."
                )
            found_start = True

    # Couldn't find the region, so raise an error.
    if not found_start:
        raise ValueError(f'Could not find start line "{start_line}".')
    if not found_end:
        raise ValueError(f'Could not find end line "{end_line}".')

    start_block = "\n".join(start_lines) + "\n"

    # If there are no lines in the region block, use the empty string.
    region_block = ("\n".join(region_lines) + "\n") if region_lines else ""

    # No need to append '\n' at the end for end_block. If the original content
    # ends in a newline, end_lines ends with an empty line.
    end_block = "\n".join(end_lines)
    return start_block, region_block, end_block


def replace_region(contents, region_name, body):
    split_content = split_region(contents, region_name)
    return f"{split_content[0]}{body}{split_content[2]}"


def main(args):
    indexed_dir = args.indexed_dir
    index_path = args.index
    if index_path is None:
        index_path = os.path.join(indexed_dir, "index.html")

    template_path = args.template
    if template_path is None:
        template_path = "{}.jinja2".format(index_path)

    # TODO: allow working directories other than site root
    site_root = os.getcwd()

    blog_paths = ssite.blog.find_paths(indexed_dir)
    entries = [
        entry for entry in summaries_from_paths(site_root, indexed_dir, blog_paths)
    ]

    # Sort the entries by date.
    # I reverse it because I want most-recent posts to appear first.
    entries.sort(key=lambda entry: entry.published, reverse=True)

    with open(template_path, "r", encoding="utf-8") as ft:
        jinja_template = jinja2.Template(ft.read())

    # Update the index file by replacing the <!--START/END INDEX--> region.
    with open(index_path, "r+", encoding="utf-8") as index_file:
        original_content = index_file.read()
        new_index = jinja_template.render(entries=entries) + "\n"
        new_content = replace_region(original_content, "INDEX", new_index)
        index_file.seek(0)
        index_file.truncate(0)  # Delete existing contents.
        index_file.write(new_content)


def add_cli_args(parser):
    parser.add_argument(
        "--index",
        help=(
            "path to the index file to be updated. "
            "Default is index.html, relative to the indexed directory."
        ),
    )
    parser.add_argument(
        "-t",
        "--template",
        help=(
            "path to index body template. Default is index.jinja2.html, "
            "relative to the indexed directory."
        ),
    )
    parser.add_argument("indexed_dir", help="path to root of a directory to be indexed")
