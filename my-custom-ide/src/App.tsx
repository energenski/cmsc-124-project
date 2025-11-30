import { useState, useRef, useEffect } from "react";
import Editor from "@monaco-editor/react";
import ResizablePane from "./components/ResizablePane";
import ResizableSidebar from "./components/ResizableSidebar";
import { io } from "socket.io-client";

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
  const [sidebarWidth, setSidebarWidth] = useState(300);
  const [symbolTable, setSymbolTable] = useState<Record<string, any>>({});

  // Socket connection
  const [socket] = useState(() => io("http://localhost:5000"));

  const fileInputRef = useRef<HTMLInputElement>(null);
  const terminalEndRef = useRef<HTMLDivElement>(null);

  const activeCode = files.find((f) => f.name === activeFile)?.code || "";

  useEffect(() => {
    socket.on("connect", () => {
      console.log("Connected to server");
    });

    socket.on("terminal_output", (data) => {
      setOutput((prev) => prev + data.output);
    });

    socket.on("symbol_table", (data) => {
      try {
        const table = JSON.parse(data.table);
        setSymbolTable(table);
      } catch (e) {
        console.error("Failed to parse symbol table", e);
      }
    });

    socket.on("process_finished", () => {
      setIsRunning(false);
      setOutput((prev) => prev + "\n> Done.\n");
    });

    return () => {
      socket.off("connect");
      socket.off("terminal_output");
      socket.off("symbol_table");
      socket.off("process_finished");
    };
  }, [socket]);

  // Auto-scroll to bottom of terminal
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [output]);

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

  const runCode = (mode: "lexer" | "syntax" | "semantics") => {
    setIsRunning(true);
    setOutput(""); // Clear output
    setSymbolTable({}); // Clear symbol table
    socket.emit("run_code", { code: activeCode, mode });
  };

  const handleTerminalInput = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      const input = e.currentTarget.value;
      socket.emit("submit_input", { input });
      setOutput((prev) => prev + input + "\n"); // Echo locally
      e.currentTarget.value = "";
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
        <div className="editor-wrapper" style={{ display: 'flex', flexDirection: 'row' }}>
          <div style={{ flex: 1, minWidth: 0 }}>
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
          <ResizableSidebar width={sidebarWidth} setWidth={setSidebarWidth}>
            <div className="symbol-table-container">
              <div className="symbol-table-header">Symbol Table</div>
              <div className="symbol-table-content">
                <table className="st-table">
                  <thead>
                    <tr>
                      <th>Variable</th>
                      <th>Value</th>
                      <th>Type</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(symbolTable).length === 0 ? (
                      <tr>
                        <td colSpan={3} style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                          No variables
                        </td>
                      </tr>
                    ) : (
                      Object.entries(symbolTable).map(([name, info]) => (
                        <tr key={name}>
                          <td>{name}</td>
                          <td>{String(info.value)}</td>
                          <td>{info.type}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </ResizableSidebar>
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
              <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontFamily: 'inherit' }}>
                {output}
              </pre>
              {isRunning && (
                <div className="terminal-input-line">
                  <span className="terminal-prompt">{">"}</span>
                  <input
                    type="text"
                    className="terminal-input"
                    onKeyDown={handleTerminalInput}
                    placeholder="Type input here..."
                    autoFocus
                  />
                </div>
              )}
              <div ref={terminalEndRef} />
            </div>
          </div>
        </ResizablePane>
      </div>
    </div>
  );
}

export default App;
