import socket
import time
import matplotlib.pyplot as plt

# Configurações do servidor
server_ip = '127.0.0.1'
server_port = 8081

# Criação do socket UDP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Dados sintéticos para envio (10MB)
data_size = 10 * 1024 * 1024  # 10MB
data = "A" * data_size

# Configurações do buffer de pacotes
buffer_size = 10  # Tamanho do buffer em pacotes
packet_size = 1024  # Tamanho máximo de cada pacote em bytes

# Variáveis de controle de timeout e retransmissão
timeout = 0.1  # Tempo em segundos para timeout
packets_sent = []  # Lista para armazenar os pacotes enviados
last_ack_received = -1  # Último ACK recebido

# Variáveis de controle de congestionamento
window_size = 1  # Tamanho inicial da janela
congestion_threshold = 10  # Limiar de congestão

# Variáveis para coletar dados de tempo e vazão
time_list = []  # Lista para armazenar o tempo
throughputs = []  # Lista para armazenar as vazões

# Variável para armazenar o tempo de início
start_timet = None

# Calculo do tempo decorrido para evitar divisão por zero
def calculate_elapsed_time():
    global start_timet
    if start_timet is None:
        start_timet = time.time()
    return (time.time() - start_timet)

# Função para calcular a vazão; retorno da função é em bps
def calculate_throughput(sequence_number):
    elapsed_time = calculate_elapsed_time()
    if elapsed_time > 0:
        return (sequence_number + 1) * packet_size * 8 / elapsed_time
    return 0

# Função para enviar pacotes
def send_packet(packet, sequence_number):
    client_socket.sendto(packet.encode(), (server_ip, server_port))
    #print("Enviado pacote com sequência", sequence_number)

# Enviar pacotes
for i in range(0, len(data), packet_size):
    message = data[i:i+packet_size]
    sequence_number = i // packet_size  # Números de sequência incrementados
    packet = f"{sequence_number}|{message}"
    send_packet(packet, sequence_number)
    packets_sent.append((packet, sequence_number))

# Definir o timeout inicial
start_time = time.time()

# Aguardar ACKs e tratar timeouts e retransmissões
while packets_sent:
    try:
        client_socket.settimeout(timeout)

        # Receber ACK do servidor
        ack_packet, _ = client_socket.recvfrom(packet_size)
        ack_number = int(ack_packet.decode())
        print("Recebido ACK:", ack_number)

        # Verificar se o ACK é válido
        if ack_number == last_ack_received + 1:
            last_ack_received = ack_number
            packets_sent = [(packet, sequence_number) for packet, sequence_number in packets_sent if sequence_number > ack_number]
            window_size = min(window_size + 1, congestion_threshold)  # Aumentar a janela em 1 até o limite de congestão

    except socket.timeout:
        #print("Timeout: retransmitindo pacotes...")
        window_size = max(1, window_size // 2)  # Reduzir a janela pela metade

        for packet, sequence_number in packets_sent[:window_size]:
            send_packet(packet, sequence_number)

    # Verificar se ocorreu timeout
    if time.time() - start_time > timeout:
        #print("Timeout: retransmitindo pacotes...")
        window_size = max(1, window_size // 2)  # Reduzir a janela pela metade

        for packet, sequence_number in packets_sent[:window_size]:
            send_packet(packet, sequence_number)

        # Verificar se atingiu o limiar de congestão
        if window_size < congestion_threshold:
            window_size += 1  # Aumentar a janela em 1

    throughput = calculate_throughput(last_ack_received)
    aux_elapsed_time = calculate_elapsed_time()
    time_list.append(aux_elapsed_time)
    throughputs.append(throughput)

print("Vazão: " + str(max(throughputs)))
print("Tempo: " + str(aux_elapsed_time))

# Plotar o gráfico tempo (s) x vazão (bps)
plt.plot(time_list, throughputs)
plt.xlabel('Tempo (s)')
plt.ylabel('Vazão (bps)')
plt.title('Tempo x Vazão')
plt.show()

# Fechamento do socket
client_socket.close()
