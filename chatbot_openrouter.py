import streamlit as st
import pandas as pd
#from your_script import chat_analysis_buy # Import your existing function

# 1. Load your Project Data
@st.cache_data
def load_data():
    return pd.read_csv(fake_data.csv) # Or your JSON mapping

df = load_data()

# 2. Sidebar for Inputs
st.sidebar.title('Real Estate Analysis')
selected_county = st.sidebar.selectbox('Select a County', df['county'].unique())
county_data = df[df['county'] == selected_county].iloc[0]

# 3. Chat Interface
st.title('Buy vs Rent Assistant')
if messages not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message[role]):
        st.markdown(message[content])

# React to user input
if prompt == st.chat_input('Ask about the 5 percent rule or county data...'):
    # Display user message
    st.chat_message(user).markdown(prompt)
    st.session_state.messages.append({role user, content prompt})

    # Prepare context for your existing function
    # We pass the relevant county data into the prompt context
    context = fCounty {selected_county}, Rent {county_data['rent_2br']}, Price {county_data['median_price']}
    full_query = fContext {context}. Question {prompt}

    # Call your OpenRouter function
    with st.spinner(Analyzing...):
        # Note Modified your function call slightly to match your script's needs
        response_json = chat_analysis_buy(full_query, selected_county, 2026)
        
        # Extract the text from your JSON response object
        answer = response_json.get(analysis, response_json.get(answer, Error processing data.))

    # Display assistant response
    with st.chat_message(assistant):
        st.markdown(answer)
    st.session_state.messages.append({role assistant, content answer})