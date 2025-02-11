diccionario = {"alerta nombre blender": "Es necesario un nombre para el Blender alternativo!",
               "alerta nombre default": "El nombre para un blender alternativo no puede ser 'Default'."
                                        " Renómbrelo por favor.",
               "alerta ruta": "La ruta de blender ingresada no es válida!", "alerta no encontrados":
                   "Algunos blends no se encontraron en el sistema y fueron omitidos.",
               "TIRAR RENDERS": "   RENDERIZAR   ", "modo_ingesta": "Ingest mode",
               "DETENER": "      DETENER       ",
               "Propiedades Extra 2L":
                   "Propiedades Extra", "Modo": "Modo", "Cambiar Escena":
                   "Escenas", "Cambiar rango frames": "Rango de frames",
               "Versión de Blender": "Blender", "Argumentos Extra":
                   "Argumentos Extra", "Explorar ruta Blend":
                   "Explorar ruta del blend", "Explorar ruta salida": "Explorar ruta de salida",
               "Explorar ruta output": "Explorar ruta de salida",
               "blend backup": "Ese archivo un blend de backup. Lo agrego igual?", "archivo malo":
                   "Quéloqués ese archivo? No lo agrego.",
               "titulo ingrese frames": "Ingrese los frames a renderizar!",
               "mensaje ingrese frames": "Ingrese el/los frame/s a renderizar. Para ingresar más de un frame, "
                                         "separelos por comas.",
               "Detener al completar": "Detener procesamiento tras el BLEND actual",
               "Stop after current frame is saved": "Detener procesamiento tras el FRAME actual",
               "render en proceso": "Hay un render en proceso. ¿Salir de todos modos?", "limpiara log":
                   "Esto eliminará de forma permanente los datos del log guardados hasta ahora.\n¿Proseguir?",
               "Pc will shutdown.": "El ordenador se apagará.",
               "Shutdown PC after queue processing is completed":
                   "Apagar ordenador al completar los renders",
               "Ignore": "Ignorar", "Render_Script": "Script", "Last": "Último",
               "Ver Render": "Ver Render",
               "faltan permisos": "Error intentando guardar la configuración."
                                  "\nB-renderon necesita permiso para escribir archivos de modo de"
                                  " guardar su configuración y log. \nIntente correr"
                                  " B-renderon como superusuario (root/administrador) o correrlo desde"
                                  " una ubicación con permisos de escritura.",
               "resetear_estado_blends": "Resetear estado de blend(s) elegido(s)",
               "renderizar_blend": "Renderizar blend(s) elegido(s)",
               "respetar_blender_blend": "Usar settings de blender y selección del blend",
               "usar_preset_nombrado": "Preset",
               "elegir_viewlayers": "Elegir viewlayer(s) para añadir a la cola",
               "Queue processing": "Procesamiento de cola", "Main": "Principales",
               "revisando_watchfolders": "Agregando tareas desde watchfolders", "Separator": "Separador",
               "nombre_preset_duplicado": "Ya existe un preset con este nombre. Desea sobreescribirlo?",
               "warning_falta_camara": "No hay cámara"}

diccionario.update(
    {"modo_animacion": "Animación", "modo_frames": "Frames", "modo_script": "Script", "enabled": "habilitados",
     "disabled": "deshabilitados", "colorize_per_state": "Colorizar por estado"})

# tooltips:
diccionario.update({"header tooltip": "Arrastrar columna para reordenar\nClick derecho para opciones"})

diccionario.update({"frames renderizados": "Frames renderizados", "frame renderizado":
    "Frame renderizado", "Ruta Blender": " Ruta Blender "})
diccionario.update({"[BOTON]_dispositivos": "Dispositivos"})

# mensajes status interrumpidos y completos
diccionario.update({"interrumpidos omitir": "omitiendo interrumpidos", "interrumpidos continuar":
    "retomando interrumpidos", "interrumpidos reiniciar":
                        "reiniciando interrumpidos",
                    "terminados omitir": "omitiendo terminados",
                    "terminados reiniciar": "reiniciando terminados",
                    "estado status": "Estado: ", "tooltip_importar_skin": "Importar skin",
                    "tooltip_exportar_skin": "Exportar skin",
                    "tooltip_agregar_skin": "Crear nueva skin en base a la actual",
                    "tooltip_quitar_skin": "Quitar skin actual"})

diccionario.update({"titulo hay interrumpidos": "Interrumpidos", "mensaje interrumpidos":
    "Algun/os blend/s de la cola han sido INTERRUMPIDOS. Qué hacer con ellos?",
                    "titulo ya renderizados": "Blends ya renderizados", "mensaje ya renderizados":
                        "Algun/os blend/s de la cola ya han sido RENDERIZADOS. Qué hacer con ellos?",
                    "mensaje interrumpir render":
                        '¿Interrumpir render en curso? \nSi elige "No", se detendrá la cola luego de '
                        'completar el render actual', "procesamiento hueco terminado":
                        "Procesamiento terminado. No se renderizó ningún blend.",
                    "guardar_settings_gpu": "Usar esta configuración\n"
                                            "como default para nuevos \n"
                                            "items agregados",
                    "patron_nombrado_default": "Usar como default para nuevos items."})

