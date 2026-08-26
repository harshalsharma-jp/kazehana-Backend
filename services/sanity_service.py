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


def get_article_by_slug(slug):

    # Escape the slug before putting it into GROQ
    safe_slug = slug.replace("\\", "\\\\").replace('"', '\\"')

    query = f'''
    *[_type == "article" && slug.current == "{safe_slug}"][0] {{
        title,
        "slug": slug.current,
        excerpt,
        category,
        subcategory,
        "heroImageUrl": heroImage.asset->url,
        content,
        featured,
        tags
    }}
    '''

    url = (
        f"https://{PROJECT_ID}.api.sanity.io/"
        f"v{API_VERSION}/data/query/{DATASET}"
    )

    headers = {
        "Authorization": f"Bearer {TOKEN}"
    }

    response = requests.get(
        url,
        headers=headers,
        params={
            "query": query
        }
    )

    response.raise_for_status()

    data = response.json()

    return data.get("result")
