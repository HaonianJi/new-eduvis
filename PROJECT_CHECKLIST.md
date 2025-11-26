# 项目文件清单

这是准备上传 GitHub 的完整项目文件列表。

## ✅ 已创建文件

### 根目录文件

| 文件名 | 用途 | 状态 |
|--------|------|------|
| `.gitignore` | 忽略敏感文件和临时文件 | ✅ |
| `.env.example` | 环境变量模板（供用户参考） | ✅ |
| `README.md` | 项目主文档 | ✅ |
| `LICENSE` | MIT 开源协议 | ✅ |
| `requirements.txt` | Python 依赖列表 | ✅ |
| `setup_mineru.sh` | MinerU 一键部署脚本 | ✅ 可执行 |
| `run_visual_plan.sh` | 运行脚本（从 .env 读取配置） | ✅ 可执行 |
| `UPLOAD_GUIDE.md` | GitHub 上传指南 | ✅ |
| `PROJECT_CHECKLIST.md` | 本文件（项目清单） | ✅ |

### project/ 目录

| 文件名 | 用途 | 状态 |
|--------|------|------|
| `pdf_to_flowchart_v2.py` | 主程序（三阶段 Pipeline） | ✅ |
| `VISUAL_PLAN_GUIDE.md` | 详细使用指南 | ✅ |
| `CHANGELOG_V2.md` | 版本更新日志 | ✅ |

## 🔐 安全检查

### ✅ 已确保安全的配置

- [x] API key 从环境变量读取，不在代码中硬编码
- [x] `.env` 文件被 `.gitignore` 排除
- [x] 提供 `.env.example` 模板供用户参考
- [x] `run_visual_plan.sh` 从 `.env` 文件读取配置
- [x] 所有敏感输出目录被 `.gitignore` 排除

### ✅ 代码中的环境变量读取

```python
# 在 pdf_to_flowchart_v2.py 中：
endpoint = os.getenv("AZURE_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
```

### ✅ Shell 脚本中的环境变量读取

```bash
# 在 run_visual_plan.sh 中：
if [ -f "${SCRIPT_DIR}/.env" ]; then
    export $(grep -v '^#' "${SCRIPT_DIR}/.env" | xargs)
fi
```

## 📂 目录结构

```
paper2visualplan_github/
├── .gitignore                 # Git 忽略文件
├── .env.example               # 环境变量模板
├── README.md                  # 项目说明
├── LICENSE                    # MIT 协议
├── requirements.txt           # Python 依赖
├── setup_mineru.sh            # MinerU 部署脚本 (可执行)
├── run_visual_plan.sh         # 运行脚本 (可执行)
├── UPLOAD_GUIDE.md            # 上传指南
├── PROJECT_CHECKLIST.md       # 本文件
└── project/
    ├── pdf_to_flowchart_v2.py      # 主程序
    ├── VISUAL_PLAN_GUIDE.md        # 详细指南
    └── CHANGELOG_V2.md             # 更新日志
```

## 🚀 下一步操作

1. **阅读上传指南**
   ```bash
   cat UPLOAD_GUIDE.md
   ```

2. **创建 .env 文件（仅本地使用，不要提交！）**
   ```bash
   cp .env.example .env
   # 然后编辑 .env 填入你的 API key
   ```

3. **测试脚本**
   ```bash
   ./setup_mineru.sh          # 安装 MinerU
   ./run_visual_plan.sh test.pdf  # 测试运行
   ```

4. **上传到 GitHub**
   - 使用 GitHub Desktop 或
   - 使用命令行（详见 UPLOAD_GUIDE.md）

## 📊 文件统计

- **总文件数**: 12 个
- **Python 文件**: 1 个
- **Shell 脚本**: 2 个（均可执行）
- **Markdown 文档**: 6 个
- **配置文件**: 3 个

## ⚠️ 重要提醒

**上传前必须确认：**

1. ❌ **不要**提交 `.env` 文件
2. ❌ **不要**提交包含真实 API key 的任何文件
3. ❌ **不要**提交 MinerU 模型文件（太大）
4. ✅ **确保** `.gitignore` 文件已正确配置
5. ✅ **确保**所有脚本使用环境变量读取配置

---

**准备完成！可以安全上传到 GitHub 了！** 🎉
