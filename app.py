import streamlit as st
import ast
import redis
import openai

# 1. Page Config
st.set_page_config(page_title="Ewaka Restaurant")
st.title("EWAKA RESTAURANT")

# 2. Database Connection
r = redis.Redis(
    url=st.secrets["UPSTASH_URL"], 
    password=st.secrets["UPSTASH_TOKEN"]
)

# 3. AI Client
client = openai.OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# 4. Tabs
tab1, tab2, tab3 = st.tabs(["Ordering System", "Kitchen Dashboard", "Ewaka AI Chef"])

# --- TAB 3: AI CHEF ---
with tab3:
    st.header("👨‍🍳 Ask the Ewaka Chef")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a professional chef for Ewaka Restaurant. Only answer about the menu."}]

    if prompt := st.chat_input("How can I help?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True,
            )
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
        
