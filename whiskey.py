#!/usr/bin/env python3
import re
import random
import hashlib
from datetime import datetime
from calendar import month_abbr
import json

from namify import namify

TIME_RE = re.compile(r'([A-Z][a-z]{2}) (\d+), (\d{2}):(\d{2})')
AUTHOR_RE = re.compile(r'([A-Z][a-z]+) ([a-z ]*[A-Z]\w+):?')
PHONE_RE = re.compile(r'(\+[\d ]+\d)')


class Whiskey(object):
    def __init__(self, filename):
        self.filename = filename
        self.messages = []


    def _namify_match(self, match):
        return namify(match.groups()[0])


    def read(self):
        n = 0
        with open(self.filename, 'r') as f:
            for line in f:
                line = line.replace(b"\xe2\x80\xaa".decode(), '')
                line = line.replace(b"\xe2\x80\xac".decode(), '')

                line = re.sub(PHONE_RE, self._namify_match, line)

                msg = {}
                time = re.match(TIME_RE, line)
                if time is None:
                    self.messages[n-1]['text'] += line
                    continue

                g = time.groups()
                ma = {v: k for k,v in enumerate(month_abbr)}
                dt = datetime(
                    2014,
                    int(ma[g[0]]),
                    int(g[1]),
                    int(g[2]),
                    int(g[3])
                )
                msg['datetime'] = dt.isoformat()
                msg['time'] = line[0:time.end(4)]

                rest = line[time.end(4) + 3:]

                if rest.lower().startswith('you'):
                    msg['author'] = 'you'
                    before = rest[:3]
                    rest = rest[3:]
                else:
                    author = re.match(AUTHOR_RE, rest.lstrip())
                    msg['author'] = author.groups()[0]

                    before = rest[:author.end(2)]
                    rest = rest[author.end(2):]

                if rest[0] == ':':
                    msg['type'] = 'chat'
                    rest = rest[2:]
                else:
                    msg['type'] = 'action'

                msg['text'] = rest[:-1]
                self.messages.append(msg)


    def write_json(self, outfile):
        with open(outfile, 'w') as f:
            json.dump(self.messages, f, indent=2)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Parse a Whatsapp history file.")
    parser.add_argument('in_file', help="the history file")
    parser.add_argument('out_file', help="a json file to write to")

    args = parser.parse_args()

    glass = Whiskey(args.in_file)
    glass.read()
    glass.write_json(args.out_file)
