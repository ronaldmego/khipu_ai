#scripts\setup.py
import os
import subprocess
import sys
import platform
from pathlib import Path

# Get the project root directory (parent of scripts directory)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

def create_venv():
    """Create virtual environment"""
    print("Creating virtual environment...")
    venv_path = PROJECT_ROOT / "venv"
    subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])

def get_activate_command():
    """Get the appropriate activate command based on OS"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "activate")
    return "source venv/bin/activate"

def get_python_path():
    """Get the appropriate python path based on OS"""
    if platform.system() == "Windows":
        return str(PROJECT_ROOT / "venv" / "Scripts" / "python.exe")
    return str(PROJECT_ROOT / "venv" / "bin" / "python")

def install_requirements():
    """Install required packages from requirements.txt"""
    python_cmd = get_python_path()
    requirements_file = PROJECT_ROOT / "requirements.txt"
    
    if not requirements_file.exists():
        print(f"❌ Error: requirements.txt not found in {requirements_file}!")
        sys.exit(1)
    
    print("📦 Installing packages...")
    try:
        # Actualizar pip usando python -m pip
        print("Upgrading pip...")
        subprocess.check_call([python_cmd, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Instalar los requerimientos
        print("Installing requirements...")
        subprocess.check_call([python_cmd, "-m", "pip", "install", "-r", str(requirements_file)])
        print("✅ All packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {str(e)}")
        sys.exit(1)

def setup_env_file():
    """Create .env file if it doesn't exist"""
    env_file = PROJECT_ROOT / ".env"
    if not env_file.exists():
        print("\n📝 Creating .env file template...")
        env_template = """# OpenAI Configuration
OPENAI_API_KEY=your_key_here

# OpenAI Models Configuration (optional)
OPENAI_MODELS=gpt-4o-mini|GPT-4 Mini (Most Economic)|gpt-4o-mini|1;gpt-4o-mini-2024-07-18|GPT-4 Mini July|gpt-4o-mini-2024-07-18|2;gpt-4o-2024-08-06|GPT-4 Turbo August|gpt-4o-2024-08-06|3;gpt-4o|GPT-4 Turbo (High Performance)|gpt-4o|4

# Database Configuration
MYSQL_USER=your_user
MYSQL_PASSWORD=your_password
MYSQL_HOST=your_host
MYSQL_DATABASE=your_database

# Application Configuration
IGNORED_TABLES=table1,table2,table3"""
        
        env_file.write_text(env_template)
        print("✅ .env template created successfully!")

def main():
    try:
        print("\n🚀 Starting setup process...")
        print(f"Project root directory: {PROJECT_ROOT}")
        
        # Crear entorno virtual
        create_venv()
        activate_cmd = get_activate_command()
        print("✅ Virtual environment created successfully!")
        
        # Instalar requerimientos
        install_requirements()
        
        # Configurar archivo .env
        setup_env_file()
        
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print(f"1. Run: {activate_cmd}")
        print("2. Configure your .env file with your credentials")
        print("3. Run: streamlit run src/pages/Home.py")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()