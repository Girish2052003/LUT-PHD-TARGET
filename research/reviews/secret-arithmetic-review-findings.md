# Initial postprocessor review — unresolved, not accepted

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
