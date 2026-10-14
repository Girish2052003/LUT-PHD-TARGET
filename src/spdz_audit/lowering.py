"""Lower a restricted pure scalar language to straight-line arithmetic.

This is an independently written extension experiment, not SPDZCoder itself.
The baseline illustrates eager arithmetic predication from paper section 2.2.
The safe mode gives *inactive* sqrt/log/division operations valid arguments.
It does not make invalid active computations valid, prove arbitrary Python
secure, or prevent fixed-point overflow. See docs/report.md for the scope.
"""
from __future__ import annotations

import ast
import math
from typing import Callable


class UnsupportedSyntax(ValueError):
    """The source cannot be given the guarantees of our restricted frontend."""


def _parse(source: str) -> ast.FunctionDef:
    if not isinstance(source, str) or len(source) > 20_000:
        raise UnsupportedSyntax('Expected at most 20,000 characters of source')
    try:
        tree = ast.parse(source)
    except (SyntaxError, RecursionError) as error:
        raise UnsupportedSyntax('Source is not a supported Python program') from error
    if len(list(ast.walk(tree))) > 1_000:
        raise UnsupportedSyntax('Source exceeds the 1,000-node analysis limit')
    if len(tree.body) != 1 or not isinstance(tree.body[0], ast.FunctionDef):
        raise UnsupportedSyntax('Expected exactly one function, without module statements')
    fn = tree.body[0]
    args = fn.args
    if (fn.decorator_list or fn.returns or getattr(fn, 'type_params', [])
            or len(args.args) != 1 or args.posonlyargs or args.kwonlyargs
            or args.vararg or args.kwarg or args.defaults or args.kw_defaults
            or args.args[0].annotation):
        raise UnsupportedSyntax('Use one plain positional parameter, without annotations or decorators')
    for name in (fn.name, args.args[0].arg):
        if name.startswith('_') or name in {'math', 'sfix', 'mpc_math'}:
            raise UnsupportedSyntax(f'Reserved identifier: {name}')
    if fn.name == args.args[0].arg:
        raise UnsupportedSyntax('Function and parameter must have different names')
    return fn


