# Changelog: V1 → V2 (Nano Banana Pro Edition)

## 核心变化

从「通用论文分析」升级为「视觉优先的主图设计系统」。

---

## V1 架构（pdf_to_flowchart.py）

### 处理流程
1. PDF → Markdown（MinerU）
2. 解析模块
3. **单一分类**：只识别 method 相关模块
4. 全文分析：提取 data / pipeline / model / improvements
5. 生成简单的 main_figure_ideas（扁平 list）
6. 输出 Markdown 报告

### 特点
- ✅ 快速、直接
- ❌ 主图设计缺乏系统性
- ❌ 输出 Prompt 不具备实际可用性
- ❌ 没有视觉风格库支持

### 输出示例
```markdown
## Main-Figure Brainstorm
- **End-to-end pipeline**: 画一个端到端的流程图
- **Model architecture**: 画一个模型结构图
```

**问题**：这些描述过于通用，无法直接用于 AI 绘图。

---

## V2 架构（pdf_to_flowchart_v2.py）

### 三阶段处理流程

#### Phase 1: Module Role Routing
- **多标签分类**：每个模块可以同时是 `method_pipeline` + `model_architecture`
- **7 类角色标签**：task_problem / data / method_pipeline / model_architecture / training_inference / evaluation_results / system_deployment
- **轻量化**：只看标题 + 首尾句，可选用 gpt-4o-mini 节省成本
- **输出**：`roles_map`（module_id → 角色列表）

#### Phase 2: Fusion Core Engine

**双路径并行处理**：

1. **Logic Path（文本摘要）**
   - 提取 7 个维度的结构化摘要
   - 基于 Phase 1 的角色线索精准定位

2. **Visual Path（Nano Banana Pro）**
   - **视觉容器库**：5 种预设构图结构（等轴测爆炸图、AR overlay、信息网格、分镜叙事、知识网络）
   - **艺术风格滤镜库**：4 种预设渲染风格（硬核工程风、温馨手绘风、现代大屏风、专业商务风）
   - **拆解逻辑**：core_object + components + flow
   - **Magic Instruction**：强制模型按公式拼接 Prompt

**输出**：`analysis_result` JSON，包含：
- `logic_summaries`（7 个维度）
- `main_figure_ideas`（2 个完全不同的设计方案）
  - 每个方案带有：concept_title / target_audience / rationale / visual_params / **final_prompt**

#### Phase 3: Report Rendering
- 格式化文本摘要（上半部分）
- 渲染 **🎨 Main Figure Brainstorming** 板块（下半部分）
- 每个设计方案展示：
  - 视觉参数（container / style / deconstruction）
  - **完整可复制的 Final Prompt**（代码块格式）

### 特点
- ✅ **系统化**：从视觉协议库中选择，而不是自由发挥
- ✅ **可执行**：生成的 Prompt 可直接用于 DALL-E / Midjourney / Stable Diffusion
- ✅ **多样性**：强制生成 2 个不同的设计方案，覆盖不同受众
- ✅ **可解释**：每个方案都有 rationale 说明为什么这个风格适合这篇论文
- ✅ **成本优化**：Phase 1 可使用轻量模型

### 输出示例

```markdown
## Design 1: Multi-Layer Attention Mechanism Exploded View

**Target Audience**: AI researchers, model designers
**Rationale**: The paper focuses on Transformer architecture internals,
              which maps perfectly to an exploded view showing layer-by-layer structure.

**Visual Container**: `isometric_exploded_view`
**Art Style**: `engineering_tech`

**Core Object**: A transparent glass multi-layer cube with glowing blue circuits
**Components**:
  - Input embedding layer (bottom plate)
  - Multi-head attention modules (floating glass blocks)
  - Feed-forward network (middle transparent cylinder)
  - Output projection layer (top plate)
**Flow**: Blue laser beams connecting layers, showing information flow

**🎨 Final Prompt (Ready for Image Generation):**
```
A transparent multi-layer glass cube representing a Transformer architecture,
isometric exploded view with components floating in vertical layers,
connected by neon blue glowing laser beams showing data flow,
industrial CAD rendering style, blueprint aesthetic, neon blue glowing edges,
semi-transparent glass materials, dark tech background,
8k, high resolution, cinematic lighting
```
```

**优势**：这段 Prompt 可以直接复制到 Midjourney / DALL-E，得到专业的科技风主图。

---

## 对比表格

| 维度 | V1 | V2 |
|------|----|----|
| **模块分类** | 单一角色（仅 method） | 多角色标签（7 类） |
| **视觉设计** | 通用描述 | Nano Banana Pro 协议库 |
| **Prompt 质量** | 不可用 | 可直接用于 AI 绘图 |
| **设计数量** | 1 个扁平 list | 2 个完整方案 |
| **风格控制** | 无 | 5 种容器 × 4 种风格 = 20 种组合 |
| **可解释性** | 无 | 每个方案带 rationale |
| **成本优化** | 无 | Phase 1 可用轻量模型 |
| **输出结构** | Markdown（简单） | Markdown（结构化 + 代码块 Prompt） |

---

## 升级建议

如果你当前使用 V1：

1. **保留 V1**：用于快速的通用论文分析
2. **使用 V2**：当你需要设计论文主图、准备会议海报、制作视频封面时

如果你是新用户：

- **直接使用 V2**：它包含了 V1 的所有功能，并且输出更加专业

---

## 迁移路径

### 从 V1 迁移到 V2

V2 完全兼容 V1 的输入格式（都是 PDF），但输出结构不同。

**V1 输出**：
```markdown
## Data
...
## Method / Pipeline
...
## Main-Figure Brainstorm
- Idea 1: ...
```

**V2 输出**：
```markdown
## Data
...
## Method / Pipeline
...
## 🎨 Main Figure Brainstorming
### Design 1: ...
**Final Prompt:**
```
<完整 Prompt>
```
```

如果你的下游工具依赖 V1 的输出格式，可以：
1. 保留 V1 脚本用于自动化 Pipeline
2. 手动使用 V2 进行主图设计

---

## 版本信息

- **V1**: `pdf_to_flowchart.py`（通用论文分析）
- **V2**: `pdf_to_flowchart_v2.py`（视觉优先 + Nano Banana Pro）

两个版本可以共存，根据需求选择使用。

---

**更新时间**: 2025-11-24  
**作者**: 基于用户规格说明书实现
