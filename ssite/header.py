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

"""Replace the header (before title tag) in HTML files. (Beta)"""

import os.path
import re

import bs4
import jinja2


def calculate_absolute_url(prefix, root, content_path, target_path):
    # TODO: consolidate with copy in blog.py
    #       Or maybe not? We don't want to mess with logic for existing URLs.
    fs_target_path = os.path.join(os.path.dirname(content_path), target_path)
    relative_path = os.path.relpath(fs_target_path, start=root)
    if target_path.endswith("/"):
        relative_path += "/"
    return f"{prefix}{relative_path}"


def is_canonical_link(tag):
    return tag.name == "link" and tag.has_attr("rel") and "canonical" in tag["rel"]


def replace_header(content_path, site, site_root, header_template):
    with open(content_path, "r", encoding="utf-8") as in_file:
        content = in_file.read()
    header_lines = []
    output_lines = []
    end_prog = re.compile("<title>")
    header_ended = False

    for line in content.split("\n"):
        if end_prog.match(line):
            header_ended = True
        if header_ended:
            output_lines.append(line)
        else:
            header_lines.append(line)

    previous_header = "\n".join(header_lines)

    canonical_link = None
    soup = bs4.BeautifulSoup(previous_header, "html5lib")
    canonical_links = soup.find_all(is_canonical_link)
    if canonical_links:
        # Use the existing canonical link if present
        canonical_link = canonical_links[0]["href"]
    else:
        # Otherwise, calculate a link to the content itself.
        canonical_path = content_path
        filename = os.path.basename(content_path)
        if filename in ("index.html", "index.htm"):
            # Link to directories instead of index.html files for prettier URLs.
            canonical_path = os.path.abspath(os.path.dirname(content_path))
            # Add trailing slash if not present.
            # https://stackoverflow.com/a/15010678/101923
            canonical_path = os.path.join(canonical_path, "")
        canonical_link = calculate_absolute_url(
            site, site_root, site_root, canonical_path
        )

    new_header = header_template.render(rel_canonical=canonical_link)
    return "\n".join([new_header] + output_lines)


def main(args):
    with open(args.template_path, "r", encoding="utf-8") as ft:
        header_template = jinja2.Template(ft.read())
    content_paths = args.content_path
    for content_path in content_paths:
        content = replace_header(
            os.path.abspath(content_path),
            args.site,
            os.path.abspath(args.site_root),
            header_template,
        )
        with open(content_path, "w", encoding="utf-8") as out_file:
            out_file.write(content)


def add_cli_args(parser):
    parser.add_argument("site", help="base URL of site")
    parser.add_argument("site_root", help="path to site root directory")
    parser.add_argument("template_path", help="path to header template (jinja2)")
    parser.add_argument("content_path", help="path file(s) to update", nargs="+")
