#!/usr/bin/env python3
"""
Smart PPE Compliance Checker - Main Runner Script

This script provides an easy way to start the PPE Compliance Checker system
with proper configuration and error handling.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def setup_logging(debug=False):
    """Set up logging configuration"""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('ppe_compliance.log')
        ]
    )

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'sqlalchemy', 'requests', 
        'python-dotenv', 'pydantic', 'opencv-python'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_configuration():
    """Check if configuration is properly set up"""
    from config import settings
    
    required_configs = [
        ('ROBOFLOW_API_KEY', settings.ROBOFLOW_API_KEY),
        ('ROBOFLOW_PROJECT_ID', settings.ROBOFLOW_PROJECT_ID),
    ]
    
    missing_configs = []
    for config_name, config_value in required_configs:
        if not config_value or config_value in ['', 'your_roboflow_api_key_here', 'your_project_id_here']:
            missing_configs.append(config_name)
    
    if missing_configs:
        print("❌ Missing or invalid configuration:")
        for config in missing_configs:
            print(f"   - {config}")
        print("\n💡 Please update your configuration in config.py or .env file")
        return False
    
    return True

def initialize_database():
    """Initialize the database with required tables"""
    try:
        from models import create_tables
        create_tables()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {str(e)}")
        return False

def start_server(host="0.0.0.0", port=8000, debug=False):
    """Start the FastAPI server"""
    try:
        import uvicorn
        from main import app
        
        print(f"🚀 Starting PPE Compliance Checker server...")
        print(f"   Host: {host}")
        print(f"   Port: {port}")
        print(f"   Debug: {debug}")
        print(f"   API Docs: http://{host}:{port}/docs")
        print(f"   Frontend: Open frontend/index.html in your browser")
        print("\n" + "="*50)
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=debug,
            log_level="debug" if debug else "info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {str(e)}")
        return False
    
    return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Smart PPE Compliance Checker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                    # Start server with default settings
  python run.py --debug           # Start server in debug mode
  python run.py --port 9000       # Start server on port 9000
  python run.py --check-config    # Check configuration only
  python run.py --init-db         # Initialize database only
        """
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind the server to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to bind the server to (default: 8000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--check-config',
        action='store_true',
        help='Check configuration and exit'
    )
    
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database and exit'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check dependencies and exit'
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    print("🛡️  Smart PPE Compliance Checker")
    print("=" * 40)
    
    # Check dependencies
    if args.check_deps:
        if check_dependencies():
            print("✅ All dependencies are installed")
            sys.exit(0)
        else:
            sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    # Check configuration
    if args.check_config:
        if check_configuration():
            print("✅ Configuration is valid")
            sys.exit(0)
        else:
            sys.exit(1)
    
    if not check_configuration():
        print("\n💡 Run 'python run.py --check-config' for detailed configuration check")
        sys.exit(1)
    
    # Initialize database
    if args.init_db:
        if initialize_database():
            sys.exit(0)
        else:
            sys.exit(1)
    
    if not initialize_database():
        sys.exit(1)
    
    # Start server
    if not start_server(args.host, args.port, args.debug):
        sys.exit(1)

if __name__ == "__main__":
    main()


