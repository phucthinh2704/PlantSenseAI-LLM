// components/TypewriterMarkdown.jsx
import React, { useEffect, useMemo, useRef, useState } from "react";
import MarkdownFormatter from "@components/MarkdownFormatter";

/**
 * Hiển thị text kiểu “gõ chữ”.
 * - speed: ms/ ký tự
 * - pauseOnPunctuation: tạm dừng ngắn khi gặp . , ; : ! ?
 * - onDone: callback khi gõ xong
 */
export default function TypewriterMarkdown({
  text = "",
  speed = 18,
  pauseOnPunctuation = true,
  className,
  onDone,
}) {
  const [visible, setVisible] = useState("");
  const iRef = useRef(0);
  const runningRef = useRef(false);

  const sigil = useMemo(() => new Set([".", ",", ";", ":", "!", "?", "…"]), []);

  useEffect(() => {
    setVisible("");
    iRef.current = 0;
    runningRef.current = true;

    const tick = () => {
      if (!runningRef.current) return;
      if (iRef.current >= text.length) {
        runningRef.current = false;
        onDone?.();
        return;
      }

      // Thêm 1–2 ký tự/nhịp cho mượt hơn
      const step = text[iRef.current] === "\n" ? 1 : 2;
      const next = Math.min(iRef.current + step, text.length);
      setVisible(text.slice(0, next));
      iRef.current = next;

      // Delay cơ bản
      let delay = speed;

      // Tạm dừng ngắn ở dấu câu để tự nhiên hơn
      if (pauseOnPunctuation) {
        const ch = text[next - 1];
        if (sigil.has(ch)) delay += 120;
        if (ch === "\n") delay += 80;
      }

      timer = setTimeout(tick, delay);
    };

    let timer = setTimeout(tick, speed);
    return () => {
      runningRef.current = false;
      clearTimeout(timer);
    };
  }, [text, speed, pauseOnPunctuation, onDone, sigil]);

  return (
    <div className={className}>
      {/* Khi chưa xong: render phần đã gõ + caret nháy */}
      <div className="relative">
        <MarkdownFormatter value={visible || "‎"} />
        {/* caret nháy */}
        <span className="ml-0.5 inline-block w-[2px] h-4 align-baseline bg-gray-500 animate-pulse" />
      </div>
    </div>
  );
}
