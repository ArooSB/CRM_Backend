from backend import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import CheckConstraint


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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sales_leads = db.relationship('SalesLead', backref='customer', lazy=True, cascade="all, delete-orphan")
    interactions = db.relationship('Interaction', backref='customer', lazy=True, cascade="all, delete-orphan")
    support_tickets = db.relationship('SupportTicket', backref='customer', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        """Return a string representation of the customer."""
        return f"<Customer {self.first_name} {self.last_name}>"


class SalesLead(db.Model):
    """Model representing a sales lead in the database."""

    __tablename__ = 'sales_leads'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'), nullable=True)  # Optional field
    lead_status = db.Column(db.String(50), nullable=False)  # Status of the lead
    lead_source = db.Column(db.String(100), nullable=True)  # Optional source of the lead
    potential_value = db.Column(db.Float, nullable=True)  # Estimated monetary value of the lead
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Automatically set timestamp

    def __repr__(self):
        """Return a string representation of the sales lead."""
        return f"<SalesLead ID: {self.id}, Status: {self.lead_status}, Customer ID: {self.customer_id}>"


class Interaction(db.Model):
    """Model representing an interaction in the database."""

    __tablename__ = 'interactions'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),
                            nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('workers.id'),
                          nullable=True)
    interaction_type = db.Column(db.String(50), nullable=False)
    interaction_date = db.Column(db.Date, nullable=False)
    interaction_notes = db.Column(db.Text, default="")
    communication_summary = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
    created_by = db.Column(db.String(100), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('workers.id'),
                            nullable=True)  # Changed to Integer
    ticket_subject = db.Column(db.String(200), nullable=False)
    ticket_description = db.Column(db.Text, nullable=True)
    ticket_status = db.Column(
        db.String(50),
        nullable=False,
        default='Open'
    )  # Ticket status (Open, Close, In Process)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "ticket_status IN ('Open', 'Close', 'In Process')",
            name='check_ticket_status'
        ),
    )

    def __repr__(self):
        """Return a string representation of the support ticket."""
        return (f"<SupportTicket ID: {self.id}, Status: {self.ticket_status}, "
                f"Created By: {self.created_by}, Assigned To: {self.assigned_to}>")


class Analytics(db.Model):
    """Model representing analytics data in the database."""

    __tablename__ = 'analytics'
    __table_args__ = {'extend_existing': True}

    analytics_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, nullable=False)
    worker_id = db.Column(db.Integer, nullable=False)
    period_start_date = db.Column(db.Date, nullable=False)
    period_end_date = db.Column(db.Date, nullable=False)
    metric_value = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow,
                           nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        """Return a string representation of the analytics data."""
        return f"<Analytics analytics_id: {self.analytics_id}, customer_id: {self.customer_id}, worker_id: {self.worker_id}>"
