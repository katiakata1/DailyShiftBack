from firebase_functions import firestore_fn, options, https_fn
from firebase_functions.https_fn import Request, Response

from firebase_functions.params import StringParam
import json
from firebase_admin import initialize_app, credentials, firestore
from firebase_functions.private.util import firebase_config
from google.cloud.firestore import DocumentSnapshot, ArrayUnion
import logging
import google.cloud.logging
import vertexai
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from datetime import datetime

sendgrid_email = StringParam("SENDGRID_EMAIL")
sendgrid_name = StringParam("SENDGRID_EMAIL_NAME")
sendgrid_api_key = StringParam("SENDGRID_API_KEY")


class EmailSender:
    def __init__(self, api_key=None):
        """Initialize EmailSender with optional API key"""
        self.api_key = api_key or sendgrid_api_key.value
        if not self.api_key:
            raise ValueError("SendGrid API key is required")
        self.sender = sendgrid_email.value  # Replace with your verified sender

    def get_shift_email_template(self, shift_data, shift_id, user_id):
        """
        Generate HTML email template for shift notification using DailyPay design

        Args:
            shift_data (dict): Dictionary containing shift information including:
                - startTime (datetime): Shift start time
                - endTime (datetime): Shift end time
                - firstName (str): Recipient's first name
                - description (str): Shift description

        Returns:
            str: Formatted HTML email template
        """
        shift_start = shift_data["startTime"].strftime("%I:%M %p")
        shift_end = shift_data["endTime"].strftime("%I:%M %p")
        shift_date = shift_data["startTime"].strftime("%B %d, %Y")

        return f"""<!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DailyPay Shift Opportunity</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f8f9fa; -webkit-font-smoothing: antialiased;">
        <table role="presentation" style="width: 100%; border: none; border-spacing: 0; background-color: #f8f9fa;">
            <tr>
                <td align="center" style="padding: 40px 0;">
                    <table role="presentation" style="width: 100%; max-width: 600px; border: none; border-spacing: 0; background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
                        <!-- Header with Logo -->
                        <tr>
                            <td style="padding: 32px 40px; text-align: center; border-bottom: 1px solid #eaeaea;">
                                <img src="https://ok3static.oktacdn.com/fs/bco/1/fs01oadkh97BLGcQ21d8" alt="DailyPay" style="width: 180px; height: auto;">
                            </td>
                        </tr>

                        <!-- Main Content -->
                        <tr>
                            <td style="padding: 40px;">
                                <p style="margin: 0 0 20px; font-size: 16px; line-height: 1.5; color: #333;">
                                    Hello {shift_data.get('firstName', '')},
                                </p>
                                <p style="margin: 0 0 24px; font-size: 16px; line-height: 1.5; color: #333;">
                                    There's an opportunity to earn some extra income today - see below for details.
                                </p>
                                
                                <!-- Shift Details Box -->
                                <div style="background-color: #f8f9fa; border-radius: 8px; padding: 24px; margin-bottom: 24px;">
                                    <p style="margin: 0 0 16px; font-size: 16px; line-height: 1.5; color: #333;">
                                        {shift_data.get('description', '')}
                                    </p>
                                    <p style="margin: 0; font-size: 16px; font-weight: bold; color: #333;">
                                        {shift_date} {shift_start} - {shift_end}
                                    </p>
                                </div>

                                <!-- Action Buttons -->
                                <table role="presentation" style="width: 100%; border: none; border-spacing: 0;">
                                    <tr>
                                        <td align="center" style="padding: 0 10px;">
                                            <a href="https://handle-shift-response-ku5aqyrn6a-uc.a.run.app/?shift_id={shift_id}&user_id={user_id}&response=accept" style="display: inline-block; padding: 14px 24px; background-color: #FF4D2D; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px;">I'm Interested</a>
                                        </td>
                                        <td align="center" style="padding: 0 10px;">
                                            <a href="#no-thanks" style="display: inline-block; padding: 14px 24px; background-color: #f8f9fa; color: #666; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px;">No Thanks</a>
                                        </td>
                                    </tr>
                                </table>

                                <p style="margin: 24px 0 0; font-size: 16px; line-height: 1.5; color: #666; text-align: center;">
                                    This opportunity could help you meet your financial goals a little bit faster.
                                </p>
                            </td>
                        </tr>

                        <!-- Footer -->
                        <tr>
                            <td style="padding: 24px 40px; background-color: #f8f9fa; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
                                <p style="margin: 0; font-size: 14px; color: #666; text-align: center;">
                                    <a href="https://www.dailypay.com" style="color: #FF4D2D; text-decoration: none;">Visit DailyPay</a>
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>"""

    def send_email(self, to_email: str, subject: str, html_content: str):
        """Send an email using SendGrid"""
        try:
            sg = SendGridAPIClient(self.api_key)

            message = Mail(
                from_email=Email(self.sender),
                to_emails=To(to_email),
                subject=subject,
                html_content=Content("text/html", html_content),
            )

            response = sg.send(message)
            logging.info(
                f"Email sent successfully to {to_email}. Status code: {response.status_code}"
            )
            return True, response.status_code

        except Exception as e:
            logging.error(f"Failed to send email: {str(e)}")
            return False, str(e)

    def send_shift_notification(self, to_email: str, shift_data: dict):
        """Convenience method to send shift notification email"""
        subject = "New Shift Available - Perfect Match!"
        html_content = self.get_shift_email_template(shift_data)
        return self.send_email(to_email, subject, html_content)


