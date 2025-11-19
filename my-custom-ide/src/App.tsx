import { useState } from "react";
import Editor from "@monaco-editor/react";
import ResizablePane from "./components/ResizablePane";
import "./index.css";

function App() {
  const [code, setCode] = useState("# Write your code here\n");
  const [output, setOutput] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [terminalHeight, setTerminalHeight] = useState(200);

  const runCode = () => {
    setIsRunning(true);
    setTimeout(() => {
      setOutput("Mock terminal output:\n$ " + code.toUpperCase());
      setIsRunning(false);
    }, 800);
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <div className="header">
        <h1>LOLCODE Interpreter</h1>
        <button onClick={runCode} disabled={isRunning}>
          {isRunning ? "Running..." : "Run"}
        </button>
      </div>

      <div style={{ flex: 1, display: "flex", flexDirection: "column", minHeight: 0 }}>
        {/* Editor grows to fill remaining space */}
        <div style={{ flex: 1, minHeight: 0 }}>
          <Editor
            height="100%"
            defaultLanguage="python"
            theme="vs-dark"
            value={code}
            onChange={(value) => setCode(value || "")}
          />
        </div>

        {/* Terminal at bottom */}
        <ResizablePane
          height={terminalHeight}
          setHeight={setTerminalHeight}
          minHeight={100}
          maxHeight={400}
        >
          <div className="output-pane">
            <div className="title">Terminal:</div>
            <pre>{output}</pre>
          </div>
        </ResizablePane>
      </div>
    </div>
  );
}

export default App;
