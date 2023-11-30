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

from robots_cc import RobotsMatcher
from robotstxtparser import RobotsTxtParser


class RobotsStatsReporter(RobotsMatcher):
    def __init__(self):
        self._last_line_seen = 0
        self._valid_directives = 0
        self._unknown_directives = 0
        self._sitemap = ""

    def handle_robots_start(self):
        self._last_line_seen = 0
        self._valid_directives = 0
        self._unknown_directives = 0
        self._sitemap = ""

    def handle_robots_end(self):
        pass

    def handle_user_agent(self, line_num, value):
        self.digest(line_num)

    def handle_allow(self, line_num, value):
        self.digest(line_num)

    def handle_disallow(self, line_num, value):
        self.digest(line_num)

    def handle_sitemap(self, line_num, value):
        self.digest(line_num)
        self._sitemap += value

    def handle_unknown_action(self, line_num, action, value):
        self._last_line_seen = line_num
        self._unknown_directives += 1

    def digest(self, line_num):
        assert line_num >= self._last_line_seen
        self._last_line_seen = line_num
        self._valid_directives += 1

    @property
    def last_line_seen(self):
        return self._last_line_seen

    @property
    def valid_directives(self):
        return self._valid_directives

    @property
    def unknown_directives(self):
        return self._unknown_directives

    @property
    def sitemap(self):
        return self._sitemap


class TestRobotsStatsReporter(unittest.TestCase):
    def setUp(self):
        self.report = RobotsStatsReporter()

    # Different kinds of line endings are all supported: %x0D / %x0A / %x0D.0A
    def test_ID_LinesNumbersAreCountedCorrectly(self):
        unix_file = (
            "User-Agent: foo\n"
            "Allow: /some/path\n"
            "User-Agent: bar\n"
            "\n"
            "\n"
            "Disallow: /\n"
        )
        parser = RobotsTxtParser(unix_file.encode("UTF-8"), self.report)
        parser.parse()
        self.assertEqual(4, self.report.valid_directives)
        self.assertEqual(6, self.report.last_line_seen)

        dos_file = (
            "User-Agent: foo\r\n"
            "Allow: /some/path\r\n"
            "User-Agent: bar\r\n"
            "\r\n"
            "\r\n"
            "Disallow: /\r\n"
        )
        parser = RobotsTxtParser(dos_file.encode("UTF-8"), self.report)
        parser.parse()
        self.assertEqual(4, self.report.valid_directives)
        self.assertEqual(6, self.report.last_line_seen)

        mac_file = (
            "User-Agent: foo\r\n"
            "Allow: /some/path\r\n"
            "User-Agent: bar\r\n"
            "\r\n"
            "\r\n"
            "Disallow: /\r\n"
        )
        parser = RobotsTxtParser(mac_file.encode("UTF-8"), self.report)
        parser.parse()
        self.assertEqual(4, self.report.valid_directives)
        self.assertEqual(6, self.report.last_line_seen)

        no_finale_new_line = (
            "User-Agent: foo\n"
            "Allow: /some/path\n"
            "User-Agent: bar\n"
            "\n"
            "\n"
            "Disallow: /"
        )
        parser = RobotsTxtParser(no_finale_new_line.encode("UTF-8"), self.report)
        parser.parse()
        self.assertEqual(4, self.report.valid_directives)
        self.assertEqual(6, self.report.last_line_seen)

        mixed_file = (
            "User-Agent: foo\n"
            "Allow: /some/path\r\n"
            "User-Agent: bar\n"
            "\r\n"
            "\n"
            "Disallow: /"
        )
        parser = RobotsTxtParser(mixed_file.encode("UTF-8"), self.report)
        parser.parse()
        self.assertEqual(4, self.report.valid_directives)
        self.assertEqual(6, self.report.last_line_seen)

    # BOM characters are unparseable and thus skipped. The rules following the line are used.
    def test_ID_UTF8ByteOrderMarkIsSkipped(self):
        utf8_file_full_BOM = b"\xEF\xBB\xBF" b"User-Agent: foo\n" b"Allow: /AnyValue\n"
        parser = RobotsTxtParser(utf8_file_full_BOM, self.report)
        parser.parse()
        self.assertEqual(2, self.report.valid_directives)
        self.assertEqual(0, self.report.unknown_directives)

        utf8_file_partial2BOM = b"\xEF\xBB" b"User-Agent: foo\n" b"Allow: /AnyValue\n"
        # We allow as well partial ByteOrderMarks.
        parser = RobotsTxtParser(utf8_file_partial2BOM, self.report)
        parser.parse()
        self.assertEqual(2, self.report.valid_directives)
        self.assertEqual(0, self.report.unknown_directives)

        utf8_file_partial1BOM = b"\xEF" b"User-Agent: foo\n" b"Allow: /AnyValue\n"
        parser = RobotsTxtParser(utf8_file_partial1BOM, self.report)
        parser.parse()
        self.assertEqual(2, self.report.valid_directives)
        self.assertEqual(0, self.report.unknown_directives)

        # If the BOM is not the right sequence, the first line looks like garbage
        # that is skipped.
        utf8_file_brokenBOM = b"\xEF\x11\xBF" b"User-Agent: foo\n" b"Allow: /AnyValue\n"
        parser = RobotsTxtParser(utf8_file_brokenBOM, self.report)
        parser.parse()
        self.assertEqual(1, self.report.valid_directives)
        self.assertEqual(1, self.report.unknown_directives)

        # Some other messed up file: BOMs only valid in the beginning of the file.
        utf8_file_BOM_somewhere_in_middle_of_file = (
            b"User-Agent: foo\n" b"\xEF\xBB\xBF" b"Allow: /AnyValue\n"
        )
        parser = RobotsTxtParser(utf8_file_BOM_somewhere_in_middle_of_file, self.report)
        parser.parse()
        self.assertEqual(1, self.report.valid_directives)
        self.assertEqual(1, self.report.unknown_directives)

    # Google specific: the RFC allows any line that crawlers might need, such as
    # sitemaps, which Google supports.
    # See REP RFC section "Other records".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.4
    def test_ID_NonStandardLineExample_Sitemap(self):
        sitemap_loc = "http://foo.bar/sitemap.xml"
        robotstxt = (
            "User-Agent: foo\n"
            "Allow: /some/path\n"
            "User-Agent: bar\n"
            "\n"
            "\n"
            "Sitemap: " + sitemap_loc + "\n"
        )
        parser = RobotsTxtParser(robotstxt.encode("UTF-8"), self.report)
        parser.parse()
        self.assertEqual(sitemap_loc, self.report.sitemap)

        # A sitemap line may appear anywhere in the file.
        robotstxt = (
            "Sitemap: " + sitemap_loc + "\n"
            "User-Agent: foo\n"
            "Allow: /some/path\n"
            "User-Agent: bar\n"
            "\n"
            "\n"
        )
        parser = RobotsTxtParser(robotstxt.encode("UTF-8"), self.report)
        parser.parse()
        self.assertEqual(sitemap_loc, self.report.sitemap)


if __name__ == "__main__":
    unittest.main()
