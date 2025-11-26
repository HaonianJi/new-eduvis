# Paper2VisualPlan

Automatically convert academic papers (PDF) into structured visual plans with intelligent content analysis.

## ✨ Features

- **Three-Phase Architecture**: 
  - Phase 1: Module role classification (task, method, data, results, etc.)
  - Phase 2: Deep content extraction with visual elements
  - Phase 3: Markdown report generation
- **Smart Visual Distribution**: Automatically associates figures/tables/equations to relevant sections
- **Core Four Dimensions**: Emphasizes task_problem, method_pipeline, model_architecture, and data
- **LaTeX Support**: Direct equation extraction and display
- **Powered by MinerU**: High-quality PDF parsing with OCR support

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/your-username/paper2visualplan.git
cd paper2visualplan
```

### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Azure OpenAI credentials
# AZURE_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_API_KEY=your_api_key_here
```

### 3. Install MinerU (One-Click)

```bash
chmod +x setup_mineru.sh
./setup_mineru.sh
```

### 4. Run Pipeline

```bash
# Make script executable
chmod +x run_visual_plan.sh

# Process a paper
./run_visual_plan.sh your_paper.pdf
```

Output will be saved to `.visual_plan_output/`

## 📋 Requirements

- Python 3.10+
- Azure OpenAI API access (GPT-4 or GPT-5)
- 8GB RAM minimum (16GB recommended)
- macOS or Linux

## 🛠️ Manual Installation

If the automatic script doesn't work:

```bash
# Create virtual environment
cd MinerU
python3 -m venv venv
source venv/bin/activate

# Install MinerU
pip install magic-pdf[full]==0.7.1b1 --extra-index-url https://wheels.myhloli.com

# Download models
mineru-models-download --model_type pipeline
```

## 📖 Usage

### Basic Usage

```bash
./run_visual_plan.sh paper.pdf
```

### Advanced Usage

```bash
# Specify custom output directory
python project/pdf_to_flowchart_v2.py \
  --pdf paper.pdf \
  --output ./custom_output
```

## 🎯 Output Structure

```
.visual_plan_output/
└── paper_name/
    ├── paper_name_visual_plan.md    # Final visual plan
    ├── paper_name.md                # MinerU parsed markdown
    └── auto/                        # Extracted figures/tables
```

## 🔧 Configuration

Edit `.env` file:

```bash
# Required
AZURE_ENDPOINT=your_endpoint
AZURE_API_KEY=your_key

# Optional
AZURE_GPT_DEPLOYMENT=gpt-5.1           # Default deployment name
AZURE_API_VERSION=2025-01-01-preview   # API version
```

## 📚 Documentation

- `project/VISUAL_PLAN_GUIDE.md` - Detailed pipeline guide
- `project/CHANGELOG_V2.md` - Version history

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License

## 🙏 Acknowledgments

- [MinerU](https://github.com/opendatalab/MinerU) - PDF parsing engine
- Azure OpenAI - LLM backend
