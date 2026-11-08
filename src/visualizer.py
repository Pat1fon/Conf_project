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


def get_direct_deps(package, base_url, is_test=False):
    """Извлекает прямые зависимости пакета (из сети или из тест-файла)."""
    if is_test:
        if os.path.exists("test_graph.json"):
            with open("test_graph.json", "r", encoding="utf-8") as f:
                mock_db = json.load(f)
                return mock_db.get(package, [])
        return []
    url = f"{base_url}/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
            reqs = data.get("info", {}).get("requires_dist")
            if reqs is None:
                return []
            return [parse_dep_name(r) for r in reqs if "extra ==" not in r]
    except Exception:
        return []


def build_graph_bfs_recursive(queue, base_url, f_sub, is_test, graph, visited):
    """Рекурсивно строит граф транзитивных зависимостей методом BFS."""
    if not queue:
        return graph
    next_queue = []
    for node in queue:
        if node in visited:
            continue
        visited.add(node)
        raw_deps = get_direct_deps(node, base_url, is_test)
        filtered_deps = [d for d in raw_deps if f_sub not in d]
        graph[node] = filtered_deps
        for dep in filtered_deps:
            if dep not in visited:
                next_queue.append(dep)
    return build_graph_bfs_recursive(
        next_queue, base_url, f_sub, is_test, graph, visited
    )


def generate_d2_markup(graph):
    """Генерирует текстовое представление графа на языке D2."""
    lines = []
    for parent, children in graph.items():
        for child in children:
            lines.append(f"{parent} -> {child}")
    return "\n".join(lines)


def main():
    """Главная точка входа приложения."""
    xml_path = "config.xml"
    try:
        root = load_config(xml_path)
        cfg = validate_config(root)
        is_test = cfg["test_mode"].lower() == "true"
        graph = {}
        visited = set()
        build_graph_bfs_recursive(
            [cfg["package_name"]], cfg["repo_url"],
            cfg["filter_substring"], is_test, graph, visited
        )
        print("СГЕНЕРИРОВАННЫЙ ГРАФ D2")
        print(generate_d2_markup(graph))
    except (FileNotFoundError, ValueError, KeyError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
