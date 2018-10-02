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

"""Syndicate content to an RSS file."""

import hashlib
import os
import os.path
import shutil
import subprocess

import bs4
import jinja2
from PIL import Image, ImageSequence

import ssite.blog
import ssite.hentry


def is_animated(im):
    for frame_id, _ in enumerate(ImageSequence.Iterator(im)):
        if frame_id > 0:
            return True
    return False


def resize_static_image(im, resized_path, resize_to, is_pixel_art=True):
    resized_frame = im.resize(
        resize_to,
        # Use Image.NEAREST for sharp pixel art images.
        # Use Image.LANCZOS for high quality photo resizing.
        resample=Image.NEAREST if is_pixel_art else Image.LANCZOS,
    )
    resized_frame.save(resized_path, optimize=True)


def resize_animation(original_path, resized_path, resize_to, is_pixel_art=True):
    """Resize an animated GIF using gifsicle."""
    # I find Pillow's optimization insufficient for large GIFs. Use gifsicle to
    # resize and optimize, instead.
    gifsicle_command = [
        "gifsicle",
        "-O3",
        original_path,
        "-o",
        resized_path,
        "--resize",
        "{}x{}".format(*resize_to),
    ]
    if is_pixel_art:
        gifsicle_command += ["--resize-method", "sample"]
    subprocess.run(gifsicle_command)


def resize_image(original_path, resized_path, resize_width=600, is_pixel_art=True):
    im = Image.open(original_path)
    orig_w, orig_h = im.size
    orig_aspect_ratio = orig_w / orig_h
    resize_height = int(resize_width / orig_aspect_ratio)
    resize_to = (resize_width, resize_height)

    if is_animated(im):
        resize_animation(
            original_path, resized_path, resize_to, is_pixel_art=is_pixel_art
        )
    else:
        resize_static_image(im, resized_path, resize_to, is_pixel_art=is_pixel_art)

    return resize_to


def syndicate_images(soup, syndication_url, output_dir, site_root, content_path):
    """Write syndicated images to ``output_dir``.

    Modifies image source attributes in``soup``.
    """
    for img in soup.find_all("img"):
        img_props = ssite.hentry.photo_template(img)
        local_path = ssite.blog.calculate_filepath(site_root, content_path, img["src"])

        # Image source is already absolute.
        if local_path is None:
            continue

        with open(local_path, "rb") as image_file:
            image_bytes = image_file.read()

        # Create a directory based on the hash of the image to de-duplicate and
        # uniquely identify an image so that resized versions are grouped
        # together.
        image_hash = hashlib.sha256(image_bytes).hexdigest()
        destination_dir = os.path.join(
            output_dir, "images", "sha256-{}".format(image_hash)
        )
        os.makedirs(destination_dir, exist_ok=True)

        extension = os.path.splitext(local_path)[1].lower()
        destination_original = os.path.join(
            destination_dir, "original{}".format(extension)
        )

        if not os.path.exists(destination_original):
            shutil.copy(local_path, destination_original)

        width = None
        height = None

        if (
            # Don't try to resize SVGs or other non-bitmap formats.
            # TODO: what other image formats should we resize?
            extension in (".png", ".gif", ".jpg", ".jpeg")
            # Keep thumbnails at their original resolution.
            and not img_props["is_thumbnail"]
        ):
            destination_resized = os.path.join(
                destination_dir, "resized-600px{}".format(extension)
            )

            if not os.path.exists(destination_resized):
                width, height = resize_image(
                    local_path,
                    destination_resized,
                    is_pixel_art=img_props["is_pixel_art"],
                )
            else:
                # Already resized, grab the image size.
                im = Image.open(destination_resized)
                width, height = im.size

        else:
            # TODO: render SVGs?
            destination_resized = destination_original

        img["src"] = "{}{}".format(
            syndication_url, os.path.relpath(destination_resized, start=output_dir)
        )
        if height:
            img["height"] = str(height)
        if width:
            img["width"] = str(width)


def replace_urls_with_absolute(soup, prefix, root, content_path):
    for link in soup.find_all("a"):
        link["href"] = ssite.blog.calculate_absolute_url(
            prefix, root, content_path, link["href"]
        )

    # TODO: What to do for video embeds?
    for source in soup.find_all("source"):
        source["src"] = ssite.blog.calculate_absolute_url(
            prefix, root, content_path, source["src"]
        )
    for video in soup.find_all("video"):
        video["poster"] = ssite.blog.calculate_absolute_url(
            prefix, root, content_path, video["poster"]
        )


def summary_from_path(
    site_root, index_root, path, path_date, syndication_url, output_dir
):
    filepath = os.path.join(index_root, path)
    with open(filepath, "r", encoding="utf-8") as fb:
        return extract_summary(
            site_root, index_root, filepath, path_date, fb, syndication_url, output_dir
        )


def extract_summary(
    site_root, index_root, path, path_date, markup, syndication_url, output_dir
):
    doc = bs4.BeautifulSoup(markup, "html5lib")
    replace_urls_with_absolute(doc, "/", site_root, path)
    syndicate_images(doc, syndication_url, output_dir, site_root, path)
    relative_path = os.path.relpath(path, start=index_root)
    relative_path = f"{os.path.dirname(relative_path)}/"
    return ssite.hentry.extract_hentry(relative_path, path_date, doc)


def summaries_from_paths(site_root, index_root, paths, syndication_url, output_dir):
    for path, path_date in paths:
        summary = summary_from_path(
            site_root, index_root, path, path_date, syndication_url, output_dir
        )
        if summary is not None:
            yield summary


def main(args):
    indexed_dir = args.indexed_dir
    output_dir = args.output_dir
    site_url = args.site_url
    syndication_url = args.syndication_url
    template_path = args.template
    xml_path = os.path.join(output_dir, "blog.xml")

    # TODO: allow working directories other than site root
    site_root = os.getcwd()

    with open(template_path, "r", encoding="utf-8") as ft:
        jinja_template = jinja2.Template(ft.read())
    blog_paths = ssite.blog.find_paths(indexed_dir)
    entries = [
        entry
        for entry in summaries_from_paths(
            site_root, indexed_dir, blog_paths, syndication_url, output_dir
        )
    ]

    # Sort the entries by date.
    # I reverse it because I want most-recent posts to appear first.
    entries.sort(key=lambda entry: entry.published, reverse=True)

    with open(xml_path, "wt", encoding="utf-8") as xml_file:
        new_content = jinja_template.render(entries=entries) + "\n"
        xml_file.write(new_content)


def add_cli_args(parser):
    parser.add_argument(
        "--output_dir",
        help="path to write blog.xml and syndicated images to. ",
        default="syndicate/",
    )
    parser.add_argument(
        "--site_url",
        help="URL of site (must end in /)",
        default="https://www.timswast.com/",
    )
    parser.add_argument(
        "--syndication_url",
        help="URL of syndication site (must end in /)",
        default="http://syndicate.timswast.com/",
    )
    parser.add_argument(
        "-t",
        "--template",
        help="path to index blog.xml template.",
        default="syndicate/blog.jinja2.xml",
    )
    parser.add_argument("indexed_dir", help="path to root of a directory to be indexed")
