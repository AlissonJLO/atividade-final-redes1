import socket
import hashlib

def calcula_hash(caminho):
    hash_sha256 = hashlib.sha256() #cria o objeto sha256
    with open(caminho, "rb") as f: #abre o arquivo em modo binário
        while True:
            pedaco = f.read(4096) #lê 4096 bytes por vez
            if not pedaco: #se acabou de ler para
                break
            hash_sha256.update(pedaco) #adiciona o pedaço e atualiza o hash
    return hash_sha256.hexdigest() #retorna o hash em texto hexadecimal

IP = '0.0.0.0'
porta = 5000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

sock.bind((IP, porta))
sock.listen()

print('Aguardando conexões...')

while True:

    conexao, ip = sock.accept()

    try:

        tamanho_cabecalho_bytes = conexao.recv(4) #recebe o tamanho do cabeçalho nome|hash|tamanho em 4 bytes
        tamanho_cabecalho_decimal = int.from_bytes(tamanho_cabecalho_bytes, byteorder='big')
        string_de_bytes = b''

        while len(string_de_bytes) < tamanho_cabecalho_decimal: #tcp envia o que está disponível no buffer então o while
            parte = conexao.recv(tamanho_cabecalho_decimal - len(string_de_bytes))
            if not parte:
                raise ConnectionError("Cliente desconectou no cabeçalho")
            string_de_bytes = string_de_bytes + parte
        
        cabecalho = string_de_bytes.decode() #decode converte bytes em string
        nome, hash_cliente, tamanho_arquivo = cabecalho.split('|') #divide a string que tem '|' troca isso por ',' e coloca em uma lista
        tamanho_arquivo = int(tamanho_arquivo)
        bytes_recebidos = b''

        while len(bytes_recebidos) < tamanho_arquivo:
            parte = conexao.recv(min(4096, tamanho_arquivo - len(bytes_recebidos))) #min retorna o menor valor. 4096 ou o outro
            if not parte:
                raise ConnectionError("Cliente desconectou no arquivo")
            bytes_recebidos += parte

        #salvar o arquivo
        caminho = f"recebido_{nome}"
        with open(caminho, "wb") as f:
            f.write(bytes_recebidos)

        #calcular o hash
        hash_calculado = calcula_hash(caminho)

        #comparar hashes
        if hash_calculado == hash_cliente:
            conexao.sendall("hash certo".encode())
            print("Arquivo íntegro.")
        else:
            conexao.sendall("hash errado".encode())
            print("Hash inválido!")

    finally:
        conexao.close()
