from pathlib import Path


def test_v11_uses_new_aurora_identity():
    home = Path("views/home.py").read_text(encoding="utf-8")
    common = Path("components/common.py").read_text(encoding="utf-8")
    sidebar = Path("components/sidebar.py").read_text(encoding="utf-8")
    assert "AURORA FLOW" in home
    assert "AURORA INTELLIGENCE OS · V11" in common
    assert "Aurora Intelligence" in sidebar


def test_new_design_has_bento_and_native_control_styling():
    css = Path("assets/styles.py").read_text(encoding="utf-8")
    for token in ["hero-v10", "welcome-card", "quick-card", "feature-card", "stBaseButton-primary", "stTabs"]:
        assert token in css
