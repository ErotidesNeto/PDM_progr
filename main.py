import os
import subprocess
import sys
import time
import streamlit as st
from analise_ai import analisa_peticao_inicial
from construcao_doc import criar_novo_documento as criar_minuta
import json



# Função para salvar arquivos localmente
def save_uploadedfile(uploadedfile, filename):
    with open(filename, "wb") as f:
        f.write(uploadedfile.getbuffer())
    return filename

# Função para limpar arquivos locais
def clear_files(*files):
    for file in files:
        if file and os.path.exists(file):
            os.remove(file)

# Função principal da aplicação Streamlit
def main():
    st.set_page_config(page_title='Gerador de Contestação de Progressão', layout='centered', initial_sidebar_state='auto')
    
    st.title('Gerador de Contestação')
    st.subheader('Progressão Magistério')
    st.write("Arraste e solte o arquivo PDF da petição inicial na área abaixo.")
    
    st.markdown("---")

    # Inicializa os estados da sessão
    if 'peticao_inicial_path' not in st.session_state:
        st.session_state.peticao_inicial_path = None   
    if 'show_download_button' not in st.session_state:
        st.session_state.show_download_button = False
    if 'minuta_file_path' not in st.session_state:
        st.session_state.minuta_file_path = None
    if 'analize_time' not in st.session_state:
        st.session_state.generation_time = 0
    if 'generation_time' not in st.session_state:
        st.session_state.generation_time = 0   
    if 'resultado_analise' not in st.session_state:
        st.session_state.resultado_analise = None
    if 'resultado_atualizado' not in st.session_state:
        st.session_state.resultado_atualizado = {}

    # Força a atualização dos widgets de upload de arquivos
    if 'file_uploader_key' not in st.session_state:
        st.session_state.file_uploader_key = 0

    # # Área para Petição Inicial
    # peticao_inicial_file = st.file_uploader("Petição Inicial (max: 30 páginas)", type="pdf", accept_multiple_files=False, key=f"peticao_inicial_{st.session_state.file_uploader_key}")
    # if peticao_inicial_file:
    #     st.session_state.peticao_inicial_path = save_uploadedfile(peticao_inicial_file, 'peticao_inicial.pdf')
    #     st.success("Petição Inicial carregada com sucesso!")    
      
    # st.markdown("---")
    
    # # Botão para preencher formulário automaticamente
    # if st.button('Preencher com IA'):
    #     if st.session_state.peticao_inicial_path:
            
    #         start_time = time.time()
    #         with st.spinner('A IA está analisando'):                
    #             st.session_state.resultado_analise = analisa_peticao_inicial(st.session_state.peticao_inicial_path)              
    #             end_time = time.time()
    #             st.session_state.analize_time = end_time - start_time                
    #             st.success(f"Formulário preenchido pela IA em {st.session_state.analize_time:.2f} segundos!")
    #             json_resultado = json.dumps(st.session_state.resultado_analise, ensure_ascii=False, indent=4)
    #         #st.json(json_resultado)
                
    #     else:
    #         st.error('Por favor, carregue todos os arquivos necessários.')

    # # Pega os valores analisados para preencher automaticamente
    # resultado = st.session_state.resultado_analise if st.session_state.resultado_analise else {}
    
    # if resultado:
    #     st.write(f"Data do ingresso no cargo: {resultado.get('data_ingresso', '')}")
    #     st.write(f"Data da inatividade: {resultado.get('data_inatividade', '')}")
    #     st.write(f"Data da petição inicial: {resultado.get('data_peticao', '')}")
    
    # Checkbox para "Prova do vínculo"
    prova_vinculo = st.checkbox(
        'Prova do vínculo', 
        value=resultado.get('prova_vinculo', False)
        
    )
       
    # Checkbox para "Prazo Quinquenal desde a Inatividade"
    prazo_quinquenal_inatividade = st.checkbox(
        'Prazo de 5 anos ou mais entre a inatividade e o ajuizamento da ação', 
        value=resultado.get('prazo_quinquenal_inatividade', False)
    )

    # Checkbox para "Servidor efetivo"
    servidor_efetivo = st.checkbox(
        'Servidor efetivo', 
        value=resultado.get('servidor_efetivo', False)
    )

    # Checkbox para "Servidor Temporário ou não estável"
    servidor_nao_estavel = st.checkbox(
        'Servidor não estável', 
        value=resultado.get('servidor_nao_estavel', False)
    )

    # Checkbox para "Servidor Temporário "
    servidor_temporario = st.checkbox(
        'Servidor temporário', 
        value=resultado.get('servidor_temporario', False)
    )

    # Campo de texto para "Portaria"
    portaria = ""
    if servidor_temporario|servidor_nao_estavel:
        portaria = st.text_input(
            'Portaria', 
            value=resultado.get('portaria', "")
        )
    else:
        portaria = ''
    
    st.session_state.resultado_atualizado = {
        'prova_vinculo': prova_vinculo,
        'prazo_quinquenal_inatividade': prazo_quinquenal_inatividade,
        'servidor_temporario_nao_estavel': servidor_temporario|servidor_nao_estavel,
        'portaria': portaria
    }
    
    
    st.markdown("---")

    # Botão para gerar a minuta
    if st.button('Gerar Minuta'):
        start_time = time.time()
        with st.spinner('Gerando minuta...'):                
            st.session_state.minuta_file_path = criar_minuta(st.session_state.resultado_atualizado)
            end_time = time.time()
            st.session_state.generation_time = end_time - start_time
            st.session_state.show_download_button = True
            st.success(f'Minuta gerada com sucesso em {st.session_state.generation_time:.2f} segundos!')
    
    # Botão para baixar a minuta gerada
    if st.session_state.show_download_button and st.session_state.minuta_file_path:
        with open(st.session_state.minuta_file_path, 'rb') as f:
            st.download_button(label="Baixar Minuta", data=f, file_name='contestacao.docx', mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    
    st.markdown("---")

    # Botão para reiniciar
    if st.button('Reiniciar'):
        clear_files(st.session_state.peticao_inicial_path, st.session_state.minuta_file_path)
        
        # Remove as chaves do estado da sessão
        for key in ['peticao_inicial_path', 'show_download_button', 'minuta_file_path', 'generation_time', 'resultado_analise','resultado_atualizado']:
            if key in st.session_state:
                del st.session_state[key]
        
        # Incrementa a chave para forçar a atualização dos widgets de upload
        st.session_state.file_uploader_key += 1
        
        st.rerun()

if __name__ == '__main__':
    # Verifica se o script está congelado (executável)
    if getattr(sys, 'frozen', False):
        script_path = os.path.join(sys._MEIPASS, 'your_script.py')
        subprocess.run(['streamlit', 'run', script_path])
    else:
        main()
