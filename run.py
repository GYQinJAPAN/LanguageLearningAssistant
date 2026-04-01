import uvicorn
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()  # 加载 .env
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
