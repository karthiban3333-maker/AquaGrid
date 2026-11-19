import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged, User as FirebaseUser } from "firebase/auth";
import { getFirestore, collection, doc, setDoc, getDoc, getDocs, addDoc, query, where, serverTimestamp, updateDoc } from "firebase/firestore";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "dhaarasathi.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "dhaarasathi",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "dhaarasathi.firebasestorage.app",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "170799025230",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "1:170799025230:web:b3351c782b20728da8471f",
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID || "G-T9BG9R4C4N"
};

const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();
export const auth = getAuth(app);
export const db = getFirestore(app);
export const googleProvider = new GoogleAuthProvider();

export {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  collection,
  doc,
  setDoc,
  getDoc,
  getDocs,
  addDoc,
  query,
  where,
  serverTimestamp,
  updateDoc
};
export type { FirebaseUser };
