import streamlit as st
import ast
import redis
import openai

# --- CONFIGURATION ---
st.set_page_config(page_title="Ewaka Restaurant", layout="wide")

# --- CONNECTIONS (Using Secrets) ---
# Ensure your Streamlit Cloud "Secrets" contains:
# UPSTASH_URL = "your_redis_url"
# OPENAI_API_KEY = "your_groq_api_key"

r = redis.from_url(st.secrets["UPSTASH_URL"])
client = openai.OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["Ordering System", "Kitchen Dashboard", "Ewaka AI Chef"])

# --- TAB 1: ORDERING SYSTEM ---
with tab1:
    st.header("Place Your Order")
    menu_items = {"Chapati": 50, "Beans": 100, "Pilau": 250, "Soda": 50}
    selected_items = {}
    for item, price in menu_items.items():
        qty = st.number_input(f"{item} ({price} ksh)", min_value=0, max_value=10, key=item)
        if qty > 0:
            selected_items[item] = {"qty": qty, "price": price}

    phone = st.text_input("Phone Number")
    location = st.text_input("Location")
    if st.button("Submit Order"):
        if phone and location and selected_items:
            total = sum(i["qty"] * i["price"] for i in selected_items.values())
            order = {"items": selected_items, "phone": phone, "location": location, "total": total}
            r.rpush("orders", str(order))
            st.success("Order sent!")
        else:
            st.warning("Fill in all details.")

# --- TAB 2: KITCHEN DASHBOARD ---
with tab2:
    st.header("Staff Access")
    pwd = st.text_input("Password", type="password")
    if pwd == "1243":
        if st.button("Refresh"):
            orders = r.lrange("orders", 0, -1)
            for order in orders:
                st.write(ast.literal_eval(order.decode('utf-8')))
        if st.button("Clear All"):
            r.delete("orders")

# --- TAB 3: AI CHEF ---
with tab3:
    st.header("Ask the Ewaka Chef")
    SYSTEM_PROMPT = "You are a professional chef for Ewaka Restaurant. Only answer about the menu."
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if prompt := st.chat_input("How can I help?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            stream = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=st.session_state.messages, stream=True)
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
