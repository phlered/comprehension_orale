#!/usr/bin/env python3
"""
Serveur web pour l'interface batch_genmp3.py
Fournit une API REST pour générer les ressources audio

Usage:
    python batch_server.py        # Lance sur http://localhost:5000
    python batch_server.py --port 8080
"""

import argparse
import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path
from typing import Generator
import traceback
import webbrowser
import threading
import time
import signal

try:
    from flask import Flask, render_template, request, jsonify, send_from_directory, Response
    from werkzeug.utils import secure_filename
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    print("❌ Flask non installé. Installez avec: pip install flask")
    sys.exit(1)


class BatchProcessor:
    """Traite les demandes de génération batch"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.python_exe = str(self.project_root / ".venv312" / "bin" / "python")
        
    def process_batch(self, prompt_file: str, languages: str, level: str, delay: float = 3.0, ssml: bool = False) -> Generator[str, None, None]:
        """
        Lance la génération batch et yield les résultats ligne par ligne
        
        Args:
            prompt_file: Chemin du fichier de prompts
            languages: Langues séparées par virgule (nl,eng,all)
            level: Niveau CECRL (A1-C2)
            delay: Délai entre les générations en secondes
            ssml: Activer SSML pour emphases et pauses
            
        Yields:
            Lignes JSON avec: type, message, status, current, total
        """
        # Construire la commande avec Python unbuffered
        cmd = [
            self.python_exe,
            "-u",  # Unbuffered output
            str(self.project_root / "batch_genmp3.py"),
            "-f", prompt_file,
            "-l", languages,
            "-n", level,
            "--delai", str(delay)
        ]
        
        # Ajouter --ssml si activé
        if ssml:
            cmd.append("--ssml")
        
        yield json.dumps({
            "type": "status",
            "message": f"🚀 Démarrage de la génération batch...",
            "status": "info"
        }) + "\n"
        
        yield json.dumps({
            "type": "output",
            "message": f"Commande: {' '.join(cmd)}\n"
        }) + "\n"
        
        try:
            # Lancer le processus
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,  # Line buffered
                cwd=str(self.project_root)
            )
            
            # Lire la sortie ligne par ligne
            for line in iter(process.stdout.readline, ''):
                if line:
                    yield json.dumps({
                        "type": "output",
                        "message": line.rstrip('\n')
                    }) + "\n"
            
            # Attendre la fin du processus
            process.wait()
            
            if process.returncode == 0:
                yield json.dumps({
                    "type": "status",
                    "message": "✅ Génération batch réussie!",
                    "status": "success"
                }) + "\n"
                
                # Lancer la mise à jour du site
                yield json.dumps({
                    "type": "status",
                    "message": "🔨 Mise à jour du site web...",
                    "status": "info"
                }) + "\n"
                
                site_cmd = ["bash", str(self.project_root / "site.sh"), "build"]
                site_process = subprocess.Popen(
                    site_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    cwd=str(self.project_root)
                )
                
                for line in iter(site_process.stdout.readline, ''):
                    if line:
                        yield json.dumps({
                            "type": "output",
                            "message": line.rstrip('\n')
                        }) + "\n"
                
                site_process.wait()
                
                if site_process.returncode == 0:
                    yield json.dumps({
                        "type": "status",
                        "message": "✅ Site web mis à jour avec succès!",
                        "status": "success"
                    }) + "\n"
                else:
                    yield json.dumps({
                        "type": "status",
                        "message": "⚠️  La mise à jour du site a rencontré une erreur",
                        "status": "warning"
                    }) + "\n"
            else:
                yield json.dumps({
                    "type": "status",
                    "message": f"❌ Génération batch échouée (code {process.returncode})",
                    "status": "error"
                }) + "\n"
            
            yield json.dumps({
                "type": "complete",
                "message": "Processus terminé"
            }) + "\n"
            
        except Exception as e:
            error_msg = f"Erreur lors de l'exécution: {str(e)}\n{traceback.format_exc()}"
            yield json.dumps({
                "type": "error",
                "message": error_msg,
                "status": "error"
            }) + "\n"


def create_app(project_root: str = "."):
    """Crée l'application Flask"""
    app = Flask(__name__, static_folder=".", static_url_path="")
    
    # Configuration
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max
    UPLOAD_FOLDER = tempfile.gettempdir()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    project_path = Path(project_root).resolve()
    processor = BatchProcessor(str(project_path))
    
    @app.route('/')
    def index():
        """Serve the HTML interface"""
        return send_from_directory(".", "batch_ui.html")
    
    @app.route('/api/batch-generate', methods=['POST'])
    def batch_generate():
        """API endpoint for batch generation with streaming output"""
        
        # Validate request
        prompt_text = request.form.get('promptText')
        if not prompt_text:
            return jsonify({"error": "No prompt text provided"}), 400
        
        level = request.form.get('level')
        languages = request.form.get('languages')
        delay = request.form.get('delay', '40.0')  # Default 40 seconds
        ssml = request.form.get('ssml') == '1'  # Checkbox value
        
        if not level or not languages:
            return jsonify({"error": "Missing level or languages"}), 400
        
        # Validate level
        valid_levels = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
        if level not in valid_levels:
            return jsonify({"error": f"Invalid level: {level}"}), 400
        
        # Validate delay
        try:
            delay_float = float(delay)
            if delay_float < 0 or delay_float > 120:
                delay_float = 40.0
        except (ValueError, TypeError):
            delay_float = 40.0
        
        # Validate languages
        valid_langs = ['fr', 'eng', 'us', 'esp', 'hisp', 'nl', 'all', 'co', 'cor', 'it']
        langs = [l.strip() for l in languages.split(',')]
        invalid_langs = [l for l in langs if l not in valid_langs]
        if invalid_langs:
            return jsonify({"error": f"Invalid languages: {', '.join(invalid_langs)}"}), 400
        
        # Create temporary file with prompt text
        temp_fd, filepath = tempfile.mkstemp(suffix='.md', dir=app.config['UPLOAD_FOLDER'])
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as f:
                f.write(prompt_text)
        except Exception as e:
            os.close(temp_fd)
            return jsonify({"error": f"Failed to create temp file: {str(e)}"}), 500
        
        try:
            # Generate streaming response and cleanup the temp file AFTER stream ends
            def stream_and_cleanup():
                try:
                    for line in processor.process_batch(filepath, languages, level, delay_float, ssml):
                        yield line
                finally:
                    try:
                        os.remove(filepath)
                    except Exception:
                        pass
            
            return Response(stream_and_cleanup(), mimetype='application/x-ndjson')
        except Exception as e:
            error_msg = f"Server error: {str(e)}"
            return Response(
                json.dumps({"type": "error", "message": error_msg, "status": "error"}) + "\n",
                status=500,
                mimetype='application/json'
            )
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    return app


