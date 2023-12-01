# Copyright 2023 cocon.se (http://cocon.se/)
# Copyright 1999 Google LLC
#
# Licensed under the GNU General Public License v3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.gnu.org/licenses/gpl-3.0
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

class Match:
    kNoMatchPriority = -1

    def __init__(self, priority=kNoMatchPriority, line=0):
        self.priority = priority
        self.line = line

    def set(self, priority, line):
        self.priority = priority
        self.line = line

    def clear(self):
        self.set(self.kNoMatchPriority, 0)

    def get_line(self):
        return self.line

    def get_priority(self):
        return self.priority

    def higher_priority_match(a, b):
        return a if a.get_priority() > b.get_priority() else b

class MatchHierarchy:
    def __init__(self):
        self._global = Match()     # Match for '*'
        self._specific = Match()   # Match for queried agent

    def clear(self):
        self._global.clear()
        self._specific.clear()