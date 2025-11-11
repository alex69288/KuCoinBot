import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(ROOT, 'webapp', 'static')


def test_icons_svg_exists():
    path = os.path.join(STATIC_DIR, 'icons.svg')
    assert os.path.exists(path), f"icons.svg не найден: {path}"
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert '<symbol id="icon-robot"' in content, 'В icons.svg не найден символ icon-robot'


def test_index_has_setup_function():
    index_path = os.path.join(STATIC_DIR, 'index.html')
    assert os.path.exists(index_path), f"index.html не найден: {index_path}"
    with open(index_path, 'r', encoding='utf-8') as f:
        html = f.read()
    assert 'function setupSvgIcons()' in html, 'В index.html не найдена функция setupSvgIcons()'
    assert '/static/icons.svg' in html, 'В index.html нет ссылки на /static/icons.svg'


if __name__ == '__main__':
    # Простой запуск без pytest
    test_icons_svg_exists()
    test_index_has_setup_function()
    print('OK: sprites configured')
