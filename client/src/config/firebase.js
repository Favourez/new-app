import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';
import { getDatabase } from 'firebase/database';

const firebaseConfig = {
  apiKey: "AIzaSyBGI5FiqCAEYauz1cP_nSzo9lHCffxeIcU",
  authDomain: "jobportal-b622b.firebaseapp.com",
  projectId: "jobportal-b622b",
  storageBucket: "jobportal-b622b.firebasestorage.app",
  messagingSenderId: "736881486152",
  appId: "1:736881486152:web:67c5cee14c0d0d9b0aab7d",
  measurementId: "G-HN3PDEMPP0"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
export const realtimeDb = getDatabase(app);

export default app;
