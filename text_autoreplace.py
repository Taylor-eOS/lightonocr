import sys

sup_map = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
sup_digit = r'[⁰¹²³⁴⁵⁶⁷⁸⁹]'

def compile_pattern(pattern):
    import re
    return re.compile(pattern)

sup_run = compile_pattern(sup_digit + r'+')
wrapped_sup = compile_pattern(r'\$\^\{([⁰¹²³⁴⁵⁶⁷⁸⁹]+)\}\$')
footnote_line_start = compile_pattern(r'^\s*\$\^{(?:\d+|[⁰¹²³⁴⁵⁶⁷⁸⁹]+)\}')

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

AVAILABLE_PROCESSORS = [
    ('Normalize superscripts', step_normalize_supers),
    ('Remove footnote lines', step_remove_footnotes),
]

def select_processors(available):
    print('\nAvailable processors:')
    for i, (name, _) in enumerate(available, 1):
        print(f'  {i}. {name}')
    print('\nEnter processor numbers separated by spaces (e.g., "1 2")')
    print('Or press Enter to select all:')
    choice = input('> ').strip()
    if not choice:
        return [proc for _, proc in available]
    selected = []
    for part in choice.split():
        try:
            idx = int(part) - 1
            if 0 <= idx < len(available):
                selected.append(available[idx][1])
        except ValueError:
            pass
    return selected

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
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(data)

def main():
    inp_name = input('Input file: ').strip() or 'input.txt'
    if not inp_name:
        sys.exit(1)
    processors = select_processors(AVAILABLE_PROCESSORS)
    if not processors:
        print('No processors selected. Exiting.')
        sys.exit(0)
    text = read_file(inp_name)
    result = run_pipeline(text, processors)
    out_name = build_output_name(inp_name)
    write_file(out_name, result)
    print('Finished. Output saved to', out_name)

if __name__ == '__main__':
    main()
