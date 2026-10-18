# Postprocessor review history — bounded static GO; runtime acceptance pending

Reviewer: `modification_review`, 16 October 2026. The initial AST prototype
passed seven syntax tests and changed three archived candidates in a static
screen. Those checks did not establish semantic preservation. Review found:

1. Chained, tuple and annotated assignments can invalidate a stored type fact.
2. Unsupported loops and later iterations can invalidate facts inherited from
   an outer block.
3. A syntactic comparison is not necessarily a secret comparison.
4. In MP-SPDZ 0.3.6, multiplication by Python zero can return Python zero.
   Thus `acc=sint(1); acc*=0; acc+=1` no longer has a secret accumulator.
   Removing a later comparison reveal can change a public return into a secret
   return and break an otherwise valid public print.

The reviewer located the zero simplification in `Compiler/types.py:254–258` and
the secret-print rejection in `Compiler/library.py:91,95`. No downloaded program
was executed on the host. The review then hit a usage limit; no final GO was
issued. These findings must be fixed and independently rechecked before the
modified implementation is accepted or merged.

Proposed correction: use actual compiler value types at the rewrite boundary,
preserving original behavior for public/unsupported values instead of relying on
the current approximate AST facts. Mixed fixed/integer comparisons additionally
need an explicit precision/range argument and runtime tests. No runtime repair or
improvement is claimed by the present prototype.

## Correction independently checked on 16 October 2026

The final correction uses a narrower static invariant rather than adding dynamic
type helpers. A candidate accumulator must be initialized with `sint(0)` or
`sint(1)`, and every store to the name must be that constructor or a supported
comparison-mask multiplication. All other stores, zero-folding arithmetic,
unsupported statement/control forms, dynamic calls, defaults and annotations
cause conservative fallback. The module supports only the target function,
specified Compiler.types imports and docstrings. This also closes a second-round
review defect: Python `match` captures are string fields, not `Name(Store)` nodes,
and can rebind an accumulator or shadow `sint` at module scope.

The earlier proposed opened-operand comparison rule is removed. In particular,
`lower_bound` remains unchanged: mixed fixed/integer comparisons require a separate
type/range argument. No claim is made to fix all detected reveal indicators.

`modification_review` independently ran 13 focused tests and scanned all 626
authentic final-stage candidates without executing them. Exactly two change:
`loop_test/count_distinct` candidate 1 and `loop_test/is_ascending` candidate 0.
The other 624, including the original parse failure, are byte-identical. The two
changed ASTs differ only at their one recorded reveal site and are idempotent.
Changed modules are re-rendered with `ast.unparse`; their formatting/comments are
not byte-preserved.

Reviewed extension SHA-256:
`8c93f4687569c7419b573b20b1349b2d67563a39ce50dba16fda38dd197d8aa2`.
The review gives **bounded GO for integration and restricted runtime evaluation**,
under standard MP-SPDZ primitives, valid numeric ranges and no custom operators,
reflection or dynamic rebinding. This is not runtime acceptance, a general privacy
guarantee, or merge readiness. Matched execution and independent evidence review
remain required.
