import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

def build_faiss_index():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(os.path.dirname(current_dir), "data")
    index_path = os.path.join(data_folder, "ftc_faiss_index")

    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDFs found in {data_folder}. Please add files.")
        return

    print(f"Found {len(pdf_files)} PDF(s). Starting extraction...")
    
    all_chunks = []
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    for pdf_path in pdf_files:
        filename = os.path.basename(pdf_path)
        print(f"Processing: {filename}")
        
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        chunks = text_splitter.split_documents(documents)
        
        for chunk in chunks:
            chunk.metadata["platform"] = "youtube"
            chunk.metadata["source_file"] = filename
            
        all_chunks.extend(chunks)

    print(f"Generated {len(all_chunks)} text chunks. Initializing embeddings...")
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    vectorstore = FAISS.from_documents(all_chunks, embeddings)
    
    vectorstore.save_local(index_path)
    print(f"FAISS index saved to: {index_path}")

if __name__ == "__main__":
    build_faiss_index()