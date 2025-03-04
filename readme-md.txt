# Email Automation App

This application helps automate the process of creating and sending personalized emails in Outlook based on data from uploaded Excel files.

## Features

- Upload Excel (.xlsx) files containing contact information
- Filter recipients based on CORE and SUB values
- Preview selected recipients before sending
- Create personalized email templates with name placeholder
- Send personalized emails directly through Outlook

## Setup Instructions

1. Install the required dependencies:
```
pip install -r requirements.txt
```

2. Make sure your definitions.txt file is correctly formatted and contains all necessary CORE and SUB values

3. Run the application:
```
python app.py
```

4. Open your web browser and navigate to `http://localhost:5000`

## Usage

1. **Step 1:** Upload an Excel file containing the following required columns:
   - CORE
   - SUB
   - First_Name
   - Email

2. **Step 2:** Select the desired CORE and/or SUB values to filter recipients
   - Leave as "Any" to include all values

3. **Step 3:** Review the filtered recipients list
   - Verify the correct contacts have been selected

4. **Step 4:** Create your email template
   - Enter a subject line
   - Enter your email body using `<name>` as a placeholder for the recipient's first name
   - Click "Send Emails" to send personalized emails to all selected recipients

## Requirements

- Windows operating system
- Microsoft Outlook installed and configured
- Python 3.8 or higher

## Note

The application sends real emails through your Outlook account. Double-check the recipient list before sending to avoid unintended emails.
