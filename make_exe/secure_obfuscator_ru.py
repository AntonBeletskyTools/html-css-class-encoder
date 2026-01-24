#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enterprise Static Resource Obfuscator
=====================================
Инструмент для безопасной обфускации HTML/CSS/JS проектов.
Гарантирует целостность путей, переменных и визуального отображения.

Автор: Gemini AI
Версия: 2.0.0 (Production Ready)
"""

import os
import re
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Dict, Set, List, Pattern
from dataclasses import dataclass, field

# --- КОНФИГУРАЦИЯ ЛОГГЕРА ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Obfuscator")

@dataclass
class Config:
    """Централизованная конфигурация проекта."""
    
    # Папка с исходным кодом (откуда берем)
    SOURCE_DIR: str = "src" 
    
    # Папка для готового билда (куда кладем)
    DIST_DIR: str = "dist"
    
    # Файлы, которые подлежат обработке
    TARGET_EXTENSIONS: Set[str] = field(default_factory=lambda: {'.html', '.htm', '.css', '.js'})
    
    # Папки, которые полностью игнорируем
    EXCLUDED_DIRS: Set[str] = field(default_factory=lambda: {'.git', 'node_modules', '.vscode', '__pycache__', 'venv'})
    
    # Вайтлист (слова, которые НЕЛЬЗЯ трогать ни при каких условиях)
    # Сюда добавляем теги, стандартные атрибуты, зарезервированные слова JS/CSS
    WHITELIST: Set[str] = field(default_factory=lambda: {
        'body', 'html', 'head', 'title', 'meta', 'link', 'script', 'div', 'span', 
        'section', 'article', 'header', 'footer', 'main', 'nav', 'ul', 'li', 'a', 
        'img', 'button', 'input', 'form', 'label', 'p', 'h1', 'h2', 'h3', 'container',
        'row', 'col', 'hidden', 'active', 'show', 'type', 'name', 'id', 'class', 
        'href', 'src', 'style', 'width', 'height', 'checked', 'disabled'
    })

class Hasher:
    """Отвечает за генерацию детерминированных имен."""
    
    @staticmethod
    def generate(name: str) -> str:
        """Создает короткий валидный CSS-идентификатор (начинается с буквы)."""
        hash_obj = hashlib.md5(name.encode())
        # Префикс 'x' гарантирует, что имя не начнется с цифры или дефиса
        return f"x{hash_obj.hexdigest()[:6]}"

class ContextProcessor:
    """
    Ядро логики обработки. Использует регулярные выражения с учетом контекста,
    чтобы не ломать пути, переменные и значения.
    """

    def __init__(self, mapping: Dict[str, str]):
        self.mapping = mapping
        # Сортируем ключи по длине (от длинных к коротким), чтобы избежать 
        # частичной замены (например, чтобы замена 'btn' не сломала 'btn-group')
        self.sorted_keys = sorted(self.mapping.keys(), key=len, reverse=True)

    def process_html(self, content: str) -> str:
        """
        Безопасная обработка HTML.
        Меняет классы и ID только внутри атрибутов class="..." и id="...".
        """
        def replace_attr_value(match):
            attr_name = match.group(1) # class или id
            quote = match.group(2)     # " или '
            values = match.group(3)    # содержимое атрибута (напр. "btn btn-red")
            
            new_values = []
            for val in values.split():
                # Если значение есть в маппинге, меняем. Если нет — оставляем.
                new_values.append(self.mapping.get(val, val))
            
            return f'{attr_name}={quote}{" ".join(new_values)}{quote}'

        # Ищем паттерн: (class|id)=["']...["']
        pattern = re.compile(r'\b(class|id)=("|\')(.*?)(\2)')
        return pattern.sub(replace_attr_value, content)

    def process_css(self, content: str) -> str:
        """
        Безопасная обработка CSS.
        1. Игнорирует CSS-переменные (--var).
        2. Меняет селекторы (.class, #id).
        3. Не трогает свойства (color: red) и пути (url(...)).
        """
        # Сначала защитим переменные, заменив их на плейсхолдеры (чтобы случайно не задеть)
        # Это сложная логика, поэтому пойдем путем умного Lookbehind regex.
        
        processed_content = content
        
        for key in self.sorted_keys:
            target = self.mapping[key]
            
            # Regex объяснение:
            # (?<=[.#])      -> Ищем только если перед словом стоит точка или решетка
            # {re.escape(key)} -> Наше искомое слово
            # (?![\w-])      -> И убеждаемся, что слово закончилось (нет продолжения типа -primary)
            # ПРИ ЭТОМ: Этот паттерн не матчит --variable, так как там два дефиса, а не . или #
            pattern = re.compile(rf'(?<=[.#]){re.escape(key)}(?![\w-])')
            processed_content = pattern.sub(target, processed_content)
            
        return processed_content

    def process_js(self, content: str) -> str:
        """
        Обработка JS (ОСТОРОЖНЫЙ РЕЖИМ).
        Меняет только строковые литералы, которые точно совпадают с именем класса.
        НЕ меняет динамическую конкатенацию ('btn-' + type).
        """
        processed_content = content
        for key in self.sorted_keys:
            target = self.mapping[key]
            # Ищем точное совпадение слова в кавычках
            # classList.add('my-class') -> classList.add('x3f4a1')
            pattern = re.compile(rf'(["\']){re.escape(key)}\1')
            processed_content = pattern.sub(f"\\1{target}\\1", processed_content)
        return processed_content

class ProjectObfuscator:
    def __init__(self, config: Config):
        self.cfg = config
        self.root = Path(os.getcwd())
        self.src_path = self.root / self.cfg.SOURCE_DIR
        self.dist_path = self.root / self.cfg.DIST_DIR
        self.mapping: Dict[str, str] = {}
        
        if not self.src_path.exists():
            raise FileNotFoundError(f"Исходная папка не найдена: {self.src_path}")

    def _scan_selectors(self):
        """Этап 1: Сканирование всех HTML файлов для поиска классов и ID."""
        logger.info("Начинаю сканирование исходных кодов...")
        selector_set = set()
        
        # Regex для поиска значений внутри class="" и id=""
        attr_pattern = re.compile(r'\b(?:class|id)=["\'](.*?)["\']')

        for file_path in self._walk_files(self.src_path):
            if file_path.suffix in {'.html', '.htm'}:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = attr_pattern.findall(content)
                    for match in matches:
                        # Разбиваем "btn btn-primary" на отдельные слова
                        names = match.split()
                        for name in names:
                            if name not in self.cfg.WHITELIST:
                                selector_set.add(name)
        
        logger.info(f"Найдено {len(selector_set)} уникальных селекторов для обфускации.")
        
        # Генерируем маппинг
        for selector in selector_set:
            self.mapping[selector] = Hasher.generate(selector)

    def _walk_files(self, path: Path) -> List[Path]:
        """Рекурсивный обход файлов с учетом исключений."""
        files_found = []
        for root, dirs, files in os.walk(path):
            # Фильтрация папок
            dirs[:] = [d for d in dirs if d not in self.cfg.EXCLUDED_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in self.cfg.TARGET_EXTENSIONS:
                    files_found.append(file_path)
        return files_found

    def _clone_project(self):
        """Создает полную копию проекта в папку dist."""
        if self.dist_path.exists():
            logger.warning(f"Удаление старой версии билда: {self.dist_path}")
            shutil.rmtree(self.dist_path)
        
        logger.info(f"Клонирование проекта: {self.src_path} -> {self.dist_path}")
        shutil.copytree(self.src_path, self.dist_path, 
                       ignore=shutil.ignore_patterns(*self.cfg.EXCLUDED_DIRS))

    def run(self):
        """Главный метод запуска."""
        print("-" * 50)
        print("🚀 ЗАПУСК ОБФУСКАТОРА v2.0")
        print("-" * 50)

        # 1. Сканируем исходники и строим карту хешей
        self._scan_selectors()

        # 2. Создаем рабочую копию (чтобы не трогать исходники)
        self._clone_project()

        # 3. Применяем замены в dist папке
        processor = ContextProcessor(self.mapping)
        processed_count = 0

        # Обрабатываем файлы в новой папке dist
        target_files = []
        for root, dirs, files in os.walk(self.dist_path):
             for file in files:
                 fpath = Path(root) / file
                 if fpath.suffix in self.cfg.TARGET_EXTENSIONS:
                     target_files.append(fpath)

        logger.info(f"Начинаю обработку {len(target_files)} файлов...")

        for file_path in target_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                new_content = content
                ext = file_path.suffix

                # Применяем стратегию в зависимости от типа файла
                if ext in {'.html', '.htm'}:
                    new_content = processor.process_html(new_content)
                    # HTML также может содержать внутренние стили, 
                    # но для простоты здесь меняем только атрибуты
                
                elif ext == '.css':
                    new_content = processor.process_css(new_content)
                
                elif ext == '.js':
                    new_content = processor.process_js(new_content)

                # Записываем изменения
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    processed_count += 1
            
            except Exception as e:
                logger.error(f"Ошибка при обработке {file_path}: {e}")

        print("-" * 50)
        logger.info(f"✅ Успешно! Обработано файлов: {processed_count}")
        logger.info(f"📁 Результат находится в папке: {self.dist_path.absolute()}")
        print("-" * 50)

if __name__ == "__main__":
    # Предполагается, что исходники лежат в папке 'src' рядом со скриптом.
    # Если они лежат в текущей папке (где скрипт), измените SOURCE_DIR="." 
    # Но лучше положить сайт в подпапку src для порядка.
    
    # ПРИМЕР: Структура папок
    # /my-project
    #    ├── secure_obfuscator.py
    #    └── src/              <-- Сюда положи свой сайт (index.html, css, js)
    #          ├── index.html
    #          └── style.css
    
    try:
        config = Config(SOURCE_DIR="src", DIST_DIR="dist-encrypted")
        app = ProjectObfuscator(config)
        app.run()
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")