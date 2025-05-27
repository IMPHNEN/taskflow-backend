import uvicorn
from app.main import app

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        # Don't change this to True, because it's buggy [https://github.com/langchain-ai/langchain/issues/10475]
        reload=False
    ) 