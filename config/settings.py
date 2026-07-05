# Import the os module to talk to your computer's operating system environment
import os
# Import dotenv to read hidden configuration keys from a secret '.env' file
from dotenv import load_dotenv

# Load all the secrets from the '.env' file into your program
load_dotenv()

# Grab the Groq API key that you saved inside the '.env' file
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Tell the app exactly which AI brain model we want to talk to
# We are using the highly capable Qwen 32B model hosted on Groq
DEFAULT_MODEL = "qwen-32b"
