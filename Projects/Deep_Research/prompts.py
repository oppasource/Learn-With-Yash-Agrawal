# Given user query generate list of search queries
generate_search_queries_prompt = """Given the user query: '{user_query}', generate a set of well-structured search queries to retrieve the most relevant information.

Guidelines:
- Identify key components of the query and determine if multiple searches are required to cover different aspects.
- Generate a logical sequence of search queries that refine and expand the results progressively.
- Ensure that the total number of search queries does not exceed {MAX_QUERY_GENERATIONS}.
- Use variations in phrasing, synonyms, and alternative search approaches where applicable to maximize coverage.
- Today's date is {current_date} for your reference if needed.

Output Format:
- Provide each search query on a new line without any additional text, explanations, or headers.
- Do no give triple backticks or any other formatting, just the query itself."""


# Given user query, search queries and search results, generate refined search queries
refine_search_queries_prompt = """For the given user query: `{user_query}`, we previously generated search queries and obtained the following search results:

Search Queries:
```
{search_queries}
```

Search Results:
```
{search_results}
```

Task:
Evaluate the search results to identify new terms, insights, or related concepts that could enhance search effectiveness. If needed, generate refined search queries to improve relevance and depth.

Guidelines:
- Identify new keywords, insights, or related concepts from the search results that may warrant additional searches.
- Generate refined search queries that enhance clarity, specificity, or breadth.
- Ensure the total number of refined queries does not exceed {MAX_QUERY_GENERATIONS}.
- Avoid redundant queries that do not meaningfully improve search outcomes.
- Today's date is {current_date} for your reference if needed.

Output Format:
- Provide each refined search query on a new line, without any additional text, explanations, or headers.
- Do no give triple backticks or any other formatting, just the query itself."""


# Given user query and search results, generate search result wise summary and final markdown report
final_report_prompt = """#### Task
Generate a concise and well-structured markdown report based on the given user query and retrieved search results. The report should synthesize key insights, highlight critical information, and present findings in a clear and actionable manner.

Additionally, provide an extremely brief 1-2 line summary for each search result, mentioning its title first. These summaries should be enclosed within `<summary>` and `</summary>` tags. After all summaries, generate the final markdown report enclosed within `<final_markdown_report>` and `</final_markdown_report>` tags.

The structure of the final report is not rigid and should be dynamically determined based on the user query. Sections and subsections should be organized logically to best present the information relevant to the query.

#### Input Parameters
- **User Query**: The original query provided by the user.
- **Search Results**: The retrieved information from the search process.

#### Output Structure
1. **Summaries of Search Results**
   - Each search result summary should start with its title.
   - Provide an extremely brief (1-2 line) summary for each result.
   - Enclose each summary within `<summary>` and `</summary>` tags.
   
   **Example Format:**
   ```
   <summary>
   "Title of the Search Result Page"
   Extremely brief summary of this search result page.
   </summary>
   ```

2. **Final Markdown Report**
   - After presenting all search result summaries, generate the final markdown report.
   - The structure of the report should be dynamically determined based on the user query.
   - Enclose the entire report within `<final_markdown_report>` and `</final_markdown_report>` tags.
   
   **Example Format:**
   ```
   <final_markdown_report>
   # Title
   ## Relevant Section Based on Query
   ...
   ## Another Relevant Section
   ...
   ## Additional Insights
   ...
   </final_markdown_report>
   ```

#### Guidelines
1. **Title & Introduction**
   - Begin with a clear, precise title that captures the report's focus.
   - Provide a brief introduction explaining the context and objective based on the user query.

2. **Dynamic Structure for Key Insights & Analysis**
   - Extract and present the most valuable insights in a structured format.
   - The report should adapt its sectioning based on the nature of the query.
   - Use comparisons, statistical insights, or noteworthy trends where applicable.
   - Keep content direct and to the point with clear subheadings.

3. **Recommendations (If Applicable)**
   - Provide actionable recommendations based on the insights gathered.
   - Suggest next steps or areas for further research if relevant.

4. **Conclusion**
   - Summarize key takeaways succinctly.
   - Reinforce the significance of findings in relation to the user's query.

#### Output Format
- The final report should be formatted in **Markdown**.
- Use appropriate **headings, bullet points, and code blocks** (if necessary) for clarity.
- Ensure the content is structured, professional, and to the point, avoiding unnecessary details.
- Present search result summaries first, followed by the dynamically structured final report.
- Cite references where necessary to support the findings in final report using the links (hrefs) of the search result pages. Do not include a references section in the report though, only cite links for claims within the report.

User Query: 
```
{user_query}
```

Search Results:
```
{search_results}
```"""
