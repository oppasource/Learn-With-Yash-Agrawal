# multi-ai-agent-property-marketing

This project leverages a multi-agent system to generate high-quality marketing content for property listings. It uses three distinct AI agents to create a polished markdown version of the property listing:

### 1. **Analyzer**  
   - Analyzes the provided property listing URL and critiques the content.
   - Points out areas for improvement and suggests enhancements.
   - Utilizes a scraping tool to gather website content.

### 2. **Writer**  
   - Generates an initial draft of the property listing based on the content and critiques provided by the analyzer.
   - Uses the scraped content to form the structure of the marketing material.

### 3. **Editor**  
   - Proofreads the generated draft and makes necessary changes.
   - Ensures the content is error-free and polished, producing the final markdown version for publication.

### Orchestration
   - The multi-agent flow is orchestrated using **Crew AI**, which coordinates the tasks between the agents.

