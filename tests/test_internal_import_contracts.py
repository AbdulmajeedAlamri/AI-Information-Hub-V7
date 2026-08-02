from pathlib import Path
import ast

def names(path):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    return {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}

def test_entity_service_contract():
    exported = names("services/entity_service.py")
    assert "get_entity_profile" in exported
    assert "search_entity" in exported

def test_page_entry_points():
    expected = {
        "views/home.py": "render_home",
        "views/dashboard.py": "render_dashboard",
        "views/news.py": "render_news",
        "views/people.py": "render_people",
        "views/compare.py": "render_compare",
        "views/entities.py": "render_entities",
        "views/ai_chat.py": "render_ai_chat",
        "views/account.py": "render_account",
        "views/settings.py": "render_settings",
    }
    for path, function_name in expected.items():
        assert function_name in names(path)
