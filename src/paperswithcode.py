import urllib.parse
import requests
from tqdm import tqdm


def extract_papers(query: str):
    query = urllib.parse.quote(query)
    url = f"https://paperswithcode.com/api/v1/papers/?q={query}"
    response = requests.get(url)
    response = response.json()
    count = response["count"]
    results = []
    results += response["results"]

    num_pages = count // 50
    for page in tqdm(range(2, num_pages)):
        url = f"https://paperswithcode.com/api/v1/papers/?page={page}&q={query}"
        response = requests.get(url)
        response = response.json()
        results += response["results"]
    return results
