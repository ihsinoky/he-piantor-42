"""Minimal s-expr parser/serializer for KiCad text files."""
import re

def tokenize(text):
    toks, i, n = [], 0, len(text)
    while i < n:
        c = text[i]
        if c in ' \t\r\n':
            i += 1
        elif c == '(' or c == ')':
            toks.append(c); i += 1
        elif c == '"':
            j = i + 1; buf = ''
            while j < n:
                if text[j] == '\\':
                    buf += text[j:j+2]; j += 2
                elif text[j] == '"':
                    break
                else:
                    buf += text[j]; j += 1
            toks.append(('str', buf)); i = j + 1
        else:
            j = i
            while j < n and text[j] not in ' \t\r\n()':
                j += 1
            toks.append(text[i:j]); i = j
    return toks

def parse(text):
    toks = tokenize(text)
    pos = 0
    def rec():
        nonlocal pos
        t = toks[pos]
        if t == '(':
            pos += 1
            out = []
            while toks[pos] != ')':
                out.append(rec())
            pos += 1
            return out
        pos += 1
        return t
    return rec()

def ser(node, depth=0):
    if isinstance(node, tuple):
        return '"' + node[1] + '"'
    if isinstance(node, list):
        if not node:
            return '()'
        head = node[0]
        if all(not isinstance(x, list) for x in node) and len(node) <= 8:
            return '(' + ' '.join(ser(x) for x in node) + ')'
        inner = '\n'.join('\t' * (depth + 1) + ser(x, depth + 1) for x in node[1:])
        return '(' + ser(head) + '\n' + inner + '\n' + '\t' * depth + ')'
    return str(node)

def is_str(node):
    return isinstance(node, tuple)

def atom(node):
    return node[1] if isinstance(node, tuple) else node
