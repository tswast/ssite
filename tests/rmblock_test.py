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

import pytest

from ssite import rmblock


@pytest.mark.parametrize(
    'content,start_block,end_block,expected',
    [
        (
            'No\nblocks\nhere\n',
            '\[START\]$',
            '\[END\]$',
            'No\nblocks\nhere\n',
        ),
        (
            'Some\nblock\n[START]\nwith hidden\ncontent\n[END]\nhere\n',
            '\[START\]$',
            '\[END\]$',
            'Some\nblock\nhere\n',
        ),
        (
            'Block\n [START]\nwith whitespace\ncontent\n [END]\nhere\n',
            '\[START\]$',
            '\[END\]$',
            'Block\nhere\n',
        ),
        (
            'More\n[START]\nhidden\n[END]\nblocks\n[START]\nin\n[END]\nhere\n',
            '\[START\]$',
            '\[END\]$',
            'More\nblocks\nhere\n',
        ),
    ])
def test_remove_blocks(content, start_block, end_block, expected):
    got = rmblock.remove_blocks(content, start_block, end_block)
    assert got == expected
