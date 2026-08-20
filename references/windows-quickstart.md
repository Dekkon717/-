# Windows 小白启动步骤

## 1. 准备数据目录

不要把案例数据放进 Skill 目录。可以在资源管理器中建立：

```text
D:\LegalData\fujian-trademark\
├── raw
├── normalized
└── database
```

如果电脑没有 D 盘，改用任何你有权限保存的文件夹。

## 2. 打开 PowerShell

在 Skill 目录中点击右键选择“在终端中打开”，或者先执行：

```powershell
Set-Location "<Skill目录>"
```

系统有 Python 时，命令中的 `python` 可以直接使用。当前 Codex 工作区也提供了一个 Python 路径：

```text
C:\Users\23693\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
```

## 3. 初始化数据库

```powershell
python scripts/init_database.py --db "D:\LegalData\fujian-trademark\database\cases.db"
```

## 4. 制作第一份案例 JSON

复制 `references/case-template.json`，保存为 `D:\LegalData\fujian-trademark\normalized\cases.json`，然后填写真实案例资料。第一批只填写 1 至 3 份，先不要批量处理。

必须替换空白字段：

- `case_id`；
- `title`；
- `case_number`；
- `court`；
- `judgment_date`；
- `source_type`；
- `source_tier`；
- `source_url`；
- `full_text`。

## 5. 导入和校验

```powershell
python scripts/ingest_cases.py --db "D:\LegalData\fujian-trademark\database\cases.db" --input "D:\LegalData\fujian-trademark\normalized\cases.json"
python scripts/validate_corpus.py --db "D:\LegalData\fujian-trademark\database\cases.db"
```

出现错误时先修正数据，不要使用 `--allow-sensitive` 绕过脱敏提示。

## 6. 试做检索

```powershell
python scripts/search_cases.py --db "D:\LegalData\fujian-trademark\database\cases.db" --query "合法来源 进货凭证" --limit 10 --json
```

结果中的 `source_url`、`case_number` 和 `snippet` 用于人工回到原文复核。
