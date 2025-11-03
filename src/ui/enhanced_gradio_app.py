"""
Enhanced Gradio UI with Satellite Image Fetching and Change Detection
Features API integration for fetching satellite images and dedicated change detection mode.
"""

import os
import gradio as gr
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import logging

# Import modules
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from modules.llm_agent import SimpleLLMAgent, LLMAgent
from modules.satellite_fetcher import SatelliteImageFetcher, EXAMPLE_LOCATIONS
from modules.change_detector import ChangeDetectionAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedGradioApp:
    """Enhanced Gradio application with satellite image fetching."""

    def __init__(self, use_full_llm: bool = False):
        """
        Initialize the enhanced Gradio app.

        Args:
            use_full_llm: Whether to use full LLM agent or simple version
        """
        self.use_full_llm = use_full_llm

        # Initialize components
        if use_full_llm:
            logger.info("Initializing with full LLM agent")
            self.agent = LLMAgent()
        else:
            logger.info("Initializing with simple agent")
            self.agent = SimpleLLMAgent()

        self.satellite_fetcher = SatelliteImageFetcher()
        self.change_detector = ChangeDetectionAgent()

        # State variables
        self.pokemon_data_loaded = False
        self.image1_path = None
        self.image2_path = None
        self.fetched_images = {"before": None, "after": None}

    def load_pokemon_data(self, file) -> str:
        """Load Pokémon dataset."""
        if file is None:
            return "❌ No file uploaded."

        try:
            logger.info(f"Loading Pokémon data from: {file.name}")

            if self.use_full_llm:
                self.agent.initialize_pokemon_rag(file.name)
            else:
                self.agent.initialize_pokemon_data(file.name)

            self.pokemon_data_loaded = True

            import pandas as pd
            if file.name.endswith('.csv'):
                df = pd.read_csv(file.name)
            else:
                df = pd.read_excel(file.name)

            return f"✅ Successfully loaded {len(df)} Pokémon entries!"

        except Exception as e:
            logger.error(f"Error loading Pokémon data: {e}")
            return f"❌ Error loading data: {str(e)}"

    def fetch_satellite_images(
        self,
        location_name: str,
        latitude: float,
        longitude: float,
        date_before: str,
        date_after: str,
        api_source: str
    ) -> Tuple[Optional[gr.Image], Optional[gr.Image], str]:
        """
        Fetch satellite images from API.

        Args:
            location_name: Name/description of location
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            date_before: Before date
            date_after: After date
            api_source: API source to use

        Returns:
            Tuple of (before_image, after_image, status_message)
        """
        try:
            logger.info(f"Fetching satellite images for {location_name} ({latitude}, {longitude})")

            # Fetch images
            img_before, img_after = self.satellite_fetcher.fetch_image_pair(
                latitude=latitude,
                longitude=longitude,
                date1=date_before,
                date2=date_after,
                source=api_source.lower(),
                zoom=12
            )

            if img_before is None and img_after is None:
                return None, None, f"❌ Failed to fetch images. Check API configuration and try again."

            # Save fetched images
            if img_before:
                path_before = "data/images/fetched_before.jpg"
                self.satellite_fetcher.save_image(img_before, path_before)
                self.image1_path = path_before
                self.fetched_images["before"] = img_before

            if img_after:
                path_after = "data/images/fetched_after.jpg"
                self.satellite_fetcher.save_image(img_after, path_after)
                self.image2_path = path_after
                self.fetched_images["after"] = img_after

            # Update agent
            self.agent.set_images(self.image1_path, self.image2_path)

            status = "✅ Successfully fetched satellite images!\n"
            if img_before:
                status += f"Before ({date_before}): ✓\n"
            if img_after:
                status += f"After ({date_after}): ✓"

            return img_before, img_after, status

        except Exception as e:
            logger.error(f"Error fetching satellite images: {e}")
            return None, None, f"❌ Error: {str(e)}"

    def upload_image1(self, image) -> str:
        """Upload first image."""
        if image is None:
            return "No image uploaded."

        try:
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
            path = "data/images/temp_image2.png"
            os.makedirs("data/images", exist_ok=True)
            image.save(path)

            self.image2_path = path
            self.agent.set_images(self.image1_path, self.image2_path)

            return "✅ Second image uploaded successfully!"

        except Exception as e:
            logger.error(f"Error uploading image 2: {e}")
            return f"❌ Error: {str(e)}"

    def run_change_detection(self) -> str:
        """
        Run dedicated change detection analysis with specialized system prompt.

        Returns:
            Detailed change detection report
        """
        if not self.image1_path or not self.image2_path:
            return "❌ Please upload or fetch both images first!"

        try:
            logger.info("Running dedicated change detection analysis")

            # Run analysis with specialized change detector
            analysis = self.change_detector.analyze_temporal_changes(
                self.image1_path,
                self.image2_path,
                date1=None,  # Could be extracted from UI
                date2=None,
                location=None
            )

            # Return the detailed report
            return analysis['detailed_report']

        except Exception as e:
            logger.error(f"Error in change detection: {e}")
            return f"❌ Error running analysis: {str(e)}"

    def chat_response(self, message: str, history: List[Tuple[str, str]]) -> Tuple[List[Tuple[str, str]], str]:
        """Handle chat messages."""
        if not message.strip():
            return history, ""

        try:
            response = self.agent.chat(message)
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

    def load_example_location(self, location_name: str) -> Tuple[str, float, float, str]:
        """Load example location coordinates."""
        if location_name in EXAMPLE_LOCATIONS:
            loc = EXAMPLE_LOCATIONS[location_name]
            return location_name, loc["lat"], loc["lon"], loc["description"]
        return "", 0.0, 0.0, ""

    def build_interface(self):
        """Build and return the enhanced Gradio interface."""

        # Custom CSS
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
        }
        .api-info {
            background: #f0e6ff;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #9370DB;
        }
        """

        with gr.Blocks(css=custom_css, theme=gr.themes.Soft(
            primary_hue="purple",
            secondary_hue="pink"
        )) as interface:

            # Header
            gr.HTML("""
                <div class="header-title">
                    🛰️ Enhanced Satellite Image Change Detection & Pokémon AI Tool
                </div>
                <p style="text-align: center; color: #9370DB; font-size: 1.2em;">
                    Fetch satellite images from free APIs and analyze temporal changes with AI
                </p>
            """)

            with gr.Tabs():
                # TAB 1: Satellite Image Fetching & Change Detection
                with gr.Tab("🛰️ Satellite Image Analysis"):
                    gr.HTML('<div class="section-header">Fetch & Analyze Satellite Images</div>')

                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.Markdown("### 📍 Location Settings")

                            # Example location selector
                            example_location = gr.Dropdown(
                                choices=list(EXAMPLE_LOCATIONS.keys()),
                                label="Quick Select Example Location",
                                value=None
                            )

                            location_name = gr.Textbox(
                                label="Location Name",
                                placeholder="e.g., Amazon Rainforest"
                            )

                            with gr.Row():
                                latitude = gr.Number(
                                    label="Latitude",
                                    value=25.2048,
                                    precision=4
                                )
                                longitude = gr.Number(
                                    label="Longitude",
                                    value=55.2708,
                                    precision=4
                                )

                            location_desc = gr.Textbox(
                                label="Description",
                                placeholder="Brief description of the location",
                                lines=2
                            )

                            gr.Markdown("---")
                            gr.Markdown("### 📅 Date Selection")

                            # Default dates
                            default_before = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
                            default_after = datetime.now().strftime("%Y-%m-%d")

                            date_before = gr.Textbox(
                                label="Before Date (YYYY-MM-DD)",
                                value=default_before
                            )
                            date_after = gr.Textbox(
                                label="After Date (YYYY-MM-DD)",
                                value=default_after
                            )

                            gr.Markdown("---")
                            gr.Markdown("### 🌍 API Source")

                            api_source = gr.Radio(
                                choices=["NASA", "Sentinel", "Mapbox"],
                                value="NASA",
                                label="Image Source",
                                info="NASA GIBS requires NO API key (recommended for testing)"
                            )

                            fetch_btn = gr.Button("🚀 Fetch Satellite Images", variant="primary")

                            fetch_status = gr.Textbox(
                                label="Status",
                                interactive=False,
                                lines=3
                            )

                        with gr.Column(scale=2):
                            gr.Markdown("### 🖼️ Fetched Images")

                            with gr.Row():
                                fetched_before = gr.Image(
                                    label="Before Image",
                                    type="pil"
                                )
                                fetched_after = gr.Image(
                                    label="After Image",
                                    type="pil"
                                )

                            detect_changes_btn = gr.Button(
                                "🔍 Run Change Detection Analysis",
                                variant="primary",
                                size="lg"
                            )

                            change_report = gr.Textbox(
                                label="Change Detection Report",
                                lines=20,
                                interactive=False
                            )

                    # API Info Box
                    with gr.Accordion("ℹ️ API Setup Instructions", open=False):
                        gr.Markdown("""
                        <div class="api-info">

                        ## Free Satellite Imagery APIs

                        ### 1. 🌍 NASA GIBS (Recommended - No API Key Required!)
                        - **Cost**: Completely FREE
                        - **Setup**: NO registration needed
                        - **Coverage**: Global, daily updates
                        - **Resolution**: Medium (250m-1km)
                        - **Temporal**: 2000-present
                        - **Best for**: Testing, education, global coverage

                        ### 2. 🛰️ Sentinel Hub
                        - **Cost**: FREE tier (5000 requests/month)
                        - **Setup**: Register at [sentinel-hub.com](https://www.sentinel-hub.com/)
                        - **Coverage**: Global
                        - **Resolution**: High (10-60m)
                        - **Temporal**: 2015-present
                        - **API Key**: Set `SENTINEL_HUB_INSTANCE_ID` environment variable

                        **Setup Steps:**
                        1. Sign up at https://www.sentinel-hub.com/
                        2. Create a new configuration
                        3. Copy your Instance ID
                        4. Set environment variable: `export SENTINEL_HUB_INSTANCE_ID=your-id`

                        ### 3. 🗺️ Mapbox Satellite
                        - **Cost**: FREE tier (50,000 requests/month)
                        - **Setup**: Register at [mapbox.com](https://www.mapbox.com/)
                        - **Coverage**: Current imagery only (no temporal)
                        - **Resolution**: Very high
                        - **API Key**: Set `MAPBOX_ACCESS_TOKEN` environment variable

                        **Setup Steps:**
                        1. Sign up at https://www.mapbox.com/
                        2. Get your access token from dashboard
                        3. Set environment variable: `export MAPBOX_ACCESS_TOKEN=your-token`

                        ## Setting Environment Variables

                        **Linux/macOS:**
                        ```bash
                        export SENTINEL_HUB_INSTANCE_ID="your-instance-id"
                        export MAPBOX_ACCESS_TOKEN="your-access-token"
                        ```

                        **Windows (PowerShell):**
                        ```powershell
                        $env:SENTINEL_HUB_INSTANCE_ID="your-instance-id"
                        $env:MAPBOX_ACCESS_TOKEN="your-access-token"
                        ```

                        **Or create a `.env` file:**
                        ```
                        SENTINEL_HUB_INSTANCE_ID=your-instance-id
                        MAPBOX_ACCESS_TOKEN=your-access-token
                        ```

                        </div>
                        """)

                # TAB 2: Manual Upload & Pokémon (original functionality)
                with gr.Tab("📤 Manual Upload & Pokémon"):
                    with gr.Row():
                        with gr.Column(scale=1):
                            gr.HTML('<div class="section-header">📊 Data & Image Upload</div>')

                            gr.Markdown("### 🎮 Pokémon Dataset")
                            pokemon_file = gr.File(
                                label="Upload Pokémon Data (CSV or Excel)",
                                file_types=[".csv", ".xlsx", ".xls"]
                            )
                            pokemon_status = gr.Textbox(label="Status", interactive=False)
                            load_pokemon_btn = gr.Button("🔄 Load Pokémon Data", variant="primary")

                            gr.Markdown("---")
                            gr.Markdown("### 🛰️ Manual Image Upload")

                            image1 = gr.Image(label="📷 Image 1 (Before)", type="pil")
                            image1_status = gr.Textbox(label="Status", interactive=False)

                            image2 = gr.Image(label="📷 Image 2 (After)", type="pil")
                            image2_status = gr.Textbox(label="Status", interactive=False)

                        with gr.Column(scale=2):
                            gr.HTML('<div class="section-header">💬 AI Assistant Chat</div>')

                            chatbot = gr.Chatbot(label="Conversation", height=500)

                            with gr.Row():
                                msg = gr.Textbox(
                                    label="Your Message",
                                    placeholder="Ask about Pokémon or images...",
                                    lines=2,
                                    scale=4
                                )
                                with gr.Column(scale=1):
                                    send_btn = gr.Button("📤 Send", variant="primary")
                                    clear_btn = gr.Button("🗑️ Clear", variant="secondary")

                            gr.Examples(
                                examples=[
                                    "What are the top 5 Pokémon with highest Attack?",
                                    "Describe the first image",
                                    "What changed between the two images?"
                                ],
                                inputs=msg
                            )

            # Event Handlers

            # Example location selection
            example_location.change(
                fn=self.load_example_location,
                inputs=[example_location],
                outputs=[location_name, latitude, longitude, location_desc]
            )

            # Fetch satellite images
            fetch_btn.click(
                fn=self.fetch_satellite_images,
                inputs=[location_name, latitude, longitude, date_before, date_after, api_source],
                outputs=[fetched_before, fetched_after, fetch_status]
            )

            # Run change detection
            detect_changes_btn.click(
                fn=self.run_change_detection,
                outputs=[change_report]
            )

            # Manual upload handlers
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

            # Chat handlers
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


def launch_enhanced_app(use_full_llm: bool = False, share: bool = False, server_port: int = 7860):
    """Launch the enhanced Gradio application."""
    logger.info("Launching Enhanced Gradio application...")

    app = EnhancedGradioApp(use_full_llm=use_full_llm)
    interface = app.build_interface()

    interface.launch(
        share=share,
        server_port=server_port,
        server_name="0.0.0.0"
    )


if __name__ == "__main__":
    launch_enhanced_app(use_full_llm=False, share=False)
