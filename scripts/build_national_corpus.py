"""将福建基础库与北大法宝全国检索索引合并为全国知识产权案例库。"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urljoin


def province_for(court: str) -> str:
    if "福建" in court:
        return "福建省"
    prefixes = {
        "浙江": "浙江省", "江苏": "江苏省", "湖北": "湖北省", "四川": "四川省",
        "江西": "江西省", "重庆": "重庆市", "广东": "广东省", "北京": "北京市",
        "安徽": "安徽省", "天津": "天津市", "山东": "山东省", "湖南": "湖南省",
        "上海": "上海市", "海南": "海南省",
    }
    for key, value in prefixes.items():
        if key in court:
            return value
    if "最高人民法院" in court or "知识产权法院" in court:
        return "全国"
    return "全国"


def cause(category: str) -> str:
    return {
        "商标": "侵害商标权纠纷",
        "著作权": "著作权侵权纠纷",
        "专利": "专利权权属、侵权纠纷或确认不侵害专利权纠纷",
        "不正当竞争": "不正当竞争纠纷",
        "商业秘密": "侵害商业秘密纠纷",
        "植物新品种": "植物新品种权权属、侵权纠纷",
    }.get(category, category)


def make_case(lead: dict, base_url: str, obtained: str) -> dict:
    source_url = base_url.rstrip("/") + lead["path"]
    text = (
        f"北大法宝司法案例检索索引：{lead['title']}；案号：{lead['case_number']}；"
        f"审结日期：{lead['date']}；审理法院：{lead['court']}。"
        "该条为登录数据库检索到的索引记录，全文、证据、裁判理由、主文和生效状态尚未导出，"
        "必须在正式法律意见中回到原文二次核验。"
    )
    return {
        "case_id": lead["id"],
        "title": lead["title"],
        "case_number": lead["case_number"],
        "court": lead["court"],
        "court_level": "最高" if "最高人民法院" in lead["court"] else "高级/中级/基层（以原文为准）",
        "province": province_for(lead["court"]),
        "city": "",
        "case_type": lead["category"],
        "cause_of_action": cause(lead["category"]),
        "procedure": lead["procedure"],
        "judgment_date": lead["date"],
        "effective_status": "待核实",
        "source_type": "other_verified_public_case",
        "source_tier": 6,
        "source_url": source_url,
        "obtained_at": obtained,
        "rights": {},
        "claims": [],
        "defenses": [],
        "material_facts": ["目前仅有检索索引，案件事实待全文核验"],
        "disputed_issues": [],
        "evidence": [],
        "infringing_acts": [],
        "comparison": {},
        "applicable_laws": [],
        "court_reasoning": [],
        "key_rules": ["索引线索，不得替代裁判文书；需回到原文核验裁判规则"],
        "disposition": "待从全文核验",
        "claimed_amount": None,
        "awarded_amount": None,
        "reasonable_expenses": None,
        "punitive_damages": False,
        "punitive_multiplier": None,
        "damages": {},
        "law_version_status": "待核实",
        "review_status": "待二次核验（北大法宝检索索引）",
        "citations": [{"field": "index", "paragraph": "北大法宝登录检索结果"}],
        "full_text": text,
    }


def make_rmfyalk_case(raw: dict, category: str, index: int, base_url: str, obtained: str) -> dict:
    """把人民法院案例库列表页的真实索引记录转为统一字段。"""
    text = str(raw.get("text", "")).strip()
    pattern = re.compile(
        r"(?P<rmid>\d{4}-\d+-\d+-\d+-\d+)\s*/\s*"
        r"(?P<kind>刑事|民事|行政|国家赔偿|执行)\s*/\s*"
        r"(?P<cause>.*?)\s*/\s*(?P<court>.*?)\s*/\s*"
        r"(?P<date>\d{4}\.\d{2}\.\d{2})\s*/\s*"
        r"(?P<number>.*?)\s*/\s*(?P<procedure>一审|二审|再审|其他审理程序)"
    )
    match = pattern.search(text)
    if match:
        meta = match.groupdict()
        judgment_date = meta["date"].replace(".", "-")
        case_number = meta["number"].strip()
        court = meta["court"].strip()
        procedure = meta["procedure"]
        parsed_cause = meta["cause"].strip()
    else:
        meta = {}
        judgment_date = "1900-01-01"
        case_number = "待从人民法院案例库原文核验"
        court = "待核实"
        procedure = "待核实"
        parsed_cause = category
    rule = ""
    if "裁判要旨" in text:
        rule = text.split("裁判要旨", 1)[1].split("展开", 1)[0].strip()
    source_url = urljoin(base_url + "/view/list.html", str(raw.get("href", "")))
    code = {"商标": "TM", "著作权": "COPY", "专利": "PAT", "不正当竞争": "UC", "商业秘密": "SEC", "植物新品种": "PLANT"}.get(category, "IP")
    case_id = f"RMFY-{code}-{index:03d}"
    return {
        "case_id": case_id,
        "title": str(raw.get("title", "")).strip(),
        "case_number": case_number,
        "court": court,
        "court_level": "最高" if "最高人民法院" in court else "高级/中级/基层（以原文为准）",
        "province": province_for(court),
        "city": "",
        "case_type": category,
        "cause_of_action": parsed_cause or cause(category),
        "procedure": procedure,
        "judgment_date": judgment_date,
        "effective_status": "已公开收录，生效状态待核实",
        "source_type": "people_court_case_library",
        "source_tier": 2,
        "source_url": source_url,
        "obtained_at": obtained,
        "rights": {},
        "claims": [],
        "defenses": [],
        "material_facts": ["人民法院案例库列表页公开的裁判摘要"],
        "disputed_issues": [],
        "evidence": [],
        "infringing_acts": [],
        "comparison": {},
        "applicable_laws": [],
        "court_reasoning": [rule] if rule else [],
        "key_rules": [rule[:1000]] if rule else ["裁判规则待从案例库正文核验"],
        "disposition": "裁判主文待从案例库正文核验",
        "claimed_amount": None,
        "awarded_amount": None,
        "reasonable_expenses": None,
        "punitive_damages": False,
        "punitive_multiplier": None,
        "damages": {},
        "law_version_status": "待核实",
        "review_status": "机器提取（人民法院案例库）",
        "citations": [{"field": "index", "paragraph": "人民法院案例库列表页裁判要旨"}],
        "full_text": text,
    }


def make_wenshu_case(raw: dict, category: str, index: int, base_url: str, obtained: str) -> dict:
    """把中国裁判文书网公开列表的裁判理由摘要转为统一字段。"""
    text = str(raw.get("text", "")).strip()
    number_match = re.search(r"（\d{4}）[^\s]+?号", text)
    date_match = re.search(r"\d{4}-\d{2}-\d{2}", text)
    case_number = number_match.group(0) if number_match else "待从裁判文书正文核验"
    judgment_date = date_match.group(0) if date_match else "1900-01-01"
    court_match = re.search(r"(最高人民法院|[^ ]{1,30}(?:省|市|自治区|区|县)[^ ]{0,30}人民法院|[^ ]{1,20}知识产权法院)", text)
    court = court_match.group(1).strip() if court_match else "待核实"
    procedure_match = re.match(r"(民事|行政|刑事|执行|国家赔偿)[^ ]*", text)
    procedure = procedure_match.group(0) if procedure_match else "待核实"
    rule = ""
    if "[裁判理由]" in text:
        rule = text.split("[裁判理由]", 1)[1].split("收藏", 1)[0].strip()
    source_url = urljoin(base_url + "/website/wenshu/181217BMTKHNT2W0/index.html", str(raw.get("href", "")))
    code = {"商标": "TM", "著作权": "COPY", "专利": "PAT", "不正当竞争": "UC", "商业秘密": "SEC", "植物新品种": "PLANT"}.get(category, "IP")
    return {
        "case_id": f"WS-{code}-{index:03d}",
        "title": str(raw.get("title", "")).strip(),
        "case_number": case_number,
        "court": court,
        "court_level": "最高" if "最高人民法院" in court else "高级/中级/基层（以原文为准）",
        "province": province_for(court),
        "city": "",
        "case_type": category,
        "cause_of_action": cause(category),
        "procedure": procedure,
        "judgment_date": judgment_date,
        "effective_status": "已公开上网，生效状态待核实",
        "source_type": "effective_judgment",
        "source_tier": 5,
        "source_url": source_url,
        "obtained_at": obtained,
        "rights": {},
        "claims": [],
        "defenses": [],
        "material_facts": ["裁判文书网列表公开的裁判理由摘要"],
        "disputed_issues": [],
        "evidence": [],
        "infringing_acts": [],
        "comparison": {},
        "applicable_laws": [],
        "court_reasoning": [rule[:2000]] if rule else [],
        "key_rules": [rule[:1000]] if rule else ["裁判规则待从裁判文书正文核验"],
        "disposition": "裁判主文待从裁判文书正文核验",
        "claimed_amount": None,
        "awarded_amount": None,
        "reasonable_expenses": None,
        "punitive_damages": False,
        "punitive_multiplier": None,
        "damages": {},
        "law_version_status": "待核实",
        "review_status": "机器提取（裁判文书网列表摘要）",
        "citations": [{"field": "index", "paragraph": "裁判文书网列表页裁判理由"}],
        "full_text": text,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="既有福建案例 JSON")
    parser.add_argument("--leads", required=True, help="北大法宝索引线索 JSON")
    parser.add_argument("--pkulaw", help="可选：北大法宝索引线索 JSON")
    parser.add_argument("--wenshu", help="可选：裁判文书网索引线索文件前缀")
    parser.add_argument("--out", required=True, help="全国案例库目录")
    args = parser.parse_args()

    base = json.loads(Path(args.base).read_text(encoding="utf-8"))
    leads_path = Path(args.leads)
    leads = []
    rmfyalk_categories = {"trademark": "商标", "copyright": "著作权", "patent": "专利", "unfair": "不正当竞争", "secret": "商业秘密", "plant": "植物新品种"}
    if leads_path.name == "rmfyalk-leads":
        for file in sorted(leads_path.parent.glob("rmfyalk-leads-*.json")):
            suffix = file.stem.removeprefix("rmfyalk-leads-")
            category = rmfyalk_categories.get(suffix)
            if not category:
                continue
            rows = json.loads(file.read_text(encoding="utf-8"))
            leads.extend(make_rmfyalk_case(row, category, i + 1, "https://rmfyalk.court.gov.cn", date.today().isoformat()) for i, row in enumerate(rows))
    else:
        leads = json.loads(leads_path.read_text(encoding="utf-8"))
    if args.pkulaw:
        leads.extend(json.loads(Path(args.pkulaw).read_text(encoding="utf-8")))
    if args.wenshu:
        wenshu_categories = {"trademark": "商标", "copyright": "著作权", "patent": "专利", "unfair": "不正当竞争", "secret": "商业秘密", "plant": "植物新品种"}
        prefix = Path(args.wenshu)
        for file in sorted(prefix.parent.glob(prefix.name + "-*.json")):
            suffix = file.stem.removeprefix(prefix.name + "-")
            category = wenshu_categories.get(suffix)
            if not category:
                continue
            rows = json.loads(file.read_text(encoding="utf-8"))
            leads.extend(make_wenshu_case(row, category, i + 1, "https://wenshu.court.gov.cn", date.today().isoformat()) for i, row in enumerate(rows))
    obtained = date.today().isoformat()
    merged = list(base)
    existing = {str(item.get("case_id")) for item in merged}
    def dedup_key(item: dict) -> tuple[str, str]:
        number = str(item.get("case_number", "")).strip()
        title = str(item.get("title", "")).strip()
        if number and not number.startswith("待"):
            return (title, number)
        return (title, str(item.get("source_url", "")).split("?", 1)[0])

    seen_source_keys = {dedup_key(item) for item in merged}
    for lead in leads:
        lead_id = lead.get("id") or lead.get("case_id")
        source_key = dedup_key(lead)
        if source_key in seen_source_keys:
            continue
        if lead_id not in existing:
            merged.append(lead if lead.get("case_id") else make_case(lead, "https://www.pkulaw.com", obtained))
            existing.add(lead_id)
            seen_source_keys.add(source_key)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "cases.json").write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for item in merged:
        counts[item.get("case_type", "未分类")] = counts.get(item.get("case_type", "未分类"), 0) + 1
    verified = sum(1 for item in merged if item.get("review_status") == "机器提取")
    summary = {
        "scope": "全国（含福建本地）",
        "generated_at": obtained,
        "total_cases": len(merged),
        "by_case_type": counts,
        "verified_or_official_count": verified,
        "pkulaw_index_lead_count": sum(1 for item in merged if item.get("source_type") == "other_verified_public_case"),
        "rmfyalk_index_count": sum(1 for item in merged if item.get("source_type") == "people_court_case_library"),
        "wenshu_index_count": sum(1 for item in merged if item.get("source_type") == "effective_judgment"),
        "note": "三类数据库新增记录均来自已登录会话或公开列表，保留原始链接和可见摘要；全文、裁判理由和主文仍需逐案二次核验。",
    }
    (out / "collection-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registry = {
        "pkulaw": {"status": "可用（用户已登录Edge扩展）", "collected_count": sum(1 for item in merged if item.get("source_type") == "other_verified_public_case"), "scope": "全国司法案例索引", "access_note": "仅使用用户现有登录权限，未绕过认证或付费限制"},
        "wenshu": {"status": "用户已登录，公开列表与裁判理由摘要可访问", "collected_count": sum(1 for item in merged if item.get("source_type") == "effective_judgment")},
        "people_case_library": {"status": "用户已登录，公开案例列表可访问", "collected_count": sum(1 for item in merged if item.get("source_type") == "people_court_case_library")},
        "trial_process": {"status": "公开接口返回412，且非完整裁判文书库", "collected_count": 0},
        "wkinfo": {"status": "需要JavaScript/登录状态，未批量抓取", "collected_count": 0},
    }
    (out / "source-registry.json").write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    provenance = (
        "# 全国知识产权案例库来源说明\n\n"
        f"生成日期：{obtained}\n\n"
        f"共 {len(merged)} 条：既有公开权威/福建记录 {verified + (len(merged)-len(leads)-verified)} 条，"
        f"北大法宝全国检索索引线索 {sum(1 for item in merged if item.get('source_type') == 'other_verified_public_case')} 条，"
        f"人民法院案例库列表索引 {sum(1 for item in merged if item.get('source_type') == 'people_court_case_library')} 条，"
        f"中国裁判文书网列表摘要 {sum(1 for item in merged if item.get('source_type') == 'effective_judgment')} 条。\n\n"
        "北大法宝线索来自用户已登录的Edge浏览器会话，保存了标题、案号、法院、日期和检索结果链接；"
        "因数据库权限与版权边界，未批量复制全文，所有线索均须打开原文后人工复核。\n"
    )
    (out / "provenance.md").write_text(provenance, encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
