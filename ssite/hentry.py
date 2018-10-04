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

"""Create an h-entry dictionary for a post.

Note: this module does not parse all microformats. It also does not use the
canonical parsing format. Instead, it extracts only what is needed to render
indexes for www.timswast.com.
"""

import collections
import logging

import dateutil.parser
import pytz


logger = logging.getLogger(__name__)

HEntry = collections.namedtuple(
    "HEntry", ["name", "published", "path", "content", "summary", "photos"]
)


def photo_template(photo_elem, is_in_content=False):
    classes = photo_elem.attrs.get("class", [])
    is_pixel_art = "u-pixel-art" in classes or "pixel-art" in classes
    is_thumbnail = "thumbnail" in classes
    return {
        "id": photo_elem.attrs.get("id"),
        "src": photo_elem["src"],
        "alt": photo_elem.attrs.get("alt", ""),
        "is_pixel_art": is_pixel_art,
        "is_thumbnail": is_thumbnail,
        "is_in_content": is_in_content,
        "width": photo_elem.attrs.get("width"),
        "height": photo_elem.attrs.get("height"),
    }


def extract_hentry(path, path_date, doc, default_timezone="America/Los_Angeles"):
    # Find the first h-entry.
    # Getting just the first h-entry skips any inline replies.
    entry = doc.find(class_="h-entry")
    if not entry:
        logger.warn(f"Skipping {path} because missing h-entry")
        return None

    title_elem = entry.find(class_="p-name")
    if not title_elem:
        logger.warn(f"Skipping {path} because missing title")
        return None

    title = None
    if (
        "e-content" not in title_elem["class"]
        and "p-content" not in title_elem["class"]
    ):
        title = title_elem.string

    # It there is a published element, parse the datetime from that, otherwise,
    # use the datetime from the filepath.
    published_elem = entry.find(class_="dt-published")
    published = None
    if published_elem:
        if published_elem.has_attr("datetime"):
            published = dateutil.parser.parse(published_elem["datetime"])
        else:
            published = dateutil.parser.parse(published_elem.string)

    if published and published.date() != path_date.date():
        logger.warn(f"Date in {path} doesn't match dt-published {published}")

    if published and not published.tzinfo:
        tz = pytz.timezone(default_timezone)
        published = tz.localize(published)
    date = published or path_date

    content = None
    content_elem = entry.find(class_="e-content")
    if content_elem:
        content = "".join(map(str, content_elem.children))
    else:
        content_elem = entry.find(class_="p-content")
        if content_elem:
            content = content_elem.string

    if content is None:
        logger.warn(f"Skipping {path} because has no e-content or p-content")
        return None

    summary = None
    summary_elem = entry.find(class_="e-summary") or entry.find(class_="p-summary")
    if summary_elem:
        summary = "".join(map(str, summary_elem.children))

    photo_elems_root = entry.find_all(
        class_="u-photo",
        # Find only direct children so as not to pick up photos from the
        # h-card.
        recursive=False,
    )
    photo_elems_content = content_elem.find_all(class_="u-photo")
    photos = []
    for photo_elem in photo_elems_root:
        photos.append(photo_template(photo_elem, is_in_content=False))
    for photo_elem in photo_elems_content:
        photos.append(photo_template(photo_elem, is_in_content=True))

    return HEntry(title, date, path, content, summary=summary, photos=tuple(photos))
