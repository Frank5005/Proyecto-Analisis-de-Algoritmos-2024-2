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
    "rojo": "naranja",
    "verde": "turquesa",
    "azul": "fucsia",
    "amarillo": "violeta",
    "naranja": "rojo",  # Reversa para volver al claro
    "turquesa": "verde",
    "fucsia": "azul",
    "violeta": "amarillo",
    "+1": "+5",
    "salta uno": "salta todos",
    "reversa": "reversa",
    "flip": "flip",
    "+2": "toma un color",
    "+5": "+1",
    "salta todos": "salta uno",
    "toma un color": "+2"
}

#lightSpecialCards = ["+1", "reversa", "salta uno", "flip", "+2"]
#darkSpecialCards = ["+5", "reversa", "salta todos", "flip", "toma un color"]

# Función para manejar el efecto de las cartas especiales
def apply_special_effect(card, player_hands, current_player_index, players, allLightCards, allDarkCards, current_side, discard_pile):
    next_player_index = (current_player_index + 1) % len(players)
    #global discard_pile

    if "+2" in card and current_side == "claro":
        print(f"{players[next_player_index]} debe robar 2 cartas y pierde su turno.")
        for _ in range(2):
            player_hands[players[next_player_index]].append(allLightCards.pop())
        return (next_player_index + 1) % len(players)  # Saltar turno
    elif "+5" in card and current_side == "oscuro":
        print(f"{players[next_player_index]} debe robar 5 cartas y pierde su turno.")
        for _ in range(5):
            player_hands[players[next_player_index]].append(allDarkCards.pop())
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
        # Cambiar el lado claro/oscuro
        current_side = "oscuro" if current_side == "claro" else "claro"
        print(f"¡El mazo ha cambiado al lado {current_side}!")

        # Cambiar el color de la carta en la pila de descartes al correspondiente lado oscuro o claro
        top_card_color, top_card_value = discard_pile[-1].split()
        new_color = color_map[top_card_color]
        discard_pile[-1] = f"{new_color} {top_card_value}"  # Actualizamos la carta en la pila de descartes

        print(f"Carta en la pila de descartes: {discard_pile[-1]}")
        return next_player_index  # El turno sigue con el siguiente jugador
    elif "cambio de color" in card:
        new_color = input("Elige el nuevo color (azul, verde, rojo, amarillo): ")
        while new_color not in ["azul", "verde", "rojo", "amarillo"]:
            new_color = input("Color inválido. Elige nuevamente: ")
        print(f"El nuevo color es {new_color}.")
        return next_player_index
    return next_player_index  # Si no es una carta especial, pasa al siguiente jugador

# Función para calcular los puntos de una mano
def points_calculator(hand):
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
    print("\nPuntuación final:")
    puntuactions = {}
    for player, hand in player_hands.items():
        points = points_calculator(hand)
        puntuactions[player] = points
        print(f"{player} tiene {len(hand)} cartas restantes con un total de {points} puntos.")
    return puntuactions

# Función para verificar si una carta es numérica
def is_numeric_card(card):
    """Devuelve True si la carta es numérica (de 0 a 9), de lo contrario, False."""
    card_type = card.split()[1]  # Obtenemos el tipo de la carta (número o especial)
    return card_type.isdigit()  # Verifica si es un número (0-9)

# Funcion implementar la lógica de juego para un jugador sintético.
def ai_play_turn(player_name, hand, top_card, current_side, players, current_player_index):
    """
    
    Args:
        player_name: Nombre del jugador sintético
        hand: Lista de cartas en la mano del jugador
        top_card: Carta superior en la pila de descartes
        current_side: Lado actual del juego ('claro' u 'oscuro')
        players: Lista de todos los jugadores
        current_player_index: Índice del jugador actual
        
    Returns:
        chosen_card: La carta elegida para jugar o None si no hay jugadas posibles
    """
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

