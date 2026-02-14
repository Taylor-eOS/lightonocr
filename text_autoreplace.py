import re
import sys

sup_map = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9'}

sup_digit = r'[⁰¹²³⁴⁵⁶⁷⁸⁹]'
sup_run = re.compile(sup_digit + r'+')
wrapped_sup = re.compile(r'\$\^\{([⁰¹²³⁴⁵⁶⁷⁸⁹]+)\}\$')

def normalize_superscripts(text):
    def repl_wrapped(m):
        digits=''.join(sup_map[ch] for ch in m.group(1))
        return f'$^{{{digits}}}$'
    text=wrapped_sup.sub(repl_wrapped,text)
    def repl(m):
        digits=''.join(sup_map[ch] for ch in m.group(0))
        return f'$^{{{digits}}}$'
    return sup_run.sub(repl,text)

footnote_line_start = re.compile(
    r'^\s*'
    r'\$\^{'
    r'(?:\d+|'
    r'[⁰¹²³⁴⁵⁶⁷⁸⁹]+'
    r')'
    r'\}'
)

def remove_footnote_lines(lines):
    result=[]
    for line in lines:
        if footnote_line_start.match(line):
            continue
        result.append(line)
    return result

if __name__=='__main__':
    inp_name=input('Input file: ').strip() or 'input.txt'
    if not inp_name:
        sys.exit(1)
    remove_choice=input('Remove lines that start with a footnote marker? (y/n): ').strip().lower()
    remove=remove_choice.startswith('y')
    dot=inp_name.rfind('.')
    out_name=inp_name[:dot]+'_cleaned'+inp_name[dot:] if dot!=-1 else inp_name+'_cleaned'
    with open(inp_name,'r',encoding='utf-8') as f:
        full_text=f.read()
    normalized=normalize_superscripts(full_text)
    if remove:
        lines=normalized.splitlines(keepends=True)
        cleaned_lines=remove_footnote_lines(lines)
        output_text=''.join(cleaned_lines)
    else:
        output_text=normalized
    with open(out_name,'w',encoding='utf-8') as g:
        g.write(output_text)
    print('Finished. Output saved to',out_name)

