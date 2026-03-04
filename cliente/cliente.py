import sys
import socket
import hashlib
import os

def calcula_hash(caminho):
    hash_sha256 = hashlib.sha256()
    with open(caminho, "rb") as f:
        while True:
            pedaco = f.read(4096)
            if not pedaco:
                break
            hash_sha256.update(pedaco)
    return hash_sha256.hexdigest()

def main():
    if len(sys.argv) != 3:
        print("Uso: python3 cliente.py <ip-do-servidor> <arquivo>")
        sys.exit(1)

    ip = sys.argv[1]
    arquivo = sys.argv[2]
    porta = 5000

    if not os.path.exists(arquivo):
        print(f"Erro: o arquivo '{arquivo}' nao existe.")
        sys.exit(1)

    nome = os.path.basename(arquivo)
    hash_arquivo = calcula_hash(arquivo)
    tamanho = os.path.getsize(arquivo)

    print(f"Arquivo: {nome}")
    print(f"Hash: {hash_arquivo}")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, porta))

        info = f"{nome}|{hash_arquivo}|{tamanho}".encode('utf-8')
        sock.sendall(len(info).to_bytes(4, byteorder='big'))
        sock.sendall(info)

        print("Enviando...")
        with open(arquivo, "rb") as f:
            while True:
                dados = f.read(4096)
                if not dados:
                    break
                sock.sendall(dados)

        print("Sucesso! Arquivo enviado.")

    except ConnectionRefusedError:
        print("Erro de conexao: o servidor ta rodando?")
    except Exception as erro:
        print(f"Deu ruim na rede: {erro}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()