class _Emitter:
    def __init__(self, fn: ast.FunctionDef, mode: str, backend: str):
        self.fn, self.mode, self.backend = fn, mode, backend
        self.parameter = fn.args.args[0].arg
        self.lines: list[str] = []

    def save(self, expression: str) -> str:
        name = f'_sc_{len(self.lines)}'
        self.lines.append(f'    {name} = {expression}')
        return name

    def masked_argument(self, value: str, active: str) -> str:
        # When active=1, preserve value. When active=0, substitute 1, which is
        # valid for sqrt, log and a denominator. Never reveal the secret bit.
        if self.mode == 'baseline' or active == '1':
            return value
        return self.save(f'({value}) * ({active}) + (1 - ({active}))')

    def combine_mask(self, outer: str, inner: str) -> str:
        # For bits, multiplication is logical AND. Both bits stay secret.
        return inner if outer == '1' else self.save(f'({outer}) * ({inner})')

    def scalar(self, node: ast.AST, active: str, predicate: bool = False) -> str:
        if isinstance(node, ast.Name) and node.id == self.parameter:
            return node.id
        if isinstance(node, ast.Constant):
            if type(node.value) not in (int, float):
                raise UnsupportedSyntax('Only finite numeric constants are allowed')
            try:
                finite = math.isfinite(node.value)
            except OverflowError:
                finite = False
            if not finite:
                raise UnsupportedSyntax('Constants must be finite and float-representable')
            return repr(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            arg = self.scalar(node.operand, active, predicate)
            return self.save(f'{"-" if isinstance(node.op, ast.USub) else "+"}({arg})')
        if isinstance(node, ast.BinOp) and type(node.op) in (ast.Add, ast.Sub, ast.Mult, ast.Div):
            if predicate and isinstance(node.op, ast.Div):
                raise UnsupportedSyntax('Predicates must not contain partial operations')
            left = self.scalar(node.left, active, predicate)
            right = self.scalar(node.right, active, predicate)
            if isinstance(node.op, ast.Div):
                right = self.masked_argument(right, active)
            op = {ast.Add: '+', ast.Sub: '-', ast.Mult: '*', ast.Div: '/'}[type(node.op)]
            return self.save(f'({left}) {op} ({right})')
        if isinstance(node, ast.Call) and not predicate:
            if (not isinstance(node.func, ast.Attribute)
                    or not isinstance(node.func.value, ast.Name)
                    or node.func.value.id != 'math'
                    or node.func.attr not in {'sqrt', 'log'}
                    or len(node.args) != 1 or node.keywords):
                raise UnsupportedSyntax('Only math.sqrt(x) and math.log(x) calls are supported')
            arg = self.scalar(node.args[0], active)
            arg = self.masked_argument(arg, active)
            if self.backend == 'mpspdz':
                expression = (f'mpc_math.sqrt(sfix({arg}))' if node.func.attr == 'sqrt'
                              else f'mpc_math.log_fx(sfix({arg}), math.e)')
            else:
                expression = f'math.{node.func.attr}({arg})'
            return self.save(expression)
        if isinstance(node, ast.IfExp) and not predicate:
            return self.branch(node.test, node.body, node.orelse, active)
        raise UnsupportedSyntax(f'Unsupported scalar expression: {type(node).__name__}')

    def condition(self, node: ast.AST) -> str:
        # Restrict conditions to genuine bits. Python's "x and y" can return an
        # arbitrary operand, so accepting arbitrary scalar operands would be wrong.
        if isinstance(node, ast.Compare):
            operators = {ast.Gt: '>', ast.GtE: '>=', ast.Lt: '<', ast.LtE: '<=', ast.Eq: '==', ast.NotEq: '!='}
            left = self.scalar(node.left, '1', predicate=True)
            bits = []
            for op, rhs in zip(node.ops, node.comparators):
                if type(op) not in operators:
                    raise UnsupportedSyntax('Unsupported comparison')
                right = self.scalar(rhs, '1', predicate=True)
                bits.append(self.save(f'({left}) {operators[type(op)]} ({right})'))
                left = right
            return bits[0] if len(bits) == 1 else self.save(' * '.join(f'({b})' for b in bits))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return self.save(f'1 - ({self.condition(node.operand)})')
        if isinstance(node, ast.BoolOp):
            result = self.condition(node.values[0])
            for value in node.values[1:]:
                other = self.condition(value)
                if isinstance(node.op, ast.And):
                    result = self.save(f'({result}) * ({other})')
                else:
                    result = self.save(f'({result}) + ({other}) - ({result}) * ({other})')
            return result
        raise UnsupportedSyntax('Use comparisons (optionally combined with and/or/not) as conditions')

    def branch(self, test: ast.AST, yes: ast.AST | list[ast.stmt], no: ast.AST | list[ast.stmt], active: str) -> str:
        bit = self.condition(test)
        complement = self.save(f'1 - ({bit})')
        yes_mask = self.combine_mask(active, bit)
        no_mask = self.combine_mask(active, complement)
        visit = self.block if isinstance(yes, list) else self.scalar
        yes_value = visit(yes, yes_mask)
        no_value = visit(no, no_mask)
        # Both values are evaluated; only their weighted result is selected.
        return self.save(f'({yes_value}) * ({bit}) + ({no_value}) * ({complement})')

    def block(self, statements: list[ast.stmt], active: str) -> str:
        if len(statements) != 1:
            raise UnsupportedSyntax('Each block must contain one return or one complete if/else')
        stmt = statements[0]
        if isinstance(stmt, ast.Return) and stmt.value is not None:
            return self.scalar(stmt.value, active)
        if isinstance(stmt, ast.If) and stmt.orelse:
            return self.branch(stmt.test, stmt.body, stmt.orelse, active)
        raise UnsupportedSyntax('Only returns and complete if/else blocks are supported')


def lower(source: str, mode: str = 'safe', backend: str = 'python') -> str:
    """Return generated source; reject everything outside the documented subset.

    Finite intermediates are a precondition. Masking cannot neutralize a NaN or
    infinity (zero times infinity is NaN); this compiler is not an overflow repair.
    """
    if mode not in {'safe', 'baseline'} or backend not in {'python', 'mpspdz'}:
        raise ValueError('mode must be safe/baseline; backend must be python/mpspdz')
    fn = _parse(source)
    emitter = _Emitter(fn, mode, backend)
    try:
        result = emitter.block(fn.body, '1')
    except RecursionError as error:
        raise UnsupportedSyntax('Source is too deeply nested') from error
    imports = 'import math\n'
    if backend == 'mpspdz':
        imports += 'from Compiler.types import sfix\nfrom Compiler import mpc_math\n'
    return (imports + f'\ndef {fn.name}({emitter.parameter}):\n'
            + '\n'.join(emitter.lines) + f'\n    return {result}\n')


def original_callable(source: str) -> Callable[[float], float]:
    """Execute only an AST-validated function under its ordinary Python semantics."""
    lower(source)  # Complete validation happens before any source is executed.
    fn = _parse(source)
    namespace = {'math': math, '__builtins__': {}}
    exec(compile(source, '<validated-original>', 'exec'), namespace)
    return namespace[fn.name]


def lowered_callable(source: str, mode: str = 'safe') -> Callable[[float], float]:
    """Run our Python backend for semantic experiments, not MPC simulation."""
    generated = lower(source, mode=mode)
    tree = ast.parse(generated)
    # Imports in generated code are ours. Supply math explicitly instead.
    tree.body = [stmt for stmt in tree.body if not isinstance(stmt, ast.Import)]
    namespace = {'math': math, '__builtins__': {}}
    exec(compile(tree, '<lowered>', 'exec'), namespace)
    return namespace[_parse(source).name]
