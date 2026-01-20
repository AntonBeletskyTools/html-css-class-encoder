import os

def create_pure_demo():
    """
    Generates a standalone web project with zero external dependencies.
    Designed specifically to test class and ID obfuscation.
    """
    
    # 1. HTML - Pure structure
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Internal Demo System</title>
    <link rel="stylesheet" href="style.css">
</head>
<body class="app-background">
    <header class="top-navigation-bar">
        <div class="logo-container">
            <span id="brand-name">PROTECT-TECH</span>
        </div>
    </header>

    <main class="content-viewport">
        <section class="dashboard-card">
            <h1 class="primary-heading">Secure Dashboard</h1>
            <p class="status-description">System status: <span id="system-indicator" class="label-inactive">Standby</span></p>
            
            <div class="control-panel">
                <button id="init-sequence-btn" class="btn-action-primary">Initialize System</button>
                <button class="btn-action-reset">Reset View</button>
            </div>
        </section>

        <div id="data-log-window" class="log-container hidden-element">
            <p class="log-entry">Attempting secure handshake...</p>
            <p class="log-entry">Data integrity verified.</p>
        </div>
    </main>

    <script src="script.js"></script>
</body>
</html>"""

    # 2. CSS - Using complex nesting and custom properties
    css_content = """/* Global Styles */
:root {
    --primary-color: #2563eb;
    --success-color: #16a34a;
}

.app-background {
    background-color: #f8fafc;
    font-family: sans-serif;
    margin: 0;
}

.top-navigation-bar {
    background: #1e293b;
    color: white;
    padding: 1rem 2rem;
}

.content-viewport {
    max-width: 800px;
    margin: 40px auto;
    padding: 0 20px;
}

.dashboard-card {
    background: white;
    padding: 30px;
    border-radius: 12px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.primary-heading {
    color: #1e293b;
    margin-top: 0;
}

/* Specific button classes for testing length-based sorting */
.btn-action-primary {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: bold;
}

.btn-action-reset {
    background: transparent;
    color: #64748b;
    border: 1px solid #cbd5e1;
    padding: 12px 24px;
    border-radius: 6px;
    margin-left: 10px;
    cursor: pointer;
}

.label-inactive {
    color: #ef4444;
    font-weight: bold;
}

.label-active {
    color: var(--success-color);
    font-weight: bold;
}

.log-container {
    margin-top: 20px;
    background: #0f172a;
    color: #38bdf8;
    padding: 15px;
    border-radius: 8px;
    font-family: monospace;
}

.hidden-element {
    display: none;
}"""

    # 3. JS - Logic with selectors and class manipulation
    js_content = """document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('init-sequence-btn');
    const indicator = document.getElementById('system-indicator');
    const logWindow = document.getElementById('data-log-window');

    startBtn.addEventListener('click', () => {
        // Toggle system status via class replacement
        if (indicator.classList.contains('label-inactive')) {
            indicator.classList.remove('label-inactive');
            indicator.classList.add('label-active');
            indicator.textContent = 'Operational';
            
            // Show the log window
            logWindow.classList.remove('hidden-element');
            startBtn.textContent = 'Shutdown';
        } else {
            indicator.classList.add('label-inactive');
            indicator.classList.remove('label-active');
            indicator.textContent = 'Standby';
            
            logWindow.classList.add('hidden-element');
            startBtn.textContent = 'Initialize System';
        }
    });
});"""

    # Writing files
    files = {
        "index.html": html_content,
        "style.css": css_content,
        "script.js": js_content
    }

    for filename, content in files.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Generated: {filename}")

    print("\n[SUCCESS] Pure demo project ready. No external dependencies.")
    print("[RUN] 'python encoder.py' to test obfuscation on this local code.")

if __name__ == "__main__":
    create_pure_demo()