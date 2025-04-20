import streamlit as st
import pandas as pd
import pywhatkit as kit
import datetime

st.set_page_config(page_title="Excel WhatsApp Tool", layout="wide")
st.title("📊 Slim Gym Message Tool")

# Initialize session state
if "df" not in st.session_state:
    st.session_state.df = pd.DataFrame(columns=["ID", "Name", "Phone"])

if "show_add_form" not in st.session_state:
    st.session_state.show_add_form = False

# Helper to ensure +91 prefix
def format_phone(phone):
    phone = str(phone).strip()
    if not phone.startswith("+"):
        if phone.startswith("91"):
            return "+" + phone
        elif len(phone) == 10:
            return "+91" + phone
    return phone

# Upload Excel File
uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    if all(col in df.columns for col in ["ID", "Name", "Phone"]):
        df["Phone"] = df["Phone"].apply(format_phone)
        st.session_state.df = df
        st.success("✅ Excel file loaded successfully!")
    else:
        st.error("❌ Excel must have columns: ID, Name, Phone")

# Show Add Form Button
if st.button("➕ Add New Entry"):
    st.session_state.show_add_form = True

# Add Entry Form (conditionally visible)
if st.session_state.show_add_form:
    with st.form("add_entry_form", clear_on_submit=True):
        new_id = st.text_input("ID")
        new_name = st.text_input("Name")
        new_phone = st.text_input("Phone Number (e.g., 9876543210 or +91...)")
        submit = st.form_submit_button("Submit")
        if submit:
            formatted_phone = format_phone(new_phone)
            st.session_state.df.loc[len(st.session_state.df)] = [new_id, new_name, formatted_phone]
            st.success(f"✅ Entry added: {new_name} ({formatted_phone})")
            st.session_state.show_add_form = False

# View and Manage Table with row selection
st.subheader("👁️ View & Manage Data")
selected_rows = st.data_editor(
    st.session_state.df,
    num_rows="dynamic",
    use_container_width=True,
    key="data_table",
    column_config={"Phone": st.column_config.TextColumn(disabled=True)},
    disabled=["ID", "Name", "Phone"],
    hide_index=True,
)

# Send WhatsApp Messages
st.subheader("📤 Send WhatsApp Messages")
message = st.text_area("Type your message (use `{name}` and `{id}` for personalization)", height=100)

if st.button("📲 Send WhatsApp Message to Selected"):
    if selected_rows.empty:
        st.warning("⚠️ Please select rows in the table above.")
    else:
        for index, row in selected_rows.iterrows():
            id_ = row["ID"]
            name = row["Name"]
            phone = format_phone(row["Phone"])
            final_msg = message.replace("{name}", name).replace("{id}", str(id_))

            try:
                # Ensure that the message is sent instantly with the correct timing
                kit.sendwhatmsg_instantly(phone, final_msg, wait_time=15, tab_close=True, close_time=3)
                st.success(f"✅ Message sent to {name} ({phone})")
            except Exception as e:
                st.error(f"❌ Failed to send message to {name} ({phone}): {e}")

# Delete all data
if st.button("❌ Delete All Data"):
    st.session_state.df = pd.DataFrame(columns=["ID", "Name", "Phone"])
    st.success("🧹 All data deleted!")
