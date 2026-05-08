#!/usr/bin/env python3
"""
genera_scheda.py — Genera una scheda palestra HTML mobile da un PDF.

Uso:
    python3 genera_scheda.py <file.pdf> [output.html]

Il PDF deve contenere una tabella con colonne:
    Esercizio | N colonne programma (es. Prog A, Prog B, ...) | Link

Richiede: pdfplumber
    pip install pdfplumber --break-system-packages
"""

import sys
import re
import json
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("❌  Installa pdfplumber: pip install pdfplumber --break-system-packages")
    sys.exit(1)


# ── Helpers ────────────────────────────────────────────────────────────────────

def slugify(text):
    text = text.lower().strip()
    for a, b in [('à','a'),('á','a'),('è','e'),('é','e'),('ì','i'),('í','i'),
                 ('ò','o'),('ó','o'),('ù','u'),('ú','u')]:
        text = text.replace(a, b)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:35]


def parse_params(s):
    """Parsa una stringa parametri (es. '3 serie x 10 60%') in lista di badge (tipo, testo)."""
    if not s or not s.strip():
        return []
    s = s.strip()

    # "X" da solo = esercizio presente senza parametri specificati
    if re.fullmatch(r'x', s, re.IGNORECASE):
        return [('series', '✓')]

    badges = []

    # ── Special early-exit patterns ─────────────────────────────────────────
    if re.search(r'elastic\s*band', s, re.IGNORECASE):
        m = re.search(r'[x×]\s*(\d+)', s)
        badges.append(('series', f'Elastic band{" × " + m.group(1) if m else ""}'))
        return badges

    if re.search(r'sfinimento', s, re.IGNORECASE):
        m2 = re.search(r'[x×]\s*(\d+)', s)
        if m2:
            badges.append(('series', f'× {m2.group(1)} serie'))
        badges.append(('load', 'a sfinimento'))
        return badges

    if re.search(r'\bAMRAP\b', s, re.IGNORECASE):
        m = re.search(r'(\d+)\s*min', s, re.IGNORECASE)
        badges.append(('series', f'AMRAP{" " + m.group(1) + "min" if m else ""}'))
        return badges

    if re.search(r'\bEMOM\b', s, re.IGNORECASE):
        m = re.search(r'(\d+)', s)
        badges.append(('series', f'EMOM{" " + m.group(1) + "min" if m else ""}'))
        return badges

    # ── Serie × Ripetizioni ──────────────────────────────────────────────────
    # "M rip x N serie" (invertito)
    m_inv = re.search(r'(\d+)\s*(?:rip(?:etizioni?)?|rep(?:s|etitions?)?)\s*[xX×]\s*(\d+)\s*(?:serie|set|sets?)', s, re.IGNORECASE)
    if m_inv:
        badges.append(('series', f'{m_inv.group(2)} serie × {m_inv.group(1)}'))
    else:
        # "NxM", "N serie x M", "N+NxM" (bilaterale es. "8+8x4")
        m_ser = re.search(r'(\d+(?:\+\d+)?)\s*(?:serie|set|sets?)?\s*[xX×]\s*(\d+)', s, re.IGNORECASE)
        if m_ser:
            raw_a = m_ser.group(1)
            b = int(m_ser.group(2))
            a = int(raw_a.split('+')[0])
            bilateral = raw_a if '+' in raw_a else None
            series, rips_num = (a, b) if a <= b else (b, a)
            rips_label = bilateral if bilateral else str(rips_num)
            badges.append(('series', f'{series} serie × {rips_label}'))
        else:
            # Solo serie
            m_only_ser = re.search(r'(\d+)\s*(?:serie|set|sets?)\b', s, re.IGNORECASE)
            if m_only_ser:
                badges.append(('series', f'{m_only_ser.group(1)} serie'))
            # Solo ripetizioni
            m_only_rep = re.search(r'(\d+)\s*(?:rip(?:etizioni?)?|rep(?:s|etitions?)?)\b', s, re.IGNORECASE)
            if m_only_rep:
                badges.append(('series', f'× {m_only_rep.group(1)} rip'))

    # ── Recupero ─────────────────────────────────────────────────────────────
    m_minsec = re.search(r"(\d+)\s*(?:min(?:uto?)?|')\s*[:\s]?\s*(\d+)\s*(?:s(?:ec(?:ondi?)?)?|[\u201d\u2019\"'])", s, re.IGNORECASE)
    if m_minsec:
        badges.append(('rest', f'⏱ {m_minsec.group(1)}\'{m_minsec.group(2).zfill(2)}"'))
    else:
        m_min = re.search(r"(?:^|[\s\bR])(\d+)\s*(?:min(?:ut[oi]?)?|minut[oi]|')\s*$", s, re.IGNORECASE)
        if m_min:
            badges.append(('rest', f"⏱ {m_min.group(1)}'00\""))
        else:
            m_sec = re.search(r"R?(\d+)\s*(?:[\u201d\u2019\"]|s(?:ec(?:ondi?)?)?(?:\b|$))", s, re.IGNORECASE)
            if m_sec:
                badges.append(('rest', f'⏱ {m_sec.group(1)}"'))

    # ── Carico ───────────────────────────────────────────────────────────────
    m_pct  = re.search(r'(\d+(?:\.\d+)?)\s*%', s)
    m_bw   = re.search(r'\b(?:BW|peso\s+corporeo|bodyweight)\b', s, re.IGNORECASE)
    m_kg   = re.search(r'(\d+(?:\.\d+)?)\s*kg', s, re.IGNORECASE)
    m_lbs  = re.search(r'(\d+(?:\.\d+)?)\s*lb(?:s|bs?)?\b', s, re.IGNORECASE)
    m_rpe  = re.search(r'\bRPE\s*(\d+(?:\.\d+)?)', s, re.IGNORECASE)
    m_rir  = re.search(r'\bRIR\s*(\d+)', s, re.IGNORECASE)

    if m_pct:
        badges.append(('load', f'{m_pct.group(1)}%'))
    elif m_bw:
        badges.append(('load', 'BW'))
    elif m_kg:
        badges.append(('load', f'{m_kg.group(1)} kg'))
    elif m_lbs:
        badges.append(('load', f'{m_lbs.group(1)} lbs'))

    if m_rpe:
        badges.append(('load', f'RPE {m_rpe.group(1)}'))
    if m_rir:
        badges.append(('load', f'RIR {m_rir.group(1)}'))

    if not badges:
        badges.append(('series', s))

    return badges


