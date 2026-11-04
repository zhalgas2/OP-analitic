"""Generates the three soft-3D course illustrations (master SVGs).

Run:  python3 tools/build_illustrations.py
Then: node tools/render_webp.mjs   (rasterises SVG -> WebP 320/640)

All three scenes share the same platform, arch, lighting (top-left key light,
warm gold ambient) and palette so they read as one family.
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "illustrations"

CREAM = "#FAF6EE"
FOREST = "#213E32"
SAGE = "#567B62"
BEIGE = "#E9E0D1"
GOLD = "#C9A66B"


def defs(extra=""):
    return f"""
<defs>
  <linearGradient id="plTop" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#FFFEFA"/><stop offset=".55" stop-color="#F6EFE2"/><stop offset="1" stop-color="#E6D9C2"/>
  </linearGradient>
  <linearGradient id="plSide" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#D9C8AA"/><stop offset=".35" stop-color="{BEIGE}"/><stop offset=".7" stop-color="#DDCDB1"/><stop offset="1" stop-color="#C3AE8C"/>
  </linearGradient>
  <linearGradient id="archFace" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#3F7159"/><stop offset=".45" stop-color="{FOREST}"/><stop offset="1" stop-color="#16291F"/>
  </linearGradient>
  <linearGradient id="archSide" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#132a20"/><stop offset="1" stop-color="#0C1A14"/>
  </linearGradient>
  <linearGradient id="niche" x1=".5" y1="0" x2=".5" y2="1">
    <stop offset="0" stop-color="#132a20"/><stop offset=".6" stop-color="#1F3D30"/><stop offset="1" stop-color="#2D5241"/>
  </linearGradient>
  <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#F6E6BF"/><stop offset=".45" stop-color="{GOLD}"/><stop offset="1" stop-color="#946F38"/>
  </linearGradient>
  <linearGradient id="goldV" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#F8E9C4"/><stop offset=".5" stop-color="#D8B77A"/><stop offset="1" stop-color="#A9844A"/>
  </linearGradient>
  <radialGradient id="warm" cx=".5" cy=".5" r=".5">
    <stop offset="0" stop-color="#FFE9B8" stop-opacity=".85"/><stop offset=".5" stop-color="#E9C988" stop-opacity=".28"/><stop offset="1" stop-color="#E9C988" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="halo" cx=".5" cy=".55" r=".5">
    <stop offset="0" stop-color="#FFFFFF" stop-opacity=".9"/><stop offset="1" stop-color="{CREAM}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="lattice" width="14" height="14" patternUnits="userSpaceOnUse">
    <path d="M7 0 L14 7 L7 14 L0 7 Z" fill="none" stroke="{GOLD}" stroke-width=".6" opacity=".22"/>
  </pattern>
  <filter id="blur6" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="6"/></filter>
  <filter id="blur3" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3"/></filter>
  <filter id="drop" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="2" dy="4" stdDeviation="3" flood-color="{FOREST}" flood-opacity=".28"/>
  </filter>
  <filter id="dropS" x="-30%" y="-30%" width="160%" height="160%">
    <feDropShadow dx="1" dy="2" stdDeviation="1.6" flood-color="{FOREST}" flood-opacity=".3"/>
  </filter>
  {extra}
