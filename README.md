# ResQMap - Disaster Intelligence Mapping Platform

## Overview
ResQMap is an AI-powered, real-time disaster intelligence platform that ingests multi-modal data (satellite images, drone footage, social media) to detect damaged infrastructure, identify flood-affected zones, track population displacement, and generate actionable disaster maps for emergency management teams.

## Features
- 🗺️ **Real-time Disaster Mapping** - Interactive maps with multiple layers
- 🤖 **AI-Powered Detection** - Satellite & drone image analysis
- 🌊 **Flood Zone Identification** - Real-time flood monitoring
- 👥 **Population Displacement Tracking** - Monitor affected populations
- 📊 **Analytics Dashboard** - Comprehensive disaster metrics
- 🚨 **Alert System** - Multi-severity level notifications
- 📄 **Report Generation** - Automated incident reports
- 🌤️ **Weather Integration** - HERE Weather API integration

## Tech Stack
### Backend
- Python 3.10+
- FastAPI (REST API & WebSockets)
- TensorFlow/PyTorch (AI Models)
- OpenCV (Image Processing)
- PostgreSQL (Database)
- Redis (Caching & Real-time)

### Frontend
- React 18
- TypeScript
- TailwindCSS
- shadcn/ui
- Leaflet/Mapbox GL JS
- Socket.io Client

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

## Setup Instructions

### Backend Setup
```bash
cd backend
python -m venv venv
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
venv\Scripts\activate

try this ->
pip install -r requirements.txt
uvicorn app.main:app --reload

OR this->
pip install -r requirements-minimal.txt
copy .env.example .env
python seed_data.py
python -m uvicorn app.main:app --reload

```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables (Optional for Demo)

The app works with default values! You can optionally create `.env` files to customize:

### Backend (.env) - Optional
```bash
# Already configured with these defaults:
DATABASE_URL=sqlite:///./resqmap.db  # File-based, no installation needed
SECRET_KEY=your-secret-key-here
HERE_API_KEY=your_here_api_key  # Optional - mock data used if not set

# For production only:
# DATABASE_URL=postgresql://user:password@localhost/resqmap
# REDIS_URL=redis://localhost:6379
```

### Frontend (.env) - Optional
```bash
# Already configured with these defaults:
VITE_API_URL=http://localhost:8000
VITE_HERE_API_KEY=your_here_api_key  # Optional - not required for demo
```

**For hackathon demo:** No `.env` files needed! Everything works with defaults.

## API Documentation
Once the backend is running, visit: http://localhost:8000/docs

## License
MIT License
