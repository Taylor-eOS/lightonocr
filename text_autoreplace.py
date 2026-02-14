import sys

sup_map = {'⁰':'0', '¹':'1', '²':'2', '³':'3', '⁴':'4', '⁵':'5', '⁶':'6', '⁷':'7', '⁸':'8', '⁹':'9'}

def convert_stream(inp, out):
    inside = False
    buffer = []
    while True:
        ch = inp.read(1)
        if not ch:
            break
        if inside:
            out.write(ch)
            if ch == '}':
                inside = False
            continue
        if ch == '$':
            nxt = inp.read(2)
            if nxt == '^{':
                out.write('$^{')
                inside = True
            else:
                out.write(ch)
                out.write(nxt)
            continue
        if ch in sup_map:
            buffer.append(sup_map[ch])
            while True:
                pos = inp.tell()
                nxt = inp.read(1)
                if nxt in sup_map:
                    buffer.append(sup_map[nxt])
                else:
                    inp.seek(pos)
                    break
            out.write('$^{' + ''.join(buffer) + '}$')
            buffer.clear()
        else:
            out.write(ch)

if __name__ == '__main__':
    inp_name = input('Input file: ').strip() or 'input.txt'
    if not inp_name:
        sys.exit(1)
    dot = inp_name.rfind('.')
    if dot == -1:
        out_name = inp_name + '_edited'
    else:
        out_name = inp_name[:dot] + '_edited' + inp_name[dot:]
    with open(inp_name, 'r', encoding = 'utf-8', errors = 'strict') as f, open(out_name, 'w', encoding = 'utf-8') as g:
        convert_stream(f, g)
    print('Finished process')