def open_browser(url: str, delay: float = 1.5):
    """Ouvre le navigateur après un court délai"""
    def _open():
        time.sleep(delay)
        print(f"🌐 Ouverture du navigateur sur {url}...")
        webbrowser.open(url)
    
    threading.Thread(target=_open, daemon=True).start()


def setup_signal_handler():
    """Configure un gestionnaire propre pour Ctrl+C"""
    def signal_handler(sig, frame):
        print("\n\n👋 Arrêt du serveur...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)


def main():
    parser = argparse.ArgumentParser(
        description="Serveur web pour le générateur batch",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  # Lancer sur localhost:5000 (défaut)
  python batch_server.py
  
  # Lancer sur un port personnalisé
  python batch_server.py --port 8080
  
  # Lancer en mode production (pas recommandé)
  python batch_server.py --host 0.0.0.0
  
  # Ne pas ouvrir le navigateur automatiquement
  python batch_server.py --no-browser
        """
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port du serveur (défaut: 5000)"
    )
    
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Adresse du serveur (défaut: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Mode debug Flask"
    )
    
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Ne pas ouvrir le navigateur automatiquement"
    )
    
    args = parser.parse_args()
    
    # Get project root (directory of this script)
    project_root = Path(__file__).parent.resolve()
    
    # Create and run app
    app = create_app(str(project_root))
    
    # Configure le gestionnaire de signal pour Ctrl+C
    setup_signal_handler()
    
    # URL du serveur
    server_url = f"http://{args.host}:{args.port}"
    
    print(f"""
╔════════════════════════════════════════════════════════════════╗
║          🚀 Serveur Batch Génération Audio                     ║
╚════════════════════════════════════════════════════════════════╝

🌐 Accédez à l'interface sur:
   {server_url}

💡 Pour arrêter le serveur: Appuyez sur Ctrl+C

📝 Interface: {project_root}/batch_ui.html
🔧 Serveur: {project_root}/batch_server.py
    """)
    
    # Ouvrir le navigateur automatiquement (sauf si --no-browser)
    if not args.no_browser:
        open_browser(server_url)
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=args.debug
        )
    except KeyboardInterrupt:
        print("\n\n👋 Arrêt du serveur...")
        sys.exit(0)


if __name__ == '__main__':
    main()
