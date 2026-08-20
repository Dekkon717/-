"""将 Skill 源码打包为可分发 ZIP；不重复嵌套已有压缩包。"""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--output", default="dist/fujian-ip-litigation-skill.zip")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
output = root / args.output
output.parent.mkdir(parents=True, exist_ok=True)
skip_parts = {".git", "__pycache__", "dist", ".venv"}
with ZipFile(output, "w", ZIP_DEFLATED) as zf:
    for path in root.rglob("*"):
        if not path.is_file() or any(part in skip_parts for part in path.parts):
            continue
        zf.write(path, path.relative_to(root).as_posix())
print(f"已生成：{output}")
