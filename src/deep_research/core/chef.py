"""MasterChef - orchestrates strategies on knowledge graphs."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

from deep_research.core.node import Node, NodeType, EpistemicStatus
from deep_research.core.graph import KnowledgeGraph
from deep_research.core.operation import Operation
from deep_research.core.strategy import Strategy, StrategyStep, STRATEGIES

logger = logging.getLogger(__name__)


class CookResult:
    """Result of a MasterChef research run."""

    def __init__(self, graph: KnowledgeGraph, output_dir: Path):
        self.graph = graph
        self.output_dir = output_dir

    @property
    def final_synthesis(self) -> Node | None:
        syntheses = self.graph.nodes_by_type(NodeType.SYNTHESIS)
        if not syntheses:
            return None
        # Return the one at lowest depth (most aggregated)
        return min(syntheses, key=lambda n: n.depth)

    @property
    def all_answers(self) -> list[Node]:
        return self.graph.nodes_by_type(NodeType.ANSWER)

    @property
    def blind_spots(self) -> list[Node]:
        return self.graph.nodes_by_type(NodeType.BLIND_SPOT)


class MasterChef:
    """Executes research strategies on knowledge graphs with parallel agents."""

    def __init__(
        self,
        output_dir: Path | None = None,
        max_parallel: int = 10,
        max_depth: int = 0,
        operations: dict[str, Operation] | None = None,
    ):
        self.output_dir = output_dir or Path("reports/default")
        self.max_parallel = max_parallel
        self.max_depth = max_depth
        self._operations: dict[str, Operation] = operations or {}
        self._semaphore = asyncio.Semaphore(max_parallel)

    def register_operation(self, op: Operation) -> None:
        self._operations[op.name] = op

    async def cook(
        self,
        question: str,
        strategy: str | Strategy,
        context: dict[str, Any] | None = None,
    ) -> CookResult:
        """Execute a full research run.

        Args:
            question: The research question.
            strategy: Strategy name or Strategy object.
            context: Additional context (model, web_search, etc.)

        Returns:
            CookResult with the knowledge graph and output directory.
        """
        if isinstance(strategy, str):
            strategy = STRATEGIES[strategy]

        ctx = {
            "model": "haiku",
            "researcher_model": "haiku",
            "merger_model": None,
            "leaf_models": None,
            "web_search": False,
            "output_dir": self.output_dir,
            **(context or {}),
        }

        self.output_dir.mkdir(parents=True, exist_ok=True)

        graph = KnowledgeGraph()
        root = Node(
            node_type=NodeType.QUESTION,
            content=question,
            depth=0,
        )
        graph.add_node(root)

        logger.info(f"Starting research: {question}")
        logger.info(f"Strategy: {strategy.name}, Max depth: {self.max_depth}")

        # Phase 1: Recursive decomposition and answering
        await self._process_level(graph, strategy, ctx, current_depth=0)

        # Phase 2: Bottom-up synthesis
        await self._synthesize_up(graph, strategy, ctx)

        # Save checkpoint
        graph.save(self.output_dir / "graph.json")

        # Write final report
        result = CookResult(graph, self.output_dir)
        await self._write_report(result, strategy)

        return result

    async def _process_level(
        self,
        graph: KnowledgeGraph,
        strategy: Strategy,
        ctx: dict[str, Any],
        current_depth: int,
    ) -> None:
        """Process all nodes at the current depth level."""
        questions = [
            n for n in graph.unanswered_questions()
            if n.depth == current_depth
        ]

        if not questions:
            return

        # Check depth limit
        at_max_depth = self.max_depth > 0 and current_depth >= self.max_depth

        if at_max_depth:
            # At max depth: just answer, don't decompose further
            answer_steps = [
                s for s in strategy.steps if s.operation == "answer"
            ]
            if answer_steps:
                tasks = [
                    self._run_operation(answer_steps[0], q, graph, ctx)
                    for q in questions
                ]
                await asyncio.gather(*tasks)
                for q in questions:
                    q.status = EpistemicStatus.EXPLORED
        else:
            # Decompose questions into sub-questions
            decompose_steps = [
                s for s in strategy.steps if s.operation == "decompose"
            ]
            if decompose_steps:
                tasks = [
                    self._run_operation(decompose_steps[0], q, graph, ctx)
                    for q in questions
                ]
                await asyncio.gather(*tasks)
                for q in questions:
                    q.status = EpistemicStatus.EXPLORED

            # Detect blind spots if strategy calls for it
            detect_steps = [
                s for s in strategy.steps
                if s.operation == "detect" and s.applies_to == NodeType.QUESTION
            ]
            if detect_steps:
                tasks = [
                    self._run_operation(detect_steps[0], q, graph, ctx)
                    for q in questions
                ]
                await asyncio.gather(*tasks)

            # Recurse to next level
            await self._process_level(graph, strategy, ctx, current_depth + 1)

        # Ground answers if strategy calls for it
        ground_steps = [s for s in strategy.steps if s.operation == "ground"]
        if ground_steps:
            answers = [
                n for n in graph.nodes_by_type(NodeType.ANSWER)
                if n.depth == current_depth + 1
                or (at_max_depth and n.depth == current_depth)
            ]
            if answers:
                tasks = [
                    self._run_operation(ground_steps[0], a, graph, ctx)
                    for a in answers
                ]
                await asyncio.gather(*tasks)

    async def _synthesize_up(
        self,
        graph: KnowledgeGraph,
        strategy: Strategy,
        ctx: dict[str, Any],
    ) -> None:
        """Bottom-up synthesis from leaves to root."""
        synth_steps = [s for s in strategy.steps if s.operation == "synthesize"]
        if not synth_steps:
            return

        max_d = graph.max_depth()
        for depth in range(max_d, -1, -1):
            nodes_at_depth = graph.nodes_at_depth(depth)
            parents_to_synth = set()
            for n in nodes_at_depth:
                if n.node_type in (NodeType.ANSWER, NodeType.GROUNDED_CLAIM):
                    if n.parent_id:
                        parents_to_synth.add(n.parent_id)

            if parents_to_synth:
                parent_nodes = [
                    graph.get_node(pid) for pid in parents_to_synth
                    if graph.get_node(pid) is not None
                ]
                tasks = [
                    self._run_operation(synth_steps[0], p, graph, ctx)
                    for p in parent_nodes
                    if p is not None
                ]
                if tasks:
                    await asyncio.gather(*tasks)

        # Final root synthesis
        root = graph.root
        if root:
            all_syntheses = graph.nodes_by_type(NodeType.SYNTHESIS)
            if all_syntheses:
                await self._run_operation(synth_steps[0], root, graph, ctx)

    async def _run_operation(
        self,
        step: StrategyStep,
        node: Node,
        graph: KnowledgeGraph,
        ctx: dict[str, Any],
    ) -> None:
        """Run a single operation with concurrency control."""
        op = self._operations.get(step.operation)
        if not op:
            logger.warning(f"Operation '{step.operation}' not registered, skipping")
            return

        merged_ctx = {**ctx, **step.config}

        async with self._semaphore:
            try:
                new_nodes = await op.execute(node, graph, merged_ctx)
                for new_node in new_nodes:
                    graph.add_node(new_node)
                logger.info(
                    f"[{step.operation}] {node.content[:60]}... → {len(new_nodes)} nodes"
                )
            except Exception as e:
                logger.error(f"Operation {step.operation} failed on {node.id}: {e}")

    async def _write_report(self, result: CookResult, strategy: Strategy) -> None:
        """Write the final synthesis report."""
        synth = result.final_synthesis
        if not synth:
            return

        report_path = self.output_dir / "SYNTHESIS.md"
        lines = [
            f"# Research Synthesis",
            f"",
            f"**Strategy**: {strategy.name}",
            f"**Nodes explored**: {result.graph.size}",
            f"**Max depth**: {result.graph.max_depth()}",
            f"",
            f"---",
            f"",
            synth.content,
        ]

        blind_spots = result.blind_spots
        if blind_spots:
            lines.extend([
                "",
                "---",
                "",
                "## Blind Spots & Tensions",
                "",
            ])
            for bs in blind_spots:
                lines.append(f"- {bs.content}")

        lines.extend([
            "",
            "---",
            "",
            f"## Graph Summary",
            "",
        ])
        summary = result.graph.summary()
        for key, val in summary.items():
            lines.append(f"- **{key}**: {val}")

        report_path.write_text("\n".join(lines))
        logger.info(f"Report written to {report_path}")
