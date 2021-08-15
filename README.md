# pdfbox

Author: Mustafa Erdogan (08.2021)

`pdfbox` is an application that you can upload your pdfs, list the uploaded pdfs and search for a word in the uploaded pdfs. The name is inspired by `dropbox` and it has no relation with `Apache pdfbox` or another application.

## usage
Run the app by `docker-compose up` command in the root directory. If you make any changes in the code, you can use `docker-compose up --build` to run with building the changes. You might need `sudo` command before like `sudo docker-compose up` depending on your docker installment on your computer.

## details
- When a pdf is uploaded, it is immediately converted to txt. When a search request comes, the txt files are used instead of the pdf files, which makes reading and processing faster.
- I didn't only check exact matches, I also look at the possible matches which may occur because of typos. After finding the matches, I sorted my matching list by exact matches and then by possible matches. Then, I return the first 3 results as the response.
- Length of the search word should be at least 4 letters, otherwise there are many unmeaningful matches which also takes too much time to process. And, it is useless to just count a letter in a document.
- When the number of uploaded pdf files are 100+ and the number of pages for those are 200+, it might take up to 10 minutes to search for a word. Usually the longer the search word, the shorter the response time.
- Files without `pdf` extension are not allowed by the system.
- `ProcessPoolExecutor` from `concurrent.futures` is used to add concurrency which makes getting a response from search endpoint faster.
- pytest is used for testing. Test cases are called before running the application with docker-compose. When you call `docker-compose up` without the `-d` command, you can see the result of the unit tests.

## deployment

I would normally use serverless Google Cloud Functions or Amazon AWS Lambda for my endpoints. In that way, I don't need to worry about the scaling, load-balancers and nginx.

## implementation choices
- I used `flask` because `flask` is an easy to use micro web framework which is very suitable for small projects like this.
- To read pdfs, I used `pdftotext` library which is very convenient to read pdf files and convert them to text. I first considered `PyPDF2` due to a previous experience but I had some problems with that library for some of the inputs that I tested.
- I used `regex` library to do a fuzzy search on text.
- I used `pytest` library for unit testing, which is a very popular library for testing.

## future improvements

- `Caching`: Caching for the search results can be done. Each pdf will have an increasing id. Since we don't have a delete option, we can use this id as the id of the last file uploaded. We cache the word with the id of the last pdf uploaded and the result. When this word is used to search among the pdfs again, we will check the last pdf uploaded when we cached this word. If there is no new upload, give the cached result as response. If there are new uploads, only search for those new uploads and compare the new results with the cached result. Update the cache for that search word. Return the new result.
- Currently I used a sync API structure for the ease of the project but an async structure can also be used. When a user makes a search request, the system starts a searching in a queue and immediately returns a link to user for where to get the result of the searching. When the results are ready, the system writes those in the location that the user got from the previous request. The user makes a polling request to the url they got from the previous request.
Search request -> (async search starts) -> result url is returned -> result is ready -> result url is requested by the user.

## Endpoints

There are 4 endpoints which are `test`, `upload`, `list` and `search`. Authentication is not required.

### test
`GET /test`. Used to test the status of the server.

#### Example

```python
import requests

response = requests.get(ROOT_URL+"/test")
```

Postman:

![test](docs_images/test.png "Postman test")

#### Success response
Code: `200`

```json
{
    "status": "running"
}
```

### upload
`PUT /upload`. Used to upload pdf files.

#### Example

```python
import requests

with open(FILE_PATH, "rb") as file:
    response = requests.put(ROOT_URL+"/upload", files={"file": file})
```

Postman:

![upload](docs_images/upload.png "Postman upload")

#### Success response
Code: `200`

```json
{
    "result": "File uploaded successfully!",
    "file_name": "test.pdf"
}
```

#### Fail responses
When the file is not put in the request:

Code: `400`
```json
{
    "error": "file not found"
}
```

When a non-pdf file is uploaded:

Code: `415`
```json
{
    "error": "Only pdf files are allowed"
}
```

### list
`GET /list` Used to list the names of the uploaded files.

#### Example

```python
import requests

response = requests.get(ROOT_URL+"/list")
```

Postman:

![list](docs_images/list.png "Postman list")

#### Success response
Code: `200`

```json
{
    "files": ["test.pdf","second_test.pdf"],
    "number_of_files": 2
}
```

### search
`POST /search` Used to search for a word in the pdf files.

#### Example

```python
import requests

data = {"word": "search"}
response = requests.post(ROOT_URL+"/search", data)
```

Postman:

![search](docs_images/search.png "Postman search")

#### Success response
Code: `200`

```json
{
    "word": "search",
    "result": [
        {
            "file_name": "second_test.pdf",
            "exact_match": 8,
            "possible_match": 9,
        },
        {
            "file_name": "test.pdf",
            "exact_match": 5,
            "possible_match": 17,
        },
        {
            "file_name": "second_test.pdf",
            "exact_match": 1,
            "possible_match": 1,
        }
    ],
}
```
#### Fail responss
When the search word is shorter than 4 letters:

Code: `400`
```json
{
    "error": "Word is too short. Use at least 4 letters"
}
```
