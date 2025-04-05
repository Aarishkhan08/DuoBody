import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8501/callback')
GOOGLE_AUTH_SCOPE = ['https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile', 'openid']

# Application Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key_for_development')
CONTACT_EMAIL = os.getenv('CONTACT_EMAIL', 'mohdzohakhanlearning@gmail.com')

# Email Configuration
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Rate Limiting Configuration
RATE_LIMIT_REQUESTS = int(os.getenv('RATE_LIMIT_REQUESTS', 100))
RATE_LIMIT_PERIOD = int(os.getenv('RATE_LIMIT_PERIOD', 3600))  # In seconds (1 hour)

# PDB File Configuration
ALLOWED_EXTENSIONS = {'.pdb'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
