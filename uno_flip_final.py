# pylint: disable=C0103
# pylint: disable=C0301
# pylint: disable=W0105
# pylint: disable=W0621
# pylint: disable=C0116
# pylint: disable=W0602
# pylint: disable=C0303
# pylint: disable=W0108

"""
Proyecto de Análisis de Algoritmos
El objetivo del presente proyecto es diseñar y construir un algoritmo que juegue una partida de UNO-FLIP. Además, debe
construir una interfaz sencilla que permita un juego de entre 2 y 10 jugadores (humanos o sintéticos).
"""
import random

# Determinar quién inicia (el jugador con el número más alto inicia)
# Extraemos el número de la carta si es una carta numérica, y asignamos un valor bajo a las cartas especiales.
def card_value(card):
    """Determinando quien empieza jugando"""
    for num in range(10):
        if str(num) in card:
            return num
    return 0  # Asignamos 0 para cartas especiales (que no son números)

# Función para verificar si una carta es jugable
def is_playable(card, top_card, current_side):
    """Verificar si la carta es jugable"""
    try:
        # Dividir la carta solo si tiene dos componentes (color y tipo)
        card_parts = card.split()
        top_parts = top_card.split()

        # Si la carta no tiene dos partes, podría ser una carta especial
        if len(card_parts) < 2 or len(top_parts) < 2:
            # Si es una carta especial como "cambio de sentido" o "flip", la jugada es válida
            return "cambio" in card or "flip" in card or "cambio" in top_card or "flip" in top_card

        card_color, card_type = card_parts[0], card_parts[1]
        top_color, top_type = top_parts[0], top_parts[1]

        # Verificar si se está en el lado claro y se juega un +2 o +1
        if current_side == "claro":
            if card_type == "+2" or card_type == "+1":
                # Puede jugar +2 o +1 si el color coincide o si la carta superior es +2 o +1
                return card_color == top_color or top_type in ["+2", "+1"]

        # Verificar si se está en el lado oscuro y se juega un +5
        if current_side == "oscuro":
            if card_type == "+5":
                # Puede jugar +5 si el color coincide o si la carta superior es +5
                return card_color == top_color or top_type == "+5"

        # Comprobar si la carta es jugable (por color o tipo)
        return card_color == top_color or card_type == top_type  or "cambio" in card or "flip" in card
    except IndexError:
        return False  # Si la carta no tiene el formato esperado, no es jugable

# Mapeo entre colores claros y oscuros
color_map = {
    # Colores
    "rojo": "naranja",
    "verde": "turquesa",
    "azul": "fucsia",
    "amarillo": "violeta",
    # Colores al revés
    "naranja": "rojo",
    "turquesa": "verde",
    "fucsia": "azul",
    "violeta": "amarillo",
    # Cartas especiales
    "+1": "+5",
    "salta uno": "salta todos",
    "+2": "+color",
    # Cartas especiales al revés
    "+5": "+1",
    "salta todos": "salta uno",
    "+color": "+2",
    # Cartas especiales que no varían
    "reversa": "reversa",
    "flip": "flip",
    "multicolor": "multicolor",
}

# Hace toda la rotación de las cartas
def flip(current_side, discard_pile, player_hands, color_map):
    """Cambia el lado del mazo y rota las cartas al nuevo lado activo."""
    # Cambiar el lado del mazo
    new_side = "oscuro" if current_side == "claro" else "claro"
    print(f"¡El mazo ha cambiado al lado {new_side}!")

    # Rotar las cartas en la pila de descartes
    flipped_discard_pile = []
    for card in discard_pile:
        parts = card.split(maxsplit=1)  # Separar en color y valor
        if len(parts) == 2:
            color, value = parts
            flipped_color = color_map.get(color, color)  # Cambiar el color según el mapa
            flipped_discard_pile.append(f"{flipped_color} {value}")
        else:
            flipped_discard_pile.append(card)  # Manejo de cartas con formato inesperado

    discard_pile[:] = flipped_discard_pile  # Actualizar la pila de descartes

    # Rotar las cartas en las manos de los jugadores
    for player, hand in player_hands.items():
        flipped_hand = []
        for card in hand:
            parts = card.split(maxsplit=1)
            if len(parts) == 2:
                color, value = parts
                flipped_color = color_map.get(color, color)
                flipped_hand.append(f"{flipped_color} {value}")
            else:
                flipped_hand.append(card)
        player_hands[player] = flipped_hand  # Actualizar la mano del jugador

    # Reabastecer el mazo correspondiente si es necesario
    if new_side == "claro":
        if len(lightCards) < 20:  # Si quedan menos de 20 cartas en el mazo claro
            print("Reabasteciendo el mazo claro...")
            refill_deck(lightCards, discard_pile, new_side, color_map)
    else:
        if len(darkCards) < 20:  # Si quedan menos de 20 cartas en el mazo oscuro
            print("Reabasteciendo el mazo oscuro...")
            refill_deck(darkCards, discard_pile, new_side, color_map)

    print("¡Las cartas han sido rotadas correctamente!")
    return new_side

