def register_routers():

    from fastapi import APIRouter
    from fastapi.sse import EventSourceResponse
    from pydantic import BaseModel

    router = APIRouter()

    class Item(BaseModel):
        name: str
        description: str | None


    items = [
        Item(name="Plumbus", description="A multi-purpose household device."),
        Item(name="Portal Gun", description="A portal opening device."),
        Item(name="Meeseeks Box", description="A box that summons a Meeseeks."),
    ]

    @router.get("/api/v1/messages", response_class=EventSourceResponse)
    async def sse_stream_messages():
        for item in items:
            yield item

    return router



def create_app():

    from fastapi import FastAPI
    app = FastAPI()

    app.include_router(register_routers())

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app

app = create_app()