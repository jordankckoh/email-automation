import streamlit as st
import pandas as pd
import os
import tempfile
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Set page configuration
st.set_page_config(
    page_title="Email Automation App",
    page_icon="📧",
    layout="centered"
)

# Function to load definitions from the definitions.txt file
def load_definitions():
    try:
        with open('definitions.txt', 'r') as f:
            content = f.read()
            
        core_line = content.split('\n')[0]
        if 'Core = [' in core_line:
            core_items = core_line.split('[')[1].split(']')[0].replace('"', '')
            core_values = [item.strip().replace('"', '').replace("'", "") for item in core_items.split(',')]
        else:
            core_values = []
        
        return core_values
    except Exception as e:
        st.error(f"Error loading definitions: {e}")
        return []

# Initialize session state variables if they don't exist
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'df' not in st.session_state:
    st.session_state.df = None
if 'recipients' not in st.session_state:
    st.session_state.recipients = []
if 'core_values' not in st.session_state:
    st.session_state.core_values = []
if 'sub_values' not in st.session_state:
    st.session_state.sub_values = []
if 'step' not in st.session_state:
    st.session_state.step = 1

# Function to reset the app
def reset_app():
    st.session_state.uploaded_file = None
    st.session_state.df = None
    st.session_state.recipients = []
    st.session_state.step = 1

# Main app title
st.title("Email Automation App")

# Step 1: File Upload
if st.session_state.step == 1:
    st.header("Step 1: Upload Excel File")
    uploaded_file = st.file_uploader("Choose an Excel file", type=['xlsx', 'xls', 'csv'])
    
    if uploaded_file is not None:
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                temp_path = tmp.name
            
            if uploaded_file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(temp_path)
            else:
                df = pd.read_csv(temp_path)
            
            required_columns = ['CORE', 'SUB', 'First_Name', 'Email']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.error(f"Missing required columns: {', '.join(missing_columns)}")
            else:
                st.session_state.uploaded_file = temp_path
                st.session_state.df = df
                st.session_state.core_values = df['CORE'].unique().tolist()
                st.session_state.sub_values = df['SUB'].unique().tolist()
                st.session_state.step = 2
                st.success("File successfully uploaded! Please continue to the next step.")
                st.experimental_rerun()
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# Step 2: Select Filters
elif st.session_state.step == 2:
    st.header("Step 2: Select Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        core_selection = st.selectbox(
            "Select CORE Value",
            ["Any"] + st.session_state.core_values
        )
    
    with col2:
        sub_selection = st.selectbox(
            "Select SUB Value",
            ["Any"] + st.session_state.sub_values
        )
    
    if st.button("Apply Filters"):
        df = st.session_state.df.copy()
        
        if core_selection != "Any":
            df = df[df['CORE'] == core_selection]
        if sub_selection != "Any":
            df = df[df['SUB'] == sub_selection]
        
        if len(df) == 0:
            st.warning("No recipients match the selected criteria. Please adjust your filters.")
        else:
            st.session_state.recipients = df[['First_Name', 'Email']].to_dict('records')
            st.session_state.step = 3
            st.experimental_rerun()

    if st.button("Go Back", key="back_to_upload"):
        st.session_state.step = 1
        st.experimental_rerun()

# Step 3: Recipients Preview
elif st.session_state.step == 3:
    st.header("Step 3: Recipients Preview")
    
    st.write(f"Found **{len(st.session_state.recipients)}** recipients matching your criteria.")
    
    recipients_df = pd.DataFrame(st.session_state.recipients)
    st.dataframe(recipients_df)
    
    if st.button("Continue to Email Template"):
        st.session_state.step = 4
        st.experimental_rerun()
    
    if st.button("Go Back", key="back_to_filters"):
        st.session_state.step = 2
        st.experimental_rerun()

# Step 4: Email Template
elif st.session_state.step == 4:
    st.header("Step 4: Create Email Template")
    
    # SMTP Configuration
    st.subheader("SMTP Configuration")
    smtp_server = st.text_input("SMTP Server (e.g., smtp.gmail.com)")
    smtp_port = st.number_input("SMTP Port", min_value=1, max_value=65535, value=587)
    smtp_email = st.text_input("Sender Email")
    smtp_password = st.text_input("Password", type="password")
    
    email_subject = st.text_input("Email Subject")
    email_template = st.text_area(
        "Email Body",
        value="Hi <name>,\n\n",
        height=250,
        help="Use <name> as a placeholder for recipient's first name."
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Send Emails", type="primary"):
            if not all([smtp_server, smtp_port, smtp_email, smtp_password, email_subject, email_template]):
                st.error("Please fill in all required fields")
            else:
                try:
                    # Initialize SMTP connection
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(smtp_email, smtp_password)
                    
                    sent_count = 0
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for i, recipient in enumerate(st.session_state.recipients):
                        # Create email message
                        msg = MIMEMultipart()
                        msg['From'] = smtp_email
                        msg['To'] = recipient['Email']
                        msg['Subject'] = email_subject
                        
                        personalized_body = email_template.replace('<name>', recipient['First_Name'])
                        msg.attach(MIMEText(personalized_body, 'plain'))
                        
                        # Send email
                        server.send_message(msg)
                        sent_count += 1
                        
                        # Update progress
                        progress = (i + 1) / len(st.session_state.recipients)
                        progress_bar.progress(progress)
                        status_text.text(f"Sent {i+1} of {len(st.session_state.recipients)} emails...")
                    
                    server.quit()
                    st.success(f"Successfully sent {sent_count} emails!")
                    
                    if st.button("Start Over"):
                        reset_app()
                        st.experimental_rerun()
                        
                except Exception as e:
                    st.error(f"Error sending emails: {str(e)}")
    
    with col2:
        if st.button("Go Back", key="back_to_preview"):
            st.session_state.step = 3
            st.experimental_rerun()
    
    # Email preview section
    st.subheader("Email Preview")
    st.info(f"Subject: {email_subject}")
    preview_text = email_template.replace('<name>', 'John')
    st.text_area("Body Preview", preview_text, height=200, disabled=True)

# Add a footer
st.markdown("---")
st.markdown("Email Automation App | Made with Streamlit")