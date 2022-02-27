
# Fast API for Hello World

This is the FastAPI backend for the [HelloWorld](https://github.com/sam9111/HelloWorld) webapp which fetches news from the NewsCatcher News API and performs sentiment analysis on it using Azure Text Analytics.


## Deployment

This API has been deployed using Azure App Services and can be found here:

https://hello-world-fastapi.azurewebsites.net/


## API Reference

#### Get all news fetched every 23 hours

```
  GET /api/news
```
#### Get all data processed using text analytics

```
  GET /api/data
```

#### Get all point objects being rendered as markers in the front end

```
  GET /api/points
```


## Environment Variables

To run this project, you will need to add the following environment variables to your .env file

`API_KEY` 

Your NewsCatcherAPI key 

`AZURE_API_KEY`

Your subscription key for the Azure Text Analytics Service

`ENDPOINT`

Endpoint for the above service
## Run Locally

Clone the project

```bash
  git clone https://github.com/sam9111/HelloWorld-FastAPI
```

Go to the project directory

```bash
  cd HelloWorld-FastAPI
```

Install requirements

```bash
  pip install -r requirements.txt
```

Start the server

```bash
  uvicorn main:app --host 0.0.0.0 --reload
```


## Contributing

Contributions are always welcome!

Create an issue or a PR and I will check it out immediately.

