"""
Data Loader and Vector Store Module for Pokémon RAG System
This module handles loading Pokémon data from CSV/Excel and creating a vector store for RAG.
"""

import os
import pandas as pd
from typing import List, Optional
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PokemonDataLoader:
    """Handles loading and processing Pokémon dataset for RAG."""

    def __init__(self, persist_directory: str = "./vectordb"):
        """
        Initialize the data loader.

        Args:
            persist_directory: Directory to persist the vector database
        """
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.embeddings = None
        self.df = None

    def load_embeddings(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Load the embedding model.

        Args:
            model_name: Name of the HuggingFace embedding model
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        logger.info("Embedding model loaded successfully")

    def load_pokemon_data(self, file_path: str) -> pd.DataFrame:
        """
        Load Pokémon data from CSV or Excel file.

        Args:
            file_path: Path to the data file

        Returns:
            DataFrame containing the Pokémon data
        """
        logger.info(f"Loading Pokémon data from: {file_path}")

        if file_path.endswith('.csv'):
            self.df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            self.df = pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or Excel.")

        logger.info(f"Loaded {len(self.df)} Pokémon entries")
        return self.df

    def create_documents(self) -> List[Document]:
        """
        Convert DataFrame rows into LangChain Document objects.

        Returns:
            List of Document objects
        """
        if self.df is None:
            raise ValueError("No data loaded. Call load_pokemon_data first.")

        documents = []

        for idx, row in self.df.iterrows():
            # Create a descriptive text for each Pokémon
            text_parts = []

            # Add all column information
            for col in self.df.columns:
                value = row[col]
                if pd.notna(value):
                    text_parts.append(f"{col}: {value}")

            # Combine into a single text
            content = " | ".join(text_parts)

            # Create Document with metadata
            doc = Document(
                page_content=content,
                metadata={
                    "source": "pokemon_dataset",
                    "row_index": idx,
                    **{col: str(row[col]) for col in self.df.columns if pd.notna(row[col])}
                }
            )
            documents.append(doc)

        logger.info(f"Created {len(documents)} documents from dataset")
        return documents

    def create_vector_store(self, documents: List[Document], force_recreate: bool = False):
        """
        Create or load vector store from documents.

        Args:
            documents: List of Document objects
            force_recreate: If True, recreate the vector store even if it exists
        """
        if self.embeddings is None:
            self.load_embeddings()

        # Check if vector store already exists
        if os.path.exists(self.persist_directory) and not force_recreate:
            logger.info("Loading existing vector store")
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
        else:
            logger.info("Creating new vector store")
            # Create new vector store
            self.vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=self.persist_directory
            )
            self.vectorstore.persist()
            logger.info("Vector store created and persisted")

    def get_retriever(self, search_kwargs: Optional[dict] = None):
        """
        Get a retriever from the vector store.

        Args:
            search_kwargs: Optional search parameters (e.g., {'k': 5})

        Returns:
            Retriever object
        """
        if self.vectorstore is None:
            raise ValueError("Vector store not initialized. Call create_vector_store first.")

        if search_kwargs is None:
            search_kwargs = {'k': 5}

        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)

    def initialize(self, data_file: str, force_recreate: bool = False):
        """
        Complete initialization workflow.

        Args:
            data_file: Path to the Pokémon data file
            force_recreate: If True, recreate the vector store
        """
        logger.info("Initializing Pokémon data loader")

        # Load embeddings
        self.load_embeddings()

        # Load data
        self.load_pokemon_data(data_file)

        # Create documents
        documents = self.create_documents()

        # Create vector store
        self.create_vector_store(documents, force_recreate)

        logger.info("Initialization complete")


def test_data_loader():
    """Test the data loader with sample data."""
    # Create sample data
    sample_data = {
        'Name': ['Pikachu', 'Charizard', 'Blastoise'],
        'Type1': ['Electric', 'Fire', 'Water'],
        'Type2': [None, 'Flying', None],
        'HP': [35, 78, 79],
        'Attack': [55, 84, 83],
        'Defense': [40, 78, 100]
    }

    df = pd.DataFrame(sample_data)
    sample_file = 'data/pokemon/sample_pokemon.csv'
    os.makedirs('data/pokemon', exist_ok=True)
    df.to_csv(sample_file, index=False)

    # Test the loader
    loader = PokemonDataLoader()
    loader.initialize(sample_file)

    # Test retrieval
    retriever = loader.get_retriever()
    results = retriever.get_relevant_documents("Electric type Pokémon")
    print(f"Found {len(results)} relevant documents")
    for doc in results:
        print(doc.page_content)


if __name__ == "__main__":
    test_data_loader()