# Función para determinar si es un jugador sintético
def is_synthetic_player(player):
    """Determina si es o no sintético"""
    return player.startswith("Jugador")  # Asumiendo que los jugadores sintéticos tienen un prefijo "Jugador"


# Función para manejar el efecto de las cartas especiales
def apply_special_effect(card, player_hands, current_player_index, players, lightCards, darkCards, current_side, discard_pile):
    """Aplica el efecto de una carta especial"""
    next_player_index = (current_player_index + 1) % len(players)
    
    if  "+1" in card and current_side == "claro":
        print(f"{players[next_player_index]} debe robar 1 carta y pierde su turno.")
        player_hands[players[next_player_index]].append(draw_card(current_side, lightCards, darkCards, discard_pile, color_map))
        return (next_player_index + 1) % len(players)  # Saltar turno
    
    elif "+2" in card and current_side == "claro":
        print(f"{players[next_player_index]} debe robar 2 cartas y pierde su turno.")
        for _ in range(2):
            player_hands[players[next_player_index]].append(draw_card(current_side, lightCards, darkCards, discard_pile, color_map))
        return (next_player_index + 1) % len(players)  # Saltar turno
    
    elif "+5" in card and current_side == "oscuro":
        print(f"{players[next_player_index]} debe robar 5 cartas y pierde su turno.")
        for _ in range(5):
            player_hands[players[next_player_index]].append(draw_card(current_side, lightCards, darkCards, discard_pile, color_map))
        return (next_player_index + 1) % len(players)  # Saltar turno
    
    elif "salta uno" in card and current_side == "claro":
        print(f"{players[next_player_index]} pierde su turno.")
        return (next_player_index + 1) % len(players)  # Saltar turno
    
    elif "salta todos" in card and current_side == "oscuro":
        print(f"Todos pierden su turno, {players[current_player_index]} sigue jugando.")
        return current_player_index  # Salta todos los jugadores y vuelve al mismo jugador
    
    elif "reversa" in card:
        if len(players) > 2:
            print("El orden de los turnos ha sido invertido.")
            players.reverse()
        else:
            print("Reversa no tiene efecto en un juego de 2 jugadores.")
        return current_player_index
    
    elif "flip" in card:
        # Usar el método flip para cambiar el lado del juego
        current_side = flip(current_side, discard_pile, player_hands, color_map)

        # Verificar si el mazo actual necesita ser reabastecido
        deck = lightCards if current_side == "claro" else darkCards
        if len(deck) < 20:  # Reabastecer si quedan menos de 20 cartas
            refill_deck(deck, discard_pile, current_side, color_map)

        return next_player_index  # El turno sigue con el siguiente jugador
    
    elif "multicolor" in card:
        if current_side == "claro":
            if is_synthetic_player(players[current_player_index]):  # Verifica si el jugador es sintético
                # Contar la cantidad de cartas de cada color en la mano del jugador sintético
                color_counts = {}
                for hand_card in player_hands[players[current_player_index]]:
                    card_color = hand_card.split(maxsplit=1)[0]  # Extraer el color de la carta
                    if card_color in color_map:  # Solo considerar colores válidos
                        card_color_mapped = color_map[card_color] if current_side == "oscuro" else card_color
                        color_counts[card_color_mapped] = color_counts.get(card_color_mapped, 0) + 1

                # Determinar el color con la mayor cantidad de cartas
                new_color = max(color_counts, key=color_counts.get, default="azul")  # Azul por defecto si hay empate
                print(f"El jugador sintético elige el color {new_color}.")
            else:
                # Para jugadores humanos, solicitar el nuevo color
                new_color = input("Elige el nuevo color (azul, verde, rojo, amarillo): ")
                while new_color not in ["azul", "verde", "rojo", "amarillo"]:
                    new_color = input("Color inválido. Elige nuevamente: ")
                print(f"El nuevo color es {new_color}.")
        else:
            if is_synthetic_player(players[current_player_index]):  # Verifica si el jugador es sintético
                # Contar la cantidad de cartas de cada color en la mano del jugador sintético
                color_counts = {}
                for hand_card in player_hands[players[current_player_index]]:
                    card_color = hand_card.split(maxsplit=1)[0]  # Extraer el color de la carta
                    if card_color in color_map:  # Solo considerar colores válidos
                        card_color_mapped = color_map[card_color] if current_side == "oscuro" else card_color
                        color_counts[card_color_mapped] = color_counts.get(card_color_mapped, 0) + 1

                # Determinar el color con la mayor cantidad de cartas
                new_color = max(color_counts, key=color_counts.get, default="azul")  # Azul por defecto si hay empate
                print(f"El jugador sintético elige el color {new_color}.")
            else:
                # Para jugadores humanos, solicitar el nuevo color
                new_color = input("Elige el nuevo color (fucsia, turquesa, naranja, violeta): ")
                while new_color not in ["fucsia", "turquesa", "naranja", "violeta"]:
                    new_color = input("Color inválido. Elige nuevamente: ")
                print(f"El nuevo color es {new_color}.")
        return next_player_index

    elif "+color" in card and current_side == "oscuro":
        print(f"{players[current_player_index]} juega 'Toma un color'.")

        chosen_color = input("Elige un nuevo color oscuro (naranja, turquesa, fucsia, violeta): ").strip().lower()
        while chosen_color not in ["naranja", "turquesa", "fucsia", "violeta"]:
            chosen_color = input("Color inválido. Elige nuevamente: ").strip().lower()
        print(f"El nuevo color oscuro elegido es {chosen_color}.")

        print(f"{players[next_player_index]} debe robar cartas hasta encontrar una del color {chosen_color}.")
        draw_limit = len(darkCards) + len(discard_pile)  # Evitar loops infinitos
        draw_count = 0

        while draw_count < draw_limit:
            if not darkCards:
                refill_deck(darkCards, discard_pile, "oscuro", color_map)
            drawn_card = draw_card("oscuro", lightCards, darkCards, discard_pile, color_map)
            player_hands[players[next_player_index]].append(drawn_card)
            print(f"{players[next_player_index]} recibe: {drawn_card}")
            draw_count += 1
            if chosen_color in drawn_card:
                break

        if draw_count == draw_limit:
            print("El mazo no contiene más cartas del color elegido. Termina el turno.")
        print(f"{players[next_player_index]} pierde su turno.")
        return (next_player_index + 1) % len(players)

    return next_player_index  # Si no es una carta especial, pasa al siguiente jugador

