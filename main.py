import os
import re
from io import BytesIO

import httpx
import uvicorn
import urllib.parse
from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from PIL import Image

# 1. 配置 Headers
HEADERS = {
    "Referer": "https://jable.tv/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


# 2. 全局客户端生命周期管理 (避免连接过多)
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(
        headers=HEADERS,
        timeout=httpx.Timeout(20.0, connect=10.0),
        follow_redirects=True,
        limits=httpx.Limits(max_connections=100)
    )
    yield
    await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)

# 3. 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/proxy-img")
async def proxy_img(url: str = Query(...)):
    try:

        if url.endswith('preview.jpg'):
            url = url.replace('preview.jpg', '320x180/1.jpg')

        resp = await app.state.client.get(url)

        img = Image.open(BytesIO(resp.content))
        if img.mode in ("RGBA", "P"):
            img = img.convert('RGB')
        buffer = BytesIO()
        img.save(buffer, format="JPEG", optimize=True, quality=75)
        buffer.seek(0)
        return Response(content=buffer.getvalue(), media_type=resp.headers.get("Content-Type"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 核心 API (必须放在静态资源挂载之前)
# ==========================================

@app.get("/proxy-m3u8")
async def proxy_m3u8(url: str = Query(...)):
    base_url = url.rsplit('/', 1)[0]
    try:
        resp = await app.state.client.get(url)
        content = resp.text

        # 替换 Key
        def replace_key(match):
            k_url = match.group(1)
            full_k = k_url if k_url.startswith("http") else f"{base_url}/{k_url}"
            return f'URI="/proxy-ts?url={urllib.parse.quote(full_k)}"'

        content = re.sub(r'URI="([^"]+)"', replace_key, content)

        # 替换 TS
        def replace_ts(match):
            ts_url = match.group(0).strip()
            full_ts = ts_url if ts_url.startswith("http") else f"{base_url}/{ts_url}"
            return f"/proxy-ts?url={urllib.parse.quote(full_ts)}"

        content = re.sub(r"^(?!#)(.+)$", replace_ts, content, flags=re.MULTILINE)
        return Response(content=content, media_type="application/vnd.apple.mpegurl")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/proxy-ts")
async def proxy_ts(url: str = Query(...)):
    async def iter_stream():
        try:
            async with app.state.client.stream("GET", url) as r:
                async for chunk in r.aiter_bytes():
                    yield chunk
        except:
            pass

    return StreamingResponse(iter_stream(), media_type="application/octet-stream")


# ==========================================
# 静态资源与页面路径 (最后挂载)
# ==========================================

if os.path.exists("dist/assets"):
    app.mount("/assets", StaticFiles(directory="dist/assets"), name="assets")


@app.get("/")
async def read_index():
    return FileResponse("dist/index.html")


@app.get("/{catchall:path}")
async def serve_vue_app(catchall: str):
    file_path = os.path.join("dist", catchall)
    if os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse("dist/index.html")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)