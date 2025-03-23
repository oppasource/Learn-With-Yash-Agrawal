import streamlit as st

from langgraph_workflow import build_graph

# Initialize session state
if "final_report_generated" not in st.session_state:
    st.session_state["final_report_generated"] = False
    st.session_state["stream_data"] = []
    st.session_state["final_markdown_report"] = ""
    st.session_state["search_results"] = []


# Function to simulate streaming of data
def fetch_results_streaming(query):
    for chunk in build_graph().stream(
        {
            "user_query": query,
        }
    ):
        key = list(chunk.keys())[0]

        # Case where nodes don't return any data but just go to another step
        if chunk[key] is None:
            continue

        st.session_state["stream_data"].append(chunk)

        if key == "query_planner":
            st.session_state["search_results"] += chunk["query_planner"][
                "search_results"
            ]
        elif key == "should_refine_query":
            st.session_state["search_results"] += chunk["should_refine_query"][
                "search_results"
            ]
        elif key == "final_report_generator":
            st.session_state["final_report_generated"] = True
            st.session_state["final_markdown_report"] = chunk["final_report_generator"][
                "report_markdown"
            ]
        yield


# UI Setup
st.set_page_config(page_title="Deep Research", layout="wide")
st.title("Deep Research")
query = st.text_input(
    "Enter your research query:",
)

if query:
    tab1, tab2, tab3 = st.tabs(["Steps Taken", "Final Report", "Fetched Sources"])

    with tab1:
        output_placeholder = st.empty()

        if not st.session_state["final_report_generated"]:
            for _ in fetch_results_streaming(query):
                output_placeholder.empty()  # Clear previous content

                with output_placeholder.container():

                    for step in st.session_state["stream_data"]:
                        if "query_planner" in step:
                            with st.expander(
                                "Looking into initial set of search results",
                                expanded=False,
                            ):
                                st.markdown("**Searching**")
                                queries = step["query_planner"]["search_queries"]
                                cols = st.columns(len(queries))
                                for col, query in zip(cols, queries):
                                    with col:
                                        st.markdown(f"🔍 `{query}`")

                                st.markdown("**Results**")
                                results = step["query_planner"]["search_results"]
                                cols = st.columns(len(results))
                                for col, result in zip(cols, results):
                                    with col:
                                        st.markdown(
                                            f"[{result['title']}]({result['href']})"
                                        )

                        elif "should_refine_query" in step:
                            with st.expander(
                                "Refining search queries based on findings till now",
                                expanded=False,
                            ):
                                st.markdown("**Searching**")
                                queries = step["should_refine_query"]["search_queries"]
                                cols = st.columns(len(queries))
                                for col, query in zip(cols, queries):
                                    with col:
                                        st.markdown(f"🔍 `{query}`")

                                st.markdown("**Results**")
                                results = step["should_refine_query"]["search_results"]
                                cols = st.columns(len(results))
                                for col, result in zip(cols, results):
                                    with col:
                                        st.markdown(
                                            f"[{result['title']}]({result['href']})"
                                        )

                        elif "final_report_generator" in step:
                            with st.expander(
                                "Summarizing search results till now and generating final report",
                                expanded=False,
                            ):
                                for summary in step["final_report_generator"][
                                    "individual_page_summaries"
                                ]:
                                    st.markdown(f"- {summary}")

    with tab2:
        if st.session_state["final_report_generated"]:
            st.markdown(st.session_state["final_markdown_report"])

    with tab3:
        if st.session_state["final_report_generated"]:
            for result in st.session_state["search_results"]:
                st.write(f"- [{result['title']}]({result['href']})")