</defs>"""


def star8(cx, cy, r, fill="url(#gold)", opacity=1):
    """Rub el hizb style 8-point star (two rotated squares)."""
    s = r * 0.72
    sq = f"M{cx-s} {cy-s} H{cx+s} V{cy+s} H{cx-s} Z"
    return (f'<g opacity="{opacity}"><path d="{sq}" fill="{fill}"/>'
            f'<path d="{sq}" fill="{fill}" transform="rotate(45 {cx} {cy})"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r*0.32}" fill="{FOREST}" opacity=".55"/></g>')


def sparkle(cx, cy, r, op=1):
    return (f'<path d="M{cx} {cy-r} Q{cx+r*.18} {cy-r*.18} {cx+r} {cy} Q{cx+r*.18} {cy+r*.18} {cx} {cy+r} '
            f'Q{cx-r*.18} {cy+r*.18} {cx-r} {cy} Q{cx-r*.18} {cy-r*.18} {cx} {cy-r} Z" fill="#E7CF9C" opacity="{op}"/>')


def base_scene():
    """Halo, ground shadow, platform and arch (shared by all three icons)."""
    return f"""
  <ellipse cx="120" cy="118" rx="112" ry="104" fill="url(#halo)"/>
  <ellipse cx="122" cy="206" rx="98" ry="15" fill="{FOREST}" opacity=".22" filter="url(#blur6)"/>
  <!-- platform -->
  <path d="M28 184 V197 A92 22 0 0 0 212 197 V184 Z" fill="url(#plSide)"/>
  <path d="M28 197 A92 22 0 0 0 212 197" fill="none" stroke="#B9A27E" stroke-width="1" opacity=".6"/>
  <ellipse cx="120" cy="184" rx="92" ry="22" fill="url(#plTop)"/>
  <ellipse cx="120" cy="184" rx="91" ry="21.3" fill="none" stroke="#FFFFFF" stroke-width="1.4" opacity=".8"/>
  <ellipse cx="120" cy="184.5" rx="78" ry="16.5" fill="none" stroke="{GOLD}" stroke-width="1" opacity=".55"/>
  <!-- arch: depth, face, trim, niche -->
  <g filter="url(#drop)">
    <path d="M69 181 V100 C69 64 99 44 127 26 C155 44 185 64 185 100 V181 Z" fill="url(#archSide)"/>
    <path d="M62 180 V98 C62 62 92 42 120 24 C148 42 178 62 178 98 V180 Z" fill="url(#archFace)"/>
  </g>
  <path d="M63.5 178 V98 C63.5 63 92 44 120 26" fill="none" stroke="#FFFFFF" stroke-width="1.2" opacity=".22"/>
  <path d="M68 180 V99 C68 66 95 48 120 31 C145 48 172 66 172 99 V180" fill="none" stroke="url(#gold)" stroke-width="1.6" opacity=".9"/>
  <path d="M80 180 V104 C80 76 101 61 120 48 C139 61 160 76 160 104 V180 Z" fill="url(#niche)"/>
  <path d="M80 180 V104 C80 76 101 61 120 48 C139 61 160 76 160 104 V180 Z" fill="url(#lattice)"/>
  <path d="M80 180 V104 C80 76 101 61 120 48" fill="none" stroke="#0A1510" stroke-width="3" opacity=".35"/>
  {star8(120, 39.5, 5)}
  <rect x="58" y="175" width="124" height="9" rx="2.5" fill="#1A3328"/>
  <rect x="58" y="175" width="124" height="1.6" rx=".8" fill="url(#gold)" opacity=".85"/>
