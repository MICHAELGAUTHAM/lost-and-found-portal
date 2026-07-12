# Lost & Found Campus Portal

A full-stack web application designed for campus environments to help students and staff report lost items, list found items, and facilitate the secure claiming process. 

## Features

- **User Authentication**: Secure registration and login system with role-based access control (Student and Admin roles).
- **Report Lost Items**: Users can post details about items they have lost, including descriptions, categories, locations, dates, and images.
- **Report Found Items**: Users can list items they have found to help return them to their rightful owners.
- **Search Functionality**: Search for lost or found items by name, description, or location.
- **Claims System**: Users can submit a claim for a found item by providing proof of ownership.
- **Admin Dashboard**: Administrators can view pending claims, review proof descriptions, and approve or reject claims.
- **Image Uploads**: Support for uploading images for both lost and found items.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: PostgreSQL
- **Database Driver**: pg8000
- **Environment Management**: python-dotenv
- **Frontend**: HTML, CSS (Jinja2 Templates)

## Requirements

- Python 3.x
- PostgreSQL

## Setup & Installation

1. **Clone the repository** (or navigate to the project directory):
   ```bash
   cd path/to/project
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure Environment Variables**:
   Create a `.env` file in the root directory (if not already present) and add your database configuration:
   ```env
   SECRET_KEY=your_secret_key_here
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password
   DB_NAME=lost_and_found
   ```

6. **Initialize the Database**:
   Make sure your PostgreSQL server is running. Then create the database and run the initialization script:
   ```bash
   # Run the initialization script which uses schema.sql
   python init_db.py
   ```

7. **Run the Application**:
   ```bash
   python app.py
   ```
   The application will start on `http://127.0.0.1:5000/`.

## Directory Structure

```
├── app.py               # Main Flask application
├── init_db.py           # Database initialization script
├── schema.sql           # SQL schema for tables
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create this)
├── static/              # Static files (CSS, JS, uploads)
│   └── uploads/         # Uploaded images
└── templates/           # Jinja2 HTML templates
```

## Contributing
Feel free to open issues or submit pull requests for any improvements or bug fixes.
