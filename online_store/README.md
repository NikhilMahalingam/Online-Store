Simple Flask application for Online Store.

# App Setup

## Source virtual environment (local development)
On Windows: `venv\Scripts\activate`
On macOS/Linux: `source venv/bin/activate`

## Install dependencies
`pip install -r requirements.txt`

## Start PostgreSQL & Set up database
With Homebrew: `brew services start postgresql`
Stop: `brew services stop postgresql`

```
psql postgres
\i /path/to/schema.sql -- Build tables
\i /path/to/insert_sample_products.sql -- Insert sample data
```

## Start Flask app
`cd online_store && python app.py`

# PostgreSQL Help
## Access PostgreSQL shell
`psql postgres`

## Users
Test user: `username: username, password: password123`

## Run script
`\i path/to/script.sql`



# installations
Flask 
SQLAlchemy 
psycopg2
flask_sqlalchemy