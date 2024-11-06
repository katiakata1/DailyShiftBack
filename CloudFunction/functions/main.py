# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import https_fn, firestore_fn
from firebase_admin import initialize_app, credentials, firestore
from google.cloud.firestore import DocumentSnapshot
import datetime

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

    # Extract fields from the document data
    start_time = new_value.get("startTime")
    end_time = new_value.get("endTime")

    # Convert `DatetimeWithNanoseconds` to `datetime` if they exist
    if start_time:
        if isinstance(start_time, datetime.datetime):
            print(f"Start Time: {start_time.isoformat()}")
        else:
            print("Start Time is not a valid datetime.")
    else:
        print("No start time found.")

    if end_time:
        if isinstance(end_time, datetime.datetime):
            print(f"End Time: {end_time.isoformat()}")
        else:
            print("End Time is not a valid datetime.")
    else:
        print("No end time found.")

    # Return a response (if applicable, e.g., for logging or further processing)
    if start_time and end_time:
        return f"Shift from {start_time.isoformat()} to {end_time.isoformat()}."
    else:
        return "Incomplete shift information."