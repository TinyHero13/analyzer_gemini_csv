import streamlit as st
import google.generativeai as genai
from contextlib import redirect_stdout
from io import StringIO
import pandas as pd

load_dotenv()

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    'candidate_count': 1,
    'temperature': 0.5
}

safety_settings = {
    'HARASSMENT': 'BLOCK_NONE',
    'HATE': 'BLOCK_NONE',
    'SEXUAL': 'BLOCK_NONE',
    'DANGEROUS': 'BLOCK_NONE'
}

model = genai.GenerativeModel(model_name='gemini-1.0-pro',
                              generation_config=generation_config,
                              safety_settings=safety_settings)

st.write('Analize planilhas')

uploaded_file = st.file_uploader('Entre com o arquivo', type=["csv", "xlsx"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        st.chat_message(message['role']).markdown(message['content'])

    question = st.chat_input("Enter the message")

    if question:
        st.chat_message('user').markdown(question)

        st.session_state.messages.append({'role': 'user', 'content': question})

        response = model.generate_content(f"""
                                          Você é um analista de dados e precisa analisar csvs, montar gráficos, com relação da entrada do usuário.
                                          Quando o usuário escrever, 'Python:' você deverá fornecer um código em Python, caso não tenha 'Python', apenas escreva a resposta.
                                          O nome do dataframe é df, logo já pode escrever os códigos em cima do df.
                                          Se falarem para construir um gráfico, utilize a biblioteca ploty, e em vez de utilizar fig.show(), utilize st.plotly_chart(fig).
                                          Aqui está o prompt do usuário: {question}
                                          Aqui está dataframe (csv): {df}""").text

        if "```python" in response:
            response = response.strip("```python").strip("\n")

            with StringIO() as output_buffer:
                with redirect_stdout(output_buffer):
                    exec(response)
                captured_output = output_buffer.getvalue()

            st.chat_message('Assistant').markdown(captured_output)

            st.session_state.messages.append({'role': 'assistant', 'content': captured_output})

        else:
            captured_output = response
            st.chat_message('Assistant').markdown(captured_output)

            st.session_state.messages.append({'role': 'assistant', 'content': captured_output})
