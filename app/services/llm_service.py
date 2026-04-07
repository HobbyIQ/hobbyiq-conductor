import os

from openai import AzureOpenAI

SYSTEM_PROMPT = """You are HobbyIQ, an expert AI assistant specialising in the sports-card \
and collectibles hobby. You have deep knowledge of player prospects, card values, market \
trends, grading services (PSA, BGS, SGC), auction results, and investment considerations. \
When a collector asks whether to buy, hold, or sell a card, provide balanced, data-informed \
guidance while noting that card values can fluctuate and final decisions rest with the \
collector. Be concise, friendly, and actionable."""


def _get_client() -> AzureOpenAI:
    return AzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-02-01"),
    )


def answer_hobby_query(query: str) -> str:
    """Send *query* to Azure OpenAI and return the assistant's response text."""
    client = _get_client()
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]

    response = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ],
        temperature=0.7,
        max_tokens=512,
    )
    return response.choices[0].message.content.strip()
