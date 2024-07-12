from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pickle
from pathlib import Path


app = FastAPI()


app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.absolute() / "static"),
    name="static",
)
templates = Jinja2Templates(directory="templates")


books = pickle.load(open('model/books.pkl','rb'))
df_for_collaborative_images = pickle.load(open('model/df_for_collaborative_book_image.pkl','rb'))
similarity_score = pickle.load(open('model/collaborative_similarity_score.pkl','rb'))
populars = pickle.load(open('model/popular_df.pkl','rb'))


# Fetching data for the All-time Favorite Books section
popular_list = populars["Book-Title"]
popular_list_images = populars["Image-URL-M"]
popular_books_with_images = [(index, book, image_url) for index, (book, image_url) in enumerate(zip(popular_list, popular_list_images))]



@app.get("/books-recommendation", response_class=HTMLResponse)
async def book_rec_page(request: Request):
    #for collaborative recommendations
    return templates.TemplateResponse(
        request=request, name="index.html", context={"book_list": books,"popular_books_with_images": popular_books_with_images})



@app.post("/books-recommendation", response_class=HTMLResponse)
async def get_book_rec(request: Request):
    response_book = await request.form()
    selected_book = response_book["selected_book"]

    recs = []
    recs_image = []

    #logic to get collaborative  recommended books
    book_index = books.index(selected_book)
    dis = similarity_score[book_index]
    book_list = sorted(list(enumerate(dis)), reverse=True, key = lambda x:x[1])[1:6]

    #for getting recommended books' names
    for i, _ in book_list:
        recs.append(books[i])

    #for getting recommended books' images
    for rec in recs:
        recs_image.append(df_for_collaborative_images[df_for_collaborative_images['Book-Title']==rec]['Image-URL-M'].values[0])

    #zipping both
    recommended_books_with_images = [(index, book, image_url) for index, (book, image_url) in enumerate(zip(recs, recs_image))]

    return templates.TemplateResponse("index.html",{"request":request,"selected_book":selected_book, "book_list": books,"popular_books_with_images": popular_books_with_images, "recommended_books_with_images": recommended_books_with_images})

