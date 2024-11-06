# Welcome to Cloud Functions for Firebase for Python!
# To get started, simply uncomment the below code or create your own.
# Deploy with `firebase deploy`

from firebase_functions import firestore_fn
from firebase_admin import initialize_app, credentials
from google.cloud.firestore import DocumentSnapshot
import logging

initialize_app(
    credentials.ApplicationDefault(),
)


@firestore_fn.on_document_created(document="shift/{shift_id}")
def on_shift_created(event: firestore_fn.Event[DocumentSnapshot | None]):
    """Triggered when a new document is added to the `shift` collection."""
    if event.data is None:
        return  # Do nothing
    data = event.data.to_dict()
    if data is None:
        logging.error("No data found in the document.")
        return
    start_time = data.get("startTime")
    end_time = data.get("endTime")

    logging.info(f"Shift started at {start_time} and ended at {end_time}")
