"""Remove two redundant-opening patterns in MP-SPDZ arithmetic.

This is a scoped transformation, not a general privacy validator. It assumes
standard MP-SPDZ scalar/Array operations and valid numeric ranges. Arbitrary
Python objects, overloaded operators and secret-dependent public control are
outside its contract. The original caller remains responsible for authorized
outputs. Unsupported code is returned byte-for-byte unchanged.
"""
import ast
from collections import Counter


def _opening(node):
    return (isinstance(node, ast.Call) and not node.args and not node.keywords
            and isinstance(node.func, ast.Attribute) and node.func.attr == 'reveal')


def _plain(node):
    """Only side-effect-free numeric expressions in the stated MP-SPDZ domain."""
    if isinstance(node, ast.Name):
        return True
    if isinstance(node, ast.Constant):
        return type(node.value) in (int, float)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return _plain(node.operand)
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
        return _plain(node.left) and _plain(node.right)
    if isinstance(node, ast.Subscript):
        return isinstance(node.value, ast.Name) and _plain(node.slice)
    return False


def _comparison(node):
    return (isinstance(node, ast.Compare) and len(node.ops) == 1
            and isinstance(node.ops[0], (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE))
            and _plain(node.left) and _plain(node.comparators[0]))


def _constructor(node):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in ('sint', 'sfix') and len(node.args) == 1
            and not node.keywords and isinstance(node.args[0], ast.Constant)
            and type(node.args[0].value) in (int, float))


def _mask_openings(node, facts):
    """Recognize a comparison bit, optionally complemented as 1-bit."""
    if _opening(node):
        value = node.func.value
        if _comparison(value) or (isinstance(value, ast.Name) and facts.get(value.id) == 'comparison'):
            return [node]
    if (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Sub)
            and isinstance(node.left, ast.Constant) and node.left.value == 1):
        return _mask_openings(node.right, facts)
    return []


def preserve_secret_arithmetic(source, function_name):
    """Return (source, rewrite records), with no source execution or model calls.

    Rule 1 keeps a comparison bit secret when multiplied into a known secret
    accumulator. Rule 2 keeps a pair of comparison operands secret when the
    resulting bit is used exclusively in a product with another comparison bit.
    Neither rule changes public indices, loop bounds or explicit returned opens.
    """
    try:
        tree = ast.parse(source)
    except (SyntaxError, ValueError, TypeError):
        return source, []
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function_name]
    if len(functions) != 1:
        return source, []
    function = functions[0]
    # Keep the analysis deliberately small: public counted loops and assignments.
    forbidden = (ast.If, ast.While, ast.Try, ast.With, ast.AsyncFunctionDef,
                 ast.Lambda, ast.ClassDef, ast.Global, ast.Nonlocal, ast.BoolOp,
                 ast.IfExp, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp,
                 ast.NamedExpr, ast.Yield, ast.YieldFrom, ast.Await, ast.Delete)
    if function.decorator_list or any(isinstance(n, forbidden) for n in ast.walk(function)):
        return source, []
    if sum(isinstance(n, ast.FunctionDef) for n in ast.walk(function)) != 1:
        return source, []
    protected = {'sint', 'sfix', 'range', 'len'}
    if (any(isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store) and n.id in protected for n in ast.walk(tree))
            or any(a.arg in protected for a in function.args.args)
            or any(isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in protected for n in tree.body)):
        return source, []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            return source, []
        if isinstance(node, ast.ImportFrom) and (node.module != 'Compiler.types'
                or any(a.asname or a.name == '*' for a in node.names)):
            return source, []
    # Unique assignments avoid aliases whose meaning changes elsewhere in a loop.
    stores = Counter(n.id for n in ast.walk(function) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store))
    comparisons = {n.targets[0].id for n in ast.walk(function)
                   if isinstance(n, ast.Assign) and len(n.targets) == 1
                   and isinstance(n.targets[0], ast.Name) and _comparison(n.value)
                   and stores[n.targets[0].id] == 1}
    parents = {child: parent for parent in ast.walk(function) for child in ast.iter_child_nodes(parent)}
    replacements, events = {}, []

    def record(nodes, rule):
        for node in nodes:
            if node not in replacements:
                replacements[node] = node.func.value
                events.append({'rule': rule, 'line': node.lineno, 'column': node.col_offset,
                               'original': ast.unparse(node), 'replacement': ast.unparse(node.func.value)})

    def selector_only(name):
        uses = [n for n in ast.walk(function) if isinstance(n, ast.Name)
                and isinstance(n.ctx, ast.Load) and n.id == name]
        if not uses or stores[name] != 1:
            return False
        for use in uses:
            parent = parents[use]
            if not isinstance(parent, ast.BinOp) or not isinstance(parent.op, ast.Mult):
                return False
            other = parent.right if parent.left is use else parent.left
            if not isinstance(other, ast.Name) or other.id not in comparisons:
                return False
        return True

    def block(statements, facts):
        for stmt in statements:
            if isinstance(stmt, ast.For):
                if (not isinstance(stmt.target, ast.Name) or not isinstance(stmt.iter, ast.Call)
                        or not isinstance(stmt.iter.func, ast.Name) or stmt.iter.func.id != 'range'
                        or stmt.orelse):
                    continue
                inner = dict(facts)
                inner.pop(stmt.target.id, None)
                block(stmt.body, inner)
                # A loop may execute zero times: don't export new local facts.
                for n in ast.walk(stmt):
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                        facts.pop(n.id, None)
            elif isinstance(stmt, ast.AugAssign) and isinstance(stmt.target, ast.Name):
                name = stmt.target.id
                if facts.get(name) == 'secret' and isinstance(stmt.op, ast.Mult):
                    record(_mask_openings(stmt.value, facts), 'secret_product')
                # A secret primitive remains secret under addition/multiplication.
                if not isinstance(stmt.op, (ast.Mult, ast.Add, ast.Sub)):
                    facts.pop(name, None)
            elif isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and isinstance(stmt.targets[0], ast.Name):
                name, value = stmt.targets[0].id, stmt.value
                preserved = False
                if (facts.get(name) == 'secret' and isinstance(value, ast.BinOp)
                        and isinstance(value.op, ast.Mult) and isinstance(value.left, ast.Name)
                        and value.left.id == name):
                    record(_mask_openings(value.right, facts), 'secret_product')
                    preserved = True
                if (isinstance(value, ast.Compare) and len(value.ops) == 1
                        and isinstance(value.ops[0], (ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE))
                        and _opening(value.left) and _opening(value.comparators[0])
                        and _plain(value.left.func.value) and _plain(value.comparators[0].func.value)
                        and selector_only(name)):
                    record([value.left, value.comparators[0]], 'secret_selector')
                facts.pop(name, None)
                if _constructor(value) or preserved:
                    facts[name] = 'secret'
                elif _comparison(value):
                    facts[name] = 'comparison'
    block(function.body, {})
    if not events:
        return source, []

    class Replace(ast.NodeTransformer):
        def visit_Call(self, node):
            if node in replacements:
                return ast.copy_location(replacements[node], node)
            return self.generic_visit(node)
    changed = ast.unparse(ast.fix_missing_locations(Replace().visit(tree))) + '\n'
    return changed, sorted(events, key=lambda e: (e['line'], e['column']))
