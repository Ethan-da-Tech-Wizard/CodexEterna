"""
Gradio UI for LLM-Powered Pokémon Data & Satellite Image Tool
Features a gold, purple, white, and pink color scheme.
"""

import os
import gradio as gr
from typing import List, Tuple, Optional
import logging

# Import agent module
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.llm_agent import SimpleLLMAgent, LLMAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GradioApp:
    """Gradio application wrapper."""

    def __init__(self, use_full_llm: bool = False):
        """
        Initialize the Gradio app.

        Args:
            use_full_llm: Whether to use full LLM agent or simple version
        """
        self.use_full_llm = use_full_llm

        # Initialize agent
        if use_full_llm:
            logger.info("Initializing with full LLM agent")
            self.agent = LLMAgent()
        else:
            logger.info("Initializing with simple agent")
            self.agent = SimpleLLMAgent()

        # State variables
        self.pokemon_data_loaded = False
        self.image1_path = None
        self.image2_path = None

    def load_pokemon_data(self, file) -> str:
        """
        Load Pokémon dataset.

        Args:
            file: Uploaded file object

        Returns:
            Status message
        """
        if file is None:
            return "❌ No file uploaded."

        try:
            logger.info(f"Loading Pokémon data from: {file.name}")

            # Initialize data
            if self.use_full_llm:
                self.agent.initialize_pokemon_rag(file.name)
            else:
                self.agent.initialize_pokemon_data(file.name)

            self.pokemon_data_loaded = True

            # Count rows
            import pandas as pd
            if file.name.endswith('.csv'):
                df = pd.read_csv(file.name)
            else:
                df = pd.read_excel(file.name)

            return f"✅ Successfully loaded {len(df)} Pokémon entries!"

        except Exception as e:
            logger.error(f"Error loading Pokémon data: {e}")
            return f"❌ Error loading data: {str(e)}"

    def upload_image1(self, image) -> str:
        """Upload first image."""
        if image is None:
            return "No image uploaded."

        try:
            # Save to temporary location
            path = "data/images/temp_image1.png"
            os.makedirs("data/images", exist_ok=True)
            image.save(path)

            self.image1_path = path
            self.agent.set_images(self.image1_path, self.image2_path)

            return "✅ First image uploaded successfully!"

        except Exception as e:
            logger.error(f"Error uploading image 1: {e}")
            return f"❌ Error: {str(e)}"

    def upload_image2(self, image) -> str:
        """Upload second image."""
        if image is None:
            return "No image uploaded."

        try:
            # Save to temporary location
            path = "data/images/temp_image2.png"
            os.makedirs("data/images", exist_ok=True)
            image.save(path)

            self.image2_path = path
            self.agent.set_images(self.image1_path, self.image2_path)

            return "✅ Second image uploaded successfully!"

        except Exception as e:
            logger.error(f"Error uploading image 2: {e}")
            return f"❌ Error: {str(e)}"

    def chat_response(self, message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
        """
        Handle chat messages.

        Args:
            message: User message
            history: Chat history

        Returns:
            Updated history and empty string for input box
        """
        if not message.strip():
            return history, ""

        try:
            # Get response from agent
            response = self.agent.chat(message)

            # Update history
            history.append((message, response))

            return history, ""

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            error_msg = f"Sorry, I encountered an error: {str(e)}"
            history.append((message, error_msg))
            return history, ""

    def clear_chat(self) -> List:
        """Clear chat history."""
        if hasattr(self.agent, 'reset_memory'):
            self.agent.reset_memory()
        return []

    def build_interface(self):
        """Build and return the Gradio interface."""

        # Custom CSS for color scheme
        custom_css = """
        .gradio-container {
            background: linear-gradient(135deg, #ffffff 0%, #f8f0ff 100%) !important;
            font-family: 'Segoe UI', Arial, sans-serif;
        }

        .header-title {
            background: linear-gradient(90deg, #DAA520 0%, #9370DB 50%, #FFB6C1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
            padding: 20px;
        }

        .section-header {
            background: linear-gradient(90deg, #9370DB 0%, #DAA520 100%);
            color: white;
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
            font-weight: bold;
        }

        button {
            background: linear-gradient(135deg, #DAA520 0%, #9370DB 100%) !important;
            border: none !important;
            color: white !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            transition: transform 0.2s !important;
        }

        button:hover {
            transform: scale(1.05) !important;
        }

        .chatbot {
            border: 2px solid #9370DB !important;
            border-radius: 12px !important;
            background: white !important;
        }

        .message.user {
            background: linear-gradient(135deg, #FFB6C1 0%, #FFC0CB 100%) !important;
            border-radius: 12px !important;
            padding: 10px !important;
        }

        .message.bot {
            background: linear-gradient(135deg, #E6E6FA 0%, #F0E6FF 100%) !important;
            border-radius: 12px !important;
            padding: 10px !important;
        }

        .upload-area {
            border: 3px dashed #9370DB !important;
            border-radius: 12px !important;
            background: #f8f0ff !important;
            padding: 20px !important;
        }

        .status-message {
            background: linear-gradient(135deg, #DAA520 0%, #FFB6C1 100%);
            color: white;
            padding: 10px;
            border-radius: 8px;
            font-weight: bold;
        }
        """

        with gr.Blocks(css=custom_css, theme=gr.themes.Soft(
            primary_hue="purple",
            secondary_hue="pink",
            neutral_hue="zinc"
        )) as interface:

            # Header
            gr.HTML("""
                <div class="header-title">
                    ✨ LLM-Powered Pokémon Data & Satellite Image Analysis Tool ✨
                </div>
                <p style="text-align: center; color: #9370DB; font-size: 1.2em;">
                    Your AI Assistant for Pokémon Knowledge and Image Change Detection
                </p>
            """)

            with gr.Row():
                # Left Column - Data and Image Upload
                with gr.Column(scale=1):
                    gr.HTML('<div class="section-header">📊 Data & Image Upload</div>')

                    # Pokémon Data Upload
                    gr.Markdown("### 🎮 Pokémon Dataset")
                    pokemon_file = gr.File(
                        label="Upload Pokémon Data (CSV or Excel)",
                        file_types=[".csv", ".xlsx", ".xls"],
                        elem_classes=["upload-area"]
                    )
                    pokemon_status = gr.Textbox(
                        label="Status",
                        interactive=False,
                        elem_classes=["status-message"]
                    )
                    load_pokemon_btn = gr.Button("🔄 Load Pokémon Data", variant="primary")

                    gr.Markdown("---")

                    # Image Upload Section
                    gr.Markdown("### 🛰️ Satellite Images")
                    gr.Markdown("*Upload two images to compare changes over time*")

                    image1 = gr.Image(
                        label="📷 Image 1 (Before)",
                        type="pil",
                        elem_classes=["upload-area"]
                    )
                    image1_status = gr.Textbox(
                        label="Status",
                        interactive=False,
                        elem_classes=["status-message"]
                    )

                    image2 = gr.Image(
                        label="📷 Image 2 (After)",
                        type="pil",
                        elem_classes=["upload-area"]
                    )
                    image2_status = gr.Textbox(
                        label="Status",
                        interactive=False,
                        elem_classes=["status-message"]
                    )

                # Right Column - Chat Interface
                with gr.Column(scale=2):
                    gr.HTML('<div class="section-header">💬 AI Assistant Chat</div>')

                    chatbot = gr.Chatbot(
                        label="Conversation",
                        height=500,
                        elem_classes=["chatbot"]
                    )

                    with gr.Row():
                        msg = gr.Textbox(
                            label="Your Message",
                            placeholder="Ask me about Pokémon or image analysis...",
                            lines=2,
                            scale=4
                        )
                        with gr.Column(scale=1):
                            send_btn = gr.Button("📤 Send", variant="primary")
                            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")

                    # Example queries
                    gr.Markdown("### 💡 Example Questions")
                    gr.Examples(
                        examples=[
                            "What are the top 5 Pokémon with the highest Attack stat?",
                            "Tell me about Electric-type Pokémon",
                            "Describe the first image",
                            "What differences do you see between the two images?",
                            "Compare the images and tell me what changed"
                        ],
                        inputs=msg
                    )

            # Info Section
            with gr.Accordion("ℹ️ How to Use", open=False):
                gr.Markdown("""
                ## Getting Started

                ### 1️⃣ Pokémon Data Q&A
                - Upload a Pokémon dataset (CSV or Excel format)
                - Click "Load Pokémon Data"
                - Ask questions about the Pokémon in the chat!

                ### 2️⃣ Satellite Image Analysis
                - Upload two images (before and after)
                - Ask the AI to describe each image
                - Request a comparison to see what changed

                ### 3️⃣ Chat Tips
                - Ask natural questions - the AI will understand!
                - You can switch between topics freely
                - The AI remembers context within the conversation

                ### Example Questions
                - *"Which Water-type Pokémon have Defense over 100?"*
                - *"What does the first image show?"*
                - *"Compare the two images - what are the major changes?"*
                - *"Are these images of the same location?"*
                """)

            # Footer
            gr.HTML("""
                <div style="text-align: center; padding: 20px; color: #9370DB;">
                    <p>Built with ❤️ using Open-Source Models | Powered by LangChain & Gradio</p>
                    <p style="font-size: 0.9em;">Models: Dolly 2.0, BLIP, DETR | License: MIT/Apache 2.0</p>
                </div>
            """)

            # Event Handlers
            load_pokemon_btn.click(
                fn=self.load_pokemon_data,
                inputs=[pokemon_file],
                outputs=[pokemon_status]
            )

            image1.change(
                fn=self.upload_image1,
                inputs=[image1],
                outputs=[image1_status]
            )

            image2.change(
                fn=self.upload_image2,
                inputs=[image2],
                outputs=[image2_status]
            )

            send_btn.click(
                fn=self.chat_response,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )

            msg.submit(
                fn=self.chat_response,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )

            clear_btn.click(
                fn=self.clear_chat,
                outputs=[chatbot]
            )

        return interface


def launch_app(use_full_llm: bool = False, share: bool = False, server_port: int = 7860):
    """
    Launch the Gradio application.

    Args:
        use_full_llm: Whether to use full LLM (requires more resources)
        share: Whether to create a public link
        server_port: Port to run the server on
    """
    logger.info("Launching Gradio application...")

    app = GradioApp(use_full_llm=use_full_llm)
    interface = app.build_interface()

    interface.launch(
        share=share,
        server_port=server_port,
        server_name="0.0.0.0"
    )


if __name__ == "__main__":
    # Launch with simple agent by default
    launch_app(use_full_llm=False, share=False)
