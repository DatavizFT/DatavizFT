#!/usr/bin/env python3
"""
Script pour créer une prévisualisation HTML du README.md
Contournement pour le bug de VS Code 1.105.0
"""

import webbrowser
from pathlib import Path

try:
    import markdown
    from markdown.extensions import codehilite, fenced_code, tables
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    print("⚠️ Module markdown non disponible. Installation en cours...")

def markdown_to_html(markdown_text):
    """Convertit le Markdown en HTML avec la bibliothèque markdown."""
    if MARKDOWN_AVAILABLE:
        md = markdown.Markdown(extensions=[
            'tables',
            'fenced_code',
            'codehilite',
            'nl2br',
            'toc'
        ])
        return md.convert(markdown_text)
    else:
        # Fallback basique si markdown n'est pas disponible
        return f"<pre>{markdown_text}</pre>"

def create_readme_preview():
    """Crée une prévisualisation HTML du README.md"""

    # Chemin du README
    readme_path = Path(__file__).parent.parent / "README.md"

    if not readme_path.exists():
        print(f"❌ README.md non trouvé : {readme_path}")
        return

    # Lire le contenu
    with open(readme_path, encoding='utf-8') as f:
        markdown_content = f.read()

    # CSS moderne
    css = """
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px;
            background: #fafafa;
            color: #333;
        }
        h1 {
            color: #2c5aa0;
            border-bottom: 3px solid #f39c12;
            padding-bottom: 10px;
            font-size: 2.5em;
        }
        h2 {
            color: #27ae60;
            margin-top: 30px;
            font-size: 1.8em;
        }
        h3 {
            color: #8e44ad;
            margin-top: 25px;
            font-size: 1.4em;
        }
        pre {
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid #4299e1;
        }
        code {
            background: #f7fafc;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'JetBrains Mono', Consolas, monospace;
            color: #e53e3e;
            border: 1px solid #e2e8f0;
        }
        pre code {
            background: transparent;
            border: none;
            color: inherit;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #e2e8f0;
            padding: 12px;
            text-align: left;
        }
        th {
            background: #4299e1;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background: #f7fafc;
        }
        .badges img {
            margin: 2px;
        }
        ul, ol {
            padding-left: 20px;
        }
        li {
            margin: 5px 0;
        }
        blockquote {
            border-left: 4px solid #4299e1;
            background: #f7fafc;
            padding: 15px 20px;
            margin: 20px 0;
            font-style: italic;
        }
        .center {
            text-align: center;
        }
        .emoji {
            font-size: 1.2em;
        }
    </style>
    """

    # Convertir le Markdown en HTML
    html_content = markdown_to_html(markdown_content)

    # Template HTML
    html_template = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DatavizFT - README Preview</title>
    {css}
</head>
<body>
    <div class="container">
        {html_content}
    </div>
    
    <script>
        // Améliorer l'affichage des badges
        document.querySelectorAll('img[src*="shields.io"], img[src*="badge"]').forEach(img => {{
            img.style.margin = '2px';
            img.style.verticalAlign = 'middle';
        }});
        
        // Améliorer les tables
        document.querySelectorAll('table').forEach(table => {{
            table.style.borderCollapse = 'collapse';
            table.style.width = '100%';
            table.style.marginBottom = '20px';
        }});
    </script>
</body>
</html>"""

    # Sauvegarder le fichier HTML
    output_path = Path(__file__).parent.parent / "readme_preview.html"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"✅ Prévisualisation créée : {output_path}")

    # Ouvrir dans le navigateur
    try:
        webbrowser.open(f"file://{output_path.absolute()}")
        print("🌐 Ouverture dans le navigateur par défaut...")
    except Exception as e:
        print(f"⚠️ Impossible d'ouvrir automatiquement : {e}")
        print(f"📂 Ouvrez manuellement : {output_path}")

if __name__ == "__main__":
    create_readme_preview()
