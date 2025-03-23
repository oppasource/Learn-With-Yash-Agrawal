from openai import OpenAI
import bs4, requests
from duckduckgo_search import DDGS

openai_client = OpenAI()


def call_llm(prompt, model="gpt-4o"):
    response = openai_client.chat.completions.create(
        model=model, messages=[{"role": "system", "content": prompt}]
    )
    response_text = response.choices[0].message.content
    return response_text


def get_search_results(query, max_results, previous_search_results=[]):
    # Extract hrefs from previous_search_results for comparison
    visited_hrefs = {result["href"] for result in previous_search_results}

    # Retrieve max_results + len(previous_search_results) to account for duplicates
    retrieved_search_results = DDGS().text(
        query, max_results=max_results + len(previous_search_results)
    )

    # Filter out already visited pages - worst case we will still get max_results if all are visited
    new_search_results = [
        result
        for result in retrieved_search_results
        if result["href"] not in visited_hrefs
    ]

    # Limit the max results after filtering to max_results and some minor room - this is needed as we get many results if len of previous_search_results is high
    new_search_results = new_search_results[: max_results + 1]

    # Can make this loop execute in parallel for faster results
    for retrieved_search_result in new_search_results:
        try:
            response = requests.get(
                retrieved_search_result["href"], headers={"User-Agent": "Mozilla/5.0"}
            )
            soup = bs4.BeautifulSoup(response.text, "lxml")
            text_content = soup.body.get_text(" ", strip=True)
            # Limit the text content in case we encounter a large page
            retrieved_search_result["text_content"] = text_content[:2000]
        except:
            retrieved_search_result["text_content"] = retrieved_search_result["body"]

    return new_search_results
