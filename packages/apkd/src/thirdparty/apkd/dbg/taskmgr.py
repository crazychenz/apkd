from __future__ import annotations

import logging
log = logging.getLogger(__name__)

from dataclasses import dataclass, field
from graphlib import TopologicalSorter, CycleError
from typing import Callable, Any

@dataclass
class Task:
    name: str
    func: Callable
    provides: set[str]
    depends_on: set[str]


class _TaskRegistry:
    def __init__(self):
        self._tasks: dict[str, Task] = {}
        self._provider_index: dict[str, str] = {}  # provided-name -> task name

    def register(self, name: str | None = None, provides: list[str] | None = None,
                 depends_on: list[str] | None = None):
        """
        Decorator to register a function as a task node.

        - `name` defaults to the function's own name.
        - `provides` are labels other tasks can depend on (defaults to [name]).
        - `depends_on` are labels (not necessarily task names) this task needs
          to have run first.
        """
        def decorator(func):
            task_name = name or func.__name__
            provided = set(provides) if provides else {task_name}
            deps = set(depends_on) if depends_on else set()

            task = Task(name=task_name, func=func, provides=provided, depends_on=deps)
            self._tasks[task_name] = task

            for label in provided:
                if label in self._provider_index and self._provider_index[label] != task_name:
                    raise ValueError(
                        f"'{label}' is provided by both "
                        f"'{self._provider_index[label]}' and '{task_name}'"
                    )
                self._provider_index[label] = task_name

            return func
        return decorator

    def _build_graph(self) -> dict[str, set[str]]:
        graph: dict[str, set[str]] = {}
        for task_name, task in self._tasks.items():
            resolved_deps = set()
            for dep_label in task.depends_on:
                if dep_label not in self._provider_index:
                    raise ValueError(
                        f"Task '{task_name}' depends on '{dep_label}', "
                        f"but no registered task provides it"
                    )
                resolved_deps.add(self._provider_index[dep_label])
            graph[task_name] = resolved_deps
        return graph

    def execution_order(self) -> list[str]:
        graph = self._build_graph()
        try:
            ts = TopologicalSorter(graph)
            return list(ts.static_order())
        except CycleError as e:
            raise ValueError(f"Circular dependency detected: {e.args[1]}") from e

    def run(self, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Executes all registered tasks in dependency order. Each task function
        receives the shared `context` dict and can read/write into it freely
        -- this is how "results" flow between tasks without you having to
        wire up individual return values manually.
        """
        context = context if context is not None else {}
        for task_name in self.execution_order():
            task = self._tasks[task_name]
            print(f"Running: {task_name}")
            task.func(context)
        return context

    def run_one(self, target: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Executes only what's needed to satisfy one specific task (and its
        transitive dependencies), rather than the entire registered set.

        `target` can be either a task's own name, or one of the labels it
        `provides` -- both are resolved to the owning task.
        """
        context = context if context is not None else {}

        if target in self._tasks:
            task_name = target
        elif target in self._provider_index:
            task_name = self._provider_index[target]
        else:
            raise ValueError(
                f"'{target}' is neither a registered task name nor a provided label"
            )

        graph = self._build_graph()
        needed = self._transitive_deps(task_name, graph) | {task_name}

        subgraph = {n: (graph.get(n, set()) & needed) for n in needed}

        try:
            ts = TopologicalSorter(subgraph)
            order = list(ts.static_order())
        except CycleError as e:
            raise ValueError(f"Circular dependency detected: {e.args[1]}") from e

        for n in order:
            task = self._tasks[n]
            print(f"Running: {n}")
            task.func(context)
        return context

    def _transitive_deps(self, task_name: str, graph: dict[str, set[str]]) -> set[str]:
        seen = set()
        stack = list(graph.get(task_name, set()))
        while stack:
            dep = stack.pop()
            if dep not in seen:
                seen.add(dep)
                stack.extend(graph.get(dep, set()))
        return seen

TaskRegistry = _TaskRegistry()








# registry = TaskRegistry()

# @registry.register(provides=["sdk_installed"])
# def install_sdk(ctx):
#     ctx["sdk_path"] = "/opt/android-sdk"

# @registry.register(depends_on=["sdk_installed"], provides=["avd_created"])
# def create_avd(ctx):
#     ctx["avd_name"] = "Pixel_7_API_33"

# @registry.register(depends_on=["avd_created"], provides=["emulator_running"])
# def start_emulator(ctx):
#     print(f"Booting {ctx['avd_name']} using SDK at {ctx['sdk_path']}")

# @registry.register(depends_on=["emulator_running"])
# def install_apk(ctx):
#     print("Installing APK...")

# @registry.register(depends_on=["emulator_running"])
# def start_logcat(ctx):
#     print("Tailing logcat...")

# registry.run()