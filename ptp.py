#!/usr/bin/python3

import os, sys
from subprocess import Popen, PIPE


pageses, gs = [], globals()
for pages in [name for name in dir() if name.startswith('pages_')]:
    _, first, last = pages.split('_')
    for i in range(int(first), int(last) + 1):
        code = 'page_%i = lambda : pages_%i_%i(%i)\n' % (i, int(first), int(last), i)
        code = compile(code, '-generated', 'exec')
        exec(code, globals())

def center(text):
    length, escape = 0, False
    for c in text:
        if c == '\033':
            escape = True
        elif escape:
            escape = c != 'm'
        else:
            length += 1
    length = (width - length) // 2
    return ' ' * length + text

def h(text, cond):
    if cond:
        return '\033[01;31m%s\033[m' % text
    else:
        return text

def pp(local, page):
    for p in range(1, page + 1):
        if ('p%i' % p) in local:
            if p == page:
                print('\033[01;31m', end = '')
            local['p%i' % p]()
            if p == page:
                print('\033[m', end = '')

pages, gs = [], globals()
for i in range(len([name for name in dir() if name.startswith('page_')])):
    pages.append(gs['page_' + str(i + 1)])

print('\033[?25l\033[H\033[2J', end = '')
Popen('stty -echo -icanon'.split(' '), stderr = sys.stderr)
size = Popen('stty size'.split(' '), stderr = sys.stderr, stdout = PIPE).communicate()[0]
(height, width) = size.decode('utf-8', 'replace').split('\n')[0].split(' ')
height, width = int(height), int(width)

pid = os.fork()
if pid != 0:
    try:
        while True:
            (reaped, status) = os.wait()
            if reaped == pid:
                break
    except:
        pass
    if status == 0:
        print('\033[H\033[2J', end = '')
    print('\033[?25h', end = '', flush = True)
    Popen('stty echo icanon'.split(' '), stderr = sys.stderr)
    sys.exit(status)

old_print = print
def print(text = '', *, end = '\n', flush = True):
    old_print(text + '\033[K', end = end, flush = flush)

page, page_last = (1 if len(sys.argv) == 1 else int(sys.argv[1])), len(pages) - 1
page -= 1
while True:
    old_print('\033[H', end = '')
    pages[page]()
    bar, start, switched = int(width * page / page_last), width - len(str(page + 1)), False
    text = '\033[J\033[%i;%iH\033[45m%s\033[m\033[%i;%iH\033[45;30m' % (height, 0, ' ' * bar, height, start)
    for i, c in enumerate(str(page + 1)):
        if start + i > bar:
            if not switched:
                switched = True
                text += '\033[00;35m'
        text += c
    old_print('%s\033[00m' % text, end = '', flush = True)
    while True:
        text = sys.stdin.buffer.read(1)
        if text in b'\n C':
            if page == page_last:
                continue
            page += 1
        elif text in b'\x7fD':
            if page == 0:
                continue
            page -= 1
        elif text in b'\x04':
            sys.exit(0)
        elif text in b'\x0c':
            pass
        else:
            continue
        break