# Función para calcular los puntos de una mano
def points_calculator(hand):
    """Calcula los puntos de cada jugador"""
    points = 0
    for card in hand:
        if any(num in card for num in "0123456789"):
            points += int(card.split()[1])  # Las cartas numéricas tienen su valor numérico
        elif "+1" in card:
            points += 10
        elif "+5" in card or "reversa" in card or "salta uno" in card or "flip" in card:
            points += 20
        elif "salta todos" in card:
            points += 30
        elif "cambio de color" in card:
            points += 40
        elif "+2" in card:
            points += 50
        elif "toma un color" in card:
            points += 60
    return points

# Función para mostrar la puntuación final
def final_punctuation(player_hands):
    """Calcula y muestra la puntuación final de cada jugador"""
    print("\nPuntuación final:")
    puntuactions = {}
    for player, hand in player_hands.items():
        points = points_calculator(hand)
        puntuactions[player] = points
        print(f"{player} tiene {len(hand)} cartas restantes con un total de {points} puntos.")
    return puntuactions

# Función para verificar si una carta es numérica
def is_numeric_card(card):
    """Verifica si una carta es numérica"""
    card_parts = card.split()  # Divide la carta en color y tipo
    if len(card_parts) < 2:  # Verifica que haya al menos dos elementos
        print(f"Formato de carta inválido: {card}")
        return False  # Considera la carta no válida como no numérica
    card_type = card_parts[1]  # Obtén el tipo de carta
    return card_type.isdigit()  # Verifica si es un número (0-9)

