import json


def extract_json_payload(raw_text: str) -> object:
    """Parse a JSON object/array from the LLM output."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        starts = [index for index in (text.find("{"), text.find("[")) if index >= 0]
        if not starts:
            raise RuntimeError("学习模式返回格式无效：未找到 JSON。")

        start = min(starts)
        end = max(text.rfind("}"), text.rfind("]"))
        if end <= start:
            raise RuntimeError("学习模式返回格式无效：JSON 不完整。")

        try:
            return json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise RuntimeError("学习模式返回格式无效：无法解析 JSON。") from exc
