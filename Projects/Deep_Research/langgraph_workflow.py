import operator
from typing import Annotated
from typing_extensions import TypedDict, Literal
from langgraph.graph import START, END, StateGraph
from langgraph.types import Command
from dotenv import load_dotenv
from datetime import datetime
import re

# Load environment variables
load_dotenv()

from utils import call_llm, get_search_results
from prompts import (
    generate_search_queries_prompt,
    refine_search_queries_prompt,
    final_report_prompt,
)

# Constants
MAX_QUERY_GENERATIONS = 3
MAX_RESULT_TO_FETCH = 1
MAX_QUERY_REFINEMENTS = 2


# State definition for langgraph agent workflow
class DeepResearchState(TypedDict):
    user_query: str
    search_queries: Annotated[list, operator.add]
    search_results: Annotated[list, operator.add]
    individual_page_summaries: Annotated[list, operator.add]
    report_markdown: str
    query_generation_count: int


def query_planner(state: DeepResearchState):
    user_query = state["user_query"]
    query_generation_count = state.get("query_generation_count", 0)

    current_date = datetime.today().strftime("%d %B %Y")

    search_queries_response = call_llm(
        generate_search_queries_prompt.format(
            user_query=user_query,
            current_date=current_date,
            MAX_QUERY_GENERATIONS=MAX_QUERY_GENERATIONS,
        )
    )

    search_queries = [
        q.strip().strip("'\"").strip("-").strip()
        for q in search_queries_response.split("\n")
    ]

    # Guard rails to force limit the number of queries in case llm decides to generate more
    search_queries = search_queries[:MAX_QUERY_GENERATIONS]

    consolidated_search_results = []
    for search_query in search_queries:
        search_results_per_query = get_search_results(
            search_query,
            MAX_RESULT_TO_FETCH,
            previous_search_results=consolidated_search_results,
        )
        consolidated_search_results += search_results_per_query

    return {
        "search_queries": search_queries,
        "search_results": consolidated_search_results,
        "query_generation_count": query_generation_count + 1,
    }


def should_refine_query(
    state: DeepResearchState,
) -> Command[Literal["should_refine_query", "final_report_generator"]]:
    user_query = state["user_query"]
    search_queries = state["search_queries"]
    search_results = state["search_results"]
    query_generation_count = state.get("query_generation_count", 0)

    current_date = datetime.today().strftime("%d %B %Y")

    if query_generation_count >= MAX_QUERY_REFINEMENTS:
        return Command(update={}, goto="final_report_generator")

    search_results_str = "\n===========\n".join(
        f"Title: {r['title']}\nContent: {r['text_content']}" for r in search_results
    )

    refined_search_queries_response = call_llm(
        refine_search_queries_prompt.format(
            user_query=user_query,
            current_date=current_date,
            search_queries="\n".join(search_queries),
            search_results=search_results_str,
            MAX_QUERY_GENERATIONS=MAX_QUERY_GENERATIONS,
        )
    )

    # Removed "None" instructions from prompt - can add it back if needed
    # It can optionally return "None" if no refinements are needed
    refined_search_queries = [
        q.strip().strip("'\"").strip("-").strip()
        for q in refined_search_queries_response.split("\n")
        if q.lower() != "none"
    ]

    # Guard rails to force limit the number of queries in case llm decides to generate more
    refined_search_queries = refined_search_queries[:MAX_QUERY_GENERATIONS]

    consolidated_search_results = []
    for refined_search_query in refined_search_queries:
        search_results_per_query = get_search_results(
            refined_search_query,
            MAX_RESULT_TO_FETCH,
            search_results + consolidated_search_results,
        )
        consolidated_search_results += search_results_per_query

    if refined_search_queries:
        return Command(
            update={
                "search_queries": refined_search_queries,
                "search_results": consolidated_search_results,
                "query_generation_count": query_generation_count + 1,
            },
            goto="should_refine_query",
        )
    else:
        return Command(update={}, goto="final_report_generator")


def final_report_generator(state: DeepResearchState):
    user_query = state["user_query"]
    search_results = state["search_results"]

    search_results_str = "\n===========\n".join(
        f"Title: {r['title']}\nLink:{r['href']}\nContent: {r['text_content']}"
        for r in search_results
    )

    final_report_response = call_llm(
        final_report_prompt.format(
            user_query=user_query, search_results=search_results_str
        )
    )

    # Extract summaries
    summaries = re.findall(
        r"<summary>\n(.*?)\n</summary>", final_report_response, re.DOTALL
    )

    # Extract final report
    final_report_match = re.search(
        r"<final_markdown_report>\n(.*?)\n</final_markdown_report>",
        final_report_response,
        re.DOTALL,
    )
    final_report = final_report_match.group(1) if final_report_match else ""

    return {
        "individual_page_summaries": summaries,
        "report_markdown": final_report,
    }


def build_graph():
    graph_builder = StateGraph(DeepResearchState)

    graph_builder.add_node(query_planner)
    graph_builder.add_node(should_refine_query)
    graph_builder.add_node(final_report_generator)

    graph_builder.add_edge(START, "query_planner")
    graph_builder.add_edge("query_planner", "should_refine_query")
    graph_builder.add_edge("final_report_generator", END)

    graph = graph_builder.compile()

    # Generate the graph image and save it
    graph_image_path = "graph.png"
    with open(graph_image_path, "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())

    return graph


if __name__ == "__main__":
    graph = build_graph()
    for chunk in graph.stream(
        {
            "user_query": "have we reached agi with manus ai?",
        }
    ):
        print(chunk)
