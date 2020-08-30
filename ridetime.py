# Initialises the RideTime app by calling the code in the 'app' module

from app import app, db
from app.models import User, Route


# For development purposes: Allows handling of User and Route objects and DB operations from the shell
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Route': Route}
