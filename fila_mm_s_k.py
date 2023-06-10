import math
import random
import simpy

# Função para gerar chegadas exponenciais
def generate_interarrival():
    return random.expovariate(arrival_rate)

# Função para gerar tempos de serviço exponenciais
def generate_service_time():
    return random.expovariate(service_rate)

# Função para o processo de chegada
def arrival(env, server, queue):
    global arrivals, lost_customers
    while True:
        yield env.timeout(generate_interarrival())
        arrivals += 1
        if len(queue) >= capacity:
            # Fila cheia, cliente é descartado
            lost_customers += 1
            continue
        queue.append(env.now)
        if server.count == 0:
            # Servidor ocioso, iniciar o serviço
            env.process(service(env, server, queue))

# Função para o processo de serviço
def service(env, server, queue):
    global departures, total_waiting_time, total_system_time
    while True:
        if len(queue) == 0:
            # Não há clientes na fila, encerrar o serviço
            break
        with server.request() as req:
            yield req
            departures += 1
            arrival_time = queue.pop(0)
            service_time = generate_service_time()
            total_waiting_time += env.now - arrival_time
            total_system_time += service_time
            yield env.timeout(service_time)

# Parâmetros da simulação
arrival_rate = 10  # taxa de chegada (clientes por unidade de tempo)
service_rate = 5  # taxa de serviço (clientes por unidade de tempo)
num_servers = 3     # número de servidores
capacity = 5        # capacidade da fila

event_duration = 24 # tempo total de simulação. altere aqui o valor

# Variáveis de controle
arrivals = 0
departures = 0
lost_customers = 0
total_waiting_time = 0
total_system_time = 0


# Criação do ambiente de simulação
env = simpy.Environment()

# Criação do servidor
server = simpy.Resource(env, capacity=num_servers)

# Criação da fila
queue = []

# Início dos processos de chegada
env.process(arrival(env, server, queue))

# Execução da simulação
env.run(until=event_duration)  # tempo total de simulação

# Cálculo dos parâmetros
utilization = arrival_rate / (num_servers * service_rate )

summation = 0
for n in range(num_servers):
    term1 = (utilization * num_servers) ** n / math.factorial(n)
    summation += term1

term2 = ((num_servers * utilization) ** num_servers) / math.factorial(num_servers)
term3 = (1 - utilization ** (capacity - num_servers + 1)) / (1 - utilization)
expression = summation + term2 * term3

prob_empty_queue = 1 / expression

avg_queue_length = (((prob_empty_queue * num_servers**num_servers * utilization**( num_servers + 1)) / (math.factorial(num_servers) * (1 - utilization)**2)) * (1 - utilization** (capacity - num_servers) * (1 + (1 - utilization) * (capacity - num_servers))))

avg_waiting_time = ((prob_empty_queue * num_servers**num_servers * utilization**( num_servers)) / (service_rate * ((1 - utilization)** 2)  * (math.factorial(num_servers) - (num_servers** num_servers) * (utilization** capacity) * prob_empty_queue)) * (1 - utilization** (capacity - num_servers) * (1 + (1 - utilization) * (capacity - num_servers))))


# Resultados
print("Para", event_duration, "unidades de tempo")
print("Total de chegadas:", arrivals)
print("Total de saídas:", departures)
print("Clientes perdidos:", lost_customers)
print("Clientes na fila no final da simulação:", len(queue))
print("-------------------Parametros de desempenho-------------------")
print("Utizliçao:", utilization)
print("Probabilidade N:", summation * prob_empty_queue)
print("Probabilidade 0:", prob_empty_queue)
print("Número médio de clientes na fila:", avg_queue_length)
print("Temp médio de espera na fila:", avg_waiting_time)