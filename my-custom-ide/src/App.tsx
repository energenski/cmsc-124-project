import { useState, useRef } from "react";
import Editor from "@monaco-editor/react";
import ResizablePane from "./components/ResizablePane";

import "./index.css";

interface File {
  name: string;
  code: string;
}

function App() {
  const [files, setFiles] = useState<File[]>([
    { name: "main.lol", code: "# Write your code here\n" },
  ]);
  const [activeFile, setActiveFile] = useState("main.lol");
  const [output, setOutput] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [terminalHeight, setTerminalHeight] = useState(200);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const activeCode = files.find((f) => f.name === activeFile)?.code || "";

  const updateCode = (newCode: string) => {
    setFiles((prev) =>
      prev.map((file) =>
        file.name === activeFile ? { ...file, code: newCode } : file
      )
    );
  };

  const addFile = () => {
    const newName = `file${files.length + 1}.lol`;
    setFiles([...files, { name: newName, code: "# New file\n" }]);
    setActiveFile(newName);
  };

  const runCode = async (mode: "lexer" | "syntax" | "semantics") => {
    setIsRunning(true);
    const modeName = mode.charAt(0).toUpperCase() + mode.slice(1);
    setOutput((prev) => prev + `\n> Running ${modeName} Analysis on ${activeFile}...\n`);

    let endpoint = "http://localhost:5000/run"; // Default to lexer
    if (mode === "syntax") {
      endpoint = "http://localhost:5000/run-syntax";
    } else if (mode === "semantics") {
      endpoint = "http://localhost:5000/run-semantics";
    }

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ code: activeCode }),
      });

      const data = await response.json();

      if (response.ok) {
        setOutput((prev) => prev + `> Output:\n${data.output}\n> Done.\n`);
      } else {
        setOutput((prev) => prev + `> Error:\n${data.output}\n`);
      }
    } catch (error) {
      setOutput((prev) => prev + `> Connection Error: Is the backend server running?\n${error}\n`);
    } finally {
      setIsRunning(false);
    }
  };

  const closeFile = (name: string) => {
    const remaining = files.filter((f) => f.name !== name);
    setFiles(remaining);
    if (activeFile === name && remaining.length > 0) {
      setActiveFile(remaining[0].name);
    }
  };

  //Handle file input click and read
  const handleOpenFiles = () => {
    fileInputRef.current?.click();
  };

  const handleFilesSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (!selectedFiles) return;

    const newFiles: File[] = [];

    for (const file of Array.from(selectedFiles)) {
      const content = await file.text();
      newFiles.push({ name: file.name, code: content });
    }

    // Avoid duplicates: if file already exists, overwrite its content
    setFiles((prev) => {
      const updated = [...prev];
      for (const nf of newFiles) {
        const existing = updated.find((f) => f.name === nf.name);
        if (existing) {
          existing.code = nf.code;
        } else {
          updated.push(nf);
        }
      }
      return updated;
    });

    // Set the last opened file as active
    if (newFiles.length > 0) {
      setActiveFile(newFiles[newFiles.length - 1].name);
    }

    // Reset input so reselecting the same file works again
    e.target.value = "";
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="header-title">
          <span>🐈</span> LOLCODE IDE
        </div>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={addFile}>
            <span>+</span> New File
          </button>
          <button className="btn btn-secondary" onClick={handleOpenFiles}>
            <span>📂</span> Open
          </button>
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              className="btn btn-primary"
              onClick={() => runCode("lexer")}
              disabled={isRunning}
              title="Run Lexical Analysis"
            >
              <span>{isRunning ? "⏳" : "▶️"}</span>
              Lexer
            </button>
            <button
              className="btn btn-primary"
              onClick={() => runCode("syntax")}
              disabled={isRunning}
              title="Run Syntax Analysis"
            >
              <span>{isRunning ? "⏳" : "▶️"}</span>
              Syntax
            </button>
            <button
              className="btn btn-primary"
              onClick={() => runCode("semantics")}
              disabled={isRunning}
              title="Run semantics Check"
            >
              <span>{isRunning ? "⏳" : "▶️"}</span>
              Semantics
            </button>
          </div>
        </div>

        {/* Hidden file input */}
        <input
          type="file"
          multiple
          ref={fileInputRef}
          style={{ display: "none" }}
          onChange={handleFilesSelected}
        />
      </header>

      {/* File Tabs */}
      <div className="tabs-container">
        {files.map((file) => (
          <div
            key={file.name}
            className={`tab ${file.name === activeFile ? "active" : ""}`}
            onClick={() => setActiveFile(file.name)}
          >
            <span>{file.name}</span>
            {files.length > 1 && (
              <button
                className="tab-close"
                onClick={(e) => {
                  e.stopPropagation();
                  closeFile(file.name);
                }}
                title="Close file"
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            )}
          </div>
        ))}
        <button className="tab-new" onClick={addFile} title="New File">
          +
        </button>
      </div>

      {/* Editor + Terminal */}
      <div className="main-content">
        <div className="editor-wrapper">
          <Editor
            height="100%"
            defaultLanguage="python" // keeping python for syntax highlighting approximation
            theme="vs-dark"
            value={activeCode}
            onChange={(value) => updateCode(value || "")}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              fontFamily: "'JetBrains Mono', Consolas, monospace",
              padding: { top: 16 },
              scrollBeyondLastLine: false,
            }}
          />
        </div>

        <ResizablePane
          height={terminalHeight}
          setHeight={setTerminalHeight}
          minHeight={100}
          maxHeight={500}
        >
          <div className="terminal-container" style={{ height: '100%' }}>
            <div className="terminal-header">
              Terminal Output
            </div>
            <div className="terminal-content">
              {output ? (
                <div>{output}</div>
              ) : (
                <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>
                  Ready to run code...
                </div>
              )}
            </div>
          </div>
        </ResizablePane>
      </div>
    </div>
  );
}

export default App;
