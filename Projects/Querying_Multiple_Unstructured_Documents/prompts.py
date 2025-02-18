SYSTEM_PROMPT = """Following is the text extracted from a PDF. It may or may not be properly structured since it is converted to text. Your job is to extract (key, value) information pairs. The description of keys we want to extract values for is given below

Today's date is {today_date} for your reference.

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


NATURAL_TO_PANDAS_QUERY_PROMPT = """You are given a natural language query and the first few rows of a pandas DataFrame. Your task is to generate a valid pandas `.query()` string that will be passed directly to `df.query()`. The output should strictly be the query string without additional explanations.

**Input format:**
- **Query:** A natural language request describing the filtering condition.
- **DataFrame Head:** The first 5 rows of the DataFrame converted to a dictionary using `df.head(5).to_dict()`.

**Output format:**
- A valid pandas `.query()` string without additional quotes or formatting. Just put the query between backticks `<query>`.

Input Query:
```
{natural_query}
```

Input DataFrame Head:
```
{df_details}
```"""