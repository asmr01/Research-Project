# Deep Research

## Overview

Fractal exploration of any question through recursive AI agents. A question spawns angles, each angle spawns deeper angles, the tree grows until questions become atomic — then everything synthesizes back up into one comprehensive answer.

## Project Structure

```
Research-Project/
├── src/deep_research/
│   ├── core/                    # MasterChef framework
│   │   ├── node.py              # Typed nodes, epistemic states
│   │   ├── graph.py             # Knowledge graphs with persistence
│   │   ├── operation.py         # Operation protocol (ABC)
│   │   ├── strategy.py          # Declarative strategies
│   │   ├── chef.py              # MasterChef orchestrator
│   │   └── operations/          # Concrete operations
│   │       ├── decompose.py     # DECOMPOSE: Question → Sub-questions
│   │       ├── answer.py        # ANSWER: Question → Answer (with ensemble)
│   │       ├── synthesize.py    # SYNTHESIZE: Findings → Synthesis
│   │       ├── detect.py        # DETECT: Blind spots, tensions
│   │       └── ground.py        # GROUND: Web-verified claims
│   ├── providers/               # LLM integrations (httpx-based)
│   │   ├── claude.py            # Anthropic API
│   │   ├── gemini.py            # Google AI API
│   │   ├── openai_azure.py      # Azure OpenAI
│   │   ├── openrouter.py        # OpenRouter (Grok)
│   │   └── kimi.py              # Moonshot AI
│   ├── recipes/                 # Higher-level methodologies
│   │   ├── perspective.py       # Perspective expansion
│   │   └── socratic.py          # Socratic questioning
│   └── cli.py                   # Typer CLI entry point
├── deep-research.sh             # Bash wrapper
├── psychiatric-feedback-research.sh  # Domain-specific wrapper
├── pyproject.toml               # Python packaging
└── claude.md                    # This file
```

## Development

### Setup

```bash
pip install -e ".[dev]"
cp .env.example .env  # Add your API keys
```

### Running

```bash
deep-research research -d 2 "Your question"
deep-research socratic "Your question"
deep-research perspectives "Your question"
```

### Key Patterns

- **Providers use httpx** for async HTTP. Each provider implements `LLMProvider.call()`.
- **Model strings**: `"provider:model"` or aliases like `"haiku"`, `"flash"`, `"opus"`.
- **Operations** are epistemic transitions: they take a Node + Graph and return new Nodes.
- **Strategies** are declarative step lists; MasterChef executes them.
- **KnowledgeGraph** is the central data structure; saves to JSON checkpoints.

### Code Style

- Python 3.10+, type hints throughout
- Pydantic models for data (Node)
- asyncio for concurrency
- Rich for terminal output
- Keep operations stateless; all state lives in KnowledgeGraph

## Guidelines for Claude

- Read relevant files before making changes
- Keep changes focused and minimal
- All LLM calls go through `providers.call_llm()` — never call APIs directly in operations
- New operations should subclass `Operation` and implement `execute()`
- New providers should subclass `LLMProvider` and implement `call()`
