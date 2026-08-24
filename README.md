# 🔎 CodeLens AI

AI-powered Python code analysis and code quality dashboard.

CodeLens AI analyzes Python projects using AST, Radon and Bandit
and provides a visual dashboard for understanding code quality,
security issues and project structure.

## ✨ Features

- 🔍 AST-based code analysis
- 📊 Code quality scoring
- 🛡 Security analysis with Bandit
- 📈 Complexity analysis with Radon
- 🏗 Class and function detection
- 📦 Import analysis
- ⚠ TODO / FIXME detection
- 🖨 Suspicious print detection
- 📁 Project scanner
- ⚡ Background analysis
- 🖥 Modern CustomTkinter dashboard
- 📊 Maintainability metrics
- 🎯 Overall project score

## 🛠 Tech Stack

- Python
- CustomTkinter
- AST
- Radon
- Bandit

## 🚀 Installation

```bash
git clone YOUR_REPOSITORY_URL
cd CodeLens-AI

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
▶ Run
python -m app.main
📁 Project Structure
CodeLens-AI/
│
├── app/
│   ├── core/
│   │   ├── analyzer.py
│   │   ├── parser.py
│   │   ├── scanner.py
│   │   ├── quality.py
│   │   ├── security.py
│   │   ├── score_engine.py
│   │   └── project_analyzer.py
│   │
│   ├── ui/
│   │   └── dashboard.py
│   │
│   └── main.py
│
├── tests/
├── .gitignore
├── requirements.txt
└── README.md
📌 Roadmap
 Project scanner
 AST analyzer
 Security analyzer
 Code quality analyzer
 Score engine
 GUI dashboard
 Background analysis
 Issue filtering
 HTML reports
 JSON export
 Code visualization
 AI-powered explanations
📄 License

MIT License
