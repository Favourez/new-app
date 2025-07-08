// Firebase configuration for employer section
import { initializeApp } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-app.js";
import { getFirestore, collection, addDoc, getDocs, doc, updateDoc, deleteDoc, query, where, orderBy } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-firestore.js";
import { getAuth, createUserWithEmailAndPassword, signInWithEmailAndPassword, signOut } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-auth.js";
import { getStorage, ref, uploadBytes, getDownloadURL } from "https://www.gstatic.com/firebasejs/11.8.1/firebase-storage.js";

const firebaseConfig = {
  apiKey: "AIzaSyADnc7UmVIH1CFICk4r-ZqWMWdviOaYD10",
  authDomain: "employer-db-f647c.firebaseapp.com",
  projectId: "employer-db-f647c",
  storageBucket: "employer-db-f647c.firebasestorage.app",
  messagingSenderId: "650661422093",
  appId: "1:650661422093:web:9ea412eea4d5752d896144",
  measurementId: "G-JSJW6HVYNW"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
const storage = getStorage(app);

// Export Firebase services
window.firebaseDB = db;
window.firebaseAuth = auth;
window.firebaseStorage = storage;

// Export Firestore functions
window.firestoreFunctions = {
  collection,
  addDoc,
  getDocs,
  doc,
  updateDoc,
  deleteDoc,
  query,
  where,
  orderBy
};

// Export Auth functions
window.authFunctions = {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut
};

// Export Storage functions
window.storageFunctions = {
  ref,
  uploadBytes,
  getDownloadURL
};

console.log('Firebase initialized for employer section');
