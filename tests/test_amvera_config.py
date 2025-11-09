"""
Тест для проверки конфигурации Amvera
Проверяет, что все необходимые файлы существуют и имеют правильный формат
"""
import os
import sys
import yaml

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_amvera_yml_exists():
    """Проверяет, что файл amvera.yml существует"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    amvera_yml_path = os.path.join(project_root, 'amvera.yml')
    
    assert os.path.exists(amvera_yml_path), "❌ Файл amvera.yml не найден"
    print("✅ Файл amvera.yml существует")
    return amvera_yml_path

def test_amvera_yml_format():
    """Проверяет формат amvera.yml"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    amvera_yml_path = os.path.join(project_root, 'amvera.yml')
    
    with open(amvera_yml_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Проверяем секцию meta
    assert 'meta' in config, "❌ Секция 'meta' не найдена"
    assert 'environment' in config['meta'], "❌ Поле 'environment' не найдено в секции meta"
    assert config['meta']['environment'] == 'python', "❌ environment должен быть 'python'"
    assert 'toolchain' in config['meta'], "❌ Поле 'toolchain' не найдено"
    assert config['meta']['toolchain']['name'] == 'pip', "❌ toolchain name должен быть 'pip'"
    
    print("✅ Секция meta правильно настроена")
    
    # Проверяем секцию build
    assert 'build' in config, "❌ Секция 'build' не найдена"
    assert 'requirementsPath' in config['build'], "❌ Поле 'requirementsPath' не найдено"
    
    requirements_path = config['build']['requirementsPath']
    full_requirements_path = os.path.join(project_root, requirements_path)
    assert os.path.exists(full_requirements_path), f"❌ Файл {requirements_path} не найден"
    
    print(f"✅ Секция build правильно настроена, файл {requirements_path} существует")
    
    # Проверяем секцию run
    assert 'run' in config, "❌ Секция 'run' не найдена"
    
    if 'scriptName' in config['run']:
        script_name = config['run']['scriptName']
        full_script_path = os.path.join(project_root, script_name)
        assert os.path.exists(full_script_path), f"❌ Файл {script_name} не найден"
        print(f"✅ Файл запуска {script_name} существует")
    elif 'command' in config['run']:
        print(f"✅ Команда запуска: {config['run']['command']}")
    else:
        raise AssertionError("❌ Не найдено ни 'scriptName', ни 'command' в секции run")
    
    print("✅ Секция run правильно настроена")
    
    return config

def test_required_files():
    """Проверяет наличие всех необходимых файлов"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    required_files = [
        'main_with_webapp.py',
        'requirements.txt',
        'amvera.yml'
    ]
    
    for file in required_files:
        file_path = os.path.join(project_root, file)
        assert os.path.exists(file_path), f"❌ Файл {file} не найден"
        print(f"✅ Файл {file} существует")

def test_requirements_content():
    """Проверяет содержимое requirements.txt"""
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    requirements_path = os.path.join(project_root, 'requirements.txt')
    
    with open(requirements_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Проверяем наличие основных зависимостей
    required_packages = ['uvicorn', 'fastapi', 'ccxt']
    
    for package in required_packages:
        assert package.lower() in content.lower(), f"❌ Пакет {package} не найден в requirements.txt"
        print(f"✅ Пакет {package} найден в requirements.txt")

def main():
    """Запуск всех тестов"""
    print("=" * 60)
    print("🧪 ТЕСТИРОВАНИЕ КОНФИГУРАЦИИ AMVERA")
    print("=" * 60)
    
    try:
        print("\n📋 Тест 1: Проверка наличия amvera.yml")
        test_amvera_yml_exists()
        
        print("\n📋 Тест 2: Проверка формата amvera.yml")
        config = test_amvera_yml_format()
        
        print("\n📋 Тест 3: Проверка наличия всех необходимых файлов")
        test_required_files()
        
        print("\n📋 Тест 4: Проверка содержимого requirements.txt")
        test_requirements_content()
        
        print("\n" + "=" * 60)
        print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        print("\n📝 Конфигурация amvera.yml:")
        print(yaml.dump(config, allow_unicode=True, default_flow_style=False))
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ ОШИБКА: {e}")
        return False
    except Exception as e:
        print(f"\n❌ НЕПРЕДВИДЕННАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
