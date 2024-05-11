import streamlit as st
import google.generativeai as genai
from contextlib import redirect_stdout
from io import StringIO
import pandas as pd

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

st.title('Assistente para analisar planilhas')
st.write('''
Este é um assistente virtual projetado para auxiliar na análise de planilhas. 

Se deseja que ele execute cálculos, crie gráficos ou realize outras tarefas, insira "Calcule:" antes da sua instrução. 

Ele suporta arquivos nos formatos .csv e .xlsx

Para uma compreensão mais clara da linguagem Python, após enviar outra mensagem, o gráfico ou tabela será substituido pelo código em Python correspondente.

Exemplos de prompt:

- Sobre o que é o csv?

- Calcule: quantas linhas tem no csv?

- Calcule: mostre as 5 primeiras linhas do csv

- Calcule: qual a média/soma da coluna x

- Calcule: monte um gráfico da coluna x por sua quantidade
         ''')

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
                                        Como analista de dados, você é encarregado de analisar conjuntos de dados em formato CSV e criar visualizações com base nas solicitações dos usuários. 
                                        Quando o usuário inserir 'Calcule:', você deve fornecer um código em Python para realizar operações no DataFrame, utilizando 'df' seguido do código específico para realizar a operação desejada, não precisa ler o csv, pois ele já está dentro da variavel df.
                                        Utilize o st.write() para mostrar o código.
                                        Por exemplo: st.write(df.shape[0]), st.write(df.head())
                                        
                                        Se o usuário perguntar quantas linhas tem no csv, escreva: 
                                        
                                        Se o usuário não inserir 'Calcule:', você deve simplesmente responder à consulta.

                                        Se você for solicitado a construir um gráfico, utilize a biblioteca Plotly e, em vez de exibir a figura diretamente com fig.show(), utilize st.plotly_chart(fig).
                                        Onde que se pedirem pela quantidade você deverá fazer um value_counts da coluna específicada.
                                        Exemplo:
                                        import plotly.express as px
                                        value_counts = df['Item'].value_counts()
                                        fig = px.bar(x=value_counts.index, y=value_counts.values
                                        st.plotly_chart(fig)
                                        
                                        Outros exemplos:
                                        - Gráfico de barras
                                        import plotly.express as px
                                        fig = px.bar(df, x='year', y='pop')
                                        st.plotly_chart(fig)
                                        
                                        - Gráfico de rosca
                                        import plotly.express as px
                                        fig = px.pie(df, values='pop', names='country')
                                        st.plotly_chart(fig)
                                        
                                        
                                        Se perguntarem quais são as colunas responda com df.columns.to_list()
                                        
                                        Se pedirem para mostrar as linhas do df utilize st.write(df), no caso se for primeiras linhas, st.write(df.head()), se for as últimas linhas st.write(df.tail())
                                        
                                        Aqui está o prompt do usuário: {question}
                                        Aqui está dataframe (csv): {df}""").text
        if "```python" in response:
            response = response.strip("```python").strip("\n")
            print(response)
            
            with StringIO() as output_buffer:
                with redirect_stdout(output_buffer):
                    exec(response)
                captured_output = output_buffer.getvalue()
                
            st.chat_message('Assistant').markdown(captured_output)

            if captured_output == '':
                st.session_state.messages.append({'role': 'assistant', 'content': f'O código utilizado para sua montagem foi\n{response}'})
            else:
                st.session_state.messages.append({'role': 'assistant', 'content': captured_output})
        else:
            captured_output = response
            st.chat_message('Assistant').markdown(captured_output)

            st.session_state.messages.append({'role': 'assistant', 'content': captured_output})
