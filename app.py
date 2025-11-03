"""
Main Application Entry Point
LLM-Powered Pokémon Data & Satellite Image Change Detection Tool
"""

import os
import sys
import argparse
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui.gradio_app import launch_app
from ui.enhanced_gradio_app import launch_enhanced_app
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="LLM-Powered Pokémon Data & Satellite Image Analysis Tool"
    )

    parser.add_argument(
        "--full-llm",
        action="store_true",
        help="Use full LLM agent (requires more GPU/RAM, ~8-16GB)"
    )

    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public Gradio link (for sharing)"
    )

    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to run the server on (default: 7860)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )

    parser.add_argument(
        "--enhanced",
        action="store_true",
        help="Use enhanced UI with satellite image fetching (recommended)"
    )

    args = parser.parse_args()

    # Display startup banner
    print("\n" + "=" * 70)
    print("  🎮 LLM-Powered Pokémon Data & Satellite Image Analysis Tool 🛰️")
    print("=" * 70)
    print("\n📋 Configuration:")
    print(f"  • UI: {'Enhanced (with satellite fetching)' if args.enhanced else 'Standard'}")
    print(f"  • Mode: {'Full LLM Agent' if args.full_llm else 'Simple Agent (Lightweight)'}")
    print(f"  • Port: {args.port}")
    print(f"  • Public Share: {'Enabled' if args.share else 'Disabled'}")
    print("\n💡 Tips:")
    print("  - Use --enhanced for satellite image fetching from APIs")
    print("  - Use --full-llm for more advanced responses (requires more resources)")
    print("=" * 70 + "\n")

    # Check for data directory
    os.makedirs("data/pokemon", exist_ok=True)
    os.makedirs("data/images", exist_ok=True)
    os.makedirs("vectordb", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Launch the application
    try:
        logger.info("Starting application...")

        if args.enhanced:
            logger.info("Launching enhanced UI with satellite fetching capabilities")
            launch_enhanced_app(
                use_full_llm=args.full_llm,
                share=args.share,
                server_port=args.port
            )
        else:
            logger.info("Launching standard UI")
            launch_app(
                use_full_llm=args.full_llm,
                share=args.share,
                server_port=args.port
            )

    except KeyboardInterrupt:
        logger.info("\nApplication stopped by user")
    except Exception as e:
        logger.error(f"Error running application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
