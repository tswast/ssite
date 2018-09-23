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

"""Utilities for finding blog entries."""

import collections
import datetime
import os
import os.path
import re


BlogPath = collections.namedtuple("BlogPath", ["path", "published"])


def calculate_filepath(site_root_path, content_path, target_path):
    # Already absolute?
    if "://" in target_path:
        return None

    # Site-relative?
    if target_path.startswith("/"):
        return os.path.join(site_root_path, target_path[1:])

    # Content-relative?
    return os.path.join(os.path.dirname(content_path), target_path)


def calculate_absolute_url(prefix, site_root_path, content_path, target_path):
    # Already absolute?
    if "://" in target_path:
        return target_path

    # Already site-relative?
    if target_path.startswith("/"):
        return f"{prefix}{target_path[1:]}"

    fs_target_path = os.path.join(os.path.dirname(content_path), target_path)
    relative_path = os.path.relpath(fs_target_path, start=site_root_path)
    if target_path.endswith("/"):
        relative_path += "/"
    return f"{prefix}{relative_path}"


def find_paths(indexed_dir):
    """Find all the blog entry paths in a directory.

    Returns:
        Iterable[BlogPath]: An iterable of blog paths.
    """
    return blogfiles(flatten_dir(indexed_dir))


def flatten_dir(initial_path):
    """Return a flattened list of files in ``initial_path`` directory.

    Output paths are relative to ``initial_path``.
    """

    for root, dirs, files in os.walk(initial_path):
        # We can modify "dirs" in-place to skip paths that don't
        # match the expected pattern.
        # http://docs.python.org/3/library/os.html#os.walk
        # Use this to filter out version-control directories.
        dirs_set = set(dirs)
        ignored_dirs = [".bzr", ".dat", ".hg", ".git", ".svn"]
        for ignored_dir in ignored_dirs:
            if ignored_dir in dirs_set:
                dirs.remove(ignored_dir)

        for file_path in files:
            relative_root = root[len(initial_path) + 1 :]
            yield os.path.join(relative_root, file_path)


def blogfiles(filepaths):
    # Match all files in the subdirectory to see if they match the pattern for
    # blog posts.
    pattern = re.compile(r"([0-9]+)/([0-9]+)/([0-9]+)/.*/index.html$")

    for filepath in filepaths:
        # Try to match the pattern to find blog posts.
        match = pattern.match(filepath)
        if match:
            year, month, day = match.groups()
            yield BlogPath(
                filepath,
                datetime.datetime(
                    int(year, base=10), int(month, base=10), int(day, base=10)
                ),
            )
