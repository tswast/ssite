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

"""cleanhtml removes all styles and class attributes from an HTML file.

I use this to clean up exported HTML files from Google Docs, where I draft blog
posts. I want to keep the HTML in my actual blog as simple as possible.

Note: BeautifulSoup outputs XHTML. You might want to run this output through
something like Pandoc to convert to HTML5.
"""

from __future__ import print_function

import argparse
import codecs

import bs4


def cleanhtml(input_, output=None):
    with codecs.open(input_, 'r', 'utf8') as f:
        html_doc = f.read()
        soup = bs4.BeautifulSoup(html_doc, 'html.parser')

        # Loop until we have cleaned up all tags. We can't do it in a single
        # pass since we are modifying the descendents tree as we go.
        isnotclean = True
        while isnotclean:
            isnotclean = False
            for tag in soup.descendants:
                if not isinstance(tag, bs4.element.Tag):
                    continue
                # Remove any style elements.
                if tag.name == 'style':
                    tag.decompose()
                    isnotclean = True
                    continue
                # Remove any span elements.
                if tag.name == 'span':
                    tag.unwrap()
                    isnotclean = True
                    continue
                # Remove any styles or classes.
                del tag['id']
                del tag['class']
                del tag['style']

        html_clean = soup.prettify()
        if output is None:
            print(html_clean)
            return

        with codecs.open(output, 'w', 'utf8') as f:
            f.write(html_clean)


def add_cli_args(parser):
    parser.add_argument('input', help='path to html document to clean')
    parser.add_argument(
        '-o', '--output', help='path to output cleaned html document')


def main(args):
    cleanhtml(args.input, output=args.output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    add_cli_args(parser)
    args = parser.parse_args()
    main(args)
