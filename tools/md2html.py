import re, sys, html

def inline(t):
    t = html.escape(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*([^*]+?)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', t)
    # ASCII only: \w also matches Hangul, which pulled particles like 으로 into the link.
    t = re.sub(r'([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})', r'<a href="mailto:\1">\1</a>', t)
    return t

def slug(s):
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'[^\w\s-]', '', s).strip().lower()
    return re.sub(r'[\s_]+', '-', s)

def convert(md, ids=None):
    """ids: optional {heading text: id} overrides, for anchors that must stay
    stable across languages (e.g. the app links terms.html#5a-usage-measurement)."""
    ids = ids or {}
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
        if ln.lstrip().startswith('>'):
            close()
            quote = []
            while i < len(lines) and lines[i].lstrip().startswith('>'):
                quote.append(lines[i].lstrip()[1:].strip()); i += 1
            out.append('<blockquote><p>' + inline(' '.join(quote)) + '</p></blockquote>')
            continue
        if ln.lstrip().startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|?[\s:|-]+\|?\s*$', lines[i + 1]) and '-' in lines[i + 1]:
            close()
            cells = lambda row: [c.strip() for c in row.strip().strip('|').split('|')]
            head = cells(ln)
            i += 2
            rows = []
            while i < len(lines) and lines[i].lstrip().startswith('|'):
                rows.append(cells(lines[i])); i += 1
            th = ''.join(f'<th scope="col">{inline(c)}</th>' for c in head)
            body = ''.join('<tr>' + ''.join(f'<td>{inline(c)}</td>' for c in r) + '</tr>' for r in rows)
            out.append(f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>')
            continue
        m = re.match(r'^(#{1,6})\s+(.*)$', ln)
        if m:
            close()
            lvl, raw = len(m.group(1)), m.group(2)
            txt = inline(raw)
            if lvl == 1:
                i += 1; continue  # title handled by page template
            plain = re.sub(r'\*\*|\*', '', raw).strip()
            sid = ids.get(plain) or slug(plain)
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
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#{1,6}\s|[-*]\s|---$|>|\|)', lines[i].strip()):
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
