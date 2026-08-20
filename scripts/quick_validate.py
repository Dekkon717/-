"""无需第三方依赖的 Skill 快速校验器。"""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
skill = root / "SKILL.md"
errors = []
if not skill.exists():
    errors.append("缺少 SKILL.md")
else:
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---"):
        errors.append("SKILL.md 缺少 YAML frontmatter 起始标记")
    if "\n---" not in text[3:]:
        errors.append("SKILL.md 缺少 YAML frontmatter 结束标记")
    for key in ("name:", "description:"):
        if not re.search(rf"^\s*{re.escape(key)}\s*.+$", text, re.M):
            errors.append(f"frontmatter 缺少 {key}")
for required in ("agents/openai.yaml", "references/domain-routing.md", "scripts/search_cases.py"):
    if not (root / required).exists():
        errors.append(f"缺少必需文件：{required}")
if errors:
    for error in errors:
        print(f"错误：{error}")
    raise SystemExit(1)
print(f"Skill 结构校验通过：{root}")
