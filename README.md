---
title: Stash Go Backend
emoji: 📦
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---
# **📦 Stash GO**

**A modern, high-performance Point-of-Sale (POS) and Inventory Management system tailored for shopkeepers and small businesses.**

Stash GO provides a secure, real-time business intelligence dashboard that tracks inventory movement, logs daily sales transactions, and generates automated financial reports. Built with a lightning-fast Python backend and a responsive, glassmorphism-styled Svelte frontend.

## **✨ Key Features**

* **Secure Authentication:** Robust user registration and login flow utilizing JWT (JSON Web Tokens) and bcrypt password hashing.  
* **Business Intelligence Dashboard:** Real-time analytics displaying gross revenue, net profit yields, top-selling items, and low-stock warnings.  
* **Automated Reporting:** Instantly generate and download monthly sales ledgers in both Excel (.xlsx) and PDF formats.  
* **Live Ledger:** A real-time transaction stream tracking every order, quantity, and timestamp.  
* **Modern UI/UX:** A premium, dark-mode SaaS interface featuring frosted glass aesthetics (glassmorphism), responsive grid layouts, and custom animations.

## **🛠️ Technology Stack**

**Frontend (Client)**

* [Svelte](https://svelte.dev/) \- UI Framework  
* [TypeScript](https://www.typescriptlang.org/) \- Static Typing  
* [Vite](https://vitejs.dev/) \- Build Tool & Development Server  
* Custom CSS (Design Tokens & CSS Variables)

**Backend (API Node)**

* [FastAPI](https://fastapi.tiangolo.com/) \- High-performance web framework  
* [Python 3.x](https://www.python.org/) \- Core language  
* [SQLAlchemy](https://www.sqlalchemy.org/) \- ORM & Database Management  
* [Pandas](https://pandas.pydata.org/) & [FPDF2](https://pyfpdf.github.io/fpdf2/) \- Data processing and report generation  
* Passlib & python-jose \- Security & JWT cryptography

## **🚀 Getting Started**

Follow these instructions to get a copy of Stash GO running on your local machine for development and testing.

### **1\. Backend Setup (FastAPI)**

Navigate to your backend directory:

cd backend

Create a virtual environment and activate it:

\# Windows  
python \-m venv venv  
venv\\Scripts\\activate

\# macOS/Linux  
python3 \-m venv venv  
source venv/bin/activate

Install the required dependencies:

pip install fastapi uvicorn sqlalchemy passlib\[bcrypt\] python-jose python-dotenv pandas openpyxl fpdf2

Create a .env file in the backend root and add your secret keys:

SECRET\_KEY="your\_super\_secret\_jwt\_key\_here"

Start the development server:

uvicorn main:app \--reload

*The API will be available at http://127.0.0.1:8000*

### **2\. Frontend Setup (Svelte)**

Open a new terminal window and navigate to your frontend directory:

cd frontend

Install the Node.js dependencies:

npm install

Start the Vite development server:

npm run dev

*The web app will be available at http://localhost:5173*

## **🏗️ Project Architecture**

* /backend/main.py \- Application entry point and CORS configuration.  
* /backend/routes/ \- Modular API endpoints (auth\_routes.py, report\_routes.py, etc.).  
* /backend/database.py \- Database connection and session management.  
* /backend/models.py \- SQLAlchemy database schemas (User\_Auth, Sale, Product).  
* /frontend/src/App.svelte \- Main frontend routing.  
* /frontend/src/lib/Login.svelte \- Secure authentication portal.  
* /frontend/src/lib/Dashboard.svelte \- The main BI and analytics view.

## **📝 Future Roadmap**

* \[ \] Interactive Point-of-Sale (Checkout) Interface  
* \[ \] CRUD Operations for Inventory Management (Add/Edit/Restock)  
* \[ \] Google SSO Integration  
* \[ \] Cloud Deployment (AWS EC2 & RDS)