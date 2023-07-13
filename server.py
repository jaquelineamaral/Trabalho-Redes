import socket
import random
import time

# Configurações do servidor
server_ip = '127.0.0.1'
server_port = 8081

# Criação do socket UDP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip, server_port))

# Configurações do buffer de pacotes
buffer_size = 10  # Tamanho do buffer em pacotes
packet_size = 1024  # Tamanho máximo de cada pacote em bytes

# Número de sequência inicial
next_sequence_number = 0

# Tamanho da janela do destinatário
receiver_window_size = 10

# Simulação de perdas de pacotes (20% de chance de descartar um pacote)
def simulate_packet_loss():
    return random.random() < 0.2

# Estrutura de dados para armazenar os pacotes recebidos
class MessageBuffer:
    def __init__(self):
        self.buffer = []

    def add_packet(self, packet, client_address):
        sequence_number, message = packet.split('|')
        if int(sequence_number) >= next_sequence_number and int(sequence_number) < next_sequence_number + receiver_window_size:
            if not simulate_packet_loss():
                # Pacote recebido dentro da janela deslizante
                self.buffer.append((sequence_number, message, client_address))
                print("Recebido pacote com sequência", sequence_number)
                self.deliver_ordered_messages()
            else:
                print("Pacote com sequência", sequence_number, "descartado (simulação de perda)")

    def deliver_ordered_messages(self):
        global next_sequence_number
        while str(next_sequence_number) in [packet[0] for packet in self.buffer]:
            packets_to_deliver = [
                packet for packet in self.buffer if packet[0] == str(next_sequence_number)
            ]
            for packet in packets_to_deliver:
                sequence_number, message, client_address = packet
                #print("Entregue mensagem:", message)
                server_socket.sendto(sequence_number.encode(), client_address)
                self.buffer.remove(packet)
            next_sequence_number += 1

# Instância da estrutura de dados para armazenar os pacotes recebidos
message_buffer = MessageBuffer()

while True:
    # Recebe o pacote do cliente
    packet, client_address = server_socket.recvfrom(packet_size)
    message_buffer.add_packet(packet.decode(), client_address)

# Fechamento do socket
server_socket.close()
