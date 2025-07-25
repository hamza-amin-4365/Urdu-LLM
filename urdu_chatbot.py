import streamlit as st
import google.generativeai as genai
import argparse
import os
from dotenv import load_dotenv

load_dotenv()

class UrduGeminiChatbot:
    def __init__(self, api_key):
        self.api_key = api_key
        self._configure_api()
        self._initialize_model()

    def _configure_api(self):
        genai.configure(api_key=self.api_key)

    def _initialize_model(self):
        system_instruction = """
        You are an AI assistant that ONLY speaks and responds in Urdu.
        No matter what the user says, or in what language they say it, you MUST respond in Urdu script.
        Do not use Roman Urdu or English. Your entire response must be in the Urdu language and script.
        """
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=system_instruction
        )
        self.chat = self.model.start_chat(history=[])

    def send_prompt(self, prompt):
        try:
            response = self.chat.send_message(prompt, stream=True)
            return response
        except Exception as e:
            st.error(f"ایک خرابی پیش آگئی ہے: {e}")
            return None

class StreamlitApp:
    def __init__(self, chatbot):
        self.chatbot = chatbot
        self.setup_page()

    def setup_page(self):
        st.set_page_config(page_title="اردو چیٹ بوٹ", page_icon="🤖")
        st.title("اردو جیمنی چیٹ بوٹ 🤖")
        st.markdown("آپ کا استقبال ہے! براہ کرم اپنا سوال درج کریں۔")

    def initialize_session_state(self):
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

    def display_chat_history(self):
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(f'<div dir="rtl">{message["content"]}</div>', unsafe_allow_html=True)

    def handle_user_input(self):
        user_prompt = st.chat_input("آپ کا پیغام...")
        if user_prompt:
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(f'<div dir="rtl">{user_prompt}</div>', unsafe_allow_html=True)
            
            self.generate_response(user_prompt)

    def generate_response(self, user_prompt):
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            response_stream = self.chatbot.send_prompt(user_prompt)
            if response_stream:
                for chunk in response_stream:
                    full_response += chunk.text
                    message_placeholder.markdown(f'<div dir="rtl">{full_response} ▌</div>', unsafe_allow_html=True)
                message_placeholder.markdown(f'<div dir="rtl">{full_response}</div>', unsafe_allow_html=True)
            
            st.session_state.chat_history.append({"role": "assistant", "content": full_response})

    def run(self):
        self.initialize_session_state()
        self.display_chat_history()
        self.handle_user_input()


def main():
    parser = argparse.ArgumentParser(description="Run the Urdu Gemini Chatbot Streamlit app.")
    parser.add_argument("--api_key", type=str, help="Gemini API Key")
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("GEMINI_API_KEY")

    if not api_key:
        st.error("براہ کرم اپنی Gemini API کلید فراہم کریں۔")
        st.stop()

    chatbot = UrduGeminiChatbot(api_key=api_key)
    app = StreamlitApp(chatbot=chatbot)
    app.run()

if __name__ == "__main__":
    main()