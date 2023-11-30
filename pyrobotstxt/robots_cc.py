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
#
# Implements expired internet draft
#  http://www.robotstxt.org/norobots-rfc.txt
# with Google-specific optimizations detailed at
#   https://developers.google.com/search/reference/robots_txt
#
#
# Converted 2023-11-17, from https://github.com/google/robotstxt/blob/master/robots.cc

from urllib.parse import urlparse
from typing import List

from pyrobotstxt.robotsmatchstrategy import RobotsMatchStrategy
from pyrobotstxt.robotstxtparser import RobotsTxtParser
from pyrobotstxt.match import MatchHierarchy


def find_first_of(s, characters, pos=0):
    st = set(characters)
    ind = next((i for i, ch in enumerate(s[pos:]) if ch in st), None)
    if ind is not None:
        return pos + ind
    return -1


def get_path_params_query(url: str):
    # Extracts path (with params) and query part from URL. Removes scheme,
    # authority, and fragment. Result always starts with "/".
    # Returns "/" if the url doesn't have a path or is not valid.

    path = ""

    # Initial two slashes are ignored.
    search_start = 0
    if len(url) >= 2 and url[0] == "/" and url[1] == "/":
        search_start = 2

    early_path = find_first_of(url, "/?;", search_start)
    protocol_end = url.find("://", search_start)
    if early_path < protocol_end:
        # If path, param or query starts before ://, :// doesn't indicate protocol.
        protocol_end = -1

    if protocol_end == -1:
        protocol_end = search_start
    else:
        protocol_end += 3

    path_start = find_first_of(url, "/?;", protocol_end)
    if path_start != -1:
        hash_pos = url.find("#", search_start)
        if hash_pos != -1 and hash_pos < path_start:
            return "/"
        path_end = len(url) if hash_pos == -1 else hash_pos
        if url[path_start] != "/":
            # Prepend a slash if the result would start e.g. with '?'.
            return "/" + url[path_start:path_end]
        return url[path_start:path_end]

    return "/"


