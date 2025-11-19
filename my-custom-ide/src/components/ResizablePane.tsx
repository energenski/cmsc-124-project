import { ResizableBox } from "react-resizable";
import "react-resizable/css/styles.css";
import "../index.css"; // import CSS for handle

interface ResizablePaneProps {
  height: number;
  setHeight: (height: number) => void;
  minHeight?: number;
  maxHeight?: number;
  children: React.ReactNode;
}

export default function ResizablePane({
  height,
  setHeight,
  minHeight = 100,
  maxHeight = 600,
  children,
}: ResizablePaneProps) {
  return (
    <ResizableBox
      width={Infinity}
      height={height}
      minConstraints={[Infinity, minHeight]}
      maxConstraints={[Infinity, maxHeight]}
      axis="y"
      resizeHandles={["n"]}
      onResize={(_, { size }) => setHeight(size.height)}
      handle={<span className="resizable-handle" />}
    >
      <div style={{ height: "100%", overflow: "auto", position: "relative" }}>
        {children}
      </div>
    </ResizableBox>
  );
}
