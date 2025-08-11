# Flask + SQLAlchemy Product Chatbot

A simple AI-powered chatbot built with Flask, SQLAlchemy, and OpenRouter API.  
It can handle product lookups from a database and answer FAQs, making it suitable for customer service integrations.

---

## 🚀 Features
- **Product Lookup:** Search for products in a SQL database by name or category.  
- **FAQ Support:** Predefined answers for common queries.  
- **LLM Integration:** Uses OpenRouter API for intelligent and conversational responses.  
- **Web Interface:** Simple HTML/CSS/JS frontend for interaction.  
- **REST API Endpoints:** Easily integrable into other applications.

---

## 📂 Project Structure
project/

│
├── app.py # Main Flask application


├── templates/

│ └── index.html # Chatbot frontend


├── static/

│ ├── style.css # Styling

│ └── script.js # For Logic


├── requirements.txt # Dependencies


└── README.md # Project documentation


 How It Works
 
User sends a query via the web UI or API.

Flask routes the message to the backend.

SQLAlchemy checks for a matching product or FAQ.

If found, it returns the predefined answer.

If not found, it sends the query to OpenRouter API for AI-generated response.

The reply is displayed in the chatbot UI.


📜 Requirements

Python 3.8+

Flask

SQLAlchemy

Requests

dotenv

Install them via:

bash
Copy
Edit
pip install flask sqlalchemy python-dotenv requests


📌 Future Improvements

Add authentication for API endpoints.

Support multimedia responses.

Improve UI design with modern chat components.

Add analytics for chatbot usage.
