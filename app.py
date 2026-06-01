import streamlit as st
import ast
from redis import Redis
from openai import openai
# 1. Page Configuration
st.set_page_config(page_title="Ewaka Restaurant", layout="wide")
st.title("EWAKA RESTAURANT")

# 2. Connections (Using Streamlit Secrets)
# These keys MUST be in your Streamlit Cloud "Secrets" dashboard
redis_client = Redis(
    url=st.secrets["UPSTASH_URL"], 
    token=st.secrets["UPSTASH_TOKEN"]
)

client = OpenAI(
    api_key=st.secrets["GK"],
    base_url="https://api.groq.com/openai/v1"
)

# 3. Define Tabs
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

    phone_number = st.text_input("📞 Phone Number")
    delivery_location = st.text_input("📍 Delivery Location/Address")
   
    if st.button("Submit Order"):
        if not phone_number or not delivery_location or not selected_items:
            st.warning("Please fill in everything and select items!")
        else:
            total = sum(i["qty"] * i["price"] for i in selected_items.values())
            order_details = {
                "items": selected_items,
                "phone": phone_number,
                "location": delivery_location,
                "total_price": total
            }
            redis_client.rpush("orders", str(order_details))
            st.success(f"Order sent! Total: {total} ksh")

# --- TAB 2: KITCHEN DASHBOARD ---
with tab2:
    st.header("Staff Access")
    password = st.text_input("Enter Staff Password", type="password")
    if password == "1243":
        if st.button("Refresh Kitchen"):
            orders = redis_client.lrange("orders", 0, -1)
            for i, order in enumerate(orders):
                order_dict = ast.literal_eval(order.decode('utf-8'))
                st.write(f"--- Order {i+1} ---")
                st.write(f"**Phone:** {order_dict['phone']} | **Location:** {order_dict['location']}")
                st.json(order_dict['items'])
        if st.button("Clear All Orders"):
            redis_client.delete("orders")
            st.warning("Database Cleared!")

# --- TAB 3: EWAKA AI CHEF ---
with tab3:
    st.title("👨‍🍳 Ask the Ewaka Chef")
    
    # Strict Instructions (The "Law")
    SYSTEM_PROMPT = """
    You are a professional assistant for Ewaka Restaurant.
    STRICT RULES:
    1. ONLY answer questions about the menu, cooking, and restaurant services.
    2. If a question is not about Ewaka, say: "I am sorry, I can only assist with Ewaka Restaurant inquiries."
    3. Do not make up prices or items.
    4. If you don't know, say "I don't have that information."
    5. Be concise and professional.
    """

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

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
        
