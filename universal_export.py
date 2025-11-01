"""
УНИВЕРСАЛЬНЫЙ ЭКСПОРТЕР ДЛЯ ЛЮБЫХ ПРОЕКТОВ
"""
import os
import json
from pathlib import Path

class UniversalProjectExporter:
    def __init__(self):
        # Настройки по умолчанию для разных типов проектов
        self.presets = {
            'python': {
                'include_ext': ['.py', '.txt', '.md', '.yml', '.yaml', '.ini', '.cfg'],
                'exclude_dirs': {'.git', '__pycache__', 'venv', 'env', '.vscode', '.idea', 'logs', 'dist', 'build'},
                'exclude_files': {'.pyc', '.pkl', '.log', '.zip', '.db', '.so'}
            },
            'javascript': {
                'include_ext': ['.js', '.ts', '.jsx', '.tsx', '.json', '.html', '.css', '.md'],
                'exclude_dirs': {'.git', 'node_modules', 'dist', 'build', '.vscode'},
                'exclude_files': {'.log', '.zip'}
            },
            'java': {
                'include_ext': ['.java', '.xml', '.properties', '.md'],
                'exclude_dirs': {'.git', 'target', 'build', '.gradle'},
                'exclude_files': {'.class', '.jar', '.log'}
            },
            'all_files': {
                'include_ext': [],  # Все файлы
                'exclude_dirs': {'.git', '__pycache__', 'node_modules', 'venv'},
                'exclude_files': {'.pyc', '.class', '.log', '.zip'}
            }
        }
    
    def detect_project_type(self):
        """Автоматически определяет тип проекта"""
        files = os.listdir('.')
        
        if 'package.json' in files:
            return 'javascript'
        elif 'pom.xml' in files or 'build.gradle' in files:
            return 'java'
        elif 'requirements.txt' in files or 'setup.py' in files:
            return 'python'
        else:
            return 'all_files'
    
    def export_project(self, project_type=None, custom_settings=None):
        """Экспортирует проект"""
        if not project_type:
            project_type = self.detect_project_type()
        
        if custom_settings:
            settings = custom_settings
        else:
            settings = self.presets.get(project_type, self.presets['all_files'])
        
        print(f"🎯 Экспортируем проект типа: {project_type}")
        
        export_content = f"🚀 УНИВЕРСАЛЬНЫЙ ЭКСПОРТ ПРОЕКТА ({project_type.upper()})\n"
        export_content += "=" * 60 + "\n\n"
        
        # Структура проекта
        export_content += "📁 СТРУКТУРА ПРОЕКТА:\n"
        export_content += "=" * 30 + "\n"
        
        file_count = 0
        
        for root, dirs, files in os.walk('.'):
            # Фильтруем директории
            dirs[:] = [d for d in dirs if d not in settings['exclude_dirs']]
            
            level = root.count(os.sep) - 1
            indent = '  ' * level
            folder_name = os.path.basename(root) if os.path.basename(root) else 'ROOT'
            export_content += f"{indent}📁 {folder_name}/\n"
            
            # Файлы в текущей директории
            sub_indent = '  ' * (level + 1)
            for file in files:
                file_ext = os.path.splitext(file)[1]
                
                # Проверяем расширение
                if settings['include_ext'] and file_ext not in settings['include_ext']:
                    continue
                
                # Проверяем исключения
                if any(file.endswith(ext) for ext in settings['exclude_files']):
                    continue
                
                export_content += f"{sub_indent}📄 {file}\n"
        
        export_content += "\n\n" + "=" * 60 + "\n"
        export_content += "📄 СОДЕРЖАНИЕ ФАЙЛОВ:\n"
        export_content += "=" * 60 + "\n\n"
        
        # Содержимое файлов
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in settings['exclude_dirs']]
            
            for file in files:
                file_ext = os.path.splitext(file)[1]
                file_path = Path(root) / file
                
                # Фильтрация по расширению
                if settings['include_ext'] and file_ext not in settings['include_ext']:
                    continue
                
                # Исключения файлов
                if any(file.endswith(ext) for ext in settings['exclude_files']):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    
                    if content:
                        export_content += f"[FILE_NAME]: {file_path}\n"
                        export_content += "[FILE_CONTENT_BEGIN]\n"
                        export_content += content
                        export_content += "\n[FILE_CONTENT_END]\n\n"
                        export_content += "─" * 50 + "\n\n"
                        
                        file_count += 1
                        
                except UnicodeDecodeError:
                    # Пропускаем бинарные файлы
                    continue
                except Exception as e:
                    export_content += f"[FILE_NAME]: {file_path}\n"
                    export_content += f"[ERROR]: {e}\n\n"
                    export_content += "─" * 50 + "\n\n"
        
        export_content += f"\n✅ Всего экспортировано файлов: {file_count}\n"
        export_content += f"🎯 Тип проекта: {project_type}\n"
        
        # Сохраняем
        filename = f'project_export_{project_type}.txt'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(export_content)
        
        print(f"✅ Проект экспортирован в {filename}")
        print(f"📊 Файлов: {file_count}")
        
        return export_content
    
    def show_available_presets(self):
        """Показывает доступные пресеты"""
        print("\n🎯 ДОСТУПНЫЕ ПРЕСЕТЫ:")
        for preset_name, settings in self.presets.items():
            print(f"  {preset_name}: {settings['include_ext']}")

def main():
    exporter = UniversalProjectExporter()
    
    print("🚀 УНИВЕРСАЛЬНЫЙ ЭКСПОРТЕР ПРОЕКТОВ")
    print("=" * 50)
    
    # Автоопределение типа проекта
    detected_type = exporter.detect_project_type()
    print(f"🔍 Автоопределен тип проекта: {detected_type}")
    
    exporter.show_available_presets()
    
    # Спрашиваем пользователя
    user_choice = input(f"\n🎯 Выбери тип проекта (Enter для {detected_type}): ").strip()
    project_type = user_choice if user_choice else detected_type
    
    # Экспортируем
    exporter.export_project(project_type)

if __name__ == "__main__":
    main()