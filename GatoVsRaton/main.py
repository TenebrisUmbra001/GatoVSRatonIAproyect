import numpy as np
import random
import time
import os
import pickle
import multiprocessing
from datetime import datetime

# Importar las clases necesarias
from environment.maze import Maze
from environment.game import Game
from environment.sensors import OdorSystem
from agents.mouse_agent import MouseAgent
from agents.cat_agent import CatAgent
from rl.q_learning import QLearningAgent


class TrainingManager:
    def __init__(self):
        self.models = {
            'Guallabito': {'difficulty': 1, 'filename': 'Guallabito_model.npy', 'plays': 0, 'successes': 0},
            'Remmil': {'difficulty': 2, 'filename': 'Remmil_model.npy', 'plays': 0, 'successes': 0},
            'Mickey': {'difficulty': 3, 'filename': 'Mickey_model.npy', 'plays': 0, 'successes': 0}
        }
        self.load_model_stats()
        print(f"Estadísticas cargadas inicialmente: {self.models}")

    def load_model_stats(self):
        """Carga estadísticas de modelos existentes"""
        if os.path.exists('model_stats.pkl'):
            try:
                with open('model_stats.pkl', 'rb') as f:
                    loaded_models = pickle.load(f)
                    # Actualizar solo los modelos que existen en el archivo
                    for name in self.models.keys():
                        if name in loaded_models:
                            self.models[name]['plays'] = loaded_models[name]['plays']
                            self.models[name]['successes'] = loaded_models[name]['successes']
                print(f"Estadísticas cargadas desde model_stats.pkl: {self.models}")
            except Exception as e:
                print(f"Error al cargar estadísticas: {e}")
        else:
            print("model_stats.pkl no encontrado, iniciando con estadísticas en 0")

    def save_model_stats(self, name, plays, successes):
        """Guarda estadísticas del modelo"""
        try:
            # Actualizar las estadísticas en memoria
            self.models[name]['plays'] = plays
            self.models[name]['successes'] = successes

            # Guardar todas las estadísticas en el archivo
            with open('model_stats.pkl', 'wb') as f:
                pickle.dump(self.models, f)
            print(f"Estadísticas guardadas para {name}: plays={plays}, successes={successes}")
        except Exception as e:
            print(f"Error al guardar estadísticas para {name}: {e}")

    def get_difficulty_settings(self, difficulty):
        """Obtiene los parámetros según la dificultad"""
        settings = {
            1: {'width': 10, 'height': 10, 'initial_energy': 20, 'food_energy': 15, 'food_count': 12},
            2: {'width': 20, 'height': 20, 'initial_energy': 15, 'food_energy': 10, 'food_count': 20},
            3: {'width': 45, 'height': 45, 'initial_energy': 12, 'food_energy': 8, 'food_count': 35}
        }
        return settings[difficulty]

    def train_model(self, name):
        """Entrena un modelo específico (para multiprocessing)"""
        model = self.models[name]
        difficulty = model['difficulty']
        settings = self.get_difficulty_settings(difficulty)

        # Configuración del juego - 100,000 EPISODIOS por modelo
        max_episodes = 10
        max_steps_per_episode = 1000

        # Inicializar componentes
        odor_system = OdorSystem()
        game = Game(settings['food_energy'])

        # Inicializar agentes
        mouse_agent = MouseAgent(settings['width'], settings['height'], settings['initial_energy'])
        cat_agent = CatAgent()

        # Intentar cargar modelo existente
        if os.path.exists(model['filename']):
            try:
                print(f"Cargando modelo existente para {name}...")
                mouse_agent.load_model(model['filename'])
                print(f"Modelo {name} cargado exitosamente!")
            except Exception as e:
                print(f"Error al cargar modelo {name}: {e}")
                print(f"Iniciando entrenamiento desde cero para {name}...")
        else:
            print(f"Iniciando entrenamiento desde cero para {name}...")

        print(f"\n=== INICIANDO ENTRENAMIENTO DE {name.upper()} ===")
        print(f"Dificultad: {'Fácil' if difficulty == 1 else 'Medio' if difficulty == 2 else 'Difícil'}")
        print(f"Tamaño del laberinto: {settings['width']} x {settings['height']}")
        print(f"Energía inicial: {settings['initial_energy']}, Comida: +{settings['food_energy']}")
        print(f"Comida total: {settings['food_count']}")
        print(f"Episodios totales: {max_episodes}")
        print(f"Modelo: {model['filename']}")
        print("=" * 70)

        # Variables para monitorear el progreso
        best_reward = -float('inf')
        successful_escapes = 0
        total_episodes = 0

        # Tiempo de inicio
        start_time = time.time()
        last_save_time = start_time
        last_stats_save = start_time

        # Bucle de entrenamiento
        for episode in range(max_episodes):
            total_episodes = episode + 1

            # Generar un NUEVO laberinto en cada episodio
            maze = Maze(settings['width'], settings['height'], settings['food_count'])

            # Reiniciar estado del juego
            mouse_pos = maze.get_random_empty_position()
            cat_pos = maze.entrance_position
            mouse_energy = settings['initial_energy']
            game_over = False
            total_reward = 0
            steps_without_progress = 0
            last_position = mouse_pos

            # Mostrar progreso cada 10 episodios
            if episode % 10 == 0:
                elapsed_time = time.time() - start_time
                success_rate = (successful_escapes / total_episodes * 100) if total_episodes > 0 else 0
                print(
                    f"\n=== {name.upper()} - EPISODIO {episode + 1}/{max_episodes} - Tiempo: {elapsed_time / 60:.1f} min ===")
                print(
                    f"Mejor recompensa: {best_reward:.2f}, Éxitos: {successful_escapes}/{total_episodes} ({success_rate:.1f}%)")

            for step in range(max_steps_per_episode):
                # 1. Obtener señal de luz en la posición del ratón
                light_intensity = maze.get_light_at(mouse_pos)

                # 2. Discretizar estado del ratón
                current_state = mouse_agent.discretize_state(
                    mouse_pos, mouse_energy, odor_system.get_odor_at(mouse_pos), light_intensity
                )

                # 3. Elegir acción
                action = mouse_agent.choose_action(current_state)

                # 4. Ejecutar acción
                next_pos, action_result = maze.execute_action(mouse_pos, action)

                # 5. Actualizar energía y sistema de olores
                mouse_energy -= 1
                if action_result['found_food']:
                    mouse_energy = min(100, mouse_energy + settings['food_energy'])
                    odor_system.add_odor(next_pos, intensity=1.0)
                elif action_result['found_exit']:
                    mouse_energy = 100

                # 6. Actualizar memoria del gato
                if odor_system.get_odor_at(cat_pos) > 0:
                    cat_agent.update_odor_memory(mouse_pos, odor_system.get_odor_at(cat_pos))

                # 7. Mover gato
                cat_pos = cat_agent.move_towards_target(cat_pos, mouse_pos, maze)

                # 8. Calcular recompensa
                reward = game.calculate_reward(
                    {'energy': mouse_energy},
                    action_result
                )
                total_reward += reward

                # 9. Obtener señal de luz en la nueva posición
                next_light_intensity = maze.get_light_at(next_pos)

                # 10. Discretizar siguiente estado
                next_state = mouse_agent.discretize_state(
                    next_pos, mouse_energy, odor_system.get_odor_at(next_pos), next_light_intensity
                )

                # 11. Aprender de la experiencia
                mouse_agent.learn(current_state, action, reward, next_state)

                # 12. Actualizar estado
                mouse_pos = next_pos

                # Verificar condiciones de fin de juego
                if mouse_energy <= 0:
                    game_over = True

                if action_result['escaped']:
                    game_over = True
                    successful_escapes += 1
                    print(f"  → ÉXITO en episodio {episode + 1} (paso {step + 1})")

                if action_result['captured']:
                    game_over = True
                    print(f"  → CAPTURADO en episodio {episode + 1}")

                if mouse_pos == last_position:
                    steps_without_progress += 1
                    if steps_without_progress > 30:
                        game_over = True
                else:
                    steps_without_progress = 0
                    last_position = mouse_pos

                if game_over:
                    break

            # Actualizar exploración
            mouse_agent.update_exploration()

            # Monitorear progreso
            if total_reward > best_reward:
                best_reward = total_reward

            # Guardar modelo y estadísticas periódicamente
            current_time = time.time()
            if (current_time - last_save_time > 1800) or (episode % 100 == 0 and episode > 0):
                try:
                    mouse_agent.save_model(model['filename'])
                    self.save_model_stats(name, total_episodes, successful_escapes)
                    last_save_time = current_time
                    last_stats_save = current_time
                    print(f"  → Modelo y estadísticas guardados para {name}")
                except Exception as e:
                    print(f"  → Error al guardar {name}: {e}")

        # Guardar modelo final y estadísticas
        try:
            mouse_agent.save_model(model['filename'])
            self.save_model_stats(name, total_episodes, successful_escapes)
            print(f"  → Guardado final para {name}")
        except Exception as e:
            print(f"  → Error en guardado final de {name}: {e}")

        # Resumen final
        elapsed_time = time.time() - start_time
        print(f"\n=== ENTRENAMIENTO COMPLETADO PARA {name.upper()} ===")
        print(f"Tiempo total: {elapsed_time / 60:.1f} minutos")
        print(f"Episodios completados: {total_episodes}")
        print(f"Éxitos totales: {successful_escapes}")
        print(f"Porcentaje de éxito: {(successful_escapes / total_episodes * 100):.1f}%")

        return mouse_agent


