# AI-Powered Recruitment System

A modern, scalable, and secure recruitment platform powered by AI for streamlined hiring processes.

## 🚀 Features

- AI-powered JD generation and resume analysis
- Automated interview bot with MCQ generation
- Role-based access control (Admin, Recruiter, Candidate)
- Secure authentication and authorization
- Real-time application tracking
- Beautiful, responsive UI with animations
- Comprehensive admin dashboard
- Automated email notifications

## 🛠️ Tech Stack

### Backend
- FastAPI (Python)
- MongoDB Atlas
- PyJWT & Bcrypt
- Hugging Face Transformers
- Ollama
- scikit-learn

### Frontend
- ReactJS
- TailwindCSS
- Framer Motion
- React Router
- Axios

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- MongoDB Atlas account
- Hugging Face API key
- Ollama (for local LLM processing)

## 🔧 Setup Instructions

### Backend Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run the backend:
```bash
uvicorn main:app --reload
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the frontend:
```bash
npm run dev
```

## 🌐 Deployment

### Backend
- Deploy to Render/Railway/AWS EC2
- Set environment variables
- Configure MongoDB Atlas connection

### Frontend
- Deploy to Vercel
- Set environment variables
- Configure build settings

## 🔐 Security Features

- JWT authentication
- Role-based access control
- Secure password hashing
- HTTPS enforcement
- Admin panel with enhanced security
- Error logging and monitoring

## 📝 License

MIT License

## 👥 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📋 Getting Started

### Prerequisites

- Node.js (v18 or higher)
- Python (v3.9 or higher)
- MongoDB
- AWS Account (for S3 storage)
- OpenAI API key
- Hugging Face API key (optional)
- Ollama (optional, for local AI)

### Environment Setup

1. Clone the repository
2. Copy the environment template:
   ```bash
   cp backend/.env.example.template backend/.env
   ```
3. Update the `.env` file with your actual credentials:
   - MongoDB connection string
   - AWS credentials
   - API keys
   - Email settings
   - Admin credentials

### Installation

1. Install backend dependencies:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. Start the backend server:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. Start the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📋 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── ai_models.py
│   │   └── core/
│   ├── models/
│   ├── routers/
│   └── main.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── api/
│   │   └── App.jsx
│   └── public/
└── README.md
```

## 📋 Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## 📝 License

This project is licensed under the MIT License. 