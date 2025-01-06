import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from starlette.middleware.cors import CORSMiddleware

from apis.users import user_router
from apis.posts import post_router
from apis.quests import quest_router
from apis.meetings import meetings_router

app = FastAPI()


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="",
        version="1.1.1",
        description="",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "cookieAuth": {"type": "apiKey", "in": "cookie", "name": "access_token"}
    }

    openapi_schema["security"] = [{"cookieAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
app.include_router(user_router)
app.include_router(post_router)
app.include_router(quest_router)
app.include_router(meetings_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["http://localhost:3000", "https://jgtower.com"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
