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

from ssite import blogindex


def test_flatten_dir():
    test_dir = os.path.dirname(os.path.abspath(__file__))
    filepaths = tuple(sorted(blogindex.flatten_dir(
        os.path.join(test_dir, 'data', 'testblog'))))
    assert filepaths == (
        '2012/01/01/index.html',
        '2012/01/01/other.html',
        '2012/04/30/index.html',
        '2012/index.html',
        '2013/12/31/index.html',
    )


def test_extract_summary_missing_title_returns_none():
    assert blogindex.extract_summary(
            "some/path",
            datetime.datetime(2016, 5, 5),
            "<!DOCTYPE html>Hello") is None


def test_extract_summary_returns_summary():
    assert blogindex.extract_summary(
            "some/path/index.html",
            datetime.datetime(2016, 5, 5),
            "<!DOCTYPE html><title>Hello</title>Some beginning text."
            ) == blogindex.Summary(
                    "Hello",
                    datetime.datetime(2016, 5, 5),
                    u"some/path/",
                    "Some beginning text.")
