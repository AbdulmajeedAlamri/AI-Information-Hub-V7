from pathlib import Path


def test_aurora_brand_palette_is_configured():
    config = Path(".streamlit/config.toml").read_text(encoding="utf-8")
    css = Path("assets/styles.py").read_text(encoding="utf-8")
    assert 'primaryColor = "#4F7CFF"' in config
    assert '--blue:#4F7CFF' in css
    assert '--violet:#9B6CFF' in css
    assert '--cyan:#28D6E7' in css


def test_responsive_shell_prevents_horizontal_overflow():
    css = Path("assets/styles.py").read_text(encoding="utf-8")
    assert 'max-width:100vw!important' in css
    assert 'overflow-x:hidden!important' in css
