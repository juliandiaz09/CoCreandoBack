// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyDnCfzF5psHLcnmbeJGrBuWpxOkUp01Lfo",
  authDomain: "cocreando-2dbd1.firebaseapp.com",
  projectId: "cocreando-2dbd1",
  storageBucket: "cocreando-2dbd1.firebasestorage.app",
  messagingSenderId: "862709485856",
  appId: "1:862709485856:web:e0994b08e2a748679b0745",
  measurementId: "G-EXLRNLVN1B"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);