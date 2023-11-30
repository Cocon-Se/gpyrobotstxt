# pyrobotstxt

[![Apache 2.0](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

`pyrobotstxt` is a native Python port of [Google's robots.txt parser and matcher C++
library](https://github.com/google/robotstxt).

- Preserves all behaviour of original library
- All 100% of original test suite functionality
- Minor language-specific cleanups

As per Google's original library, we include a small main executable,
for webmasters, that allows testing a single URL and user-agent against
a robots.txt. Ours is called `robots_main`, and its inputs and outputs
are compatible with the original tool.

## About

Quoting the README from Google's robots.txt parser and matcher repo:

> The Robots Exclusion Protocol (REP) is a standard that enables website owners to control which URLs may be accessed by automated clients (i.e. crawlers) through a simple text file with a specific syntax. It's one of the basic building blocks of the internet as we know it and what allows search engines to operate.
>
> Because the REP was only a de-facto standard for the past 25 years, different implementers implement parsing of robots.txt slightly differently, leading to confusion. This project aims to fix that by releasing the parser that Google uses.
>
> The library is slightly modified (i.e. some internal headers and equivalent symbols) production code used by Googlebot, Google's crawler, to determine which URLs it may access based on rules provided by webmasters in robots.txt files. The library is released open-source to help developers build tools that better reflect Google's robots.txt parsing and matching.

Package `pyrobotstxt`` aims to be a faithful conversion, from C++ to Python, of Google's robots.txt parser and matcher.

## Pre-requisites

- [Python](https://www.python.org/) version 3.9
Older Python releases should NOT be OK. Python versions above 3.11 should work fine, but only Python 3.9, 3.10 & 3.11 has been tested (so far).

## Installation

```shell
pip install pyrobotstxt
```

## Example Code

```python
from pyrobotstxt.robots_cc import RobotsMatcher

if __name__ == "__main__":
    # Contents of robots.txt file.
    robotsTxt_content = b"""
        # robots.txt with restricted area

        User-agent: *
        Disallow: /members/*

        Sitemap: http://example.net/sitemap.xml
    """
    # Target URI.
    uri = "http://example.net/members/index.html"

    matcher = RobotsMatcher()
    allowed = matcher.allowed_by_robots(robotsTxt_content, "FooBot/1.0", uri)

```

## Testing

To run the tests execute `python -m unittest discover -s test -p test_*.py`
For a specific test `python -m unittest discover -s test -p [TEST_NAME].py`, for example `python -m unittest discover -s test -p test_google_only_system.py`

## Notes

The library required that the URI passed to the
`AgentAllowed` and `AgentsAllowed` functions, or to the URI parameter
of the standalone binary tool, should follow the encoding/escaping format specified by RFC3986, because the library itself does not perform URI normalisation.

## License

Like the original library, `pyrobotstxt` is licensed under the terms of the
Apache License, Version 2.0.

See [LICENSE](LICENSE) for more information.

## Links

- Original project: [Google robots.txt parser and matcher library](https://github.com/google/robotstxt)
