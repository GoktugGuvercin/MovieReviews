

# Model Deployment
In classical ML lifecycle, we design a data processing pipeline, train a model on this dataset and validate its performance. Nevertheless, this is only the half of the story. In order for someone other than you to be able to use this model, you need to make it accessible to general public or to other pieces of software that could interact with the model. To accomplish this, the model needs to be deployed. 

A common and effective strategy is to wrap the trained model within an API. This allows other applications to easily send data and receive predictions. We can then build and test this API, potentially using a framework like FastAPI in Python. To ensure reliable and consistent execution across different environments, the entire API with model and dependencies are packaged into a Docker container. 

## Model Storage
When preparing a trained model for production environment, it is standard practice to save it, typically using a binary format. This is driven by some key advantages:

- Efficiency: Binary formats are compact for storing large numerical weights, and significantly faster to load.

- Compatibility: Machine learning frameworks like PyTorch TensorFlow, and Scikit-Learn provide built-in ways to save (serialize) and load (deserialize) the models utilizinf optimized binary formats like .pt, .h5 and .joblib. 


## The Scope of Model Loading
For model inference, leveraging `pipeline` abstraction can simplify code complexity dramatically. With this approach, raw input is at first converted into the numerical representation by the tokenizer, then  tokenized input is passed through the trained model to generate raw outputs, and finally output logits are interpreted into meaningful predictions. By encapsulating these stages, `pipeline` provides a single cohesive workflow. We are loading the model in the global scope, so this kind of potentially time-consuming stage happens only once when FastAPI application starts, not on every request. 

## Client and Server

In HTTP context, a client is any application or program that initiates the communication by sending a request to a server. The client is always the party that starts the interaction; the server, in turn, listens for these requests, processes them, and sends back a response. Various types of applications function as HTTP clients:

- Web browsers (Chrome, Firefox, Safari) are perhaps the most common examples. When you enter a URL or click a link, your browser acts as an HTTP client, sending requests (typically GET requests) to retrieve that page’s layout composed of HTML, CSS and images. 

- Command line tools such as HTTPie and curl also serve as HTTP clients. These are freqently used by the developers for testing APIs,  debugging network interactions, and programmatically interacting with HTTP servers.

- Some programming libraries are also used within the applications to make them act as HTTP clients. Python's requests or Java's HttpClient provide the functionality needed for an application to send requests to other services, whether that's fetching data from an API or sending information to a webhook endpoint.

## FastAPI decorators and HTTP Requests

FastAPI provides many decorators to define an API structure. `@app.get("/")` is actually one of these. It tells our FastAPI application that the function defined just below will be executed to handle incoming HTTP requests, and these requests are the ones made using HTTP GET method. Decorated function is responsible for these requests if they are sent to root endpoint.

When we type https://example.com/ into your address bar and hit Enter, the browser issues a GET request for root endpoint (/). Similarly, we click an *<a href="/about">About</a>* link, the browser sends a GET request to /about. These are made by browser navigation. At this point, the server receive the request, understands the path, send back webpage content in response.

In FastAPI and HTTP analogy, GET means "Give me something, I will not send any data or change anything". On the contrary, POST, designated by `@app.post("/predict")`, sends the data to the server to be processed, but additionally server is allowed to create a respond with HTML, JSON, or anything else. In other words, you can also receive data in POST; nevertheless, this is not the main purpose of it. 

## Jinja
Jinja is a template engine used to generate HTML, XML or any other text based format, specifically returned to the user for HTTP response. We create a template text file, inject data with placeholders, construct a simple logic and run it to create a presentation (HTML), separated from your main application code. When these templates are evaluated and rendered, placeholder variables and expressions are replaced by their corresponding, actual values. 

```python
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
```

Jinja2Templates enable us to create a template engine, by `directory="templates"` we tell FastAPI to look for HTML templates inside that folder located in same directory as this python script. In the function `read_root()`, we have `response_class=HTMLResponse` to specify that the purpose of this function is to create, render and return HTML content. The core part is to return `templates.TemplateResponse()`, which handles the rendering. The dictionary that we pass while calling `TemplateResponse()` for rendering refers to the context, every key in this dictionary becomes a variable in the templates. In that way, we can pass data from python code into templates. We always need to include `"request": request` in this dictionary because it is used to generate URLs and access request data if needed:

    - You can write url inside your HTML: <a href="{{ request.url_for('predict_form_page') }}">Predict Form</a>
    - You can show current path query parameters and cookies in template via {{ request.url.path }} and {{ request.query_params.page }}


## Async vs and Regular Functions

In FastAPI, Python functions handle HTTP requests through decorators like `@app.get()` and `@app.post()`. When these functions are defined as async, they become asynchronous and non-blocking, meaning the server can continue handling other requests while waiting for slow operations to finish. This allows FastAPI to handle multiple requests efficiently and concurrently. For time-consuming tasks such as running a machine learning model, querying a database, or making API calls, it's better to define the route handler as `async def` to avoid blocking the event loop. On the other hand, for simple and fast operations that don’t involve I/O or delays, regular `def` functions are sufficient.