# Lógica de juego para un jugador sintético
def ai_play_turn(player_name, hand, top_card, current_side, players, current_player_index):
    """Lógica de juego para el jugador sintético"""
    # Encontrar todas las cartas jugables
    playable_cards = [card for card in hand if is_playable(card, top_card, current_side)]
    
    if not playable_cards:
        print(f"{player_name} no tiene cartas jugables. Debe robar una carta.")
        return None
        
    # Analizar la situación del juego
    next_player = players[(current_player_index + 1) % len(players)]
    next_player_cards = len(player_hands[next_player])
    
    # Estrategias de juego basadas en la situación
    
    # 1. Si el siguiente jugador tiene pocas cartas (1-2), priorizar cartas de ataque
    if next_player_cards <= 2:
        attack_cards = [card for card in playable_cards 
                if any(attack in card for attack in (["+2", "+5", "salta uno", "salta todos"] 
                                                     if current_side == "claro" else ["+5", "salta todos"]))]

        if attack_cards:
            chosen_card = max(attack_cards, key=lambda c: card_value(c))
            print(f"{player_name} juega carta de ataque: {chosen_card}")
            return chosen_card
    
    # 2. Si tenemos pocas cartas, priorizar cartas numéricas para mantener especiales
    if len(hand) <= 3:
        numeric_cards = [card for card in playable_cards if any(str(num) in card for num in range(10))]
        if numeric_cards:
            chosen_card = numeric_cards[0]
            print(f"{player_name} juega carta numérica: {chosen_card}")
            return chosen_card
    
    # 3. Si hay muchas cartas de un color, usar ese color
    color_counts = {}
    for card in hand:
        if ' ' in card:  # Asegurarse de que la carta tiene color
            color = card.split()[0]
            color_counts[color] = color_counts.get(color, 0) + 1
    
    if color_counts:
        most_common_color = max(color_counts, key=color_counts.get)
        same_color_cards = [card for card in playable_cards if card.startswith(most_common_color)]
        if same_color_cards:
            chosen_card = same_color_cards[0]
            print(f"{player_name} juega carta del color más común: {chosen_card}")
            return chosen_card
    
    # 4. Priorizar cartas especiales si tenemos muchas cartas
    if len(hand) > 5:
        special_cards = [card for card in playable_cards if not any(str(num) in card for num in range(10))]
        if special_cards:
            chosen_card = special_cards[0]
            print(f"{player_name} juega carta especial: {chosen_card}")
            return chosen_card
    
    # 5. Si ninguna estrategia específica aplica, jugar la primera carta válida
    chosen_card = playable_cards[0]
    print(f"{player_name} juega: {chosen_card}")
    return chosen_card

# Función para verificar que las cartas que se tengan sean de un único lado
def clean_deck(deck, current_side):
    """
    Limpia el mazo para asegurarse de que solo contiene cartas del lado actual (claro u oscuro).
    """
    valid_colors = set(color_map.keys() if current_side == "claro" else color_map.values())
    cleaned_deck = [card for card in deck if card.split(maxsplit=1)[0] in valid_colors]
    
    if len(cleaned_deck) != len(deck):
        print(f"Se han eliminado cartas no válidas del mazo {current_side}.")
    
    deck[:] = cleaned_deck


# Función para tomar una carta del mazo. Si el mazo está vacío, lo reabastece desde la pila de descartes
def draw_card(current_side, lightCards, darkCards, discard_pile, color_map):
    """Roba una carta del mazo y valida el lado actual."""
    # Seleccionar el mazo correspondiente al lado actual
    if current_side == "claro":
        deck = lightCards
        print("Mazo seleccionado: Claro")
    else:
        deck = darkCards
        print("Mazo seleccionado: Oscuro")

    # Si el mazo tiene menos de 20 cartas o está vacío, se reabastece
    if not deck or len(deck) < 20:
        print(f"El mazo {current_side} está vacío o tiene menos de 20 cartas. Reabasteciendo con la pila de descartes...")
        refill_deck(deck, discard_pile, current_side, color_map)
    
    # Verificar que el mazo actual esté compuesto solo por cartas del lado correcto
    clean_deck(deck, current_side)
    
    # Si el mazo sigue vacío después de reabastecerse, el juego no puede continuar
    if not deck:
        raise ValueError(f"El mazo {current_side} sigue vacío incluso después del reabastecimiento. ¡El juego no puede continuar!")
    
    # Tomar la carta del mazo correspondiente
    return deck.pop()

