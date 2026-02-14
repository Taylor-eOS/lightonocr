import re
import sys

sup_map = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
sup_digit = r'[⁰¹²³⁴⁵⁶⁷⁸⁹]'
sup_run = re.compile(sup_digit + r'+')
wrapped_sup = re.compile(r'\$\^\{([⁰¹²³⁴⁵⁶⁷⁸⁹]+)\}\$')
footnote_line_start = re.compile(r'^\s*\$\^{(?:\d+|[⁰¹²³⁴⁵⁶⁷⁸⁹]+)\}')

def normalize_superscripts(text):
    def repl_wrapped(m):
        digits = ''.join(sup_map[ch] for ch in m.group(1))
        return f'$^{{{digits}}}$'
    text = wrapped_sup.sub(repl_wrapped, text)
    def repl(m):
        digits = ''.join(sup_map[ch] for ch in m.group(0))
        return f'$^{{{digits}}}$'
    return sup_run.sub(repl, text)

def remove_footnote_lines_from_text(text):
    lines = text.splitlines(keepends=True)
    out = []
    for line in lines:
        if not footnote_line_start.match(line):
            out.append(line)
    return ''.join(out)

def step_normalize_supers(text):
    return normalize_superscripts(text)

def step_remove_footnotes(text):
    return remove_footnote_lines_from_text(text)

PROCESSORS = [step_normalize_supers, step_remove_footnotes]

def run_pipeline(text, processors):
    for proc in processors:
        text = proc(text)
    return text

def build_output_name(name):
    dot = name.rfind('.')
    if dot == -1:
        return name + '_cleaned'
    return name[:dot] + '_cleaned' + name[dot:]

def read_file(path):
    with open(path, 'r', encoding = 'utf-8') as f:
        return f.read()

def write_file(path, data):
    with open(path, 'w', encoding = 'utf-8') as f:
        f.write(data)

def main():
    inp_name = input('Input file: ').strip() or 'input.txt'
    if not inp_name:
        sys.exit(1)
    text = read_file(inp_name)
    result = run_pipeline(text, PROCESSORS)
    out_name = build_output_name(inp_name)
    write_file(out_name, result)
    print('Finished. Output saved to', out_name)

if __name__ == '__main__':
    main()

