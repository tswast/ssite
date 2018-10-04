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

"""Create a new note-type post."""

import datetime
import logging
import os
import os.path
import re
import shutil

import bs4
import dateutil.parser
import jinja2
import pytz


logger = logging.getLogger(__name__)


def render_note(template, note, published, pixelart_filename=None):
    soup = bs4.BeautifulSoup(note, "html5lib")
    return template.render(
        note=note,
        note_text=soup.text,
        published=published,
        pixelarts=[pixelart_filename] if pixelart_filename else [],
    )


def add_note(template_path, note, published, pixelart_path=None, blog_dir="."):
    destination_dir = os.path.join(
        blog_dir,
        published.strftime("%Y"),
        published.strftime("%m"),
        published.strftime("%d"),
        # Assume that notes aren't added more than once per second to use the
        # existence of the destination directory as a way to make adding a note
        # idempotent.
        "note-{}".format(published.strftime("%H%M%S")),
    )
    try:
        os.makedirs(destination_dir)
    except FileExistsError as exc:
        logger.warning(
            "Not adding note. " "Destination directory already exists: {}".format(exc)
        )
        return

    try:
        pixelart_filename = None
        if pixelart_path:
            pixelart_filename = os.path.basename(pixelart_path)
            shutil.copy(pixelart_path, os.path.join(destination_dir, pixelart_filename))

        with open(template_path, "r", encoding="utf-8") as ft:
            note_template = jinja2.Template(ft.read())

        note_path = os.path.join(destination_dir, "index.html")
        content = render_note(
            note_template, note, published, pixelart_filename=pixelart_filename
        )
        with open(note_path, "w", encoding="utf-8") as out_file:
            out_file.write(content)
    except Exception:
        # We failed to add the note, so remove the directory so that we can try
        # again.
        shutil.rmtree(destination_dir)
        raise


def main(args):
    if args.published_date:
        published = dateutil.parser.parse(args.published_date)
    else:
        published = datetime.datetime.now()
        # No need for microsecond-level precision.
        published = published.replace(microsecond=0)

    # Use specified timezone if no timezone is specified.
    if not published.tzinfo:
        tz = pytz.timezone(args.published_timezone)
        published = tz.localize(published)

    add_note(
        args.template_path,
        args.note,
        published,
        pixelart_path=args.pixelart,
        blog_dir=args.blog_dir,
    )


def add_cli_args(parser):
    parser.add_argument("--blog_dir", help="Path to blog directory.", default=".")
    parser.add_argument("--pixelart", help="Path to pixel art image for note.")
    parser.add_argument(
        "--published_date",
        help=(
            "Date-time that the note was published. Notes are assumed to be "
            "published at most once per second."
        ),
    )
    parser.add_argument(
        "--published_timezone",
        help="What timezone to use when interpreting the --published_date argument?",
        default="America/Los_Angeles",
    )
    parser.add_argument("template_path", help="Path to note template (jinja2).")
    parser.add_argument("note", help="Text or HTML content for note post.")