# Reabastecer el mazo desde la pila de descartes.
def refill_deck(deck, discard_pile, current_side, color_map):
    """Reabastece el mazo desde la pila de descartes."""
    if len(discard_pile) > 1:
        top_card = discard_pile.pop()  # Mantén la carta superior
        for card in discard_pile:
            parts = card.split(maxsplit=1)  # Manejar nombres de cartas
            if len(parts) == 2:
                color, value = parts
                flipped_color = color_map.get(color, color) if current_side == "oscuro" else color
                deck.append(f"{flipped_color} {value}")
            else:
                print(f"Advertencia: Carta con formato inesperado '{card}', omitiendo.")
        discard_pile.clear()
        discard_pile.append(top_card)  # Devuelve la carta superior a la pila de descartes
        random.shuffle(deck)
    else:
        print("No hay suficientes cartas en la pila de descartes para reabastecer.")

# Función para generar cartas de un lado (claro u oscuro)
def generate_cards(colors, numbers, special_cards, wild_cards):
    """Generador de las cartas de juego"""
    cards = []
    # Agregar cartas numéricas
    for color in colors:
        cards.extend([f"{color} {num}" for num in numbers] * 2)  # Cada número tiene dos cartas por color

    # Agregar cartas especiales
    for color in colors:
        for special in special_cards:
            cards.extend([f"{color} {special}"] * 2)  # Cada especial tiene dos cartas por color

    # Agregar cartas Flip
    for color in colors:
        cards.extend([f"{color} flip"] * 2)  # Cada color tiene dos cartas Flip

    # Agregar cartas de comodín
    cards.extend(wild_cards)

    return cards


# Aquí empieza el juego
print("Bienvenido al UNO FLIP!!!")
players = int(input("Ingresa la cantidad de jugadores de esta partida: "))
while players < 2 or players > 10 :
    print("Lo siento, pero el juego solo admite hasta 10 jugadores.")
    players = int(input("Ingresa una cantidad de jugadores correcta (entre 2 y 10 jugadores): "))

#Selección de cantidad de jugadores humanos y sintéticos
condition = False
while not condition:
    humanPlayers = int(input("Ingresa la cantidad de jugadores humanos: "))
    if humanPlayers == players:
        aiPlayers = 0
    else:
        aiPlayers = int(input("Ingresa la cantidad de jugadores sintéticos: "))
    total = humanPlayers + aiPlayers
    if total == players:
        condition = True
    else:
        print("La suma de jugadores humanos y sintéticos no coincide con la cantidad de jugadores de la partida.")

#Asignación de nombres de los jugadores
synthetic = [None] * aiPlayers
for aiPlayer in range(aiPlayers):
    synthetic[aiPlayer] = "Jugador " + str(aiPlayer)
humans = [None] * humanPlayers
for humanPlayer in range(humanPlayers):
    humans[humanPlayer] = input("Ingrese el nombre del jugador humano " + str(humanPlayer) + ": ")

# Todos los jugadores
all_players = humans + synthetic

#Mezclar el maso, cada jugador saca una carta y de esa manera se elige el orden de juego
#Hay 112 cartas en total, distribuidas:
"""
18 azules - 18 fucsias
18 verdes - 18 turquesas
18 rojas - 18 naranjas
18 amarillas - 18 violetas
8 cartas come una - 8 cartas come 5
8 reversa - 8 reversa
8 salta uno - 8 salta todos
8 flip - 8 flip
4 multicolor - 4 multicolor
4 toma 2 - 4 toma un color
"""
# Cartas de tipo claro
lightColors = ["azul", "verde", "rojo", "amarillo"]
lightNumbers = [str(i) for i in range(10)]
lightSpecialCards = ["+1", "reversa", "salta uno"]
lightWildCards = ["multicolor"]*4 + ["+2"]*4
lightFlipCards = ["flip"]

# Cartas de tipo oscuro
darkColors = ["fucsia", "turquesa", "naranja", "violeta"]
darkNumbers = [str(i) for i in range(10)]
darkSpecialCards = ["+5", "reversa", "salta todos"]
darkWildCards = ["multicolor"]*4 + ["+color"]*4
darkFlipCards = ["flip"]

# Generación de los mazos
lightCards = generate_cards(lightColors, lightNumbers, lightSpecialCards, lightWildCards)
darkCards = generate_cards(darkColors, darkNumbers, darkSpecialCards, darkWildCards)

