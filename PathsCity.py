import json  # Importa el módulo json para trabajar con datos JSON.
import networkx as nx  # Importa el módulo networkx para crear, manipular y estudiar la estructura, dinámica y funciones de redes complejas.
import matplotlib.pyplot as plt  # Importa el módulo matplotlib.pyplot para crear visualizaciones estáticas, animadas e interactivas en Python.
from itertools import islice  # Importa la función islice del módulo itertools para hacer un iterador que devuelve elementos seleccionados del iterable.
import matplotlib.image as mpimg  # Importa el módulo matplotlib.image para proporcionar funcionalidad de lectura de imágenes.

# Define una función para dibujar la ruta en el grafo.
def dibujar_ruta(grafo_ruta, posiciones, rutas_cortas=None, img_path=None):
    # Crear la figura y los ejes
    fig, ax = plt.subplots()
    ax.axis('off')  # Ocultar los ejes

    # Mostrar la imagen
    if img_path:
        img = mpimg.imread(img_path)
        ax.imshow(img)

    # Dibujar las aristas (edges) del grafo
    nx.draw_networkx_edges(grafo_ruta, posiciones, ax=ax, edge_color='gray')

    # Dibujar los nodos del grafo
    nx.draw_networkx_nodes(grafo_ruta, posiciones, ax=ax, node_size=500, node_color='skyblue', alpha=0.8)

    # Dibujar las etiquetas de los nodos
    nx.draw_networkx_labels(grafo_ruta, posiciones, ax=ax, font_size=10, font_color='black')

    # Dibujar las rutas más cortas si se proporcionan
    if rutas_cortas:
        colores = ['red', 'blue', 'green', 'purple', 'orange']  # Define una lista de colores para las rutas
        for i, ruta_corta in enumerate(rutas_cortas):
            edges_in_path = [(ruta_corta[j], ruta_corta[j + 1]) for j in range(len(ruta_corta) - 1)]
            nx.draw_networkx_edges(grafo_ruta, posiciones, edgelist=edges_in_path, ax=ax, edge_color=colores[i % len(colores)], width=2)

    plt.show()


# Define una función para guardar los datos del grafo en formato GeoJSON.
def guardar_datos_en_geojson(grafo_geojson, nombre_archivo):
    datos = {
        'type': 'FeatureCollection',
        'features': []
    }
    for u, v, data in grafo_geojson.edges(data=True):
        caracteristica = {
            'type': 'Feature',
            'geometry': {
                'type': 'LineString',
                'coordinates': [u, v]
            },
            'properties': data
        }
        datos['features'].append(caracteristica)
    for nodo in grafo_geojson.nodes():
        caracteristica = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': nodo
            },
            'properties': {}
        }
        datos['features'].append(caracteristica)
    with open(nombre_archivo, 'w') as archivo:
        json.dump(datos, archivo, indent=4)  # Escribe los datos en el archivo en formato JSON.

# Define una función para encontrar la ruta más rápida entre dos nodos.
def camino_mas_rapido(grafo_ruta, inicio, fin):
    try:
        camino = nx.dijkstra_path(grafo_ruta, inicio, fin, weight='tiempo')  # Usa el algoritmo de Dijkstra para encontrar la ruta más corta.
        tiempo = sum(grafo_ruta[u][v]['tiempo'] for u, v in zip(camino[:-1], camino[1:]))  # Calcula el tiempo total de la ruta.
        return camino, tiempo
    except nx.NetworkXNoPath:
        return "No existe un camino entre {} y {}.".format(inicio, fin)  # Devuelve un mensaje de error si no hay ruta.
    except nx.NodeNotFound:
        return "Uno o ambos lugares no existen en la ciudad"  # Devuelve un mensaje de error si uno o ambos nodos no existen.

# Define una función para crear un grafo a partir de calles y lugares de la ciudad.
def crear_grafo(calles_ciudad, lugares_ciudad):
    grafo_nuevo = nx.Graph()  # Crea un nuevo grafo.
    for lugar in lugares_ciudad:
        grafo_nuevo.add_node(lugar)  # Añade cada lugar como un nodo.
    for calle_mapa in calles_ciudad:
        if calle_mapa[0] in lugares_ciudad and calle_mapa[1] in lugares_ciudad:
            grafo_nuevo.add_edge(calle_mapa[0], calle_mapa[1], tiempo=calle_mapa[2])  # Añade cada calle como un borde.
    return grafo_nuevo

# Define una función para encontrar todas las rutas más cortas entre dos nodos.
def todos_los_caminos_mas_cortos(grafo_ruta, inicio, fin):
    if inicio not in grafo_ruta or fin not in grafo_ruta:
        return "Uno o ambos lugares no existen en la ciudad"  # Devuelve un mensaje de error si uno o ambos nodos no existen.
    try:
        caminos = list(islice(nx.all_shortest_paths(grafo_ruta, inicio, fin, weight='tiempo'), 1000))  # Encuentra todas las rutas más cortas.
        tiempos = [sum(grafo_ruta[u][v].get('tiempo', 0) for u, v in zip(camino[:-1], camino[1:])) for camino in caminos]  # Calcula el tiempo total de cada ruta.
        return caminos, tiempos
    except nx.NetworkXNoPath:
        return "No existe un camino entre {} y {}.".format(inicio, fin)  # Devuelve un mensaje de error si no hay ruta.

