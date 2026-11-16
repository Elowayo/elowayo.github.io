"""Build the Elowa public site into _site/.

    python3 tools/build.py

Reads the legal markdown from content/ and the list of published languages
from site.json. English lives at the site root (/terms.html, /privacy.html,
/index.html) so links in shipped apps keep working; every other language
lives under /<lang>/. A language that is not listed in site.json is not built
at all, and the language switcher does not offer it.
"""
import json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from md2html import convert

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "_site")
SITE_URL = "https://elowayo.github.io"
DEFAULT_LANG = "en"

# Heading -> id overrides so anchors are the same in every language.
# The app links terms.html#5a-usage-measurement.
STABLE_IDS = {
    "5A. Usage Measurement": "5a-usage-measurement",
    "5A. 사용 데이터 수집": "5a-usage-measurement",
}

PAGES = ["index.html", "privacy.html", "terms.html"]

MARK = ('<svg viewBox="0 0 96 96" fill="none" aria-hidden="true" focusable="false">'
        '<path d="M48 12 A36 36 0 0 0 48 84 C45 81 43 78 40.5 71 C39 68 39 66 40 63.5 '
        'C42.5 62 43 59 39.5 57.5 C41 56 42 54 39 52 C35 52 33 50 34 48 C37 43 41 38 43 33 '
        'C42 27 43 20 48 12 Z" fill="currentColor"/>'
        '<path d="M48 12 A36 36 0 0 1 48 84" stroke="currentColor" stroke-width="6" stroke-linecap="round"/>'
        '<path d="M79 5 C80.5 10.5 82 12 87.5 13.5 C82 15 80.5 16.5 79 22 C77.5 16.5 76 15 70.5 13.5 '
        'C76 12 77.5 10.5 79 5 Z" fill="currentColor"/></svg>')

HOME_EN = '''<div class="hero">
  <div class="wrap">
    <p class="eyebrow">Coming soon</p>
    <h1>Is my skin actually improving?</h1>
    <p class="lede">Elowa answers that with a one-minute daily photo check-in — three guided poses,
      an honest before-and-after comparison, and photos that stay on your phone.</p>
    <div class="actions">
      <a class="btn btn-primary" href="mailto:hello.elowa@gmail.com?subject=Elowa">Get in touch</a>
      <a class="btn btn-outline" href="privacy.html">How your data is handled</a>
    </div>
  </div>
</div>

<section>
  <div class="wrap">
    <h2 class="section-title">How a check-in works</h2>
    <p class="section-intro">The same three photos, taken the same way, every day. Consistency is what makes
      a comparison worth looking at.</p>
    <div class="cards">
      <div class="card">
        <span class="step">1</span>
        <h3>Line up</h3>
        <p>On-screen guides hold your angle, distance, and framing steady. Elowa reads the live preview
          for brightness and colour temperature, and your phone's motion sensors for tilt, so it can tell
          you when the light or the angle has drifted since last time.</p>
      </div>
      <div class="card">
        <span class="step">2</span>
        <h3>Three poses</h3>
        <p>Front, left, right. It takes about a minute. Add a note if the day is worth remembering —
          a new product, a flare-up, a bad night's sleep.</p>
      </div>
      <div class="card">
        <span class="step">3</span>
        <h3>Compare honestly</h3>
        <p>Wipe between any two days, or view them side by side. When a comparison may be unreliable,
          Elowa says so instead of quietly showing you a flattering one.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2 class="section-title">Your face is yours</h2>
    <p class="section-intro">Privacy isn't a setting in Elowa — it's the architecture. There is no
      server-side copy of your photos, because they are never sent anywhere.</p>
    <div class="pledge">
      <div>
        <h3>Photos stay on your device</h3>
        <p>Check-in photos and notes are stored in the app's own storage on your phone. We never
          receive, view, or store them.</p>
      </div>
      <div>
        <h3>Processing happens on your phone</h3>
        <p>Lighting and angle checks, and the optional reframing assist, all run on-device. Nothing
          from them is transmitted.</p>
      </div>
      <div>
        <h3>We hold only your account</h3>
        <p>Your name, email, and your consent record. Not your photos, not your notes, not even the
          concerns you pick — those stay on your phone.</p>
      </div>
      <div>
        <h3>Measurement you opt into</h3>
        <p>Off unless you turn it on. Limited technical and usage data, never touching your photos,
          notes, or concerns — and the app works identically either way.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="disclaimer"><strong>Elowa is a tracking tool, not a medical device.</strong> It does not
      diagnose, treat, cure, or prevent any disease or skin condition, and nothing in the app is medical
      or dermatological advice. If you have a concern about your skin, a mole, or a lesion, see a
      licensed dermatologist or physician.</p>
  </div>
</section>'''

