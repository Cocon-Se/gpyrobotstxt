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

import re
import io

from gpyrobotstxt.parsedrobotskey import ParsedRobotsKey


def ishexdigit(c):
    return "0" <= c <= "9" or "a" <= c <= "f" or "A" <= c <= "F"


class RobotsTxtParser:
    def __init__(self, robots_body, handler):
        self._robots_body = robots_body
        self._handler = handler

    def get_key_and_value_from(self, line: str):
        # get_key_and_value_from attempts to parse a line of robots.txt into a key/value pair.
        # On success, the parsed key and value, and true, are returned.
        # If parsing is unsuccessful, parseKeyAndValue returns two empty strings and false.

        # Remove comments from the current robots.txt line
        comment = line.find("#")
        if comment != -1:
            line = line[:comment]

        line = line.strip()

        # Rules must match the following pattern:
        #   <key>[ \t]*:[ \t]*<value>
        sep = line.find(":")
        if sep == -1:
            # Google-specific optimization: some people forget the colon, so we need to
            # accept whitespace in its stead.
            white = re.compile("|".join([" ", "\t"]))
            sep = white.search(line)
            if sep is not None:
                sep = sep.start()
                val = line[sep + 1 :]
                if len(val) == 0:
                    raise SyntaxError("Syntax error in 'robots.txt' file.")
                if white.search(val) is not None:
                    # We only accept whitespace as a separator if there are exactly two
                    # sequences of non-whitespace characters.  If we get here, there were
                    # more than 2 such sequences since we stripped trailing whitespace above.
                    return "", "", False

        if sep == -1:
            return "", "", False  # Couldn't find a separator.

        key = line[:sep].strip()
        if len(key) == 0:
            return "", "", False

        value = line[sep + 1 :].strip()

        return key, value, True

    def need_escape_value_for_key(self, key):
        key_type = key.type()
        if key_type in [
            ParsedRobotsKey.KeyType.USER_AGENT,
            ParsedRobotsKey.KeyType.SITEMAP,
        ]:
            return False
        else:
            return True

    def maybe_escape_pattern(self, path: str):
        need_capitalize = False
        num_to_escape = 0

        def s(i):
            if i < len(path):
                return path[i]
            return ""

        # First, scan the buffer to see if changes are needed. Most don't.
        for i in range(len(path)):
            # (a) % escape sequence.
            if path[i] == "%" and ishexdigit(s(i + 1)) and ishexdigit(s(i + 2)):
                if s(i + 1).islower() or s(i + 2).islower():
                    need_capitalize = True
            elif not path[i].isascii():
                # (b) needs escaping.
                num_to_escape += 1
            # (c) Already escaped and escape-characters normalized (eg. %2f -> %2F).

        # Return if no changes needed.
        if num_to_escape == 0 and not need_capitalize:
            return path

        dst = io.BytesIO()
        i = 0
        while (i < len(path)):
            if path[i] == '%' and ishexdigit(s(i + 1)) and ishexdigit(s(i + 2)):
              # (a) Normalize %-escaped sequence (eg. %2f -> %2F).
              dst.write(b'%')
              i += 1
              dst.write(path[i].upper().encode())
              i += 1
              dst.write(path[i].upper().encode())
            elif not path[i].isascii():
                # (b) %-escape octets whose highest bit is set. These are outside the ASCII range
                dst.write(b'%')
                dst.write(path[i].encode().hex('%').upper().encode())
            else:
                # (c) Normal character, no modification needed.
                dst.write(path[i].encode())
            i += 1

        return dst.getvalue().decode('utf-8')

    def emit_key_value_to_handler(self, line, key, value, handler):
        key_type = key.type()

        if key_type == ParsedRobotsKey.KeyType.USER_AGENT:
            handler.handle_user_agent(line, value)
        elif key_type == ParsedRobotsKey.KeyType.ALLOW:
            handler.handle_allow(line, value)
        elif key_type == ParsedRobotsKey.KeyType.DISALLOW:
            handler.handle_disallow(line, value)
        elif key_type == ParsedRobotsKey.KeyType.SITEMAP:
            handler.handle_sitemap(line, value)
        elif key_type == ParsedRobotsKey.KeyType.UNKNOWN:
            handler.handle_unknown_action(line, key.unknown_key(), value)

    def parse_and_emit_line(self, current_line: int, line: str):
        string_key, value, ok = self.get_key_and_value_from(line)
        if not ok:
            return

        key = ParsedRobotsKey()
        key.parse(string_key)

        if self.need_escape_value_for_key(key):
            value = self.maybe_escape_pattern(value)

        self.emit_key_value_to_handler(current_line, key, value, self._handler)

    def parse(self):
        utf_bom = bytes([0xEF, 0xBB, 0xBF])

        # Certain browsers limit the URL length to 2083 bytes. In a robots.txt, it's
        # fairly safe to assume any valid line isn't going to be more than many times
        # that max url length of 2KB. We want some padding for
        # UTF-8 encoding/nulls/etc. but a much smaller bound would be okay as well.
        # If so, we can ignore the chars on a line past that.
        kmax_line_len = 2083 * 8

        self._handler.handle_robots_start()

        length = len(self._robots_body)
        cur = 0

        # Skip BOM if present - including partial BOMs.
        for i in range(len(utf_bom)):
            if cur == length:
                break
            b = self._robots_body[cur]
            if b != utf_bom[i]:
                break
            cur += 1

        line_num = 0
        last_was_carriage_return = False

        start = cur
        end = cur

        while True:
            if cur == length:
                break
            b = self._robots_body[cur]
            cur += 1
            if b != 0x0A and b != 0x0D:  # Non-line-ending char case.
                # Add to current line, as long as there's room.
                if end - start < kmax_line_len - 1:
                    end += 1
            else:
                is_CRLF_continuation = (
                    (end == start) and last_was_carriage_return and (b == 0x0A)
                )
                if not is_CRLF_continuation:
                    line_num += 1
                    self.parse_and_emit_line(line_num, self._robots_body[start:end].decode('utf-8', 'replace'))
                start = cur
                end = cur
                last_was_carriage_return = b == 0x0D

        line_num += 1
        self.parse_and_emit_line(line_num, self._robots_body[start:end].decode('utf-8', 'replace'))
        self._handler.handle_robots_end()
