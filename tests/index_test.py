#!/usr/bin/env python
# coding: utf-8

# Copyright 2016, The Ssite Authors. All Rights Reserved.
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

import ssite.index


def test_flatten_dir():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    filepaths = tuple(
        sorted(ssite.index.flatten_dir(os.path.join(test_dir, "data", "testblog")))
    )
    assert filepaths == (
        "2012/01/01/index.html",
        "2012/01/01/other.html",
        "2012/04/30/index.html",
        "2012/index.html",
        "2013/12/31/index.html",
    )


def test_extract_summary_missing_title_returns_none():
    assert (
        ssite.index.extract_summary(
            "some/path", datetime.datetime(2016, 5, 5), "<!DOCTYPE html>Hello"
        )
        is None
    )


def test_extract_summary_returns_summary():
    assert ssite.index.extract_summary(
        "some/path/index.html",
        datetime.datetime(2016, 5, 5),
        (
            '<!DOCTYPE html><article class="h-entry">'
            '<span class="p-name">Hello</span>'
            '<div class="p-content">Some beginning text.</div>'
        ),
    ) == ssite.index.HEntry(
        "Hello", datetime.datetime(2016, 5, 5), "some/path/", "Some beginning text."
    )


@pytest.mark.parametrize(
    "content,region_name,expected",
    [
        (
            """<!--START empty_block-->
<!--END empty_block-->
""",
            "empty_block",
            ("<!--START empty_block-->\n", "", "<!--END empty_block-->\n"),
        ),
        (
            """<!--START ALLCAPS-->
<!--END ALLCAPS-->
""",
            "ALLCAPS",
            ("<!--START ALLCAPS-->\n", "", "<!--END ALLCAPS-->\n"),
        ),
        (
            """<!--START ws_block-->

<!--END ws_block-->
""",
            "ws_block",
            ("<!--START ws_block-->\n", "\n", "<!--END ws_block-->\n"),
        ),
        (
            """Lines
at the start.

<!--START search-->
 Some more lines
 live inside this block.
<!--END search-->

And lines at the end.
""",
            "search",
            (
                "Lines\nat the start.\n\n<!--START search-->\n",
                " Some more lines\n live inside this block.\n",
                "<!--END search-->\n\nAnd lines at the end.\n",
            ),
        ),
    ],
)
def test_split_region(content, region_name, expected):
    assert ssite.index.split_region(content, region_name) == expected


@pytest.mark.parametrize(
    "content,region_name,expected_error_message",
    [
        (
            """<!--START dup_start-->
<!--START dup_start-->
<!--END dup_start-->
""",
            "dup_start",
            'Found duplicate start line "<!--START dup_start-->" at line 2.',
        ),
        (
            """<!--START dup_end-->
<!--END dup_end-->
<!--END dup_end-->
""",
            "dup_end",
            'Found duplicate end line "<!--END dup_end-->" at line 3.',
        ),
        (
            """<!--START wrong_tag-->
<!--END wrong_tag-->
""",
            "other_tag",
            'Could not find start line "<!--START other_tag-->".',
        ),
        (
            """<!--START missing_end-->
<!--END not_the_correct_end-->
""",
            "missing_end",
            'Could not find end line "<!--END missing_end-->".',
        ),
    ],
)
def test_split_region_errors(content, region_name, expected_error_message):
    with pytest.raises(ValueError) as excinfo:
        ssite.index.split_region(content, region_name)
    assert expected_error_message in str(excinfo.value)
