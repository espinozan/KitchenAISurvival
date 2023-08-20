import openai
import click
import questionary
import os
import logging
from cachetools import LRUCache, cached
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

# Configuración de la API de OpenAI
openai.api_key = 'tu_clave_de_api_aqui'

# Configuración de logging
logging.basicConfig(filename='receta_asistente.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KitchenAISurvival:
    def __init__(self, api_key):
        self.api_key = api_key
        self.motor = "text-davinci-003"
        self.cache = LRUCache(maxsize=10)  # Caché de respuestas

    @cached(cache)
    def buscar_receta(self, ingredientes):
        consulta = f"Busca recetas con los siguientes ingredientes: {', '.join(ingredientes)}."
        
        openai.api_key = self.api_key  # Configuración dinámica de la API Key
        respuesta_api = openai.Completion.create(
            engine=self.motor,
            prompt=consulta,
            max_tokens=200
        )
        
        return respuesta_api.choices[0].text.strip()

    def mostrar_receta(self, receta):
        console = Console()
        console.print("\n[bold green]Receta sugerida:[/bold green]")
        console.print("[yellow]-------------------------------[/yellow]")
        console.print(receta)
        console.print("[yellow]-------------------------------[/yellow]")

    def guardar_receta(self, nombre_archivo, receta):
        with open(nombre_archivo, 'w') as archivo:
            archivo.write(receta)

    def cargar_receta(self, nombre_archivo):
        with open(nombre_archivo, 'r') as archivo:
            receta = archivo.read()
        return receta

    def listar_recetas(self):
        recetas = [nombre for nombre in os.listdir() if nombre.endswith(".txt")]
        return recetas

    def ejecutar(self, ingredientes):
        try:
            receta_generada = self.buscar_receta(ingredientes)
            self.mostrar_receta(receta_generada)
            
            guardar = Prompt.ask("¿Quieres guardar esta receta en un archivo?", choices=["Sí", "No"])
            if guardar == "Sí":
                nombre_archivo = Prompt.ask("Ingresa el nombre del archivo para guardar la receta:")
                self.guardar_receta(nombre_archivo, receta_generada)
                print(f"Receta guardada en '{nombre_archivo}'")
                
            opciones_ver_recetas = ["Ver recetas guardadas", "Ordenar recetas por fecha", "Ordenar recetas por nombre", "Cancelar"]
            ver_recetas = Prompt.ask("¿Qué deseas hacer?", choices=opciones_ver_recetas)
            if ver_recetas == "Ver recetas guardadas":
                recetas_guardadas = self.listar_recetas()
                if recetas_guardadas:
                    table = Table(show_header=True, header_style="bold magenta")
                    table.add_column("Recetas Guardadas")
                    for receta in recetas_guardadas:
                        table.add_row(receta)
                    console.print(table)
                    receta_elegida = Prompt.ask("Selecciona una receta para ver:")
                    if receta_elegida in recetas_guardadas:
                        receta_cargada = self.cargar_receta(receta_elegida)
                        console.print("[bold cyan]Receta cargada:[/bold cyan]")
                        console.print("[yellow]-------------------------------[/yellow]")
                        console.print(receta_cargada)
                        console.print("[yellow]-------------------------------[/yellow]")
                    else:
                        console.print("Receta no encontrada.")
                else:
                    console.print("Aún no has guardado recetas.")
            elif ver_recetas == "Ordenar recetas por fecha":
                # Implementa la ordenación por fecha
                pass
            elif ver_recetas == "Ordenar recetas por nombre":
                # Implementa la ordenación por nombre
                pass
                    
        except openai.error.OpenAIError as e:
            logging.error("Error de OpenAI: %s", str(e))
            print("Hubo un error al comunicarse con la API de OpenAI. Por favor, intenta nuevamente más tarde.")
        except Exception as e:
            logging.error("Error inesperado: %s", str(e))
            print("¡Oops! Algo salió mal. Por favor, verifica tus ingredientes e intenta nuevamente.")

@click.command()
@click.option('--api-key', prompt='Ingresa tu API Key de OpenAI', help='Tu clave de API de OpenAI')
def main(api_key):
    kitchen_ai_survival = KitchenAISurvival(api_key)
    console = Console()
    banner = r"""
 _   ___ _       _                 ___  _____                     _            _ 
| | / (_) |     | |               / _ \|_   _|                   (_)          | |
| |/ / _| |_ ___| |__   ___ _ __ / /_\ \ | | ___ _   _ _ ____   _____   ____ _| |
|    \| | __/ __| '_ \ / _ \ '_ \|  _  | | |/ __| | | | '__\ \ / / \ \ / / _` | |
| |\  \ | || (__| | | |  __/ | | | | | |_| |\__ \ |_| | |   \ V /| |\ V / (_| | |
\_| \_/_|\__\___|_| |_|\___|_| |_\_| |_/\___/___/\__,_|_|    \_/ |_| \_/ \__,_|_|
                                                                                 
                                                                                  . :
"""
    console.print(banner)
    console.print("[bold cyan]Bienvenido a KitchenAISurvival:[/bold cyan] Tu Asistente de Recetas y Supervivencia en la Cocina")
    
    while True:
        ingredientes = Prompt.ask("Ingresa los ingredientes disponibles en tu despensa (separados por comas):")
        kitchen_ai_survival.ejecutar(ingredientes.split(','))

        continuar = Prompt.ask("¿Quieres buscar otra receta?", choices=["Sí", "No"])
        if continuar == "No":
            console.print("¡Hasta luego!")
            break

if __name__ == "__main__":
    main()
