import streamlit as st
import pandas as pd
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

from utils import extract_pdf_info, get_filtered_df


# Streamlit UI
st.title("Batch PDF Processing with Ollama")
st.markdown("Upload multiple PDF files and provide key-description pairs to process them.")

# Sidebar for inputs
with st.sidebar:
    st.header("Input Settings")
    uploaded_files = st.file_uploader("Upload PDF files", type=["pdf"], accept_multiple_files=True)
    
    # Dynamic key-description input fields
    if "key_descriptions" not in st.session_state:
        st.session_state.key_descriptions = [("", "")]
    
    def add_field():
        st.session_state.key_descriptions.append(("", ""))
    
    def remove_field():
        if len(st.session_state.key_descriptions) > 1:
            st.session_state.key_descriptions.pop()
    
    # Buttons side by side
    col1, col2 = st.columns(2)
    col1.button("Add Key-Description", on_click=add_field)
    col2.button("Remove Key-Description", on_click=remove_field)
    
    key_description_pairs = []
    st.markdown("### Key-Description Pairs")
    for i, (key, description) in enumerate(st.session_state.key_descriptions):
        cols = st.columns(2)
        key = cols[0].text_input(f"Key {i+1}", key, key=f"key_{i}")
        description = cols[1].text_input(f"Description {i+1}", description, key=f"desc_{i}")
        key_description_pairs.append((key, description))
    
    # Generate Data button
    if st.button("Generate Data"):
        extracted_info = extract_pdf_info(uploaded_files, key_description_pairs)
        
        if extracted_info:
            st.session_state.df = pd.DataFrame(extracted_info)
            st.session_state.filtered_df = st.session_state.df.copy()
            st.session_state.generate_data = True
        else:
            st.error("No data extracted. Please upload valid PDF files.")
    
    # Filter command input field
    st.markdown("### Filter Data")
    filter_command = st.text_input("Filter Command", key="filter_command")
    
    # Apply Filter button
    if st.button("Apply Filter") and "df" in st.session_state:
        try:
            filtered_df = get_filtered_df(st.session_state.df, filter_command)
            st.session_state.filtered_df = filtered_df
        except Exception as e:
            st.error(f"Invalid filter command: {e}")

# Display DataFrame when generated
dataframe_placeholder = st.empty()
if "filtered_df" in st.session_state:
    dataframe_placeholder.dataframe(st.session_state.filtered_df, use_container_width=True)
