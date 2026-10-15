"""Builds the site from tools/hub-template.html (all systems, grouped by company).
Run after editing the template:  python tools/build-company-pages.py
  index.html             -> หน้าเลือกบริษัท (2 ปุ่มใหญ่)
  nap/index.html         -> บริษัท แน็ป นิวตริซายส์ จำกัด
  thepwatana/index.html  -> บริษัท เทพวัฒนา จำกัด
"""
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = io.open(os.path.join(ROOT, 'tools', 'hub-template.html'), encoding='utf-8').read()
STAMP = '<!-- GENERATED from tools/hub-template.html by tools/build-company-pages.py — edit the template, then re-run the script -->'

COMPANIES = [
    dict(dir='nap', gid='g-nap', icon='🏭', cls='', name='บริษัท แน็ป นิวตริซายส์ จำกัด', short='แน็ป นิวตริซายส์', sub='Nap Nutriscience',
         words=['บริหารพาเลท RM · PK · FG', 'ใบขออนุญาตปฏิบัติงาน', 'บริหารจัดการของเสีย'],
         chips=['Pallet Hub', 'e-Work Permit', 'Balance Waste']),
    dict(dir='thepwatana', gid='g-thep', icon='🏢', cls=' c-blue', name='บริษัท เทพวัฒนา จำกัด', short='เทพวัฒนา', sub='Thepwatana',
         words=['เอกสาร SDS สารเคมี', 'ใบขออนุญาตปฏิบัติงาน', 'บริหารจัดการของเสีย'],
         chips=['SDS Management', 'e-Work Permit', 'Balance Waste']),
]


def sub(s, pattern, repl, flags=re.S):
    out, n = re.subn(pattern, lambda m: m.expand(repl) if '\\' in repl else repl, s, count=1, flags=flags)
    assert n == 1, 'pattern not found: ' + pattern[:60]
    return out


def css(s, block):
    return sub(s, r'(  /\* one group per company \*/)', block + r'\1')


groups = re.search(r'  <div class="groups">\n(.*?)\n  </div>\n\n  <footer>', src, re.S)
assert groups, 'groups block not found'

SOLO_CSS = '''  /* single-company page: bigger cards, centred */
  .solo .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); max-width: 860px; margin: 0 auto; }
  .solo .group-h { max-width: 860px; margin-left: auto; margin-right: auto; }
  .h1-co { font-size: .55em; font-weight: 700; color: var(--ink); }
  .back { font-family: 'Kanit', sans-serif; font-size: 14px; padding: 8px 14px; border: 1px solid var(--line); border-radius: 12px; background: rgba(255, 255, 255, .04); color: var(--muted); transition: color .2s, border-color .2s; margin-left: auto; }
  .back:hover { color: var(--ink); border-color: rgba(255, 255, 255, .25); }
  @media (max-width: 560px) { .solo .cards { grid-template-columns: 1fr; } }
'''

# ---------------------------------------------------------------- one page per company
for c in COMPANIES:
    sec = re.search(r'  <section class="group" aria-labelledby="%s">.*?\n  </section>' % c['gid'], groups.group(1), re.S).group(0)
    sec = re.sub(r'<a class="g-link"[^>]*>.*?</a>', '', sec)
    n = len(re.findall(r'<a class="card', sec))
    p = src
    p = sub(p, r'<title>.*?</title>', '<title>%s · Operations Hub</title>' % c['short'])
    p = sub(p, r'<meta name="description" content="[^"]*">', '<meta name="description" content="ศูนย์รวมระบบงานของ %s">' % c['name'])
    p = sub(p, r'  <div class="groups">\n.*?\n  </div>\n\n  <footer>', '  <div class="solo">\n' + sec + '\n  </div>\n\n  <footer>')
    p = sub(p, r'<span class="badge"><i></i>[^<]*</span>', '<span class="badge"><i></i>%d ระบบพร้อมใช้งาน · ออนไลน์ 24 ชม.</span>' % n)
    p = sub(p, r'<h1>.*?</h1>', '<h1><span class="shine">ศูนย์รวมระบบงาน</span><br><span class="h1-co">%s</span></h1>' % c['name'])
    p = sub(p, r'<div>Operations Hub<small>ศูนย์รวมระบบงาน</small>', '<div>Operations Hub<small>%s</small>' % c['name'])
    p = p.replace('<div class="clock"', '<a class="back" href="../">← เลือกบริษัท</a>\n    <div class="clock"', 1)
    p = sub(p, r'<footer>.*?</footer>', '<footer>Operations Hub · %s · %s</footer>' % (c['name'], ' · '.join('<b>%s</b>' % x for x in c['chips'])))
    p = sub(p, r"const words = \[[^\]]*\];", 'const words = [%s];' % ', '.join("'%s'" % w for w in c['words']))
    p = p.replace('  /* one group per company */', SOLO_CSS + '  /* one group per company */', 1)
    p = p.replace('<html lang="th">', '<html lang="th">\n' + STAMP, 1)
    os.makedirs(os.path.join(ROOT, c['dir']), exist_ok=True)
    io.open(os.path.join(ROOT, c['dir'], 'index.html'), 'w', encoding='utf-8', newline='').write(p)
    print('built', c['dir'] + '/index.html', n, 'systems')

