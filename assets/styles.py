from __future__ import annotations

import streamlit as st


def apply_styles(theme: str, language: str = "ar") -> None:
    light = theme == "light"
    direction = "rtl" if language == "ar" else "ltr"
    p = {
        "bg": "#F4F7FC" if light else "#070A16",
        "bg2": "#EAF0FA" if light else "#0B1022",
        "surface": "rgba(255,255,255,.90)" if light else "rgba(15,21,45,.78)",
        "surface2": "#FFFFFF" if light else "#101731",
        "surface3": "#EDF2FC" if light else "#151E3C",
        "text": "#11182D" if light else "#F7F8FF",
        "muted": "#68738B" if light else "#97A1BD",
        "border": "rgba(32,50,96,.11)" if light else "rgba(145,164,230,.14)",
        "shadow": "0 24px 70px rgba(26,42,84,.13)" if light else "0 30px 80px rgba(0,0,0,.42)",
    }
    st.markdown(f"""
<style>
:root {{
  --bg:{p['bg']};--bg2:{p['bg2']};--surface:{p['surface']};--surface2:{p['surface2']};--surface3:{p['surface3']};
  --text:{p['text']};--muted:{p['muted']};--border:{p['border']};--shadow:{p['shadow']};
  --blue:#4F7CFF;--blue2:#6E9BFF;--violet:#9B6CFF;--cyan:#28D6E7;--amber:#FFB454;--rose:#FF6B91;--green:#34D399;
  --r-xl:30px;--r-lg:22px;--r-md:15px;
}}
*{{box-sizing:border-box}}
html{{color-scheme:{'light' if light else 'dark'};scroll-behavior:smooth}}
html,body,.stApp,[data-testid="stApp"],[data-testid="stAppViewContainer"]{{direction:{direction};color:var(--text)!important;background:var(--bg)!important;background-color:var(--bg)!important}}
body{{margin:0}}
[data-testid="stAppViewContainer"]{{
 background:
 radial-gradient(circle at 12% -8%,rgba(79,124,255,.20),transparent 31%),
 radial-gradient(circle at 98% 5%,rgba(155,108,255,.17),transparent 29%),
 radial-gradient(circle at 42% 112%,rgba(40,214,231,.09),transparent 32%),
 linear-gradient(145deg,var(--bg),var(--bg2));
}}
[data-testid="stHeader"]{{background:transparent!important}}
[data-testid="stDecoration"],[data-testid="stBottom"]{{background:transparent!important}}
[data-testid="stToolbar"]{{right:1rem}}
.block-container{{max-width:1520px;padding:1.15rem 2rem 5rem}}
h1,h2,h3,h4,h5,p,label,span,li{{color:var(--text)}}
a{{color:var(--blue2)}}
.muted{{color:var(--muted)!important}}.rtl{{direction:rtl;text-align:right}}.ltr{{direction:ltr;text-align:left}}

/* Shell and sidebar */
section[data-testid="stSidebar"]{{background:linear-gradient(180deg,rgba(79,124,255,.08),transparent 34%),var(--bg)!important;border-inline-end:1px solid var(--border)!important}}
section[data-testid="stSidebar"]>div{{padding:1rem .9rem 1.5rem!important}}
.sidebar-brand{{position:relative;overflow:hidden;padding:17px;border-radius:22px;background:linear-gradient(145deg,rgba(79,124,255,.13),rgba(155,108,255,.07)),var(--surface);border:1px solid var(--border);box-shadow:var(--shadow);margin-bottom:14px}}
.sidebar-brand:after{{content:"";position:absolute;width:110px;height:110px;border-radius:50%;inset:-55px -35px auto auto;background:radial-gradient(circle,rgba(40,214,231,.30),transparent 70%)}}
.brand-row{{display:flex;align-items:center;gap:12px;position:relative;z-index:1}}
.brand-mark{{width:45px;height:45px;border-radius:16px;display:grid;place-items:center;background:linear-gradient(135deg,var(--blue),var(--violet));box-shadow:0 12px 28px rgba(79,124,255,.36);color:#fff;font-weight:900;font-size:18px}}
.brand-row h3{{font-size:14px;margin:0;letter-spacing:.01em}}.brand-row p{{font-size:9px;margin:4px 0 0;color:var(--muted);letter-spacing:.14em}}
.user-shell{{min-width:0;overflow:hidden;padding:13px;border-radius:18px;background:var(--surface);border:1px solid var(--border);margin:12px 0}}
.user-shell strong{{display:block;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.user-email{{display:block!important;direction:ltr!important;unicode-bidi:isolate!important;text-align:left!important;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:11px;line-height:1.8}}
.user-shell small{{display:block;margin-top:7px;color:var(--muted)}}
.online-dot{{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--green);box-shadow:0 0 14px rgba(52,211,153,.8)}}
section[data-testid="stSidebar"] [role="radiogroup"]{{gap:5px}}
section[data-testid="stSidebar"] [role="radiogroup"] label{{min-height:43px;padding:8px 10px;border-radius:14px;border:1px solid transparent;transition:.2s ease}}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover{{background:rgba(79,124,255,.09);border-color:rgba(79,124,255,.17);transform:translateX(-2px)}}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){{background:linear-gradient(120deg,rgba(79,124,255,.18),rgba(155,108,255,.09));border-color:rgba(110,155,255,.28)}}
section[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p{{color:var(--blue2)!important;font-weight:850}}

/* Universal panels */
.glass{{background:linear-gradient(145deg,rgba(255,255,255,.035),rgba(255,255,255,.005)),var(--surface);border:1px solid var(--border);box-shadow:var(--shadow);backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);animation:enter .42s ease both}}
@keyframes enter{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:none}}}}

/* Page header */
.page-head{{position:relative;overflow:hidden;padding:32px 34px;border-radius:26px;margin:0 0 18px;background:linear-gradient(112deg,rgba(79,124,255,.15),rgba(155,108,255,.08)),var(--surface)}}
.page-head:before{{content:"";position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:38px 38px;mask-image:linear-gradient(to left,black,transparent 65%)}}
.page-head:after{{content:"";position:absolute;width:240px;height:240px;border-radius:50%;inset:-130px -75px auto auto;background:radial-gradient(circle,rgba(40,214,231,.25),transparent 68%)}}
.page-head>*{{position:relative;z-index:1}}.page-kicker,.hero-kicker{{font-size:10px;letter-spacing:.2em;font-weight:900;color:var(--cyan)!important;text-transform:uppercase}}
.page-head h1{{font-size:clamp(32px,4vw,51px);margin:9px 0 6px;letter-spacing:-1.4px}}.page-head p{{margin:0;max-width:840px;color:var(--muted);line-height:1.8}}

/* Home Aurora hero */
.hero-v10{{position:relative;overflow:hidden;border-radius:32px;padding:58px 54px;margin-bottom:18px;background:linear-gradient(115deg,rgba(79,124,255,.18),rgba(155,108,255,.09) 55%,rgba(40,214,231,.06)),var(--surface)}}
.hero-v10:before{{content:"";position:absolute;inset:0;background-image:radial-gradient(circle at 1px 1px,rgba(255,255,255,.10) 1px,transparent 0);background-size:25px 25px;mask-image:linear-gradient(90deg,transparent,black)}}
.hero-v10:after{{content:"";position:absolute;width:390px;height:390px;border-radius:50%;inset:-190px -90px auto auto;background:radial-gradient(circle,rgba(79,124,255,.36),rgba(155,108,255,.12) 45%,transparent 70%)}}
.hero-grid{{position:relative;z-index:2;display:grid;grid-template-columns:1.15fr .85fr;gap:34px;align-items:center}}
.hero-v10 h1{{font-size:clamp(46px,6vw,80px);line-height:1.02;margin:12px 0 16px;letter-spacing:-3px;max-width:860px}}
.hero-v10 p{{font-size:17px;line-height:1.9;max-width:760px;color:var(--muted)}}
.status-row{{display:flex;gap:9px;flex-wrap:wrap;margin-top:23px}}
.status-pill{{display:flex;gap:7px;align-items:center;padding:8px 12px;border-radius:999px;background:rgba(79,124,255,.09);border:1px solid rgba(110,155,255,.21);font-size:11px;font-weight:750}}
.hero-visual{{height:285px;position:relative;border-radius:27px;overflow:hidden;background:linear-gradient(145deg,rgba(10,14,34,.65),rgba(24,31,66,.55));border:1px solid rgba(151,171,235,.16);box-shadow:inset 0 0 50px rgba(79,124,255,.08)}}
.hero-visual:before,.hero-visual:after{{content:"";position:absolute;inset:24px;border:1px solid rgba(110,155,255,.23);border-radius:50%;transform:rotate(-16deg)}}
.hero-visual:after{{inset:54px;transform:rotate(33deg);border-color:rgba(155,108,255,.25)}}
.orb{{position:absolute;border-radius:50%}}.orb.a{{width:126px;height:126px;right:40px;top:37px;background:linear-gradient(135deg,var(--blue),var(--cyan));box-shadow:0 25px 80px rgba(79,124,255,.55)}}
.orb.b{{width:79px;height:79px;left:38px;bottom:38px;background:linear-gradient(135deg,var(--violet),var(--rose));box-shadow:0 20px 55px rgba(155,108,255,.43)}}
.orbit{{position:absolute;inset:0}}.visual-label{{position:absolute;z-index:4;left:23px;top:21px;color:white;font-size:10px;font-weight:900;letter-spacing:.16em}}

/* Bento system */
.welcome-card,.quick-card,.feature-card,.analysis-card,.chat-shell,.profile-card,.entity-card,.stat-card,.health-card,.timeline-card,.home-metric{{border-radius:22px;padding:21px;margin-bottom:13px}}
.welcome-card{{min-height:146px;display:flex;align-items:center;justify-content:space-between;background:linear-gradient(115deg,rgba(79,124,255,.12),transparent 63%),var(--surface)}}
.welcome-card h2{{font-size:clamp(27px,3vw,42px);margin:6px 0}}.eyebrow{{color:var(--amber)!important;font-size:10px;font-weight:900;letter-spacing:.16em;text-transform:uppercase}}
.welcome-orb{{width:72px;height:72px;border-radius:24px;display:grid;place-items:center;background:linear-gradient(135deg,var(--blue),var(--violet));color:#fff;font-size:25px;box-shadow:0 22px 50px rgba(79,124,255,.27)}}
.home-metric{{min-height:110px;display:flex;align-items:center;gap:14px;background:linear-gradient(145deg,rgba(79,124,255,.06),transparent),var(--surface)}}
.metric-icon{{width:47px;height:47px;flex:0 0 47px;border-radius:16px;display:grid;place-items:center;background:linear-gradient(135deg,rgba(79,124,255,.19),rgba(155,108,255,.13));font-size:21px}}
.home-metric strong{{font-size:29px;display:block;line-height:1}}.home-metric span{{font-size:11px;color:var(--muted)}}
.section-heading{{display:flex;align-items:end;justify-content:space-between;gap:20px;margin:31px 0 14px}}.section-heading>div{{display:flex;align-items:center;gap:10px}}.section-heading h2{{margin:0}}.section-heading p{{margin:0;color:var(--muted)}}
.section-dot{{width:10px;height:10px;border-radius:50%;background:var(--amber);box-shadow:0 0 18px rgba(255,180,84,.7)}}
.quick-card,.feature-card{{min-height:205px;position:relative;overflow:hidden;transition:.22s ease}}
.quick-card:after,.feature-card:after{{content:"";position:absolute;width:120px;height:120px;border-radius:50%;inset:auto -55px -65px auto;background:radial-gradient(circle,rgba(79,124,255,.18),transparent 70%)}}
.quick-card:hover,.feature-card:hover{{transform:translateY(-5px);border-color:rgba(110,155,255,.31);box-shadow:0 28px 75px rgba(0,0,0,.29)}}
.quick-top,.feature-card-top{{display:flex;align-items:center;justify-content:space-between}}.quick-top span,.feature-card-top span{{font-size:9px;color:var(--cyan);letter-spacing:.12em}}
.feature-icon{{font-size:30px}}.quick-card p,.feature-card p{{color:var(--muted);line-height:1.75}}
.stat-card h2{{font-size:38px;margin:8px 0 0}}.service-strip{{display:flex;gap:13px;flex-wrap:wrap;border-radius:17px;padding:15px 18px}}
.metrics{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.metric{{padding:18px;border-radius:18px}}.metric strong{{display:block;margin-bottom:8px}}
.analysis-card p,.analysis-card li{{line-height:1.85}}.analysis-summary .summary-line{{margin:.45rem 0;line-height:1.9}}.timeline-item{{border-inline-start:2px solid var(--blue);padding-inline-start:16px}}
.meta{{display:flex;gap:7px;flex-wrap:wrap}}.meta span{{padding:6px 9px;border-radius:999px;background:rgba(79,124,255,.10);border:1px solid rgba(110,155,255,.18);font-size:11px}}
.chat-message{{padding:16px 18px;border-radius:18px;margin:10px 0;background:var(--surface3);border:1px solid var(--border)}}

/* Native Streamlit controls */
.stButton>button,.stDownloadButton>button,.stLinkButton>a{{min-height:43px;border-radius:14px!important;color:var(--text)!important;background:var(--surface2)!important;border:1px solid var(--border)!important;box-shadow:none!important;transition:.18s ease}}
.stButton>button:hover,.stDownloadButton>button:hover,.stLinkButton>a:hover{{border-color:rgba(110,155,255,.45)!important;background:rgba(79,124,255,.10)!important;transform:translateY(-1px)}}
.stButton>button[kind="primary"],button[data-testid="stBaseButton-primary"]{{color:#fff!important;background:linear-gradient(135deg,var(--blue),var(--violet))!important;border-color:transparent!important;box-shadow:0 13px 32px rgba(79,124,255,.28)!important}}
.stTextInput input,.stTextArea textarea,[data-baseweb="select"]>div,.stDateInput input,.stNumberInput input{{border-radius:14px!important;background:var(--surface2)!important;color:var(--text)!important;border-color:var(--border)!important}}
.stTextInput input:focus,.stTextArea textarea:focus,[data-baseweb="select"]>div:focus-within{{border-color:var(--blue)!important;box-shadow:0 0 0 1px var(--blue)!important}}
[data-baseweb="popover"],[role="listbox"]{{background:var(--surface2)!important;color:var(--text)!important;border:1px solid var(--border)!important}}
[data-testid="stAlert"]{{border-radius:16px!important;border:1px solid var(--border)!important}}[data-testid="stDataFrame"]{{border-radius:17px;overflow:hidden;border:1px solid var(--border)}}
.stTabs [data-baseweb="tab-list"]{{gap:7px;background:var(--surface);border:1px solid var(--border);border-radius:16px;padding:5px}}.stTabs [data-baseweb="tab"]{{border-radius:11px}}.stTabs [aria-selected="true"]{{background:rgba(79,124,255,.14)!important;color:var(--blue2)!important}}
hr{{border-color:var(--border)!important}}code,pre{{background:var(--surface3)!important;color:var(--text)!important;border-radius:14px!important}}
.app-footer{{text-align:center;color:var(--muted);font-size:10px;padding:28px 0 5px;letter-spacing:.08em}}

@media(max-width:980px){{.hero-grid{{grid-template-columns:1fr}}.hero-visual{{height:220px}}.metrics{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:760px){{
 section[data-testid="stSidebar"][aria-expanded="true"]{{width:min(88vw,330px)!important;min-width:min(88vw,330px)!important;max-width:min(88vw,330px)!important;flex-basis:min(88vw,330px)!important;visibility:visible!important;overflow-x:hidden!important}}
 section[data-testid="stSidebar"][aria-expanded="false"]{{width:0!important;min-width:0!important;max-width:0!important;flex:0 0 0!important;margin:0!important;padding:0!important;border:0!important;overflow:hidden!important;visibility:hidden!important;opacity:0!important;pointer-events:none!important;transform:translateX(-110%)!important}}
 section[data-testid="stSidebar"][aria-expanded="false"]>div{{width:0!important;min-width:0!important;max-width:0!important;padding:0!important;overflow:hidden!important}}
 [data-testid="stAppViewContainer"],[data-testid="stAppViewBlockContainer"]{{width:100%!important;max-width:100vw!important;margin:0!important;overflow-x:hidden!important}}
 .block-container{{padding:.75rem .85rem 4rem}}.hero-v10{{padding:35px 22px;border-radius:25px}}.hero-v10 h1{{font-size:42px;letter-spacing:-1.7px}}.hero-v10 p{{font-size:14px}}.hero-visual{{display:none}}.page-head{{padding:26px 22px;border-radius:22px}}.page-head h1{{font-size:34px}}
 .welcome-card{{align-items:flex-start;min-height:125px}}.welcome-orb{{display:none}}.section-heading{{align-items:start;flex-direction:column}}.metrics{{grid-template-columns:1fr}}
}}
</style>
""", unsafe_allow_html=True)
