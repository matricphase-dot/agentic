# 🏗️ Agentic Workflow Engine

A **Generalized Agentic Workflow Engine** designed to surpass traditional AI assistants by teaching workflows instead of just answering questions. This system guarantees correctness through multi-agent verification and works seamlessly across any software or data source. This project represents a research demonstrator exploring the agentic design space.

## 🎯 Ultimate Vision & Features

*   **Workflow Teaching**: Learn by demonstration. Record a process once, and the system can automate it forever.
*   **Guaranteed Correctness**: Employs a multi-agent verification system (Planner, Researcher, QA, Executor) to validate each step.
*   **Tool Agnostic**: Integrates with a wide registry of tools (Web APIs, Databases, Compilers, Browsers).
*   **Self-Improving Memory**: Uses a hybrid memory system (Neo4j Graph + Chroma Vector Store) to learn from successful executions and past artifacts.
*   **Production Ready**: Built with scalability, error handling, and observability in mind from the ground up.

## 🚀 Quick Start

### Prerequisites
*   Python 3.8+
*   Git
*   A Google Gemini API key ([Get one for free here](https://makersuite.google.com/app/apikey))

### Installation & Setup
`ash
# 1. Clone the repository
git clone <your-repository-url>
cd agentic-core

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure your environment
cp .env.example .env
# Edit .env with your GEMINI_API_KEY and other settings

# 4. Verify the installation
python main.py run "Check langchain version"
