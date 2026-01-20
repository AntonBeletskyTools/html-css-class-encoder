import os

def create_demo_project():
    """
    Creates a sample web project with HTML, CSS, and JS files 
    to test the obfuscation script.
    """
    # 1. HTML File
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Obfuscation Demo</title>
    <link rel="stylesheet" href="style.css">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
    <div class="container mt-5">
        <div class="main-card-wrapper p-4 shadow-sm bg-white rounded">
            <h1 id="main-title" class="text-primary">Hello Corporate World</h1>
            <p class="description-text">This is a demo project to test the Python Obfuscator script.</p>
            
            <div class="button-group mt-3">
                <button id="action-btn" class="custom-button-primary">Click Me</button>
                <button class="custom-button-secondary">Secondary Action</button>
            </div>
            
            <div id="status-message" class="alert-box hidden">
                Success! The script is working.
            </div>
        </div>
    </div>
    <script src="script.js"></script>
</body>
</html>"""

    # 2. CSS File
    css_content = """/* Custom styles with complex selectors */
.main-card-wrapper {
    border: 2px solid #e0e0e0;
    transition: transform 0.3s ease;
}

.main-card-wrapper:hover {
    transform: translateY(-5px);
}

.description-text {
    font-size: 1.1rem;
    color: #666;
}

.custom-button-primary {
    background-color: #007bff;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.custom-button-secondary {
    background-color: #6c757d;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    margin-left: 10px;
}

.alert-box {
    margin-top: 20px;
    padding: 15px;
    background-color: #d4edda;
    color: #155724;
    border-radius: 4px;
}

.hidden {
    display: none;
}"""

    # 3. JS File
    js_content = """document.addEventListener('DOMContentLoaded', () => {
    const actionBtn = document.getElementById('action-btn');
    const statusMsg = document.getElementById('status-message');

    // Testing selector replacement in JS
    actionBtn.addEventListener('click', () => {
        console.log('Button clicked!');
        
        // Toggle classes
        statusMsg.classList.toggle('hidden');
        
        // Changing content of a selector
        const title = document.querySelector('#main-title');
        title.style.color = 'green';
    });
});"""

    # Writing files to disk
    files = {
        "index.html": html_content,
        "style.css": css_content,
        "script.js": js_content
    }

    for filename, content in files.items():
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[+] Created {filename}")

    print("\\n[!] Demo project is ready. Now run 'python encoder.py' to encrypt it.")

if __name__ == "__main__":
    create_demo_project()
