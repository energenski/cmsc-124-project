from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import tempfile

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Path to the lexer script (relative to this file)
LEXER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../lexer1.py"))

@app.route('/run', methods=['POST'])
def run_code():
    data = request.json
    code = data.get('code', '')

    if not code:
        return jsonify({"output": "No code provided."}), 400

    # Create a temporary file to store the code
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.lol', delete=False, encoding='utf-8') as temp:
        temp.write(code)
        temp_path = temp.name

    try:
        # Run the lexer script with the temporary file
        result = subprocess.run(
            ['python', LEXER_PATH, temp_path],
            capture_output=True,
            text=True,
            timeout=5  # Timeout after 5 seconds
        )
        
        output = result.stdout
        if result.stderr:
            output += "\nError:\n" + result.stderr

    except Exception as e:
        output = f"Server Error: {str(e)}"
    
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify({"output": output})

# Path to the syntax script
SYNTAX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../syntax/syntax2.py"))

@app.route('/run-syntax', methods=['POST'])
def run_syntax():
    data = request.json
    code = data.get('code', '')

    if not code:
        return jsonify({"output": "No code provided."}), 400

    with tempfile.NamedTemporaryFile(mode='w+', suffix='.lol', delete=False, encoding='utf-8') as temp:
        temp.write(code)
        temp_path = temp.name

    try:
        result = subprocess.run(
            ['python', SYNTAX_PATH, temp_path],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        output = result.stdout
        if result.stderr:
            output += "\nError:\n" + result.stderr

    except Exception as e:
        output = f"Server Error: {str(e)}"
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    return jsonify({"output": output})

if __name__ == '__main__':
    print(f"Starting server... Lexer path: {LEXER_PATH}")
    app.run(port=5000, debug=True)
