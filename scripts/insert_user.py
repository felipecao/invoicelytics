from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from invoicelytics.entities.domain_entities import User
from werkzeug.security import generate_password_hash
import uuid

# Database connection setup
DATABASE_URL = "postgresql://invoicelytics:password@localhost:2345/invoicelytics"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# User details
username = "felipe"
email = "felipe.carvalho@gmail.com"
password = "felipe_123"
tenant_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")

# Create a new user instance
new_user = User(id=uuid.uuid4(), username=username, email=email, password_hash=generate_password_hash(password), tenant_id=tenant_id)

# Add and commit the new user to the database
session.add(new_user)
session.commit()

print(f"User {username} added successfully.")
