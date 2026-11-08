import unittest
from src.visualizer import generate_d2_markup


class TestVisualizerConfig(unittest.TestCase):

    def test_d2_markup_generation(self):
        """Проверяет корректность генерации синтаксиса связей D2."""
        mock_graph = {
            "A": ["B"],
            "B": ["C"]
        }
        markup = generate_d2_markup(mock_graph)
        self.assertIn("A -> B", markup)
        self.assertIn("B -> C", markup)


if __name__ == "__main__":
    unittest.main()
