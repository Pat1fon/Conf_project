import sys
import os
import xml.etree.ElementTree as ET


def load_config(xml_path):
    """Загружает и парсит XML-файл конфигурации."""
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Файл не найден: {xml_path}")
    try:
        tree = ET.parse(xml_path)
        return tree.getroot()
    except ET.ParseError as err:
        raise ValueError(f"Ошибка XML: {err}")


def validate_config(root):
    """Проверяет наличие всех обязательных тегов в XML."""
    required_tags = [
        "package_name", "repo_url", "test_mode",
        "version", "filter_substring"
    ]
    config_data = {}
    for tag in required_tags:
        element = root.find(tag)
        if element is None or element.text is None:
            raise KeyError(f"Отсутствует параметр: {tag}")
        config_data[tag] = element.text.strip()
    return config_data


def print_config(config_data):
    """Выводит параметры в формате ключ-значение."""
    print("=== CONFIGURATION PARAMETERS ===")
    for key, value in config_data.items():
        print(f"{key}: {value}")
    print("================================")


def main():
    """Главная точка входа приложения."""
    xml_path = "config.xml"
    try:
        root = load_config(xml_path)
        config_data = validate_config(root)
        print_config(config_data)
    except (FileNotFoundError, ValueError, KeyError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
