"""
LangChain Agent Module
Integrates LLM with RAG and image analysis tools for conversational AI.
"""

import os
import logging
from typing import Optional, Dict, Any, List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from langchain.llms import HuggingFacePipeline
from langchain.chains import RetrievalQA
from langchain.agents import Tool, AgentExecutor, ConversationalAgent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

from .data_loader import PokemonDataLoader
from .image_analyzer import ImageAnalyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAgent:
    """Main agent orchestrating LLM, RAG, and image analysis."""

    def __init__(self, model_name: str = "databricks/dolly-v2-3b",
                 device: Optional[str] = None):
        """
        Initialize the LLM agent.

        Args:
            model_name: Name of the HuggingFace model to use
            device: Device to run on ('cuda', 'cpu', or None for auto)
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        logger.info(f"Initializing LLM Agent with model: {model_name}")
        logger.info(f"Using device: {self.device}")

        self.model_name = model_name
        self.llm = None
        self.tokenizer = None
        self.model = None

        # Components
        self.data_loader = PokemonDataLoader()
        self.image_analyzer = ImageAnalyzer(device=self.device)

        # Agent components
        self.qa_chain = None
        self.agent = None
        self.memory = None

        # Image paths (set by UI)
        self.image1_path = None
        self.image2_path = None

    def load_llm(self, load_in_8bit: bool = True, max_length: int = 512):
        """
        Load the language model.

        Args:
            load_in_8bit: Whether to use 8-bit quantization
            max_length: Maximum sequence length
        """
        logger.info(f"Loading language model: {self.model_name}")

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, padding_side="left")

        # Load model with appropriate settings
        model_kwargs = {
            "device_map": "auto",
            "torch_dtype": torch.float16 if self.device == "cuda" else torch.float32,
        }

        if load_in_8bit and self.device == "cuda":
            model_kwargs["load_in_8bit"] = True

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            **model_kwargs
        )

        # Create pipeline
        pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_length=max_length,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.15,
            pad_token_id=self.tokenizer.eos_token_id
        )

        # Wrap in LangChain
        self.llm = HuggingFacePipeline(pipeline=pipe)
        logger.info("Language model loaded successfully")

    def initialize_pokemon_rag(self, data_file: str, force_recreate: bool = False):
        """
        Initialize the Pokémon RAG system.

        Args:
            data_file: Path to Pokémon data file
            force_recreate: Whether to recreate the vector store
        """
        logger.info("Initializing Pokémon RAG system")

        # Initialize data loader
        self.data_loader.initialize(data_file, force_recreate)

        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.data_loader.get_retriever(search_kwargs={'k': 5}),
            return_source_documents=True
        )

        logger.info("Pokémon RAG system initialized")

    def create_tools(self) -> List[Tool]:
        """
        Create LangChain tools for the agent.

        Returns:
            List of Tool objects
        """
        tools = []

        # Pokémon Database Tool
        def query_pokemon_db(query: str) -> str:
            """Query the Pokémon database."""
            if self.qa_chain is None:
                return "Pokémon database not initialized. Please load a dataset first."
            try:
                result = self.qa_chain({"query": query})
                return result["result"]
            except Exception as e:
                logger.error(f"Error querying Pokémon DB: {e}")
                return f"Error accessing Pokémon database: {str(e)}"

        tools.append(Tool(
            name="PokemonDatabase",
            func=query_pokemon_db,
            description="Useful for answering questions about Pokémon data including stats, types, abilities, and other attributes. Input should be a question about Pokémon."
        ))

        # Image 1 Caption Tool
        def describe_image1(query: str) -> str:
            """Describe the first image."""
            if self.image1_path is None:
                return "No first image uploaded yet."
            try:
                caption = self.image_analyzer.generate_caption(self.image1_path)
                return f"Image 1 (Before): {caption}"
            except Exception as e:
                logger.error(f"Error generating caption for image 1: {e}")
                return f"Error analyzing image 1: {str(e)}"

        tools.append(Tool(
            name="DescribeImage1",
            func=describe_image1,
            description="Describes the first/before image that was uploaded. Use this when the user asks about the first image or 'before' image."
        ))

        # Image 2 Caption Tool
        def describe_image2(query: str) -> str:
            """Describe the second image."""
            if self.image2_path is None:
                return "No second image uploaded yet."
            try:
                caption = self.image_analyzer.generate_caption(self.image2_path)
                return f"Image 2 (After): {caption}"
            except Exception as e:
                logger.error(f"Error generating caption for image 2: {e}")
                return f"Error analyzing image 2: {str(e)}"

        tools.append(Tool(
            name="DescribeImage2",
            func=describe_image2,
            description="Describes the second/after image that was uploaded. Use this when the user asks about the second image or 'after' image."
        ))

        # Image Comparison Tool
        def compare_images_tool(query: str) -> str:
            """Compare two images and find differences."""
            if self.image1_path is None or self.image2_path is None:
                return "Both images must be uploaded before comparison."
            try:
                analysis = self.image_analyzer.analyze_differences(
                    self.image1_path,
                    self.image2_path,
                    include_objects=True
                )
                return analysis
            except Exception as e:
                logger.error(f"Error comparing images: {e}")
                return f"Error comparing images: {str(e)}"

        tools.append(Tool(
            name="CompareImages",
            func=compare_images_tool,
            description="Compares the two uploaded images and identifies changes, differences, or similarities. Use this when user asks about changes between images, what's different, or if they are the same location."
        ))

        return tools

    def initialize_agent(self):
        """Initialize the conversational agent with tools and memory."""
        logger.info("Initializing conversational agent")

        # Create memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # Create tools
        tools = self.create_tools()

        # Create custom prompt
        prefix = """You are a helpful AI assistant with access to specialized tools. You can:
