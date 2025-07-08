# Job Portal Web Application

A comprehensive job portal web application built with React and Firebase that connects jobseekers with employers through intelligent matching and real-time communication.

## Features

### For Jobseekers
- ✅ User registration and authentication
- ✅ Resume upload with automatic parsing
- ✅ Skill extraction from resumes
- ✅ Job browsing with compatibility scoring
- ✅ Job application system
- ✅ Email notifications for applications
- ✅ Real-time chat with other users

### For Employers
- ✅ Company registration and authentication
- ✅ Job posting with skill requirements
- ✅ Application management
- ✅ Candidate compatibility scoring
- ✅ Application status management
- ✅ Real-time chat with candidates

### General Features
- ✅ Responsive design with Tailwind CSS
- ✅ Real-time chat system for all users
- ✅ Firebase integration for authentication and data storage
- ✅ Email notifications for job applications
- ✅ Modern UI with Lucide React icons

## Technology Stack

### Frontend
- **React 18** - Modern React with hooks
- **Vite** - Fast development build tool
- **React Router** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Lucide React** - Beautiful icons
- **React Hot Toast** - Toast notifications

### Backend & Database
- **Firebase Authentication** - User authentication
- **Firebase Firestore** - NoSQL database
- **Firebase Storage** - File storage for resumes
- **Firebase Realtime Database** - Real-time chat
- **Node.js/Express** - Backend API server
- **EmailJS/Nodemailer** - Email notifications

## Project Structure

```
new-app/
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── context/       # React context
│   │   ├── config/        # Firebase configuration
│   │   └── ...
├── server/                # Node.js backend (optional)
│   ├── index.js          # Express server
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Firebase account

### 1. Clone and Install Dependencies

```bash
# Install frontend dependencies
cd client
npm install

# Install backend dependencies (optional)
cd ../server
npm install
```

### 2. Firebase Configuration

The Firebase configuration is already set up in `client/src/config/firebase.js` with your provided credentials:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyBGI5FiqCAEYauz1cP_nSzo9lHCffxeIcU",
  authDomain: "jobportal-b622b.firebaseapp.com",
  projectId: "jobportal-b622b",
  storageBucket: "jobportal-b622b.firebasestorage.app",
  messagingSenderId: "736881486152",
  appId: "1:736881486152:web:67c5cee14c0d0d9b0aab7d",
  measurementId: "G-HN3PDEMPP0"
};
```

### 3. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: `jobportal-b622b`
3. Enable the following services:
   - **Authentication** (Email/Password)
   - **Firestore Database**
   - **Storage**
   - **Realtime Database**

### 4. Firestore Security Rules

Set up the following security rules in Firestore:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can read/write their own profile
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // Jobs can be read by authenticated users, written by employers
    match /jobs/{jobId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
        get(/databases/$(database)/documents/users/$(request.auth.uid)).data.userType == 'employer';
    }
    
    // Applications can be read/written by involved parties
    match /applications/{applicationId} {
      allow read, write: if request.auth != null && 
        (resource.data.applicantId == request.auth.uid || 
         resource.data.employerId == request.auth.uid);
    }
  }
}
```

### 5. Storage Security Rules

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /resumes/{userId}/{allPaths=**} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

### 6. Realtime Database Rules

```json
{
  "rules": {
    "messages": {
      ".read": "auth != null",
      ".write": "auth != null"
    },
    "onlineUsers": {
      ".read": "auth != null",
      ".write": "auth != null"
    }
  }
}
```

### 7. Start Development Servers

```bash
# Start frontend (from client directory)
cd client
npm run dev

# Start backend (optional, from server directory)
cd server
npm run dev
```

The application will be available at `http://localhost:5173`

## Usage Guide

### For Jobseekers

1. **Register** as a jobseeker with username, email, and password
2. **Upload Resume** - PDF files are automatically parsed to extract skills
3. **Browse Jobs** - View available positions with compatibility scores
4. **Apply for Jobs** - Submit applications and receive email confirmations
5. **Use Chat** - Communicate with employers and other users

### For Employers

1. **Register** as an employer with company information
2. **Post Jobs** - Create job listings with required skills
3. **Manage Applications** - Review candidates with compatibility scores
4. **Accept/Reject** - Update application statuses
5. **Use Chat** - Communicate with candidates

## Key Features Explained

### Resume Parsing
- Automatic skill extraction from PDF resumes
- Experience and education parsing
- Skills stored in user profile for matching

### Compatibility Scoring
- Matches job requirements with candidate skills
- Percentage-based scoring system
- Visual indicators for skill matches

### Real-time Chat
- Firebase Realtime Database for instant messaging
- Online user presence
- User type indicators (jobseeker/employer)

### Email Notifications
- Automatic emails when applications are submitted
- Professional email templates
- Application confirmation details

## Customization

### Adding New Skills
Skills are automatically extracted from resumes, but you can modify the parsing logic in:
- `client/src/pages/JobseekerDashboard.jsx` (parseResume function)
- `server/index.js` (resume parsing endpoint)

### Email Templates
Customize email templates in:
- `server/index.js` (send-application-email endpoint)
- EmailJS templates (if using EmailJS)

### UI Styling
The app uses Tailwind CSS. Customize colors and styling in:
- `client/tailwind.config.js`
- `client/src/index.css`

## Deployment

### Frontend (Vercel/Netlify)
```bash
cd client
npm run build
# Deploy the dist/ folder
```

### Backend (Heroku/Railway)
```bash
cd server
# Set environment variables
# Deploy to your preferred platform
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please create an issue in the repository or contact the development team.
