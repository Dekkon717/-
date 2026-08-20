# 知识产权案例字段规范

## 必填字段

| 字段 | 含义 |
|---|---|
| `case_id` | 内部唯一编号，不因标题变化而改变 |
| `title` | 文书或案例标题 |
| `case_number` | 案号 |
| `court` | 审理法院全称 |
| `judgment_date` | `YYYY-MM-DD` 格式裁判日期 |
| `source_type` | 见来源排序文件 |
| `source_tier` | 1至6的来源等级 |
| `source_url` | 可回溯的原始网址 |
| `full_text` | 原始正文或经过可追溯清洗的正文 |

## 推荐字段

- `court_level`：基层、中级、高级、最高。
- `province`、`city`。
- `case_type`：商标、著作权、不正当竞争、专利、商业秘密、植物新品种或其他知识产权领域。
- `cause_of_action`：具体案由，应以文书为准。
- `procedure`：一审、二审、再审、其他。
- `effective_status`：已生效、未生效、待核实。
- `obtained_at`：资料取得日期。
- `source_hash`：正文 SHA-256；缺失时导入脚本自动计算。
- `rights`：权利人、注册号、核定范围、有效状态和许可。
- `claims`、`defenses`、`material_facts`、`disputed_issues`、`evidence`。
- `infringing_acts`：生产、销售、网络展示等行为。
- `comparison`：标识、商品或服务、混淆判断。
- `applicable_laws`、`court_reasoning`、`key_rules`。
- `disposition`：最终判项摘要。
- `claimed_amount`、`awarded_amount`、`reasonable_expenses`。
- `punitive_damages`、`punitive_multiplier`、`damages`。
- `law_version_status`：现行、已修改、已废止、待核实。
- `review_status`：机器提取、人工复核、复核退回。
- `citations`：结构化结论与原文段落的映射。

## JSON 规则

`rights`、`comparison`、`damages` 使用对象；其他复数字段使用数组。金额字段使用数字，不带“元”或逗号。没有信息时使用空数组、空对象或 `null`，不要用推测值填充。

案例模板见 [case-template.json](case-template.json)。
