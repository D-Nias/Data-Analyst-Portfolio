"""Render the Washington EV and NYC 311 summaries as GitHub-friendly SVGs.

The e-commerce SVGs are generated from that project's source CSV; see
ecommerce/README.md for its analysis-to-visualization workflow.
"""
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).parent


def t(x, y, value, size=22, color='#213047', weight='normal', anchor='start'):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'


def bar(x, y, width, label, value, max_value, display, color):
    parts = [t(x, y - 10, label, 20),
             f'<rect x="{x}" y="{y}" width="{width}" height="24" rx="12" fill="#e8edf2"/>',
             f'<rect x="{x}" y="{y}" width="{round(width * value / max_value, 1)}" height="24" rx="12" fill="{color}"/>',
             t(x + width + 18, y + 20, display, 20, '#213047', 'bold')]
    return ''.join(parts)


def chart(path, title, subtitle, sections, footnote, accent):
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="1000" viewBox="0 0 1000 1000" role="img">',
             f'<title>{escape(title)}</title><desc>{escape(subtitle + ". " + footnote)}</desc>',
             '<rect width="1000" height="1000" fill="#ffffff"/>',
             f'<rect width="1000" height="12" fill="{accent}"/>',
             t(55, 68, title, 34, '#15243a', 'bold'),
             t(55, 102, subtitle, 19, '#5c6a79')]
    for header, items, unit, y0, max_value in sections:
        parts.append(t(55, y0, header, 25, '#15243a', 'bold'))
        for i, (label, value, display) in enumerate(items):
            parts.append(bar(55, y0 + 54 + 62*i, 690, label, value, max_value, display, accent))
        parts.append(t(55, y0 + 54 + 62*len(items) + 37, unit, 16, '#647285'))
    parts.append(f'<line x1="55" y1="927" x2="945" y2="927" stroke="#d6dee8"/>')
    parts.append(t(55, 958, footnote, 16, '#5c6a79'))
    parts.append('</svg>')
    path.write_text('\n'.join(parts), encoding='utf-8')


chart(ROOT/'washington-ev'/'chart.svg',
      'Washington EV registry snapshot', '298,916 Washington records · September 2026 download',
      [('Vehicle type mix', [('Battery electric', 80.67, '80.67%'), ('Plug-in hybrid', 19.33, '19.33%')], 'Share of Washington-registered EVs', 155, 100),
       ('Counties with the most registered EVs', [('King', 144257, '144,257'), ('Snohomish', 37818, '37,818'), ('Pierce', 25042, '25,042')], 'Raw counts; these are not county adoption rates', 420, 150000)],
      'Source: Washington State Department of Licensing', '#16876a')

chart(ROOT/'nyc-311'/'chart.svg',
      'NYC 311 service operations', '80,941 requests created June 1–7, 2026',
      [('Highest-volume request types', [('Illegal Parking', 13694, '13,694'), ('Noise – Residential', 8141, '8,141'), ('Blocked Driveway', 3947, '3,947')], 'Number of requests', 155, 15000),
       ('Median recorded time to close', [('Illegal Parking', 1.64, '1.64 h'), ('Damaged Tree', 47.77, '47.77 h'), ('Unsanitary Condition', 174.38, '174.38 h')], 'Valid closed requests only; closure does not imply physical repair', 455, 190)],
      'Source: NYC Open Data 311 service requests', '#8059b1')
