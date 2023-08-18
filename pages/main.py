import os
import openai
import streamlit as st
import requests
import pandas as pd
import json

# Set up your API key
openai.api_key = "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"

AYP_API_KEY = 'ask_9485bafc556cfd1bc5d26caa8893cfef'

# Make a completion request
def gpt_response(user_message):
    with st.spinner(text = """
In Progress, please wait ... ō͡≡o˞̶ 
"""):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or the appropriate chat model name
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{user_message}"},
            ],
        )

    assistant_response = response["choices"][0]["message"]["content"]
    return assistant_response

def upload_pdf():
    # Allow user to upload a file
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    # If a file is uploaded
    if uploaded_file:
        # Check if the file extension is .pdf
        if os.path.splitext(uploaded_file.name)[1] == ".pdf":
            st.write("Successfully uploaded the PDF file:", uploaded_file.name)
            # You can now process the PDF or save it, etc.
            # For demonstration, let's just display its size
            st.write("File size:", round(uploaded_file.size / 1024 / 1024, 2), "MB")
        else:
            st.error("The uploaded file is not a PDF. Please upload a valid PDF file.")

# # Header text
# st.header("Report Generation from PDF")

# # Sidebar
# sidebar = st.sidebar.selectbox(
#     "PDF Parsing or Regular Chat", ("PDF Parsing", "Regular Chat")
# )

# if sidebar == "PDF Parsing":
#     upload_pdf()
# elif sidebar == "Regular Chat":
#     user_message = st.text_input('Type your message', value="", type="default", label_visibility="visible")
#     if st.button("Get Response"):
#         response = gpt_response(user_message)
#         st.text_area("Assistant's Response:", response, height = 500)

ayp_prompt = """comparison between Delta Air Lines and Haufe page 3"""

def ayp_extract_data(doc_id):
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': AYP_API_KEY
    }

    data = [
        {
            "sender": "User",
            "message": ayp_prompt
        }
    ]

    response = requests.post(f'https://api.askyourpdf.com/v1/chat/{doc_id}',
    headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print(response.json())
        return response.json().get('answer', {}).get('message', 'No data extracted.')
    else:
        return f'Error: {response.status_code}'


def ayp_delete_document(doc_id):
    headers = {
        'x-api-key': AYP_API_KEY
    }

    response = requests.delete(f'https://api.askyourpdf.com/v1/api/documents/{doc_id}', headers=headers)
    if response.status_code == 200:
        print('Document deleted successfully')
    else:
        print('Error:', response.status_code)
        

# Upload PDF to AskYourPDF
def ayp_upload_document(file_data, file_name):
    headers = {
        'x-api-key': AYP_API_KEY
    }

    response = requests.post('https://api.askyourpdf.com/v1/api/upload', headers=headers,
                             files={'file': (file_name, file_data)})

    if response.status_code == 201:
        return response.json().get('docId')
    else:
        print('Error:', response.status_code)
        return None

# Fetch all documents from AskYourPDF
def ayp_get_documents():
    headers = {
        'x-api-key': AYP_API_KEY
    }

    params = {
        'page': 1,
        'page_size': 10
    }

    response = requests.get('https://api.askyourpdf.com/v1/api/documents', 
    headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print('Error:', response.status_code)
        return None


# Streamlit app
st.header("Report Generation from PDF")

sidebar = st.sidebar.selectbox(
    "PDF Parsing or Regular Chat", ("PDF Parsing", "Regular Chat")
)

if sidebar == "PDF Parsing":
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file:
        if os.path.splitext(uploaded_file.name)[1] == ".pdf":
            doc_id = ayp_upload_document(uploaded_file, uploaded_file.name)
            if doc_id:
                st.success(f"Successfully uploaded the PDF file: {uploaded_file.name} with Doc ID: {doc_id}")
            else:
                st.error("Failed to upload the PDF to AskYourPDF.")
        else:
            st.error("The uploaded file is not a PDF. Please upload a valid PDF file.")

    # Display uploaded documents
    documents_data = ayp_get_documents()
    if documents_data and 'documents' in documents_data:
        # Extract relevant data
        docs_list = documents_data['documents']
        df_data = [{'doc_id': doc['doc_id'], 'name': doc['name'], 'pages': doc['pages'], 'datetime': doc['date_time']} for doc in docs_list]
        
        # Convert to DataFrame
        df = pd.DataFrame(df_data)
        
        # Display each row with a checkbox
        selected_rows = []
        for index, row in df.iterrows():
            selected = st.checkbox(f"{row['name']} (Pages: {row['pages']}, Date: {row['datetime']})", key=row['doc_id'])
            if selected:
                selected_rows.append(row['doc_id'])
        
        # Delete button
        if st.button("Delete Selected"):
            for doc_id in selected_rows:
                ayp_delete_document(doc_id)
            st.write(f"Deleted {len(selected_rows)} documents.")
        
        # Extract data button
        if st.button("Extract Data"):
            if len(selected_rows) == 1:  # Ensure only one document is selected
                message = "What does this document say?"
                response = ayp_extract_data(selected_rows[0])
                st.text_area("Extracted Data:", response, height=500)
            else:
                st.warning("Please select only one document for data extraction.")

    else:
        st.write("No documents found.")

elif sidebar == "Regular Chat":
    user_message = st.text_input('Type your message')
    if st.button("Get Response"):
        response = gpt_response(user_message)
        st.text_area("Assistant's Response:", response, height=500)
