import io
import PyPDF2
from openai import OpenAI
import re
import uuid

from prompts import (
    EXTRACT_INFORMATION_FROM_TEXT_PROMPT,
    NATURAL_QUERY_TO_PANDAS_QUERY_PROMPT,
    NATURAL_QUERY_TO_KEY_DESCRIPTION_PROMPT,
)

openai_client = OpenAI()

# Can either hardcode to set it to current date
today_date = "1st Feb 2022"


def generate_uuid():
    return str(uuid.uuid4())


def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        text = text.strip()
    except Exception as e:
        text = f"Error reading PDF file: {e}"
    return text


def call_llm(prompt, model="gpt-4o"):
    response = openai_client.chat.completions.create(
        model=model, messages=[{"role": "system", "content": prompt}]
    )
    response_text = response.choices[0].message.content
    return response_text


def generate_key_description_pairs(natural_query):
    natural_query_prompt = NATURAL_QUERY_TO_KEY_DESCRIPTION_PROMPT.format(
        natural_query=natural_query
    )
    natural_query_prompt_response = call_llm(natural_query_prompt)

    key_description_pairs = parse_key_description_pairs(natural_query_prompt_response)

    return key_description_pairs


def parse_key_description_pairs(response):
    pattern = r"key:\s*(.*?)\s*description:\s*(.*?)\s*utilized for:\s*(.+)"
    matches = re.findall(pattern, response, re.IGNORECASE)

    key_description = []
    for key, description, utilized_for in matches:
        key_description.append((key.strip(), description.strip()))

    return key_description


def extract_pdf_info(pdf_files, key_description_pairs):
    extracted_info_files = []

    for pdf_file in pdf_files:
        pdf_text = extract_text_from_pdf(
            io.BytesIO(pdf_file.read())
        )  # Read PDF content

        key_value_descriptions = "\n".join(
            [f"{k}: {d}" for k, d in key_description_pairs if k and d]
        )

        if key_value_descriptions.strip():
            formatted_system_prompt = EXTRACT_INFORMATION_FROM_TEXT_PROMPT.format(
                today_date=today_date,
                pdf_text=pdf_text,
                key_value_descriptions=key_value_descriptions,
            )

            response_text = call_llm(formatted_system_prompt)
            extracted_info = parse_extracted_info_form_pdf(
                response_text, key_description_pairs
            )
            extracted_info["id"] = generate_uuid()
            extracted_info["pdf_file"] = pdf_file.name
            extracted_info = {
                k: extracted_info[k]
                for k in sorted(
                    extracted_info.keys(), key=lambda x: (x != "id", x != "pdf_file")
                )
            }

            extracted_info_files.append(extracted_info)

    return extracted_info_files


def parse_extracted_info_form_pdf(output, key_description_pairs):
    expected_keys = {k for k, _ in key_description_pairs}
    parsed_data = {key: None for key in expected_keys}

    for line in output.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            if key in expected_keys:
                parsed_data[key] = value.strip()

    return parsed_data


def get_filtered_df(df, natural_query):
    df_query = ""
    natural_query_prompt = NATURAL_QUERY_TO_PANDAS_QUERY_PROMPT.format(
        natural_query=natural_query, df_details=df.head(5).to_dict()
    )
    natural_query_prompt_response = call_llm(natural_query_prompt)

    query = [
        line for line in natural_query_prompt_response.split("\n") if line != "```"
    ]

    try:
        df_query = query[0].strip("`")
        filtered_df = df.query(df_query)
    except Exception as e:
        print("ERROR")
        filtered_df = df

    return df_query, filtered_df
