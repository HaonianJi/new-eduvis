"""
Paper-to-Visual-Plan Pipeline (Nano Banana Pro Edition)

Three-phase architecture:
1. Phase 1: Module Role Routing (title + first/last sentence only)
2. Phase 2: Fusion Core Engine (full text + Nano Banana Pro visual translation)
3. Phase 3: Markdown Report Rendering
"""

import argparse
import json
import os
import re
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import requests


@dataclass
class Module:
    module_id: str
    level: int
    title: str
    content: str
    first_sentence: str
    last_sentence: str
    # Enhanced metadata from content_list.json
    figures: Optional[List[Dict]] = None  # List of figures in this section
    tables: Optional[List[Dict]] = None   # List of tables in this section
    equations: Optional[List[Dict]] = None  # List of equations in this section


def run_mineru_cli(pdf_path: Path, output_dir: Path) -> tuple[Path, Optional[Path]]:
    """Run MinerU CLI to convert PDF to Markdown.
    
    Returns:
        tuple: (md_path, content_list_json_path)
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "mineru",
        "-p", str(pdf_path),
        "-o", str(output_dir),
        "-m", "auto",
        "-b", "pipeline",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"mineru CLI failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

    md_files = sorted(output_dir.rglob("*.md"), key=lambda p: p.stat().st_size, reverse=True)
    if not md_files:
        raise FileNotFoundError(f"No .md files found under {output_dir}")

    # Try to find content_list.json in the same directory as the markdown file
    md_path = md_files[0]
    content_list_path = md_path.parent / f"{md_path.stem}_content_list.json"
    
    if not content_list_path.exists():
        print(f"[Warning] content_list.json not found at {content_list_path}", file=sys.stderr)
        content_list_path = None

    return md_path, content_list_path


def split_sentences(paragraph: str) -> List[str]:
    text = paragraph.strip()
    if not text:
        return []
    parts = re.split(r"(?<=[。！？!?\.])\s+", text)
    sentences = [p.strip() for p in parts if p.strip()]
    return sentences if sentences else [text]


def parse_markdown_modules(md_text: str, content_list: Optional[List[Dict]] = None) -> List[Module]:
    """Parse markdown into modules based on headers.
    
    Args:
        md_text: Markdown content
        content_list: Optional structured data from MinerU JSON for enhanced parsing
    """
    lines = md_text.splitlines()
    modules: List[Module] = []
    current_title: Optional[str] = None
    current_level: Optional[int] = None
    current_lines: List[str] = []
    counter = 0

    header_pattern = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")

    for line in lines:
        m = header_pattern.match(line)
        if m:
            if current_title is not None:
                counter += 1
                modules.append(_build_module(counter, current_level, current_title, current_lines))

            hashes, title = m.groups()
            current_title = title.strip()
            current_level = len(hashes)
            current_lines = []
        else:
            if current_title is not None:
                current_lines.append(line)

    if current_title is not None:
        counter += 1
        modules.append(_build_module(counter, current_level, current_title, current_lines))

    return modules


def _build_module(counter: int, level: Optional[int], title: str, lines: List[str]) -> Module:
    content = "\n".join(lines).strip()
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", content) if p.strip()]

    first_sentence = ""
    last_sentence = ""
    if paragraphs:
        first_sentences = split_sentences(paragraphs[0])
        if first_sentences:
            first_sentence = first_sentences[0]
        last_sentences = split_sentences(paragraphs[-1])
        if last_sentences:
            last_sentence = last_sentences[-1]

    return Module(
        module_id=f"sec_{counter}",
        level=level or 1,
        title=title,
        content=content,
        first_sentence=first_sentence,
        last_sentence=last_sentence,
        figures=None,
        tables=None,
        equations=None,
    )


def enhance_modules_with_json(modules: List[Module], content_list_path: Optional[Path]) -> List[Module]:
    """Enhance modules with structured data from content_list.json.
    
    Smart distribution: associates figures/tables/equations with relevant sections
    based on title matching and heuristics.
    
    Args:
        modules: List of modules parsed from Markdown
        content_list_path: Path to content_list.json file
        
    Returns:
        Enhanced modules with figures, tables, and equations metadata
    """
    if not content_list_path or not content_list_path.exists():
        print("[Info] Skipping JSON enhancement - content_list.json not available", file=sys.stderr)
        return modules
    
    try:
        with open(content_list_path, 'r', encoding='utf-8') as f:
            content_list = json.load(f)
        
        # Extract structured elements with enhanced metadata
        figures = [item for item in content_list if item.get('type') == 'image']
        tables = [item for item in content_list if item.get('type') == 'table']
        equations = [item for item in content_list if item.get('type') == 'equation']
        
        print(f"[JSON Enhancement] Found {len(figures)} figures, {len(tables)} tables, {len(equations)} equations", file=sys.stderr)
        
        # Smart distribution: assign visual elements to relevant modules
        for module in modules:
            title_lower = module.title.lower()
            
            # Associate figures with method/architecture sections
            if any(kw in title_lower for kw in ['method', 'approach', 'architecture', 'model', 'framework', 'pipeline']):
                # Attach figures that likely show architecture
                module.figures = [f for f in figures if _is_architecture_figure(f)]
                if module.figures:
                    print(f"  → Assigned {len(module.figures)} figure(s) to '{module.title}'", file=sys.stderr)
            
            # Associate tables with results/evaluation sections
            elif any(kw in title_lower for kw in ['result', 'experiment', 'evaluation', 'performance', 'comparison']):
                module.tables = tables if tables else None
                if module.tables:
                    print(f"  → Assigned {len(module.tables)} table(s) to '{module.title}'", file=sys.stderr)
            
            # Associate equations with method/model sections
            elif any(kw in title_lower for kw in ['method', 'model', 'formulation', 'optimization']):
                module.equations = equations if equations else None
                if module.equations:
                    print(f"  → Assigned {len(module.equations)} equation(s) to '{module.title}'", file=sys.stderr)
        
        # Fallback: attach all to first module as global reference
        if modules and not any(m.figures or m.tables or m.equations for m in modules):
            print("  → Fallback: Attaching all visual elements to first module", file=sys.stderr)
            modules[0].figures = figures if figures else None
            modules[0].tables = tables if tables else None
            modules[0].equations = equations if equations else None
            
    except Exception as e:
        print(f"[Warning] Failed to parse content_list.json: {e}", file=sys.stderr)
    
    return modules


def _is_architecture_figure(fig: Dict) -> bool:
    """Heuristic to identify architecture/pipeline figures."""
    caption = ' '.join(fig.get('image_caption', [])).lower()
    architecture_keywords = [
        'architecture', 'framework', 'pipeline', 'model', 'system',
        'overview', 'diagram', 'workflow', 'structure', 'network'
    ]
    return any(kw in caption for kw in architecture_keywords)


def build_modules_summary(modules: List[Module]) -> str:
    """Build metadata-only summary for Phase 1, including visual elements hint."""
    blocks = []
    
    # Add visual elements hint at the beginning
    total_figures = sum(len(m.figures) if m.figures else 0 for m in modules)
    total_tables = sum(len(m.tables) if m.tables else 0 for m in modules)
    total_equations = sum(len(m.equations) if m.equations else 0 for m in modules)
    
    if total_figures > 0 or total_tables > 0 or total_equations > 0:
        hint = f"[PAPER META] This paper contains {total_figures} figures, {total_tables} tables, {total_equations} equations\n\n"
        blocks.append(hint)
    
    for m in modules:
        block = textwrap.dedent(
            f"""
            [MODULE START]
            id: {m.module_id}
            level: {m.level}
            title: {m.title}
            first_sentence: {m.first_sentence}
            last_sentence: {m.last_sentence}
            [MODULE END]
            """
        ).strip()
        blocks.append(block)
    return "\n\n".join(blocks)


def call_azure_gpt(
    messages: List[Dict],
    max_completion_tokens: int = 800,
    seed: Optional[int] = None,
    deployment_override: Optional[str] = None,
) -> Dict:
    """Call Azure OpenAI with gpt-5.1 (or specified deployment)."""
    endpoint = os.getenv("AZURE_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
    deployment = deployment_override or os.getenv("AZURE_GPT_DEPLOYMENT", "gpt-5.1")
    api_version = os.getenv("AZURE_API_VERSION", "2025-01-01-preview")

    if not endpoint or not api_key:
        raise RuntimeError("AZURE_ENDPOINT and AZURE_API_KEY must be set")

    url = f"{endpoint.rstrip('/')}/openai/deployments/{deployment}/chat/completions?api-version={api_version}"

    payload: Dict = {
        "messages": messages,
        "max_completion_tokens": max_completion_tokens,
    }
    if seed is not None:
        payload["seed"] = seed

    headers = {
        "Content-Type": "application/json",
        "api-key": api_key,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if resp.status_code != 200:
        try:
            data = resp.json()
        except Exception:
            data = resp.text
        raise RuntimeError(f"Azure GPT request failed ({resp.status_code}): {data}")

    result = resp.json()
    
    # Debug: 保存完整的 API 响应
    debug_api_path = Path("/tmp/azure_gpt_response.json")
    debug_api_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[DEBUG] Azure GPT full response saved to: {debug_api_path}", file=sys.stderr)
    
    return result


# ============================================================
# Phase 1: Module Role Routing
# ============================================================

def classify_module_roles(modules: List[Module]) -> Dict[str, List[str]]:
    """
    Phase 1: Classify each module into multiple functional roles based on metadata only.
    
    Returns a mapping: {module_id: [role1, role2, ...]}
    """
    summary = build_modules_summary(modules)

    system_prompt = textwrap.dedent(
        """
        You are a precise scientific paper structure classifier with expertise in ML/AI research papers.
        
        CRITICAL: Focus on accuracy and logical consistency. Each module MUST be classified correctly.
        
        ## Input
        You will receive:
        1. [PAPER META]: Overall statistics (figures, tables, equations)
        2. Module list with: id, level, title, first_sentence, last_sentence
        
        ## Classification Strategy
        
        ### PRIORITY 1: Core Four Dimensions (MOST IMPORTANT)
        These four categories define the paper's technical contribution. Be EXTREMELY PRECISE:
        
        ⭐ **task_problem**: Problem definition, research question, motivation
           - Keywords: "problem", "task", "challenge", "motivation", "background", "introduction"
           - Usually appears in: Abstract, Introduction, Problem Statement
           - Must clearly state WHAT problem the paper solves
        
        ⭐ **method_pipeline**: Core algorithmic approach, workflow, procedures
           - Keywords: "method", "approach", "algorithm", "pipeline", "framework", "procedure"
           - Usually appears in: Method, Approach, Algorithm sections
           - Must describe HOW the solution works (step-by-step logic)
        
        ⭐ **model_architecture**: Neural network design, components, structural details
           - Keywords: "architecture", "model", "network", "layer", "component", "structure"
           - Usually appears in: Model, Architecture sections
           - Must describe concrete model/system STRUCTURE (not just workflow)
        
        ⭐ **data**: Datasets, data preprocessing, data collection/annotation
           - Keywords: "data", "dataset", "corpus", "benchmark", "collection", "preprocessing"
           - Usually appears in: Data, Dataset, Benchmark sections
           - Must describe concrete data sources and processing
        
        ### PRIORITY 2: Supporting Dimensions
        
        - **training_inference**: Training details, optimization, hyperparameters, inference
        - **evaluation_results**: Experiments, metrics, performance comparison, ablation
        - **system_deployment**: System design, UI, deployment, real-world application
        - **other**: Introduction, related work, conclusion, appendix, etc.
        
        ## Classification Rules
        
        1. **Multi-label**: A module can have multiple roles (e.g., method_pipeline + model_architecture)
        2. **Main role**: Choose ONE most dominant role per module
        3. **Accuracy over speed**: Take time to reason carefully about core four dimensions
        4. **Use metadata**: Pay attention to [PAPER META] to understand paper type
        5. **Be conservative**: If uncertain between core dimension and "other", prefer "other"
        
        ## Examples
        
        - "3.1 Transformer Architecture" → main_role: model_architecture (describes structure)
        - "3. Method" → could be method_pipeline OR model_architecture (check content!)
        - "4. Experiments" → main_role: evaluation_results
        - "2. Dataset" → main_role: data
        - "1. Introduction" → main_role: task_problem (if defines problem) OR other
        
        ## Output Format
        
        Respond in strict JSON:
        {
          "modules": [
            {
              "module_id": "sec_1",
              "roles": ["task_problem", "method_pipeline"],
              "main_role": "task_problem",
              "reason": "Clear explanation of WHY this classification"
            },
            ...
          ]
        }
        """
    ).strip()

    user_prompt = "Here are the modules:\n\n" + summary

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    # Use a lightweight model for Phase 1 if available
    phase1_deployment = os.getenv("AZURE_GPT_DEPLOYMENT_PHASE1", "gpt-5.1")

    data = call_azure_gpt(
        messages,
        max_completion_tokens=8000,  # GPT-5.1 needs more for reasoning + output
        seed=42,
        deployment_override=phase1_deployment,
    )

    content = data["choices"][0]["message"]["content"].strip()
    
    # Debug: 保存原始 LLM 输出
    debug_path = Path("/tmp/phase1_llm_output.txt")
    debug_path.write_text(content, encoding="utf-8")
    print(f"[DEBUG] Phase 1 LLM output saved to: {debug_path}", file=sys.stderr)

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return _fallback_classify(modules)
        try:
            result = json.loads(match.group(0))
        except Exception:
            return _fallback_classify(modules)

    modules_list = result.get("modules") or []
    roles_map: Dict[str, List[str]] = {}

    for item in modules_list:
        if not isinstance(item, dict):
            continue
        mid = item.get("module_id")
        roles = item.get("roles") or []
        if mid and roles:
            roles_map[mid] = roles

    if not roles_map:
        return _fallback_classify(modules)

    return roles_map


def _fallback_classify(modules: List[Module]) -> Dict[str, List[str]]:
    """Heuristic fallback classifier."""
    roles_map: Dict[str, List[str]] = {}
    for m in modules:
        title_lower = m.title.lower()
        roles = []

        if any(kw in title_lower for kw in ["method", "approach", "pipeline", "方法", "流程"]):
            roles.append("method_pipeline")
        if any(kw in title_lower for kw in ["model", "architecture", "network", "模型", "结构"]):
            roles.append("model_architecture")
        if any(kw in title_lower for kw in ["data", "dataset", "数据"]):
            roles.append("data")
        if any(kw in title_lower for kw in ["experiment", "evaluation", "result", "实验", "评估"]):
            roles.append("evaluation_results")
        if any(kw in title_lower for kw in ["training", "optimization", "训练"]):
            roles.append("training_inference")

        if not roles:
            roles = ["other"]

        roles_map[m.module_id] = roles

    return roles_map


# ============================================================
# Phase 2: Fusion Core Engine (with Nano Banana Pro)
# ============================================================

def build_visual_elements_summary(modules: List[Module]) -> str:
    """Build a summary of figures, tables, and equations from enhanced modules."""
    lines = []
    
    total_figures = 0
    total_tables = 0
    total_equations = 0
    
    for m in modules:
        if m.figures:
            total_figures += len(m.figures)
        if m.tables:
            total_tables += len(m.tables)
        if m.equations:
            total_equations += len(m.equations)
    
    if total_figures == 0 and total_tables == 0 and total_equations == 0:
        return ""
    
    lines.append("\n📊 Visual Elements Summary (from MinerU structured extraction):")
    lines.append(f"  - Figures: {total_figures}")
    lines.append(f"  - Tables: {total_tables}")
    lines.append(f"  - Equations: {total_equations}")
    
    # Add figure captions if available
    for m in modules:
        if m.figures:
            lines.append("\n🖼️  Key Figures:")
            for idx, fig in enumerate(m.figures[:3], 1):  # Show first 3
                caption = fig.get('image_caption', [])
                if caption:
                    caption_text = caption[0][:150] + "..." if len(caption[0]) > 150 else caption[0]
                    lines.append(f"  Figure {idx}: {caption_text}")
            break  # Only show from first module with figures
    
    # Add table info if available
    for m in modules:
        if m.tables:
            lines.append("\n📋 Key Tables:")
            for idx, tbl in enumerate(m.tables[:2], 1):  # Show first 2
                caption = tbl.get('table_caption', [])
                if caption:
                    caption_text = caption[0][:100] + "..." if len(caption[0]) > 100 else caption[0]
                    lines.append(f"  Table {idx}: {caption_text}")
            break
    
    # Add LaTeX equations if available (Optimization 5)
    for m in modules:
        if m.equations:
            lines.append("\n🔢 Key Equations (LaTeX):")
            for idx, eq in enumerate(m.equations[:3], 1):  # Show first 3
                latex = eq.get('text', '')
                if latex and len(latex) < 200:  # Only show short equations
                    lines.append(f"  Eq {idx}: {latex}")
            break
    
    return "\n".join(lines)


def run_fusion_core(modules: List[Module], roles_map: Dict[str, List[str]]) -> Dict:
    """
    Phase 2: Deep reading + Nano Banana Pro visual translation.
    
    Returns analysis_result dict with:
    - logic_summaries
    - main_figure_ideas (two designs with full Nano Banana Pro params)
    """
    
    # Build full markdown with role hints
    role_hints_lines = ["Role hints from Phase 1:"]
    for mid, roles in roles_map.items():
        role_hints_lines.append(f"  {mid}: {', '.join(roles)}")
    role_hints_text = "\n".join(role_hints_lines)

    full_markdown_blocks = []
    for m in modules:
        header = f"# [{m.module_id}] {m.title}\n\n"
        full_markdown_blocks.append(header + m.content)
    full_markdown = "\n\n".join(full_markdown_blocks)

    system_prompt = textwrap.dedent(
        """
        You are a dual expert: a senior academic researcher AND the chief scientific illustrator for "Nano Banana Pro".
        
        Your mission is to perform two parallel tasks with EXTREME ACCURACY:
        
        ===== TASK A: Logic Extraction (CORE FOUR DIMENSIONS) =====
        
        CRITICAL: Extract precise, detailed summaries for the CORE FOUR dimensions. These define the paper's technical contribution.
        
        ## PRIORITY 1: Core Four Dimensions (MUST be accurate and comprehensive)
        
        ⭐ **task_problem** (WHAT problem does this paper solve?)
           - Define the specific research problem/task
           - Explain current limitations and challenges
           - State why existing methods fail
           - Clearly articulate the research gap
           Example: "The paper addresses X problem where existing Y methods fail because Z..."
        
        ⭐ **method_pipeline** (HOW does the solution work?)
           - Describe the algorithmic workflow step-by-step
           - Explain the key procedures and logic flow
           - Highlight novel algorithmic contributions
           - Use clear, logical structure (Stage 1→2→3 or Pipeline A→B→C)
           Example: "The method consists of: (1) Input preprocessing via..., (2) Core algorithm X that..., (3) Output refinement..."
        
        ⭐ **model_architecture** (WHAT is the concrete structure?)
           - Describe the system/model architecture in detail
           - Specify components, modules, layers
           - Explain how components connect and interact
           - Include architectural innovations
           Example: "The model comprises: encoder with N layers of..., decoder using..., attention mechanism connecting..."
        
        ⭐ **data** (WHAT data is used and how?)
           - List all datasets with sizes and characteristics
           - Describe data collection/annotation process
           - Explain preprocessing and augmentation
           - Specify train/val/test splits
           Example: "Datasets: (1) DatasetA: 10K samples from..., (2) DatasetB: benchmark with..."
        
        ## PRIORITY 2: Supporting Dimensions (extract if present)
        
        - **training_inference**: Training details, optimization, hyperparameters
        - **evaluation_results**: Experiments, metrics, SOTA comparison, ablation
        - **system_deployment**: System design, UI, deployment (if applicable)
        
        ===== TASK B: Visual Translation (Nano Banana Pro Protocol) =====
        Design TWO completely different ACADEMIC PAPER MAIN FIGURE proposals for this paper.
        
        ## IMPORTANT: Academic Paper Main Figure Requirements
        
        You are designing the **main figure (graphical abstract)** for an academic paper, which must:
        
        1. **Single Integrated Composition**: One cohesive image that summarizes the paper's core contribution
        2. **Self-Contained**: Understandable without reading the full paper text
        3. **Information Hierarchy**: Clear visual flow from problem → method → results
        4. **Publication Ready**: Suitable for both print and digital display (landscape 16:9 or 4:3 ratio preferred)
        5. **Professional Academic Style**: Balance between visual appeal and scientific rigor
        
        Each design should answer: "If a researcher sees only this figure, what is the paper's key innovation?"
        
        You must strictly follow the "Nano Banana Pro Visual Protocol":
        
        ## 3.1 Visual Containers (select one per design)
        
        - isometric_exploded_view:
          Use for: Transformers, multi-modal models, chip design, precision machinery
          Features: Components float in vertical layers, connected by light flows, exposing internal black-box structure
        
        - ar_real_world_overlay:
          Use for: Computer vision, autonomous driving, smart city, AR applications
          Features: High-fidelity photorealistic base (street/indoor), overlaid with digital wireframes, bounding boxes, floating data labels
        
        - modular_infographic_grid:
          Use for: Multi-model performance comparison, dataset taxonomy, tool library overview
          Features: Screen divided into 2x2 or 3x3 card regions, each showing a different sub-topic, emphasizing neatness and contrast
        
        - sequential_storyboard:
          Use for: User interaction flow, agent decision process, end-to-end operational steps
          Features: Comic-like horizontal panels (Step 1 -> Step 2 -> Step 3), clear temporal flow
        
        - knowledge_network:
          Use for: Literature review, logic reasoning, entity relation extraction
          Features: Center-radial or hierarchical tree structure, nodes connected by solid/dashed lines, similar to mind maps
        
        - pipeline_flow_diagram:
          Use for: Data processing pipeline, model training workflow, system architecture
          Features: Left-to-right or top-to-bottom flow with clear stages, arrows showing data/control flow, color-coded processing blocks
        
        - before_after_comparison:
          Use for: Method improvements, ablation studies, performance gains
          Features: Split-screen or side-by-side layout, clear visual contrast between baseline and proposed method
        
        - circular_ecosystem:
          Use for: Multi-component systems, closed-loop processes, interconnected modules
          Features: Central core surrounded by satellite components in circular arrangement, bidirectional arrows showing interactions
        
        - layered_stack_diagram:
          Use for: Deep learning architectures, protocol stacks, hierarchical frameworks
          Features: Horizontal layers stacked vertically, each layer shows internal structure, vertical connections between layers
        
        - research_poster_layout:
          Use for: Comprehensive overview, multi-aspect summary, conference presentation
          Features: Title banner + multiple organized sections (problem/method/results), academic poster aesthetic
        
        ## 3.2 Art Style Filters (select one per design)
        
        **IMPORTANT: DEFAULT TO BRIGHT STYLES - Both designs should use bright, academic-friendly styles unless the paper topic specifically requires dark themes.**
        
        **PRIORITY: Use these bright styles first:**
        - academic_bright (HIGHEST PRIORITY - clean, professional)
        - infographic_colorful (playful, educational)
        - data_journalism (editorial, storytelling)
        - medical_illustration (soft, clinical)
        - scientific_blueprint (technical, precise)
        - professional_business (whiteboard, minimalist)
        
        **Use dark styles ONLY if paper topic matches (e.g., aerospace, gaming, night vision):**
        - engineering_tech (dark tech background)
        - modern_dashboard (dark mode UI)
        
        - academic_bright:
          Source: Nature/Science journal figures
          Keywords: clean white background, vibrant color palette (blue/orange/green gradients), professional vector graphics, clear typography, high contrast for readability, publication-quality rendering
        
        - medical_illustration:
          Source: medical textbooks and scientific posters
          Keywords: pastel color scheme, soft blue and coral tones, anatomical precision, clean labels and annotations, clinical whiteboard aesthetic, educational clarity
        
        - infographic_colorful:
          Source: data journalism and educational materials
          Keywords: bright primary colors (red/blue/yellow/green), flat design, playful icons, clear visual hierarchy, engaging and accessible, light grey or white background
        
        - engineering_tech:
          Source: SpaceX/aerospace engine diagrams
          Keywords: industrial CAD rendering, blueprint aesthetic, neon blue glowing edges, semi-transparent glass materials, dark tech background
        
        - cozy_hand_drawn:
          Source: hand journaling/illustration
          Keywords: watercolor and ink texture, dotted notebook background, cute hand-drawn icons, warm tones, high affinity
        
        - modern_dashboard:
          Source: data visualization dashboards
          Keywords: dark mode UI, black-gold/cyan color scheme, flat vector icons, glowing data charts, HUD heads-up display style
        
        - professional_business:
          Source: McKinsey whiteboards
          Keywords: marker pen hand-drawn style, minimalist whiteboard background, clear logical connections, sticky note elements, high readability
        
        - scientific_blueprint:
          Source: scientific textbooks and technical manuals
          Keywords: blueprint grid background (light blue or white), precise line drawings, technical annotations with leader lines, monochromatic or limited color palette, engineering precision
        
        - data_journalism:
          Source: The New York Times graphics, FiveThirtyEight
          Keywords: editorial illustration style, bold color blocks, geometric shapes, clear data storytelling, mix of charts and iconography, highly readable
        
        - minimalist_swiss:
          Source: Swiss design/Bauhaus
          Keywords: extreme minimalism, grid-based layout, limited color palette (usually 2-3 colors), strong typography, geometric precision, white space emphasis
        
        - organic_natural:
          Source: environmental science publications
          Keywords: earth tones (green/brown/beige), natural textures, organic shapes, friendly and approachable, sustainability-focused aesthetic
        
        - tech_gradient:
          Source: modern tech company presentations (Apple, Google)
          Keywords: smooth gradients (purple-blue, orange-pink), glassmorphism, soft shadows, modern sans-serif fonts, clean and futuristic
        
        ## 3.3 Color Palette Suggestions (optional, enhance visual richness)
        
        Consider specifying a concrete color palette to enhance visual coherence:
        
        - academic_cool: Deep blue (#2E5090), Orange (#E67E22), Teal (#16A085) - common in STEM papers
        - medical_soft: Soft blue (#5DADE2), Coral (#EC7063), Mint green (#52BE80) - friendly and clinical
        - data_vivid: Purple (#8E44AD), Yellow (#F39C12), Cyan (#3498DB) - high contrast for data viz
        - nature_earth: Forest green (#27AE60), Terracotta (#D35400), Beige (#D4AC0D) - organic feel
        - tech_neon: Electric blue (#00D9FF), Hot pink (#FF006E), Lime (#39FF14) - futuristic
        - monochrome_accent: Grayscale base + single accent color (e.g., all greys + red highlights) - minimalist
        
        ## 3.4 Deconstruction Logic (required for each design)
        
        You must complete the following thinking chain before generating the final prompt:
        - core_object: Concretize the abstract algorithm into a physical object (e.g., Encoder -> "glowing multi-layer glass cube")
        - components: List 3-5 specific parts that must appear (e.g., input layer, attention heads, output layer)
        - flow: What visual element represents data flow? (e.g., blue laser beams, dashed arrows, liquid pipelines)
        - colors (NEW): Optionally specify a color palette from section 3.3 or create a custom one that fits the paper's domain
        
        ## Magic Instruction (critical) - ENHANCED FOR REASONING-CAPABLE IMAGE MODELS
        
        When constructing the final_prompt, you MUST follow this DETAILED formula:
        
        "Academic paper main figure showing" 
        + [SPECIFIC subject from paper: include actual model/algorithm names, not just "a model"]
        + [selected visual container with WHY it fits]
        + [CONCRETE components from extracted data: actual figure captions, equation symbols, architecture layers]
        + [selected art style keywords]
        + [DETAILED deconstruction: use extracted LaTeX equations, specific dataset names, actual performance numbers]
        + [Spatial layout: where each component goes, what connects to what]
        + [Color coding: which color represents what concept]
        + "single cohesive composition, publication-ready layout, professional academic visualization, 16:9 aspect ratio, 8k, high resolution, cinematic lighting"
        
        CRITICAL FOR COMPLEX PROMPTS (300-500 words): 
        - ✅ START: "Academic paper main figure showing" to establish context
        - ✅ USE EXTRACTED DATA: If you saw "Figure 1: Transformer architecture", write "showing the Transformer architecture with encoder stack on left (6 layers of multi-head self-attention + feed-forward), decoder on right..."
        - ✅ INCLUDE FORMULAS: If you saw "Attention(Q,K,V) = softmax(QK^T/√d_k)V", mention "with the scaled dot-product attention mechanism (softmax(QK^T/√d_k)V) connecting..."
        - ✅ MENTION DATASETS: If you saw "Table 1: Results on WMT2014", write "evaluation panel showing WMT2014 English-German translation with 28.4 BLEU score..."
        - ✅ BE SPECIFIC: Not "a neural network" but "6-layer encoder-decoder Transformer with 8 attention heads and 512-dimensional embeddings"
        - ✅ END: "single cohesive composition, publication-ready layout"
        - ❌ NO GENERIC PROMPTS: Don't write "showing a model architecture" - write the ACTUAL architecture from the paper!
        
        ===== OUTPUT FORMAT =====
        
        Respond in the following JSON format:
        {
          "analysis_result": {
            "logic_summaries": {
              "task_problem": "⭐ CORE: Detailed problem definition (3-5 sentences minimum)",
              "method_pipeline": "⭐ CORE: Step-by-step algorithmic workflow (4-6 sentences, clear structure)",
              "model_architecture": "⭐ CORE: Concrete architectural components and connections (3-5 sentences)",
              "data": "⭐ CORE: Complete dataset details with sizes and preprocessing (3-4 sentences)",
              "training_inference": "Training/optimization details (if present, 2-3 sentences)",
              "evaluation_results": "Experimental results and metrics (if present, 2-3 sentences)",
              "system_deployment": "Deployment/system design (if present, 1-2 sentences or empty)"
            },
            "main_figure_ideas": [
              {
                "concept_title": "Clear, descriptive title reflecting the paper's main contribution",
                "target_audience": "Who will benefit most from this visual?",
                "rationale": "Why this flow-based container fits? How does it map to the paper's logic?",
                "visual_params": {
                  "container": "pipeline_flow_diagram (or sequential_storyboard, layered_stack_diagram)",
                  "style": "academic_bright (DEFAULT - or infographic_colorful, data_journalism, medical_illustration)",
                  "deconstruction": {
                    "core_object": "Specific object from paper (e.g., 'DPO training loop', 'Transformer encoder-decoder')",
                    "components": [
                      "Concrete component 1 from paper (use actual names from figures/text)",
                      "Concrete component 2 with specific details (e.g., '6-layer encoder with 8 attention heads')",
                      "Concrete component 3 (e.g., 'WMT2014 dataset evaluation panel showing 28.4 BLEU')"
                    ],
                    "flow": "Specific data/control flow (e.g., 'cyan arrows for preference pairs → DPO loss → implicit reward update')",
                    "colors": "Specific color mapping (e.g., 'teal for DPO, orange for PPO baseline, grey for shared SFT')"
                  },
                  "final_prompt": "300-500 word DETAILED prompt using ACTUAL extracted data: mention specific model names, layer counts, dataset names, equation symbols (e.g., softmax(QK^T/√d_k)V), performance numbers, etc. NOT generic descriptions!"
                }
              },
              {
                "concept_title": "Second design with COMPLETELY different perspective",
                "target_audience": "Different audience or same audience with different focus",
                "rationale": "Why this container/style provides complementary view?",
                "visual_params": {
                  "container": "DIFFERENT container (can be flow-based or conceptual-based)",
                  "style": "DIFFERENT BRIGHT style from first design (e.g., if first is academic_bright, use infographic_colorful or data_journalism)",
                  "deconstruction": {
                    "core_object": "...",
                    "components": ["Use actual extracted information here too!"],
                    "flow": "...",
                    "colors": "..."
                  },
                  "final_prompt": "Another 300-500 word DETAILED prompt grounded in extracted visual elements, equations, and data"
                }
              }
            ]
          }
        }
        """
    ).strip()

    # Build visual elements summary from structured JSON
    visual_elements_summary = build_visual_elements_summary(modules)
    
    user_prompt = (
        "🎯 CRITICAL REQUIREMENTS FOR ACADEMIC PAPER MAIN FIGURES:\n\n"
        "1. **FLOW-BASED VISUAL PRIORITY** (MOST IMPORTANT):\n"
        "   - At least ONE design MUST use a FLOW/PIPELINE-based container:\n"
        "     • pipeline_flow_diagram (PREFERRED for most papers)\n"
        "     • sequential_storyboard (for step-by-step processes)\n"
        "     • layered_stack_diagram (for hierarchical architectures)\n"
        "   - Academic papers are best explained through WORKFLOW and LOGIC FLOW!\n\n"
        
        "2. **DATA-DRIVEN PROMPT GENERATION** (USE EXTRACTED INFORMATION):\n"
        "   - You have access to structured data: figure captions, table descriptions, LaTeX equations\n"
        "   - MUST incorporate these CONCRETE DETAILS into your final_prompt:\n"
        "     • If you see 'Figure 1: Architecture of X', describe X's specific components in final_prompt\n"
        "     • If you see equations like Attention(Q,K,V), mention the actual formula in final_prompt\n"
        "     • If you see 'Table 1: Performance on X datasets', include dataset names and metrics\n"
        "   - DO NOT write generic prompts! Use the ACTUAL content from Visual Elements Summary!\n\n"
        
        "3. **LEVERAGE REASONING-CAPABLE IMAGE MODEL**:\n"
        "   - The image generation model has reasoning ability - use it!\n"
        "   - Your final_prompt can be COMPLEX and DETAILED (300-500 words is fine)\n"
        "   - Include specific architectural components, mathematical notations, data flow details\n"
        "   - Be precise with technical terms from the paper (model names, layer types, algorithm steps)\n\n"
        
        "4. **TWO DIFFERENT DESIGNS (BOTH BRIGHT STYLES)**:\n"
        "   - First design: Flow-based container (pipeline/sequential/layered) + BRIGHT style (academic_bright/infographic_colorful/data_journalism)\n"
        "   - Second design: Different container OR different perspective + DIFFERENT BRIGHT style\n"
        "   - DEFAULT: Use bright styles (academic_bright, infographic_colorful, data_journalism, medical_illustration)\n"
        "   - AVOID dark styles (engineering_tech, modern_dashboard) unless paper topic specifically requires them\n\n"
        
        + role_hints_text + "\n"
        + visual_elements_summary + "\n\n"
        + "=" * 80 + "\n"
        + "Full paper markdown:\n\n"
        + full_markdown
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    data = call_azure_gpt(
        messages,
        max_completion_tokens=16000,  # GPT-5.1 needs much more: reasoning + full JSON output
        seed=123,
    )

    content = data["choices"][0]["message"]["content"].strip()
    
    # Debug: 保存原始 LLM 输出
    debug_path = Path("/tmp/phase2_llm_output.txt")
    debug_path.write_text(content, encoding="utf-8")
    print(f"[DEBUG] Phase 2 LLM output saved to: {debug_path}", file=sys.stderr)

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", content)
        if not match:
            return {"analysis_result": {"raw_response": content}}
        try:
            result = json.loads(match.group(0))
        except Exception:
            return {"analysis_result": {"raw_response": content}}

    return result.get("analysis_result") or result


# ============================================================
# Phase 3: Report Rendering
# ============================================================

def render_report(analysis_result: Dict) -> str:
    """
    Phase 3: Render structured data into a beautiful Markdown report.
    """
    parts = ["# Paper Analysis & Visual Plan", ""]

    # Check if we got a fallback raw response
    if "raw_response" in analysis_result:
        parts.append("## Raw LLM Response")
        parts.append("```")
        parts.append(analysis_result["raw_response"])
        parts.append("```")
        return "\n".join(parts)

    logic_summaries = analysis_result.get("logic_summaries") or {}
    main_figure_ideas = analysis_result.get("main_figure_ideas") or []

    # Render logic summaries
    summaries_order = [
        ("task_problem", "Task / Problem"),
        ("data", "Data"),
        ("method_pipeline", "Method / Pipeline"),
        ("model_architecture", "Model / Architecture"),
        ("training_inference", "Training & Inference"),
        ("evaluation_results", "Evaluation / Results"),
        ("system_deployment", "System / Deployment"),
    ]

    for key, title in summaries_order:
        summary = logic_summaries.get(key)
        if summary and str(summary).strip():
            parts.append(f"## {title}")
            parts.append(str(summary))
            parts.append("")

    # Render main figure brainstorming section
    if main_figure_ideas:
        parts.append("---")
        parts.append("")
        parts.append("# 🎨 Main Figure Brainstorming")
        parts.append("")
        parts.append("*Powered by Nano Banana Pro Visual Protocol*")
        parts.append("")

        for idx, idea in enumerate(main_figure_ideas, 1):
            if not isinstance(idea, dict):
                continue

            concept_title = idea.get("concept_title", f"Design {idx}")
            target_audience = idea.get("target_audience", "N/A")
            rationale = idea.get("rationale", "N/A")
            visual_params = idea.get("visual_params") or {}

            parts.append(f"## Design {idx}: {concept_title}")
            parts.append("")
            parts.append(f"**Target Audience**: {target_audience}")
            parts.append("")
            parts.append(f"**Rationale**: {rationale}")
            parts.append("")

            container = visual_params.get("container", "N/A")
            style = visual_params.get("style", "N/A")
            deconstruction = visual_params.get("deconstruction") or {}

            parts.append(f"**Visual Container**: `{container}`")
            parts.append(f"**Art Style**: `{style}`")
            parts.append("")

            core_object = deconstruction.get("core_object", "N/A")
            components = deconstruction.get("components") or []
            flow = deconstruction.get("flow", "N/A")

            parts.append(f"**Core Object**: {core_object}")
            parts.append(f"**Components**:")
            if isinstance(components, list):
                for comp in components:
                    parts.append(f"  - {comp}")
            else:
                parts.append(f"  - {components}")
            parts.append(f"**Flow**: {flow}")
            parts.append("")

            final_prompt = visual_params.get("final_prompt", "")
            if final_prompt:
                parts.append("**🎨 Final Prompt (Ready for Image Generation):**")
                parts.append("```")
                parts.append(final_prompt)
                parts.append("```")
            parts.append("")

    return "\n".join(parts)


# ============================================================
# Main Orchestration
# ============================================================

def main(argv=None):
    parser = argparse.ArgumentParser(
        description="PDF → Visual Plan Pipeline (Nano Banana Pro Edition)",
    )
    parser.add_argument("pdf", type=str, help="Path to input PDF")
    parser.add_argument("--workdir", type=str, default=".pdf_flow_output", help="Work directory")
    parser.add_argument("--report", type=str, default=None, help="Output report path")

    args = parser.parse_args(argv)

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.is_file():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    workdir_base = Path(args.workdir).expanduser().resolve()
    # Create a unique subdirectory for this PDF to avoid conflicts
    pdf_specific_dir = workdir_base / pdf_path.stem
    pdf_specific_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/5] Running MinerU CLI on {pdf_path} ...", file=sys.stderr)
    md_path, content_list_path = run_mineru_cli(pdf_path, pdf_specific_dir)
    print(f"[1/5] MinerU output: {md_path}", file=sys.stderr)
    if content_list_path:
        print(f"[1/5] Found structured data: {content_list_path}", file=sys.stderr)

    print("[2/5] Parsing markdown into modules ...", file=sys.stderr)
    md_text = md_path.read_text(encoding="utf-8", errors="ignore")
    modules = parse_markdown_modules(md_text)
    if not modules:
        raise RuntimeError("No modules parsed")
    print(f"[2/5] Parsed {len(modules)} modules", file=sys.stderr)
    
    # Enhance modules with structured JSON data
    modules = enhance_modules_with_json(modules, content_list_path)

    print("[3/5] Phase 1: Classifying module roles ...", file=sys.stderr)
    roles_map = classify_module_roles(modules)
    print(f"[3/5] Roles map: {len(roles_map)} modules classified", file=sys.stderr)

    print("[4/5] Phase 2: Running Fusion Core (Nano Banana Pro) ...", file=sys.stderr)
    analysis_result = run_fusion_core(modules, roles_map)
    print(f"[4/5] Analysis complete", file=sys.stderr)

    print("[5/5] Phase 3: Rendering report ...", file=sys.stderr)
    report_md = render_report(analysis_result)

    if args.report:
        report_path = Path(args.report).expanduser().resolve()
    else:
        report_name = pdf_path.stem + "_visual_plan.md"
        report_path = workdir_base / report_name

    report_path.write_text(report_md, encoding="utf-8")
    print(f"✅ Done. Report saved to: {report_path}")


if __name__ == "__main__":
    main()
