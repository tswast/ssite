# Copyright 2019 The Ssite Authors
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

import pytest

import ssite.clean


@pytest.mark.parametrize(
    "before,expected",
    (
        (
            '(\n  <a href="url.html">\n  Hello\n  </a>\n  )\n',
            '(<a href="url.html">Hello</a>)\n',
        ),
        (
            'some\n  <a href="url.html">\n  words\n  </a>\n to keep.\n',
            'some\n<a href="url.html">words</a>\nto keep.\n',
        ),
    )
)
def test_remove_extra_whitespace(before, expected):
    actual = ssite.clean.remove_extra_whitespace(before)
    assert actual == expected