# status castellano
diccionario.update(
    {"vacia": "Cola vacía. ", "no_iniciada": "Procesamiento no iniciado. ", "renderizando":
        "Renderizando blend(s): ", "finalizada": "Procesamiento completo: ", "detenida":
         "Procesamiento interrumpido: "})

diccionario.update({"Idioma": "Idioma", "establecer frame automaticamente":
    "Usar frame 1", "Reproducir sonido": "Reproducir sonido al terminar de renderizar",
                    "agregar en modo frames":
                        "Al añadir un blend en modo Frames:   ", "advertencia escenas pesadas":
                        "*Estas opciones pueden demorar la carga de blends pesados.",
                    "elegir escena al duplicar":
                        "Permitir elegir qué escena a renderizar para la nueva instancia*",
                    "duplicar multiescena":
                        "Al duplicar un blend con más de una escena:", "escenas_elegir":
                        "Permitir elegir qué escena(s) agregar a la cola*", "escenas_todas":
                        "Añadir todas*", "escenas_activa": "Usar la escena activa",
                    "al agregar multiescena":
                        "Con más de una escena:",
                    "sin_skin": "Ninguna (Default S.O.)", "bdark": "B-Renderon Dark",
                    "tooltip_watchfolders": "Activar watchfolders.\nClick derecho para modificar",
                    "detener_item": "Detener render del blend elegido",
                    "Add range to list": "Agregar rango a lista", "leave_as_is": "Respetar",
                    "replicate": "Replicar", "disable": "Desactivar", "guardar_como_preset": "Guardar como preset"})

# log:

diccionario.update({"procesamiento iniciado": "\nProcesamiento iniciado: ", "error nuevo intento":
    " - Error! Nuevo intento a continuación...", "desde interrupcion":
                        " de ellos desde la última interrupcion)",
                    "promedio por frame": "Tiempo promedio por frame: "})

diccionario.update({"lbl_visor_imagenes": "Imágenes",
                    "lbl_visor_secuencias": "Secuencias",
                    "lbl_visor_videos": "Videos",
                    "blender_player": "Blender Player", "system_default": "Default Sistema",
                    "custom_viewer": "Personalilzado"})

diccionario.update({"al_agregar_blends": "Al agregar blends",
                    "Can't rename this mode!": "No se puede renombrar este modo!"})

# nombres columnas

