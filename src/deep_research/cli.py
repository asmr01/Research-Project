"""CLI interface for Deep Research."""

from __future__ import annotations

import asyncio
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.tree import Tree

load_dotenv()

app = typer.Typer(
    name="deep-research",
    help="Fractal exploration of any question through recursive AI agents.",
    no_args_is_help=True,
)
console = Console()


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, show_time=False, show_path=False)],
    )


def _slugify(text: str, max_len: int = 50) -> str:
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug[:max_len]


def _make_output_dir(question: str, base: str | None = None) -> Path:
    base_path = Path(base) if base else Path("reports")
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = _slugify(question)
    out = base_path / f"{date_str}-{slug}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _build_chef(
    model: str,
    researcher: str,
    leaves: str | None,
    merger: str | None,
    depth: int,
    parallel: int,
    output_dir: Path,
) -> tuple:
    """Build MasterChef with all operations registered."""
    from deep_research.core.chef import MasterChef
    from deep_research.core.operations import (
        DecomposeOperation,
        AnswerOperation,
        SynthesizeOperation,
        DetectOperation,
        GroundOperation,
    )

    chef = MasterChef(
        output_dir=output_dir,
        max_parallel=parallel,
        max_depth=depth,
    )
    chef.register_operation(DecomposeOperation())
    chef.register_operation(AnswerOperation())
    chef.register_operation(SynthesizeOperation())
    chef.register_operation(DetectOperation())
    chef.register_operation(GroundOperation())

    context = {
        "model": model,
        "researcher_model": researcher,
        "merger_model": merger,
        "leaf_models": leaves.split(",") if leaves else None,
    }

    return chef, context


@app.command()
def research(
    question: str = typer.Argument(..., help="The research question"),
    model: str = typer.Option("opus", "-m", "--model", help="Orchestrator model"),
    researcher: str = typer.Option("haiku", "-r", "--researcher", help="Researcher model"),
    leaves: Optional[str] = typer.Option(None, "-l", "--leaves", help="Leaf ensemble (comma-separated)"),
    merger: Optional[str] = typer.Option(None, "--merger", help="Model for merging ensembles"),
    depth: int = typer.Option(0, "-d", "--depth", help="Max depth (0 = unlimited)"),
    parallel: int = typer.Option(10, "-p", "--parallel", help="Max concurrent agents"),
    web: bool = typer.Option(False, "-w", "--web", help="Enable web search"),
    output: Optional[str] = typer.Option(None, "-o", "--output", help="Output directory"),
    strategy: str = typer.Option("recursive_research", "--strategy", help="Strategy name"),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Verbose logging"),
) -> None:
    """Run recursive research on a question."""
    _setup_logging(verbose)

    output_dir = _make_output_dir(question, output)
    chef, context = _build_chef(model, researcher, leaves, merger, depth, parallel, output_dir)
    context["web_search"] = web

    console.print(Panel(
        f"[bold]{question}[/bold]\n\n"
        f"Strategy: {strategy} | Model: {model} | Depth: {depth or '∞'} | Parallel: {parallel}",
        title="Deep Research",
        border_style="blue",
    ))

    result = asyncio.run(chef.cook(question, strategy, context))

    # Display results
    synth = result.final_synthesis
    if synth:
        console.print(Panel(synth.content, title="Synthesis", border_style="green"))

    summary = result.graph.summary()
    console.print(f"\n[dim]Nodes: {summary['total_nodes']} | "
                  f"Max depth: {summary['max_depth']} | "
                  f"Output: {output_dir}[/dim]")


@app.command()
def socratic(
    question: str = typer.Argument(..., help="The question to examine"),
    model: str = typer.Option("opus", "-m", "--model"),
    researcher: str = typer.Option("haiku", "-r", "--researcher"),
    parallel: int = typer.Option(10, "-p", "--parallel"),
    output: Optional[str] = typer.Option(None, "-o", "--output"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
) -> None:
    """Socratic mode - challenge assumptions and improve questions."""
    _setup_logging(verbose)
    from deep_research.recipes.socratic import run_socratic_inquiry

    output_dir = _make_output_dir(question, output)

    console.print(Panel(
        f"[bold]{question}[/bold]\n\nMode: Socratic Inquiry",
        title="Deep Research",
        border_style="yellow",
    ))

    result = asyncio.run(run_socratic_inquiry(
        question, output_dir, model=model, researcher_model=researcher,
        max_parallel=parallel,
    ))

    synth = result.final_synthesis
    if synth:
        console.print(Panel(synth.content, title="Socratic Synthesis", border_style="green"))

    console.print(f"\n[dim]Output: {output_dir}[/dim]")


@app.command()
def perspectives(
    question: str = typer.Argument(..., help="The question to analyze"),
    model: str = typer.Option("opus", "-m", "--model"),
    researcher: str = typer.Option("haiku", "-r", "--researcher"),
    parallel: int = typer.Option(10, "-p", "--parallel"),
    output: Optional[str] = typer.Option(None, "-o", "--output"),
    verbose: bool = typer.Option(False, "-v", "--verbose"),
) -> None:
    """Perspective expansion - multi-angle analysis."""
    _setup_logging(verbose)
    from deep_research.recipes.perspective import run_perspective_expansion

    output_dir = _make_output_dir(question, output)

    console.print(Panel(
        f"[bold]{question}[/bold]\n\nMode: Perspective Expansion",
        title="Deep Research",
        border_style="magenta",
    ))

    result = asyncio.run(run_perspective_expansion(
        question, output_dir, model=model, researcher_model=researcher,
        max_parallel=parallel,
    ))

    synth = result.final_synthesis
    if synth:
        console.print(Panel(synth.content, title="Multi-Perspective Synthesis", border_style="green"))

    console.print(f"\n[dim]Output: {output_dir}[/dim]")


@app.command()
def show(
    path: str = typer.Argument(..., help="Path to graph.json checkpoint"),
) -> None:
    """Display a saved knowledge graph."""
    from deep_research.core.graph import KnowledgeGraph

    graph = KnowledgeGraph.load(Path(path))

    tree = Tree(f"[bold]Knowledge Graph[/bold] ({graph.size} nodes)")
    root = graph.root
    if root:
        _add_tree_node(tree, root, graph)

    console.print(tree)
    console.print(f"\n{graph.summary()}")


def _add_tree_node(tree_node, graph_node, graph) -> None:
    """Recursively add nodes to Rich tree."""
    from deep_research.core.node import NodeType

    style_map = {
        NodeType.QUESTION: "blue",
        NodeType.ANSWER: "green",
        NodeType.SYNTHESIS: "yellow",
        NodeType.BLIND_SPOT: "red",
        NodeType.PERSPECTIVE: "magenta",
        NodeType.GROUNDED_CLAIM: "cyan",
        NodeType.TENSION: "red",
        NodeType.INSIGHT: "bright_white",
    }
    style = style_map.get(graph_node.node_type, "white")
    label = f"[{style}][{graph_node.node_type.value}][/{style}] {graph_node.content[:100]}"
    child_tree = tree_node.add(label)

    for child in graph.get_children(graph_node.id):
        _add_tree_node(child_tree, child, graph)


if __name__ == "__main__":
    app()
