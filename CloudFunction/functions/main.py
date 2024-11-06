# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn
from firebase_admin import initialize_app, credentials

initialize_app(
    credentials.ApplicationDefault(),  # Uses credentials from firebase login
    {
        "projectId": "dailyshift-7227e",
        "databaseURL": "https://dshift.firebaseio.com"  # Use your Firestore URL here
    }
)


# Define the Cloud Function
@https_fn.on_request()
def on_request_example(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("Hello world!")