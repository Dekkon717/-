# 中国知识产权类案检索 Skill

这是一个可安装到 Codex 的法律研究 Skill，面向中国大陆知识产权民事案件，重点支持福建法院案例，同时提供全国类案对比。它把用户描述转换为可检索的法律要素，再结合本地案例库输出权利基础、侵权构成、抗辩、证据、赔偿和诉讼方向。

> 本项目是法律研究辅助工具，不是律师意见、诉讼结果承诺或自动生成裁判结论。公开裁判数据存在选择偏差；所有关键事实、案号、法条、赔偿金额和裁判主文都应回到原文逐案核验。

## 已覆盖领域

- 注册商标侵权、商标不使用抗辩、混淆与惩罚性赔偿
- 著作权侵权（文字、美术、摄影、软件、短视频等）
- 专利侵权及专利权评价、恶意诉讼线索
- 不正当竞争（混淆、虚假宣传、商业诋毁、网络流量等）
- 商业秘密侵权
- 植物新品种权侵权

## 当前案例库

`data/national-ip-corpus/` 内置全国范围的结构化索引，共 610 条记录：人民法院案例库 327 条、中国裁判文书网列表摘要 234 条、北大法宝检索索引 42 条以及 9 条公开权威/已核验记录。六个领域均达到 50 条以上，具体数量见 `collection-summary.json`。

新增记录保留来源 URL、案号、法院、日期、案由和可见摘要，并标记机器提取/待二次核验。该数据集不替代来源网站的完整裁判文书，也不绕过登录、验证码或访问限制。

## 一键安装

### Windows（推荐）

在仓库根目录打开 PowerShell，运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_skill.ps1
```

脚本会把 `SKILL.md`、`agents/`、`references/` 和 `scripts/` 安装到 `%USERPROFILE%\.codex\skills\fujian-ip-litigation`。如需指定位置，可传入 `-TargetRoot`。

### 手动安装

将本仓库复制到：

```text
%USERPROFILE%\.codex\skills\fujian-ip-litigation
```

安装后在 Codex 中用 `$fujian-ip-litigation` 调用。

## 本地案例库使用

```powershell
python scripts/init_database.py --db .\data\national-ip-corpus\cases.db
python scripts/search_cases.py --db .\data\national-ip-corpus\cases.db --query "软件 著作权" --limit 10
python scripts/validate_corpus.py --db .\data\national-ip-corpus\cases.db
```

如要建立新库，先阅读 `references/data-workflow.md`、`references/schema.md` 和 `references/safety-rules.md`。导入前必须脱敏，不得把客户材料写入公共仓库。

## 仓库索引

| 路径 | 用途 |
| --- | --- |
| `SKILL.md` | Skill 主指令、边界和工作流程 |
| `agents/openai.yaml` | Codex 显示名称、默认提示词和调用策略 |
| `references/domain-routing.md` | 六个领域的路由与要素清单 |
| `references/source-ranking.md` | 来源层级与核验顺序 |
| `references/report-template.md` | 类案报告输出模板 |
| `references/schema.md` | 案例 JSON/SQLite 字段定义 |
| `references/data-workflow.md` | 采集、清洗、导入、复核流程 |
| `references/safety-rules.md` | 隐私、版权和法律风险控制 |
| `scripts/search_cases.py` | 结构化类案检索 |
| `scripts/build_national_corpus.py` | 合并各来源索引并去重 |
| `scripts/validate_corpus.py` | 数据结构和质量检查 |
| `scripts/install_skill.ps1` | Windows 一键安装 |
| `scripts/package_skill.py` | 打包发布 ZIP |
| `data/national-ip-corpus/` | 当前全国案例索引及 SQLite 数据库 |

## 数据来源与更新

案例来源登记在 `data/national-ip-corpus/source-registry.json`，包括北大法宝、中国裁判文书网、人民法院案例库等。采集只使用已登录会话可见内容或公开列表，不自动破解验证码、反爬或付费墙。更新时应保留原始链接、采集日期、提取方式和复核状态，并重新运行校验脚本。

## 发布与贡献

```powershell
python scripts/package_skill.py
python scripts/quick_validate.py .
```

如果本机已安装 `PyYAML`，也可以使用 Codex 自带的严格校验器：`python C:\Users\23693\.codex\skills\.system\skill-creator\scripts\quick_validate.py .`。

详细规范见 `CONTRIBUTING.md`。代码按 MIT License 发布；来源网站内容和裁判文书的版权、访问条款及个人信息保护义务仍由使用者承担。

