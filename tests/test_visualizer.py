import unittest
import xml.etree.ElementTree as ET
from src.visualizer import validate_config, build_graph_bfs_recursive


class TestVisualizerConfig(unittest.TestCase):

    def test_recursive_bfs_cyclic(self):
        """Проверяет устойчивость алгоритма BFS к циклическим графам."""
        graph = {}
        visited = set()
        # Имитируем граф с циклом A -> B -> A
        with unittest.mock.patch('src.visualizer.get_direct_deps') as mock_deps:
            mock_deps.side_effect = lambda pkg, url, tst: (
                ["B"] if pkg == "A" else ["A"]
            )
            build_graph_bfs_recursive(
                ["A"], "http://url", "filter_none", False, graph, visited
            )
        self.assertIn("A", graph)
        self.assertIn("B", graph)


if __name__ == "__main__":
    unittest.main()
