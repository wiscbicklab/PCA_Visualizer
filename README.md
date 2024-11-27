# Clone the repository from here  (get url from green code button - paste into your terminal)
git clone <your-github-url>
cd <your-project>

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app in development mode
python main.py
