import os
import time
import json
import datetime
import requests
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

import streamlit as st
from app import LLMTagger

# ----- GENERAL PAGE SETTINGS AND STYLE -----
st.set_page_config(page_title="Language, Sentiment and Intent Analysis", layout="centered")
st.markdown("""
    <style>
    .block-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .stApp {
        background-color: #0f1117 !important;
        color: #eaeaea !important;
    }
    h1 {
        font-size: 36px !important;
        font-weight: bold;
        white-space: nowrap;
    }
    h1, h2, h3, h4, h5, h6, label, .stTextInput label, .stChatMessage {
        color: #eaeaea !important;
    }
    .stTextInput > div > input {
        background-color: #0F0F0F !important; 
        color: #eaeaea !important; 
        border: 1px solid #555555 !important;
        border-radius: 5px !important;
    }
    div.stButton > button {
        background-color: #0F0F0F !important;
        border: 1px solid #555555 !important;
        color: #eaeaea !important;
        font-size: 16px;
        cursor: pointer;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
    }
    div.stButton > button:hover {
        background-color: #1a1a1a !important;
        border: 1px solid #666666 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("Language, Sentiment and Intent Analysis")
st.write("Enter text or a complete conversation to receive real-time analysis results.")

# Initialize session state variables if they don't exist
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.environ.get('OPENAI_API_KEY', '')
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'tagger' not in st.session_state:
    st.session_state.tagger = None

# API key input form
with st.expander("OpenAI API Settings", expanded=not st.session_state.api_key_valid):
    api_key_form = st.form(key="api_key_form")
    api_key_input = api_key_form.text_input(
        "Enter your OpenAI API Key:", 
        value=st.session_state.api_key,
        type="password",
        help="Your API key will be stored in your session and not saved on the server."
    )
    model_name = api_key_form.selectbox(
        "Select OpenAI model:",
        ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4", "gpt-4o"],
        index=0
    )
    temperature = api_key_form.slider(
        "Temperature:", 
        min_value=0.0, 
        max_value=1.0, 
        value=0.0, 
        step=0.1,
        help="Higher values make output more random, lower values more deterministic."
    )
    submit_button = api_key_form.form_submit_button("Save API Settings")
    
    if submit_button:
        try:
            # Update environment variables with the new values
            os.environ['OPENAI_API_KEY'] = api_key_input
            os.environ['OPEN_AI_MODEL_NAME'] = model_name
            os.environ['OPENAI_MODEL_TEMPERATURE'] = str(temperature)
            
            # Create a new tagger with the updated API key
            st.session_state.tagger = LLMTagger()
            st.session_state.api_key = api_key_input
            
            # Make a simple test call to verify the API key works
            test_result = st.session_state.tagger.tag("This is a test message.")
            
            # If we get here without errors, the API key is valid
            st.session_state.api_key_valid = True
            st.success("API key saved and verified!")
        except Exception as e:
            st.session_state.api_key_valid = False
            st.error(f"Error with API key: {e}")

# Only show the analysis interface if the API key is valid
if st.session_state.api_key_valid and st.session_state.tagger:
    analysis_mode = st.selectbox("Select Analysis Mode", ["Single Sentence", "Conversation"])

    if analysis_mode == "Single Sentence":
        user_input = st.chat_input("Enter text and press Enter:")
        if user_input:
            # Display user message on screen
            with st.chat_message("user", avatar="👤"):
                st.write(user_input)

            if user_input.strip() == "":
                st.warning("Please enter valid text.")
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    result = st.session_state.tagger.tag(user_input)
                    
                    # Prepare log data
                    log_data = {
                        "timestamp": datetime.datetime.now().isoformat(),
                        "text": user_input,
                        "analysis": result
                    }
                    # Send to log service
                    try:
                        # Use 127.0.0.1 inside Docker container - localhost sometimes behaves differently
                        response = requests.post("http://127.0.0.1:8000/log", json=log_data, timeout=2)
                        if response.status_code != 200:
                            st.error(f"Error response from log service: {response.status_code}")
                    except requests.exceptions.ConnectionError:
                        st.warning("Could not connect to log service - logs will not be saved to MongoDB")
                    except requests.exceptions.Timeout: 
                        st.warning("Timeout connecting to log service")
                    except Exception as e:
                        st.error(f"Error connecting to log service: {e}")

                    # Display the result
                    st.markdown("```json\n" + json.dumps(result, indent=2) + "\n```", unsafe_allow_html=True)

    else:
        # In "Conversation" mode, use chat_input to fix it to the bottom
        conversation_input = st.chat_input("Enter conversation text and press Enter:")
        if conversation_input:
            with st.chat_message("user", avatar="👤"):
                st.write(conversation_input)

            if conversation_input.strip() == "":
                st.warning("Please enter valid text.")
            else:
                with st.chat_message("assistant", avatar="🤖"):
                    # Call conversation_analysis module for multi-sentence analysis
                    from conversation_analysis import analyze_conversation
                    analysis_results = analyze_conversation(conversation_input)

                    # Display results in chat format, listing each sentence
                    for idx, result in enumerate(analysis_results):
                        st.write(f"**Sentence {idx+1}:** {result['sentence']}")
                        st.write("```json\n" + json.dumps(result['analysis'], indent=2) + "\n```")
else:
    if not st.session_state.api_key_valid:
        st.info("Please enter a valid OpenAI API key to use the application.")