# Barajar los mazos
random.shuffle(lightCards)
random.shuffle(darkCards)

# Mezclar en el mazo de juego
gameCards = lightCards + darkCards
random.shuffle(gameCards)

#Distribuir 7 cartas a cada jugador
player_hands = {player: [lightCards.pop() for _ in range(7)] for player in all_players}

# Carta inicial en la pila de descartes
discard_pile = []

# Carta inicial en la pila de descartes: debe ser del lado claro
discard_pile = []
# Sacar cartas hasta obtener una carta numérica
while True:
    initial_card = lightCards.pop()  # Sacar una carta del lado claro
    if is_numeric_card(initial_card):
        discard_pile.append(initial_card)
        break  # Salir del bucle cuando se obtenga una carta numérica
print(f"\nCarta inicial en la pila de descartes: {discard_pile[-1]}")

# Verificar que no hay cartas del lado oscuro en las manos iniciales
"""
for player, hand in player_hands.items():
    assert all("flip" not in card for card in hand), f"Error: Carta 'flip' en la mano de {player}"
"""
    
# Orden del juego: Asignar una carta para determinar quién comienza
orderCard = {player: lightCards.pop() for player in all_players}
# Determinar quin tiene la carta con mayor valor
initPlayer = max(orderCard, key=lambda player: card_value(orderCard[player]))
# Ordenar los jugadores según el valor de sus cartas de mayor a menor
gameOrder = sorted(all_players, key=lambda player: card_value(orderCard[player]), reverse=True)

print(f"\n{initPlayer} comenzará el juego dada la carta {orderCard[initPlayer]}")
print("\nOrden del juego:", gameOrder)

# Mostrar las cartas de cada jugador
print("\nManos de los jugadores:")
for player, hand in player_hands.items():
    print(f"{player}: {hand}")

#Ciclo para el juego hasta que alguien gane (se le acaben las cartas o se alcance los puntos objetivo sumando las cartas de los demás)
#Verificar que se manejen los turnos bien
#Verificar que la carta usada para jugar sea viable o usable
#Si no tiene posible carta de juego, toma una sola carta del mazo, según lo que salga juega o no
#Tener en cuenta las cartas especiales de color(cambio de color, comer +2 o +1, ir en sentido contrario de juego, pierde turno o FLIP)
#Tener en cuenta las cartas especiales oscuras (Cambio de color, cambio de color salvaje, comer +5, FLIP, sentido contrario o saltar turno de todos)
#Cambio de color salvaje: el siguiente jugador, de no tener el color, tomará toda carta posible del mazo mientras no le salga del color que el anterior jugador eligió
"""
Cambios de lado del mazo
•+2: El siguiente jugador roba 2 cartas y pierde su turno.
•+5: El siguiente jugador roba 5 cartas y pierde su turno.
•Saltar: El siguiente jugador pierde su turno.
•Saltar a todos: Todos los jugadores pierden un turno y el turno regresa al jugador que jugó la carta.
•Invertir: Invierte el orden de los turnos.
•Cambio de color: El jugador elige el color del siguiente turno.
Cambios de lado del mazo
RF4.1: Cuando se juegue una carta Flip, el sistema debe cambiar el mazo de cartas del lado claro al lado oscuro (o viceversa).
RF4.2: Todas las cartas en manos de los jugadores también deben "vol-tearse", mostrando el nuevo lado activo.
"""

objective = int(input("Ingrese valor de puntos objetivo, si solo quiere que se juegue hasta que se acaben las cartas escriba 0: "))
# Ciclo principal del juego
current_side = "claro"  # Comienza con el lado claro
game_over = False
turn_index = 0

