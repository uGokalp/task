from fastapi import FastAPI
from routers import books, interactions, users
from starlette.responses import RedirectResponse

app = FastAPI(
    title="B2Metric Python Task Assignment",
    version="0.0.1",
    contact={
        "name": "Umur Gökalp",
        "email": "umur.gokalp@queensu.ca",
    },
)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(interactions.router)


@app.get("/")
def index():
    return RedirectResponse(url="/docs")