def train_all_models_parallel(manager):
    """Entrena todos los modelos en paralelo"""
    processes = []
    results = {}

    # Crear un proceso para cada modelo
    for name in manager.models.keys():
        p = multiprocessing.Process(target=manager.train_model, args=(name,))
        processes.append(p)
        p.start()

    # Esperar a que todos los procesos terminen
    for p in processes:
        p.join()

    print("\n=== TODOS LOS MODELOS HAN TERMINADO DE ENTRENAR ===")


def main_menu():
    manager = TrainingManager()

    while True:
        print("\n=== MENÚ PRINCIPAL - GATO VS RATÓN IA ===")
        print("1. Entrenar todos los modelos (Guallabito, Remmil, Mickey) en paralelo")
        print("2. Entrenar un modelo específico")
        print("3. Ver estadísticas de modelos")
        print("4. Salir")

        choice = input("Elige una opción: ")

        if choice == '1':
            print("\n=== INICIANDO ENTRENAMIENTO PARALELO DE TODOS LOS MODELOS ===")
            train_all_models_parallel(manager)

        elif choice == '2':
            print("\n=== SELECCIONA MODELO PARA ENTRENAR ===")
            print("1. Guallabito (Fácil)")
            print("2. Remmil (Medio)")
            print("3. Mickey (Difícil)")
            model_choice = input("Elige: ")

            if model_choice == '1':
                manager.train_model('Guallabito')
            elif model_choice == '2':
                manager.train_model('Remmil')
            elif model_choice == '3':
                manager.train_model('Mickey')
            else:
                print("Opción no válida")

        elif choice == '3':
            print("\n=== ESTADÍSTICAS DE MODELOS ===")
            for name, model in manager.models.items():
                plays = model['plays']
                successes = model['successes']
                success_rate = (successes / plays * 100 if plays > 0 else 0)
                print(f"{name}:")
                print(
                    f"  Dificultad: {'Fácil' if model['difficulty'] == 1 else 'Medio' if model['difficulty'] == 2 else 'Difícil'}")
                print(f"  Partidas jugadas: {plays}")
                print(f"  Éxitos: {successes}")
                print(f"  Porcentaje de éxito: {success_rate:.1f}%")
                print(f"  Archivo: {model['filename']}")
                print()

        elif choice == '4':
            print("Saliendo del programa...")
            break

        else:
            print("Opción no válida. Inténtalo de nuevo.")


if __name__ == "__main__":
    main_menu()