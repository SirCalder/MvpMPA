import os
import json
import requests
import time

def chamar_api_gemini(model_name, prompt_sistema, conteudo_bruto, api_key):
   
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    payload = {
        "systemInstruction": {
            "parts": [{"text": prompt_sistema}]
        },
        "contents": [
            {"parts": [{"text": f"Aqui estão os dados brutos do OCR para estruturar:\n\n{conteudo_bruto}"}]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    
   
    delays = [1, 2, 4, 8, 16]
    for delay in delays:
        resposta = requests.post(url, headers=headers, json=payload)
        if resposta.status_code not in [503, 429]:
            return resposta
        time.sleep(delay)
        
    return requests.post(url, headers=headers, json=payload)

def estruturar_dados_mercado(arquivo_entrada, arquivo_saida, api_key, nome_mercado, nome_sessao):
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: O arquivo {arquivo_entrada} não foi encontrado.")
        return
        
    with open(arquivo_entrada, "r", encoding="utf-8") as f:
        conteudo_bruto = f.read()

    prompt_sistema = (
        "Você é um assistente especialista em estruturação de dados de varejo. "
        "Sua tarefa é receber um log bruto de OCR de prateleiras de supermercado e transformá-lo em um JSON limpo.\n\n"
        "Regras cruciais de limpeza:\n"
        "1. Corrija abreviações ou erros do OCR para nomes reais (ex: 'Spril' ou 'Sprit' vira 'Sprite', 'Guapana' vira 'Guaraná', 'Voade' vira 'Unidade').\n"
        "2. Identifique o produto, a marca, o volume/peso (ex: 2L, 500ml) e o preço correto.\n"
        "3. Ignore códigos numéricos avulsos que pareçam códigos de barras ou códigos internos do mercado.\n"
        "4. Agrupe leituras repetidas do mesmo produto em uma única entrada no catálogo final, mantendo o preço mais nítido encontrado.\n"
        "5. Identifique se o item parece uma promoção (preços terminados em 9 ou indicações explícitas).\n\n"
        "Formato de Saída esperado (Apenas o array JSON puro):\n"
        "[\n"
        "  {\n"
        "    \"produto\": \"Nome do Produto Corrigido\",\n"
        "    \"marca\": \"Marca\",\n"
        "    \"volume\": \"2L\",\n"
        "    \"preco\": 10.45,\n"
        "    \"promocao\": false\n"
        "  }\n"
        "]"
    )


    modelos_fallback = [
        "gemini-2.5-flash-lite",     
        "gemini-2.5-flash",          
        "gemini-1.5-flash-latest"    
    ]

    resposta_valida = None

    for modelo in modelos_fallback:
        print(f"Tentando enviar dados para o modelo: {modelo}...")
        resposta = chamar_api_gemini(modelo, prompt_sistema, conteudo_bruto, api_key)
        
        if resposta.status_code == 200:
            print(f"-> Sucesso na conexão com {modelo}!")
            resposta_valida = resposta
            break
        else:
            print(f"-> Aviso: {modelo} apresentou instabilidade (Erro {resposta.status_code}).")
            time.sleep(2) 

    try:
        
        if not resposta_valida:
            resposta.raise_for_status() 

        dados = resposta_valida.json()
        texto_resposta = dados['candidates'][0]['content']['parts'][0]['text'].strip()
        
        #LimpezaDeMarkdown 
        if texto_resposta.startswith("```json"):
            texto_resposta = texto_resposta.replace("```json", "").replace("```", "").strip()
        elif texto_resposta.startswith("```"):
            texto_resposta = texto_resposta.replace("```", "").strip()

        dados_json = json.loads(texto_resposta)
        
        
        for item in dados_json:
            item["mercado"] = nome_mercado
            item["sessao"] = nome_sessao
        
        
        with open(arquivo_saida, "w", encoding="utf-8") as f_out:
            json.dump(dados_json, f_out, indent=2, ensure_ascii=False)
            
        print(f"\nSucesso! Dados salvos em: {arquivo_saida}")
        print(f"Produtos catalogados no {nome_mercado} ({nome_sessao}): {len(dados_json)}")
        
    except Exception as e:
        print(f"Erro fatal no processamento: {e}")
        if 'resposta' in locals() and resposta:
            print(f"Detalhes do servidor: {resposta.text}")

if __name__ == "__main__":
    ARQUIVO_TXT = "dados_brutos_mercado.txt"
    ARQUIVO_JSON_FINAL = "catalogo_final.json"
    MINHA_API_KEY = "COLOQUE_SUA_CHAVE_AQUI"
    
    MERCADO_ALVO = "Mercado São Paulo"
    SESSAO_ALVO = "Refrigerantes"
    
    if not MINHA_API_KEY or MINHA_API_KEY == "COLOQUE_SUA_CHAVE_AQUI":
        print("Por favor, insira uma API Key válida.")
    else:
        estruturar_dados_mercado(ARQUIVO_TXT, ARQUIVO_JSON_FINAL, MINHA_API_KEY, MERCADO_ALVO, SESSAO_ALVO)
