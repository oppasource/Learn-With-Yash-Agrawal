# Querying Multiple Unstructured Documents

Querying multiple unstructured documents is particularly useful when dealing with large collections of resumes or other text-heavy files. For example, if you have a large number of resumes, you can easily search for candidates with specific years of experience or other qualifications using natural language queries.

This project is inspired by the blog post: [Hire Like a Data Scientist: How to Screen 1000 Resumes in 50 Seconds with SQL](https://www.getroe.ai/post/hire-like-a-data-scientist-how-to-screen-1000-resume-in-50-sec-with-sql).

A dataset containing PDF resumes was used for testing, which can be found here: [Kaggle Dataset](https://www.kaggle.com/datasets/sauravsolanki/hire-a-perfect-machine-learning-engineer).

## Setup Instructions

### 1. Create an Environment File
- Use the provided `.env.sample` file as a reference.
- Create a new `.env` file in the same directory.
- Add your OpenAI API key to the `.env` file.

### 2. Run the Application
To start the application, execute the following command in your terminal:
```bash
streamlit run main.py
```

### 3. Usage
- Upload multiple PDF files using the provided interface.
- Start querying the documents using natural language to extract relevant information.

