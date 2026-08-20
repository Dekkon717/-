"""兼容 GitHub Actions 的 Skill 结构校验入口。"""
from pathlib import Path
import runpy
import sys

validator = Path.home() / ".codex" / "skills" / ".system" / "skill-creator" / "scripts" / "quick_validate.py"
if validator.exists():
    sys.argv = [str(validator), *(sys.argv[1:] or ["."])]
    runpy.run_path(str(validator), run_name="__main__")
else:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    skill = root / "SKILL.md"
    if not skill.exists():
        raise SystemExit("缺少 SKILL.md")
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---") or "name:" not in text or "description:" not in text:
        raise SystemExit("SKILL.md frontmatter 不完整")
    print("基础结构校验通过")
