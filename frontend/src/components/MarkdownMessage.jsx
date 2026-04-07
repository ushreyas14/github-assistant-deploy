import { useMemo, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";

function CodeBlock({ className, children, inline }) {
  const [copied, setCopied] = useState(false);
  const raw = String(children || "").replace(/\n$/, "");
  const language = useMemo(() => {
    if (!className) return "text";
    return className.replace("language-", "") || "text";
  }, [className]);

  if (inline) {
    return <code className="inline-code">{children}</code>;
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(raw);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch (_error) {
      setCopied(false);
    }
  };

  return (
    <div className="code-wrap">
      <div className="code-head">
        <span>{language}</span>
        <button type="button" className="copy-btn" onClick={handleCopy}>
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre>
        <code className={className}>{raw}</code>
      </pre>
    </div>
  );
}

export default function MarkdownMessage({ content }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      rehypePlugins={[rehypeHighlight]}
      components={{
        code({ inline, className, children }) {
          return (
            <CodeBlock inline={inline} className={className}>
              {children}
            </CodeBlock>
          );
        },
      }}
    >
      {content || ""}
    </ReactMarkdown>
  );
}
