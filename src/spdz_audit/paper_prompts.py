"""Representative paper-grounded rule prompts (not the authors' full prompts).

Grounding: SPDZCoder v2 paper Table 1; supplementary Tables 9-12.
The appendix includes ellipses and only ONE of the ten complete high-level
rule instances. The reconstructed portions below are explicitly distinguished.
"""


def refactor_prompt(name: str, description: str) -> str:
    common = ("Write simple and explicit Python. Preserve the signature, "
              "the inputs and returned values. Do not reveal secret inputs. "
              "Apply this specific CFP refactoring rule: " + name +
              ". Goal: " + description)
    if name == "EliminateBreak":
        return (common +
                "\nThe published Table 9 illustrates replacing a break with "
                "a monotone flag and using oblivious masked updates. "
                "Never use break/continue in the output, but do not invent "
                "an unbounded loop or change the original return value.")
    if name == "ObliviousForm":
        return (common +
                "\nA secret-valued condition must not directly determine a "
                "Python if branch. Use secret arithmetic selection or "
                "MP-SPDZ-style if_else; handle inactive partial operations "
                "so an invalid inactive sqrt, log or division cannot fail.")
    if name == "RewriteWhileLoop":
        return (common +
                "\nOnly transform to a bounded loop when a correct public "
                "bound is provable. Otherwise return an explicit unsupported "
                "diagnostic rather than inventing a stopping bound.")
    return common


def generation_prompt(selected_rules: list[str]) -> str:
    examples = [
        "Map Python float variables to secret fixed-point sfix variables.",
        "Map Python boolean combinations of secret comparisons to bit_and / bit_or.",
        "Use mpc_math.sqrt(sfix(x)) for square roots.",
        "Use mpc_math.log_fx(sfix(x), math.e) for natural logarithms.",
        "Include from Compiler import mpc_math when needed.",
        "Only use actual MP-SPDZ APIs; do not leave placeholder calls."
    ]
    if "EliminateAdvancedArrayOperations" in selected_rules:
        examples.append("Replace unsupported NumPy array operators with explicit MP-SPDZ Array/Matrix operations.")
    if "ObliviousForm" in selected_rules:
        examples.append("Never branch publicly on secret data or reveal it.")
    return ("Translate Canonical Form Python to MP-SPDZ following the "
            "paper's low-level in-context demonstration approach. "
            "Selected examples: " + "\n".join(examples))


def reflection_prompt() -> str:
    return (
        "Review MP-SPDZ code with the concrete API error patterns in "
        "supplementary Table 11. Incorrect mpc_math.exp(x) should be "
        "mpc_math.pow_fx(math.e, x). Incorrect mpc_math.log(x) should be "
        "mpc_math.log_fx(x, math.e). Replace mpc_math.sqrt_fx(x) by "
        "mpc_math.sqrt(sfix(x)). Ensure the Compiler.types and "
        "Compiler.mpc_math imports exist. Replace secret-dependent "
        "Python ternary expressions with condition.if_else(a,b). "
        "Remove placeholder/example-usage text and return the full code."
    )


def repair_prompt(kind: str) -> str:
    if kind == "compile_runtime":
        return ("Read compiler/runtime traceback and repair the MP-SPDZ "
                "program as in supplementary Table 12. Preserve intended "
                "Python semantics and return the complete corrected code.")
    return ("Identify incorrect functionality or extra secret disclosures, "
            "compare with Canonical Form Python, and repair the MP-SPDZ "
            "program as in supplementary Table 12. Return complete code.")