HOME_KO = '''<div class="hero">
  <div class="wrap">
    <p class="eyebrow">피부 경과 기록</p>
    <h1>내 피부 비포 애프터를<br> 한눈에!</h1>
    <p class="lede">하루 1분의 체크인으로 어제와 오늘, 한 달 전과 지금을 한눈에
      비교해 보세요.</p>
    <div class="actions">
      <a class="btn btn-primary" href="mailto:hello.elowa@gmail.com?subject=Elowa">문의하기</a>
      <a class="btn btn-outline" href="privacy.html">사진은 어디에 저장되나요?</a>
    </div>
  </div>
</div>

<section>
  <div class="wrap">
    <h2 class="section-title">하루 1분, 세 장이면 끝</h2>
    <p class="section-intro">매일 같은 방식으로 같은 사진 세 장을 찍습니다. 조건이 같아야 비교할 의미가 생깁니다.</p>
    <div class="cards">
      <div class="card">
        <span class="step">1</span>
        <h3>위치 맞추기</h3>
        <p>화면 안내선이 각도, 거리, 구도를 일정하게 잡아 줍니다. Elowa는 미리보기 화면으로 밝기와
          색온도를, 휴대폰 동작 센서로 기울기를 읽어서, 지난번과 조명이나 각도가 달라지면 알려 줍니다.</p>
      </div>
      <div class="card">
        <span class="step">2</span>
        <h3>세 방향 촬영</h3>
        <p>정면, 왼쪽, 오른쪽. 1분이면 끝납니다. 새 제품을 쓰기 시작했거나, 트러블이 올라왔거나,
          잠을 설친 날이라면 메모를 남겨 두세요.</p>
      </div>
      <div class="card">
        <span class="step">3</span>
        <h3>있는 그대로 비교</h3>
        <p>두 날짜를 밀어서 넘겨 보거나 나란히 놓고 봅니다. 비교 결과를 믿기 어려울 때는 그럴듯한
          사진을 슬쩍 보여 주는 대신 그렇다고 알려 줍니다.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2 class="section-title">사진은 내 폰에만</h2>
    <p class="section-intro">Elowa에서 개인정보 보호는 설정 항목이 아니라 처음부터 그렇게 만든 구조입니다.
      사진을 어디에도 보내지 않으니, 서버에 사진 사본이 있을 수 없습니다.</p>
    <div class="pledge">
      <div>
        <h3>사진은 내 기기에만</h3>
        <p>체크인 사진과 메모는 휴대폰 안 앱 전용 저장 공간에 저장됩니다. 당사는 이를 받지도, 보지도,
          보관하지도 않습니다.</p>
      </div>
      <div>
        <h3>처리는 휴대폰 안에서</h3>
        <p>조명·각도 확인과 선택 기능인 위치 맞추기 도움은 모두 기기 안에서 실행되며, 그 결과는 어디에도
          전송되지 않습니다.</p>
      </div>
      <div>
        <h3>당사가 가진 것은 계정 정보뿐</h3>
        <p>이름, 이메일, 동의 기록만 보관합니다. 사진도, 메모도, 직접 고른 피부 고민도 아닙니다. 그런
          정보는 휴대폰에 남습니다.</p>
      </div>
      <div>
        <h3>사용 데이터 수집은 직접 켤 때만</h3>
        <p>켜지 않으면 꺼져 있습니다. 수집하는 것은 제한된 기술·사용 데이터이며 사진, 메모, 피부 고민은
          건드리지 않습니다. 켜든 끄든 앱은 똑같이 작동합니다.</p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <p class="disclaimer"><strong>Elowa는 기록 도구이며 의료기기가 아닙니다.</strong> 어떤 질병이나
      피부 질환도 진단, 치료, 완화, 예방하지 않으며, 앱의 어떤 내용도 의학적·피부과적 조언이 아닙니다.
      피부, 점, 병변이 걱정된다면 피부과 전문의나 의사와 상담하십시오.</p>
  </div>
</section>'''

