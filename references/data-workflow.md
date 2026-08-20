# 数据制作与导入

## 第一次使用

1. 在 Skill 目录之外新建数据文件夹，例如 `D:\LegalData\fujian-ip`。
2. 使用 `scripts/init_database.py --db D:\LegalData\fujian-ip\cases.db` 建库。
3. 从官方来源合法取得案例，保存原文件、网址和取得日期。
4. 复制 `references/case-template.json`，每份裁判制作一个 JSON 对象；多份案例可以组成 JSON 数组或 JSONL。
5. 使用 `scripts/ingest_cases.py` 导入。脚本发现明显身份证号、手机号或银行卡号时默认拒绝导入。
6. 使用 `scripts/validate_corpus.py` 检查缺失字段、重复文书、来源和敏感信息。
7. 使用 `scripts/search_cases.py` 测试检索。

## 原始材料管理

原文和数据库分开：

```text
fujian-ip-data/
├── raw/          原始网页、PDF或Word
├── normalized/   清洗后的文本及结构化JSON
├── database/     SQLite数据库
├── evaluations/  测试问题和人工答案
└── logs/         导入和复核记录
```

不覆盖原始文件。原文文件名变化时使用哈希识别重复文书。

## 第一批数据

按领域分别做 1 至 20 份案例验证流程，其中优先选择来源明确的二审、生效裁判、指导性案例和人民法院案例库案例。字段稳定后再扩充到每个领域 50 至 200 份。不要为了数量降低来源或复核标准。

## 更新

每次更新记录检索日期、来源范围、新增数量、撤回数量和复核人。网站原文撤回或更正后，将数据库记录停用或更正，并保留历史记录。
