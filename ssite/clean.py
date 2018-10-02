#!/usr/bin/env python
# coding: utf-8

# Copyright 2017, The Ssite Authors.
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

"""Remove all styles and class attributes from an HTML file.

Use this to clean up exported HTML from Google Docs to keep the markup as
simple as if it were hand-written.
"""

from __future__ import print_function

import argparse
import re
import textwrap
import urllib.parse

import bs4


def extract_redirect(href):
    url = urllib.parse.urlsplit(href)

    if url.netloc == "www.google.com":
        query = urllib.parse.parse_qs(url.query)
        return query.get("q")

    # Could not find redirect.
    return None


def unredirect_links(a_tag):
    if not a_tag.has_attr("href") or not a_tag["href"]:
        return

    redirect = extract_redirect(a_tag.get_attribute_list("href")[0])
    if redirect:
        a_tag["href"] = redirect


def remove_html_cruft(text):
    soup = bs4.BeautifulSoup(text, "html.parser")

    # Loop until we have cleaned up all tags. We can't do it in a single
    # pass since we are modifying the descendents tree as we go.
    isnotclean = True
    while isnotclean:
        isnotclean = False
        for tag in soup.descendants:
            if isinstance(tag, bs4.element.NavigableString):
                # Wrap text.
                text = tag.string
                wrapped = textwrap.fill(text, width=80)
                if text != wrapped:
                    tag.string.replace_with(wrapped)
                    isnotclean = True
                continue

            # Skip attributes.
            if not isinstance(tag, bs4.element.Tag):
                continue

            # Remove unwanted tags.
            # Remove empty paragraphs.
            if tag.name == "p" and not tag.contents:
                tag.decompose()
                isnotclean = True
                continue
            # Remove any style elements.
            if tag.name == "style":
                tag.decompose()
                isnotclean = True
                continue
            # Remove any span elements.
            if tag.name == "span":
                tag.unwrap()
                isnotclean = True
                continue

            # Clean up desired tags.
            # Clean up links.
            if tag.name == "a":
                unredirect_links(tag)

            # Remove any styles or classes.
            del tag["id"]
            del tag["class"]
            del tag["style"]

    return soup.prettify()


def remove_closing_tags(text):
    text = re.sub(r"<p>\s*", "<p>", text)
    return re.sub(r"\s*</p>", "\n", text)


def cleanhtml(input_, output=None):
    with open(input_, "r", encoding="utf-8") as f:
        html_doc = f.read()

    html_clean = remove_html_cruft(html_doc)
    html_clean = remove_closing_tags(html_clean)

    if output is None:
        print(html_clean)
        return

    with open(output, "w", encoding="utf-8") as f:
        f.write(html_clean)


def add_cli_args(parser):
    parser.add_argument("input", help="path to html document to clean")
    parser.add_argument("-o", "--output", help="path to output cleaned html document")


def main(args):
    cleanhtml(args.input, output=args.output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    add_cli_args(parser)
    args = parser.parse_args()
    main(args)
