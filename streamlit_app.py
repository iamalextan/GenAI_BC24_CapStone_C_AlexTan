import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Alex - start 1
    def get_completion(prompt, model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1):
        messages = [{"role": "user", "content": prompt}]
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            n=1
        )
        return response.choices[0].message.content
    # Alex - end 1

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            #model="gpt-3.5-turbo",
            model="gpt-4o-mini", temperature=0, top_p=1.0, max_tokens=1024, n=1,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})

#use beautifulsoap to scrape the web page: https://www.cpf.gov.sg/member/growing-your-savings/earning-higher-returns/earning-attractive-interest
#to get the latest interest rates
import requests
from bs4 import BeautifulSoup
import pandas as pd

bs4 = st.checkbox("Use BeautifulSoup to scrape the web page: https://www.cpf.gov.sg/member/growing-your-savings/earning-higher-returns/earning-attractive-interest to get the latest interest rates")

if bs4:
    url = 'https://www.cpf.gov.sg/member/growing-your-savings/earning-higher-returns/earning-attractive-interest'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all('table')[0]
    df = pd.read_html(str(table))
    df = df[0]
    df = df.dropna()
    df.columns = df.iloc[0]
    df = df[1:]
    df = df.reset_index(drop=True)
    df = df.rename(columns={'Account': 'Account Type', 'Current': 'Current Rate', 'From': 'From Date', 'To': 'To Date'})
    df['From Date'] = pd.to_datetime(df['From Date'])
    df['To Date'] = pd.to_datetime(df['To Date'])
    df['Current Rate'] = df['Current Rate'].str.replace('%', '').astype(float)
    df = df.sort_values(by='From Date', ascending=False)
    df = df.reset_index(drop=True)
    df = df.drop(columns=['From Date', 'To Date'])
    df = df.set_index('Account Type')

    st.write(df)

# Show a placeholder while the chatbot is loading.
if openai_api_key and not st.session_state.messages:
    st.info("Please start the conversation by typing a message.", icon="💬")