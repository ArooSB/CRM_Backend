# 🎉 CRM Backend Application

Welcome to the CRM Backend project! This powerful, scalable backend application provides a complete suite for managing customers, sales leads, worker interactions, support tickets, and analytics in a CRM system. Built with Flask and SQLAlchemy, it includes role-based access control, detailed logging, and CLI commands for smooth database management.

![Flask](https://img.shields.io/badge/Flask-v2.0.3-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

---

## ⚡ Features

- **🔐 Secure Authentication**: JWT-based user authentication and role-based access control.
- **🗃️ Robust CRUD Operations**: Manage customers, sales leads, interactions, tickets, and analytics data.
- **🔄 Database CLI Commands**: Quick commands for database setup, seeding, migration, and reset.
- **⚠️ Error Handling**: Custom error handling with detailed logging for seamless debugging.
- **📈 Analytics Tracking**: Real-time tracking of analytics metrics like active, inactive, and in-process leads.
- **🔍 Modular Code Structure**: Organized blueprints for easy scalability and maintenance.

---

## 📂 Project Structure

Here's a high-level overview of the project files and folders:

```plaintext
crm_backend/
├── backend/
│   ├── __init__.py             # App setup, blueprint registration, error handling, logging
│   ├── config.py               # App configuration settings
│   ├── manage.py               # CLI commands for database operations
│   └── models.py               # Database models (Customer, Worker, SalesLead, etc.)
├── routes/                     # Separate route files for each entity
│   ├── customers.py
│   ├── workers.py
│   ├── sales_leads.py
│   ├── interactions.py
│   ├── support_tickets.py
│   └── analytics.py
├── migrations/                 # Database migrations folder (auto-generated)
└── requirements.txt            # Dependencies for the project