1. Answer questions about Pokémon data from a comprehensive database
2. Analyze and describe satellite or aerial images
3. Compare two images to detect changes over time

When answering:
- Be concise and clear
- Use the appropriate tool for each task
- If you don't have enough information, ask for clarification
- Always ground your answers in the data/images provided

You have access to the following tools:"""

        suffix = """Begin!

Chat History:
{chat_history}

Question: {input}
{agent_scratchpad}"""

        # Create agent
        agent = ConversationalAgent.from_llm_and_tools(
            llm=self.llm,
            tools=tools,
            prefix=prefix,
            suffix=suffix,
            verbose=True
        )

        # Create executor
        self.agent = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            max_iterations=3,
            handle_parsing_errors=True
        )

        logger.info("Agent initialized successfully")

    def chat(self, message: str) -> str:
        """
        Send a message to the agent and get a response.

        Args:
            message: User's message

        Returns:
            Agent's response
        """
        if self.agent is None:
            return "Agent not initialized. Please set up the system first."

        try:
            response = self.agent.run(message)
            return response
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"I encountered an error: {str(e)}. Please try rephrasing your question."

    def set_images(self, image1_path: Optional[str], image2_path: Optional[str]):
        """
        Set the paths for images to analyze.

        Args:
            image1_path: Path to first image
            image2_path: Path to second image
        """
        self.image1_path = image1_path
        self.image2_path = image2_path
        logger.info(f"Images set: {image1_path}, {image2_path}")

    def reset_memory(self):
        """Clear conversation history."""
        if self.memory:
            self.memory.clear()
            logger.info("Conversation memory cleared")

    def full_initialize(self, pokemon_data_file: str,
                        use_smaller_model: bool = True):
        """
        Complete initialization of all components.

        Args:
            pokemon_data_file: Path to Pokémon data
            use_smaller_model: If True, use a smaller 3B model instead of 7B
        """
        logger.info("Starting full initialization")

        # Adjust model based on flag
        if use_smaller_model and "7b" in self.model_name.lower():
            self.model_name = self.model_name.replace("7b", "3b")
            logger.info(f"Using smaller model: {self.model_name}")

        # Load LLM
        self.load_llm()

        # Initialize Pokémon RAG
        if os.path.exists(pokemon_data_file):
            self.initialize_pokemon_rag(pokemon_data_file)
        else:
            logger.warning(f"Pokémon data file not found: {pokemon_data_file}")

        # Initialize agent
        self.initialize_agent()

        logger.info("Full initialization complete")


# Simple fallback agent for when full LLM is too heavy
class SimpleLLMAgent:
    """Lightweight agent using smaller models or rule-based responses."""

    def __init__(self):
        """Initialize simple agent."""
        self.data_loader = PokemonDataLoader()
        self.image_analyzer = ImageAnalyzer()
        self.image1_path = None
        self.image2_path = None
        self.chat_history = []

    def initialize_pokemon_data(self, data_file: str):
        """Initialize Pokémon data."""
        self.data_loader.initialize(data_file)

    def set_images(self, image1_path: Optional[str], image2_path: Optional[str]):
        """Set image paths."""
        self.image1_path = image1_path
        self.image2_path = image2_path

    def chat(self, message: str) -> str:
        """
        Simple chat function with keyword-based routing.

        Args:
            message: User message

        Returns:
            Response string
        """
        message_lower = message.lower()

        # Image-related queries
        if any(word in message_lower for word in ["image", "picture", "photo", "compare", "difference", "change"]):
            if "compare" in message_lower or "difference" in message_lower or "change" in message_lower:
                if self.image1_path and self.image2_path:
                    return self.image_analyzer.analyze_differences(
                        self.image1_path, self.image2_path, include_objects=True
                    )
                else:
                    return "Please upload both images first before comparison."
            elif "first" in message_lower or "before" in message_lower or "1" in message_lower:
                if self.image1_path:
                    caption = self.image_analyzer.generate_caption(self.image1_path)
                    return f"The first image shows: {caption}"
                else:
                    return "No first image uploaded yet."
            elif "second" in message_lower or "after" in message_lower or "2" in message_lower:
                if self.image2_path:
                    caption = self.image_analyzer.generate_caption(self.image2_path)
                    return f"The second image shows: {caption}"
                else:
                    return "No second image uploaded yet."

        # Pokémon queries
        elif any(word in message_lower for word in ["pokemon", "pikachu", "charizard", "type", "attack", "defense"]):
            if self.data_loader.vectorstore:
                retriever = self.data_loader.get_retriever()
                docs = retriever.get_relevant_documents(message)
                if docs:
                    results = "\n".join([doc.page_content for doc in docs[:3]])
                    return f"Here's what I found:\n\n{results}"
                else:
                    return "No relevant Pokémon data found for your query."
            else:
                return "Pokémon database not initialized. Please upload a dataset."

        # Default response
        else:
            return ("I can help you with:\n"
                    "1. Questions about Pokémon data\n"
                    "2. Analyzing and comparing images\n"
                    "Please ask me about Pokémon or upload images to analyze!")


if __name__ == "__main__":
    # Test initialization
    agent = SimpleLLMAgent()
    print("Simple LLM Agent initialized successfully")