LANGS = {
    "en": {
        "name": "English",
        "skip": "Skip to content",
        "nav_label": "Primary",
        "footer_label": "Footer",
        "switch_label": "Language",
        "nav": {"index.html": "Home", "privacy.html": "Privacy", "terms.html": "Terms"},
        "footer": {"index.html": "Home", "privacy.html": "Privacy Policy", "terms.html": "Terms of Service"},
        "on_this_page": "On this page",
        "updated": "Last updated {}",
        "home": {
            "title": "Elowa — see whether your skin is actually changing",
            "desc": "Elowa is a one-minute daily photo check-in that shows whether your skin is actually changing. Three guided poses, honest comparison, photos that never leave your phone.",
            "body": HOME_EN,
        },
        "privacy": {
            "src": "privacy-policy.md",
            "title": "Privacy Policy — Elowa",
            "heading": "Privacy Policy",
            "desc": "How Elowa handles your information. Your check-in photos stay on your device and are never uploaded to us.",
            "intro": "How Elowa handles your information — and why your check-in photos never leave your phone.",
        },
        "terms": {
            "src": "terms-of-service.md",
            "title": "Terms of Service — Elowa",
            "heading": "Terms of Service",
            "desc": "The agreement between you and Elowa covering your use of the Elowa mobile app.",
            "intro": "The agreement between you and Elowa covering your use of the app.",
        },
    },
    "ko": {
        "name": "한국어",
        "skip": "본문으로 건너뛰기",
        "nav_label": "주 메뉴",
        "footer_label": "바닥글 메뉴",
        "switch_label": "언어",
        "nav": {"index.html": "홈", "privacy.html": "개인정보", "terms.html": "약관"},
        "footer": {"index.html": "홈", "privacy.html": "개인정보처리방침", "terms.html": "이용약관"},
        "on_this_page": "목차",
        "updated": "최종 수정일 {}",
        "home": {
            "title": "Elowa — 내 피부 비포 애프터를 한눈에",
            "desc": "하루 1분의 체크인으로 어제와 오늘, 한 달 전과 지금을 한눈에 비교해 보세요. 사진은 휴대폰에만 남습니다.",
            "body": HOME_KO,
        },
        "privacy": {
            "src": "privacy-policy.ko.md",
            "title": "개인정보처리방침 — Elowa",
            "heading": "개인정보처리방침",
            "desc": "Elowa가 이용자의 정보를 처리하는 방법. 체크인 사진은 기기에만 남고 당사에 업로드되지 않습니다.",
            "intro": "Elowa가 정보를 어떻게 처리하는지, 그리고 체크인 사진이 휴대폰 밖으로 나가지 않는 이유.",
        },
        "terms": {
            "src": "terms-of-service.ko.md",
            "title": "이용약관 — Elowa",
            "heading": "이용약관",
            "desc": "Elowa 모바일 앱 이용에 관한 이용자와 Elowa 사이의 약관.",
            "intro": "앱 이용에 관한 이용자와 Elowa 사이의 약속입니다.",
        },
    },
}


def published_languages():
    with open(os.path.join(ROOT, "site.json"), encoding="utf-8") as f:
        langs = json.load(f)["published_languages"]
    unknown = [l for l in langs if l not in LANGS]
    if unknown:
        sys.exit(f"site.json: unknown language(s) {unknown}; known: {list(LANGS)}")
    if DEFAULT_LANG not in langs:
        sys.exit(f"site.json: '{DEFAULT_LANG}' must stay published (shipped apps link to it)")
    return [l for l in LANGS if l in langs]  # stable order


def dir_of(lang):
    return "" if lang == DEFAULT_LANG else f"{lang}/"


def head_alternates(page, langs):
    if len(langs) < 2:
        return ""
    tail = "" if page == "index.html" else page
    links = [f'<link rel="alternate" hreflang="{l}" href="{SITE_URL}/{dir_of(l)}{tail}">' for l in langs]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{dir_of(DEFAULT_LANG)}{tail}">')
    return "\n" + "\n".join(links)


def switcher(lang, page, langs):
    if len(langs) < 2:
        return ""
    # A <details> dropdown: plain links, so it works without JavaScript.
    up = "../" if lang != DEFAULT_LANG else ""
    items = []
    for l in langs:
        name = LANGS[l]["name"]
        if l == lang:
            items.append(f'<li><a href="{page}" aria-current="true" lang="{l}">{name}</a></li>')
        else:
            items.append(f'<li><a href="{up}{dir_of(l)}{page}" hreflang="{l}" lang="{l}">{name}</a></li>')
    label = LANGS[lang]["switch_label"]
    return f'''
    <nav class="lang-switch" aria-label="{label}">
      <details class="lang-menu" id="lang-menu">
        <summary><span class="sr-only">{label}: </span>{LANGS[lang]["name"]}</summary>
        <ul>
          {"".join(items)}
        </ul>
      </details>
    </nav>
    <script>
      (function () {{
        var m = document.getElementById("lang-menu");
        document.addEventListener("click", function (e) {{ if (!m.contains(e.target)) m.open = false; }});
        document.addEventListener("keydown", function (e) {{
          if (e.key === "Escape" && m.open) {{ m.open = false; m.querySelector("summary").focus(); }}
        }});
      }})();
    </script>'''


