"""Minimal KiCad s-expression reader/writer."""
import re

class Sym(str):
    """Bare symbol token (unquoted)."""
    pass

_tok = re.compile(r'\s*(?:(\()|(\))|"((?:[^"\\]|\\.)*)"|([^\s()"]+))', re.S)

def parse(text):
    pos = 0
    stack = [[]]
    n = len(text)
    while pos < n:
        m = _tok.match(text, pos)
        if not m:
            break
        pos = m.end()
        if m.group(1):
            stack.append([])
        elif m.group(2):
            lst = stack.pop()
            stack[-1].append(lst)
        elif m.group(3) is not None:
            stack[-1].append(m.group(3).replace('\\"', '"').replace('\\\\', '\\'))
        elif m.group(4) is not None:
            stack[-1].append(Sym(m.group(4)))
    return stack[0]

def q(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'

def atom(a):
    if isinstance(a, Sym):
        return str(a)
    if isinstance(a, bool):
        return 'yes' if a else 'no'
    if isinstance(a, int):
        return str(a)
    if isinstance(a, float):
        s = ('%.6f' % a).rstrip('0').rstrip('.')
        return s if s not in ('', '-0') else '0'
    return q(a)

def dump(node, indent=0):
    pad = '\t' * indent
    if not isinstance(node, list):
        return pad + atom(node)
    if not node:
        return pad + '()'
    # inline if all children are atoms
    if all(not isinstance(c, list) for c in node):
        return pad + '(' + ' '.join(atom(c) for c in node) + ')'
    head = []
    i = 0
    while i < len(node) and not isinstance(node[i], list):
        head.append(atom(node[i]))
        i += 1
    out = pad + '(' + ' '.join(head) + '\n'
    for c in node[i:]:
        out += dump(c, indent + 1) + '\n'
    out += pad + ')'
    return out

def find(node, key):
    for c in node:
        if isinstance(c, list) and c and c[0] == key:
            return c
    return None

def find_all(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]
