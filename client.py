import socket
import time

# Configurações do servidor
server_ip = '127.0.0.1'
server_port = 8081

# Criação do socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Dados sintéticos para envio (10MB)
data_size = 10 * 1024 * 1024  # 10MB
data = "0" * data_size

# Configurações do buffer de pacotes
buffer_size = 10  # Tamanho do buffer em pacotes
packet_size = 1024  # Tamanho máximo de cada pacote em bytes

# Variáveis de controle de timeout e retransmissão
timeout = 2.0  # Tempo em segundos para timeout
last_ack_received = -1  # Último ACK recebido
packets_sent = []  # Lista para armazenar os pacotes enviados

# Função para enviar pacotes
def send_packet(packet, sequence_number):
    client_socket.sendto(packet.encode(), (server_ip, server_port))
    #print("Enviado pacote com sequência", sequence_number)

# Função para retransmitir pacotes
def resend_packets(start_sequence_number):
    for i in range(start_sequence_number, len(data), packet_size):
        message = data[i:i+packet_size]
        sequence_number = i // packet_size  # Números de sequência incrementados
        packet = f"{sequence_number}|{message}"
        send_packet(packet, sequence_number)

# Enviar pacotes
for i in range(0, len(data), packet_size):
    message = data[i:i+packet_size]
    sequence_number = i // packet_size  # Números de sequência incrementados
    packet = f"{sequence_number}|{message}"
    send_packet(packet, sequence_number)
    packets_sent.append((packet, sequence_number))

# Definir o timeout inicial
start_time = time.time()
timeout_expired = False
start_sequence_number = 0

# Aguardar ACKs e tratar timeouts e retransmissões
while packets_sent:
    try:
        client_socket.settimeout(timeout)

        # Receber ACK do servidor
        ack_packet, _ = client_socket.recvfrom(packet_size)
        ack_number = int(ack_packet.decode())
        print("Recebido ACK:", ack_number)

        # Verificar se o ACK é válido
        if ack_number >= start_sequence_number:
            start_sequence_number = ack_number + 1
            timeout_expired = False

            # Remover pacotes confirmados da lista de pacotes enviados
            packets_sent = [(packet, sequence_number) for packet, sequence_number in packets_sent if sequence_number >= start_sequence_number]

    except socket.timeout:
        if not timeout_expired:
            print("Timeout: retransmitindo pacotes de sequência", start_sequence_number)
            timeout_expired = True

            resend_packets(start_sequence_number)

    # Verificar se ocorreu timeout
    if time.time() - start_time > timeout:
        print("Timeout: retransmitindo pacotes de sequência", start_sequence_number)
        start_time = time.time()

        resend_packets(start_sequence_number)

# Fechamento do socket
client_socket.close()
