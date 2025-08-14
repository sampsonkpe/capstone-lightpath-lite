# LightPath Lite – Backend API

LightPath Lite is a simplified public transport scheduling and tracking system designed for urban areas like Accra.  
It provides real-time and scheduled transport data, weather-based trip condition simulations, and an easy-to-use API for integration.

## Features
- User registration and authentication
- Route and schedule management
- Vehicle tracking
- Weather-based condition simulation using OpenWeather API
- RESTful API endpoints for client integration

## Project Structure
lightpath-lite/
│
├── docs/
│   ├── ERD.md
│   ├── API_Endpoints.md
│
├── requirements.txt
├── .gitignore
└── README.md

## Tech Stack
- Backend Framework: Django & Django REST Framework
- Database: SQLite
- Version Control: Git and GitHub
- External API: OpenWeather API
- Development tools: Postman, cURL for API testing
- Authentication: JWT (JSON Web Tokens)

##  Installation
1. Clone the repository:
   git clone https://github.com/<your-username>/capstone-lightpath-lite.git
   cd capstone-lightpath-lite
2. Create and activate a virtual environment:
   python3 -m venv env
   source env/bin/activate
3. Install dependencies:
   pip install -r requirements.txt
4. Set up environment variables in a .env file.
   Create a .env file in the project root and add your configuration values.

## Usage
1. Run migrations:
   python3 manage.py migrate
2. Start the development server:
   python3 manage.py runserver
3. Access the API at: http://127.0.0.1:8000/api/

## Documentation
   ERD: See docs/ERD.md for the database structure.
   API Endpoints: See docs/API_Endpoints.md for available routes.

## Contributing
1. Fork the repository.
2. Create a new branch for your feature:
   git checkout -b feature-name
3. Commit your changes and push.
4. Open a pull request.
