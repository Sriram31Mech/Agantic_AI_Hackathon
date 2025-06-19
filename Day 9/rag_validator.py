from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
import re
from pillars import PILLARS

# Define the pillars and their variations
PILLARS = {
    "CLT": ["Center for Learning and Teaching", "CLT"],
    "CFC": ["Center for Creativity", "CFC"],
    "SCD": ["Skill and Career Development", "SCD"],
    "IIPC": ["Industrial Institute Partnership Cell", "IIPC"],
    "SRI": ["Social Responsive Initiative", "SRI"]
}

# Define descriptions for each pillar
PILLAR_DESCRIPTIONS = {
    "CLT": "The Center for Learning and Teaching focuses on enhancing teaching methodologies and learning outcomes through innovative educational practices and faculty development programs.",
    "CFC": "The Center for Creativity promotes creative thinking and innovation across the institution, fostering an environment where students and faculty can explore and develop their creative potential.",
    "SCD": "The Skill and Career Development center helps students develop essential skills and prepare for their professional careers through various training programs and career guidance services.",
    "IIPC": "The Industrial Institute Partnership Cell facilitates collaboration between the institution and industry partners, creating opportunities for internships, research projects, and industry-academia partnerships.",
    "SRI": "The Social Responsive Initiative focuses on community engagement and social responsibility, encouraging students and faculty to contribute to society through various outreach programs and initiatives."
}

def validate_resume_pillars(text):
    """
    Validate if the resume contains all required pillars.
    Returns a dictionary with validation results including descriptions of missing pillars.
    """
    found_pillars = set()
    missing_pillars = set()
    missing_pillars_with_descriptions = {}
    
    text_lower = text.lower()
    
    # Check for each pillar and its variations
    for pillar_key, variations in PILLARS.items():
        found = False
        for variation in variations:
            if variation.lower() in text_lower:
                found_pillars.add(pillar_key)
                found = True
                break
        if not found:
            missing_pillars.add(pillar_key)
            missing_pillars_with_descriptions[pillar_key] = PILLAR_DESCRIPTIONS[pillar_key]
    
    # Prepare the result
    result = {
        "is_valid": len(missing_pillars) == 0,
        "found_pillars": sorted(list(found_pillars)),
        "missing_pillars": sorted(list(missing_pillars)),
        "missing_pillars_descriptions": missing_pillars_with_descriptions
    }
    
    return result

def create_embeddings(text):
    """
    Create embeddings for the text using sentence transformers.
    This function is prepared for future semantic search capabilities.
    """
    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    # Split the text into chunks
    chunks = text_splitter.split_text(text)
    
    # Initialize the embeddings model
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Create the vector store
    vectorstore = FAISS.from_texts(chunks, embeddings)
    
    return vectorstore 