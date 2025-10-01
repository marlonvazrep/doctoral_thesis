import os

# CONFIGURAÇÕES
caminho_labels = "/home/larcarn/RN/yolov8/datasets/ODUTF.misto/train/tlabels" # Substitua pelo seu caminho
num_classes = 21  # Defina quantas classes existem no seu dataset

def verificar_labels_yolo(pasta_labels, num_classes):
    arquivos_corrompidos = []

    for nome_arquivo in os.listdir(pasta_labels):
        if not nome_arquivo.endswith(".txt"):
            continue

        caminho_arquivo = os.path.join(pasta_labels, nome_arquivo)
        with open(caminho_arquivo, "r") as f:
            linhas = f.readlines()

            if len(linhas) == 0:
                print(f"[AVISO] Arquivo vazio: {nome_arquivo}")

            for i, linha in enumerate(linhas, 1):
                partes = linha.strip().split()

                if len(partes) != 5:
                    print(f"[ERRO] Linha mal formatada ({nome_arquivo}, linha {i}): {linha.strip()}")
                    arquivos_corrompidos.append(nome_arquivo)
                    continue

                try:
                    class_id = int(partes[0])
                    bbox = list(map(float, partes[1:]))

                    if not (0 <= class_id < num_classes):
                        print(f"[ERRO] class_id inválido ({nome_arquivo}, linha {i}): {class_id}")
                        arquivos_corrompidos.append(nome_arquivo)

                    for valor in bbox:
                        if not (0.0 <= valor <= 1.0):
                            print(f"[ERRO] Valor fora do intervalo 0-1 ({nome_arquivo}, linha {i}): {bbox}")
                            arquivos_corrompidos.append(nome_arquivo)
                            break

                except ValueError:
                    print(f"[ERRO] Valores não numéricos ({nome_arquivo}, linha {i}): {linha.strip()}")
                    arquivos_corrompidos.append(nome_arquivo)

    print("\nVerificação concluída.")
    if arquivos_corrompidos:
        print(f"\nTotal de arquivos com problemas: {len(set(arquivos_corrompidos))}")
    else:
        print("Nenhum problema encontrado.")

# Execute a função
verificar_labels_yolo(caminho_labels, num_classes)