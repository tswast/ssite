#!/usr/bin/env python
# coding: utf-8
"""blogindex.py : Create an index for a plain-HTML blog.

By plain-HTML, I mean that each entry is a stand-alone document. It is
not a full static blog generator like Octopress/Jekyll or Hyde.

blogindex.py assumes certain conventions are used. Firstly, it assumes
articles have a path of the form:

    year/month/day/title/index.html

It knows that content in a block with id="content-header" should not be
included in the preview text. Finally, it assumes the title element of
the HTML document is actually the title of the article.

Maybe I should call this locoloco.py : The Little Engine that Doesn't?
"""

import codecs
import collections
import datetime
import os
import re
import sys

from bs4 import BeautifulSoup
from jinja2 import Template


def blogfiles(initial_path):
    # Avoid premature optimization: match all files in the
    # subdirectory to see if they match.
    pattern = re.compile(r"([0-9]+)/([0-9]+)/([0-9]+)/.*/index.html$")

    for root, dirs, files in os.walk(initial_path):
        # We can modify "dirs" in-place to skip paths that don't
        # match the expected pattern.
        # http://docs.python.org/2/library/os.html#os.walk
        # Use this to filter out version-control directories.
        dirs_set = set(dirs)
        ignored_dirs = [".hg", ".git", ".svn"]
        for ignored_dir in ignored_dirs:
            if ignored_dir in dirs_set:
                dirs.remove(ignored_dir)

        for file in files:
            # We try to match the pattern, skipping the initial,
            # configurable, search directory.
            current_path = os.path.join(root, file)[len(initial_path)+1:]
            match = pattern.match(current_path)
            if match:
                year, month, day = match.groups()
                yield (
                        current_path,
                        datetime.datetime(
                            int(year, base=10),
                            int(month, base=10),
                            int(day, base=10)
                ))


Summary = collections.namedtuple("Summary", ["title", "date", "path", "description"])
def summary_from_path(path, date):
    with codecs.open(path, "rb", "utf8") as f:
        doc = BeautifulSoup(f, "html5lib")
        title = doc.title.string

        # Destroy the header from the parse tree,
        # since we don't want it in the summary.
        header = doc.body.find(
                attrs={"id": lambda s: s == "content-header"})
        if header != None:
            header.decompose()
        description = u" ".join((
            s.string
            for s in
            doc.body.find_all(
                text=True)
            ))[:512]
    return Summary(
            title, date, unicode("{0}/".format(os.path.dirname(path)), "utf8"),
            description)





def summaries_from_paths(paths):
    for path in paths:
        yield summary_from_path(*path)


def load_template(path):
    template_path = os.path.join(path, "index.jinja2.html")
    with codecs.open(template_path, "rb", "utf8") as f:
        return Template(u"".join(f.readlines()))


def main(path):
    import pprint
    t = load_template(path)
    posts = [s for s in summaries_from_paths(blogfiles(path))]

    # Sort the posts by date.
    # I reverse it because I want most-recent posts to appear first.
    posts.sort(key=lambda p: p.date, reverse=True)

    # Create the index!
    with codecs.open(os.path.join(path, "index.html"), "wb", "utf8") as f:
        f.write(t.render(posts=posts))

if __name__ == "__main__":
    main(sys.argv[1])


