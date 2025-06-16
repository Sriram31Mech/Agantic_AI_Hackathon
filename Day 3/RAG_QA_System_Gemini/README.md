# RAG QA System - AI Research Papers (Gemini)

## Project Description
This project is a Retrieval-Augmented Generation (RAG) Question Answering system designed to answer questions about AI research papers. It leverages the Google Gemini 2.0 LLM via Langchain and integrates a FAISS vectorstore for efficient document retrieval. The system uses Streamlit for an interactive web interface.

## Features
- Ask questions about AI research papers and get answers with source references.
- Uses Google Gemini 2.0 generative AI model.
- Retrieves relevant document chunks using FAISS vectorstore.
- Processes PDF documents by chunking and embedding for retrieval.
- Simple Streamlit UI for easy interaction.

## Installation

1. Clone the repository or download the project files.
2. Navigate to the project directory:
   ```bash
   cd Day 3/RAG_QA_System_Gemini
   ```
3. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Environment Setup

1. Create a `.env` file in the project root directory.
2. Add your Google API key to the `.env` file:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   ```
3. Make sure the `.env` file is loaded automatically (handled by the code).

## Data Preparation

- Place your AI research paper PDFs inside the `data` folder.
- The system will load all PDFs from this folder, preprocess, and create embeddings.

## Running the Application

Start the Streamlit app by running:

```bash
streamlit run app.py
```

This will launch a web interface where you can input questions about the AI research papers and get answers with source snippets.

## Project Structure

- `app.py`: Streamlit application UI.
- `main.py`: (Not used for main logic, prints numpy version).
- `requirements.txt`: Project dependencies.
- `data/`: Folder to place PDF documents.
- `src/`:
  - `preprocess.py`: Loads PDFs, splits into chunks, and creates embeddings.
  - `retriever.py`: Loads or creates FAISS vectorstore for document retrieval.
  - `rag_pipeline.py`: Defines the QA pipeline using Google Gemini LLM and retriever.
- `vectorstore/`: Stores FAISS index files for fast retrieval.

## How It Works

1. PDFs are loaded and split into manageable chunks.
2. Chunks are embedded using sentence-transformers embeddings.
3. FAISS vectorstore indexes these embeddings for similarity search.
4. When a question is asked, the retriever fetches relevant chunks.
5. The Google Gemini LLM generates an answer based on retrieved documents.
6. The Streamlit UI displays the answer and source document snippets.

## Notes

- If the FAISS vectorstore index is missing, it will be created automatically on first run.
- Ensure your Google API key has access to the Gemini model.
- Adjust chunk size and overlap in `src/preprocess.py` if needed.

## Dependencies

- torch
- langchain
- langchain-community
- faiss-cpu
- google-generativeai
- sentence-transformers
- streamlit
- pypdf
- python-dotenv
- langchain-google-genai
- numpy==1.26.4

## License

This project is provided as-is without any warranty. Use at your own risk.
