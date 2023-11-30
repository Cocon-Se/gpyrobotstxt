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

class ParsedRobotsKey:
    class KeyType:
        USER_AGENT = 1
        SITEMAP = 2
        ALLOW = 3
        DISALLOW = 4
        UNKNOWN = 128

    def __init__(self):
        self._type = self.KeyType.UNKNOWN
        self._key_text = ""

    def parse(self, key):
        self._key_text = key
        if self.key_is_user_agent(key):
            self._type = self.KeyType.USER_AGENT
        elif self.key_is_allow(key):
            self._type = self.KeyType.ALLOW
        elif self.key_is_disallow(key):
            self._type = self.KeyType.DISALLOW
        elif self.key_is_sitemap(key):
            self._type = self.KeyType.SITEMAP
        else:
            self._type = self.KeyType.UNKNOWN

    def type(self):
        return self._type

    def unknown_key(self):
        return self._key_text

    def key_is_user_agent(self, key):
        # Enables the parsing of common typos in robots.txt
        return key.lower().startswith("user-agent") or \
            key.lower().startswith("useragent") or \
            key.lower().startswith("user agent")

    def key_is_allow(self, key):
        return key.lower().startswith("allow")

    def key_is_disallow(self, key):
        # Enables the parsing of common typos in robots.txt
        return key.lower().startswith("disallow") or \
            key.lower().startswith("dissallow") or \
            key.lower().startswith("dissalow") or \
            key.lower().startswith("disalow") or \
            key.lower().startswith("diaslow") or \
            key.lower().startswith("diasllow") or \
            key.lower().startswith("disallaw")

    def key_is_sitemap(self, key):
        # Enables the parsing of common typos in robots.txt
        return key.lower().startswith("sitemap") or \
            key.lower().startswith("site-map")

