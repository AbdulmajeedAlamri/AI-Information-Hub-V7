from pathlib import Path


def test_mobile_sidebar_is_overlay_and_fully_collapsible():
    styles = Path("assets/styles.py").read_text(encoding="utf-8")
    assert 'section[data-testid="stSidebar"][aria-expanded="true"]' in styles
    assert 'width:min(88vw,330px)!important' in styles
    assert 'section[data-testid="stSidebar"][aria-expanded="false"]' in styles
    assert 'flex:0 0 0!important' in styles
    assert 'visibility:hidden!important' in styles


def test_identity_email_isolated_from_rtl():
    styles = Path("assets/styles.py").read_text(encoding="utf-8")
    sidebar = Path("components/sidebar.py").read_text(encoding="utf-8")
    assert 'direction:ltr!important' in styles
    assert 'unicode-bidi:isolate!important' in styles
    assert 'user-email' in sidebar
