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

import setuptools


description = (
    "Ssite is not a static site generator. "
    "It is a collection of scripts to maintain a static site."
)
version = "0.4.0"


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ssite",
    version=version,
    author="Tim Swast",
    author_email="swast@google.com",
    description=description,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tswast/ssite",
    install_requires=[
        "beautifulsoup4>=4.4.1,<5.0dev",
        "html5lib>=0.9999999,<2.0dev",
        "Jinja2>=2.8,<3.0dev",
        "setuptools>=28.0.0",
        "python-dateutil>=2.0.0,<3.0dev",
        "pytz",
    ],
    entry_points={"console_scripts": ["ssite=ssite.cli:main"]},
    packages=setuptools.find_packages(),
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Internet",
    ),
)
