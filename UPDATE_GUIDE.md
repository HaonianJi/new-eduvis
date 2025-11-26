# 仓库更新指南

本指南说明如何在不同环境中更新你的 GitHub 仓库。

## 🔄 方法一：在新机器上从零开始

### 1. Clone 仓库到新位置

```bash
# Clone 你的 GitHub 仓库
git clone https://github.com/HaonianJi/new-eduvis.git
cd new-eduvis

# 查看当前状态
git status
git log --oneline -5  # 查看最近5次提交
```

### 2. 从原项目复制更新的文件

```bash
# 假设你的原项目在 /path/to/original/project
# 复制更新的文件到 GitHub 仓库

# 复制主程序
cp /path/to/original/project/pdf_to_flowchart_v2.py ./project/

# 复制文档（如果有更新）
cp /path/to/original/project/VISUAL_PLAN_GUIDE.md ./project/
cp /path/to/original/project/CHANGELOG_V2.md ./project/

# 复制其他更新的文件...
```

### 3. 提交并推送更新

```bash
# 检查变更
git status
git diff  # 查看具体变更内容

# 添加变更
git add .

# 提交变更
git commit -m "Update: describe your changes here"

# 推送到 GitHub
git push origin main
```

## 🔄 方法二：同步现有的 GitHub 仓库

如果你已经在某个地方有 GitHub 仓库的副本：

### 1. 拉取最新更改

```bash
cd /path/to/your/github/repo

# 拉取最新更改
git pull origin main

# 查看当前状态
git status
```

### 2. 复制新文件并提交

```bash
# 复制更新的文件（同方法一）
cp /path/to/updated/files ./

# 提交推送（同方法一）
git add .
git commit -m "Update: your message"
git push origin main
```

## 🔄 方法三：使用脚本自动同步

创建一个同步脚本：

### 创建 `sync_to_github.sh`

```bash
#!/bin/bash
# 自动同步脚本

set -e

# 配置路径
ORIGINAL_PROJECT="/Users/haonianji/windsuf/new_paper2fig"
GITHUB_REPO="/Users/haonianji/windsuf/paper2visualplan_github"

echo "🔄 Syncing files to GitHub repo..."

# 进入 GitHub 仓库目录
cd "$GITHUB_REPO"

# 拉取最新更改
git pull origin main

# 复制更新的文件
echo "📂 Copying updated files..."
cp "$ORIGINAL_PROJECT/project/pdf_to_flowchart_v2.py" ./project/
cp "$ORIGINAL_PROJECT/project/VISUAL_PLAN_GUIDE.md" ./project/
cp "$ORIGINAL_PROJECT/project/CHANGELOG_V2.md" ./project/

# 检查是否有变更
if git diff --quiet; then
    echo "✅ No changes to commit"
    exit 0
fi

# 显示变更
echo "📝 Changes detected:"
git status --short

# 提交变更
echo "💾 Committing changes..."
git add .
git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"

# 推送到 GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Sync completed!"
```

### 使用同步脚本

```bash
# 给脚本执行权限
chmod +x sync_to_github.sh

# 运行同步
./sync_to_github.sh
```

## 🌍 方法四：在完全新的环境中

### 1. 安装必要工具

```bash
# 安装 Git（如果没有）
# macOS:
xcode-select --install

# Linux:
sudo apt-get install git

# 配置 Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 2. 设置 SSH 密钥（推荐）

```bash
# 生成 SSH 密钥
ssh-keygen -t ed25519 -C "your.email@example.com"

# 添加到 ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# 复制公钥到 GitHub
cat ~/.ssh/id_ed25519.pub
# 然后在 GitHub Settings > SSH Keys 中添加
```

### 3. Clone 并开始工作

```bash
# 使用 SSH clone（推荐）
git clone git@github.com:HaonianJi/new-eduvis.git

# 或使用 HTTPS
git clone https://github.com/HaonianJi/new-eduvis.git
```

## 📋 常用 Git 命令速查

```bash
# 查看状态
git status

# 查看变更
git diff
git diff --staged  # 查看已暂存的变更

# 查看历史
git log --oneline
git log --graph --oneline --all

# 撤销操作
git checkout -- file.txt     # 撤销工作区变更
git reset HEAD file.txt      # 取消暂存
git reset --hard HEAD~1      # 撤销最后一次提交（危险！）

# 分支操作
git branch                   # 查看分支
git checkout -b new-feature  # 创建并切换分支
git merge feature-branch     # 合并分支

# 远程操作
git remote -v               # 查看远程仓库
git fetch origin            # 获取远程更新
git pull origin main        # 拉取并合并
git push origin main        # 推送到远程
```

## ⚠️ 注意事项

1. **备份重要文件**：更新前先备份
2. **检查 .gitignore**：确保不提交敏感文件
3. **写清楚提交信息**：方便以后查找
4. **定期同步**：避免冲突累积
5. **使用分支**：重大更改时创建新分支

## 🆘 遇到问题时

### 合并冲突

```bash
# 查看冲突文件
git status

# 手动解决冲突后
git add conflicted-file.txt
git commit -m "Resolve merge conflict"
```

### 推送被拒绝

```bash
# 先拉取远程更改
git pull origin main

# 解决冲突后再推送
git push origin main
```

### 误提交敏感信息

```bash
# 立即修改最后一次提交
git reset --soft HEAD~1
# 移除敏感文件，重新提交

# 如果已推送，联系 GitHub 支持
```

---

**选择适合你情况的方法开始更新吧！** 🚀