diccionario.update({"ruta_blend": "Ruta", "nombre_blend": "Blend",
                    "loQue": "Modo", "estado": "Estado", "tag_blender": "Blender", "escena": "Escena",
                    "view_layer": "View layer", "camara": "Cámara", "inicio": "Inicio", "fin": "Fin",
                    "args_extra": "Args. Extra", "nombres_dispositivos": "Dispositivos", "frames_display": "Frames",
                    "nombrado": "Ruta/Nombre de salida", "from_now": "from now",
                    "after_starting": "after starting",
                    "scheduler_opciones_stop": "Si hay renders activos al momento de detener:",
                    "tooltip_scheduler": "Establecer horarios para renderizar",
                    "lbl_timeout": "Detener inactivos luego de",
                    "alerta_camara": "Asegurese de que haya una cámara activa en la escena que desea"
                                     " renderizar.",
                    "alerta_viewlayer_escena": "Está cambiando de escena luego de haber elegido view"
                                               " layer.\nAsegurese de que la escena elegida contenga"
                                               " el view layer elegido o actualice el view layer.",
                    "Nueva": "New", "Old": "Anterior",
                    "Relocate blend(s)": "Reubicar blend(s)",
                    "explicacion_relativos": "Comenzar con + o - para desplazar valores",
                    "Split range": "Distribuir rango",
                    "tooltip_split": "Distribuir rango entre los items elegidos\no entre un número de copias establecido",
                    "label_numero_splits": "Numero de items en los que distribuir el rango:",
                    "variantes_resultados_combinados": "Mostrando resultados combinados\npara los items elegidos",
                    "Hide": "Ocultar", "Align": "Alinear", "Left": "Izquierda", "Right": "Derecha",
                    "Center": "Centro", "jobs": "trabajos", "job": "trabajo",
                    "usar_todos": "Usar para todos los items restantes",
                    "distribuir_blenders": "Asignar diferentes builds a los\nitems de la cola elegidos",
                    "distribuir_dispositivos": "Asignar un dispositivo diferente\na cada item elegido en la cola",
                    "mantener_despierta": "Mantener PC despierta durante el renderizado",
                    "ico_blender": "",
                    "msg_colapso_splitter": "La zona de estados está por ser colapsada.\nPuede recuperarse"
                                            " arrastrandoo el borde derecho hacia la izquierda.\nProceder?",
                    "chk_mostrar_columna_estado": "Mostrar columna de estados en la tabla principal",
                    "Info/Settings": "Información/Configuración",
                    "Adding/Removing": "Añadir/Quitar Blends",
                    "Open/View": "Abrir/Ver",
                    "Queues Management": "Administrar Colas",
                    "Jobs Adjustments": "Ajustes Tareas",
                    "State Functions": "Funciones de Estado", "Height": "Altura",
                    "filas_alternan": "Alternar colores", "Icons": "Iconos", "Text": "Texto",
                    "Ui Text": "Texto",
                    "Buttons Text": "Texto en botones",
                    "Autoraise": "Estilo dinámico", "Queue": "Cola", "Buttons display": "Botones",
                    "btn_abrir_blend": "Abrir Blend", "Auto shutdown": "Apagado\nautomático",
                    "settings_apariencia": "Más ajustes visuales", "Start": "Iniciar",
                    "Scheduler": "Programado", "tltp_start": "Iniciar procesamiento",
                    "tltp_stop": "Detener procesamiento",
                    "Basic Blender Args": "Argumentos básicos de Blender",
                    "alerta_args_inaplicados": "Hay argumentos que fueron configurados pero no añadidos."
                                               "\nAbandonar la ventana de argumentos extra sin añadirlos?",
                    "titulo_args_inaplicados": "Abandonar la ventana sin añadir los argumentos configurados?",
                    "averiguar_dispositivos": "Averiguar dispositivos disponibles", "gpu_fija_exe":
                        "Actualmente el ejecutable de blender para este item\n"
                        "está establecido por el dispositivo GPU asignado.",
                    "parallel_gpu": "Instancias paralelas\npor GPU",
                    "forzar_motor": "Forzar motor", "tooltip_forzar_motor":
                        "Forzar el motor de render a coincidir\ncon el que se le asignaron dispositivos",
                    "tooltip_parallel_gpu": "Los items con esta opción activada se renderizarán\ncon uno de los dispositivos seleccionados\ntan pronto como ese dispositivo no esté siendo\nocupado por otros items previos en la cola, en una\ninstancia de render paralela a las de los items previos si las hubiera.",
                    "tooltip_set_path_eevee": "Elija un ejecutable de blender al que previamente le haya\nasignado, mediante el software del gpu o configuraciones del sistema operativo\nla placa de video nombrada a la izquierda.",
                    "tooltip_columna_frames": "Numero de frames renderizados para items terminados o interrumpidos\nFrame actual para items en render. ",
                    "tooltip_eta": "Tiempo restante estimado durante el renderizado.",
                    "alerta_tag_eevee": "El nombre elegido está reservado para uso interno.\nCambielo por favor",
                    "setting_instancias_default": "Instancias paralelas de render por defecto",
                    "alerta_path_eevee_gpu": "B-renderon no logra encontrar el ejecutable de Blender\n"
                                             "asociado para Eevee con el gpu seleccionado.\nEn cambio,"
                                             " se renderizará con la versión de Blender por defecto.",
                    "frames_predef": "Frame(s) predefinido(s)", "Always ask": "Preguntar",
                    "tooltip_auto_duplicate": "Al añadir items a la cola\nduplicarlos automáticamente para que\ncada dispositivo pueda procesar uno de ellos\nen cada momento",
                    "tooltip_overwrites": "Al renderizar una escena con multiples\ninstancias paralelas, esta opción\nasegura que las diferentes instancias\nrendericen frames diferentes",
                    "script_ask": "Pedir script",
                    "tooltip_script_ask": "Al añadir blends en este modo\npedir script y asignárselo.",
                    "msg_setear_gpus": "Este modo requiere la asignación de un conjunto de GPUs\nElegirlo ahora?",
                    "titulo_setear_gpus": "Se requiere configuración!",
                    "Change/Set": "Cambiar/Establecer",
                    "Individual text log(s)": "Text logs individuales", "modo_ingesta": "Modo ingesta",
                    "Queues options": "Opciones de colas", "Modes options": "Opciones de modos",
                    "tooltip_hay_opciones": "Click derecho o click sostendio para más opciones",
                    "tooltip_reset_sliders": "Doble click o click derecho para resetear valor",
                    "(Blend path)/render/(Blend name)": "(Ruta Blend)/render/(Nombre Blend)",
                    "Scene output path": "Ruta de salida de la escena", "Apply to": "Aplicar a",
                    "File output nodes": "Nodos file output", "(drag and drop)": "(arrastrar y soltar)",
                    "usar_output_original": "Ruta de salida original",
                    "usar_patron_salida": "Ruta de salida por patrón",
                    "tareas_post_render": "Tareas post-render",
                    "explicacion_tareas": "Ejecutar post-render",
                    "titulo_ventana_estimador": "Estimar tiempo total de procesamiento",
                    "explicacion_estimador": "(Experimental) Estimar el tiempo total de procesamiento de la cola, "
                                             "renderizando uno o más frames por item.Mientras más frames "
                                             "se usen, más lenta de realizar la estimación pero más"
                                             " precisa.",
                    "opcion_estimador": "Estimar tiempo de procesado", "Scale": "Escala",
                    "Queue rows": "Filas", "color_set": "Conjunto", "Disabled": "Deshabilitados",
                    "Progress bar": "Barras de progreso", "Auto duplicate jobs": "Auto duplicar tareas",
                    "Font": "Tipografía", "Dock to Top": "Acoplar en la parte superior",
                    "Dock to bottom": "Acoplar en la parte inferior",
                    "Dock to left": "Acoplar a la izquierda",
                    "Dock to right": "Acoplar a la derecha",
                    "Save livelog as": "Guardar livelog como",
                    "Toggle Dock Floating": "Alternar entre acoplado y flotante",
                    "Jump to End": "Saltar al final",
                    "Jump to Beginning": "Saltar al inicio",
                    "Jump to Next Save/Append Entry": "Saltar a la siguiente entrada de guardado",
                    "Jump to Previous Save/Append Entry": "Saltar a la entrada anterior de guardado",
                    "Highlighted collection": "Coleccion elegida",
                    "tooltip_default_token_nombrado": "Arrastrar y soltar en el campo ruta"
                                                      " o nombre del patrón",
                    "tooltip_default_token_nombrado_incremental": "Arrastrar y soltar en el campo ruta"
                                                                  " o nombre del patrón. Sostenga shift al soltar para emplear la siguiente clave del token.\nSostenga alt para emplear la siguiente clave de coleccion repartida",
                    "tooltip_collection_token": "Este token se reemplazará por el nombre de la colección\napropiada en la ventana de colecciones según la letra entre corchetes.",
                    "warning_token_camaras": "Este token se reemplazará por el nombre de la cámara seleccionada desde B-renderon.\nNo funciona con cámaras animadas mediante marcadores",
                    "Original + camara": "Original\nOriginal + camara", "btn_colecciones_split": "Repartir"
                    })

