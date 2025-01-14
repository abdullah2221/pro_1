from sqlmodel import create_engine, SQLModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variable
connection_string = os.getenv('DB_URI')

# Debugging print statement
print(f"DB_URI: {connection_string}")

# Check if DB_URI is None
if not connection_string:
    raise ValueError("Environment variable 'DB_URI' is not set.")

# Create the engine using the connection string
connection = create_engine(connection_string)

# Function to create tables in the database
def create_tables():
    SQLModel.metadata.create_all(bind=connection)
