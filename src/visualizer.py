import sys
import os
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as et


def load_config(xml_path):
    """Загружает и парсит XML-файл конфигурации."""
    if not os.path.exists(xml_path):
        raise FileNotFoundError(f"Файл не найден: {xml_path}")
    try:
        tree = et.parse(xml_path)
        return tree.getroot()
    except et.ParseError as err:
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
    for char in req_str.strip():
        if char in " <>=!~;([":
            break
        parts.append(char)
    return "".join(parts)


def get_direct_deps(package, version, base_url):
    """Извлекает прямые зависимости заданной версии пакета из PyPI."""
    clean_url = base_url.rstrip("/")
    if clean_url == "https://pypi.org":
        clean_url = "https://pypi.org/pypi"
    url = f"{clean_url}/{package}/{version}/json"
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            info = data.get("info", {})
            reqs = info.get("requires_dist")
            if not reqs:
                return []
            deps = []
            for item in reqs:
                if "extra ==" in item or "extra==" in item:
                    continue
                name = parse_dep_name(item)
                if name and name not in deps:
                    deps.append(name)
            return deps
    except urllib.error.HTTPError as err:
        raise RuntimeError(f"Ошибка HTTP {err.code} по адресу {url}")
    except Exception as err:
        raise RuntimeError(f"Ошибка сети при запросе к PyPI: {err}")


def main():
    """Главная точка входа приложения."""
    xml_path = "config.xml"
    try:
        root = load_config(xml_path)
        cfg = validate_config(root)
        pkg = cfg["package_name"]
        ver = cfg["version"]
        print(f"Пакет: {pkg} (Версия: {ver})")
        deps = get_direct_deps(pkg, ver, cfg["repo_url"])
        print(f"Прямые зависимости: {deps}")
    except (FileNotFoundError, ValueError, KeyError, RuntimeError) as err:
        print(f"Ошибка: {err}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
