# Copyright 2023 cocon.se (http://cocon.se/)
# Copyright 1999 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This file tests the robots.txt parsing and matching code found in robots.cc
# against the current Robots Exclusion Protocol (REP) internet draft (I-D).
# https://www.rfc-editor.org/rfc/rfc9309.html
# https://tools.ietf.org/html/draft-koster-rep
#
#
# Converted 2023-11-17, from https://github.com/google/robotstxt/blob/master/robots.cc

import unittest

from pyrobotstxt.robots_cc import get_path_params_query


class TestGetPathParamsQuery(unittest.TestCase):
    def TestPath(self, url, expected_path):
        self.assertEqual(expected_path, get_path_params_query(url))

    def test_get_path_params_query(self):
        # Only testing URLs that are already correctly escaped here.
        self.TestPath("", "/")
        self.TestPath("http://www.example.com", "/")
        self.TestPath("http://www.example.com/", "/")
        self.TestPath("http://www.example.com/a", "/a")
        self.TestPath("http://www.example.com/a/", "/a/")
        self.TestPath("http://www.example.com/a/b?c=http://d.e/", "/a/b?c=http://d.e/")
        self.TestPath("http://www.example.com/a/b?c=d&e=f#fragment", "/a/b?c=d&e=f")
        self.TestPath("example.com", "/")
        self.TestPath("example.com/", "/")
        self.TestPath("example.com/a", "/a")
        self.TestPath("example.com/a/", "/a/")
        self.TestPath("example.com/a/b?c=d&e=f#fragment", "/a/b?c=d&e=f")
        self.TestPath("a", "/")
        self.TestPath("a/", "/")
        self.TestPath("/a", "/a")
        self.TestPath("a/b", "/b")
        self.TestPath("example.com?a", "/?a")
        self.TestPath("example.com/a;b#c", "/a;b")
        self.TestPath("//a/b/c", "/b/c")

if __name__ == "__main__":
    unittest.main()
