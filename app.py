import sqlite3
import streamlit as st

# ------------------- CONFIG -------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "gucci123"
# ---------------------------------------------

# Connect to SQLite database
conn = sqlite3.connect("gucci_store.db", check_same_thread=False)
cursor = conn.cursor()

# Create inventory table if not exists
cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    gender TEXT NOT NULL,
    price REAL NOT NULL,
    in_stock INTEGER NOT NULL
)
""")
conn.commit()

# Set Streamlit page config
st.set_page_config(page_title="Gucci Store Manager", page_icon="👜", layout="centered")

# ------------------- LOGIN SYSTEM -------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def login():
    st.title("🔒 Admin Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
            st.rerun()  # ✅ UPDATED
        else:
            st.error("Invalid username or password")

if not st.session_state.logged_in:
    login()
    st.stop()

# ------------------- MAIN APP -------------------
st.title("👜 Gucci Store Inventory Manager")

menu = ["Add Item", "View Inventory", "Search Items", "Inventory Statistics", "Remove Item", "Logout"]
choice = st.sidebar.radio("Navigation", menu)

# Logout
if choice == "Logout":
    st.session_state.logged_in = False
    st.success("Logged out successfully!")
    st.experimental_rerun()

# Add Item
elif choice == "Add Item":
    st.subheader("➕ Add New Item")
    name = st.text_input("Item Name")
    category = st.selectbox("Category", ["Clothing", "Bag", "Sunglasses", "Footwear"])
    gender = st.selectbox("Gender", ["Men", "Women", "Unisex"])
    price = st.number_input("Price (USD)", min_value=0.0, format="%.2f")
    in_stock = st.checkbox("In Stock", value=True)

    if st.button("Add Item"):
        if name.strip() == "":
            st.warning("Item name cannot be empty.")
        else:
            cursor.execute(
                "INSERT INTO inventory (name, category, gender, price, in_stock) VALUES (?, ?, ?, ?, ?)",
                (name, category, gender, price, int(in_stock))
            )
            conn.commit()
            st.success(f"✅ '{name}' added to inventory!")

# View Inventory
elif choice == "View Inventory":
    st.subheader("📦 All Inventory Items")
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()

    if items:
        for i, item in enumerate(items, start=1):
            st.markdown(f"**{i}. {item[1]}** - {item[2]}, {item[3]}, ${item[4]:.2f}, {'✅ In Stock' if item[5] else '❌ Out of Stock'}")
    else:
        st.info("No items found in the inventory.")

# Search Items
elif choice == "Search Items":
    st.subheader("🔍 Search Inventory")
    search_by = st.radio("Search by", ["Name", "Category"])
    keyword = st.text_input("Enter search term")

    if st.button("Search"):
        if search_by == "Name":
            cursor.execute("SELECT * FROM inventory WHERE name LIKE ?", ('%' + keyword + '%',))
        else:
            cursor.execute("SELECT * FROM inventory WHERE category LIKE ?", ('%' + keyword + '%',))
        results = cursor.fetchall()

        if results:
            for i, item in enumerate(results, start=1):
                st.markdown(f"**{i}. {item[1]}** - {item[2]}, {item[3]}, ${item[4]:.2f}, {'✅ In Stock' if item[5] else '❌ Out of Stock'}")
        else:
            st.warning("No matching items found.")

# Inventory Statistics
elif choice == "Inventory Statistics":
    st.subheader("📊 Inventory Statistics")
    cursor.execute("SELECT COUNT(*) FROM inventory")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM inventory WHERE in_stock = 1")
    in_stock = cursor.fetchone()[0]

    if total > 0:
        percent = (in_stock / total) * 100
        st.metric("Total Items", total)
        st.metric("In Stock", in_stock)
        st.metric("In Stock %", f"{percent:.2f}%")
    else:
        st.info("No items in the inventory yet.")

# Remove Item
elif choice == "Remove Item":
    st.subheader("🗑️ Remove Item")
    name = st.text_input("Enter item name to remove")

    if st.button("Remove"):
        cursor.execute("DELETE FROM inventory WHERE name LIKE ?", ('%' + name + '%',))
        conn.commit()

        if cursor.rowcount > 0:
            st.success(f"'{name}' removed from inventory.")
        else:
            st.error("Item not found.")
