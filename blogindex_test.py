#!/usr/bin/env python
# coding: utf-8

# Copyright 2016, The Locoloco Authors. All Rights Reserved.
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

from blogindex import extract_summary, Summary

def test_extract_summary_missing_title_returns_none():
    assert extract_summary(
            "some/path",
            datetime.datetime(2016, 5, 5),
            "<!DOCTYPE html>Hello") is None


def test_extract_summary_returns_summary():
    assert extract_summary(
            "some/path/index.html",
            datetime.datetime(2016, 5, 5),
            "<!DOCTYPE html><title>Hello</title>Some beginning text."
            ) == Summary(
                    "Hello",
                    datetime.datetime(2016, 5, 5),
                    u"some/path/",
                    "Some beginning text.")
