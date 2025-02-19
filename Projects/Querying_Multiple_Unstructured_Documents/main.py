import streamlit as st
import pandas as pd
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

from utils import extract_pdf_info, get_filtered_df, generate_key_description_pairs

# Streamlit UI
st.title("Structured Querying for Multiple Unstructured Documents")
st.markdown("Upload multiple PDF files and question them across the files")

# Sidebar for inputs
with st.sidebar:
    st.header("Files Upload")
    
    uploaded_files = st.file_uploader("Upload multiple PDF files", type=["pdf"], accept_multiple_files=True)
    
    # Query input field
    st.markdown("### Query")
    query = st.text_input("Enter Query", key="query")
    
    # Submit button
    if st.button("Submit"):
        key_description_pairs = generate_key_description_pairs(query)
        st.session_state.key_descriptions = key_description_pairs
        
        extracted_info = extract_pdf_info(uploaded_files, key_description_pairs)
        
        if extracted_info:
            st.session_state.df = pd.DataFrame(extracted_info)

            df_query, filtered_df = get_filtered_df(st.session_state.df, query)
            st.session_state.df_query = df_query

            st.session_state.filtered_df = filtered_df
        else:
            st.error("No data extracted. Please upload valid PDF files.")
    
    # Display key-description pairs
    if "key_descriptions" in st.session_state:
        st.markdown("---")
        st.markdown("### Generated Key-Description Pairs")
        for key, description in st.session_state.key_descriptions:
            st.write(f"**{key}:** {description}")

    if "df_query" in st.session_state:
        st.markdown("---")
        st.markdown("### Generated DataFrame Query")
        st.code(st.session_state.df_query)

# Display DataFrame when generated
dataframe_placeholder = st.empty()
if "df" in st.session_state:
    st.header("Complete DataFrame")
    dataframe_placeholder.dataframe(st.session_state.df, use_container_width=True)

# Display DataFrame when generated
dataframe_placeholder = st.empty()
if "filtered_df" in st.session_state:
    st.header("Filtered DataFrame")
    dataframe_placeholder.dataframe(st.session_state.filtered_df, use_container_width=True)