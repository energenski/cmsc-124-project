import { ResizableBox } from "react-resizable";
import "react-resizable/css/styles.css";
import "../index.css";

interface ResizableSidebarProps {
    width: number;
    setWidth: (width: number) => void;
    minWidth?: number;
    maxWidth?: number;
    children: React.ReactNode;
}

export default function ResizableSidebar({
    width,
    setWidth,
    minWidth = 200,
    maxWidth = 600,
    children,
}: ResizableSidebarProps) {
    return (
        <ResizableBox
            width={width}
            height={Infinity}
            minConstraints={[minWidth, Infinity]}
            maxConstraints={[maxWidth, Infinity]}
            axis="x"
            resizeHandles={["w"]}
            onResize={(_, { size }) => setWidth(size.width)}
            handle={<span className="resize-handle-vertical" />}
            className="sidebar-resizable"
        >
            <div style={{ width: "100%", height: "100%", position: "relative", overflow: "hidden" }}>
                {children}
            </div>
        </ResizableBox>
    );
}
