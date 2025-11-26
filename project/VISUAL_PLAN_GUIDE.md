# 🎨 Paper-to-Visual-Plan Pipeline 使用指南

## 概述

这个系统按照 **Nano Banana Pro 视觉协议** 实现，能够从学术论文 PDF 自动生成：
1. **结构化文本摘要**（数据/方法/模型/评估等）
2. **两套完全不同的主图设计方案**，每套都包含可直接用于 AI 绘图的完整 Prompt

---

## 三阶段架构

### Phase 1: 模块功能快速路由
- **输入**：仅使用标题 + 首句 + 尾句
- **输出**：每个模块的功能角色标签（task_problem / data / method_pipeline / model_architecture / training_inference / evaluation_results / system_deployment）
- **目的**：快速建立论文骨架地图，不消耗大量 Token

### Phase 2: Fusion Core Engine
- **输入**：全文 Markdown + Phase 1 的角色线索
- **双路径处理**：
  - **Logic Path**：提取各维度的结构化摘要
  - **Visual Path**：基于 Nano Banana Pro 协议设计两套主图方案
- **输出**：`analysis_result` JSON，包含 `logic_summaries` 和 `main_figure_ideas`

### Phase 3: 报告渲染
- **输入**：`analysis_result` JSON
- **输出**：格式化的 Markdown 报告，包含文本摘要和 🎨 Main Figure Brainstorming 板块

---

## 环境配置

### 1. Azure OpenAI 环境变量

```bash
export AZURE_ENDPOINT="https://your-endpoint.cognitiveservices.azure.com"
export AZURE_API_KEY="your-api-key"
export AZURE_GPT_DEPLOYMENT="gpt-5.1"  # 主模型
export AZURE_API_VERSION="2025-01-01-preview"

# 可选：为 Phase 1 使用轻量模型以节省成本
export AZURE_GPT_DEPLOYMENT_PHASE1="gpt-4o-mini"
```

### 2. MinerU 环境

确保 MinerU 已安装并激活：

```bash
cd /Users/haonianji/windsuf/new_paper2fig/MinerU
source venv/bin/activate
```

---

## 使用方法

### 基本用法

```bash
cd /Users/haonianji/windsuf/new_paper2fig
source MinerU/venv/bin/activate

python project/pdf_to_flowchart_v2.py /path/to/paper.pdf
```

### 自定义参数

```bash
# 指定工作目录
python project/pdf_to_flowchart_v2.py paper.pdf --workdir ./my_output

# 指定输出报告路径
python project/pdf_to_flowchart_v2.py paper.pdf --report ./analysis_report.md
```

---

## 输出报告结构

生成的 Markdown 报告包含以下部分：

### 上半部分：Logic Summaries

```markdown
# Paper Analysis & Visual Plan

## Task / Problem
...

## Data
...

## Method / Pipeline
...

## Model / Architecture
...

## Training & Inference
...

## Evaluation / Results
...

## System / Deployment
...
```

### 下半部分：🎨 Main Figure Brainstorming

每个设计方案包含：

```markdown
## Design 1: <concept_title>

**Target Audience**: ...
**Rationale**: ...

**Visual Container**: `isometric_exploded_view`
**Art Style**: `engineering_tech`

**Core Object**: ...
**Components**:
  - ...
**Flow**: ...

**🎨 Final Prompt (Ready for Image Generation):**
```
<完整的可复制 Prompt>
```
```

---

## Nano Banana Pro 视觉协议

系统会自动从以下预设中选择最适合论文的组合：

### 视觉容器库 (Visual Containers)

| 容器类型 | 适用场景 | 特征 |
|---------|---------|------|
| `isometric_exploded_view` | Transformer 架构、多模态模型、芯片设计 | 垂直分层悬浮，光流连接，展现内部结构 |
| `ar_real_world_overlay` | 计算机视觉、自动驾驶、智慧城市 | 写实照片底图 + 数字线框覆盖 |
| `modular_infographic_grid` | 多模型对比、数据集分类、工具库概览 | 2x2 或 3x3 卡片区域，整齐对比 |
| `sequential_storyboard` | 用户交互流程、Agent 决策过程 | 横向分格，时间流动感 |
| `knowledge_network` | 文献综述、逻辑推演、实体关系 | 中心辐射或层级树状结构 |

### 艺术风格滤镜库 (Art Style Filters)

| 风格类型 | 灵感来源 | 关键词 |
|---------|---------|--------|
| `engineering_tech` | SpaceX/航空发动机图 | 工业 CAD 渲染、蓝图美学、霓虹蓝发光边缘 |
| `cozy_hand_drawn` | 手帐/插画 | 水彩与墨水质感、点阵笔记本背景、暖色调 |
| `modern_dashboard` | 数据可视化大屏 | 暗黑模式 UI、黑金/青色配色、发光数据图表 |
| `professional_business` | 麦肯锡白板 | 马克笔手绘风、极简白板背景、清晰逻辑连线 |