def shell(lang, langs, page, title, desc, body):
    t = LANGS[lang]
    up = "../" if lang != DEFAULT_LANG else ""
    cur = ' aria-current="page"'
    nav = "\n        ".join(
        f'<a href="{p}"{cur if p == page else ""}>{t["nav"][p]}</a>' for p in PAGES)
    footer = "\n      ".join(f'<a href="{p}">{t["footer"][p]}</a>' for p in PAGES)
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#722164">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="{up}assets/img/logo.svg" type="image/svg+xml">
<link rel="stylesheet" href="{up}assets/css/style.css">{head_alternates(page, langs)}
</head>
<body>
<a class="skip-link" href="#main">{t["skip"]}</a>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="index.html">{MARK}<span>Elowa</span></a>
    <nav class="site-nav" aria-label="{t["nav_label"]}">
        {nav}
    </nav>{switcher(lang, page, langs)}
  </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    <p>&copy; 2026 Elowa &middot; <a href="mailto:hello.elowa@gmail.com">hello.elowa@gmail.com</a></p>
    <nav aria-label="{t["footer_label"]}">
      {footer}
    </nav>
  </div>
</footer>
</body>
</html>
'''


def clean(md):
    # HTML comments hold internal drafting notes (the Korean drafts open with one).
    md = re.sub(r"<!--.*?-->", "", md, flags=re.S).lstrip()
    # The "초안 — 게시 전" (draft, not in effect) notice the Korean drafts carry
    # for reviewers. A page is only built once its language is published, so
    # the notice is never true on the site.
    md = re.sub(r"^>\s*\*\*초안[^\n]*\n(?:>[^\n]*\n)*\n*", "", md, flags=re.M)
    # Internal drafting commentary that must not appear on a live site:
    # the "not reviewed by an attorney" footnote and the BC-counsel aside in Terms §13.
    md = re.sub(r"\n---\s*\n+\*This document is a starting draft.*$", "\n", md, flags=re.S)
    md = re.sub(r"\n\*\*Two things worth flagging.*?(?=\n## )", "\n", md, flags=re.S)
    return md


def legal(lang, langs, key, page):
    t = LANGS[lang]
    d = t[key]
    path = os.path.join(SRC, d["src"])
    if not os.path.exists(path):
        sys.exit(f"missing {path} (language '{lang}' is published in site.json)")
    with open(path, encoding="utf-8") as f:
        md = clean(f.read())
    m = re.search(r"^\*\*(?:Last updated|최종 수정일):\*\*\s*(.+)$", md, re.M)
    updated = m.group(1).strip() if m else ""
    md = re.sub(r"^\*\*(?:Last updated|최종 수정일):\*\*.*$", "", md, flags=re.M)
    html_body, toc = convert(md, STABLE_IDS)
    toc_html = "\n".join(f'<li><a href="#{sid}">{label}</a></li>' for sid, label in toc)
    updated_html = f'\n    <p class="updated">{t["updated"].format(updated)}</p>' if updated else ""
    body = f'''<div class="doc-header">
  <div class="wrap">
    <h1>{d["heading"]}</h1>
    <p class="doc-sub">{d["intro"]}</p>{updated_html}
  </div>
</div>
<div class="wrap doc-layout">
  <details class="toc" id="toc">
    <summary>{t["on_this_page"]}</summary>
    <nav aria-label="{t["on_this_page"]}">
      <ol>
{toc_html}
      </ol>
    </nav>
  </details>
  <article class="doc">
{html_body}
  </article>
</div>
<script>
  (function () {{
    var toc = document.getElementById("toc");
    var wide = window.matchMedia("(min-width: 900px)");
    var sync = function () {{ toc.open = wide.matches; }};
    sync();
    wide.addEventListener ? wide.addEventListener("change", sync) : wide.addListener(sync);
  }})();
</script>'''
    write(lang, page, shell(lang, langs, page, d["title"], d["desc"], body))


def write(lang, page, html):
    path = os.path.join(OUT, dir_of(lang), page)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print("wrote", os.path.relpath(path, ROOT))


def main():
    langs = published_languages()
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(OUT, "assets"))
    for lang in langs:
        h = LANGS[lang]["home"]
        write(lang, "index.html", shell(lang, langs, "index.html", h["title"], h["desc"], h["body"]))
        legal(lang, langs, "privacy", "privacy.html")
        legal(lang, langs, "terms", "terms.html")
    print("published languages:", ", ".join(langs))


if __name__ == "__main__":
    main()
