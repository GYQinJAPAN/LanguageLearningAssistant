const rawBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!rawBaseUrl) {
  throw new Error("缺少 VITE_API_BASE_URL，请检查前端 .env 配置");
}

export const API_BASE_URL = rawBaseUrl.replace(/\/+$/, "");

//从 Vite 环境变量读取地址
//缺失时立刻报错，方便排查
//去掉末尾多余 /，避免拼接出双斜杠