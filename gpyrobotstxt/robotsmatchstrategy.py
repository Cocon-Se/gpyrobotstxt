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

class RobotsMatchStrategy:
    def __init__(self):
        pass

    def match_allow(self, path, pattern):
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L640
        if self.matches(path, pattern):
            return len(pattern)
        return -1

    def match_disallow(self, path, pattern):
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L645
        if self.matches(path, pattern):
            return len(pattern)
        return -1

    def matches(self, path, pattern):
        # Ref: https://github.com/google/robotstxt/blob/master/robots.cc#L74
        """Implements robots.txt pattern matching.

        Returns true if URI path matches the specified pattern. Pattern is anchored
        at the beginning of path. '$' is special only at the end of pattern.

        Since both path and pattern are externally determined (by the webmaster),
        we make sure to have acceptable worst-case performance.
        """

        pathlen = len(path)
        numpos = 1

        ###numpos = 0

        # The pos[] array holds a sorted list of indexes of 'path', with length
        # 'numpos'.  At the start and end of each iteration of the main loop below,
        # the pos[] array will hold a list of the prefixes of the 'path' which can
        # match the current prefix of 'pattern'. If this list is ever empty,
        # return false. If we reach the end of 'pattern' with at least one element
        # in pos[], return true.
        pos = [0] * (pathlen + 1)

        for i in range(len(pattern)):
            if pattern[i] == "$" and (i + 1 == len(pattern)):
                return pos[numpos - 1] == pathlen
            if pattern[i] == "*":
                numpos = pathlen - pos[0] + 1
                for j in range(1, numpos):
                    pos[j] = pos[j - 1] + 1
            else:
                # Includes '$' when not at the end of the pattern.
                newnumpos = 0
                for j in range(numpos):
                    if pos[j] < pathlen and path[pos[j]] == pattern[i]:
                        pos[newnumpos] = pos[j] + 1
                        newnumpos += 1
                numpos = newnumpos
                if numpos == 0:
                    return False

        return True
