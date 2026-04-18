import { useCallback, useEffect, useState } from "react";
import "./App.css";
import {
  fetchHistory,
  fetchHistoryDetail,
  fetchStyles,
  translateText,
} from "./services/translatorApi";

const HISTORY_PAGE_SIZE = 10;

const languageOptions = [
  { value: "auto", label: "自动识别" },
  { value: "Chinese", label: "中文" },
  { value: "English", label: "英语" },
  { value: "Japanese", label: "日语" },
  { value: "Korean", label: "韩语" },
];

function formatDateTime(value) {
  if (!value) return "";

  try {
    return new Intl.DateTimeFormat("zh-CN", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(new Date(value));
  } catch {
    return value;
  }
}

function makeSnippet(value, maxLength = 72) {
  if (!value) return "";
  return value.length > maxLength ? `${value.slice(0, maxLength)}...` : value;
}

function App() {
  const [text, setText] = useState("");
  const [style, setStyle] = useState("base_prompt");
  const [sourceLang, setSourceLang] = useState("auto");
  const [targetLang, setTargetLang] = useState("English");

  const [styleOptions, setStyleOptions] = useState([]);
  const [stylesLoading, setStylesLoading] = useState(true);

  const [result, setResult] = useState("");
  const [styleApplied, setStyleApplied] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copyMessage, setCopyMessage] = useState("");

  const [historyItems, setHistoryItems] = useState([]);
  const [historySearch, setHistorySearch] = useState("");
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyDetailLoading, setHistoryDetailLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [selectedHistory, setSelectedHistory] = useState(null);

  const loadStyles = useCallback(async () => {
    setStylesLoading(true);
    setError("");

    try {
      const data = await fetchStyles();
      const styles = data.styles || [];
      setStyleOptions(styles);

      if (data.default_style) {
        setStyle(data.default_style);
      } else if (styles.length > 0) {
        setStyle(styles[0].key);
      }
    } catch (err) {
      setError(err.message || "加载风格列表失败");
    } finally {
      setStylesLoading(false);
    }
  }, []);

  const loadHistory = useCallback(async (query = "") => {
    setHistoryLoading(true);
    setHistoryError("");

    try {
      const data = await fetchHistory({
        page: 1,
        pageSize: HISTORY_PAGE_SIZE,
        q: query,
      });
      setHistoryItems(data.items || []);
      setHistoryTotal(data.total || 0);
    } catch (err) {
      setHistoryError(err.message || "加载历史记录失败");
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStyles();
    loadHistory();
  }, [loadStyles, loadHistory]);

  const handleTranslate = async () => {
    if (!text.trim()) {
      setError("请输入需要翻译的内容");
      return;
    }

    setLoading(true);
    setError("");
    setResult("");
    setStyleApplied("");
    setCopyMessage("");

    try {
      const data = await translateText({
        text,
        style,
        source_lang: sourceLang,
        target_lang: targetLang,
      });

      setResult(data.translated_text || "");
      setStyleApplied(data.style_applied || "");
      await loadHistory(historySearch);
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
      setCopyMessage("已复制到剪贴板");
      setTimeout(() => setCopyMessage(""), 2000);
    } catch {
      setCopyMessage("复制失败，请手动复制");
      setTimeout(() => setCopyMessage(""), 2000);
    }
  };

  const handleHistorySearch = async (event) => {
    event.preventDefault();
    await loadHistory(historySearch);
  };

  const handleSelectHistory = async (historyId) => {
    setHistoryDetailLoading(true);
    setHistoryError("");

    try {
      const data = await fetchHistoryDetail(historyId);
      setSelectedHistory(data);
    } catch (err) {
      setHistoryError(err.message || "加载历史详情失败");
    } finally {
      setHistoryDetailLoading(false);
    }
  };

  const handleReuseHistory = (record) => {
    if (!record) return;

    setText(record.source_text || "");
    setSourceLang(record.source_lang || "auto");
    setTargetLang(record.target_lang || "English");
    setResult(record.translated_text || "");
    setStyleApplied(record.style_applied || "");
    setError("");
    setCopyMessage("");

    if (styleOptions.some((item) => item.key === record.style_requested)) {
      setStyle(record.style_requested);
    }
  };

  return (
    <div className="page">
      <div className="background-glow glow-1"></div>
      <div className="background-glow glow-2"></div>

      <div className="card">
        <div className="header">
          <div className="badge">AI Translator</div>
          <h1>多语言聊天翻译助手</h1>
          <p className="subtitle">
            把原文转换成更自然、更符合目标语言表达习惯的内容。
          </p>
        </div>

        <div className="section">
          <label className="label">输入内容</label>
          <textarea
            className="textarea"
            value={text}
            onChange={(event) => setText(event.target.value)}
            placeholder="例如：我今天有点累，但是还是想和你聊天。"
            rows={7}
          />
          <div className="helper-text">
            支持自定义风格、多语言翻译和自然表达润色。
          </div>
        </div>

        <div className="grid">
          <div className="field">
            <label className="label">翻译风格</label>
            <select
              className="select"
              value={style}
              onChange={(event) => setStyle(event.target.value)}
              disabled={stylesLoading}
            >
              {stylesLoading ? (
                <option value="">加载中...</option>
              ) : styleOptions.length > 0 ? (
                styleOptions.map((item) => (
                  <option key={item.key} value={item.key}>
                    {item.label}
                  </option>
                ))
              ) : (
                <option value="base_prompt">Base Prompt</option>
              )}
            </select>
          </div>

          <div className="field">
            <label className="label">源语言</label>
            <select
              className="select"
              value={sourceLang}
              onChange={(event) => setSourceLang(event.target.value)}
            >
              {languageOptions.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>

          <div className="field">
            <label className="label">目标语言</label>
            <select
              className="select"
              value={targetLang}
              onChange={(event) => setTargetLang(event.target.value)}
            >
              {languageOptions
                .filter((item) => item.value !== "auto")
                .map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
            </select>
          </div>
        </div>

        <div className="action-row">
          <button
            className="primary-button"
            onClick={handleTranslate}
            disabled={loading || stylesLoading}
          >
            {loading ? "生成中..." : "开始翻译"}
          </button>

          <button
            className="secondary-button"
            onClick={handleCopy}
            disabled={!result}
          >
            复制结果
          </button>
        </div>

        {error && <div className="error-box">{error}</div>}

        <div className="result-section">
          <div className="result-header">
            <label className="label">翻译结果</label>
            {styleApplied && (
              <span className="result-tag">实际生效风格：{styleApplied}</span>
            )}
          </div>

          <div className={`result-box ${result ? "has-result" : ""}`}>
            {result || "这里会显示翻译结果"}
          </div>

          {copyMessage && <div className="copy-message">{copyMessage}</div>}
        </div>

        <div className="history-section">
          <div className="history-header">
            <div>
              <label className="label">历史记录</label>
              <p className="history-summary">
                最近 {historyItems.length} 条，匹配 {historyTotal} 条。
              </p>
            </div>
            <button
              className="secondary-button compact-button"
              onClick={() => loadHistory(historySearch)}
              disabled={historyLoading}
            >
              刷新
            </button>
          </div>

          <form className="history-search" onSubmit={handleHistorySearch}>
            <input
              className="history-input"
              value={historySearch}
              onChange={(event) => setHistorySearch(event.target.value)}
              placeholder="搜索原文、译文、风格或语言"
            />
            <button className="primary-button compact-button" type="submit">
              搜索
            </button>
          </form>

          {historyError && <div className="error-box">{historyError}</div>}

          <div className="history-layout">
            <div className="history-list">
              {historyLoading ? (
                <div className="history-empty">历史记录加载中...</div>
              ) : historyItems.length > 0 ? (
                historyItems.map((item) => (
                  <button
                    key={item.id}
                    className={`history-item ${
                      selectedHistory?.id === item.id ? "is-active" : ""
                    }`}
                    onClick={() => handleSelectHistory(item.id)}
                  >
                    <span className="history-item-text">
                      {makeSnippet(item.source_text)}
                    </span>
                    <span className="history-item-meta">
                      {item.style_applied} · {formatDateTime(item.created_at)}
                    </span>
                  </button>
                ))
              ) : (
                <div className="history-empty">暂无历史记录</div>
              )}
            </div>

            <div className="history-detail">
              {historyDetailLoading ? (
                <div className="history-empty">详情加载中...</div>
              ) : selectedHistory ? (
                <>
                  <div className="history-detail-row">
                    <span>时间</span>
                    <strong>{formatDateTime(selectedHistory.created_at)}</strong>
                  </div>
                  <div className="history-detail-row">
                    <span>语言</span>
                    <strong>
                      {selectedHistory.source_lang} 到 {selectedHistory.target_lang}
                    </strong>
                  </div>
                  <div className="history-detail-row">
                    <span>风格</span>
                    <strong>
                      {selectedHistory.style_requested}
                      {selectedHistory.style_applied !== selectedHistory.style_requested
                        ? `，实际 ${selectedHistory.style_applied}`
                        : ""}
                    </strong>
                  </div>
                  <div className="history-text-block">
                    <span>原文</span>
                    <p>{selectedHistory.source_text}</p>
                  </div>
                  <div className="history-text-block">
                    <span>译文</span>
                    <p>{selectedHistory.translated_text}</p>
                  </div>
                  <button
                    className="secondary-button reuse-button"
                    onClick={() => handleReuseHistory(selectedHistory)}
                  >
                    复用这条记录
                  </button>
                </>
              ) : (
                <div className="history-empty">点击一条历史记录查看详情</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