# Define una función para guardar los datos del grafo en formato JSON.
def guardar_datos_en_json(grafo_json, nombre_archivo):
    datos = {
        'nodos': list(grafo_json.nodes()),
        'aristas': [{'u': u, 'v': v, 'tiempo': data.get('tiempo', 0)} for u, v, data in grafo_json.edges(data=True)]
    }
    with open(nombre_archivo, 'w') as archivo:
        json.dump(datos, archivo)  # Escribe los datos en el archivo en formato JSON.

# Define una función para cargar los datos del grafo desde un archivo JSON.
def cargar_datos_desde_json(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            datos = json.load(archivo)  # Carga los datos del archivo.
    except json.JSONDecodeError as e:
        print(f"Error al decodificar el archivo JSON: {e}")  # Imprime un mensaje de error si el archivo no se puede decodificar.
        return None
    grafo_cargar_datos = nx.Graph()  # Crea un nuevo grafo.
    grafo_cargar_datos.add_nodes_from(datos['nodos'])  # Añade los nodos al grafo.
    grafo_cargar_datos.add_edges_from((data['u'], data['v'], {'tiempo': data['tiempo']}) for data in datos['aristas'])  # Añade los bordes al grafo.
    return grafo_cargar_datos

# Define una función para encontrar una ruta entre dos nodos.
def encontrar_camino(grafo_camino, inicio, destino):
    visitados = set()  # Crea un conjunto para almacenar los nodos visitados.
    cola = [[inicio]]  # Crea una cola para almacenar las rutas.

    while cola:  # Mientras haya rutas en la cola...
        camino = cola.pop(0)  # Obtiene la primera ruta de la cola.
        nodo_actual = camino[-1]  # Obtiene el último nodo de la ruta.

        if nodo_actual == destino:  # Si el último nodo es el destino...
            return camino  # Devuelve la ruta.

        if nodo_actual not in visitados:  # Si el nodo no ha sido visitado...
            visitados.add(nodo_actual)  # Marca el nodo como visitado.
            for vecino in grafo_camino.neighbors(nodo_actual):  # Para cada vecino del nodo...
                nuevo_camino = list(camino)  # Hace una copia de la ruta.
                nuevo_camino.append(vecino)  # Añade el vecino a la ruta.
                cola.append(nuevo_camino)  # Añade la nueva ruta a la cola.

    return None  # Si no hay ruta, devuelve None.

# Define una función para mostrar un menú para mapeo.
def menu_de_mapping(grafo_menu_mapping, pos):
    while True:  # Mientras el usuario no elija salir...
        print("\nMapping\n"
              + "\n\t1. Buscar la ruta más rápida"
              + "\n\t2. Mostrar calles"
              + "\n\t3. Mostrar ubicaciones"
              + "\n\t4. Mostrar grafo"
              + "\n\t5. Salir")
        opc = int(input("\nElige una opción:"))
        if opc == 1:
            origen = input("Introduce la intersección de inicio: ")
            destino = input("Introduce la intersección de fin: ")

            # Calcular todas las rutas más cortas
            rutas_cortas = list(nx.all_shortest_paths(grafo_menu_mapping, source=origen, target=destino, weight='tiempo'))

            # Dibujar el grafo mostrando todas las rutas más cortas en diferentes colores
            dibujar_ruta(grafo_menu_mapping, nodos, rutas_cortas=rutas_cortas)

        elif opc == 2:
            # Imprimir todas las aristas con sus pesos
            for nodo1, nodo2, data in grafo_menu_mapping.edges(data=True):
                print(f"La calle entre {nodo1} y {nodo2} tiene un peso de {data['tiempo']}")
        elif opc == 3:
            # Imprimir todos los nodos
            for nodo in grafo_menu_mapping.nodes():
                print(f"Intersección: {nodo}")
        elif opc == 4:
            # Draw the graph without any route
            dibujar_ruta(grafo_menu_mapping, pos)
        else:
            print("Elige una opción del menú")


# # Identificación de nodos (coordenadas aproximadas en la imagen)
# nodos = {
#     'Cinema': (3.5, 1.5),
#     'Gas Station': (5.5, 1.6),
#     'School': (6, 3),
#     'Church': (3, 3.5),
#     'Theatre': (1, 4),
#     'Library': (5.5, 4),
#     'Coffee': (7.1, 5),
#     'Police': (8, 6.5),
#     'Food Market': (3.5, 6.5),
#     'Hospital': (3.5, 8.8),
#     'Bank': (0.5, 7.7),
#     'Hotel': (1, 8.7),
#     'Fire Station': (5.7, 8.7),
#     '1': (1.1, 1.1),
#     '0.5': (2.4, 2.3),
#     '2': (4.8, 2.3),
#     '2.5': (6.1, 2.3),
#     '2.7': (7.2, 1),
#     '3': (8.2, 2),
#     '4': (7.6, 3.3),
#     '4.2': (6.3, 4),
#     '4.5': (8.3, 5.3),
#     '5': (9.2, 7),
#     '5.5': (8, 7.8),
#     '6': (7.5, 8.9),
#     '7': (6.9, 7),
#     '7.5': (6.4, 5.7),
#     '8': (4.8, 5.5),
#     '8.5': (4.8, 7.8),
#     '9': (2.4, 7.7),
#     '9.7': (1, 5.7),
#     '9.5': (2.4, 5.5),
#     '10': (2.4, 4),
#
# }
#
# # Definición de calles (conexiones entre nodos y tiempo de viaje)
# calles = [
#     ("0.5", "1", 1),
#     ("2", "0.5", 1),
#     ("2.5", "2", 1),
#     ("8", "2", 1),
#     ("2.7", "2.5", 1),
#     ("3", "2.7", 1),
#     ("4", "3", 1),
#     ("4.5", "4", 1),
#     ("4.2", "4", 1),
#     ("7.5", "4.2", 1),
#     ("5", "4.5", 1),
#     ("5.5", "5", 1),
#     ("6", "5.5", 1),
#     ("7", "5.5", 1),
#     ("8.5", "7", 1),
#     ("7.5", "7", 1),
#     ("8", "7.5", 1),
#     ("9.5", "8", 1),
#     ("9", "8.5", 1),
#     ("8", "8.5", 1),
#     ("9.5", "9", 1),
#     ("9.7", "9", 1),
#     ("10", "9.7", 1),
#     ("9.5", "10", 1),
#     ("0.5", "10", 1),
#     ("0.5", "Cinema", 1),
#     ("2", "Cinema", 1),
#     ("2", "Gas Station", 1),
#     ("2.5", "Gas Station", 1),
#     ("2.5", "School", 1),
#     ("4.2", "Coffee", 1),
#     ("4.5", "Coffee", 1),
#     ("4.2", "Library", 1),
#     ("5", "Police", 1),
#     ("7", "Police", 1),
#     ("5.5", "Police", 1),
#     ("8.5", "Fire Station", 1),
#     ("7", "Fire Station", 1),
#     ("9", "Hospital", 1),
#     ("8.5", "Hospital", 1),
#     ("9", "Hotel", 1),
#     ("Bank", "Hotel", 1),
#     ("9", "Bank", 1),
#     ("9.5", "Food Market", 1),
#     ("8", "Food Market", 1),
#     ("10", "Church", 1),
#     ("0.5", "Church", 1),
#     ("10", "Theatre", 1),
#     ("9.7", "Theatre", 1),
#     ('1', '0.5', 1),
#     ('0.5', '2', 1),
#     ('2', '2.5', 1),
#     ('2', '8', 1),
#     ('2.5', '2.7', 1),
#     ('2.7', '3', 1),
#     ('3', '4', 1),
#     ('4', '4.5', 1),
#     ('4', '4.2', 1),
#     ('4.2', '7.5', 1),
#     ('4.5', '5', 1),
#     ('5', '5.5', 1),
#     ('5.5', '6', 1),
#     ('5.5', '7', 1),
#     ('7', '8.5', 1),
#     ('7', '7.5', 1),
#     ('7.5', '8', 1),
#     ('8', '9.5', 1),
#     ('8.5', '9', 1),
#     ('8.5', '8', 1),
#     ('9', '9.5', 1),
#     ('9', '9.7', 1),
#     ('9.7', '10', 1),
#     ('10', '9.5', 1),
#     ('10', '0.5', 1),
#     ('Cinema', '0.5', 1),
#     ('Cinema', '2', 1),
#     ('Gas Station', '2', 1),
#     ('Gas Station', '2.5', 1),
#     ('School', '2.5', 1),
#     ('Coffee', '4.2', 1),
#     ('Coffee', '4.5', 1),
#     ('Library', '4.2', 1),
#     ('Police', '5', 1),
#     ('Police', '7', 1),
#     ('Police', '5.5', 1),
#     ('Fire Station', '8.5', 1),
#     ('Fire Station', '7', 1),
#     ('Hospital', '9', 1),
#     ('Hospital', '8.5', 1),
#     ('Hotel', '9', 1),
#     ('Hotel', 'Bank', 1),
#     ('Bank', '9', 1),
#     ('Food Market', '9.5', 1),
#     ('Food Market', '8', 1),
#     ('Church', '10', 1),
#     ('Church', '0.5', 1),
#     ('Theatre', '10', 1),
#     ('Theatre', '9.7', 1),
#
# ]

with open('data.json', 'r') as f:
    datos = json.load(f)
nodos = datos['nodos']
calles = datos['calles']

# Crear el grafo
grafo = nx.Graph()
for calle in calles:
    grafo.add_edge(calle[0], calle[1], tiempo=calle[2])

# Dibujar el grafo sin rutas
dibujar_ruta(grafo, nodos)

# Llamar al menú
menu_de_mapping(grafo, nodos)