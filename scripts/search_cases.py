"""对本地案例库进行可解释的字段加权检索。"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date

from case_db import connect, parse_json_fields, query_terms, snippet


FIELD_WEIGHTS = {
    "title": 7.0,
    "disputed_issues": 6.0,
    "key_rules": 6.0,
    "defenses": 5.0,
    "comparison": 4.5,
    "infringing_acts": 4.0,
    "evidence": 3.5,
    "material_facts": 3.0,
    "court_reasoning": 2.0,
    "full_text": 1.0,
}

AUTHORITY_BONUS = {1: 5.0, 2: 4.0, 3: 3.0, 4: 2.5, 5: 1.5, 6: 0.5}


def build_filters(args: argparse.Namespace) -> tuple[str, list[object]]:
    clauses = ["is_active = 1"]
    values: list[object] = []
    if args.court:
        clauses.append("court LIKE ?")
        values.append(f"%{args.court}%")
    if args.cause:
        clauses.append("cause_of_action LIKE ?")
        values.append(f"%{args.cause}%")
    if args.procedure:
        clauses.append("procedure = ?")
        values.append(args.procedure)
    if args.year_from:
        clauses.append("judgment_date >= ?")
        values.append(f"{args.year_from}-01-01")
    if args.year_to:
        clauses.append("judgment_date <= ?")
        values.append(f"{args.year_to}-12-31")
    return " AND ".join(clauses), values


def occurrence_score(value: object, terms: list[str], weight: float) -> float:
    if value is None:
        return 0.0
    text = str(value).lower()
    score = 0.0
    for term in terms:
        count = text.count(term.lower())
        if count:
            score += weight * min(count, 3)
    return score


def recency_bonus(judgment_date: str) -> float:
    try:
        years = max(0, (date.today() - date.fromisoformat(judgment_date)).days / 365.25)
        return max(0.0, 1.5 - years * 0.15)
    except ValueError:
        return 0.0


def main() -> int:
    parser = argparse.ArgumentParser(description="搜索福建商标案例")
    parser.add_argument("--db", required=True, help="SQLite 数据库路径")
    parser.add_argument("--query", required=True, help="自然语言检索词")
    parser.add_argument("--court", help="法院关键词")
    parser.add_argument("--cause", help="案由关键词")
    parser.add_argument("--procedure", help="一审、二审或再审")
    parser.add_argument("--year-from", type=int, help="起始年份")
    parser.add_argument("--year-to", type=int, help="结束年份")
    parser.add_argument("--limit", type=int, default=10, help="返回数量，默认10")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    terms = query_terms(args.query)
    if not terms:
        print("错误：query 没有可检索的词语。", file=sys.stderr)
        return 2
    try:
        conn = connect(args.db)
    except (OSError, FileNotFoundError) as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 2

    where, values = build_filters(args)
    rows = conn.execute(f"SELECT * FROM cases WHERE {where}", values).fetchall()
    conn.close()

    ranked: list[dict[str, object]] = []
    for raw_row in rows:
        row = parse_json_fields(dict(raw_row))
        score = sum(
            occurrence_score(row.get(field), terms, weight)
            for field, weight in FIELD_WEIGHTS.items()
        )
        score += AUTHORITY_BONUS.get(int(row["source_tier"]), 0.0)
        if row.get("effective_status") == "已生效":
            score += 2.0
        if row.get("law_version_status") == "现行":
            score += 1.0
        if row.get("review_status") == "人工复核":
            score += 1.0
        score += recency_bonus(str(row.get("judgment_date", "")))
        if score <= 0:
            continue
        ranked.append(
            {
                "score": round(score, 4),
                "case_id": row["case_id"],
                "title": row["title"],
                "case_number": row["case_number"],
                "court": row["court"],
                "province": row["province"],
                "city": row["city"],
                "case_type": row["case_type"],
                "judgment_date": row["judgment_date"],
                "procedure": row["procedure"],
                "cause_of_action": row["cause_of_action"],
                "effective_status": row["effective_status"],
                "source_type": row["source_type"],
                "source_tier": row["source_tier"],
                "source_url": row["source_url"],
                "disposition": row["disposition"],
                "key_rules": row.get("key_rules", []),
                "snippet": snippet(str(row.get("full_text", "")), terms),
            }
        )
    ranked.sort(key=lambda item: (-float(item["score"]), int(item["source_tier"])))
    result = {
        "query": args.query,
        "terms": terms,
        "filters": {
            "court": args.court,
            "cause": args.cause,
            "procedure": args.procedure,
            "year_from": args.year_from,
            "year_to": args.year_to,
        },
        "count": min(len(ranked), max(0, args.limit)),
        "warning": "这是第一版可解释关键词检索，不是法律结论，也不使用裁判结果作为相似度条件。",
        "results": ranked[: max(0, args.limit)],
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"检索词：{args.query}；结果：{result['count']} 条")
        for index, item in enumerate(result["results"], start=1):
            print(f"{index}. {item['title']} | {item['case_number']} | {item['court']}")
            print(f"   得分 {item['score']}；来源等级 {item['source_tier']}；{item['disposition']}")
            print(f"   {item['snippet']}")
            print(f"   {item['source_url']}")
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
