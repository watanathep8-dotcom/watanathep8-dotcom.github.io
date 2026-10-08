"""Builds one hub page per company from index.html (the all-companies page).
Run after editing index.html:  python tools/build-company-pages.py
  nap/index.html         -> บริษัท แน็ป นิวตริซายส์ จำกัด
  thepwatana/index.html  -> บริษัท เทพวัฒนา จำกัด
"""
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()

COMPANIES = [
    dict(dir='nap', gid='g-nap', name='บริษัท แน็ป นิวตริซายส์ จำกัด', short='แน็ป นิวตริซายส์',
         words=['บริหารพาเลท RM · PK · FG', 'ใบขออนุญาตปฏิบัติงาน'], systems='<b>Pallet Hub</b> · <b>e-Work Permit</b>'),
    dict(dir='thepwatana', gid='g-thep', name='บริษัท เทพวัฒนา จำกัด', short='เทพวัฒนา',
         words=['เอกสาร SDS สารเคมี', 'ใบขออนุญาตปฏิบัติงาน'], systems='<b>SDS Management</b> · <b>e-Work Permit</b>'),
]

def sub(s, pattern, repl, flags=re.S):
    out, n = re.subn(pattern, repl, s, count=1, flags=flags)
    assert n == 1, 'pattern not found: ' + pattern[:60]
    return out

groups = re.search(r'  <div class="groups">\n(.*?)\n  </div>\n\n  <footer>', src, re.S)
assert groups, 'groups block not found'
sections = re.findall(r'  <section class="group" aria-labelledby="(g-[a-z]+)">.*?\n  </section>', groups.group(1), re.S)

for c in COMPANIES:
    sec = re.search(r'  <section class="group" aria-labelledby="%s">.*?\n  </section>' % c['gid'], groups.group(1), re.S).group(0)
    sec = re.sub(r'<a class="g-link"[^>]*>.*?</a>', '', sec)  # no "company page" link on the company page itself
    n = len(re.findall(r'<a class="card', sec))
    p = src
    p = sub(p, r'<title>.*?</title>', '<title>%s · Operations Hub</title>' % c['short'])
    p = sub(p, r'<meta name="description" content="[^"]*">', '<meta name="description" content="ศูนย์รวมระบบงานของ %s">' % c['name'])
    p = sub(p, r'  <div class="groups">\n.*?\n  </div>\n\n  <footer>', '  <div class="solo">\n' + sec + '\n  </div>\n\n  <footer>')
    p = sub(p, r'<span class="badge"><i></i>[^<]*</span>', '<span class="badge"><i></i>%d ระบบพร้อมใช้งาน · ออนไลน์ 24 ชม.</span>' % n)
    p = sub(p, r'<h1>.*?</h1>', '<h1><span class="shine">ศูนย์รวมระบบงาน</span><br><span class="h1-co">%s</span></h1>' % c['name'])
    p = sub(p, r'<div>Operations Hub<small>ศูนย์รวมระบบงาน</small>', '<div>Operations Hub<small>%s</small>' % c['name'])
    p = sub(p, r'(<div class="clock")', r'<a class="back" href="../">← ทุกบริษัท</a>\n    \1')
    p = sub(p, r'<footer>.*?</footer>', '<footer>Operations Hub · %s · %s</footer>' % (c['name'], c['systems']))
    p = sub(p, r"const words = \[[^\]]*\];", 'const words = [%s];' % ', '.join("'%s'" % w for w in c['words']))
    p = sub(p, r'(  /\* one group per company \*/)', r'''  /* single-company page: bigger cards, centred */
  .solo .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); max-width: 860px; margin: 0 auto; }
  .solo .group-h { max-width: 860px; margin-left: auto; margin-right: auto; }
  .h1-co { font-size: .55em; font-weight: 700; color: var(--ink); }
  .back { font-family: 'Kanit', sans-serif; font-size: 14px; padding: 8px 14px; border: 1px solid var(--line); border-radius: 12px; background: rgba(255, 255, 255, .04); color: var(--muted); transition: color .2s, border-color .2s; margin-left: auto; }
  .back:hover { color: var(--ink); border-color: rgba(255, 255, 255, .25); }
  @media (max-width: 560px) { .solo .cards { grid-template-columns: 1fr; } }
\1''')
    p = p.replace('<!-- generated -->', '')
    p = p.replace('<html lang="th">', '<html lang="th">\n<!-- GENERATED from ../index.html by tools/build-company-pages.py — edit index.html, then re-run the script -->', 1)
    os.makedirs(os.path.join(ROOT, c['dir']), exist_ok=True)
    io.open(os.path.join(ROOT, c['dir'], 'index.html'), 'w', encoding='utf-8', newline='').write(p)
    print('built', c['dir'] + '/index.html', n, 'systems')
