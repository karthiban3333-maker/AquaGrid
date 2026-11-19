import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged, User as FirebaseUser } from "firebase/auth";
import { getFirestore, collection, doc, setDoc, getDoc, getDocs, addDoc, query, where, serverTimestamp, updateDoc } from "firebase/firestore";

const env = (import.meta as unknown as { env?: Record<string, string> }).env || {};

const firebaseConfig = {
  apiKey: env.VITE_FIREBASE_API_KEY || "",
  authDomain: env.VITE_FIREBASE_AUTH_DOMAIN || "dhaarasathi.firebaseapp.com",
  projectId: env.VITE_FIREBASE_PROJECT_ID || "dhaarasathi",
  storageBucket: env.VITE_FIREBASE_STORAGE_BUCKET || "dhaarasathi.firebasestorage.app",
  messagingSenderId: env.VITE_FIREBASE_MESSAGING_SENDER_ID || "170799025230",
  appId: env.VITE_FIREBASE_APP_ID || "1:170799025230:web:b3351c782b20728da8471f",
  measurementId: env.VITE_FIREBASE_MEASUREMENT_ID || "G-T9BG9R4C4N"
};

const isConfigured = Boolean(firebaseConfig.apiKey && !firebaseConfig.apiKey.includes("your_"));
const app = isConfigured ? (!getApps().length ? initializeApp(firebaseConfig) : getApp()) : null;
export const auth = app ? getAuth(app) : (null as any);
export const db = app ? getFirestore(app) : (null as any);
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
