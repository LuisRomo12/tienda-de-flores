import os
import re

base_dir = r"c:\uta\8-C\nuevo\aplicaciones web\carpeta entrega\segundo\proyecto\fori"

vue_url_code = "import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com')"

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    
    if 'axios.js' in filepath:
         content = content.replace("'http://localhost:8000'", vue_url_code)

    elif filepath.endswith('.vue') or ('src\\' in filepath or 'src/' in filepath):
        # We need to target fetch and axios calls that have literal strings for localhost
        # This replaces single quotes with template string
        content = re.sub(r"'http://(?:localhost|127\.0\.0\.1):8000(.*?)'", lambda m: f"`${{{vue_url_code}}}{m.group(1)}`", content)
        
        # This replaces inside existing template strings
        content = re.sub(r"`http://(?:localhost|127\.0\.0\.1):8000(.*?)`", lambda m: f"`${{{vue_url_code}}}{m.group(1)}`", content)
        
    elif 'public\\' in filepath or 'public/' in filepath:
        static_url = "const BASE_HOST_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com';\nconst API_BASE_URL = `${BASE_HOST_URL}/api/admin`; // API en FastAPI"
        
        if 'api.js' in filepath:
            content = content.replace("const API_BASE_URL = 'http://localhost:8000/api/admin'; // API en FastAPI", static_url)
            content = content.replace("'http://localhost:8000/api/admin/login'", "`${BASE_HOST_URL}/api/admin/login`")
            
        if 'app.js' in filepath:
            content = content.replace("'http://localhost:8000/api/admin/register'", "`${window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' ? 'http://localhost:8000' : 'https://tienda-de-flores.onrender.com'}/api/admin/register`")

    if original != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")

for root, dirs, files in os.walk(base_dir):
    if 'node_modules' in root or 'dist' in root:
        continue
    for file in files:
        if file.endswith('.vue') or file.endswith('.js'):
            process_file(os.path.join(root, file))
