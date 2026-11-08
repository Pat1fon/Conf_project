import unittest
import xml.etree.ElementTree as ET
from src.visualizer import validate_config, parse_dep_name


class TestVisualizerConfig(unittest.TestCase):

    def create_mock_xml(self, p_name, url, mode, ver, fltr):
        """Вспомогательный метод для генерации XML-узла."""
        root = ET.Element("config")
        ET.SubElement(root, "package_name").text = p_name
        ET.SubElement(root, "repo_url").text = url
        ET.SubElement(root, "test_mode").text = mode
        ET.SubElement(root, "version").text = ver
        ET.SubElement(root, "filter_substring").text = fltr
        return root

    def test_valid_config(self):
        """Проверяет успешную валидацию корректного XML."""
        root = self.create_mock_xml(
            "pip", "http://test.org", "true", "1.0", "none"
        )
        res = validate_config(root)
        self.assertEqual(res["package_name"], "pip")

    def test_missing_parameter(self):
        """Проверяет генерацию ошибки при отсутствии тега."""
        root = ET.Element("config")
        ET.SubElement(root, "package_name").text = "test"
        with self.assertRaises(KeyError):
            validate_config(root)

    def test_dep_parser(self):
        """Проверяет извлечение чистого имени из строки требований pip."""
        self.assertEqual(parse_dep_name("requests>=2.0"), "requests")
        self.assertEqual(parse_dep_name("click (==8.0)"), "click")


if __name__ == "__main__":
    unittest.main()
