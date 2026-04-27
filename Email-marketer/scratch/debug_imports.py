import sys

def log(msg):
    print(msg)
    sys.stdout.flush()

log("Importing fastapi...")
import fastapi
log("Importing app.config...")
from app.config import settings
log("Importing app.db...")
from app.db import db
log("Importing app.api.auth...")
from app.api import auth
log("Importing app.api.leads...")
from app.api import leads
log("Importing app.api.emails...")
from app.api import emails
log("Done")