"""


def svg(body, extra_defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 240" width="240" height="240">'
            f'{defs(extra_defs)}{base_scene()}{body}</svg>\n')


# ---------------------------------------------------------------- Әліппе
def alippe():
    alif = "M126.5 58 C131.5 57 134.5 60.5 133.5 65.5 L125 150 C124.4 155.5 117.4 155.5 117.2 150 L119.6 68 C119.8 62 122 58.6 126.5 58 Z"
    books = f"""
  <g filter="url(#drop)">
    <!-- bottom book -->
    <path d="M96 181 L103 176 V164 L96 169 Z" fill="#F6EEDD"/>
    <rect x="32" y="169" width="64" height="13" rx="3" fill="{FOREST}"/>
    <rect x="32" y="169" width="64" height="3" rx="1.5" fill="#3C6B53"/>
    <rect x="40" y="169" width="2.2" height="13" fill="url(#gold)"/><rect x="85" y="169" width="2.2" height="13" fill="url(#gold)"/>
    <path d="M97 172 L102 168.5 M97 175 L102 171.5 M97 178 L102 174.5" stroke="#D8CBB2" stroke-width=".6"/>
    <!-- middle book -->
    <path d="M93 168 L99 163.5 V152.5 L93 157 Z" fill="#F6EEDD"/>
    <rect x="38" y="157" width="55" height="12" rx="3" fill="{SAGE}"/>
    <rect x="38" y="157" width="55" height="2.6" rx="1.3" fill="#7A9C84"/>
    <rect x="46" y="157" width="2" height="12" fill="url(#gold)"/><rect x="82" y="157" width="2" height="12" fill="url(#gold)"/>
    <path d="M94 160 L98.5 156.5 M94 163 L98.5 159.5" stroke="#D8CBB2" stroke-width=".6"/>
    <!-- top book (tilted) -->
    <g transform="rotate(-5 64 150)">
      <path d="M41 146 L47 141 H97 L91 146 Z" fill="#D2B585"/>
      <path d="M91 146 L97 141 V151 L91 156 Z" fill="#F6EEDD"/>
      <rect x="35" y="146" width="56" height="10.5" rx="2.6" fill="#A97F4B"/>
      <rect x="35" y="146" width="56" height="2.4" rx="1.2" fill="#C49B63"/>
      <rect x="55" y="149" width="16" height="4.4" rx="1" fill="none" stroke="#F1DDB0" stroke-width=".8"/>
    </g>
  </g>"""
    inkpot = f"""
  <!-- quill (behind pot neck) -->
  <g filter="url(#dropS)">
    <path d="M170 160 C167 128 187 101 210 86 C208 114 195 140 171 160 Z" fill="url(#quill)"/>
    <path d="M170 160 C167 128 187 101 210 86" fill="none" stroke="#FFFFFF" stroke-width="1" opacity=".9"/>
    <path d="M168 168 Q186 128 209 88" fill="none" stroke="url(#gold)" stroke-width="1.5" stroke-linecap="round"/>
    <g stroke="#C9B48F" stroke-width=".6" opacity=".7" fill="none">
      <path d="M176 146 L172 140"/><path d="M180 138 L175 131"/><path d="M185 129 L180 122"/><path d="M190 121 L186 113"/><path d="M196 112 L192 105"/>
      <path d="M178 145 L186 143"/><path d="M183 136 L192 133"/><path d="M188 127 L197 123"/><path d="M194 117 L202 112"/>
    </g>
  </g>
  <!-- inkpot -->
  <g filter="url(#drop)">
    <ellipse cx="168" cy="191" rx="17" ry="4.5" fill="#0C1A14"/>
    <path d="M151 191 C149 178 154 170 168 170 C182 170 187 178 185 191 Z" fill="url(#glass)"/>
    <path d="M156 186 C155 179 158 174 164 173" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" opacity=".35"/>
    <rect x="161" y="162" width="14" height="9" rx="2" fill="url(#goldV)"/>
    <ellipse cx="168" cy="162" rx="8.5" ry="2.6" fill="#F3DFB2"/>
    <ellipse cx="168" cy="162.2" rx="5.5" ry="1.6" fill="#0C1A14"/>
    <path d="M168 168 L169.4 162.4" stroke="url(#gold)" stroke-width="1.6"/>
    <path d="M154 181 H182" stroke="url(#gold)" stroke-width="1" opacity=".7"/>
  </g>"""
    body = f"""
  <ellipse cx="120" cy="104" rx="38" ry="52" fill="url(#warm)"/>
  <!-- Alif ا : extrusion + face + highlight -->
  <path d="{alif}" fill="#7E5E30" transform="translate(3.2 3)"/>
  <path d="{alif}" fill="#9C7A45" transform="translate(1.6 1.5)"/>
  <path d="{alif}" fill="url(#goldV)"/>
  <path d="M127 61 C129.6 60.6 130.8 62.4 130.4 65 L123.6 140" fill="none" stroke="#FFF6DF" stroke-width="1.3" stroke-linecap="round" opacity=".9"/>
  {books}
  {inkpot}
  {sparkle(204, 58, 5)}{sparkle(40, 120, 4, .8)}{sparkle(148, 70, 3, .9)}{sparkle(30, 70, 3, .6)}