SECTION_COLORS = {
    'warmup': '#f59e0b',
    'lower':  '#3b82f6',
    'upper':  '#8b5cf6',
    'misc':   '#10b981',
}

def section_type(name):
    n = name.lower()
    if 'warm' in n or 'riscaldamento' in n:
        return 'warmup'
    if any(k in n for k in ('inferior', 'basso', 'gamb', 'quad', 'squat', 'leg')):
        return 'lower'
    if any(k in n for k in ('superior', 'alto', 'petto', 'schiena', 'spalle', 'braccia')):
        return 'upper'
    return 'misc'


# ── PDF Parsing ────────────────────────────────────────────────────────────────

def parse_pdf(pdf_path):
    """
    Ritorna:
      meta       — dict con 'title' e 'weeks'
      programs   — dict {key: [...sezioni...]} con chiavi dinamiche (a, b, c, ...)
        ogni sezione: {'section': str, 'stype': str, 'exercises': [...]}
        ogni esercizio: {'id': str, 'name': str, 'params': str, 'link': str}
      prog_keys  — list of program keys (e.g. ['a', 'b', 'c'])
      prog_labels — list of display labels (e.g. ['A', 'B', 'C'])
    """
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text() or ''
        tables = page.extract_tables()

    # Metadati
    weeks_match = re.search(r'Settimana\s+n[°.]?\s*[\d\-–]+', text, re.IGNORECASE)
    weeks = weeks_match.group(0).strip() if weeks_match else ''
    title = Path(pdf_path).stem

    if not tables:
        raise ValueError("Nessuna tabella trovata nel PDF. Assicurati che il PDF abbia una tabella strutturata.")

    table = tables[0]

    # Trova la riga di intestazione
    header_idx = 0
    for i, row in enumerate(table):
        if row and any(c and 'esercizio' in str(c).lower() for c in row):
            header_idx = i
            break

    header_row = table[header_idx]

    rows = table[header_idx + 1:]

    # Detect link column: by header keyword OR by presence of URLs in last column cells
    last_header = str(header_row[-1] or '') if len(header_row) > 1 else ''
    header_says_link = bool(re.search(r'link|video|youtube|youtu|url', last_header, re.IGNORECASE))
    last_col_idx = len(header_row) - 1
    last_col_has_urls = any(re.match(r'https?://', str(r[last_col_idx] if last_col_idx < len(r) else '').strip()) for r in rows)
    last_col_is_link = len(header_row) > 1 and (header_says_link or last_col_has_urls)
    prog_col_count = len(header_row) - 1 - (1 if last_col_is_link else 0)
    keys = 'abcdefghijklmnopqrstuvwxyz'
    prog_keys = list(keys[:prog_col_count])

    # Extract display labels from header
    label_cols = header_row[1:-1] if last_col_is_link else header_row[1:]
    prog_labels = []
    for i, col in enumerate(label_cols):
        lbl = str(col or '')
        m = re.search(r'(?:prog(?:ramma?)?\s*)?([A-Z0-9]+)\s*$', lbl, re.IGNORECASE)
        prog_labels.append(m.group(1).upper() if m else keys[i].upper())

    programs = {k: [] for k in prog_keys}
    current_section = {'name': 'Generale', 'type': 'misc'}
    id_counter = {}

    def make_id(prog, name):
        slug = f"{prog}-{slugify(name)}"
        id_counter[slug] = id_counter.get(slug, 0) + 1
        if id_counter[slug] > 1:
            slug = f"{slug}-{id_counter[slug]}"
        return slug

    def get_or_create_section(prog_key):
        """Restituisce la sezione corrente per il programma, creandola se necessario."""
        if not programs[prog_key] or programs[prog_key][-1]['section'] != current_section['name']:
            programs[prog_key].append({
                'section':   current_section['name'],
                'stype':     current_section['type'],
                'exercises': []
            })
        return programs[prog_key][-1]

    for row in rows:
        if not row or all(c is None or str(c).strip() == '' for c in row):
            continue

        name = str(row[0] or '').strip()
        prog_vals = [str(row[i+1] or '').strip() if len(row) > i+1 else '' for i in range(len(prog_keys))]
        link_idx = len(prog_keys) + 1 if last_col_is_link else -1
        link = str(row[link_idx] or '').strip() if link_idx >= 0 and len(row) > link_idx else ''

        # Riga sezione: col[0] vuota, col[1] ha il nome, col[2] è None
        if not name and prog_vals and prog_vals[0] and (len(row) < 3 or row[2] is None or str(row[2]).strip() == ''):
            current_section = {'name': prog_vals[0], 'type': section_type(prog_vals[0])}
            continue

        if not name:
            continue

        # Riga esercizio
        for i, (prog_key, val) in enumerate(zip(prog_keys, prog_vals)):
            if val:
                sec = get_or_create_section(prog_key)
                sec['exercises'].append({
                    'id':     make_id(prog_key, name),
                    'name':   name,
                    'params': val,
                    'link':   link
                })

    return {'title': title, 'weeks': weeks}, programs, prog_keys, prog_labels


