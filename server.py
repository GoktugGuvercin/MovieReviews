from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from transformers import pipeline

# Movie Review Model
model = pipeline("sentiment-analysis", model="goktug14/bert_imdb")

# FastAPI Application
app = FastAPI()

# Point FastAPI to the 'templates' directory
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """ Serves the root page. """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/predict-form", response_class=HTMLResponse)
async def predict_form_page(request: Request):
    """ Serves the page with the prediction form. """
    return templates.TemplateResponse("predict_form.html", {"request": request})


@app.post("/predict", response_class=HTMLResponse)
async def predict(request: Request, review: str = Form(...)):
    """ Serves generating the predictions of the reviews. """
    prediction = model(review)[0]
    label = prediction["label"]
    score = prediction["score"]

    # Return the same template, now including prediction results
    return templates.TemplateResponse(
        "predict_form.html",
        {
            "request": request,
            "pred_label": label,
            "pred_score": round(score * 100, 2),
            "review": review
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
