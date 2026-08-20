import re, sys, html

def inline(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*]+?)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', t)
    t = re.sub(r'([\w.\-]+@[\w.\-]+\.\w+)', r'<a href="mailto:\1">\1</a>', t)
    return t

def slug(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'[^\w\s-]', '', s).strip().lower()
    return re.sub(r'[\s_]+', '-', s)

def convert(md):
    lines = md.split('\n')
    out, toc = [], []
    i, in_list = 0, False
    def close():
        nonlocal in_list
        if in_list:
            out.append('</ul>')
            in_list = False
    while i < len(lines):
        ln = lines[i].rstrip()
        if not ln.strip():
            close(); i += 1; continue
        if ln.strip() == '---':
            close(); out.append('<hr>'); i += 1; continue
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            close()
            lvl, raw = len(m.group(1)), m.group(2)
            txt = inline(raw)
            if lvl == 1:
                i += 1; continue  # title handled by page template
            sid = slug(re.sub(r'\*\*|\*', '', raw))
            if lvl == 2:
                toc.append((sid, inline(re.sub(r'\*\*|\*', '', raw))))
            out.append(f'<h{lvl} id="{sid}">{txt}</h{lvl}>')
            i += 1; continue
        m = re.match(r'^[-*]\s+(.*)$', ln)
        if m:
            if not in_list:
                out.append('<ul>'); in_list = True
            item = [m.group(1)]
            i += 1
            while i < len(lines) and re.match(r'^\s{2,}\S', lines[i]):
                item.append(lines[i].strip()); i += 1
            out.append('<li>' + inline(' '.join(item)) + '</li>')
            continue
        close()
        para = [ln.strip()]
        i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6}\s|[-*]\s|---$)', lines[i].strip()):
            para.append(lines[i].strip()); i += 1
        text = ' '.join(para)
        if text.startswith('*') and text.endswith('*') and not text.startswith('**'):
            out.append('<p class="note">' + inline(text[1:-1]) + '</p>')
        elif re.match(r'^\*\*Last updated:\*\*', text):
            out.append('<p class="updated">' + inline(text) + '</p>')
        else:
            out.append('<p>' + inline(text) + '</p>')
    close()
    return '\n'.join(out), toc
