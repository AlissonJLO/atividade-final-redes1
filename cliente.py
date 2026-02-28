import sys
import socket
import hashlib
import os

def calcular_hash(caminho_arquivo):
    """Calcula o hash SHA-256 do arquivo em blocos para não estourar a RAM"""
    sha256_hash = hashlib.sha256()
    with open(caminho_arquivo, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def main():
    # Valida a sintaxe exigida: python3 cliente.py <ip> <arquivo>
    if len(sys.argv) != 3:
        print("Uso correto: python3 cliente.py <ip-do-servidor> <arquivo>")
        sys.exit(1)

    ip_servidor = sys.argv[1]
    caminho_arquivo = sys.argv[2]
    porta_servidor = 5000  # Você pode combinar essa porta com quem for fazer o servidor

    if not os.path.exists(caminho_arquivo):
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        sys.exit(1)

    nome_arquivo = os.path.basename(caminho_arquivo)
    arquivo_hash = calcular_hash(caminho_arquivo)
    tamanho_arquivo = os.path.getsize(caminho_arquivo)

    print(f"[*] Preparando envio: {nome_arquivo}")
    print(f"[*] Hash SHA-256: {arquivo_hash}")

    try:
        # Criação do Socket TCP
        cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente_socket.connect((ip_servidor, porta_servidor))

        # Monta um cabeçalho simples: NOME|HASH|TAMANHO
        cabecalho = f"{nome_arquivo}|{arquivo_hash}|{tamanho_arquivo}".encode('utf-8')

        # Envia primeiro o tamanho do cabeçalho (4 bytes), depois o cabeçalho em si
        cliente_socket.sendall(len(cabecalho).to_bytes(4, byteorder='big'))
        cliente_socket.sendall(cabecalho)

        # Envia os bytes do arquivo
        print("[*] Enviando dados...")
        with open(caminho_arquivo, "rb") as f:
            while chunk := f.read(4096):
                cliente_socket.sendall(chunk)

        print("[+] Arquivo enviado com sucesso!")

    except ConnectionRefusedError:
        print("[-] Erro: Não foi possível conectar ao servidor. Ele está rodando?")
    except Exception as e:
        print(f"[-] Erro inesperado: {e}")
    finally:
        cliente_socket.close()

if __name__ == "__main__":
    main()