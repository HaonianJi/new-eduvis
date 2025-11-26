# GitHub 上传指南

本指南帮助你将 Paper2VisualPlan 项目上传到 GitHub。

## 📋 准备清单

在上传前，请确认以下文件已准备好：

- [x] `.gitignore` - 防止敏感文件被提交
- [x] `.env.example` - 环境变量模板
- [x] `README.md` - 项目说明文档
- [x] `LICENSE` - MIT 开源协议
- [x] `requirements.txt` - Python 依赖
- [x] `setup_mineru.sh` - MinerU 一键部署脚本
- [x] `run_visual_plan.sh` - 运行脚本（从 .env 读取配置）
- [x] `project/` - 项目核心代码

## ⚠️ 安全检查

**重要：上传前必须确认！**

1. ✅ `.env` 文件已被 `.gitignore` 排除
2. ✅ 没有硬编码的 API Key
3. ✅ 所有脚本从环境变量读取配置
4. ✅ 敏感输出目录已被 `.gitignore` 排除

## 🚀 上传步骤

### 方法一：使用 GitHub Desktop（推荐新手）

1. 打开 GitHub Desktop
2. File -> Add Local Repository
3. 选择 `paper2visualplan_github` 文件夹
4. 创建初始提交（Initial commit）
5. Publish repository
6. 选择是否公开仓库

### 方法二：使用命令行

```bash
# 进入项目目录
cd /Users/haonianji/windsuf/paper2visualplan_github

# 初始化 Git 仓库
git init

# 添加所有文件
git add .

# 检查将要提交的文件（确保没有 .env 文件！）
git status

# 创建初始提交
git commit -m "Initial commit: Paper2VisualPlan v2"

# 在 GitHub 网站创建新仓库后，连接远程仓库
git remote add origin https://github.com/your-username/paper2visualplan.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 📝 提交前最后检查

运行以下命令查看将要提交的文件：

```bash
cd /Users/haonianji/windsuf/paper2visualplan_github
git status
```

**确认没有以下文件：**
- ❌ `.env` 文件
- ❌ API keys 或敏感信息
- ❌ 个人输出目录（`.visual_plan_output/` 等）
- ❌ MinerU 模型文件（`MinerU/models/`）

## 🎯 推荐的 GitHub 仓库设置

### 仓库名称
`paper2visualplan` 或 `academic-paper-visualizer`

### 仓库描述
> Automatically convert academic papers (PDF) into structured visual plans with intelligent content analysis.

### 标签（Topics）
- `pdf-processing`
- `academic-papers`
- `nlp`
- `openai`
- `azure`
- `python`
- `research-tools`

### README 徽章（可选）

在 README.md 顶部添加：

```markdown
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Azure](https://img.shields.io/badge/Azure-OpenAI-blue.svg)
```

## 🔄 后续更新流程

当你在原项目中修改代码后，更新 GitHub 仓库：

```bash
# 复制更新的文件
cp /path/to/updated/file.py /Users/haonianji/windsuf/paper2visualplan_github/project/

# 提交更新
cd /Users/haonianji/windsuf/paper2visualplan_github
git add .
git commit -m "Update: describe your changes"
git push
```

## 💡 提示

1. **版本标签**：可以为重要版本创建标签
   ```bash
   git tag -a v1.0.0 -m "First stable release"
   git push origin v1.0.0
   ```

2. **分支管理**：建议保持 `main` 分支稳定，在 `dev` 分支开发
   ```bash
   git checkout -b dev
   ```

3. **Issues 和 Projects**：在 GitHub 上启用 Issues 和 Projects 功能，方便管理

4. **GitHub Actions**：可以设置 CI/CD 自动测试（可选）

## 📞 需要帮助？

如果遇到问题：
1. 检查 `.gitignore` 是否正确配置
2. 确认 `.env` 文件没有被提交
3. 查看 Git 状态：`git status`
4. 查看提交历史：`git log`

---

**准备好了吗？开始上传吧！** 🚀
