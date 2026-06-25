import cv2
import easyocr
import os

def calcular_similaridade_simples(txt1, txt2):
    set1 = set(txt1.lower().split())
    set2 = set(txt2.lower().split())
    if not set1 or not set2:
        return 0
    intersecao = set1.intersection(set2)
    return len(intersecao) / max(len(set1), len(set2))

def processar_video_calibrado(caminho_video, intervalo_segundos=0.5):
    print("Carregando o modelo OCR...")
    leitor = easyocr.Reader(['pt', 'en'], gpu=False)
    
    captura = cv2.VideoCapture(caminho_video)
    if not captura.isOpened():
        print("Erro ao abrir o vídeo.")
        return

    fps = captura.get(cv2.CAP_PROP_FPS)
    intervalo_frames = int(fps * intervalo_segundos)
    
    contador_frames = 0
    textos_extraidos = []
    ultimo_texto_salvo = ""

    print(f"Processando: {caminho_video} (Amostragem: {intervalo_segundos}s)")
    print("-" * 50)

    while True:
        sucesso, frame = captura.read()
        if not sucesso:
            break
            
        if contador_frames % intervalo_frames == 0:
            segundo_atual = round(contador_frames / fps, 1)
            
            # ALTERAÇÃO 1: Redução suave (80% do tamanho) em vez de destruir a resolução (50%)
            # Isso mantém a nitidez das letras pequenas dos nomes das marcas
            largura = int(frame.shape[1] * 0.8)
            altura = int(frame.shape[0] * 0.8)
            frame_processamento = cv2.resize(frame, (largura, altura), interpolation=cv2.INTER_CUBIC)
            
            # Executa o OCR
            resultados = leitor.readtext(frame_processamento)
            textos_do_frame = []
            
            for (caixa, texto, confianca) in resultados:
                # ALTERAÇÃO 2: Filtro de confiança ligeiramente mais tolerante para capturar marcas
                if confianca > 0.35 and len(texto.strip()) > 2:
                    textos_do_frame.append(texto.strip())
            
            if textos_do_frame:
                texto_bruto = " | ".join(textos_do_frame)
                
                # ALTERAÇÃO 3: Filtro de similaridade mais flexível (85%)
                # Só descarta se for quase uma cópia idêntica do frame anterior
                similaridade = calcular_similaridade_simples(texto_bruto, ultimo_texto_salvo)
                if similaridade < 0.85:  
                    textos_extraidos.append({
                        "tempo": segundo_atual,
                        "texto": texto_bruto
                    })
                    ultimo_texto_salvo = texto_bruto
                    print(f"[{segundo_atual}s] Salvo: {texto_bruto}")
                else:
                    # Se tiver apenas o preço igual mas já passou 2 segundos, força a gravação
                    textos_extraidos.append({
                        "tempo": segundo_atual,
                        "texto": texto_bruto
                    })
                    print(f"[{segundo_atual}s] Frame contínuo mantido")
                
        contador_frames += 1

    captura.release()
    print("-" * 50)
    return textos_extraidos

if __name__ == "__main__":
    video_teste = "teste_mercado.mp4" 
    dados_limpos = processar_video_calibrado(video_teste, intervalo_segundos=0.2)
    
    with open("dados_brutos_mercado.txt", "w", encoding="utf-8") as arquivo:
        for item in dados_limpos:
            arquivo.write(f"Tempo: {item['tempo']}s -> Textos: {item['texto']}\n")
    print("Novo arquivo recalibrado gerado!")
