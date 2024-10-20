from backend import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class Worker(db.Model):
    """Model representing a worker in the database."""

    __tablename__ = 'workers'
    __table_args__ = {'extend_existing': True}


    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    position = db.Column(db.String(100))
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)

    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check the provided password against the stored hashed password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Return a string representation of the worker."""
        return f"<Worker {self.first_name} {self.last_name}, Position: {self.position}>"


class Customer(db.Model):
    """Model representing a customer in the database."""

    __tablename__ = 'customers'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    address = db.Column(db.String(200))
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)

    # Relationships
    sales_leads = db.relationship('SalesLead', backref='customer', lazy=True,
                                  cascade="all, delete-orphan")
    interactions = db.relationship('Interaction', backref='customer',
                                   lazy=True, cascade="all, delete-orphan")
    support_tickets = db.relationship('SupportTicket', backref='customer',
                                      lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        """Return a string representation of the customer."""
        return f"<Customer {self.first_name} {self.last_name}>"


class SalesLead(db.Model):
    """Model representing a sales lead in the database."""

    __tablename__ = 'sales_leads'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            nullable=False)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the sales lead."""
        return f"<SalesLead ID: {self.id}, Status: {self.status}>"


class Interaction(db.Model):
    """Model representing an interaction in the database."""

    __tablename__ = 'interactions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the interaction."""
        return f"<Interaction ID: {self.id}>"


class SupportTicket(db.Model):
    """Model representing a support ticket in the database."""

    __tablename__ = 'support_tickets'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50))
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the support ticket."""
        return f"<SupportTicket ID: {self.id}, Status: {self.status}>"


class Analytics(db.Model):
    """Model representing analytics data in the database."""

    __tablename__ = 'analytics'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Text)
    created_at = db.Column(db.DateTime,
                           default=datetime.utcnow)

    def __repr__(self):
        """Return a string representation of the analytics data."""
        return f"<Analytics ID: {self.id}>"
