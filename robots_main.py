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
# Simple Python program to assess whether a URL is accessible to a user-agent according
# to records found in a local robots.txt file, based on Google's robots.txt
# parsing and matching algorithms.
# Usage:
#     python robots_main.py <local_path_to_robotstxt> <user_agent> <url>
# Arguments:
# local_path_to_robotstxt: local path to a file containing robots.txt records.
#   For example: /home/users/username/robots.txt
# user_agent: a token to be matched against records in the robots.txt.
#   For example: Googlebot
# url: a url to be matched against records in the robots.txt. The URL must be
# %-encoded according to RFC3986.
#   For example: https://example.com/accessible/url.html
# Output: Prints a sentence with verdict about whether 'user_agent' is allowed
# to access 'url' based on records in 'local_path_to_robotstxt'.
# Return code:
#   0 when the url is ALLOWED for the user_agent.
#   1 when the url is DISALLOWED for the user_agent.
#   2 when --help is requested or if there is something invalid in the flags passed.

import sys
import argparse

from robots_cc import RobotsMatcher

def get_script_arguments():
    parser = argparse.ArgumentParser(description="RobotsTxt")
    parser.add_argument("--file", type=str, required=True, help="local path to a file containing 'robots.txt' records.")
    parser.add_argument("--ua", type=str, required=True, help="a User Agent to be matched against records in the robots.txt.")
    parser.add_argument("--uri", type=str, required=True, help="a url to be matched against records in the robots.txt.")
    return parser.parse_args()


if __name__ == "__main__":
    args = get_script_arguments()
    filename: str = args.file
    with open(filename,  mode='rb') as file:
        robots_content: str = file.read()
    user_agents: str = args.ua.split(",")

    matcher = RobotsMatcher()
    allowed = matcher.allowed_by_robots(robots_content, user_agents, args.uri)

    print(
        f"user-agent '{user_agents}' with URI '{args.uri}': {'ALLOWED' if allowed else 'DISALLOWED'}"
    )
    if not robots_content:
        print("notice: robots file is empty so all user-agents are allowed")

    sys.exit(0 if allowed else 1)
