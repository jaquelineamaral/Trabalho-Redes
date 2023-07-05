import socket
import time

# Configurações do servidor
server_ip = '127.0.0.1'
server_port = 8081

# Criação do socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Configurações do buffer de pacotes
buffer_size = 10  # Tamanho do buffer em pacotes
packet_size = 1024  # Tamanho máximo de cada pacote em bytes

# Dados de exemplo a serem enviados
messages = [
    "Mensagem 1",
    "Mensagem 2",
    "Mensagem 3",
    "Mensagem 4",
    "Mensagem 5",
    "Mensagem 6",
    "Mensagem 7",
    "Mensagem 8",
    "Mensagem 9",
    "Mensagem 10",
]

# Variáveis de controle de timeout e retransmissão
timeout = 2.0  # Tempo em segundos para timeout
last_ack_received = -1  # Último ACK recebido
packets_sent = []  # Lista para armazenar os pacotes enviados

# Função para enviar pacotes
def send_packet(packet, sequence_number):
    client_socket.sendto(packet.encode(), (server_ip, server_port))
    print("Enviado pacote com sequência", sequence_number)

# Enviar pacotes
for i, message in enumerate(messages):
    sequence_number = i % (buffer_size * 2)  # Números de sequência entre 0 e 19
    packet = f"{sequence_number}|{message}"
    send_packet(packet, sequence_number)
    packets_sent.append((packet, sequence_number))

# Definir o timeout inicial
start_time = time.time()
timeout_expired = False

# Aguardar ACKs e tratar timeouts e retransmissões
while last_ack_received < len(messages) - 1:
    try:
        client_socket.settimeout(timeout)

        # Receber ACK do servidor
        ack_packet, _ = client_socket.recvfrom(packet_size)
        ack_number = int(ack_packet.decode())
        print("Recebido ACK:", ack_number)

        # Verificar se o ACK é válido
        if ack_number > last_ack_received:
            last_ack_received = ack_number
            timeout_expired = False

    except socket.timeout:
        if not timeout_expired:
            print("Timeout: retransmitindo pacotes a partir da sequência", last_ack_received + 1)
            timeout_expired = True

            i = last_ack_received + 1
            sequence_number = i % (buffer_size * 2)
            packet = f"{sequence_number}|{messages[i]}"
            send_packet(packet, sequence_number)

    # Verificar se ocorreu timeout
    if time.time() - start_time > timeout:
        print("Timeout: retransmitindo pacotes a partir da sequência", last_ack_received + 1)
        start_time = time.time()

        i = last_ack_received + 1
        sequence_number = i % (buffer_size * 2)
        packet = f"{sequence_number}|{messages[i]}"
        send_packet(packet, sequence_number)

# Fechamento do socket
client_socket.close()
