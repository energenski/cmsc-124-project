# CMSC 124 Project: LOLCODE Custom IDE

A fully functional Integrated Development Environment (IDE) for the **LOLCODE** programming language, built as a final project for CMSC 124. This application combines a modern React-based frontend with a robust Python backend to provide a seamless coding experience, including lexical analysis, syntax parsing, and semantic execution.

## 🚀 Features

*   **Code Editor**: A rich text editor with syntax highlighting for LOLCODE.
*   **File Management**: Open `.lol` files from your local machine and save your work directly from the browser.
*   **Lexical Analysis**: View the stream of tokens generated from your code.
*   **Syntax Analysis**: Parse your code to check for syntax errors and view the symbol table.
*   **Semantic Execution**: Run your LOLCODE programs with support for:
    *   Variable declaration and assignment (`I HAS A`, `ITZ`).
    *   Arithmetic and boolean operations.
    *   Control flow (`O RLY?`, `YA RLY`, `NO WAI`, `WTF?`).
    *   Loops (`IM IN YR LOOP`).
    *   Input/Output (`VISIBLE`, `GIMMEH`).
*   **Interactive Terminal**: A real-time terminal emulator that supports standard output and interactive input via WebSockets.
*   **Responsive Design**: A modern, dark-themed UI built with TailwindCSS.

## 🛠️ Tech Stack

### Frontend
*   **Framework**: [React](https://react.dev/) (with TypeScript)
*   **Build Tool**: [Vite](https://vitejs.dev/)
*   **Styling**: [TailwindCSS](https://tailwindcss.com/)
*   **Editor**: [Monaco Editor](https://microsoft.github.io/monaco-editor/)
*   **Communication**: [Socket.IO Client](https://socket.io/)

### Backend
*   **Server**: [Flask](https://flask.palletsprojects.com/)
*   **Real-time**: [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
*   **CORS**: [Flask-CORS](https://flask-cors.readthedocs.io/)
*   **Interpreter**: Custom Python implementation for LOLCODE (Lexer, Parser, Interpreter).

## 📂 Project Structure

```
cmsc-124-project/
├── my-custom-ide/          # Main Web Application
│   ├── backend/            # Flask Server & File Dialogs
│   │   ├── server.py       # Main entry point for the backend
│   │   └── file_dialog.py  # Helper for file operations
│   ├── src/                # React Frontend Source
│   │   ├── components/     # UI Components (Editor, Terminal, etc.)
│   │   └── App.tsx         # Main Application Logic
│   └── package.json        # Frontend Dependencies
├── backend-files/          # LOLCODE Interpreter Logic
│   ├── lexer1.py           # Lexical Analyzer
│   ├── syntax2.py          # Syntax Analyzer
│   ├── semantics1.py       # Semantic Analyzer (Interpreter)
│   └── semantics_runner.py # Runner script
└── README.md               # Project Documentation
```

## ⚙️ Installation & Setup

### Prerequisites
*   **Node.js** (v16 or higher)
*   **Python** (v3.8 or higher)

### 1. Backend Setup
The backend handles the execution of LOLCODE scripts and file operations.

1.  Navigate to the backend directory:
    ```bash
    cd my-custom-ide/backend
    ```

2.  Install the required Python packages:
    ```bash
    pip install flask flask-cors flask-socketio
    ```
    *(Note: You may need to use `pip3` depending on your system configuration.)*

3.  Start the Flask server:
    ```bash
    python server.py
    ```
    The server will start on `http://0.0.0.0:5000`.

### 2. Frontend Setup
The frontend provides the user interface for the IDE.

1.  Open a new terminal and navigate to the project root:
    ```bash
    cd my-custom-ide
    ```

2.  Install Node.js dependencies:
    ```bash
    npm install
    ```

3.  Start the development server:
    ```bash
    npm run dev
    ```

4.  Open your browser and visit the URL shown in the terminal (usually `http://localhost:5173`).

## 📖 Usage Guide

1.  **Writing Code**: Type your LOLCODE program in the main editor window.
2.  **Opening Files**: Click the "Open File" button to select a `.lol` file from your computer.
3.  **Saving Files**: Click "Save File" to save your current code.
4.  **Running Code**:
    *   **Lexer**: Click "Run Lexer" to see the tokenized output.
    *   **Syntax**: Click "Run Syntax" to check for errors and view the symbol table.
    *   **Semantics**: Click "Run Semantics" to execute the program.
5.  **Terminal Interaction**:
    *   Output from `VISIBLE` statements will appear in the terminal pane.
    *   If your code uses `GIMMEH`, the terminal will wait for your input. Type your input and press Enter.

## 🐛 Troubleshooting

*   **Connection Refused**: Ensure the backend server is running (`python server.py`). If accessing from a different device, make sure your firewall allows connections to port 5000.
*   **Module Not Found**: If Python complains about missing modules, ensure you've installed `flask`, `flask-cors`, and `flask-socketio`.
*   **File Dialog Not Appearing**: The file dialog opens on the *host machine* where the backend is running. Check your taskbar if it doesn't appear on top.

## 👥 Authors

*   **Djeana Carel Briones**
*   **Angeline Cubelo**
*   **Gennalyn Soriano**
