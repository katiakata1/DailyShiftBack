# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn, firestore_fn
# from firebase_admin import initialize_app, credentials, firestore,Event,DocumentSnapshot
from firebase_admin import initialize_app, credentials, firestore
from google.cloud.firestore import DocumentSnapshot

initialize_app(
    credentials.ApplicationDefault(),  # Uses credentials from firebase login
)


# Define the Cloud Function
@https_fn.on_request()
def on_request_example(req: https_fn.Request) -> https_fn.Response:
    return https_fn.Response("Hello world!")


# Firestore Trigger: Triggered when a new document is added to the `shift` collection
@firestore_fn.on_document_created(document="shift/{shift_id}")
def on_shift_created(event:firestore_fn.Event[DocumentSnapshot]):
    """Triggered when a new document is added to the `shift` collection."""
    # Get the newly created document data
    new_value =event.data.to_dict()  # `after` gives the document after the update

    # Print the new document's data to the logs
    print("New Shift Document Added:")
    print(new_value)

    # Check if the 'duration' field exists
    if "endTime" in new_value:
        return f"Shift duration: {new_value["endTime"]} hours"
    else:
        return "No duration field found in this shift entry."