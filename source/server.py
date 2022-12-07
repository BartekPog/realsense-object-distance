from fastapi import FastAPI

from .depth.depth_perceptor import DepthPerceptor

app = FastAPI()

depth_perceptor = DepthPerceptor()


@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/depth")
async def root():
    return depth_perceptor.get_depth()
