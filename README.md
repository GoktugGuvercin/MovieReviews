

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



## Docker

Deploying applications across different computing environments often leads to inconsistencies and compatibility issues. Containerization offers a robust solution to address this issue by packaging the application along with its necessary dependencies into a self-contained unit. In that way, it guarantees a consistent execution regardless of the underlying infrastructure (systems and resources).

Docker, as an open platform, has revolutionized this approach in which the applications are built, shared, and run easily. It creates standardized units called containers, these containers share the kernel of the host operating system, but include our application software (code), libraries, and the necessary runtimes like JVM, or python-interpreter to execute the application code depending on its programming language and dependencies. In this perspective, we can say that docker container acts like a custom-built mini computer tailored specifically for running your application to have better understanding, but this definition is more suitable for virtual machines because they are the ones that virtualizes the physical hardware, and includes a full operating system. 

### Virtual Machines versus Containers

Virtual machines virtualize physical hardware stack for each instance, and execute a full, separate operating system within your existing one. This makes them relatively heavy and resource-intensive, using large images (typically GBs) that takes minutes to boot. In contrast, docker containers share the host operating system's kernel, and only package what is exclusive to the application, which are the source code, runtime and dependencies, so virtualization happens at the application layer. That is why, docker images are far smaller (just a few MBs) and can launch in seconds, thereby providing much more lightweight solution.

When we have two separate physical computers, a problem on one computer naturally doesn't affect the other one. Virtual machines mimic this level of separation. Software crashes or viruses within a virtual machine are largely contained, protecting other VMs and the host. Therefore, their virtualization in hardware layer provide stronger isolation. Virtual machines also offer the flexibility to run different operating systems simultaneously on the same host. However, this comprehensive virtualization incurs significant performance overhead and contributes to longer startup times. On the other hand, containers isolate at the process level, which means multiple containers share the host's operating system kernel, but the processes of one container is completely isolated from those in another containers and the host. This separation is achieved by limiting what each container can see and interact with. In other words, this separation works by giving each container's processes a limited "view" of system resources, effectively confining their access to specific parts of the file system and network resources.

Docker's core functionality for container isolation was built to rely on specific features inherent to the Linux kernel, namely namespaces and cgroups. Because the kernels of macOS (Darwin) and Windows (NT) lack these identical capabilities, Docker cannot run natively on these systems and requires compatibility solutions. These solutions vary by operating system; for instance, Docker for Mac achieves this by running a hidden virtual machine that provides the necessary Linux environment where the Docker engine can operate.


### Advantages of Docker

1. A common hurdle in software development is the "work on my machine" problem: We create a software, test it on our own computer and observe that it passes through all the test cases. When it is moved to a server, the code that runs flawlessly starts to fail. Containers help to solve this problem in a way that the application is executed inside the container and that container is organized to have all dependencies which the application needs to access so that it can work. 

2. Containers supports isolated environments: Assume that you have three Python applications, each of which needs a different Python version. The containers allow you to package each app with its specific Python runtime and libraries. This ensures every application runs in its own isolated environment, guaranteed to have the exact version of Python and dependencies it requires, thus eliminating dependency conflicts on the server.
