import streamlit as st
import time

st.set_page_config(page_title="Streamlit Demo", page_icon=":robot_face:", layout="wide")
st.title("Streamlit Demo")
st.caption("This is a simple Streamlit demo application.")
st.write("Welcome to the Streamlit Demo!")
section = st.sidebar.radio("Choose an option:", [
    "Text And layout", 
    "Widgets & Re-run", 
    "Session State",
    "Chat Preview"
    ])

if section == "Text And layout":
    st.header("Text and Layout")
    st.write("This section demonstrates text and layout features in Streamlit.")
    st.subheader("Subheader Example")
    st.markdown("You can use **Markdown** to format your text.")
    st.latex(r"e^{i\pi} + 1 = 0")
    st.code("print('Hello, Streamlit!')", language="python")

    st.write("Hello World!")
    left,right = st.columns(2)
    with left:
        st.metric(label="Temperature", value="70 °F", delta="1.2 °F")
    with right:
        st.info("This is an info message.")

    st.divider()

    st.subheader("Widgets & Re-run")

    st.code("""
    import streamlit as st
    st.title("Widgets & Re-run)""",language="python")



elif section == "Widgets & Re-run":
    st.header("Widgets & Re-run")
    st.markdown("""
        Widgets allow users to interact with your app. You can use various widgets like sliders, buttons, and text inputs. When a widget's value changes, Streamlit automatically reruns the script from top to bottom, allowing you to update the app's state dynamically.
    """)

    name = st.text_input(label="Enter your name:",placeholder="Type your name here...")
    mood   = st.selectbox(label="How are you feeling today?", options=["Happy", "Sad", "Excited", "Bored"])
    slider  = st.slider(label="Select a number:", min_value=0, max_value=100, value=50)
    print(name, mood, slider)

    st.divider()

    if st.button("Say Hello"):
        st.success(f"Hello, {name}! You are feeling {mood} and selected the number {slider}.")

    if st.button("Increment Number"):
        slider += 1
        st.success(f"Incremented number: {slider}")


elif section == "Session State":
    st.header("Session State")
    st.markdown("""
        Streamlit's session state allows you to store and manage stateful information across reruns of your app. This is useful for maintaining user inputs, counters, or any other data that needs to persist between interactions."""
    )


    # session is a dictionary-like object that allows you to store and retrieve values across reruns of your app. You can use it to keep track of user inputs, counters, or any other data that needs to persist between interactions.
    if "click_count" not in st.session_state:
        # initialize the click count in session state
        st.session_state.click_count = 0

    if "note" not in st.session_state:
        # initialize the note list in session state
        st.session_state.note = []

    col_a,col_b,col_c = st.columns(3)
    with col_a:
        if st.button("Increment"):
            st.session_state.click_count += 1
    with col_b:
        if st.button("Decrement"):
            st.session_state.click_count -= 1
    with col_c:
        st.metric(label="Click Count", value=st.session_state.click_count)

    note = st.text_input(label="Enter a note:", placeholder="Type your note here...")
    if st.button("Save Note") and note.strip() != "":
        st.session_state.note.append(note)

    if st.session_state.note:
        st.subheader("Saved Notes:")
        for idx, note in enumerate(st.session_state.note):
            st.write(f"{idx + 1}. {note}")


elif section == "Chat Preview":
    st.header("Chat Preview")
    st.markdown("""
        This section demonstrates a simple chat interface using Streamlit. You can enter messages, and they will be displayed in a chat-like format.
    """)

    if "chat_log" not in st.session_state:
        st.session_state.chat_log = []

    for entry in st.session_state.chat_log:
        if entry["role"] == "user":
            with st.chat_message("user"):
                st.write(entry["content"])
        else:
            with st.chat_message("assistant"):
                st.write(entry["content"])
    

    prompt = st.chat_input("Type your message here...")

    if prompt:
        st.session_state.chat_log.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                time.sleep(2) 
            st.write("This is a placeholder response from the assistant. You can replace this with actual AI responses.")
            st.session_state.chat_log.append({"role": "assistant", "content": "This is a placeholder response from the assistant. You can replace this with actual AI responses."})
    
