Antes de hacer ningun cambio leed este readme y todo el codigo. Si no hacemos las cosas coherentes
mejor no hacerlas.

Podes dejar al final en el propio readme comentarios o cosas para hacer.
Asi mismo para garantizar el orden, cuando vayais a hacer cambios en el codigo que querais subir
en algun momento, cread un issue lo mas especifico posible, asignarloslo en la tabla kanban del proyecto
en la columna correspondiente, cread una rama para el cambio que vais a hacer, realizadlo haciendo 
commits lo mas pequeños posibles, y cuando este mergead la rama con la de develop.
La idea es mantener develop donde se van haciendo los cambios y añadiendo funcionalidades ( a traves de merges
con otras ramas de trabajo, evitad hacer commits importantes directamente ) y unicamente cada cierto tiempo,
cuando consideremos una version del codigo completamente probada pues se pasa a main. 

·Estructura y patrones:
    -SRC-
- game.py -> (patron director) Su unica tarea es gestionar las escenas. Implementa el gameloop pero las accinones
se delegan a la escena. Emplea un stack para permitir cambiar y volver entre escenas
- scene.py -> (patron director) Son instancias aisladas, podrian considerarse juegos en si mismas. Contendran una lista
 de objetos que la componen y la logica global de la escenea y gestionaran las acciones del loopgame, llamando a las
 funciones correspondientes de los objetos que las componen.
- abstract.py -> Guarda las clases abstractas que implementan el resto de clases. ( Espero no tener que explicaros cuando,
como y porque hay que usar o crear abstractos)
- components.py -> (patron componente) Guarda clases que se instancian para crear elementos que componen otros elementos y no tienen
uso por si solos.
-objects.py ->(idk q patron) Guarda los objetos que componen la escena y tienen interaciones y sentido por si solos.
-player.py -> Guarda la logica del personaje del jugador, no deja de ser un objeto de una escena, pero como por su naturaleza contendrá
mas codigo que el resto se lleva su propio archivo.
-utils.py -> Funciones miscelaneas que queramos reutlizar y aislar para mayor claridad como podria ser dibjar texto, hacer opearciones
matematicas etc.
-settings.py -> Para guardar constantes empleadas en la configuracion del juego como resolucion, colores etc. (SERIA BUENA PRACTICA PORTARLO A UN INI)

    -ASSETS-
  archivos de arte video sonido etc.


Comentarios: 
x
TODO:
x
