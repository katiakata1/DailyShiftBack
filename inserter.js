import admin from "firebase-admin";
import fs from "node:fs";

// Initialize Firebase Admin
admin.initializeApp();

const db = admin.firestore();

// Load your JSON file
const data = JSON.parse(fs.readFileSync("./mock.json", "utf8"));

// Upload data
async function uploadData() {
  const collectionRef = db.collection("EmployeeData");

  for (const item of data["eligibleEmployees"]) {
    await collectionRef.doc(item["employee"]["uuid"]).set(item);
  }

  console.log("Data upload complete");
}

uploadData().catch(console.error);
