import unittest
from src.visualizer import find_reverse_deps


class TestVisualizerConfig(unittest.TestCase):

    def test_reverse_dependencies(self):
        """Проверяет корректность расчета входящих (обратных) связей."""
        mock_graph = {
            "A": ["B", "C"],
            "B": ["C"],
            "C": []
        }
        revs = find_reverse_deps(mock_graph, "C")
        self.assertIn("A", revs)
        self.assertIn("B", revs)


if __name__ == "__main__":
    unittest.main()