"""
    extra = f"""
  <linearGradient id="quill" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#E3D6BE"/><stop offset=".5" stop-color="#FFFDF7"/><stop offset="1" stop-color="#F2E8D6"/></linearGradient>
  <linearGradient id="glass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3B6852"/><stop offset=".5" stop-color="{FOREST}"/><stop offset="1" stop-color="#0E1D16"/></linearGradient>"""
    return svg(body, extra)


# ---------------------------------------------------------------- Тәжуид
def tajweed():
    heights = [12, 24, 38, 52, 64, 52, 38, 24, 12]
    bars, glow = [], []
    for i, h in enumerate(heights):
        x = 120 - 4 * 9 + i * 9 - 2.5 + 0.0
        x = 81.5 + i * 9 + 0.0
        y = 100 - h / 2
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="5" height="{h}" rx="2.5" fill="url(#goldV)"/>')
        glow.append(f'<rect x="{x-1:.1f}" y="{y-1:.1f}" width="7" height="{h+2}" rx="3.5" fill="#F3D99E"/>')
    waves = []
    for side in (-1, 1):
        for k, (dx, w, op) in enumerate([(0, 3, 1), (13, 2.4, .7), (26, 1.8, .45)]):
            x0 = 52 - dx if side < 0 else 188 + dx
            bend = x0 - (12 + k * 5) if side < 0 else x0 + (12 + k * 5)
            span = 22 + k * 12
            waves.append(f'<path d="M{x0} {100-span} Q{bend} 100 {x0} {100+span}" fill="none" stroke="url(#gold)" '
                         f'stroke-width="{w}" stroke-linecap="round" opacity="{op}"/>')
    headphones = f"""
  <g filter="url(#drop)">
    <!-- headband -->
    <path d="M86 162 C84 116 156 116 154 162" fill="none" stroke="#0F1F19" stroke-width="11" stroke-linecap="round"/>
    <path d="M86 162 C84 116 156 116 154 162" fill="none" stroke="url(#band)" stroke-width="9" stroke-linecap="round"/>
    <path d="M89 146 C92 124 114 118 128 120" fill="none" stroke="#6E9A80" stroke-width="2" stroke-linecap="round" opacity=".7"/>
    <path d="M98 134 C108 127 132 127 142 134" fill="none" stroke="{BEIGE}" stroke-width="4" stroke-linecap="round"/>
    <!-- yokes -->
    <rect x="81" y="152" width="9" height="12" rx="2.5" fill="url(#goldV)"/>
    <rect x="150" y="152" width="9" height="12" rx="2.5" fill="url(#goldV)"/>
    <!-- left cup -->
    <ellipse cx="84" cy="172" rx="14" ry="19" fill="url(#cup)"/>
    <ellipse cx="84" cy="172" rx="9.5" ry="14" fill="none" stroke="url(#gold)" stroke-width="1.6"/>
    <path d="M77 162 C78 158 81 156 84 156" fill="none" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" opacity=".35"/>
    <ellipse cx="95" cy="172" rx="6" ry="17" fill="url(#cushion)"/>
    <!-- right cup -->
    <ellipse cx="145" cy="172" rx="6" ry="17" fill="url(#cushion)"/>
    <ellipse cx="156" cy="172" rx="14" ry="19" fill="url(#cup)"/>
    <ellipse cx="156" cy="172" rx="9.5" ry="14" fill="none" stroke="url(#gold)" stroke-width="1.6"/>
    {star8(156, 172, 3.6)}
    {star8(84, 172, 3.6)}
  </g>"""
    body = f"""
  <ellipse cx="120" cy="100" rx="44" ry="48" fill="url(#warm)"/>
  <path d="M84 100 H156" stroke="#E7CF9C" stroke-width=".8" opacity=".35"/>
  <g filter="url(#blur3)" opacity=".55">{''.join(glow)}</g>
  {''.join(bars)}
  {''.join(waves)}
  {headphones}
  {sparkle(200, 52, 4.5)}{sparkle(42, 160, 3.5, .8)}{sparkle(186, 150, 3, .7)}
