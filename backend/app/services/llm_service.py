from openai import AsyncOpenAI
from app.core.config import OPENAI_API_KEY

client: AsyncOpenAI = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def translate_and_rewrite(
    user_text: str,
    system_prompt: str,
) -> str:
    """
    把文本和 prompts 发给 OpenAI，然后取回模型回复
    :param user_text:str
    :param system_prompt:str
    :return:str
    """
    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
            temperature=0.7,
            max_tokens=300,
        )

        content: str = response.choices[0].message.content
        return content.strip() if content else ""

    except Exception as e:
        print(f"OpenAI API 调用失败: {e}")
        raise RuntimeError("翻译服务暂时不可用，请稍后再试。")
