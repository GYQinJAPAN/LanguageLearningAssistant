import { useCallback, useEffect, useState } from "react";
import "./App.css";
import {
  clearHistory,
  deleteHistoryRecord,
  fetchHistory,
  fetchHistoryDetail,
  fetchSpeakingTips,
  fetchStyles,
  translateText,
} from "./services/translatorApi";

const HISTORY_PAGE_SIZE = 10;
const THEME_STORAGE_KEY = "translator-theme";

const resultModeOptions = [
  { value: "single", label: "普通模式" },
  { value: "learning", label: "学习模式" },
];

const variantLabelFallback = {
  written: "书面版",
  natural: "自然版",
  spoken: "口语版",
};

const languageOptions = [
  { value: "auto", label: "自动识别" },
  { value: "Chinese", label: "中文" },
  { value: "English", label: "英语" },
  { value: "Japanese", label: "日语" },
  { value: "Korean", label: "韩语" },
];

const themeOptions = [
  { value: "cool", label: "清爽" },
  { value: "warm", label: "暖色" },
  { value: "violet", label: "柔紫" },
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

function getNaturalVariant(variants) {
  return variants.find((variant) => variant.variant_type === "natural") || variants[0];
}

function getVariantKey(variant) {
  return variant.variant_id ?? variant.id ?? variant.variant_type;
}

function getVariantRequestId(variant) {
  return variant.variant_id ?? variant.id ?? null;
}

function isEnglishTargetLanguage(value) {
  const normalized = value?.trim();
  if (!normalized) return false;

  if (normalized === "英语" || normalized === "英文") {
    return true;
  }

  const lowered = normalized.toLowerCase().replace(/_/g, "-");
  return (
    lowered === "english" ||
    lowered === "en" ||
    lowered === "en-us" ||
    lowered === "en-gb" ||
    lowered.startsWith("english")
  );
}

function getInitialTheme() {
  if (typeof window === "undefined") {
    return "cool";
  }

  const savedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
  return themeOptions.some((item) => item.value === savedTheme) ? savedTheme : "cool";
}

function HistoryEmptyState({ title, description }) {
  return (
    <div className="history-empty-state">
      <div className="history-empty-icon">History</div>
      <strong>{title}</strong>
      {description && <span>{description}</span>}
    </div>
  );
}

function App() {
  const [theme, setTheme] = useState(getInitialTheme);
  const [text, setText] = useState("");
  const [style, setStyle] = useState("base_prompt");
  const [sourceLang, setSourceLang] = useState("auto");
  const [targetLang, setTargetLang] = useState("English");
  const [resultMode, setResultMode] = useState("single");

  const [styleOptions, setStyleOptions] = useState([]);
  const [stylesLoading, setStylesLoading] = useState(true);

  const [result, setResult] = useState("");
  const [learningVariants, setLearningVariants] = useState([]);
  const [styleApplied, setStyleApplied] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copyMessage, setCopyMessage] = useState("");

  const [speakingTipsByVariant, setSpeakingTipsByVariant] = useState({});
  const [speakingTipsLoading, setSpeakingTipsLoading] = useState({});
  const [speakingTipsError, setSpeakingTipsError] = useState({});
  const [focusedVariantKey, setFocusedVariantKey] = useState(null);
  const [tipsExpandedVariantKey, setTipsExpandedVariantKey] = useState(null);

  const [historyItems, setHistoryItems] = useState([]);
  const [historySearch, setHistorySearch] = useState("");
  const [activeHistorySearch, setActiveHistorySearch] = useState("");
  const [historyTotal, setHistoryTotal] = useState(0);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyDetailLoading, setHistoryDetailLoading] = useState(false);
  const [historyActionLoading, setHistoryActionLoading] = useState(false);
  const [historyError, setHistoryError] = useState("");
  const [selectedHistory, setSelectedHistory] = useState(null);

  useEffect(() => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(THEME_STORAGE_KEY, theme);
    }
  }, [theme]);

  const handleCycleTheme = () => {
    const currentIndex = themeOptions.findIndex((item) => item.value === theme);
    const nextTheme = themeOptions[(currentIndex + 1) % themeOptions.length];
    setTheme(nextTheme.value);
  };

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
      const items = data.items || [];
      setHistoryItems(items);
      setHistoryTotal(data.total || 0);
      setActiveHistorySearch(query.trim());
    } catch (err) {
      setHistoryError(err.message || "加载历史记录失败");
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const handleSelectHistory = useCallback(async (historyId, fallbackRecord = null) => {
    setHistoryDetailLoading(true);
    setHistoryError("");

    if (fallbackRecord) {
      setSelectedHistory(fallbackRecord);
    }

    try {
      const data = await fetchHistoryDetail(historyId);
      setSelectedHistory(data);
    } catch (err) {
      setSelectedHistory(null);
      setHistoryError(err.message || "加载历史详情失败");
    } finally {
      setHistoryDetailLoading(false);
    }
  }, []);

  useEffect(() => {
    loadStyles();
    loadHistory();
  }, [loadStyles, loadHistory]);

  useEffect(() => {
    if (historyLoading) {
      return;
    }

    if (historyItems.length === 0) {
      setSelectedHistory(null);
      return;
    }

    const selectedStillVisible = historyItems.some((item) => item.id === selectedHistory?.id);
    if (!selectedStillVisible) {
      handleSelectHistory(historyItems[0].id, historyItems[0]);
    }
  }, [handleSelectHistory, historyItems, historyLoading, selectedHistory?.id]);

  const resetSpeakingTipsState = () => {
    setSpeakingTipsByVariant({});
    setSpeakingTipsLoading({});
    setSpeakingTipsError({});
    setFocusedVariantKey(null);
    setTipsExpandedVariantKey(null);
  };

  const handleTranslate = async () => {
    if (!text.trim()) {
      setError("请输入需要翻译的内容");
      return;
    }

    setLoading(true);
    setError("");
    setResult("");
    setLearningVariants([]);
    setStyleApplied("");
    setCopyMessage("");
    resetSpeakingTipsState();

    try {
      const data = await translateText({
        text,
        style,
        source_lang: sourceLang,
        target_lang: targetLang,
        result_mode: resultMode,
      });

      const variants = data.variants || [];
      setLearningVariants(variants);
      setResult(
        resultMode === "learning" && variants.length > 0
          ? getNaturalVariant(variants).translated_text || data.translated_text || ""
          : data.translated_text || ""
      );
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

  const handleReuseHistory = (record) => {
    if (!record) return;

    setText(record.source_text || "");
    setSourceLang(record.source_lang || "auto");
    setTargetLang(record.target_lang || "English");
    setResult(record.translated_text || "");
    setLearningVariants(record.variants || []);
    setResultMode(record.variants?.length ? "learning" : "single");
    setStyleApplied(record.style_applied || "");
    setError("");
    setCopyMessage("");
    resetSpeakingTipsState();

    if (styleOptions.some((item) => item.key === record.style_requested)) {
      setStyle(record.style_requested);
    }
  };

  const handleUseVariantAsResult = (variant) => {
    setResult(variant.translated_text || "");
    setCopyMessage("");
  };

  const handleUseVariantAsInput = (variant) => {
    setText(variant.translated_text || "");
    setCopyMessage("");
  };

  const handleShowSpeakingTips = async (variant) => {
    const variantKey = getVariantKey(variant);
    const variantId = getVariantRequestId(variant);

    setFocusedVariantKey(variantKey);
    setTipsExpandedVariantKey(variantKey);

    if (!variantId || speakingTipsByVariant[variantId]) {
      return;
    }

    setSpeakingTipsLoading((current) => ({ ...current, [variantId]: true }));
    setSpeakingTipsError((current) => ({ ...current, [variantId]: "" }));

    try {
      const data = await fetchSpeakingTips(variantId);
      setSpeakingTipsByVariant((current) => ({ ...current, [variantId]: data }));
    } catch (err) {
      setSpeakingTipsError((current) => ({
        ...current,
        [variantId]: err.message || "加载口语提示失败",
      }));
    } finally {
      setSpeakingTipsLoading((current) => ({ ...current, [variantId]: false }));
    }
  };

  const handleToggleTips = (variant) => {
    const variantKey = getVariantKey(variant);
    if (tipsExpandedVariantKey === variantKey) {
      setTipsExpandedVariantKey(null);
      return;
    }

    void handleShowSpeakingTips(variant);
  };

  const handleBackToVariants = () => {
    setFocusedVariantKey(null);
    setTipsExpandedVariantKey(null);
  };

  const handleDeleteHistory = async (record) => {
    if (!record) return;

    const confirmed = window.confirm("确定要删除这条历史记录吗？此操作不可撤销。");
    if (!confirmed) return;

    setHistoryActionLoading(true);
    setHistoryError("");

    try {
      await deleteHistoryRecord(record.id);
      setHistoryItems((items) => items.filter((item) => item.id !== record.id));
      setHistoryTotal((total) => Math.max(0, total - 1));
      setSelectedHistory((current) => (current?.id === record.id ? null : current));
      await loadHistory(historySearch);
    } catch (err) {
      setHistoryError(err.message || "删除历史记录失败，可能已被移除。");
    } finally {
      setHistoryActionLoading(false);
    }
  };

  const handleClearHistory = async () => {
    const confirmed = window.confirm("确定要清空全部历史记录吗？此操作不可撤销。");
    if (!confirmed) return;

    setHistoryActionLoading(true);
    setHistoryError("");

    try {
      await clearHistory();
      setHistoryItems([]);
      setHistoryTotal(0);
      setSelectedHistory(null);
      await loadHistory(historySearch);
    } catch (err) {
      setHistoryError(err.message || "清空历史记录失败");
    } finally {
      setHistoryActionLoading(false);
    }
  };

  const historyEmptyTitle = activeHistorySearch
    ? "未找到匹配的历史记录"
    : "暂无历史记录，先完成一次翻译吧";
  const historyEmptyDescription = activeHistorySearch
    ? "换一个关键词再试试。"
    : "完成翻译后，记录会自动保存在这里。";
  const detailEmptyTitle =
    historyItems.length === 0 ? historyEmptyTitle : "选择一条历史记录查看详情";
  const detailEmptyDescription =
    historyItems.length === 0 ? historyEmptyDescription : "详情会显示原文、译文和使用的风格。";
  const showSpeakingTipsButton = resultMode === "learning" && isEnglishTargetLanguage(targetLang);
  const displayedLearningVariants =
    focusedVariantKey === null
      ? learningVariants
      : learningVariants.filter((variant) => getVariantKey(variant) === focusedVariantKey);
  const currentThemeLabel =
    themeOptions.find((item) => item.value === theme)?.label || themeOptions[0].label;

  return (
    <div className={`page theme-${theme}`}>
      <div className="background-glow glow-1"></div>
      <div className="background-glow glow-2"></div>

      <div className="card">
        <div className="header">
          <div className="header-top">
            <div className="badge">AI Translator</div>
            <button className="theme-button" type="button" onClick={handleCycleTheme}>
              主题：{currentThemeLabel}
            </button>
          </div>
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
            <label className="label">结果模式</label>
            <div className="mode-toggle" role="group" aria-label="结果模式">
              {resultModeOptions.map((item) => (
                <button
                  key={item.value}
                  className={`mode-button ${resultMode === item.value ? "is-active" : ""}`}
                  type="button"
                  onClick={() => setResultMode(item.value)}
                >
                  {item.label}
                </button>
              ))}
            </div>
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

          <button className="secondary-button" onClick={handleCopy} disabled={!result}>
            复制结果
          </button>
        </div>

        {error && <div className="error-box">{error}</div>}

        <div className="result-section">
          <div className="result-header">
            <label className="label">{resultMode === "learning" ? "当前结果" : "翻译结果"}</label>
            {styleApplied && <span className="result-tag">实际生效风格：{styleApplied}</span>}
          </div>

          <div className={`result-box ${result ? "has-result" : ""}`}>
            {result || "这里会显示翻译结果"}
          </div>

          {learningVariants.length > 0 && (
            <div className={`variant-grid ${focusedVariantKey !== null ? "is-focused" : ""}`}>
              {displayedLearningVariants.map((variant) => {
                const variantKey = getVariantKey(variant);
                const variantId = getVariantRequestId(variant);
                const isFocused = focusedVariantKey === variantKey;
                const isTipsExpanded = tipsExpandedVariantKey === variantKey;
                const tips = variantId ? speakingTipsByVariant[variantId] : null;
                const tipsError = variantId ? speakingTipsError[variantId] : "";
                const tipsLoading = variantId ? Boolean(speakingTipsLoading[variantId]) : false;

                return (
                  <div
                    className={`variant-card ${isFocused ? "is-focused" : ""}`}
                    key={variantKey}
                  >
                    <div className="variant-card-header">
                      <strong>
                        {variant.label || variantLabelFallback[variant.variant_type]}
                      </strong>
                      <span>{variant.variant_type}</span>
                    </div>
                    <p className="variant-note">{variant.short_note}</p>
                    <p className="variant-text">{variant.translated_text}</p>

                    <div className="variant-actions">
                      <button
                        className="card-action-button is-primary"
                        type="button"
                        onClick={() => handleUseVariantAsResult(variant)}
                      >
                        设为结果
                      </button>
                      <button
                        className="card-action-button is-secondary"
                        type="button"
                        onClick={() => handleUseVariantAsInput(variant)}
                      >
                        填入输入
                      </button>
                      {showSpeakingTipsButton && variantId && (
                        <button
                          className="card-action-button is-accent"
                          type="button"
                          onClick={() => handleToggleTips(variant)}
                          disabled={tipsLoading}
                        >
                          {tipsLoading ? "加载中..." : isTipsExpanded ? "收起提示" : "口语提示"}
                        </button>
                      )}
                      {isFocused && (
                        <button
                          className="card-action-button is-ghost"
                          type="button"
                          onClick={handleBackToVariants}
                        >
                          返回三版本
                        </button>
                      )}
                    </div>

                    {isFocused && isTipsExpanded && (
                      <div className="speaking-tips-panel is-focused">
                        <div className="speaking-tips-header">
                          <strong>Speak Tips</strong>
                          <span className="speaking-tips-chip">
                            {variant.label || variantLabelFallback[variant.variant_type]}
                          </span>
                        </div>

                        {tipsError ? (
                          <div className="speaking-tips-error">{tipsError}</div>
                        ) : tips ? (
                          <div className="speaking-tips-layout">
                            <div className="speaking-tips-block">
                              <span>重读词</span>
                              <div className="speaking-tips-tags">
                                {(tips.stress_words || []).map((word) => (
                                  <span className="speaking-tips-tag" key={word}>
                                    {word}
                                  </span>
                                ))}
                              </div>
                            </div>

                            <div className="speaking-tips-block">
                              <span>连读提醒</span>
                              {(tips.linking_notes || []).length > 0 ? (
                                <div className="speaking-tips-list">
                                  {tips.linking_notes.map((item) => (
                                    <div
                                      className="speaking-tips-list-item"
                                      key={`${item.phrase}-${item.tip}`}
                                    >
                                      <strong>{item.phrase}</strong>
                                      <p>{item.tip}</p>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <p className="speaking-tips-empty">暂无特别连读提醒</p>
                              )}
                            </div>

                            <div className="speaking-tips-block">
                              <span>更口语的说法</span>
                              <p>{tips.more_spoken_text}</p>
                            </div>

                            <div className="speaking-tips-block">
                              <span>小提示</span>
                              <p>{tips.note_text}</p>
                            </div>
                          </div>
                        ) : (
                          <div className="speaking-tips-empty">
                            {tipsLoading ? "口语提示加载中..." : "点击按钮查看口语提示"}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

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
            <div className="history-header-actions">
              <button
                className="secondary-button compact-button"
                onClick={() => loadHistory(historySearch)}
                disabled={historyLoading || historyActionLoading}
              >
                刷新
              </button>
              <button
                className="danger-button compact-button"
                onClick={handleClearHistory}
                disabled={historyLoading || historyActionLoading}
              >
                清空全部
              </button>
            </div>
          </div>

          <form className="history-search" onSubmit={handleHistorySearch}>
            <input
              className="history-input"
              value={historySearch}
              onChange={(event) => setHistorySearch(event.target.value)}
              placeholder="搜索原文、译文、风格或语言"
            />
            <button
              className="primary-button compact-button"
              type="submit"
              disabled={historyLoading || historyActionLoading}
            >
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
                  <div
                    key={item.id}
                    className={`history-item ${selectedHistory?.id === item.id ? "is-active" : ""}`}
                  >
                    <button
                      className="history-item-main"
                      type="button"
                      onClick={() => handleSelectHistory(item.id, item)}
                      disabled={historyActionLoading}
                    >
                      <span className="history-item-text">{makeSnippet(item.source_text)}</span>
                      <span className="history-item-meta">
                        {item.style_applied} · {formatDateTime(item.created_at)}
                      </span>
                    </button>
                    <button
                      className="history-delete-button"
                      type="button"
                      onClick={() => handleDeleteHistory(item)}
                      disabled={historyActionLoading}
                    >
                      删除
                    </button>
                  </div>
                ))
              ) : (
                <HistoryEmptyState
                  title={historyEmptyTitle}
                  description={historyEmptyDescription}
                />
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
                  {selectedHistory.variants?.length > 0 && (
                    <div className="history-variants">
                      <span>学习模式版本</span>
                      {selectedHistory.variants.map((variant) => (
                        <div className="history-variant-card" key={variant.id}>
                          <strong>
                            {variant.label || variantLabelFallback[variant.variant_type]}
                          </strong>
                          <p className="history-variant-note">{variant.short_note}</p>
                          <p>{variant.translated_text}</p>
                        </div>
                      ))}
                    </div>
                  )}
                  <button
                    className="secondary-button reuse-button"
                    onClick={() => handleReuseHistory(selectedHistory)}
                  >
                    复用这条记录
                  </button>
                  <button
                    className="danger-button reuse-button"
                    onClick={() => handleDeleteHistory(selectedHistory)}
                    disabled={historyActionLoading}
                  >
                    删除这条记录
                  </button>
                </>
              ) : (
                <HistoryEmptyState
                  title={detailEmptyTitle}
                  description={detailEmptyDescription}
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