# ---------------------------------------------------------------- index.html: company chooser
CARD = '''    <a class="card co-card{cls}" href="{dir}/" data-name="{name}" aria-label="เข้าสู่ระบบงานของ {name}">
      <div class="inner">
        <div class="glow-blob"></div>
        <div class="co-ic"><span>{icon}</span></div>
        <h2><small>{sub}</small>{name}</h2>
        <p class="desc">{n} ระบบงานของบริษัท</p>
        <div class="chips">{chips}</div>
        <div class="go"><span>เข้าสู่ระบบงานของบริษัท</span><span class="arrow">&#10140;</span></div>
      </div>
    </a>'''
cards = '\n'.join(CARD.format(cls=c['cls'], dir=c['dir'], name=c['name'], icon=c['icon'], sub=c['sub'], n=len(c['chips']),
                              chips=''.join('<span>%s</span>' % x for x in c['chips'])) for c in COMPANIES)
CHOOSER_CSS = '''  /* company chooser: two big cards */
  .co-pick { grid-template-columns: repeat(2, minmax(0, 1fr)); max-width: 900px; margin: 0 auto; width: 100%; }
  .co-card .inner { padding: 34px 32px 28px; }
  .co-ic { width: 104px; height: 104px; border-radius: 30px; display: grid; place-items: center; font-size: 52px; position: relative; transform: translateZ(60px);
    background: color-mix(in srgb, var(--c) 16%, transparent); border: 1px solid color-mix(in srgb, var(--c) 45%, transparent);
    box-shadow: inset 0 0 30px color-mix(in srgb, var(--c) 25%, transparent), 0 10px 40px -10px var(--c); }
  .co-ic::before { content: ""; position: absolute; inset: -12px; border-radius: 50%; border: 1px dashed color-mix(in srgb, var(--c2) 50%, transparent); animation: spin 14s linear infinite; }
  .co-ic span { display: inline-block; animation: float 4.5s ease-in-out infinite; }
  .co-card h2 { font-size: 26px; }
  @media (max-width: 760px) { .co-pick { grid-template-columns: 1fr; max-width: 520px; } }
'''
p = src
p = sub(p, r'  <div class="groups">\n.*?\n  </div>\n\n  <footer>', '  <div class="cards co-pick">\n' + cards + '\n  </div>\n\n  <footer>')
p = sub(p, r'<span class="badge"><i></i>[^<]*</span>', '<span class="badge"><i></i>2 บริษัท · ออนไลน์ 24 ชม.</span>')
p = sub(p, r'<h1>.*?</h1>', '<h1><span class="shine">ศูนย์รวมระบบงาน</span><br>เลือกบริษัท</h1>')
p = sub(p, r'<p>เลือกระบบที่ต้องการ — ', '<p>เลือกบริษัทของคุณ — ')
p = sub(p, r"const words = \[[^\]]*\];", "const words = ['บริษัท แน็ป นิวตริซายส์ จำกัด', 'บริษัท เทพวัฒนา จำกัด'];")
p = sub(p, r'<footer>.*?</footer>', '<footer>Operations Hub · ' + ' · '.join('<b>%s</b>' % c['name'] for c in COMPANIES) + '</footer>')
p = p.replace('  /* one group per company */', CHOOSER_CSS + '  /* one group per company */', 1)
p = p.replace('<html lang="th">', '<html lang="th">\n' + STAMP, 1)
io.open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8', newline='').write(p)
print('built index.html (company chooser)')
