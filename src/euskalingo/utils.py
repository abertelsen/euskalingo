import streamlit as st

def create_helptext(text: str, target: str):
    return '''
**{0}**  
{1}  
'''.format(to_canon(text), to_canon(target))

def match(text: str, target: str):

    # Words in parenthesis are optional, one may be present or not.
    # Words in square brackets are one among many, but one MUST be present.
    # The rest are mandatory

    # TODO Should interrogation marks be removed?

    split0 = target.strip().casefold().split()
    split1 = text.strip().casefold().split()

    i1 = 0
    for t0 in split0:

        if i1 >= len(split1):
            return False

        t1 = split1[i1]
        # TODO to lowercase, etc.

        if t0.startswith('('):
            t0 = t0.removeprefix('(').removesuffix(')')
            variants = t0.split(sep=',')
            # print('t1: {0}; variants: {1}'.format(t1, variants))

            if t1 in variants:
                i1 += 1
            continue 

        elif t0.startswith('[') or t0.startswith('<'):
            t0 = t0.removeprefix('[').removesuffix(']')
            t0 = t0.removeprefix('<').removesuffix('>')

            variants = t0.split(sep=',')
            # print('t1: {0}; variants: {1}'.format(t1, variants))

            if t1 not in variants:
                return False 
            else:
                i1 += 1
                continue

        else:  # exact match

            # print('t1: {0}; t0: {1}'.format(t1, t0))

            if not (t0 == t1):
                return False
            else:
                i1 += 1
                continue

    # Have we completed the target, but there are still words on the answer? Then, it is wrong.
    if i1 < len(split1):
        return False 
            
    return True

def to_blankfill(target):

    out = []
    keyword = None

    split0 = target.split()
    for t0 in split0:
        if t0.startswith('('):
            t0 = t0.removeprefix('(').removesuffix(')')
            out.append(t0.split(sep=',')[0])
        elif t0.startswith('['):
            t0 = t0.removeprefix('[').removesuffix(']')
            out.append(t0.split(sep=',')[0])
        elif t0.startswith('<'):
            t0 = t0.removeprefix('<').removesuffix('>')
            keyword = t0.split(sep=',')[0]
            out.append('_')
        else:
            out.append(t0)
            
    return ' '.join(out), keyword

def to_canon(target):

    # TODO Optional words could be printed in parenthesis, if requested.

    out = []

    split0 = target.split()
    for t0 in split0:
        if t0.startswith('('):
            t0 = t0.removeprefix('(').removesuffix(')')
            out.append(t0.split(sep=',')[0])
        elif t0.startswith('['):
            t0 = t0.removeprefix('[').removesuffix(']')
            out.append(t0.split(sep=',')[0])
        elif t0.startswith('<'):
            t0 = t0.removeprefix('<').removesuffix('>')
            out.append(t0.split(sep=',')[0])
        else:
            out.append(t0)
            
    return ' '.join(out)

def to_filename(phrase):
    return to_canon(phrase).lower().translate(str.maketrans(" ", "_", "\/:*?\"<>|¿¡!,;"))

def to_list(target):
    out = []

    split0 = target.split()
    for t0 in split0:
        if t0.startswith('('):
            t0 = t0.removeprefix('(').removesuffix(')')
            out += t0.split(sep=',')
        elif t0.startswith('['):
            t0 = t0.removeprefix('[').removesuffix(']')
            out += t0.split(sep=',')
        elif t0.startswith('<'):
            t0 = t0.removeprefix('<').removesuffix('>')
            out += t0.split(sep=',')
        else:
            out.append(t0)
            
    return out
