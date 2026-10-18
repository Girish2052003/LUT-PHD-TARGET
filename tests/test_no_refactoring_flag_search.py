"""Strict filename-grouping tests for the original author's saved RQ2 flag search."""
import unittest
from scripts.find_original_no_refactoring_evaluations import group_name, TARGET_FIRST, TARGET_UNION

class OriginalAblationGroupingTests(unittest.TestCase):
    def test_equivalent_split_suffix_delimiters(self):
        a=group_name("evaluation/baseline-evaluation/x-output-branch_test.txt")
        b=group_name("evaluation/baseline-evaluation/x-output_array_test.txt")
        self.assertEqual(a,("evaluation/baseline-evaluation/x-output","branch_test"))
        self.assertEqual(b,("evaluation/baseline-evaluation/x-output","array_test"))
    def test_not_a_source_code_path(self):
        self.assertIsNone(group_name("data/stage_2_SPDZ_output/experiment-1-array_test.jsonl"))
    def test_numpy_specific_category_takes_precedence(self):
        self.assertEqual(group_name("evaluation/stage_numpy_operation_test.txt"),
                         ("evaluation/stage","numpy_operation_test"))
    def test_exact_author_table_denominators(self):
        self.assertEqual((TARGET_FIRST,TARGET_UNION),(104,142))
if __name__=="__main__":
    unittest.main()
