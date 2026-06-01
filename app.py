
import streamlit as st
import redis
import ast
import pandas as pd

# Define tabs
tab1, tab2, tab3 = st.tabs(["Order", "Menu", "Kitchen"])

# --- TAB 1: ORDERING SYSTEM ---
with tab1:
    st.header("Place Your Order")
    phone_number = st.text_input("📞 Phone Number")
    delivery_location = st.text_input("📍 Delivery Location/Address")
    
    if st.button("Submit Order"):
        if not phone_number or not delivery_location:
            st.warning("Please enter your phone number and location!")
        else:
            st.success("Order sent to the kitchen!")

# --- TAB 3: KITCHEN DASHBOARD ---

# Load environment variables
load_dotenv()

# Initialize connections
redis = Redis(
    url=os.getenv("UPSTASH_URL"), 
    token=os.getenv("UPSTASH_TOKEN")
)
# Clean up your client initialization like this:
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)



# --- Update your Tab definitions ---
st.title("EWAKA RESTAURANT")
tab1, tab2, tab3 = st.tabs(["Ordering System", "Kitchen Dashboard", "Ewaka AI Chef"])


# --- TAB 3: AI CHEF ---
with tab3:
    st.title("👨‍🍳 Ask the Ewaka Chef")
    st.write("I am the Ewaka AI Chef")
# The "Law" for the AI (Strict Rules)
SYSTEM_PROMPT = """
You are a professional assistant for Ewaka Restaurant.
STRICT RULES:
1. ONLY answer questions about the menu, cooking, and restaurant services.
2. If a question is not about Ewaka, say: "I am sorry, I can only assist with Ewaka Restaurant inquiries."
3. Do not make up prices or items.
4. If you don't know, say "I don't have that information."
5. Be concise and professional.
"""

# Initialize session state with the system prompt
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]


    # Initialize chat history
    # 1. Define the Law (Put this at the TOP of your chat section, outside the loops)
SYSTEM_PROMPT = "You are a professional chef for Ewaka Restaurant..."

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# 2. Handle the User Input
if prompt := st.chat_input("How can I help?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 3. Handle the Assistant Response (This stays inside the 'if' block)
    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages,
            stream=True,
        )
        response = st.write_stream(stream) # This MUST align with 'stream'
    st.session_state.messages.append({"role": "assistant", "content": response})


# Database setup
redis = Redis(url="https://ruling-moccasin-69249.upstash.io", token="gQAAAAAAAQ6BAAIgcDI3ZDlhYjJjZjhmZGM0ZDRlOTk1NmE2YmUyMDFmZWIzNg")


# --- TAB 1: ORDERING ---
with tab1:
    selected_items = {}
    for item, price in menu_items.items():
        qty = st.number_input(f"{item} ({price} ksh)", min_value=0, max_value=10)
        if qty > 0:
            selected_items[item] = {"qty": qty, "price": price}

    # --- ORDERING LOGIC ---
# Initialize session state for inputs if they don't exist
if 'phone' not in st.session_state: st.session_state.phone = ""
if 'loc' not in st.session_state: st.session_state.loc = ""

# --- TAB 1: ORDERING SYSTEM ---
with tab1:
    st.header("Place Your Order")
    # ONLY define inputs here
    phone_number = st.text_input("📞 Phone Number")
    delivery_location = st.text_input("📍 Delivery Location/Address")
   

if st.button("Submit Order"):
    if not phone_number or not delivery_location:
        st.warning("Please enter your phone number and location!")
    else:
        # Calculate totals
        total = sum(i["qty"] * i["price"] for i in selected_items.values())
        
        # Create full order object
        order_details = {
            "items": selected_items,
            "phone": phone_number,
            "location": delivery_location,
            "total_price": total
        }
        
        # Save to Redis
        redis.rpush("orders", str(order_details))
        st.success("Order sent")


        if selected_items:
            total = sum(i["qty"] * i["price"] for i in selected_items.values())
            order_data = {"items": selected_items, "total_price": total}
            redis.rpush("orders", str(order_data))
            st.success(f"Order placed! Total: {total} ksh")
        else:
            st.warning("Cart is empty.")

# --- TAB 2: KITCHEN (PROTECTED) ---
with tab2:
    st.header("Staff Login")
    password = st.text_input("Enter Staff Password", type="password")
    
    if password == "1243": # Change this to your desired password
        st.success("Access Granted")
        if st.button("Refresh Kitchen"):
            orders = redis.lrange("orders", 0, -1)
            if not orders:
                st.info("No orders yet.")
            for i, order in enumerate(orders):
                order_dict = ast.literal_eval(order)
                st.write(f"--- Order {i+1} ---")
                st.write(f"**Total:** {order_dict['total_price']} ksh")
                st.json(order_dict['items'])
        
        if st.button("Clear All Orders"):
            redis.delete("orders")
            st.warning("Database Cleared!")
    elif password:
        st.error("Incorrect password")

