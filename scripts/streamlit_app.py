# library imports
import streamlit as st
from streamlit_chat import message
import requests
import json

def run_UI():
    """
    This function runs the streamlit app
    
    Args:
        None
    
    Returns:
        None
    """

    # setting page title and header
    st.set_page_config(page_title="Duke ChatBot", page_icon=":robot_face:", layout="wide")

    col_1, col_2 = st.columns([10,90])
    with col_1:
        st.image("logo.png", use_column_width="auto")
    with col_2:
        st.title("Duke ChatBot")
        st.markdown("##### A chatbot that can answer your questions about Pratt School of Engineering!")

    st.divider()

    # initialise session state variables
    if 'generated' not in st.session_state:
        st.session_state['generated'] = []
    if 'past' not in st.session_state:
        st.session_state['past'] = []
    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    # generate a response
    def generate_response(prompt):
        st.session_state['messages'].append({"role": "user", "content": prompt})

        completion = requests.get('http://0.0.0.0:8060/chat_v2/'+str(prompt), headers={"api-key": api_key}).json()
        response = completion["choices"][0]["text"]
        st.session_state['messages'].append({"role": "assistant", "content": response})
        return response

    # container for chat history
    response_container = st.empty()
    
    # container for text box
    container = st.container()

    # form for text box
    with container:
        with st.form(key='my_form', clear_on_submit=True):
            #user_input = st.text_area("You:", key='input', height=10)
            col1, col2 = st.columns([80,20])
            with col1:
                user_input = st.text_input("Ask me anything...", key='input')
            with col2:
                st.write("")
                st.write("")
                submit_button = st.form_submit_button(label='Send', use_container_width=True)

        if submit_button and user_input:
            output = generate_response(user_input)
            st.session_state['past'].append(user_input)
            st.session_state['generated'].append(output)

    if st.session_state['generated']:
        with response_container.container():
            for i in range(len(st.session_state['generated'])):
                message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
                message(st.session_state["generated"][i], key=str(i))

    # reset everything
    if st.button("Clear Chat"):
        response_container.empty()
        st.session_state['generated'] = []
        st.session_state['past'] = []
        st.session_state['messages'] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

if __name__ == '__main__':
    config = json.load(open("../config.json"))
    api_key = config["api_key"]
    run_UI()