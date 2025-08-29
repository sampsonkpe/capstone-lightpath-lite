# LightPath Lite – Backend API

LightPath Lite is a simplified public transport scheduling and tracking system designed for urban areas like Accra.  
It provides real-time and scheduled transport data, weather-based trip condition simulations, and an easy-to-use API for integration.

## FEATURES
- User registration and authentication (JWT-based)
- Passenger, conductor, and admin management
- Route, bus, and trip scheduling  
- Vehicle tracking  
- Booking, payment, and ticket issuance  
- Weather-based trip condition simulation using OpenWeather API  
- RESTful API endpoints for client integration 

## PROJECT STRUCTURE
capstone-lightpath-lite/
│
├── api_project/            # Django project configuration
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── core/                   # Main Django app: users, trips, bookings, payments, tickets
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── signals.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
│
├── core/migrations/        # Database migrations
│   ├── __init__.py
│   ├── 0001_initial.py
│   ├── 0002_alter_booking_options_alter_bus_options_and_more.py
│
├── docs/                   # Project documentation
│   ├── ERD.md
│   └── API_Endpoints.md
│
├── db.sqlite3              # SQLite database (for development)
├── manage.py               # Django CLI entry point
├── README.md
└── requirements.txt


## TECH STACK
- Backend Framework: Django 5+ / Django REST Framework
- Database: PostgreSQL (or SQLite for development)
- Version Control: Git and GitHub
- External API: OpenWeather API
- Testing: Django Test Framework / pytest
- Authentication: JWT (JSON Web Tokens)


## GETTING STARTED

## PREREQUISITES
- Python 3.11+
- pip package manager
- SQLite (for development)
- PostgreSQL (optional, for production)

##  INSTALLATION
1. Clone the repository:
   git clone https://github.com/sampsonkpe/capstone-lightpath-lite
   cd capstone-lightpath-lite
2. Create and activate a virtual environment:
   python3 -m venv env
   source env/bin/activate # Linux/macOS
   venv\Scripts\activate # Windows
3. Install dependencies:
   pip install -r requirements.txt
4. Set up environmental variables
   create a .env file in your Project Root
      SECRET_KEY=your_django_secret_key
      DEBUG=True
      OPENWEATHER_API_KEY=your_openweather_key
      DATABASE_URL=postgres://user:password@localhost:5432/dbname
5. Apply migrations
   python3 manage.py makemigrations
   python3 manage.py migrate
6. Create a superuser
   python3 manage.py createsuperuser
7. Start the development server:
   python3 manage.py runserver
8. Access the API at: http://127.0.0.1:8000/api/

## RUNNING TESTS
1. python3 manage.py test        # Using Django test framework
2. pytest         # Using pytest


## DOCUMENTATION
   ERD: See docs/ERD.md for the database structure.
   API Endpoints: See docs/API_Endpoints.md for available routes.

## CONTRIBUTING
1. Fork the repository.
2. Create a new branch for your feature:
   git checkout -b feature-name
3. Commit your changes and push.
   git add .
   git commit -m "feat: your message here"
   git push origin feature-name
4. Open a pull request.

## NOTES
1. Use PostgreSQL for production deployments.
2. Ensure your .env file is never committed to Git.
3. Follow PEP8 standards when editing Python files.