### 拆解逻辑 (Deconstruction)

每个设计方案都会完成：
- **Core Object**：将抽象算法具象化为实物
- **Components**：列出 3-5 个必须出现的具体零件
- **Flow**：用什么视觉元素代表数据流动

---

## 示例输出

假设论文是关于 Transformer 架构的，可能得到类似：

### Design 1: Multi-Layer Attention Mechanism Exploded View

**Visual Container**: `isometric_exploded_view`  
**Art Style**: `engineering_tech`

**Core Object**: A transparent glass multi-layer cube with glowing blue circuits  
**Components**:
  - Input embedding layer (bottom plate)
  - Multi-head attention modules (floating glass blocks)
  - Feed-forward network (middle transparent cylinder)
  - Output projection layer (top plate)

**Flow**: Blue laser beams connecting layers, showing information flow

**Final Prompt:**
```
A transparent multi-layer glass cube representing a Transformer architecture,
isometric exploded view with components floating in vertical layers,
connected by neon blue glowing laser beams showing data flow,
industrial CAD rendering style, blueprint aesthetic,
semi-transparent glass materials, dark tech background,
8k, high resolution, cinematic lighting
```

### Design 2: Sequential Processing Storyboard

**Visual Container**: `sequential_storyboard`  
**Art Style**: `cozy_hand_drawn`

**Core Object**: A series of hand-drawn panels showing token transformation  
**Components**:
  - Panel 1: Input tokens (cute word bubbles)
  - Panel 2: Attention weights (connecting arrows)
  - Panel 3: Output predictions (highlighted tokens)

**Flow**: Dashed arrows between panels

**Final Prompt:**
```
A horizontal comic-style storyboard showing Transformer processing steps,
hand-drawn watercolor and ink texture, dotted notebook background,
cute hand-drawn icons representing tokens and attention,
warm color tones, arrows showing sequential flow from left to right,
8k, high resolution, warm lighting
```

---

## 常见问题

### Q: Phase 1 分类不准确怎么办？
A: 可以设置 `AZURE_GPT_DEPLOYMENT_PHASE1` 为更强的模型（如 `gpt-5.1`），或检查论文的标题和首尾句是否足够清晰。

### Q: 生成的 Prompt 不符合预期？
A: 检查 Phase 2 的 system prompt 是否正确嵌入了 Nano Banana Pro 协议。系统会严格从预设库中选择，不应产生幻觉。

### Q: 如何调整生成的主图数量？
A: 当前固定为 2 个设计方案。如需更多，可以修改 `run_fusion_core` 的 system prompt，要求生成 3-4 个方案。

### Q: 报告太长，如何精简？
A: 可以在 `render_report` 函数中选择性隐藏某些 `logic_summaries` 字段，只保留核心的 Method/Model/Evaluation。

---

## 技术细节

### JSON Schema 验证

Phase 2 输出的 `analysis_result` 必须符合以下结构：

```json
{
  "analysis_result": {
    "logic_summaries": {
      "task_problem": "string",
      "data": "string",
      "method_pipeline": "string",
      "model_architecture": "string",
      "training_inference": "string",
      "evaluation_results": "string",
      "system_deployment": "string"
    },
    "main_figure_ideas": [
      {
        "concept_title": "string",
        "target_audience": "string",
        "rationale": "string",
        "visual_params": {
          "container": "enum(visual containers)",
          "style": "enum(art styles)",
          "deconstruction": {
            "core_object": "string",
            "components": ["string", ...],
            "flow": "string"
          },
          "final_prompt": "string"
        }
      }
    ]
  }
}
```

### 成本估算

- Phase 1（分类）：约 300-500 tokens 输入，200-400 tokens 输出
- Phase 2（Fusion Core）：约 8000-15000 tokens 输入，1500-2400 tokens 输出
- 单次运行总成本（gpt-5.1）：约 $0.50-1.00（取决于论文长度）

### 性能优化建议

1. **使用轻量模型做 Phase 1**：设置 `AZURE_GPT_DEPLOYMENT_PHASE1="gpt-4o-mini"` 可节省 70% Phase 1 成本
2. **批处理多篇论文**：可以修改脚本支持输入一个 PDF 目录，自动遍历处理
3. **缓存 Phase 1 结果**：如果需要多次调整 Phase 2 的 prompt，可以缓存 `roles_map` 避免重复分类

---

## 下一步优化方向

1. **支持多语言论文**（当前主要针对英文，中文论文可能需要调整 prompt）
2. **交互式主图选择**（生成 3-5 个候选，让用户选择最佳方案）
3. **与绘图 API 集成**（自动调用 DALL-E/Midjourney/Stable Diffusion 生成实际图像）
4. **主图评分系统**（基于论文类型自动评估哪种视觉风格最合适）

---

**项目路径**: `/Users/haonianji/windsuf/new_paper2fig/project/pdf_to_flowchart_v2.py`  
**文档更新时间**: 2025-11-24

如有问题，请参考规格说明书或联系开发者。
