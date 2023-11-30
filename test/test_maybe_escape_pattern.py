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

from robotstxtparser import RobotsTxtParser


class TestMaybeEscapePattern(unittest.TestCase):
    def setUp(self):
        self.parser = RobotsTxtParser("", self)

    def TestEscape(self, url, expected):
        self.assertEqual(expected, self.parser.maybe_escape_pattern(url))

    def test_maybe_escape_pattern(self):
        self.TestEscape("http://www.example.com", "http://www.example.com")
        self.TestEscape("/a/b/c", "/a/b/c")
        self.TestEscape("á", "%C3%A1")
        self.TestEscape("%aa", "%AA")


if __name__ == "__main__":
    unittest.main()