"""
    extra = f"""
  <linearGradient id="band" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3F7159"/><stop offset="1" stop-color="{FOREST}"/></linearGradient>
  <radialGradient id="cup" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#4B7E64"/><stop offset=".55" stop-color="{FOREST}"/><stop offset="1" stop-color="#0E1D16"/></radialGradient>
  <linearGradient id="cushion" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#D9CCB4"/><stop offset=".5" stop-color="#F4ECDD"/><stop offset="1" stop-color="#C9B996"/></linearGradient>"""
    return svg(body, extra)


# ---------------------------------------------------------------- Құран
def quran():
    def page_lines(side):
        # Non-readable text texture: soft dashes, no real letters or verses.
        out = []
        for i in range(9):
            y = 105 + i * 4.6
            if side < 0:
                x1, x2 = 79 + i * .25, 114
                curve = f"M{x1} {y+1.2-i*.05} Q{(x1+x2)/2} {y-1.4} {x2} {y+1.6}"
            else:
                x1, x2 = 126, 161 - i * .25
                curve = f"M{x1} {y+1.6} Q{(x1+x2)/2} {y-1.4} {x2} {y+1.2-i*.05}"
            out.append(f'<path d="{curve}" fill="none" stroke="#8A7A5E" stroke-width="1.1" '
                       f'stroke-dasharray="{3+i%3} 1.6 {5-i%2} 1.4" opacity=".38"/>')
        return "".join(out)

    rehal = f"""
  <g filter="url(#drop)">
    <!-- back plank -->
    <path d="M152 126 L166 120 L106 190 L94 190 Z" fill="url(#woodDark)"/>
    <!-- front plank -->
    <path d="M88 126 L74 120 L134 190 L146 190 Z" fill="url(#wood)"/>
    <path d="M76 121 L136 190" stroke="#E2B886" stroke-width="1" opacity=".55"/>
    <!-- carved cut-out at the hinge -->
    <path d="M114 166 C114 160 117 157 120 155 C123 157 126 160 126 166 Z" fill="#4A2D16" opacity=".85"/>
    <circle cx="120" cy="158" r="2.2" fill="url(#gold)"/>
    <path d="M100 150 L108 160 M132 160 L140 150" stroke="url(#gold)" stroke-width="1.2" opacity=".8"/>
  </g>"""
    book = f"""
  <g filter="url(#drop)">
    <!-- cover -->
    <path d="M120 156 C102 145 84 146 66 152 L62 98 C82 89 104 91 120 101 C136 91 158 89 178 98 L174 152 C156 146 138 145 120 156 Z" fill="url(#cover)"/>
    <path d="M120 156 C102 145 84 146 66 152 M174 152 C156 146 138 145 120 156" fill="none" stroke="url(#gold)" stroke-width="1.4"/>
    <!-- page stack edges -->
    <path d="M120 152 C103 142 86 143 70 148 L69 145 C86 140 103 139 120 149 C137 139 154 140 171 145 L170 148 C154 143 137 142 120 152 Z" fill="#E8DCC4"/>
    <!-- pages -->
    <path d="M120 149 C104 139 88 139 71 145 L68 98 C86 90 104 92 120 102 Z" fill="url(#pageL)"/>
    <path d="M120 149 C136 139 152 139 169 145 L172 98 C154 90 136 92 120 102 Z" fill="url(#pageR)"/>
    <!-- illuminated frames -->
    <path d="M116 141 C103 134 91 134 77 138 L75 103 C89 97 103 98 116 106 Z" fill="none" stroke="url(#gold)" stroke-width="1.1"/>
    <path d="M124 141 C137 134 149 134 163 138 L165 103 C151 97 137 98 124 106 Z" fill="none" stroke="url(#gold)" stroke-width="1.1"/>
    {page_lines(-1)}{page_lines(1)}
    <ellipse cx="96" cy="102.5" rx="7" ry="2" fill="url(#gold)" opacity=".85"/>
    <ellipse cx="144" cy="102.5" rx="7" ry="2" fill="url(#gold)" opacity=".85"/>
    <path d="M120 102 V149" stroke="#B9A47F" stroke-width="1.2" opacity=".8"/>
    <!-- ribbon bookmark -->
    <path d="M121 147 L124 166 L126.5 162 L129.5 165 L126.5 146 Z" fill="#7B2E2E" opacity=".9"/>
  </g>"""
    lantern = f"""
  <ellipse cx="192" cy="168" rx="26" ry="26" fill="url(#warm)"/>
  <g filter="url(#drop)">
    <ellipse cx="192" cy="191" rx="12" ry="3" fill="#0C1A14" opacity=".35"/>
    <path d="M192 140 v-5" stroke="url(#gold)" stroke-width="1.4"/>
    <circle cx="192" cy="133.5" r="2.4" fill="none" stroke="url(#gold)" stroke-width="1.3"/>
    <path d="M182 151 C182 145 186 141 192 140 C198 141 202 145 202 151 Z" fill="url(#goldV)"/>
    <rect x="180" y="150.5" width="24" height="3" rx="1.4" fill="#A9844A"/>
    <path d="M182 154 H202 L200 182 H184 Z" fill="url(#lampGlass)"/>
    <path d="M187.5 154 L188.5 182 M192 154 V182 M196.5 154 L195.5 182" stroke="url(#gold)" stroke-width="1.1"/>
    <path d="M182 154 H202 L200 182 H184 Z" fill="none" stroke="url(#gold)" stroke-width="1.5"/>
    <ellipse cx="192" cy="169" rx="3.2" ry="5" fill="#FFF7DF"/>
    <path d="M181 182 H203 L200 189 H184 Z" fill="url(#goldV)"/>
  </g>"""
    greens = f"""
  <g filter="url(#dropS)">
    <path d="M50 186 C48 170 44 158 36 146" fill="none" stroke="#3F6A50" stroke-width="1.6" stroke-linecap="round"/>
    <path d="M54 186 C56 168 62 156 70 146" fill="none" stroke="#3F6A50" stroke-width="1.6" stroke-linecap="round"/>
    <ellipse cx="38" cy="150" rx="7" ry="3.4" transform="rotate(-50 38 150)" fill="url(#leaf)"/>
    <ellipse cx="44" cy="163" rx="7.5" ry="3.6" transform="rotate(-25 44 163)" fill="url(#leaf)"/>
    <ellipse cx="41" cy="171" rx="6.5" ry="3.2" transform="rotate(30 41 171)" fill="url(#leaf)"/>
    <ellipse cx="67" cy="150" rx="7" ry="3.4" transform="rotate(48 67 150)" fill="url(#leaf)"/>
    <ellipse cx="61" cy="162" rx="7.5" ry="3.6" transform="rotate(20 61 162)" fill="url(#leaf)"/>
    <ellipse cx="62" cy="173" rx="6" ry="3" transform="rotate(-28 62 173)" fill="url(#leaf)"/>
    <path d="M44 185 Q52 181 60 185 Q52 189 44 185 Z" fill="#CDBB9C" opacity=".8"/>
  </g>"""
    body = f"""
  <ellipse cx="120" cy="110" rx="58" ry="48" fill="url(#warm)"/>
  {rehal}
  {book}
  {greens}
  {lantern}
  {sparkle(42, 70, 4.5, .9)}{sparkle(206, 96, 3.5, .8)}{sparkle(150, 66, 3, .8)}
"""
    extra = f"""
  <linearGradient id="wood" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#B98352"/><stop offset=".5" stop-color="#8D5A30"/><stop offset="1" stop-color="#5E3A1C"/></linearGradient>
  <linearGradient id="woodDark" x1="1" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8A5A33"/><stop offset="1" stop-color="#4E3018"/></linearGradient>
  <linearGradient id="cover" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3F7159"/><stop offset=".6" stop-color="{FOREST}"/><stop offset="1" stop-color="#12241B"/></linearGradient>
  <linearGradient id="pageL" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#FFFDF7"/><stop offset=".8" stop-color="#F6EEDD"/><stop offset="1" stop-color="#DCCDB0"/></linearGradient>
  <linearGradient id="pageR" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#F3EAD7"/><stop offset=".8" stop-color="#F7F0E1"/><stop offset="1" stop-color="#D8C8AA"/></linearGradient>
  <linearGradient id="lampGlass" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFE7AE"/><stop offset="1" stop-color="#E3B866"/></linearGradient>
  <linearGradient id="leaf" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#86A98F"/><stop offset="1" stop-color="{SAGE}"/></linearGradient>"""
    return svg(body, extra)


