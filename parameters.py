"""
PA 7: The Parameter Simulator -- starter.

Complete bind_parameters, commit_value_result, and Closure below.
Cell, evaluate(), and FunctionDecl are already provided -- do not
modify them. See the assignment, Part B, for the
full requirements.

Value-result binding has two steps: bind_parameters runs at call time
and records each caller destination; commit_value_result runs after
the simulated body and copies the final local values back in parameter
order. The handout specifies both steps.

Design note 2: variables are stored as Cell objects (a mutable box),
not raw values, specifically so reference-mode parameters can share
the exact same storage as the caller's variable -- see Part A,
Questions 1-2, for why "bind directly to the caller's slot" requires
this instead of just copying a plain value.
"""

from typing import Any, List, Tuple

from parser import BinOp, Number, Variable
from symtable import Environment


class Cell:
    """Given: a mutable box. Two names that share the SAME Cell are aliased."""

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


class FunctionDecl:
    """Given: a minimal function declaration -- params and a single expr body."""

    __slots__ = ("params", "body")

    def __init__(self, params: List[str], body) -> None:
        self.params = params
        self.body = body


def evaluate(node, env: Environment):
    """Given: evaluate a PA3 expression AST node against `env` (Cells are transparently dereferenced)."""
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Variable):
        val = env.resolve(node.name)
        return val.value if isinstance(val, Cell) else val
    if isinstance(node, BinOp):
        if node.op == "neg":
            return -evaluate(node.left, env)
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        return {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b}[node.op](left, right)
    raise ValueError(f"cannot evaluate node: {node!r}")


def assign_through(env: Environment, name: str, value: Any) -> None:
    """Given: write `value` into whatever Cell `name` resolves to (mutates in place, does not rebind)."""
    cell = env.resolve(name)
    if not isinstance(cell, Cell):
        raise TypeError(f"'{name}' is not bound to a Cell -- did you forget to wrap it?")
    cell.value = value


VALID_MODES = ("value", "reference", "value-result")


def _caller_cell(node, caller_env: Environment, param: str, mode: str) -> Cell:
    """Reference and value-result arguments need a writable caller variable."""
    if not isinstance(node, Variable):
        raise TypeError(f"{mode} parameter '{param}' needs a caller variable, got {node!r}")
    cell = caller_env.resolve(node.name)
    if not isinstance(cell, Cell):
        raise TypeError(f"caller variable '{node.name}' is not bound to a Cell")
    return cell


def bind_parameters(param_specs: List[Tuple[str, str]], arg_nodes: list, caller_env: Environment, callee_record) -> None:
    """
    Populate callee_record.locals_env according to each parameter's
    mode ("value", "reference", or "value-result"). Value-result
    destinations are recorded on callee_record.pending_writeback,
    in parameter declaration order, for commit_value_result.
    """
    if len(param_specs) != len(arg_nodes):
        raise TypeError(f"expected {len(param_specs)} argument(s), got {len(arg_nodes)}")

    env = callee_record.locals_env
    pending: List[Tuple[str, Cell]] = []

    for (name, mode), node in zip(param_specs, arg_nodes):
        if mode == "value":            
            cell = Cell(evaluate(node, caller_env))
        elif mode == "reference":
            cell = _caller_cell(node, caller_env, name, mode)
        elif mode == "value-result":
            dest = _caller_cell(node, caller_env, name, mode)
            cell = Cell(dest.value)
            pending.append((name, dest))
        else:
            raise ValueError(f"unknown parameter mode {mode!r}; expected one of {VALID_MODES}")
        env.define(name, cell)
        callee_record.parameters[name] = mode

    callee_record.pending_writeback = pending


def commit_value_result(callee_record, caller_env: Environment) -> None:
    """
    Copy each value-result parameter's FINAL local value back into the
    caller Cell recorded at call time, left to right in parameter order.
    Call only after the callee body has finished.
    """
    for name, dest in getattr(callee_record, "pending_writeback", []):
        dest.value = callee_record.locals_env.resolve(name).value
    callee_record.pending_writeback = []


class Closure:
    def __init__(self, declaration: FunctionDecl, defining_env: Environment) -> None:
        self.declaration = declaration
        self.defining_env = defining_env

    def call(self, args: list, caller_env: Environment):
        """
        Create the callee Environment as a child of self.defining_env
        (NOT caller_env), bind each parameter to a fresh Cell holding the
        already-evaluated argument, then evaluate the body there.
        """
        params = self.declaration.params
        if len(args) != len(params):
            raise TypeError(f"expected {len(params)} argument(s), got {len(args)}")
        call_env = Environment(parent=self.defining_env)
        for name, value in zip(params, args):
            call_env.define(name, Cell(value))
        return evaluate(self.declaration.body, call_env)