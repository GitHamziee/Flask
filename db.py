from flask_pymongo import PyMongo

mongo = None  # Initialize as None

def init_db(app):
    """
    Initialize the MongoDB connection.
    """
    global mongo
    try:
        mongo = PyMongo(app)  # Connect Flask to MongoDB
        # Test the connection by listing databases
        print(f"MongoDB initialized. Databases: {mongo.cx.list_database_names()}")
    except Exception as e:
        print(f"Error initializing MongoDB: {e}")
    return mongo