# ── HTML Generation ────────────────────────────────────────────────────────────

def render_badges(params_str):
    badges = parse_params(params_str)
    if not badges:
        return ''
    parts = ''.join(f'<span class="badge {t}">{txt}</span>' for t, txt in badges)
    return f'<div class="badges">{parts}</div>'


def render_exercise_card(ex, stype):
    yt_btn = ''
    if ex['link'] and ex['link'].startswith('http'):
        url = ex['link'].replace('"', '&quot;')
        yt_btn = f'<a class="yt-btn" href="{url}" target="_blank">▶ Video</a>'

    badges_html = render_badges(ex['params'])
    name_esc = ex['name'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    ex_id = ex['id']

    return f'''  <div class="card {stype}" id="{ex_id}">
    <div class="card-top">
      <span class="exercise-name">{name_esc}</span>
      {yt_btn}
    </div>
    {badges_html}
    <div class="note-label">📝 Note / Peso usato</div>
    <textarea class="note-input" rows="1" placeholder="es. peso, note…" oninput="saveNote('{ex_id}',this.value)"></textarea>
  </div>'''


def render_program_panel(prog_key, sections):
    html = f'\n<div class="panel" id="panel-{prog_key}">\n'
    for sec in sections:
        if not sec['exercises']:
            continue
        stype = sec['stype']
        color = SECTION_COLORS.get(stype, '#6b7280')
        sec_name = sec['section'].replace('&', '&amp;').replace('<', '&lt;')
        html += f'''
  <div class="section-header">
    <div class="section-dot" style="background:{color}"></div>
    <h2>{sec_name}</h2>
  </div>\n'''
        for ex in sec['exercises']:
            html += render_exercise_card(ex, stype) + '\n'
    html += f'</div><!-- /panel-{prog_key} -->\n'
    return html


def build_ex_names_js(programs):
    all_ex = {}
    for sections in programs.values():
        for sec in sections:
            for ex in sec['exercises']:
                all_ex[ex['id']] = ex['name']
    return json.dumps(all_ex, ensure_ascii=False)


TAB_COLORS    = ['#60a5fa','#4ade80','#f87171','#fb923c','#a78bfa','#34d399','#f472b6','#38bdf8']
ACCENT_COLORS = ['#2563eb','#16a34a','#dc2626','#ea580c','#7c3aed','#059669','#db2777','#0284c7']


def generate_dynamic_css(prog_keys):
    tab_css = ''.join(
        f'.tab-btn.active-{k}{{color:white;border-color:{TAB_COLORS[i % len(TAB_COLORS)]}}}'
        for i, k in enumerate(prog_keys)
    ) + '.tab-btn.active-storico{color:white;border-color:#f59e0b}'
    badge_css = ''.join(
        f'.prog-badge.{k}{{background:{ACCENT_COLORS[i % len(ACCENT_COLORS)]}}}'
        for i, k in enumerate(prog_keys)
    )
    return tab_css + badge_css


CSS = """
  :root {{
    --bg:#f5f5f5;--card:#fff;--primary:#1e3a5f;
    --text:#1a1a1a;--muted:#6b7280;--border:#e5e7eb;
    --warmup:#f59e0b;--lower:#3b82f6;--upper:#8b5cf6;--misc:#10b981;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}}
  header{{background:var(--primary);color:white;padding:16px 16px 0;position:sticky;top:0;z-index:100;box-shadow:0 2px 8px rgba(0,0,0,.2)}}
  header h1{{font-size:1.1rem;font-weight:700;letter-spacing:.5px}}
  header p{{font-size:.8rem;opacity:.75;margin-top:2px}}
  .tabs{{display:flex;margin-top:12px;gap:4px}}
  .tab-btn{{flex:1;padding:10px 6px;background:transparent;border:none;color:rgba(255,255,255,.65);font-size:.82rem;font-weight:600;cursor:pointer;border-bottom:3px solid transparent;transition:all .2s}}
  {{dyn_css}}
  .panel{{display:none;padding:12px 12px 80px}}
  .panel.active{{display:block}}
  .section-header{{display:flex;align-items:center;gap:8px;margin:18px 0 10px}}
  .section-dot{{width:10px;height:10px;border-radius:50%;flex-shrink:0}}
  .section-header h2{{font-size:.85rem;text-transform:uppercase;letter-spacing:.8px;font-weight:700;color:var(--muted)}}
  .card{{background:var(--card);border-radius:12px;padding:14px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,.07);border-left:4px solid var(--border)}}
  .card.warmup{{border-left-color:var(--warmup)}} .card.lower{{border-left-color:var(--lower)}}
  .card.upper{{border-left-color:var(--upper)}}   .card.misc{{border-left-color:var(--misc)}}
  .card-top{{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}}
  .exercise-name{{font-size:.95rem;font-weight:600;line-height:1.3;flex:1}}
  .yt-btn{{background:#f00;color:white;border:none;border-radius:6px;padding:5px 8px;font-size:.75rem;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:3px;flex-shrink:0;font-weight:600}}
  .badges{{display:flex;flex-wrap:wrap;gap:5px;margin:8px 0}}
  .badge{{background:#f3f4f6;border-radius:6px;padding:3px 8px;font-size:.75rem;font-weight:500;border:1px solid var(--border)}}
  .badge.series{{background:#eff6ff;border-color:#bfdbfe;color:#1d4ed8}}
  .badge.rest{{background:#fef3c7;border-color:#fde68a;color:#92400e}}
  .badge.load{{background:#f0fdf4;border-color:#bbf7d0;color:#15803d}}
  .note-label{{font-size:.72rem;color:var(--muted);margin-top:10px;margin-bottom:4px;font-weight:500}}
  .note-input{{width:100%;border:1px solid var(--border);border-radius:8px;padding:8px 10px;font-size:.85rem;background:#fafafa;color:var(--text);resize:none;font-family:inherit;transition:border-color .2s;min-height:38px}}
  .note-input:focus{{outline:none;border-color:#93c5fd;background:white}}
  .footer-bar{{position:fixed;bottom:0;left:0;right:0;background:white;border-top:1px solid var(--border);padding:10px 16px;display:flex;justify-content:space-between;align-items:center;z-index:99;gap:8px}}
  .footer-bar small{{font-size:.7rem;color:var(--muted);flex:1}}
  .save-btn{{background:#16a34a;color:white;border:none;border-radius:8px;padding:8px 14px;font-size:.82rem;font-weight:700;cursor:pointer}}
  .save-btn:active{{background:#15803d}}
  .reset-btn{{background:transparent;border:1px solid #fca5a5;color:#dc2626;padding:6px 12px;border-radius:8px;font-size:.78rem;cursor:pointer;font-weight:500}}
  .reset-btn:active{{background:#fee2e2}}
  .saved-dot{{width:7px;height:7px;border-radius:50%;background:#d1d5db;transition:background .4s;display:inline-block;margin-left:6px}}
  .saved-dot.saved{{background:#22c55e}}
  #panel-storico{{padding:12px 12px 80px}}
  .storico-empty{{text-align:center;color:var(--muted);padding:60px 20px;font-size:.9rem}}
  .session-card{{background:var(--card);border-radius:12px;margin-bottom:10px;box-shadow:0 1px 4px rgba(0,0,0,.07);overflow:hidden}}
  .session-header{{display:flex;align-items:center;justify-content:space-between;padding:12px 14px;cursor:pointer;user-select:none;gap:8px}}
  .session-header:active{{background:#f9fafb}}
  .session-meta{{flex:1}}
  .session-date{{font-size:.9rem;font-weight:700}}
  .session-sub{{font-size:.75rem;color:var(--muted);margin-top:2px}}
  .prog-badge{{border-radius:6px;padding:3px 10px;font-size:.78rem;font-weight:700;color:white}}
  {{dyn_badge_css}}
  .chevron{{font-size:.8rem;color:var(--muted);transition:transform .2s}}.chevron.open{{transform:rotate(180deg)}}
  .session-body{{display:none;border-top:1px solid var(--border);padding:10px 14px 14px}}.session-body.open{{display:block}}
  .session-ex{{padding:7px 0;border-bottom:1px solid #f3f4f6}}
  .session-ex:last-child{{border-bottom:none}}
  .session-ex-name{{font-size:.82rem;font-weight:600}}.session-ex-note{{font-size:.8rem;color:var(--muted);margin-top:2px}}
  .del-session-btn{{background:transparent;border:none;font-size:1rem;cursor:pointer;padding:2px 4px;color:#9ca3af}}
  .modal-overlay{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.5);z-index:200;align-items:flex-end}}.modal-overlay.open{{display:flex}}
  .modal-sheet{{background:white;border-radius:18px 18px 0 0;width:100%;max-height:80vh;overflow-y:auto;padding:20px 16px 40px}}
  .modal-title{{font-size:1rem;font-weight:700;margin-bottom:4px}}.modal-close{{float:right;background:#f3f4f6;border:none;border-radius:50%;width:28px;height:28px;font-size:1rem;cursor:pointer;line-height:28px;text-align:center}}
  .prog-row{{display:flex;align-items:flex-start;gap:10px;padding:10px 0;border-bottom:1px solid #f3f4f6}}.prog-row:last-child{{border-bottom:none}}
  .prog-row-date{{font-size:.75rem;color:var(--muted);white-space:nowrap;padding-top:2px;min-width:80px}}.prog-row-note{{font-size:.85rem;font-weight:500}}
"""

JS_TEMPLATE = """
  const NOTES_KEY   = 'palestra_notes_v1';
  const HISTORY_KEY = 'palestra_history_v1';
  const EX_NAMES    = {ex_names};

  let notes = {{}};
  let currentTab = '{first_key}';

  function loadNotes() {{
    try {{ notes = JSON.parse(localStorage.getItem(NOTES_KEY) || '{{}}'); }} catch(e) {{ notes = {{}}; }}
    document.querySelectorAll('.note-input').forEach(el => {{
      const id = el.closest('.card').id;
      if (notes[id]) el.value = notes[id];
    }});
  }}

  let saveTimer = null;
  function saveNote(id, value) {{
    if (value.trim() === '') delete notes[id]; else notes[id] = value;
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => {{
      localStorage.setItem(NOTES_KEY, JSON.stringify(notes));
      const dot = document.getElementById('saved-dot');
      dot.classList.add('saved');
      setTimeout(() => dot.classList.remove('saved'), 1500);
    }}, 500);
  }}

  function resetNotes() {{
    if (!confirm('Azzera le note del workout corrente?')) return;
    notes = {{}};
    localStorage.removeItem(NOTES_KEY);
    document.querySelectorAll('.note-input').forEach(el => el.value = '');
  }}

  function saveWorkout() {{
    const hasNotes = Object.values(notes).some(v => v.trim() !== '');
    if (!hasNotes) {{ alert('Nessuna nota da salvare. Aggiungi prima i pesi usati!'); return; }}
    const prog = currentTab.toUpperCase();
    const now  = new Date();
    const dateStr = now.toLocaleDateString('it-IT', {{ weekday:'short', day:'2-digit', month:'short', year:'numeric' }});
    const timeStr = now.toLocaleTimeString('it-IT', {{ hour:'2-digit', minute:'2-digit' }});
    const session = {{ id: now.getTime(), date: dateStr, time: timeStr, program: prog, notes: {{...notes}} }};
    let history = loadHistory();
    history.unshift(session);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
    notes = {{}};
    localStorage.removeItem(NOTES_KEY);
    document.querySelectorAll('.note-input').forEach(el => el.value = '');
    alert('✅ Allenamento Programma ' + prog + ' salvato!\\n' + dateStr + ' alle ' + timeStr);
    renderHistoryPanel();
  }}

  function loadHistory() {{
    try {{ return JSON.parse(localStorage.getItem(HISTORY_KEY) || '[]'); }} catch(e) {{ return []; }}
  }}

  function renderHistoryPanel() {{
    const history = loadHistory();
    const container = document.getElementById('storico-content');
    if (history.length === 0) {{
      container.innerHTML = '<div class="storico-empty"><div style="font-size:2.5rem;margin-bottom:12px">📋</div><strong>Nessun allenamento salvato</strong><br><span style="font-size:.8rem">Premi \\"Salva allenamento\\" al termine</span></div>';
      return;
    }}
    container.innerHTML = history.map(s => {{
      const exs  = Object.entries(s.notes).filter(([,v]) => v.trim() !== '');
      const rows = exs.map(([id, val]) =>
        '<div class="session-ex" onclick="showProgression(\'' + id + '\')" style="cursor:pointer">' +
        '<div style="display:flex;justify-content:space-between;align-items:center">' +
        '<span class="session-ex-name">' + (EX_NAMES[id] || id) + '</span>' +
        '<span style="font-size:.7rem;color:#93c5fd">progressione ▸</span></div>' +
        '<div class="session-ex-note">' + escHtml(val) + '</div></div>'
      ).join('');
      return '<div class="session-card">' +
        '<div class="session-header" onclick="toggleSession(\'sess-' + s.id + '\')">' +
        '<div class="session-meta"><div class="session-date">' + s.date + ' · ' + s.time + '</div>' +
        '<div class="session-sub">' + exs.length + ' esercizi annotati</div></div>' +
        '<span class="prog-badge ' + s.program.toLowerCase() + '">Prog. ' + s.program + '</span>' +
        '<span class="chevron" id="chev-' + s.id + '">▼</span>' +
        '<button class="del-session-btn" onclick="deleteSession(event,' + s.id + ')">🗑</button></div>' +
        '<div class="session-body" id="sess-' + s.id + '">' +
        (rows || '<div style="color:var(--muted);font-size:.8rem;padding:6px 0">Nessuna nota</div>') +
        '</div></div>';
    }}).join('');
  }}

  function toggleSession(bodyId) {{
    const body = document.getElementById(bodyId);
    const sessId = bodyId.replace('sess-','');
    const chev = document.getElementById('chev-' + sessId);
    body.classList.toggle('open');
    if (chev) chev.classList.toggle('open');
  }}

  function deleteSession(e, id) {{
    e.stopPropagation();
    if (!confirm('Eliminare questo allenamento?')) return;
    localStorage.setItem(HISTORY_KEY, JSON.stringify(loadHistory().filter(s => s.id !== id)));
    renderHistoryPanel();
  }}

  function showProgression(exId) {{
    const entries = loadHistory()
      .filter(s => s.notes[exId] && s.notes[exId].trim() !== '')
      .map(s => ({{ date: s.date + ' ' + s.time, prog: s.program, note: s.notes[exId] }}));
    document.getElementById('prog-modal-title').textContent = EX_NAMES[exId] || exId;
    document.getElementById('prog-modal-sub').textContent =
      entries.length + ' allenament' + (entries.length===1?'o':'i') + ' registrat' + (entries.length===1?'o':'i');
    document.getElementById('prog-modal-body').innerHTML = entries.length === 0
      ? '<p style="color:var(--muted);font-size:.85rem">Nessun dato storico.</p>'
      : entries.map(e =>
          '<div class="prog-row"><div class="prog-row-date">' + e.date +
          '<br><span class="prog-badge ' + e.prog.toLowerCase() +
          '" style="font-size:.65rem;padding:1px 6px">Prog. ' + e.prog + '</span></div>' +
          '<div class="prog-row-note">' + escHtml(e.note) + '</div></div>'
        ).join('');
    document.getElementById('prog-modal').classList.add('open');
  }}

  function closeProgModal(e) {{
    if (e.target === document.getElementById('prog-modal'))
      document.getElementById('prog-modal').classList.remove('open');
  }}

  function escHtml(s) {{
    return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
  }}

  function showTab(t) {{
    const allKeys={all_tabs_json};
    allKeys.forEach(x => {{
      const p = document.getElementById('panel-' + x);
      const b = document.getElementById('tab-' + x);
      if (p) p.classList.remove('active');
      if (b) allKeys.forEach(k => b.classList.remove('active-' + k));
    }});
    document.getElementById('panel-' + t).classList.add('active');
    document.getElementById('tab-' + t).classList.add('active-' + t);
    currentTab = t;
    document.getElementById('footer-bar').style.display = (t === 'storico') ? 'none' : 'flex';
    if (t === 'storico') renderHistoryPanel();
  }}

  loadNotes();
  showTab('{first_key}');
"""


def generate_html(meta, programs, prog_keys, prog_labels, output_path):
    panels_html = ''.join(render_program_panel(k, programs.get(k, [])) for k in prog_keys)
    ex_names_js = build_ex_names_js(programs)
    title    = meta['title'].replace('&', '&amp;').replace('<', '&lt;')
    subtitle = meta['weeks'] if meta['weeks'] else 'Scheda di allenamento'
    first_key = prog_keys[0] if prog_keys else 'a'
    all_tabs_json = json.dumps(prog_keys + ['storico'])
    dyn_css = generate_dynamic_css(prog_keys)
    # Extract badge css separately for CSS template placeholders
    tab_css = ''.join(
        f'.tab-btn.active-{k}{{color:white;border-color:{TAB_COLORS[i % len(TAB_COLORS)]}}}'
        for i, k in enumerate(prog_keys)
    ) + '.tab-btn.active-storico{color:white;border-color:#f59e0b}'
    badge_css = ''.join(
        f'.prog-badge.{k}{{background:{ACCENT_COLORS[i % len(ACCENT_COLORS)]}}}'
        for i, k in enumerate(prog_keys)
    )
    css = CSS.format(dyn_css=tab_css, dyn_badge_css=badge_css)
    js = JS_TEMPLATE.format(ex_names=ex_names_js, first_key=first_key, all_tabs_json=all_tabs_json)

    tab_buttons = '\n  '.join(
        f"<button class=\"tab-btn\" id=\"tab-{k}\" onclick=\"showTab('{k}')\">Prog. {prog_labels[i]}</button>"
        for i, k in enumerate(prog_keys)
    ) + '\n  <button class="tab-btn" id="tab-storico" onclick="showTab(\'storico\')">📊 Storico</button>'

    html = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>{title}</title>
<style>{css}</style>
</head>
<body>

<header>
  <h1>🏋️ {title}</h1>
  <p>{subtitle}</p>
  <div class="tabs">
  {tab_buttons}
  </div>
</header>

{panels_html}

<!-- STORICO -->
<div class="panel" id="panel-storico">
  <div id="storico-content">
    <div class="storico-empty">
      <div style="font-size:2.5rem;margin-bottom:12px">📋</div>
      <strong>Nessun allenamento salvato</strong><br>
      <span style="font-size:.8rem">Completa un allenamento e premi "Salva allenamento"</span>
    </div>
  </div>
</div>

<!-- Progressione modal -->
<div class="modal-overlay" id="prog-modal" onclick="closeProgModal(event)">
  <div class="modal-sheet">
    <button class="modal-close" onclick="document.getElementById('prog-modal').classList.remove('open')">✕</button>
    <div class="modal-title" id="prog-modal-title"></div>
    <div style="font-size:.75rem;color:var(--muted);margin-bottom:14px" id="prog-modal-sub"></div>
    <div id="prog-modal-body"></div>
  </div>
</div>

<div class="footer-bar" id="footer-bar">
  <small>Note salvate <span class="saved-dot" id="saved-dot"></span></small>
  <button class="save-btn" onclick="saveWorkout()">💾 Salva allenamento</button>
  <button class="reset-btn" onclick="resetNotes()">🗑</button>
</div>

<script>{js}</script>
</body>
</html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return html


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    pdf_path = sys.argv[1]
    if not Path(pdf_path).exists():
        print(f"❌  File non trovato: {pdf_path}")
        sys.exit(1)

    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(pdf_path).with_suffix('.html')

    print(f"📄  Lettura PDF: {pdf_path}")
    try:
        meta, programs, prog_keys, prog_labels = parse_pdf(pdf_path)
    except Exception as e:
        print(f"❌  Errore nel parsing del PDF: {e}")
        sys.exit(1)

    counts = {k: sum(len(s['exercises']) for s in programs[k]) for k in prog_keys}
    counts_str = ' | '.join(f"Prog {prog_labels[i]}: {counts[k]}" for i, k in enumerate(prog_keys))
    print(f"✅  Esercizi trovati → {counts_str}")

    html = generate_html(meta, programs, prog_keys, prog_labels, out_path)

    print(f"🎉  HTML generato: {out_path}  ({len(html)//1024} KB)")
    print(f"📱  Trasferisci il file sul telefono e aprilo nel browser!")


if __name__ == '__main__':
    main()