# ---------------------------------------------------------------- Иқро
def iqro():
    steps = []
    for i in range(6):
        x = 84 + i * 12.2
        top = 168 - (i + 1) * 13
        h = 176 - top
        steps.append(
            f'<path d="M{x+12} {top} L{x+16} {top-3} V{176-3} L{x+12} 176 Z" fill="#CDBB9C"/>'
            f'<path d="M{x} {top} L{x+4} {top-3} H{x+16} L{x+12} {top} Z" fill="#FFFDF7"/>'
            f'<rect x="{x}" y="{top}" width="12.2" height="{h}" fill="url(#stepFace)"/>'
            f'<rect x="{x}" y="{top}" width="12.2" height="1.4" fill="url(#gold)"/>'
            f'<circle cx="{x+6.1}" cy="{top+7}" r="{1.3 + i*0.18:.2f}" fill="url(#gold)" opacity=".9"/>')
    star = ("M150 52 L154.6 62 L165.5 63.2 L157.4 70.6 L159.7 81.4 L150 75.9 L140.3 81.4 "
            "L142.6 70.6 L134.5 63.2 L145.4 62 Z")
    book = f"""
  <g filter="url(#drop)">
    <path d="M36 182 L68 186 L100 182 L100 176 L68 180 L36 176 Z" fill="#E8DCC4"/>
    <path d="M68 180 C58 172 46 170 34 172 L36 176 C48 174 58 176 68 180 Z" fill="url(#cover2)"/>
    <path d="M68 180 C78 172 90 170 102 172 L100 176 C88 174 78 176 68 180 Z" fill="url(#cover2)"/>
    <path d="M68 178 C58 166 47 163 37 164 L36 172 C47 171 58 173 68 178 Z" fill="#FFFDF7"/>
    <path d="M68 178 C78 166 89 163 99 164 L100 172 C89 171 78 173 68 178 Z" fill="#F3EAD7"/>
    <path d="M42 168 Q52 167 62 172 M42 171 Q52 170 62 174 M74 172 Q84 167 94 168 M74 174 Q84 170 94 171" stroke="#8A7A5E" stroke-width=".8" stroke-dasharray="3 1.4" opacity=".45" fill="none"/>
    <path d="M100 170 L118 140" stroke="#8D5A30" stroke-width="2.4" stroke-linecap="round"/>
    <circle cx="118.6" cy="139" r="2" fill="url(#gold)"/>
  </g>"""
    body = f"""
  <ellipse cx="150" cy="70" rx="34" ry="34" fill="url(#warm)"/>
  <g filter="url(#dropS)">{''.join(steps)}</g>
  <path d="{star}" fill="#7E5E30" transform="translate(1.6 1.6)"/>
  <path d="{star}" fill="url(#goldV)"/>
  <path d="M150 56 L153.4 63.4" stroke="#FFF6DF" stroke-width="1.2" stroke-linecap="round"/>
  {book}
  {sparkle(200, 60, 4.5)}{sparkle(100, 78, 3, .8)}{sparkle(190, 140, 3.5, .7)}{sparkle(34, 120, 3, .6)}
"""
    extra = f"""
  <linearGradient id="stepFace" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F7F0E2"/><stop offset="1" stop-color="#E2D4BA"/></linearGradient>
  <linearGradient id="cover2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3F7159"/><stop offset="1" stop-color="#16291F"/></linearGradient>"""
    return svg(body, extra)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("alippe", alippe), ("iqro", iqro), ("tajweed", tajweed), ("quran", quran)]:
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", OUT / f"{name}.svg")
