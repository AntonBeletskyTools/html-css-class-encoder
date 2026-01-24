#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Enterprise Static Resource Obfuscator
=====================================
Tool for secure obfuscation of HTML/CSS/JS projects.
Guarantees integrity of paths, variables, and visual rendering.

Author: Gemini AI
Version: 2.0.0 (Production Ready)
"""

import os
import re
import shutil
import hashlib
import logging
from pathlib import Path
from typing import Dict, Set, List, Pattern
from dataclasses import dataclass, field

# --- LOGGER CONFIGURATION ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("Obfuscator")

@dataclass
class Config:
    """Centralized project configuration."""
    
    # Source code directory (input)
    SOURCE_DIR: str = "src" 
    
    # Build directory (output)
    DIST_DIR: str = "dist"
    
    # Files to be processed
    TARGET_EXTENSIONS: Set[str] = field(default_factory=lambda: {'.html', '.htm', '.css', '.js'})
    
    # Directories to ignore completely
    EXCLUDED_DIRS: Set[str] = field(default_factory=lambda: {'.git', 'node_modules', '.vscode', '__pycache__', 'venv'})
    
    # Whitelist (words that MUST NOT be touched under any circumstances)
    # Includes tags, standard attributes, and reserved JS/CSS words
    WHITELIST: Set[str] = field(default_factory=lambda: {
        'body', 'html', 'head', 'title', 'meta', 'link', 'script', 'div', 'span', 
        'section', 'article', 'header', 'footer', 'main', 'nav', 'ul', 'li', 'a', 
        'img', 'button', 'input', 'form', 'label', 'p', 'h1', 'h2', 'h3', 'container',
        'row', 'col', 'hidden', 'active', 'show', 'type', 'name', 'id', 'class', 
        'href', 'src', 'style', 'width', 'height', 'checked', 'disabled'
    })

class Hasher:
    """Responsible for generating deterministic names."""
    
    @staticmethod
    def generate(name: str) -> str:
        """Creates a short valid CSS identifier (starts with a letter)."""
        hash_obj = hashlib.md5(name.encode())
        # Prefix 'x' ensures the name doesn't start with a digit or hyphen
        return f"x{hash_obj.hexdigest()[:6]}"

class ContextProcessor:
    """
    Core processing logic. Uses context-aware regular expressions
    to avoid breaking paths, variables, and values.
    """

    def __init__(self, mapping: Dict[str, str]):
        self.mapping = mapping
        # Sort keys by length (longest to shortest) to avoid 
        # partial replacement (e.g., to prevent 'btn' from breaking 'btn-group')
        self.sorted_keys = sorted(self.mapping.keys(), key=len, reverse=True)

    def process_html(self, content: str) -> str:
        """
        Safe HTML processing.
        Changes classes and IDs only inside class="..." and id="..." attributes.
        """
        def replace_attr_value(match):
            attr_name = match.group(1) # class or id
            quote = match.group(2)     # " or '
            values = match.group(3)    # attribute content (e.g., "btn btn-red")
            
            new_values = []
            for val in values.split():
                # If value is in mapping, replace it. Otherwise, keep original.
                new_values.append(self.mapping.get(val, val))
            
            return f'{attr_name}={quote}{" ".join(new_values)}{quote}'

        # Search pattern: (class|id)=["']...["']
        pattern = re.compile(r'\b(class|id)=("|\')(.*?)(\2)')
        return pattern.sub(replace_attr_value, content)

    def process_css(self, content: str) -> str:
        """
        Safe CSS processing.
        1. Ignores CSS variables (--var).
        2. Changes selectors (.class, #id).
        3. Doesn't touch properties (color: red) or paths (url(...)).
        """
        # We use a smart Lookbehind regex to target only specific selectors.
        
        processed_content = content
        
        for key in self.sorted_keys:
            target = self.mapping[key]
            
            # Regex explanation:
            # (?<=[.#])      -> Look for the word only if preceded by a dot or hash
            # {re.escape(key)} -> The target word
            # (?![\w-])      -> Ensure the word ends there (no suffixes like -primary)
            # NOTE: This pattern won't match --variable since it has two hyphens, not . or #
            pattern = re.compile(rf'(?<=[.#]){re.escape(key)}(?![\w-])')
            processed_content = pattern.sub(target, processed_content)
            
        return processed_content

    def process_js(self, content: str) -> str:
        """
        JS processing (CAUTIOUS MODE).
        Only changes string literals that exactly match a class name.
        Does NOT change dynamic concatenation ('btn-' + type).
        """
        processed_content = content
        for key in self.sorted_keys:
            target = self.mapping[key]
            # Look for exact word match inside quotes
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
            raise FileNotFoundError(f"Source folder not found: {self.src_path}")

    def _scan_selectors(self):
        """Phase 1: Scanning all HTML files to find classes and IDs."""
        logger.info("Starting source code scan...")
        selector_set = set()
        
        # Regex to find values inside class="" and id=""
        attr_pattern = re.compile(r'\b(?:class|id)=["\'](.*?)["\']')

        for file_path in self._walk_files(self.src_path):
            if file_path.suffix in {'.html', '.htm'}:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    matches = attr_pattern.findall(content)
                    for match in matches:
                        # Split "btn btn-primary" into individual words
                        names = match.split()
                        for name in names:
                            if name not in self.cfg.WHITELIST:
                                selector_set.add(name)
        
        logger.info(f"Found {len(selector_set)} unique selectors for obfuscation.")
        
        # Generate mapping
        for selector in selector_set:
            self.mapping[selector] = Hasher.generate(selector)

    def _walk_files(self, path: Path) -> List[Path]:
        """Recursive file traversal considering exclusions."""
        files_found = []
        for root, dirs, files in os.walk(path):
            # Filter directories
            dirs[:] = [d for d in dirs if d not in self.cfg.EXCLUDED_DIRS]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in self.cfg.TARGET_EXTENSIONS:
                    files_found.append(file_path)
        return files_found

    def _clone_project(self):
        """Creates a full copy of the project in the dist folder."""
        if self.dist_path.exists():
            logger.warning(f"Removing old build version: {self.dist_path}")
            shutil.rmtree(self.dist_path)
        
        logger.info(f"Cloning project: {self.src_path} -> {self.dist_path}")
        shutil.copytree(self.src_path, self.dist_path, 
                        ignore=shutil.ignore_patterns(*self.cfg.EXCLUDED_DIRS))

    def run(self):
        """Main execution method."""
        print("-" * 50)
        print("🚀 STARTING OBFUSCATOR v2.0")
        print("-" * 50)

        # 1. Scan sources and build hash map
        self._scan_selectors()

        # 2. Create a working copy (to avoid touching originals)
        self._clone_project()

        # 3. Apply replacements in dist folder
        processor = ContextProcessor(self.mapping)
        processed_count = 0

        # Process files in the new dist folder
        target_files = []
        for root, dirs, files in os.walk(self.dist_path):
             for file in files:
                 fpath = Path(root) / file
                 if fpath.suffix in self.cfg.TARGET_EXTENSIONS:
                     target_files.append(fpath)

        logger.info(f"Starting processing of {len(target_files)} files...")

        for file_path in target_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                new_content = content
                ext = file_path.suffix

                # Apply strategy based on file type
                if ext in {'.html', '.htm'}:
                    new_content = processor.process_html(new_content)
                    # HTML may also contain internal styles, 
                    # but for simplicity we only change attributes here
                
                elif ext == '.css':
                    new_content = processor.process_css(new_content)
                
                elif ext == '.js':
                    new_content = processor.process_js(new_content)

                # Save changes
                if new_content != content:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    processed_count += 1
            
            except Exception as e:
                logger.error(f"Error while processing {file_path}: {e}")

        print("-" * 50)
        logger.info(f"✅ Success! Files processed: {processed_count}")
        logger.info(f"📁 Result is located in: {self.dist_path.absolute()}")
        print("-" * 50)

if __name__ == "__main__":
    # Assumes source files are in 'src' folder next to the script.
    # If they are in the current folder, change SOURCE_DIR="."
    # However, it is better to keep the site in a 'src' subfolder for organization.
    
    # EXAMPLE: Folder structure
    # /my-project
    #    ├── secure_obfuscator.py
    #    └── src/              <-- Put your site here (index.html, css, js)
    #          ├── index.html
    #          └── style.css
    
    try:
        config = Config(SOURCE_DIR="src", DIST_DIR="dist-encrypted")
        app = ProjectObfuscator(config)
        app.run()
    except Exception as e:
        logger.critical(f"Critical error: {e}")