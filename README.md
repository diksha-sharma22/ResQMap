# ResQMap - Disaster Intelligence Mapping Platform

## Overview

ResQMap is an AI-powered, real-time disaster intelligence platform that ingests multi-modal data (satellite images, drone footage, social media) to detect damaged infrastructure, identify flood-affected zones, track population displacement, and generate actionable disaster maps for emergency management teams.

This project was developed as a **collaborative effort**, focusing on building an end-to-end system combining AI, real-time data processing, and interactive visualization.

---

## Features

* 🗺️ **Real-time Disaster Mapping** - Interactive maps with multiple layers
* 🤖 **AI-Powered Detection** - Satellite & drone image analysis
* 🌊 **Flood Zone Identification** - Real-time flood monitoring
* 👥 **Population Displacement Tracking** - Monitor affected populations
* 📊 **Analytics Dashboard** - Comprehensive disaster metrics
* 🚨 **Alert System** - Multi-severity level notifications
* 📄 **Report Generation** - Automated incident reports
* 🌤️ **Weather Integration** - HERE Weather API integration

---

## Tech Stack

### Backend

* Python 3.10+
* FastAPI (REST API & WebSockets)
* TensorFlow/PyTorch (AI Models)
* OpenCV (Image Processing)
* PostgreSQL (Database)
* Redis (Caching & Real-time)

### Frontend

* React 18
* TypeScript
* TailwindCSS
* shadcn/ui
* Leaflet/Mapbox GL JS
* Socket.io Client

---

## Project Structure

```
ResQMap/
├── backend/          # Python FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # AI models
│   │   ├── core/     # Core functionality
│   │   └── services/ # Business logic
│   └── requirements.txt
├── frontend/         # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── package.json
└── README.md
```

---

## Setup Instructions

### Backend Setup

```bash
cd backend
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
venv\Scripts\activate

# Option 1
pip install -r requirements.txt
uvicorn app.main:app --reload

# Option 2
pip install -r requirements-minimal.txt
copy .env.example .env
python seed_data.py
python -m uvicorn app.main:app --reload
```

---

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

## Environment Variables (Optional for Demo)

The app works with default values! You can optionally create `.env` files to customize:

### Backend (.env) - Optional

```bash
DATABASE_URL=sqlite:///./resqmap.db
SECRET_KEY=your-secret-key-here
HERE_API_KEY=your_here_api_key
```

### Frontend (.env) - Optional

```bash
VITE_API_URL=http://localhost:8000
VITE_HERE_API_KEY=your_here_api_key
```

**For demo purposes:** No `.env` files are required.

---

## API Documentation

Once the backend is running, visit:
http://localhost:8000/docs

---

## Notes

* This project was built in a **shared development setup**, so version control history may not fully reflect individual contributions.
* The focus was on rapid prototyping, system design, and feature implementation.

---

## License

MIT License
