NATURAL_QUERY_TO_KEY_DESCRIPTION_PROMPT = """You are given a question that queries a set of documents. Your task is to determine the relevant keys (or columns) that should be extracted from the documents to create a structured table.

### Instructions:
1. Understand the Question: Analyze the given question to determine the core information it seeks from the documents.
2. Analyze the Documents: Identify the key pieces of information that are relevant to answering the question and structuring the data.
3. Determine Keys: Extract a list of key attributes that should be included in the structured table. Each key should be:
   - Relevant: Directly related to the question and the document content.
   - Distinct: Avoid redundancy by ensuring each key represents a unique piece of information.
   - Structured: Ensure the keys are structured in a way that enables easy data processing and tabular representation.
4. Provide a Description: For each key, provide a brief description explaining its purpose and the type of data it holds.
5. Keep the keys such that the question can be converted to an SQL style query using the derived keys to answer the question.
6. Do not mention filtering criteria or question specific conditions in description itself.
7. Remember this key-description will be sent to another prompt to extract the values for these keys from the documents. So keep the keys generic and not specific to the input question.
8. Try to keep the datatypes of values simple: mostly as string, numbers, etc and not complex types like list, json so querying is easy and fast. Better to have more keys than to try and fit everything in one key.
9. Speak about datatype as well in the description.

Input query:
```
{natural_query}
```

### Output Format:
key: <Yey that needs to be extracted. Do not keep spaces, use underscore if needed.>
description: <Description about that key, its type and what it represents>
utilized for: <How it can be utilized to address the query>

key: <Yey that needs to be extracted. Do not keep spaces, use underscore if needed.>
description: <Description about that key, its type and what it represents>
utilized for: <How it can be utilized to address the query>

key: <Yey that needs to be extracted. Do not keep spaces, use underscore if needed.>
description: <Description about that key, its type and what it represents>
utilized for: <How it can be utilized to address the query>"""


EXTRACT_INFORMATION_FROM_TEXT_PROMPT = """Following is the text extracted from a PDF. It may or may not be properly structured since it is converted to text. Your job is to extract (key, value) information pairs. The description of keys we want to extract values for is given below

Today's date is {today_date} for your reference.

IMPORTANT: Stick to the datatypes mentioned in the description. If it is numeric only add numbers and do not put units against it becaue it will be converted to that data type.

```
{key_value_descriptions}
```

The output format MUST follow the following pattern:
<key>: <value>
<key>: <value>
<key>: <value>

If value extraction is not possible or not available for any key, then just give "null" as the value for that key.

Input PDF text:
```
{pdf_text}
```"""


NATURAL_QUERY_TO_PANDAS_QUERY_PROMPT = """You are given a natural language query and the first few rows of a pandas DataFrame. Your task is to generate a valid pandas `.query()` string that will be passed directly to `df.query()`. The output should strictly be the query string without additional explanations.

**Input format:**
- **Query:** A natural language request describing the filtering condition.
- **DataFrame Head:** The first 5 rows of the DataFrame converted to a dictionary using `df.head(5).to_dict()`.

**Output format:**
- A valid pandas `.query()` string without additional quotes or formatting. Just put the query between backticks `<query>`. Do not give any explanation or context, just the query.

IMPORTANT: all fields in df are string, so use astype in query if any other type is needed for comparison. Dont forget to add proper quotes around datatype in astype. Also handle null values properly in query.

Input Query:
```
{natural_query}
```

Input DataFrame Head:
```
{df_details}
```"""
