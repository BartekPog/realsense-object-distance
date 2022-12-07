from fastapi import FastAPI

from .depth.depth_perceptor import DepthPerceptor

app = FastAPI()

depth_perceptor = DepthPerceptor()


@app.get("/health")
async def root():
    return {"message": "Hello World"}


@app.get("/depth")
async def root():
    return depth_perceptor.get_depth()


# if __name__ == "__main__":
#     import uvicorn

#     uvicorn.run(app, host