# Funcion para elegir un color cuando se juega una carta de cambio de color.
def ai_choose_color():
    colors = ["azul", "verde", "rojo", "amarillo"]
    chosen_color = random.choice(colors)
    print(f"IA elige el color: {chosen_color}")
    return chosen_color


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
4 cambia color - 4 cambia color
4 come 2 - 4 toma un color
"""
# Colores y tipos de cartas
colors = ["azul", "verde", "rojo", "amarillo"]

# Cartas numéricas (del 0 al 9 para ambos lados)
numbers = [str(i) for i in range(10)]

# Cartas especiales para ambos lados
lightSpecialCards = ["+1", "reversa", "salta uno", "flip", "+2"]
darkSpecialCards = ["+5", "reversa", "salta todos", "flip", "toma un color"]

# Carta especial de cambio de lado (existe en ambos lados)
changeSide = ["cambio de sentido"]

# Mazo del lado claro
#lightCards = {color: numbers + lightSpecialCards + changeSide for color in colors}

# Mazo del lado oscuro
#darkCards = {color: numbers + darkSpecialCards + changeSide for color in colors}

# Mazo del lado claro
lightCards = {color: [f"{color} {num}" for num in numbers] + [f"{color} {card}" for card in lightSpecialCards] + changeSide for color in colors}

# Mazo del lado oscuro
darkCards = {color: [f"{color} {num}" for num in numbers] + [f"{color} {card}" for card in darkSpecialCards] + changeSide for color in colors}


"""
# Mostrar ejemplo del mazo claro
print("Mazo Claro:")
for color, cartas in lightCards.items():
    print(f"{color.capitalize()}: {cartas}")

# Mostrar ejemplo del mazo oscuro
print("\nMazo Oscuro:")
for color, cards in darkCards.items():
    print(f"{color.capitalize()}: {cards}")
"""

#Mezcla
# Combinar todos los colores en una lista
allLightCards = sum(lightCards.values(), [])
allDarkCards = sum(darkCards.values(), [])

# Barajar ambos lados
random.shuffle(allLightCards)
random.shuffle(allDarkCards)

"""
print("\nMazo Claro Barajado:", allLightCards)
print("Mazo Oscuro Barajado:", allDarkCards)
"""

#Orden del juego
# Asignar una carta a cada jugador
orderCard = {player: allLightCards.pop() for player in all_players}
# Mostrar las cartas asignadas
print("Cartas asignadas:")
for player, card in orderCard.items():
    print(f"{player}: {card}")

# Determinar quién tiene la carta con el mayor valor
initPlayer = max(orderCard, key=lambda player: card_value(orderCard[player]))

print(f"\n{initPlayer} comenzará el juego dada la carta {orderCard[initPlayer]}")

# Ordenar los jugadores según el valor de sus cartas de mayor a menor
gameOrder = sorted(all_players, key=lambda player: card_value(orderCard[player]), reverse=True)

# Mostrar el orden de los jugadores
print("\nOrden de los jugadores (de mayor valor a menor):")
for i, player in enumerate(gameOrder, 1):
    print(f"{i}. {player} con la carta {orderCard[player]}")

#Distribuir 7 cartas a cada jugador, además de poner la carta inicial
player_hands = {player: [allLightCards.pop() for _ in range(7)] for player in all_players}

# Mostrar las cartas de cada jugador
print("\nManos de los jugadores:")
for player, hand in player_hands.items():
    print(f"{player}: {hand}")

# Carta inicial en la pila de descartes
discard_pile = []

# Sacar cartas hasta obtener una carta numérica
while True:
    initial_card = allLightCards.pop()  # Sacar una carta del lado claro
    if is_numeric_card(initial_card):
        discard_pile.append(initial_card)
        break  # Salir del bucle cuando se obtenga una carta numérica

print(f"\nCarta inicial en la pila de descartes: {discard_pile[-1]}")

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
            new_card = allLightCards.pop() if current_side == "claro" else allDarkCards.pop()
            player_hands[current_player].append(new_card)
            print(f"{current_player} recibe: {new_card}")
            turn_index = (turn_index + 1) % players
            continue
            
        # Procesar la carta elegida por la IA
        discard_pile.append(chosen_card)
        player_hands[current_player].remove(chosen_card)
        
        # Si es una carta de cambio de color
        if "cambio de color" in chosen_card:
            new_color = ai_choose_color()
            # Procesar el cambio de color...
            
        # Aplicar efectos de la carta especial
        turn_index = apply_special_effect(chosen_card, player_hands, turn_index, gameOrder, 
                                        allLightCards, allDarkCards, current_side, discard_pile)
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
            turn_index = apply_special_effect(chosen_card, player_hands, turn_index, gameOrder, allLightCards, allDarkCards, current_side, discard_pile)

            # Verificar si el jugador ha ganado
            if len(player_hands[current_player]) == 0:
                print(f"\n{current_player} ha ganado el juego!")
                game_over = True
        else:
            print(f"{current_player} no tiene cartas jugables. Toma una carta del mazo.")
            new_card = allLightCards.pop() if current_side == "claro" else allDarkCards.pop()
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
