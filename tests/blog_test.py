# Copyright 2018, The Ssite Authors. All Rights Reserved.
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

import datetime
import os.path

import pytest

import ssite.blog


@pytest.mark.parametrize('prefix,root,content_path,path,expected', [
    (
        'https://example.com/',
        '/my/site/',
        '/my/site/blog/entry/',
        './',
        'https://example.com/blog/entry/',
    ),
    (
        'https://example.com/',
        '/my/site/',
        '/my/site/blog/entry/',
        '../',
        'https://example.com/blog/',
    ),
    (
        'https://example.com/',
        '/my/site/',
        '/my/site/blog/entry/',
        '/blog/entry/',
        'https://example.com/blog/entry/',
    ),
    (
        'https://example.com/',
        '/my/site/',
        '/my/site/blog/entry/',
        'image.png',
        'https://example.com/blog/entry/image.png',
    ),
    (
        'https://example.com/',
        '/my/site/',
        '/my/site/blog/entry/',
        '/blog/entry/image.png',
        'https://example.com/blog/entry/image.png',
    ),
])
def test_calculate_absolute_url(prefix, root, content_path, path, expected):
    got = ssite.blog.calculate_absolute_url(prefix, root, content_path, path)
    assert got == expected
