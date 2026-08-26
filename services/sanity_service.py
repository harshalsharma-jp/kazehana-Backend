import os
import requests
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("SANITY_PROJECT_ID")
DATASET = os.getenv("SANITY_DATASET")
API_VERSION = os.getenv("SANITY_API_VERSION")
TOKEN = os.getenv("SANITY_TOKEN")

BASE_URL = (
    f"https://{PROJECT_ID}.api.sanity.io/"
    f"v{API_VERSION}/data/query/{DATASET}"
)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}


def run_query(query, params=None):

    response = requests.get(
        BASE_URL,
        headers=HEADERS,
        params={
            "query": query,
            **(params or {})
        },
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    return data.get("result")


def get_all_articles():

    query = """
    *[_type == "article"] | order(_createdAt desc) {
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

    return run_query(query)


import requests
import json

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
        "$slug": json.dumps(slug)
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=15
    )

    print("SANITY URL:", response.url)
    print("SANITY STATUS:", response.status_code)
    print("SANITY RESPONSE:", response.text)

    response.raise_for_status()

    return response.json()