while not game_over:
    current_player = gameOrder[turn_index]
    print(f"\nEs el turno de {current_player}")

    # Mostrar las cartas disponibles
    print(f"Tus cartas: {player_hands[current_player]}")

    # Mostrar la carta en la pila de descartes
    print(f"Carta en la pila de descartes: {discard_pile[-1]}")

    if current_player in synthetic:
        chosen_card = ai_play_turn(
            current_player,
            player_hands[current_player],
            discard_pile[-1],
            current_side,
            gameOrder,
            turn_index
        )
        
        if chosen_card is None:
            # El jugador sintético debe robar una carta
            new_card = draw_card(current_side, lightCards, darkCards, discard_pile, color_map)
            player_hands[current_player].append(new_card)
            print(f"{current_player} recibe: {new_card}")
            turn_index = (turn_index + 1) % players
            continue
            
        # Procesar la carta elegida por la IA
        discard_pile.append(chosen_card)
        player_hands[current_player].remove(chosen_card)
        
        """
        # Si es una carta de cambio de color
        if "cambio de color" in chosen_card:
            new_color = ai_choose_color()
            # Procesar el cambio de color...
        """
            
        # Aplicar efectos de la carta especial
        turn_index = apply_special_effect(chosen_card, player_hands, turn_index, gameOrder, 
                                        lightCards, darkCards, current_side, discard_pile)
    else:
        # Buscar una carta jugable
        playable_cards = [card for card in player_hands[current_player] if is_playable(card, discard_pile[-1], current_side)]

        if playable_cards:
            print(f"\nCartas jugables: {playable_cards}")
            chosen_card = input("Elige una carta para jugar: ")
            while chosen_card not in playable_cards:
                chosen_card = input("Carta inválida. Elige una carta para jugar: ")
            discard_pile.append(chosen_card)
            player_hands[current_player].remove(chosen_card)

            # Aplicar efectos de la carta especial si es necesario
            turn_index = apply_special_effect(chosen_card, player_hands, turn_index, gameOrder, lightCards, darkCards, current_side, discard_pile)

            # Verificar si el jugador ha ganado
            if len(player_hands[current_player]) == 0:
                print(f"\n{current_player} ha ganado el juego!")
                game_over = True
        else:
            print(f"{current_player} no tiene cartas jugables. Toma una carta del mazo.")
            new_card = draw_card(current_side, lightCards, darkCards, discard_pile, color_map)
            player_hands[current_player].append(new_card)
            print(f"{current_player} recibe: {new_card}")

            if not game_over:
                # Cambiar turno
                turn_index = (turn_index + 1) % players

# Finalización del juego y cálculo de puntuaciones
if objective == 0:
    print("El juego ha terminado porque un jugador se ha quedado sin cartas.")
else:
    #Por puntuación
    # Calcular las puntuaciones de las cartas restantes de cada jugador
    puntuactions = final_punctuation(player_hands)

    # Verificar si algún jugador alcanzó el objetivo
    winner = max(puntuactions, key=lambda player: puntuactions[player])
    if puntuactions[winner] >= objective:
        print(f"\n{winner} ha alcanzado el objetivo de {objective} puntos y ha ganado el juego!")
    else:
        print("\nNingún jugador ha alcanzado el objetivo de puntos, por lo que se declara el ganador por las cartas restantes:")
        print(f"{winner} es el ganador con {puntuactions[winner]} puntos.")

"""
RF5.1: El juego termina cuando uno de los jugadores se queda sin cartas.
RF5.2: El sistema debe declarar al ganador y mostrar las cartas restantes de los otros jugadores.
2.6. Pantalla de puntuación
RF6.1: Al finalizar la partida, debe aparecer una pantalla con la clasificación de los jugadores, mostrando el número de cartas restantes.
RF6.2: El sistema debe ofrecer opciones para iniciar una nueva partida o salir del juego.
Recordemos que si es por puntos, los valores son:
Cartas de números (0-9) - valor numérico
+1 - 10 puntos
+5/Reversa/Saltar uno/Flip - 20 puntos cada una
Saltar todos - 30 puntos
Cambio de color - 40 puntos
+2 - 50 puntos
toma un color 60 puntos
"""
#La interfaz debe ser intuitiva, permitiendo a los jugadores humanos indicar cartas, ver sus cartas disponibles, y entender el estado del juego
"""
RNF5.1: La interfaz debe mostrar:
•Cartas disponibles de cada jugador en cada uno de sus turnos.
•Carta actual en la pila de descartes.
•Estado del turno (quién es el siguiente jugador).
•Lado activo del mazo (claro u oscuro)
"""

#Consideración de la idea para que una IA lo haga y decida de la mejor manera
"""
RF7.1: Los jugadores IA deben ser capaces de:
•Jugar cartas que coincidan con el color, número o tipo.
•Priorizar las cartas especiales para afectar a los otros jugadores.
•Usar la lógica para cambiar el color del juego cuando sea ventajoso.
•Robar cartas si no pueden jugar ninguna carta válida
"""
