from langchain.prompts import PromptTemplate
from langchain_anthropic import ChatAnthropic
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.output_parsers import JsonOutputParser
import json


load_dotenv()

#FLAGS: PROVA_VÍNCULO (a parte comprovou o vínculo=True), PRAZO_QUINQUENAL_INATIVIDADE (já se passaram 5 anos desde a passagem para inatividade=True), SERVIDOR_TEMPORARIO_NAO_ESTAVEL (o servidor não é estável ou é temporário=True)
#CAMPOS: [PORTARIA] --> Indicar portaria de admissão do servidor
def analisa_peticao_inicial(peticao_inicial):
    
    template=PromptTemplate.from_template(
    """
    Você é um assistente jurídico que auxilia na análise de petições iniciais de processos judiciais.
    O texto abaixo é de uma petição inicial. Trata-se de ação movida por servidor(a) inativo(a) com o objetivo de obter progressão funcional, bem como seus reflexos aos proventos de aposentadoria, prevista na Lei 5.351/1986, antigo Estatuto do Magistério Público Estadual, vigente até o ano 2010, quando substituído pelo novo estatuto trazido pela Lei estadual nº 7. 442/2010.
    No entanto, devemos demonstrar que é manifesta a ausência do direito alegado, devendo ser julgados improcedentes todos os pedidos.
    Para tanto, identifique: (1) se a parte autora comprovou o vínculo com documento, (2) se já se passaram 5 anos desde a passagem para inatividade, (3) se o servidor é efetivo, se é ou não estável ou é servidor temporário.
    Extraia também o número e demais dados da portaria de admissão do servidor, se houver.
        
    Petição inicial:

    //{peticao_inicial}//

    Retorne apenas uma resposta no formato JSON com as seguintes chaves:    

    "prova_vinculo": true ou false,
    "tipo_vinculo": vínculo que alega ter tido com o Estado do Pará (efetivo, temporário, comissionado, etc)
    "data_peticao": data da petição inicial
    "data_ingresso": data do ingresso no cargo
    "data_inatividade": data da passagem para inatividade (aposentadoria, etc)
    "prazo_quinquenal_inatividade": true ou false, //se passou 5 anos ou mais entre a data da inatividade e a data da petição inicial
    "servidor_temporario_nao_estavel": true ou false, 
    "servidor_efetivo": true ou false,
    "servidor_temporario": true ou false,
    "servidor_nao_estavel": true ou false, // se o servidor apesar de ser efetivo, não é estável
    "portaria": identificação da portaria de admissão do servidor (número, data - ex. Portaria SEDUC nº 123, de 01/01/2020), se houver. Não invente.
    
    """)

    llm = ChatAnthropic(model='claude-3-haiku-20240307')
    parser=JsonOutputParser()
    chain=template|llm|parser
    loader=PyPDFLoader(peticao_inicial)
    docs=loader.load()

    if len(docs)<30:
        resposta_chain=chain.invoke(docs)    
        return resposta_chain
    else: 
        raise ValueError ("Erro: o arquivo da petição inicial não pode ter mais que 30 páginas")

