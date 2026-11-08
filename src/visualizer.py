import sys
import os
import json
import urllib.request
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


def parse_dep_name(req_str):
    """Извлекает чистое имя пакета из строки зависимости."""
    parts = []
    for char in req_str:
        if char in " <>=!~;(":
            break
        parts.append(char)
    return "".join(parts)


def get_direct_deps(package, base_url):
    """Извлекает прямые зависимости пакета из API PyPI."""
    url = f"{base_url}/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            info = data.get("info", {})
            reqs = info.get("requires_dist")
            if reqs is None:
                return []
            return [parse_dep_name(r) for r in reqs if "extra ==" not in r]
    except Exception:
        return []


def main():
    """Главная точка входа приложения."""
    xml_path = "config.xml"
    try:
        root = load_config(xml_path)
        cfg = validate_config(root)
        print(f"Пакет: {cfg['package_name']} (Версия: {cfg['version']})")
        deps = get_direct_deps(cfg["package_name"], cfg["repo_url"])
        print(f"Прямые зависимости: {deps}")
    except (FileNotFoundError, ValueError, KeyError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