diccionario.update({"estado_terminado": "Terminado",
                    "estado_renderziando": "Renderizando",
                    "estado_interrumpido": "Interrumpido", "Nombrado customizado": "Custom",
                    "Dispositivos de render": "Dispositivos",
                    "info_multiples_jobs": "Multiples tareas seleccionadas. Mostrando la configuración de la tarea activa. Los interruptores y los tokens con los que se interactúe (indicados por el icono de lápiz) se propagarán a todas las tareas seleccionadas.",
                    "preview_job": "basada en la primer tarea de las seleccionadas",
                    "ingresar_tag_blender": "Por favor ingrese un nombre para este Blender:",
                    "nombre": "Nombre", "version": "Versión", "ruta": "Ruta",
                    "Set path": "Establecer ruta", "Background mode": "Sin interfaz"
                    })

# alertas
diccionario.update(
    {"alerta_archivo_skin_invalido": "El archivo elegido no es un skin de B-renderon válido.",
     "alerta_nombre_repetido": "Ya existe un skin con ese nombre!\nElija uno diferente por favor.",
     "alerta_colecciones_diferentes": "¡Estructuras de colecciones diferentes detectadas!\nLos trabajos con colecciones que difieren de las del trabajo activo serán omitidos.",
     "Yes": "Si", "mensaje_blender_nuevo": "Se halló una nueva versión de Blender en el sistema.\nUsarla por defecto?",
     "nueva_version": "Nueva versión de blender", "no_volver_a_mostrar": "No volver a mostrar esto"

     })

# tooltips

diccionario.update({
    "tooltip_collection_exclusion": "Excluir/Incluir coleccion.\nAlt+Click para afectar subcolecciones",
    "tooltip_click_select_all": "Click para elegir todas",
    "tooltip_releer_viewlayers": "Leer blend para actualizar lisita de view layers",
    "tooltip_releer_escenas": "Leer blend para actualizar lista de escenas",
    "tooltip_releer_camaras": "Leer blend para actualizar lista de camaras",
    "tooltip_releer_colecciones": "Leer blend para actualizar lista de colecciones",
    "tooltip_add_blender": "Click para agregar un ejectutable de Blender.\nTambién se puede arrastrar y soltar un ejecutable de blender desde un explorador de archivos.",
    "tooltip_double_click_dismiss": "(Doble click para ocultar este mensaje)"

})
