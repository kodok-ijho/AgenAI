import streamlit as st 
from pandasai.llm.openai import OpenAI
from dotenv import load_dotenv
import os
import pandas as pd # type: ignore
from pandasai import SmartDataframe 

load_dotenv()


openai_api_key = "" #os.getenv("OPENAI_API_KEY")


def chat_with_csv(df,prompt):
    llm = OpenAI(api_token=openai_api_key, model="gpt-3.5-turbo", temperature=0.9)
    #pandas_ai = OpenAI(llm)
    #result = pandas_ai.run(df, prompt=prompt)
    pandas_ai = SmartDataframe(df, config={"llm": llm})
    result = pandas_ai.chat(prompt)
    #print(result)
    return st.write(result)

st.set_page_config(layout='wide')

st.title("ChatCSV powered by LLM")

input_csv = st.file_uploader("Upload your CSV file", type=['csv'])

if input_csv is not None:

        col1, col2 = st.columns([1,1])

        with col1:
            st.info("CSV Uploaded Successfully")
            data = pd.read_csv(input_csv)
            st.dataframe(data, use_container_width=True)

        with col2:

            st.info("Chat Below")
            
            input_text = st.text_area("Enter your query")

            if input_text is not None:
                if st.button("Chat with CSV"):
                    if input_text:
                         with st.spinner("Generatin response..."):
                             st.info("Your Query: "+input_text)
                             #result = chat_with_csv(data, input_text)
                             #st.success(result)
                             chat_with_csv(data, input_text)
                    #st.info("Your Query: "+input_text)
                    #result = chat_with_csv(data, input_text)
                    #st.success(result)
