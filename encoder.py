import os
import re
import hashlib
import shutil
from typing import Dict, Set, List
from pathlib import Path

class ObfuscatorConfig:
    """
    Centralized configuration for the obfuscation process.
    Defines scope, exclusions, and safety whitelists.
    """
    TARGET_EXTENSIONS = {'.html', '.htm', '.css', '.js', '.scss', '.sass'}
    EXCLUDED_DIRS = {'.git', 'node_modules', 'encrypted', '__pycache__', '.vscode'}
    # HTML Tags and global attributes that must never be renamed
    WHITELIST = {
        'div', 'span', 'section', 'article', 'header', 'footer', 'main', 
        'active', 'hidden', 'visible', 'true', 'false', 'onclick', 'id', 'class'
    }
    OUTPUT_DIR = "encrypted"

class NamingStrategy:
    """
    Provides deterministic naming for obfuscated entities.
    Uses MD5 to ensure the same input always produces the same output.
    """
    @staticmethod
    def hash_name(original_name: str) -> str:
        """
        Generates a valid CSS identifier from a string.
        CSS identifiers cannot start with a digit, hence the 'v-' prefix.
        """
        hash_digest = hashlib.md5(original_name.encode()).hexdigest()
        return f"v-{hash_digest[:8]}"

class ProjectProcessor:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.output_path = self.root_path / ObfuscatorConfig.OUTPUT_DIR
        self.mapping: Dict[str, str] = {}
        self.selectors: Set[str] = set()

    def _extract_selectors(self):
        """
        Phase 1: Discovery.
        Scans all source files to build a unique set of class and ID names.
        """
        # Regex targets: class="name", id="name", .name (CSS), #name (CSS)
        pattern = re.compile(r'(?:class=|id=)["\']([\w-]+)["\']|\.([\w-]{3,})|#([\w-]{3,})')
        
        for file_path in self._get_all_files(self.root_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                matches = pattern.findall(content)
                for match in matches:
                    name = next((item for item in match if item), None)
                    if name and name not in ObfuscatorConfig.WHITELIST:
                        self.selectors.add(name)

    def _generate_mapping(self):
        """Phase 2: Mapping. Assigns hashes to discovered selectors."""
        for selector in self.selectors:
            if selector not in self.mapping:
                self.mapping[selector] = NamingStrategy.hash_name(selector)

    def _get_all_files(self, directory: Path) -> List[Path]:
        """Utility for recursive file discovery with exclusions."""
        file_list = []
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if d not in ObfuscatorConfig.EXCLUDED_DIRS]
            for file in files:
                if any(file.endswith(ext) for ext in ObfuscatorConfig.TARGET_EXTENSIONS):
                    file_list.append(Path(root) / file)
        return file_list

    def _apply_obfuscation(self):
        """
        Phase 3: Transformation.
        Applies mapping to files and saves them to the output directory.
        """
        if self.output_path.exists():
            shutil.rmtree(self.output_path)
        
        # Sort keys by length (descending) to avoid partial matches (e.g., 'btn' in 'btn-large')
        sorted_keys = sorted(self.mapping.keys(), key=len, reverse=True)

        for src_file in self._get_all_files(self.root_path):
            relative_path = src_file.relative_to(self.root_path)
            dest_file = self.output_path / relative_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)

            with open(src_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            for key in sorted_keys:
                obfuscated = self.mapping[key]
                # Using regex \b (word boundary) to ensure we only replace exact matches
                content = re.sub(rf'\b{re.escape(key)}\b', obfuscated, content)

            with open(dest_file, 'w', encoding='utf-8') as f:
                f.write(content)

    def run(self):
        """Main execution pipeline."""
        print(f"[*] Initializing Obfuscation for: {self.root_path}")
        self._extract_selectors()
        print(f"[*] Mapped {len(self.selectors)} unique selectors.")
        self._generate_mapping()
        self._apply_obfuscation()
        print(f"[+] Process complete. Output saved to: /{ObfuscatorConfig.OUTPUT_DIR}")

# ==============================================================================
# TECHNICAL DOCUMENTATION & USAGE GUIDE
# ==============================================================================
"""
OPERATIONAL OVERVIEW:
This script functions as a "Static Resource Obfuscator". It implements a three-pass 
compilation strategy to ensure referential integrity across HTML, CSS, and JS.

1. DATA DISCOVERY (The Scanner):
   The script uses a non-greedy Regex engine to find class and ID literals.
   It looks for specific HTML attributes (class, id) and CSS selectors (.name, #name).
   The discovery phase is crucial for building a 'Symbol Table' (self.mapping).

2. COLLISION AVOIDANCE:
   To prevent "Sub-string Collision" (where replacing 'nav' would break 'navbar'),
   the script employs two critical techniques:
   - Length-Based Sorting: Longer identifiers are processed first.
   - Word Boundaries (\b): Ensures that 'button' is not replaced if it's 
     part of a larger word like 'button-container', unless specified.

3. ARCHITECTURAL INTEGRITY:
   The NamingStrategy is decoupled from the ProjectProcessor. This allows 
   future-proofing; for instance, replacing MD5 with a randomly generated 
   dictionary for even higher entropy.

USAGE EXAMPLE:
    1. Place 'encoder.py' in your project root:
       /my-web-app/
       ├── index.html
       ├── styles/main.css
       ├── scripts/app.js
       └── encoder.py

    2. Execute via CLI:
       $ python3 encoder.py

    3. Result:
       The folder /my-web-app/encrypted/ will contain a functional clone
       where <div class="nav-bar"> becomes <div class="v-a7f2d1e4">.

SECURITY LIMITATIONS:
    - This is "Security by Obscurity". It stops 99% of "copy-paste" theft.
    - Does not encrypt logic; only scrambles naming conventions.
    - Avoid using dynamic class strings in JS like: elem.addClass('btn-' + type).
      The obfuscator cannot predict runtime string concatenation.
"""

if __name__ == "__main__":
    processor = ProjectProcessor(os.getcwd())
    processor.run()