import { useState, useRef, useEffect } from "react";

const PROMPT = "$ ";

interface TerminalProps {
  height: number;
  externalOutput?: string; // New prop for runCode results
}

export default function Terminal({ height, externalOutput }: TerminalProps) {
  const [history, setHistory] = useState<string[]>([]);
  const [commands, setCommands] = useState<string[]>([]);
  const [currentInput, setCurrentInput] = useState("");
  const [historyIndex, setHistoryIndex] = useState<number | null>(null);
  const outputRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Append external output from App
  useEffect(() => {
    if (externalOutput) {
      setHistory((prev) => [...prev, PROMPT + externalOutput]);
    }
  }, [externalOutput]);

  useEffect(() => {
    outputRef.current?.scrollTo({ top: outputRef.current.scrollHeight });
    inputRef.current?.focus();
  }, [history, currentInput]);

  const runCommand = (cmd: string) => {
    if (!cmd.trim()) {
      setHistory((prev) => [...prev, PROMPT]);
      return;
    }

    let result = "";
    const lowerCmd = cmd.trim().toLowerCase();

    if (lowerCmd === "clear") {
      setHistory([]);
      setCommands([]);
      setCurrentInput("");
      return;
    } else if (lowerCmd.startsWith("echo ")) {
      result = cmd.slice(5);
    } else {
      result = `${cmd} : Command not found`;
    }

    setHistory((prev) => [...prev, PROMPT + cmd, result]);
    setCommands((prev) => [...prev, cmd]);
    setCurrentInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      runCommand(currentInput);
      setHistoryIndex(null);
      e.preventDefault();
    } else if (e.key === "ArrowUp") {
      if (commands.length === 0) return;
      setHistoryIndex((prev) => {
        const newIndex = prev === null ? commands.length - 1 : Math.max(prev - 1, 0);
        setCurrentInput(commands[newIndex]);
        return newIndex;
      });
      e.preventDefault();
    } else if (e.key === "ArrowDown") {
      if (commands.length === 0) return;
      setHistoryIndex((prev) => {
        if (prev === null) return null;
        const newIndex = Math.min(prev + 1, commands.length - 1);
        setCurrentInput(commands[newIndex]);
        return newIndex;
      });
      e.preventDefault();
    }
  };

  return (
    <div
      style={{
        height,
        display: "flex",
        flexDirection: "column",
        backgroundColor: "#1e1e1e",
        color: "#fff",
        fontFamily: "monospace",
        fontSize: "14px",
        overflow: "hidden",
      }}
      onClick={() => inputRef.current?.focus()}
    >
      {/* Terminal Header */}
      <div
        style={{
          padding: "4px 8px",
          backgroundColor: "#2c2c2c",
          borderBottom: "1px solid #444",
          fontWeight: "bold",
          fontSize: "12px",
        }}
      >
        Terminal
      </div>

      {/* Terminal Output + Input */}
      <div
        ref={outputRef}
        style={{
          flex: 1,
          padding: "8px",
          overflowY: "auto",
          whiteSpace: "pre-wrap",
        }}
      >
        {history.map((line, idx) => (
          <div key={idx}>{line}</div>
        ))}

        {/* Current input line */}
        <div style={{ display: "flex" }}>
          <span>{PROMPT}</span>
          <input
            ref={inputRef}
            style={{
              flex: 1,
              border: "none",
              outline: "none",
              background: "transparent",
              color: "#fff",
              fontFamily: "monospace",
              fontSize: "14px",
            }}
            value={currentInput}
            onChange={(e) => setCurrentInput(e.target.value)}
            onKeyDown={handleKeyDown}
            autoFocus
          />
        </div>
      </div>
    </div>
  );
}
