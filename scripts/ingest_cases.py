"""将结构化 JSON 或 JSONL 案例导入数据库。"""

from __future__ import annotations

import argparse
import sys

from case_db import (
    connect,
    detect_sensitive,
    load_input,
    normalize_case,
    upsert_case,
    validate_case,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="导入福建商标案例")
    parser.add_argument("--db", required=True, help="SQLite 数据库路径")
    parser.add_argument("--input", required=True, help="JSON、JSON 数组或 JSONL 文件")
    parser.add_argument("--replace", action="store_true", help="更新同一 case_id 的现有记录")
    parser.add_argument(
        "--allow-sensitive",
        action="store_true",
        help="允许导入疑似敏感信息，仅可在确认已经误报或具备合法处理依据时使用",
    )
    args = parser.parse_args()

    try:
        raw_cases = load_input(args.input)
        conn = connect(args.db)
    except (OSError, ValueError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    inserted = 0
    updated = 0
    failures: list[str] = []
    try:
        for index, raw in enumerate(raw_cases, start=1):
            label = str(raw.get("case_id") or f"第{index}条")
            errors = validate_case(raw)
            sensitive = detect_sensitive(str(raw.get("full_text", "")))
            if sensitive and not args.allow_sensitive:
                errors.append("正文包含" + "、".join(sensitive) + "，请先脱敏")
            if errors:
                failures.append(f"{label}：" + "；".join(errors))
                continue
            try:
                normalized = normalize_case(raw)
                action = upsert_case(conn, normalized, replace=args.replace)
                inserted += action == "inserted"
                updated += action == "updated"
            except (ValueError, TypeError) as exc:
                failures.append(f"{label}：{exc}")
        if failures:
            conn.rollback()
        else:
            conn.commit()
    finally:
        conn.close()

    if failures:
        print("导入未执行，以下记录需要修正：", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"导入完成：新增 {inserted} 条，更新 {updated} 条。")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
