#!/usr/bin/env python3


import tempfile
import subprocess
import sys
from pathlib import Path
import polib
import re


def strip_rst(line):
    return re.sub(
        r""":[^:]*?:`[^`]*?` |
            ``.*?`` |
            {[a-z]*?} |  # Sphinx tag
            -[A-Za-z]\b |
            `[^`]*?`_ |
            \*[^*]*?\*
        """, '', line, flags=re.VERBOSE)


def po_to_text(po):
    buffer = []
    lines = 0
    entries = polib.pofile(po)
    for entry in entries:
        while lines < entry.linenum:
            buffer.append('')
            lines += 1
        buffer.append(strip_rst(entry.msgstr))
        lines += 1
    return '\n'.join(buffer)


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Check spelling in po files containing restructuredText.')
    parser.add_argument('-l', '--language', type=str, default='fr')
    parser.add_argument('--glob', type=str, default='**/*.po')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)
        for po_file in Path('.').glob(args.glob):
            (tmpdir / po_file.name).write_text(po_to_text(str(po_file)))
            output = subprocess.check_output(
                ['hunspell', '-d', args.language, '-p', 'perso', '-u3',
                 str(tmpdir / po_file.name)],
                universal_newlines=True)
            for line in output.split('\n'):
                match = re.match(r'(?P<path>.*):(?P<line>[0-9]+): Locate: (?P<error>.*) \| Try: .*$', line)
                if match:
                    print(match.group('path').replace(str(tmpdir), '').lstrip('/'),
                          match.group('line'),
                          match.group('error'),
                          sep=':')


if __name__ == '__main__':
    main()
