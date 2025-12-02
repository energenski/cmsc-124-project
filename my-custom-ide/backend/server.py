from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import subprocess
import os
import tempfile
import threading
import queue
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
CORS(app)
# Use threading mode to avoid issues with subprocess pipes on Windows without monkey patching
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store active processes: {session_id: subprocess.Popen}
active_processes = {}

# Paths
LEXER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../lexer1.py"))
SYNTAX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../syntax/syntax2.py"))
SEMANTICS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../semantics/semantics1.py"))

def stream_output(process, sid):
    """Reads stdout from the process and emits it to the client."""
    try:
        # Read character by character or line by line. 
        # Line by line is safer for buffering, but char by char is more "real-time".
        for line in iter(process.stdout.readline, ''):
            if line:
                    if "<<TOKENS>>" in line:
                        parts = line.split("<<TOKENS>>")
                        if parts[0]:
                            socketio.emit('terminal_output', {'output': parts[0]}, room=sid)
                        
                        # Check if symbol table is also in the remaining part (unlikely on same line but possible if flushed together)
                        # Actually, my semantics.py prints them on separate lines with \n, but let's be safe.
                        # The semantics.py prints \n<<TOKENS>>... and \n<<SYMBOL_TABLE>>...
                        # So they should come as separate lines usually.
                        
                        json_str = parts[1].strip()
                        if json_str:
                             socketio.emit('tokens', {'tokens': json_str}, room=sid)

                    elif "<<SYMBOL_TABLE>>" in line:
                        parts = line.split("<<SYMBOL_TABLE>>")
                        if parts[0]:
                            socketio.emit('terminal_output', {'output': parts[0]}, room=sid)
                        
                        json_str = parts[1].strip()
                        if json_str:
                            socketio.emit('symbol_table', {'table': json_str}, room=sid)
                    else:
                        socketio.emit('terminal_output', {'output': line}, room=sid)
            else:
                break
    except Exception as e:
        socketio.emit('terminal_output', {'output': f"\nError reading output: {e}\n"}, room=sid)
    finally:
        # Process ended
        socketio.emit('process_finished', {}, room=sid)
        if sid in active_processes:
            del active_processes[sid]

def stream_error(process, sid):
    """Reads stderr from the process and emits it to the client."""
    try:
        for line in iter(process.stderr.readline, ''):
            if line:
                socketio.emit('terminal_output', {'output': f"Error: {line}"}, room=sid)
            else:
                break
    except:
        pass

@socketio.on('connect')
def handle_connect():
    print(f"Client connected: {request.sid}")

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in active_processes:
        process = active_processes[sid]
        process.terminate()
        del active_processes[sid]
    print(f"Client disconnected: {sid}")

@socketio.on('run_code')
def handle_run_code(data):
    sid = request.sid
    code = data.get('code', '')
    mode = data.get('mode', 'lexer') # lexer, syntax, semantics

    if not code:
        emit('terminal_output', {'output': "No code provided.\n"})
        return

    # Kill existing process for this session if any
    if sid in active_processes:
        active_processes[sid].terminate()
        del active_processes[sid]

    # Determine script path
    script_path = LEXER_PATH
    if mode == 'syntax':
        script_path = SYNTAX_PATH
    elif mode == 'semantics':
        script_path = SEMANTICS_PATH

    # Create temp file
    # Note: We need to keep the file until the process is done. 
    # For simplicity, we'll create it and let the OS/User clean up or just leave it for now.
    # Or better, use a try/finally block in a separate thread? 
    # Actually, subprocess needs the file path.
    
    fd, temp_path = tempfile.mkstemp(suffix='.lol', text=True)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(code)

    emit('terminal_output', {'output': f"> Running {mode}...\n"})

    try:
        # Start subprocess
        # bufsize=0 for unbuffered I/O (binary mode), but we want text.
        # text=True makes it buffered by line usually.
        process = subprocess.Popen(
            ['python', '-u', script_path, temp_path], # -u for unbuffered python output
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1, # Line buffered
            encoding='utf-8'
        )
        
        active_processes[sid] = process

        # Start background threads to read output
        socketio.start_background_task(target=stream_output, process=process, sid=sid)
        socketio.start_background_task(target=stream_error, process=process, sid=sid)

    except Exception as e:
        emit('terminal_output', {'output': f"Failed to start process: {str(e)}\n"})
        if os.path.exists(temp_path):
            os.remove(temp_path)

@socketio.on('submit_input')
def handle_input(data):
    sid = request.sid
    user_input = data.get('input', '')
    
    if sid in active_processes:
        process = active_processes[sid]
        if process.poll() is None: # Process is running
            try:
                process.stdin.write(user_input + '\n')
                process.stdin.flush()
                # Echo input back to terminal so user sees what they typed
                # emit('terminal_output', {'output': user_input + '\n'}, room=sid)
            except Exception as e:
                emit('terminal_output', {'output': f"\nError writing input: {e}\n"})
        else:
            emit('terminal_output', {'output': "\nProcess is not running.\n"})

if __name__ == '__main__':
    print("Starting SocketIO server...")
    socketio.run(app, port=5000, debug=True)
