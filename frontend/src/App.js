import { useState } from "react";
import "./App.css";

function App() {
  const [text, setText] = useState("");
  const [style, setStyle] = useState("base_prompt");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleTranslate = async () => {
    if (!text.trim()) {
      setError("请输入中文内容");
      return;
    }

    setLoading(true);
    setError("");
    setResult("");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/translate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: text,
          style: style,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "请求失败");
      }

      setResult(data.translated_text);
    } catch (err) {
      setError(err.message || "发生未知错误");
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result) return;

    try {
      await navigator.clipboard.writeText(result);
      alert("已复制到剪贴板");
    } catch {
      alert("复制失败，请手动复制");
    }
  };

  return (
    <div className="page">
      <div className="card">
        <h1>AI Chat Rewriter</h1>
        <p className="subtitle">把中文改写成更自然的英文聊天表达</p>

        <label className="label">输入中文</label>
        <textarea
          className="textarea"
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="例如：我今天有点累，但是还是想和你聊天。"
          rows={6}
        />

        <label className="label">语气风格</label>
        <select
          className="select"
          value={style}
          onChange={(e) => setStyle(e.target.value)}
        >
          <option value="base_prompt">基础</option>
          <option value="casual">casual</option>
          <option value="polite">polite</option>
          <option value="flirty">flirty</option>
        </select>

        <button className="button" onClick={handleTranslate} disabled={loading}>
          {loading ? "生成中..." : "转换"}
        </button>

        {error && <div className="error">{error}</div>}

        <label className="label">英文结果</label>
        <div className="result-box">
          {result || "这里会显示生成结果"}
        </div>

        <button className="copy-button" onClick={handleCopy} disabled={!result}>
          复制结果
        </button>
      </div>
    </div>
  );
}

export default App;