import os
import requests
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

# Get values from .env
PROJECT_ID = os.getenv("SANITY_PROJECT_ID")
DATASET = os.getenv("SANITY_DATASET")
API_VERSION = os.getenv("SANITY_API_VERSION")
TOKEN = os.getenv("SANITY_TOKEN")
headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def get_all_articles():
    query = """
    *[_type == "article"]{
        title,
        "slug": slug.current,
        excerpt,
        category,
        subcategory,
        "heroImageUrl": heroImage.asset->url,
        featured,
        tags
    }
    """

    url = (
        f"https://{PROJECT_ID}.api.sanity.io/"
        f"v{API_VERSION}/data/query/{DATASET}"
    )

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    params = {
        "query": query
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )


    data = response.json()
    return data["result"]



def get_article_by_slug(slug):

    query = """
    *[_type == "article" && slug.current == $slug][0]{
        title,
        "slug": slug.current,
        excerpt,
        category,
        subcategory,
        "heroImageUrl": heroImage.asset->url,
        content,
        featured,
        tags
    }
    """

    url = (
        f"https://{PROJECT_ID}.api.sanity.io/"
        f"v{API_VERSION}/data/query/{DATASET}"
    )

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    params = {
        "query": query,
        "$slug": f'"{slug}"'
    }
    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    return response.json()