# Initialize logging
client = google.cloud.logging.Client()
client.setup_logging()
# Initialize Firebase
initialize_app(
    credentials.ApplicationDefault(),
)
db = firestore.client()


@firestore_fn.on_document_created(
    document="shift/{shift_id}", region="europe-west1", memory=options.MemoryOption.GB_1
)
def on_shift_createdv2(event: firestore_fn.Event[DocumentSnapshot | None]):
    """Triggered when a new document is added to the `shift` collection."""
    if event.data is None:
        return  # Do nothing
    shift_id = event.data.id
    shift_data = event.data.to_dict()
    if shift_data is None:
        logging.error("No data found in the document.")
        return

    start_time = shift_data.get("startTime")
    end_time = shift_data.get("endTime")
    logging.info(f"Shift started at {start_time} and ended at {end_time}")

    users_ref = db.collection("EmployeeData")
    users = users_ref.limit(5).stream()
    user_list = []
    for user in users:
        user_data = user.to_dict()
        user_list.append(user_data)

    vertexai.init()
    # Load the generative model
    model = GenerativeModel(model_name="models/gemini-1.5-flash")
    prompt = f"""
     Shift data: {shift_data}
     Users data: {user_list}
- Tell me who the top 3 most likely employees are to accept this shift based on the data points provided.
- Your response must be a json array containing the 3 indexes of the employees.
- The response should look like [index1,index2,index3].
- Do not explain or add any other information.
- The result must be in json format.
     """

    response = model.generate_content(
        prompt,
        generation_config=GenerationConfig(
            response_mime_type="application/json",
        ),
    )
    logging.info(f"Gemini response: {response.text}")

    try:
        selected_indices = json.loads(response.text)
        for index in selected_indices:
            user_data = user_list[index]
            logging.info(f"Selected user: {user_data}")

            email_sender = EmailSender()
            user_id = user_data["employee"]["uuid"]
            html_content = email_sender.get_shift_email_template(
                shift_data, shift_id, user_id
            )

            subject = "New Shift Available - Perfect Match!"
            email_sent = email_sender.send_email(
                f"baggy.simandoff+{user_id}@gmail.com",
                subject,
                html_content,
            )
            if email_sent:
                logging.info("Email notification sent successfully")
            else:
                logging.error("Failed to send email notification")

    except Exception as e:
        logging.error("Failed to process response or send email", e)
        logging.warning("Gemini response: ", response.text)


@https_fn.on_request(
    cors=options.CorsOptions(cors_origins="*", cors_methods=["get", "post"])
)
def handle_shift_response(req: Request) -> Response:
    """
    HTTP trigger function to handle user responses to shift notifications
    Expected URL params:
    - shift_id: The ID of the shift
    - user_id: The ID of the responding user
    - response: 'accept' or 'decline'

    Example: /handle_shift_response?shift_id=123&user_id=456&response=accept
    """
    # Check if this is a GET request
    if req.method != "GET":
        return Response("Method not allowed. Please use GET.", status=405)

    # Get URL parameters
    shift_id = req.args.get("shift_id")
    user_id = req.args.get("user_id")
    response = req.args.get("response")

    # Validate parameters
    if not all([shift_id, user_id, response]):
        return Response(
            "Missing required parameters. Need shift_id, user_id, and response.",
            status=400,
        )

    if response not in ["accept", "decline"]:
        return Response(
            'Invalid response. Must be either "accept" or "decline".', status=400
        )

    try:
        # Get references to the documents
        db = firestore.client()
        shift_ref = db.collection("shift").document(shift_id)
        user_ref = db.collection("EmployeeData").document(user_id)

        logging.info("Got the refs")
        # Get the documents
        shift_doc = shift_ref.get()
        user_doc = user_ref.get()

        # Check if documents exist
        if not shift_doc.exists:
            return Response("Shift not found.", status=404)

        if not user_doc.exists:
            return Response("User not found.", status=404)

        # Get the current data
        shift_data = shift_doc.to_dict()
        user_data = user_doc.to_dict()

        # Check if shift is still available
        if shift_data is None:
            return Response("Shift data is missing.", status=403)
        if shift_data.get("status") == "filled":
            return Response("This shift has already been filled.", status=409)
        if user_data is None:
            return Response("User data is missing.", status=403)
        # Handle the response
        if response == "accept":
            # Update shift document
            logging.info("User accepted the shift.")
            result = shift_ref.update(
                {
                    "accepted_users": ArrayUnion([user_data["employee"]]),
                }
            )
            logging.info(f"Shift update result: {str(result)}")
            return Response("Shift accepted successfully.", status=200)
        else:
            logging.info("User declined the shift.")
            return Response("Shift declined successfully.", status=200)

    except Exception as e:
        logging.error(f"Error handling shift response: {str(e)}")
        return Response(f"Internal server error: {str(e)}", status=500)
