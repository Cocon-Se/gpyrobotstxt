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

from gpyrobotstxt.robots_cc import RobotsMatcher


class TestGoogleOnlySystem(unittest.TestCase):
    def setUp(self):
        self.robots_matcher = RobotsMatcher()

    def is_user_agent_allowed(self, robotstxt: str, useragent: str, url: str):
        return self.robots_matcher.one_agent_allowed_by_robots(
            robotstxt, useragent, url
        )

    # Google-specific: system test.
    def test_GoogleOnly_System(self):
        robotstxt = "user-agent: FooBot\n" "disallow: /\n"

        # Empty robots.txt: everything allowed.
        self.assertTrue(self.is_user_agent_allowed("", "FooBot", ""))

        # All params empty: same as robots.txt empty, everything allowed.
        self.assertTrue(self.is_user_agent_allowed("", "", ""))

        # Empty user-agent to be matched: everything allowed.
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "", ""))

        # Empty url: implicitly allowed.
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", ""))

    # Rules are colon separated name-value pairs. The following names are provisioned:
    #     user-agent: <value>
    #     allow: <value>
    #     disallow: <value>
    # See REP RFC section "Protocol Definition".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.1
    #
    # Google specific: webmasters sometimes miss the colon separator, but it's
    # obvious what they mean by "disallow /", so we assume the colon if it's missing.
    def test_ID_LineSyntax_Line(self):
        robotstxt_correct = "user-agent: FooBot\n" "disallow: /\n"
        robotstxt_incorrect = "foo: FooBot\n" "bar: /\n"
        robotstxt_incorrect_accepted = "user-agent FooBot\n" "disallow /\n"
        url = "http://foo.bar/x/y"

        self.assertFalse(self.is_user_agent_allowed(robotstxt_correct, "FooBot", url))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_incorrect, "FooBot", url))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_incorrect_accepted, "FooBot", url))

    # A group is one or more user-agent line followed by rules, and terminated
    # by a another user-agent line. Rules for same user-agents are combined
    # opaquely into one group. Rules outside groups are ignored.
    # See REP RFC section "Protocol Definition".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.1
    def test_ID_LineSyntax_Groups(self):
        robotstxt = (
            "allow: /foo/bar/\n"
            "\n"
            "user-agent: FooBot\n"
            "disallow: /\n"
            "allow: /x/\n"
            "user-agent: BarBot\n"
            "disallow: /\n"
            "allow: /y/\n"
            "\n"
            "\n"
            "allow: /w/\n"
            "user-agent: BazBot\n"
            "\n"
            "user-agent: FooBot\n"
            "allow: /z/\n"
            "disallow: /\n"
        )

        url_w = "http://foo.bar/w/a"
        url_x = "http://foo.bar/x/b"
        url_y = "http://foo.bar/y/c"
        url_z = "http://foo.bar/z/d"
        url_foo = "http://foo.bar/foo/bar/"

        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url_x))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url_z))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", url_y))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "BarBot", url_y))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "BarBot", url_w))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "BarBot", url_z))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "BazBot", url_z))

        # Lines with rules outside groups are ignored.
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", url_foo))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "BarBot", url_foo))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "BazBot", url_foo))

    # Group must not be closed by rules not explicitly defined in the REP RFC.
    # See REP RFC section "Protocol Definition".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.1
    def test_ID_LineSyntax_Groups_OtherRules(self):
        robotstxt1 = (
            "User-agent: BarBot\n"
            "Sitemap: https://foo.bar/sitemap\n"
            "User-agent: *\n"
            "Disallow: /\n"
        )
        robotstxt2 = (
            "User-agent: FooBot\n"
            "Invalid-Unknown-Line: unknown\n"
            "User-agent: *\n"
            "Disallow: /\n"
        )
        url = "http://foo.bar/"

        self.assertFalse(self.is_user_agent_allowed(robotstxt1, "FooBot", url))
        self.assertFalse(self.is_user_agent_allowed(robotstxt1, "BarBot", url))

        self.assertFalse(self.is_user_agent_allowed(robotstxt2, "FooBot", url))
        self.assertFalse(self.is_user_agent_allowed(robotstxt2, "BarBot", url))

    # REP lines are case insensitive. See REP RFC section "Protocol Definition".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.1
    def test_ID_REPLineNamesCaseInsensitive(self):
        robotstxt_upper =(
            "USER-AGENT: FooBot\n"
            "ALLOW: /x/\n"
            "DISALLOW: /\n"
        )
        robotstxt_lower = (
            "user-agent: FooBot\n"
            "allow: /x/\n"
            "disallow: /\n"
        )
        robotstxt_camel = (
            "uSeR-aGeNt: FooBot\n"
            "AlLoW: /x/\n"
            "dIsAlLoW: /\n"
        )
        url_allowed = "http://foo.bar/x/y"
        url_disallowed = "http://foo.bar/a/b"

        self.assertTrue(self.is_user_agent_allowed(robotstxt_upper, "FooBot", url_allowed))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_lower, "FooBot", url_allowed))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_camel, "FooBot", url_allowed))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_upper, "FooBot", url_disallowed))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_lower, "FooBot", url_disallowed))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_camel, "FooBot", url_disallowed))

    # A user-agent line is expected to contain only [a-zA-Z_-] characters and must
    # not be empty. See REP RFC section "The user-agent line".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.1
    def test_ID_VerifyValidUserAgentsToObey(self):
        self.assertTrue(self.robots_matcher.is_valid_user_agent_to_obey("Foobot"))
        self.assertTrue(self.robots_matcher.is_valid_user_agent_to_obey("Foobot-Bar"))
        self.assertTrue(self.robots_matcher.is_valid_user_agent_to_obey("Foo_Bar"))

        self.assertFalse(self.robots_matcher.is_valid_user_agent_to_obey(""))
        self.assertFalse(self.robots_matcher.is_valid_user_agent_to_obey("ツ"))

        self.assertFalse(self.robots_matcher.is_valid_user_agent_to_obey("Foobot*"))
        self.assertFalse(self.robots_matcher.is_valid_user_agent_to_obey(" Foobot "))
        self.assertFalse(self.robots_matcher.is_valid_user_agent_to_obey("Foobot/2.1"))

        self.assertFalse(self.robots_matcher.is_valid_user_agent_to_obey("Foobot Bar"))

    # User-agent line values are case insensitive.
    # See REP RFC section "The user-agent line".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.1
    def test_ID_UserAgentValueCaseInsensitive(self):
        robotstxt_upper = (
            "User-Agent: FOO BAR\n"
            "Allow: /x/\n"
            "Disallow: /\n"
        )
        robotstxt_lower = (
            "User-Agent: foo bar\n"
            "Allow: /x/\n"
            "Disallow: /\n"
        )
        robotstxt_camel = (
            "User-Agent: FoO bAr\n"
            "Allow: /x/\n"
            "Disallow: /\n"
        )
        url_allowed = "http://foo.bar/x/y"
        url_disallowed = "http://foo.bar/a/b"

        self.assertTrue(self.is_user_agent_allowed(robotstxt_upper, "Foo", url_allowed))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_lower, "Foo", url_allowed))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_camel, "Foo", url_allowed))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_upper, "Foo", url_disallowed))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_lower, "Foo", url_disallowed))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_camel, "Foo", url_disallowed))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_upper, "foo", url_allowed))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_lower, "foo", url_allowed))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_camel, "foo", url_allowed))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_upper, "foo", url_disallowed))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_lower, "foo", url_disallowed))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_camel, "foo", url_disallowed))

    # Google specific: accept user-agent value up to the first space. Space is not
    # allowed in user-agent values, but that doesn't stop webmasters from using
    # them. This is more restrictive than the RFC, since in case of the bad value
    # "Googlebot Images" we'd still obey the rules with "Googlebot".
    # Extends REP RFC section "The user-agent line"
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.1
    def test_GoogleOnly_AcceptUserAgentUpToFirstSpace(self):
        robotstxt = (
            "User-Agent: *\n"
            "Disallow: /\n"
            "User-Agent: Foo Bar\n"
            "Allow: /x/\n"
            "Disallow: /\n"
        )
        url = "http://foo.bar/x/y"

        self.assertTrue(self.is_user_agent_allowed(robotstxt, "Foo", url))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "Foo Bar", url))

    # If no group matches the user-agent, crawlers must obey the first group with a
    # user-agent line with a "*" value, if present. If no group satisfies either
    # condition, or no groups are present at all, no rules apply.
    # See REP RFC section "The user-agent line".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.1
    def test_ID_GlobalGroups_Secondary(self):
        robotstxt_empty = ""
        robotstxt_global = (
            "user-agent: *\n"
            "allow: /\n"
            "user-agent: FooBot\n"
            "disallow: /\n"
        )
        robotstxt_only_specific = (
            "user-agent: FooBot\n"
            "allow: /\n"
            "user-agent: BarBot\n"
            "disallow: /\n"
            "user-agent: BazBot\n"
            "disallow: /\n"
        )
        url = "http://foo.bar/x/y"

        self.assertTrue(self.is_user_agent_allowed(robotstxt_empty, "FooBot", url))
        self.assertFalse(self.is_user_agent_allowed(robotstxt_global, "FooBot", url))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_global, "BarBot", url))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_only_specific, "QuxBot", url))

    # Matching rules against URIs is case sensitive.
    # See REP RFC section "The Allow and Disallow lines".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.2
    def test_ID_AllowDisallow_Value_CaseSensitive(self):
        robotstxt_lowercase_url = (
            "user-agent: FooBot\n"
            "disallow: /x/\n"
        )
        robotstxt_uppercase_url = (
            "user-agent: FooBot\n"
            "disallow: /X/\n"
        )
        url = "http://foo.bar/x/y"

        self.assertFalse(self.is_user_agent_allowed(robotstxt_lowercase_url, "FooBot", url))
        self.assertTrue(self.is_user_agent_allowed(robotstxt_uppercase_url, "FooBot", url))

    # The most specific match found MUST be used. The most specific match is the
    # match that has the most octets. In case of multiple rules with the same
    # length, the least strict rule must be used.
    # See REP RFC section "The Allow and Disallow lines".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.2
    def test_ID_LongestMatch(self):
        url = "http://foo.bar/x/page.html"

        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /x/page.html\n"
            "allow: /x/\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", url))

        robotstxt = (
            "user-agent: FooBot\n"
            "allow: /x/page.html\n"
            "disallow: /x/\n"
        )
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/x/"))

        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: \n"
            "allow: \n"
        )
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url))

        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /\n"
            "allow: /\n"
        )
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url))

        url_a = "http://foo.bar/x"
        url_b = "http://foo.bar/x/"
        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /x\n"
            "allow: /x/\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", url_a))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url_b))

        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /x/page.html\n"
            "allow: /x/page.html\n"
        )
        # In case of equivalent disallow and allow patterns for the same user-agent, allow is used.
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url))

        robotstxt = (
            "user-agent: FooBot\n"
            "allow: /page\n"
            "disallow: /*.html\n"
        )
        # Longest match wins.
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/page.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/page"))

        robotstxt = (
            "user-agent: FooBot\n"
            "allow: /x/page.\n"
            "disallow: /*.html\n"
        )
        # Longest match wins.
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/page.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/page"))

        robotstxt = (
            "User-agent: *\n"
            "Disallow: /x/\n"
            "User-agent: FooBot\n"
            "Disallow: /y/\n"
        )
        # Most specific group for FooBot allows implicitly /x/page.
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/x/page"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/y/page"))

    # Octets in the URI and robots.txt paths outside the range of the US-ASCII
    # coded character set, and those in the reserved range defined by RFC3986,
    # MUST be percent-encoded as defined by RFC3986 prior to comparison.
    # See REP RFC section "The Allow and Disallow lines".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.2
    #
    # NOTE: It's up to the caller to percent encode a URL before passing it to the
    # parser. Percent encoding URIs in the rules is unnecessary.
    def test_ID_Encoding(self):
        # /foo/bar?baz=http://foo.bar stays unencoded.
        robotstxt =(
            "User-agent: FooBot\n"
            "Disallow: /\n"
            "Allow: /foo/bar?qux=taz&baz=http://foo.bar?tar&par\n"
        )
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar?qux=taz&baz=http://foo.bar?tar&par"))

        # 3 byte character: /foo/bar/ツ -> /foo/bar/%E3%83%84
        robotstxt =(
            "User-agent: FooBot\n"
            "Disallow: /\n"
            "Allow: /foo/bar/ツ\n"
        )
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/%E3%83%84"))
        # The parser encodes the 3-byte character, but the URL is not %-encoded.
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/ツ"))

        # Percent encoded 3 byte character: /foo/bar/%E3%83%84 -> /foo/bar/%E3%83%84
        robotstxt =(
            "User-agent: FooBot\n"
            "Disallow: /\n"
            "Allow: /foo/bar/%E3%83%84\n"
        )
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/%E3%83%84"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/ツ"))

        # Percent encoded unreserved US-ASCII: /foo/bar/%62%61%7A -> NULL
        # This is illegal according to RFC3986 and while it may work here due to
        # simple string matching, it should not be relied on.
        robotstxt =(
            "User-agent: FooBot\n"
            "Disallow: /\n"
            "Allow: /foo/bar/%62%61%7A\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/baz"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/%62%61%7A"))

    # The REP RFC defines the following characters that have special meaning in
    # robots.txt:
    # # - inline comment.
    # $ - end of pattern.
    # * - any number of characters.
    # See REP RFC section "Special Characters".
    # https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.3
    def test_ID_SpecialCharacters(self):
        robotstxt = (
            "User-agent: FooBot\n"
            "Disallow: /foo/bar/quz\n"
            "Allow: /foo/*/qux\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/quz"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/quz"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo//quz"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bax/quz"))

        robotstxt = (
            "User-agent: FooBot\n"
            "Disallow: /foo/bar$\n"
            "Allow: /foo/bar/qux\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/qux"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar/baz"))

        robotstxt = (
            "User-agent: FooBot\n"
            "# Disallow: /\n"
            "Disallow: /foo/quz#qux\n"
            "Allow: /\n"
        )
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/bar"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/foo/quz"))

    # Google-specific: "index.html" (and only that) at the end of a pattern is equivalent to "/".
    def test_GoogleOnly_IndexHTMLisDirectory(self):
        robotstxt = (
            "User-Agent: *\n"
            "Allow: /allowed-slash/index.html\n"
            "Disallow: /\n"
        )

        # If index.html is allowed, we interpret this as / being allowed too.
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "foobot", "http://foo.com/allowed-slash/"))
        # Does not exatly match.
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.com/allowed-slash/index.htm"))
        # Exact match.
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "foobot", "http://foo.com/allowed-slash/index.html"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.com/anyother-url"))

    # Google-specific: long lines are ignored after 8 * 2083 bytes.
    def test_GoogleOnly_LineTooLong(self):
        # Disallow rule pattern matches the URL after being cut off at max_line_len.
        eol_len = len("\n")
        max_line_len = 2083 * 8
        allow = "allow: "
        disallow = "disallow: "

        robotstxt = "user-agent: FooBot\n"
        longline = "/x/"
        max_length = max_line_len - len(longline) - len(disallow) + eol_len

        while len(longline) < max_length:
            longline += "a"

        robotstxt += disallow + longline + "/qux\n"
        # Matches nothing, so URL is allowed.
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fux"))
        # Matches cut off disallow rule.
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar" + longline + "/fux"))

        robotstxt = (
        "user-agent: FooBot\n"
        "disallow: /\n"
        )
        longline_a = "/x/"
        longline_b = "/x/"
        max_length = max_line_len - len(longline_a) - len(allow) + eol_len

        while len(longline_a) < max_length:
            longline_a += "a"
            longline_b += "b"

        robotstxt += allow + longline_a + "/qux\n"
        robotstxt += allow + longline_b + "/qux\n"

        # URL matches the disallow rule.
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar"))
        # Matches the allow rule exactly.
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar" + longline_a + "/qux"))
        # Matches cut off allow rule.
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar" + longline_b + "/fux"))

    # Test documentation from https://developers.google.com/search/reference/robots_txt
    def test_GoogleOnly_DocumentationChecks(self):
        # Section "URL matching based on path values".
        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /\n"
            "allow: /fish\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/bar"))

        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish/salmon.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fishheads"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fishheads/yummy.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish.html?id=anything"))

        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/Fish.asp"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/catfish"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/?id=fish"))

        # "/fish*" equals "/fish"
        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /\n"
            "allow: /fish*\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/bar"))

        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish/salmon.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fishheads"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fishheads/yummy.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish.html?id=anything"))

        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/Fish.bar"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/catfish"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/?id=fish"))

        # "/fish/" does not equal "/fish"
        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /\n"
            "allow: /fish/\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/bar"))

        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish/"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish/salmon"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish/?salmon"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish/salmon.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish/?id=anything"))

        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish.html"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/Fish/Salmon.html"))

        # "/*.php"
        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /\n"
            "allow: /*.php\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/bar"))

        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/filename.php"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/folder/filename.php"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/folder/filename.php?parameters"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar//folder/any.php.file.html"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/filename.php/"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/index?f=filename.php/"))

        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/php/"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/index?php"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/windows.PHP"))

        # "/*.php$"
        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /\n"
            "allow: /*.php$\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/bar"))

        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/filename.php"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/folder/filename.php"))

        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/folder/filename.php?parameters"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/filename.php/"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/filename.php5"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/php/"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/filename?php"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/aaaphpaaa"))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar//windows.PHP"))

        # "/fish*.php"
        robotstxt = (
            "user-agent: FooBot\n"
            "disallow: /\n"
            "allow: /fish*.php\n"
        )
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/bar"))

        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fish.php"))
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/fishheads/catfish.php?parameters"))

        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", "http://foo.bar/Fish.PHP"))

        # Section "Order of precedence for group-member records".
        robotstxt = (
            "user-agent: FooBot\n"
            "allow: /p\n"
            "disallow: /\n"
        )
        url = "http://example.com/page"
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url))

        robotstxt = (
            "user-agent: FooBot\n"
            "allow: /folder\n"
            "disallow: /folder\n"
        )
        url = "http://example.com/folder/page"
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url))

        robotstxt = (
            "user-agent: FooBot\n"
            "allow: /page\n"
            "disallow: /*.htm\n"
        )
        url = "http://example.com/page.htm"
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", url))

        robotstxt = (
            "user-agent: FooBot\n"
            "allow: /$\n"
            "disallow: /\n"
        )
        url = "http://example.com/"
        url_page = "http://example.com/page.html"
        self.assertTrue(self.is_user_agent_allowed(robotstxt, "FooBot", url))
        self.assertFalse(self.is_user_agent_allowed(robotstxt, "FooBot", url_page))


if __name__ == "__main__":
    unittest.main()