from pathlib import Path


def test_news_uses_stable_internal_filter_values_and_english_labels():
    source = Path('views/news.py').read_text(encoding='utf-8')
    assert '["today", "24_hours", "3_days", "7_days", "30_days", "all", "custom"]' in source
    assert 'News settings' in source
    assert 'Newest first' in source
    assert 'country_label(value, ui_language)' in source
    assert 'category_label(value, ui_language)' in source


def test_settings_forces_rerun_after_preference_change():
    source = Path('views/settings.py').read_text(encoding='utf-8')
    assert 'selected_theme != st.session_state.get("theme")' in source
    assert 'selected_language != st.session_state.get("language")' in source
    assert 'st.rerun()' in source


def test_light_theme_overrides_streamlit_shell_and_sidebar():
    source = Path('assets/styles.py').read_text(encoding='utf-8')
    assert "color-scheme:{'light' if light else 'dark'}" in source
    assert '[data-testid="stAppViewContainer"]' in source
    assert 'background-color:var(--bg)!important' in source
    assert 'section[data-testid="stSidebar"]' in source


def test_major_pages_have_english_ui_variants():
    expected = {
        'views/news.py': ['Smart News Center', 'News settings', 'Search topic'],
        'views/people.py': ['People Intelligence', 'Information language', 'Search'],
        'views/entities.py': ['Entity Analysis', 'Entity type', 'Result language'],
        'views/compare.py': ['Comparison Center', 'Comparison type', 'Run comparison'],
        'views/ai_chat.py': ['AI Assistant', 'New conversation', 'Write your question'],
        'views/account.py': ['Account Center', 'Search history', 'Save settings'],
    }
    for filename, phrases in expected.items():
        source = Path(filename).read_text(encoding='utf-8')
        for phrase in phrases:
            assert phrase in source, f'{phrase!r} missing from {filename}'
