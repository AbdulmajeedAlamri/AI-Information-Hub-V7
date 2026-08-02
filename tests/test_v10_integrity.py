from pathlib import Path
import ast

ROOT=Path(__file__).resolve().parents[1]

def test_all_routes_exist():
    for name in ["home","dashboard","news","people","compare","entities","ai_chat","account","settings"]:
        assert (ROOT/"views"/f"{name}.py").exists()

def test_v11_branding_and_no_real_secrets():
    assert "Aurora Intelligence V11" in (ROOT/"app.py").read_text(encoding="utf-8")
    assert not (ROOT/".streamlit"/"secrets.toml").exists()

def test_python_ast():
    for path in ROOT.rglob("*.py"):
        ast.parse(path.read_text(encoding="utf-8"),filename=str(path))
