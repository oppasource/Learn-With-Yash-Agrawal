import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils import extract_pdf_info, get_filtered_df, generate_key_description_pairs

# Streamlit UI
st.title("Querying Multiple Unstructured Documents")

# Sidebar for inputs
with st.sidebar:
    st.header("Files Upload")

    uploaded_files = st.file_uploader(
        "Upload multiple PDF files", type=["pdf"], accept_multiple_files=True
    )

    # Query input field
    st.markdown("### Query")
    query = st.text_input("Enter Query", key="query")

    # Submit button
    if st.button("Submit"):
        key_description_pairs = generate_key_description_pairs(query)
        st.session_state.key_descriptions = key_description_pairs

    # Display key-description pairs
    if "key_descriptions" in st.session_state:
        st.markdown("---")
        st.markdown("### Generated Key-Description Pairs")

        for key, description in st.session_state.key_descriptions:
            with st.expander(f"**{key}**"):
                st.write(description)

        extracted_info = extract_pdf_info(
            uploaded_files, st.session_state.key_descriptions
        )

        if extracted_info:
            st.session_state.df = pd.DataFrame(extracted_info)
        else:
            st.error("No data extracted. Please upload valid PDF files.")

    query_placeholder_design_1 = st.empty()
    query_placeholder_design_2 = st.empty()
    query_placeholder = st.empty()

# Display DataFrame when generated
if "df" in st.session_state:
    st.header("Complete DataFrame")
    st.dataframe(st.session_state.df, use_container_width=True)

    df_query, filtered_df = get_filtered_df(st.session_state.df, query)

    st.session_state.filtered_df = filtered_df

    query_placeholder_design_1.markdown("---")
    query_placeholder_design_2.markdown("### Generated DataFrame Query")
    query_placeholder.code(df_query)


# Display DataFrame when generated
if "filtered_df" in st.session_state:
    st.header("Filtered DataFrame")
    st.dataframe(st.session_state.filtered_df, use_container_width=True)
