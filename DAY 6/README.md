# OKR Task Validator - 5 Pillar Resume Matching System

This application validates if a submitted resume document includes all 5 institutional pillars required for the OKR task. It uses a combination of text matching and RAG (Retrieval-Augmented Generation) to ensure accurate validation.

## Features

- PDF document upload and processing
- Validation of 5 institutional pillars
- Case-insensitive matching
- Clear feedback on missing pillars
- Modern Streamlit UI

## Required Pillars

1. CLT – Center for Learning and Teaching
2. CFC – Center for Creativity
3. SCD – Skill and Career Development
4. IIPC – Industrial Institute Partnership Cell
5. SRI – Social Responsive Initiative

## Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     .\venv\Scripts\Activate.ps1
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a `.env` file** in the project root with the following content:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

## Usage

1. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

2. **Open the application** in your web browser (usually at `http://localhost:8501`).

3. **Upload a PDF resume document** using the file upload widget.

4. **View the results** showing which pillars are present and which are missing.

## Troubleshooting

- **ModuleNotFoundError**: If you encounter errors like `ModuleNotFoundError: No module named 'PyPDF2'`, ensure you have installed all dependencies:
  ```bash
  pip install -r requirements.txt
  ```

- **Disk Space Issues**: If you see errors like `[Errno 28] No space left on device`, free up disk space on your drive.

- **Streamlit Not Recognized**: If the `streamlit` command is not recognized, ensure you have installed streamlit:
  ```bash
  pip install streamlit==1.32.0
  ```

## Technical Details

- Built with Streamlit for the UI
- Uses LangChain for text processing
- Implements FAISS for vector storage
- Uses sentence-transformers for embeddings

## Note

The application accepts only PDF files and performs case-insensitive matching for the pillar names. 