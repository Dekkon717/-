"""初始化福建商标案例 SQLite 数据库。"""

from __future__ import annotations

import argparse
import sys

from case_db import create_database


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化福建商标案例数据库")
    parser.add_argument("--db", required=True, help="SQLite 数据库路径")
    args = parser.parse_args()
    path, tokenizer = create_database(args.db)
    print(f"数据库已初始化：{path}")
    print(f"全文索引分词器：{tokenizer}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
