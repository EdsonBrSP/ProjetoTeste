import itertools
import random
import csv
from collections import Counter

# -------------------------
# Parâmetros ajustáveis
# -------------------------
UNIVERSE_SIZE = 25          # total de números disponíveis
SUBSET_SIZE = 15            # tamanho do conjunto sorteado
TICKET_SIZE = 16            # tamanho do bilhete a apostar
TARGET_COVERAGE = 0.95      # fração do universo de 15-subsets a cobrir
TICKET_COST = 56             # custo de cada bilhete de 16 números
IGNORE_PERCENT = 0.01       # fração de 15-subsets a ignorar
HISTORICAL_NUMBERS_FILE = "historico.csv"  # arquivo com números sorteados históricos (uma linha por sorteio)

OUTPUT_FILE = "bilhetes16_otimizados.csv"

# -------------------------
# Carregar histórico e calcular frequências
# -------------------------
def load_historical_numbers():
    try:
        with open(HISTORICAL_NUMBERS_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            numbers = [int(n) for row in reader for n in row]
        counter = Counter(numbers)
        freq_numbers = [num for num,_ in counter.most_common()]
        return freq_numbers
    except FileNotFoundError:
        print(f"Aviso: arquivo {HISTORICAL_NUMBERS_FILE} não encontrado, usando ordem aleatória")
        return list(range(1, UNIVERSE_SIZE + 1))

# -------------------------
# Geração do universo de 15-subsets
# -------------------------
def generate_universe():
    all_subsets = list(itertools.combinations(range(1, UNIVERSE_SIZE + 1), SUBSET_SIZE))
    total = len(all_subsets)
    ignore_count = int(total * IGNORE_PERCENT)
    if ignore_count > 0:
        ignored = set(random.sample(range(total), ignore_count))
        universe = [s for i,s in enumerate(all_subsets) if i not in ignored]
    else:
        universe = all_subsets
    return set(universe)

# -------------------------
# Cobertura otimizada baseada em frequência
# -------------------------
def optimized_cover(universe, freq_numbers):
    remaining = set(universe)
    tickets = []
    iteration = 0
    while len(remaining)/len(universe) > (1-TARGET_COVERAGE):
        iteration += 1
        # construir candidato priorizando números mais frequentes
        candidate = set()
        for n in freq_numbers:
            if len(candidate) < TICKET_SIZE:
                candidate.add(n)
            else:
                break
        # se faltar completar, adiciona números aleatórios
        while len(candidate) < TICKET_SIZE:
            candidate.add(random.randint(1, UNIVERSE_SIZE))
        # calcula quantos 15-subsets do universo ele cobre
        covered = set(s for s in remaining if set(s).issubset(candidate))
        if covered:
            tickets.append(candidate)
            remaining -= covered
        if iteration % 1000 == 0:
            print(f"Iteração {iteration}, ainda faltam {len(remaining)} subsets")
    return tickets

# -------------------------
# Salvar bilhetes em CSV
# -------------------------
def save_tickets(tickets):
    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        for t in tickets:
            writer.writerow(sorted(t))

# -------------------------
# Função principal
# -------------------------
def main():
    print("Carregando histórico de números...")
    freq_numbers = load_historical_numbers()
    print(f"Números mais frequentes: {freq_numbers[:10]} ...")

    print("Gerando universo de 15-subsets...")
    universe = generate_universe()
    print(f"Tamanho do universo após ignorar {IGNORE_PERCENT*100:.2f}%: {len(universe)} subsets")

    print("Iniciando cobertura otimizada com bilhetes de 16 números...")
    tickets = optimized_cover(universe, freq_numbers)

    print(f"Número de bilhetes gerados: {len(tickets)}")
    total_cost = len(tickets) * TICKET_COST
    print(f"Custo estimado total: R${total_cost:.2f}")

    print(f"Salvando bilhetes em {OUTPUT_FILE} ...")
    save_tickets(tickets)
    print("Concluído!")

if __name__ == "__main__":
    main()