class RobotsMatcher:
    def __init__(self):
        self._seen_global_agent = False
        self._seen_specific_agent = False
        self._ever_seen_specific_agent = False
        self._seen_separator = False
        self._path = None
        self._user_agents = None

        self._allow = MatchHierarchy()
        self._disallow = MatchHierarchy()
        self._match_strategy = RobotsMatchStrategy()

    def init_user_agents_and_path(self, user_agents: List[str], path: str):
        if path[0] != "/":
            raise ValueError("Path must begin with '/'")
        self._path = path
        self._user_agents = user_agents

    def extract_user_agent(self, user_agent: str):
        # Allowed characters in user-agent are [a-zA-Z_-].
        def ascii_is_alpha(c):
            return "a" <= c <= "z" or "A" <= c <= "Z"

        i = 0
        while i < len(user_agent):
            c = user_agent[i]
            if not ascii_is_alpha(c) and not c == "-" and not c == "_":
                break
            i += 1

        return user_agent[:i]

    def extract_user_agent_rfc7231(self, user_agent: str):
        # extract_user_agent extracts the matchable part of a user agent string,
        # essentially stopping at the first invalid character.
        # Example: 'Googlebot/2.1' becomes 'Googlebot'

        # Allowed characters in user-agent are [a-zA-Z_-].
        #
        # Bugfix:
        #
        # According to RFC 7231, the 'product'  part of the user-agent
        # is defined as a 'token', which allows:
        #
        #  "!" / "#" / "$" / "%" / "&" / "'" / "*"
        #  / "+" / "-" / "." / "^" / "_" / "`" / "|" / "~"
        #  / DIGIT / ALPHA
        #
        # See https://httpwg.org/specs/rfc7231.html#header.user-agent

        def ascii_is_alpha(c):
            return "a" <= c <= "z" or "A" <= c <= "Z"

        def ascii_is_numeric(c):
            return "0" <= c <= "9"

        def ascii_is_special(c):
            allowed = "~#$%'*+-.^_`|~"
            return c in allowed

        i = 0
        while i < len(user_agent):
            c = user_agent[i]
            if (
                not ascii_is_alpha(c)
                and not ascii_is_numeric(c)
                and not ascii_is_special(c)
            ):
                break
            i += 1

        return user_agent[:i]

    def seen_any_agent(self):
        return self._seen_global_agent or self._seen_specific_agent

    def handle_robots_start(self):
        # This is a new robots.txt file, so we need to reset all the instance member variables.
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L538
        self._allow.clear()
        self._disallow.clear()

        self._seen_global_agent = False
        self._seen_specific_agent = False
        self._ever_seen_specific_agent = False
        self._seen_separator = False

    def handle_robots_end(self):
        # handle_robots_end is called at the end of parsing the robots.txt file.
        # For RobotsMatcher, this does nothing.
        pass

    def handle_user_agent(self, line_num, user_agent):
        # handle_user_agent is called for every "User-Agent:" line in robots.txt.
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L567
        if self._seen_separator:
            self._seen_global_agent = False
            self._seen_specific_agent = False
            self._seen_separator = False

        # Google-specific optimization: a '*' followed by space and more characters
        # in a user-agent record is still regarded a global rule.
        if (
            len(user_agent) >= 1
            and user_agent[0] == "*"
            and (len(user_agent) == 1 or user_agent[1].isspace())
        ):
            self._seen_global_agent = True
        else:
            user_agent = self.extract_user_agent(user_agent)
            for agent in self._user_agents:
                if agent.casefold() == user_agent.casefold():
                    self._ever_seen_specific_agent = True
                    self._seen_specific_agent = True
                    break

    def handle_allow(self, line_num, value):
        # handle_allow is called for every "Allow:" line in robots.txt.
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L589
        if not self.seen_any_agent():
            return

        self._seen_separator = True

        priority = self._match_strategy.match_allow(self._path, value)
        if priority >= 0:
            if self._seen_specific_agent:
                if self._allow._specific.priority < priority:
                    self._allow._specific.set(priority, line_num)
            else:
                if not self._seen_global_agent:
                    raise SyntaxError("Not seen global agent")
                if self._allow._global.priority < priority:
                    self._allow._global.set(priority, line_num)
        else:
            #  Google-specific optimization: 'index.htm' and 'index.html' are normalized to '/'
            slash_pos = value.rfind("/")
            if slash_pos != -1 and value[slash_pos:].startswith("/index.htm"):
                new_pattern = value[: slash_pos + 1] + "$"
                self.handle_allow(line_num, new_pattern)

    def handle_disallow(self, line_num, value):
        # handle_disallow is called for every "Disallow:" line in robots.txt.
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L622
        if not self.seen_any_agent():
            return

        self._seen_separator = True
        priority = self._match_strategy.match_disallow(self._path, value)
        if priority >= 0:
            if self._seen_specific_agent:
                if self._disallow._specific.priority < priority:
                    self._disallow._specific.set(priority, line_num)
            else:
                if not self._seen_global_agent:
                    raise SyntaxError("Not seen global agent")
                if self._disallow._global.priority < priority:
                    self._disallow._global.set(priority, line_num)

    def handle_sitemap(self, line_num, value):
        # handle_sitemap is called for every "Sitemap:" line in robots.txt.
        # For RobotsMatcher, this does nothing.
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L650
        pass

    def handle_unknown_action(self, line_num, action, value):
        # handle_unknown_action is called for every unrecognized line in robots.txt.
        # For RobotsMatcher, this does nothing.
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L652
        pass

    def disallow(self):
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L506
        if self._allow._specific.priority > 0 or self._disallow._specific.priority > 0:
            return self._disallow._specific.priority > self._allow._specific.priority

        if self._ever_seen_specific_agent:
            return False

        if self._allow._global.priority > 0 or self._disallow._global.priority > 0:
            return self._disallow._global.priority > self._allow._global.priority

        return False

    def allowed_by_robots(self, robots_body, user_agents, url):
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L487
        try:
            urlparse(url)
        except:
            return False

        if isinstance(robots_body, str):
            robots_body = robots_body.encode("utf-8")

        path: str = get_path_params_query(url)
        self.init_user_agents_and_path(user_agents, path)
        parser = RobotsTxtParser(robots_body, self)
        parser.parse()

        return not self.disallow()

    def one_agent_allowed_by_robots(self, robots_txt, user_agent, url):
        return self.allowed_by_robots(robots_txt, [user_agent], url)

    def is_valid_user_agent_to_obey(self, user_agent):
        return len(user_agent) > 0 and self.extract_user_agent(user_agent) == user_agent
