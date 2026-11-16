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

# Same paths as assets/img/logo.svg (copied from the app's assets/brand/logo.svg).
MARK = ('<svg viewBox="0 0 96 96" fill="none" aria-hidden="true" focusable="false">'
        '<path opacity="0.8" d="M82.8944 47.8737C73.9717 34.8952 60.7228 38.1399 56.1262 43.2772C51.5297 48.4145 49.655 52.5621 47.2035 56.7965C44.7521 61.0308 40.0567 65.5406 28.2949 65.5406C17.2091 65.5406 16.6316 77.7612 24.4911 84.6462C32.3507 91.5312 42.0662 94.7856 52.3408 93.8393C81.1502 91.1858 91.8171 60.8522 82.8944 47.8737Z" fill="#AD88B5" fill-opacity="0.2"/>'
        '<path d="M81.2283 45.4403C72.3055 32.4617 59.0567 35.7064 54.4601 40.8437C49.8635 45.981 47.9888 50.1287 45.5374 54.363C43.0859 58.5973 38.3905 63.1072 26.6288 63.1072C15.5429 63.1072 14.9655 75.3277 22.825 82.2127C30.6845 89.0977 40.4001 92.3522 50.6747 91.4058C79.484 88.7523 90.151 58.4188 81.2283 45.4403Z" fill="#AD88B5"/>'
        '<path d="M14.4174 50.5598C23.3401 63.5383 36.589 60.2936 41.1856 55.1563C45.7821 50.019 47.6568 45.8714 50.1083 41.637C52.5597 37.4027 57.2551 32.8929 69.0169 32.8929C80.1027 32.8929 80.6802 20.6723 72.8207 13.7873C64.9611 6.90233 55.2456 3.64786 44.971 4.59421C16.1616 7.2477 5.49467 37.5813 14.4174 50.5598Z" fill="#AD88B5" fill-opacity="0.2"/>'
        '<path d="M13.0654 48.1263C21.9882 61.1048 35.237 57.8602 39.8336 52.7229C44.4302 47.5855 45.7821 44.3409 48.7563 39.2036C51.7306 34.0662 55.9032 30.4594 67.6649 30.4594C78.7508 30.4594 79.3282 18.2388 71.4687 11.3538C63.6092 4.46886 53.8936 1.21439 43.619 2.16074C14.8097 4.81423 4.14271 35.1478 13.0654 48.1263Z" fill="#AD88B5"/>'
        '</svg>')

HOME_EN = '''<div class="hero">
  <div class="wrap">
    <p class="eyebrow">Skin progress journal</p>
    <h1>Your skin's before&nbsp;and&nbsp;after, at&nbsp;a&nbsp;glance</h1>
    <p class="lede">A one-minute daily check-in lets you compare yesterday with today, and last
      month with now.</p>
    <div class="actions">
      <a class="btn btn-outline" href="privacy.html">Where are my photos stored?</a>
    </div>
  </div>
</div>

<section>
  <div class="wrap">
    <h2 class="section-title">One minute, three photos, done</h2>
    <p class="section-intro">It's easy. Follow the on-screen guides and every photo lines up the same
      way, so you can compare even small changes.</p>
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
        <h3>Spot what changed</h3>
        <p>See what the mirror misses. Pick any two days and slide between them, or set them side by
          side — even small differences jump out.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2 class="section-title">Your photos stay on your phone</h2>
    <p class="section-intro">Rest easy: Elowa never uploads your photos. Privacy isn't something you
      switch on — it's how Elowa works.</p>
    <div class="pledge">
      <div>
        <h3>Photos stay on your device</h3>
        <p>Check-in photos and notes are saved only on your phone and never sent to Elowa.</p>
      </div>
      <div>
        <h3>Processing happens on your phone</h3>
        <p>Lighting and angle checks, and the optional reframing assist, all run on-device. Nothing
          from them is transmitted.</p>
      </div>
      <div>
        <h3>Only your account and consent record</h3>
        <p>Your name, email, and the record of the terms you agreed to. Photos, notes, and skin
          concerns stay on your phone.</p>
      </div>
      <div>
        <h3>Measurement you opt into</h3>
        <p>Off by default; turn it on only if you want to. When it's on, we collect only the minimal
          usage data needed to improve the app — never your photos, notes, or skin concerns. Every
          feature works the same with it off.</p>
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
      <a class="btn btn-outline" href="privacy.html">사진은 어디에 저장되나요?</a>
    </div>
  </div>
</div>

<section>
  <div class="wrap">
    <h2 class="section-title">하루 1분, 세 장이면 끝</h2>
    <p class="section-intro">어렵지 않습니다. 화면 안내만 따라 찍으면 매일 같은 구도로 맞춰져, 작은 변화까지 비교할 수 있습니다.</p>
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
        <h3>달라진 점 발견하기</h3>
        <p>거울로는 몰랐던 변화, 사진으로 확인하세요. 원하는 두 날을 골라 슬라이더로 넘겨 보거나 나란히
          놓고 보면, 작은 차이도 바로 눈에 들어옵니다.</p>
      </div>
    </div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <h2 class="section-title">사진은 내 폰에만</h2>
    <p class="section-intro">안심하세요. Elowa는 사진을 서버에 올리지 않습니다. 개인정보 보호는 따로
      켜는 기능이 아니라 Elowa의 기본입니다.</p>
    <div class="pledge">
      <div>
        <h3>사진은 내 기기에만</h3>
        <p>체크인 사진과 메모는 내 휴대폰에만 저장되며, Elowa로 전송되지 않습니다.</p>
      </div>
      <div>
        <h3>처리는 휴대폰 안에서</h3>
        <p>조명·각도 확인과 위치 맞추기 도움은 모두 기기 안에서 처리되며, 결과는 어디에도 전송되지
          않습니다.</p>
      </div>
      <div>
        <h3>계정 정보와 동의 내역만 보관</h3>
        <p>이름, 이메일, 약관 동의 내역만 보관합니다. 사진, 메모, 피부 고민은 휴대폰에만 남습니다.</p>
      </div>
      <div>
        <h3>사용 데이터 수집은 직접 켤 때만</h3>
        <p>기본으로 꺼져 있고, 원할 때만 켤 수 있습니다. 켜면 앱 개선에 필요한 최소한의 사용 데이터만
          모으며, 사진·메모·피부 고민은 수집하지 않습니다. 켜지 않아도 모든 기능을 그대로 쓸 수
          있습니다.</p>
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
            "title": "Elowa — your skin's before and after, at a glance",
            "desc": "A one-minute daily check-in to compare yesterday with today, and last month with now. Your photos stay on your phone.",
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
<link rel="apple-touch-icon" href="{up}assets/img/apple-touch-icon.png">
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
