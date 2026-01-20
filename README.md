===============================================================================
# 💾 Enterprise Static Source Obfuscator v2.0

```
===============================================================================
███████╗███████╗ ██████╗██╗   ██╗██████╗ ███████╗
██╔════╝██╔════╝██╔════╝██║   ██║██╔══██╗██╔════╝
███████╗█████╗  ██║     ██║   ██║██████╔╝█████╗  
╚════██║██╔══╝  ██║     ██║   ██║██╔══██╗██╔══╝  
███████║███████╗╚██████╗╚██████╔╝██║  ██║███████╗
╚══════╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝
      >> ENTERPRISE STATIC SOURCE OBFUSCATOR <<
===============================================================================
```

      (C) COPYRIGHT 2026 [GEMINI SYSTEMS CORP](https://github.com/AntonBeletskyTools). ALL RIGHTS RESERVED.
      SYSTEM REQUIREMENT: PYTHON 3.8 OR HIGHER.

[1.0] DESCRIPTION
-------------------------------------------------------------------------------
SECURE_OBFUSCATOR.PY is a high-grade security utility designed to scramble 
web-source metadata (HTML classes and IDs) to prevent unauthorized reverse 
engineering and source theft. Unlike primitive string-replacers, this system 
utilizes CONTEXT-AWARE ANALYSIS to ensure that your UI remains pixel-perfect 
while your code becomes unreadable to humans.

[2.0] KEY FEATURES
-------------------------------------------------------------------------------
* ADVANCED CONTEXT FILTERING: Only obfuscates attributes (class, id). 
  Does NOT break file paths, image URLs, or standard HTML tags.
* CSS VARIABLE PROTECTION: Guaranteed safety for --css-variables and var().
* JS LITERAL SCANNING: Scrambles hardcoded strings in JavaScript logic.
* DETERMINISTIC HASHING: Uses MD5 algorithms for consistent naming.
* NON-DESTRUCTIVE: All operations occur in the /DIST/ folder. 
  Your /SRC/ directory remains untouched.

[3.0] INSTALLATION & WORKFLOW
-------------------------------------------------------------------------------
Ensure your project is structured as follows:

    C:\MY_PROJECT\
    │
    ├── secure_obfuscator.py   <-- THE EXECUTABLE
    └── src\                   <-- YOUR SOURCE FILES GO HERE
        ├── index.html
        ├── styles\
        └── scripts\

[4.0] EXECUTION
-------------------------------------------------------------------------------
1. Place your raw HTML/CSS/JS files into the [src] directory.
2. Open your COMMAND PROMPT (cmd.exe or PowerShell).
3. Navigate to your project directory.
4. Execute the following command:

    C:\> python secure_obfuscator.py

5. Upon completion, the obfuscated "Ready-to-Deploy" version will be 
   available in the [dist-encrypted] directory.

[5.0] CONFIGURATION & WHITELISTING
-------------------------------------------------------------------------------
To prevent obfuscation of specific keywords (e.g., Bootstrap classes or 
external API hooks), edit the [Config] class inside the script:

    WHITELIST = {'my-special-class', 'ignore-me', 'bootstrap-class'}

[6.0] LIMITATIONS
-------------------------------------------------------------------------------
* Does not obfuscate dynamic JS concatenation like: elem.add('btn-' + color).
* External CDN resources (like FontAwesome) must be whitelisted if they are
  not hosted locally.

-------------------------------------------------------------------------------
EOF - END OF FILE
===============================================================================
