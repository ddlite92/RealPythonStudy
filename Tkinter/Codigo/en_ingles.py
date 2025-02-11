diccionario = {"Propiedades Extra": "Extra Properties", "Aplicar": "Apply", "Nombre:": "Name:",
               "Ruta:": "Path:",
               "Explorar": "Browse", "Escena": "Scene", "Frames alternativos de Inicio/Fin:":
                   "Alternative Start/End frames:", "Inicio:": "Start:", "Fin:": "End:",
               "Relativo": "Relative", "Relativa": "Relative", "Argumento:": "Argument:",
               "Ejemplo:":
                   "Example:", "Configurar B-Renderon!": "B-Renderon Settings",
               "Blender Principal:": "Main Blender:", "Idioma:": "Language:",
               "Ruta Blender": " Blender Path ",
               "DETENER": "      STOP      ", "TIRAR RENDERS": "   RENDER   ",
               "modo_ingesta": "Ingest mode", "Quitar": "Remove", "Quitar Seleccionados": "Remove Selected",
               "Duplicar Seleccionados":
                   "Duplicate Selected", "Propiedades Extra 2L":
                   "Extra Properties", "Animación": "Animation", "modo_animacion": "Animation",
               "modo_frames": "Frames", "modo_script": "Script", "modo_parallel": "Parallel GPU (Cycles)",
               "Modo": "Mode", "Estado": "Status",
               "Args. Extra:":
                   "Extra Args.", "Cambiar Escena":
                   "Scenes", "Cambiar rango frames": "Frames Range",
               "Versión de Blender": "Blender version", "Argumentos Extra":
                   "Extra Arguments", "Cámaras": "Cameras", "Nombrado Salida": "Output Filepath",
               "Nombrado de salida": "Output filepath",
               "Explorar ruta Blend":
                   "Browse blend path", "Explorar ruta salida": "Open output path",
               "btn_abrir_blend": "Open Blend",
               "Añadir Blends": "Add Blends", "Quitar Todos":
                   "Remove All", "Ruta": "Path", "Limpiar log": "Clear log", "Limpiar": "Clear",
               "Limpiar live log": "Clear live log",
               "Detener al completar": "Stop after current job(s)", " de ": " of ",
               "sin_skin": "None (O.S. Default)", "bdark": "B-Renderon Dark", "Usar": "Use",
               "Usar todos": "Use all",
               "averiguar_dispositivos": "Find available devices", "Solo CPU": "CPU only",
               "tooltip_watchfolders": "Activate watchfolders.\nRight click to modify",
               "renderizar_blend": "Render selected blend(s)", "guardar_como_preset":
                   "Save as preset",
               "respetar_blender_blend": "Use blender settings and blend's selection",
               "Nombre del preset": "Preset name", "Modificar": "Modify", "Borrar": "Delete",
               "Click derecho para opciones": "Right click for options", "No cambiar": "Original",
               "Nombrado customizado": "Custom",
               "Configurar": "Setup", "Nombre": "Name",
               "usar_preset_nombrado": "Preset",
               "Usar tipo": "Use device type(s)", "Cámara": "Camera",
               "Elegir dispositivos particulares": "Choose devices",
               "Ruta de salida": "Output path", "Para cámaras": "For cameras",
               "Para viewlayers": "For viewlayers",
               "Para watchfolders": "For watchfolders", "Establecer como default": "Set as default",
               "Nombre del blend": "Blend name", "Ruta del blend": "Blend path",
               "Ruta de salida original": "Original output path",
               "Nombre de salida original": "Original output name",
               "Número de frame": "Frame number", "Version de blender": "Blender version",
               "Tiempo": "Time", "elegir_viewlayers": "Select viewlayer(s) to add to the queue",
               "Usar configuracion de viewlayers del blend": "Use blend's viewlayers setup",
               "Leer viewlayers": "Read scene's viewlayers",
               "Ingresar viewlayer por nombre": "Choose viewlayer by name", "Deshabilitar compositing":
                   "Disable compositing"}

# menus contextuales:
diccionario.update(
    {"Modo": "Mode", "Animación": "Animation", "Añadir Blends": "Add Blends",
     "Duplicar": "Duplicate", "Subir": "Move up", "Bajar": "Move down", "Subir a tope":
         "Move to top", "Bajar a tope": "Move to bottom",
     "Quitar": "Remove",
     "Quitar Todos": "Remove All", "Propiedades Extra": "Extra Properties",
     "Configuración": "Settings", "Explorar ruta blend": "Browse blend path",
     "Explorar ruta output": "Browse output path", "Guardar cola": "Export queue file",
     "Abrir cola": "Open queue file"
        , "Recuperar sesión anterior": "Recover last session", "Cambiar escena":
         "Change scene", "Cambiar rango de frames": "Change frames range",
     "Versión de Blender": "Blender version", "Argumentos extra":
         "Extra arguments", "Añadir escenas": "Add scenes", "Duplicar (escenas)": "Duplicate (scenes)",
     "Quitar terminados": "Remove finished", "Guardar": "Save"})

# operaciones tintin

diccionario.update({"Cambiar modo para agregar": "Toggle add mode", "Abrir log": "Open log",
                    "Cerrar logs": "Close all logs", "Mostrar/Ocultar consola blender": "Toggle live log",
                    "Renderizar": "Render", "Deseleccionar todo": "Deselect all",
                    "Seleccionar todo": "Select all", "Menu contextual": "Context menu",
                    "soltar blends en cola": "drop blends in queue", "Comando": "Comamnd",
                    "Atajo": "Shortcut", "Para blends seleccionados": "For selected blends",
                    "General": "General", "Modo": "Mode",
                    "Anterior frame": "Previous frame", "Siguiente frame": "Next frame",
                    "Anterior blend": "Previous blend", "Siguiente blend": "Next blend",
                    "Ver Render": "View render", "Ver render": "View render", "Reproducir": "Play",
                    "Cerrar": "Close", "horas": "hours",
                    "minutos": "minutes", "Horas": "Hours",
                    "Minutos": "Minutes", "El render comenzará en": "Render will start in",
                    "Establecer": "Set", "Aplazar renders": "Delay renders",
                    "Empezar renders en": "Start rendering in"})

# tooltips:
diccionario.update({"header tooltip": "Drag column to reorder\nRight click for options"})

# titulos y mensajes de cuadros de dialogos
diccionario.update({"Atención!": "Warning!", "alerta nombre blender": "Alternative Blender needs a tag!",
                    "alerta nombre default": "The tag for an alternative Blender can't be 'Default'.\nPlease change it.",
                    "alerta ruta": "Invalid blender path", "alerta no encontrados":
                        "Some blends weren't found on this system and were omitted.",
                    "error general lectura": "There were errors reading the saved queue file. Some blends "
                                             "were omitted.",
                    "blend backup": "That's a backup blend."
                                    " Add it anyway?",
                    "archivo malo": "Invalid file type.",
                    "titulo ingrese frames": "Enter the frames you wish to render.", "mensaje ingrese frames":
                        "Enter the frame/s to be rendered. To enter more than one, separate them by commas",
                    "render en proceso": "There's an active render. ¿Quit anyway?", "limpiara log":
                        "This action will permanently delete the contents of the log file, proceed?", "Confirmar":
                        "Confirm Action", "¿Quitar ": "Remove ", "todos": "all", "seleccionados": "selected",
                    "Dispositivos de render ": "Render Devices", "Dispositivos":
                        "Devices", "[BOTON]_dispositivos":
                        "Devices", "Error averiguando dispositivos":
                        "Error looking for devices",
                    "Elegir de la lista": "Choose from list", "Leer escenas del blend":
                        "Read blend's scenes", "Ingresar nombre de escena": "Enter scene's name",
                    "resetear_estado_blends": "Reset state of selected blend(s)",
                    "nombre_preset_duplicado": "A preset with this name already exists. Do you want to replace it?"})

diccionario.update({"frames renderizados": "Frames rendered", "frame renderizado": "Frame rendered"})

diccionario.update({"interrumpidos omitir": "omitting interrupted", "interrumpidos continuar":
    "resuming interrupted",
                    "interrumpidos reiniciar": "restarting interrupted",
                    "terminados omitir": "omitting finished",
                    "terminados reiniciar": "restarting finished", "estado status": "Status: "})

diccionario.update({"titulo hay interrumpidos": "Interrupted blends", "mensaje interrumpidos":
    "Some of the blends in queue have been INTERRUPTED while rendering."
    " \nWhat to do with them?", "Continuarlos": "Resume rendering", "Omitirlos": "Omit",
                    "Reiniciarlos": "Restart rendering", "titulo ya renderizados": "Already rendered blends",
                    "mensaje ya renderizados": "One or more jobs in the queue have already been processed."
                                               " \nWhat to do with them?", "mensaje interrumpir render":
                        '¿Interrupt active render? \nIf you choose "No", processing will stop after the'
                        ' render currently active finishes.', 'Procesamiento terminado':
                        "Processing finished", "procesados": "processed", "procesado": "processed",
                    "procesamiento hueco terminado": "Processing finished. No items rendered"
                    })

diccionario.update({"en cola": "in queue", "Cola": "Queue", "guardar_settings_gpu": "Make default\n"
                                                                                    "for new items",
                    "patron_nombrado_default": "Use by default for new items",
                    "Ventana de Argumentos Extra": "Extra arguments window", "tareas": "jobs",
                    "tooltip_importar_skin": "Import Skin",
                    "tooltip_exportar_skin": "Export Skin",
                    "tooltip_agregar_skin": "Create new skin based on current one",
                    "tooltip_quitar_skin": "Remove current skin"})

diccionario.update({"procesamiento iniciado": "\nProcessing started: ", "error nuevo intento":
    " - Error! Starting new attempt...", "en total": "in total", "desde interrupcion":
                        " of them since last interruption)", "promedio por frame":
                        "Average rendering time per frame: ", "Promedio: ": "Average: ",
                    "Tiempo estimado restante: ": "Estimated remaining time: ",
                    "interrumpido": "interrupted", "finalizado": "finished", "procesamiento": "processing",
                    "Inicio": "Start", "Fin": "End", "Renderizado con Blender": "Rendered with Blender",
                    "Tipo de render":
                        "Render mode", "Continuando render interrumpido": "Resuming interrupted render",
                    "Frame inicio elegido": "Selected start frame", "Frame fin elegido":
                        "Selected end frame", "fallados": "failed", "fallado": "failed",
                    "Tiempos por frame: ": "Per frame rendering times: "})

diccionario.update({"Acerca de": "About", "Versión": "Version",
                    "Render manager para blender": "Render manager for blender"})

diccionario.update(
    {"Todos los archivos": "All Formats", "Elegir archivo": "Choose File", "Elegir Archivos": "Choose Files",
     "Guardar como": "Save as"})
# self.simbolos_estados = {"no_comenzado": "■ ", "renderizando": "► ", "terminado":
# "✓ ", "interrumpido": "☒ ", "fallo": "❌ "}


# botones standard
diccionario.update({"Aceptar": "Ok", "Cancelar": "Cancel"})

diccionario.update({"establecer frame automaticamente":
                        "Use frame 1", "Ingresar frames": "Enter frames", "agregar en modo frames":
                        "In Frames mode:    ", "advertencia escenas pesadas":
                        "*This option might make adding items to the queue slower, especially for heavy blend files.",
                    "escenas_elegir":
                        "Let me choose*", "duplicar multiescena":
                        "When duplicating a blend with more than one scene:", "escenas_todas":
                        "Add all*", "escenas_activa": "Use active scene",
                    "al agregar multiescena":
                        "With more than one scene:",
                    "Mantener escena":
                        "Keep scene", "Generales": "General", "Escenas": "Scenes",
                    "Más opciones": "More options",
                    "Iniciar con la ultima sesion": "Start with last session",
                    "Reproducir sonido": "Play sound when processing is completed",
                    "setting_instancias_default": "Default parallel rendering instances", "Agregar": "Add",
                    "Doble click para anexar": "Double click to dock",
                    "Seleccione un blend para ver su live log": "Select a file to see it's live log.",
                    "Argumentos": "Arguments",
                    "Argumentos útiles": "Useful arguments", "Distribuir": "Distribute",
                    "Abrir blend": "Open blend",
                    "Intentar detectar y  continuar renders fallidos": "Try to detect and resume failed"
                                                                       " renders",
                    "faltan permisos": "Error trying to save settings file."
                                       "\nB-renderon needs file writing permisions to save your settings"
                                       " and log. \n"
                                       "Try to run B-renderon as superuser (root/administrador)\nor from a"
                                       " location with writing permission.",
                    "Auto-asignar blenders": "Automatically assign blender versions",
                    "Cambiar cámara": "Change camera", "Resolución": "Resolution",
                    "Resolución %": "Resolution %",
                    "Resolución X": "Resolution X", "Resolución Y": "Resolution Y",
                    "Usar distancia focal": "Use Depth of field",
                    "Renderizar viewlayer específico": "Render specific viewlayer"})

diccionario.update(
    {"cámaras": "cameras", "Elegir cámara(s) para añadir a la cola": "Select camera(s) to add to the queue",
     "Leer cámaras": "Read scene cameras", "Ingresar cámara por nombre": "Enter camera's name",
     "Nombrado de archivos de salida:": "Output filepath:",
     "Ajustar para los blends elegidos": "Manage for selected blends",
     "Usar blender en modo factory": "Use blender factory settings", "Renderizando": "Rendering"})

diccionario.update({"Previamente procesados":
                        "Previous jobs",
                    "finalizados": "finished", "interrumpidos": "interrupted", "omitir": "omit",
                    "preguntar": "ask", "reiniciar": "restart", "continuar": "resume"})

diccionario.update({"Interfaz": "Interface", "Sistema": "System", "General": "General", "Idioma": "Language"})
diccionario.update({"Elegir script para renderizar": "Choose rendering script"})

diccionario.update(
    {"No se encuentra la carpeta": "Folder not found", "alerta_file_not_found": "File not found"})

diccionario.update({"Elegir escenas": "Select scenes", "Elegir qué escenas agregar a la cola":
    "Select scene(s) to add to the queue", "Elegir todas": "Select all",
                    "Usar escena activa en el blend": "Use blend's active scene",
                    "Usar cámara activa en la escena": "Use scene's active camera",
                    "Dejar campos vacíos para usar los valores originales":
                        "Leave fields empty to use original values",
                    "usar_patron_salida": "Output filepath pattern",
                    "usar_output_original": "Original output filepath",
                    "Nombrado": "Name", "detener_item": "Stop selected blend's render"
                    })

diccionario.update({"Guardar como preset": "Save as custom preset", "leave_as_is": "Leave as is"})

# status ingles
diccionario.update(
    {"vacia": "Queue is empty. ", "no_iniciada": "Processing not yet started. ", "renderizando":
        "Processing job(s): ", "finalizada": "Processing completed: ", "detenida": "Processing interrupted: "})

diccionario.update({"Visor de renders": "Render viewer", "lbl_visor_imagenes": "Stills",
                    "lbl_visor_secuencias": "Sequences", "lbl_visor_videos": "Videos",
                    "blender_player": "Blender Player", "custom_viewer": "Custom",
                    "system_default": "System Default"})

diccionario.update({"Colas": "Queues", "Recientes": "Recent", "Actual": "Current", "Abrir archivo": "Open file",
                    "Nueva cola nombrada": "New named queue",
                    "Ingresar nombre para la nueva cola": "Enter a name for the new queue",
                    "Ingresar nuevo nombre para la cola": "Enter new name for queue",
                    "Exportar": "Export", "Añadir desde archivo": "Add from file"})

diccionario.update({"al_agregar_blends": "When adding blends"})

diccionario.update({"ruta_blend": "Path", "nombre_blend": "Blend",
                    "loQue": "Mode", "estado": "Status", "tag_blender": "Blender", "escena": "Scene",
                    "view_layer": "View layer", "camara": "Camera", "Iniciar": "Start",
                    "Detener": "Stop", "ico_blender": "", "frames_display": "Frames",
                    "args_extra": "Extra Args.", "nombres_dispositivos": "Devices",
                    "nombrado": "Output filepath", "Desactivar/Activar": "Disable/Enable",
                    "desactivado": "disabled",
                    "Establecer horarios para renderizar": "Set rendering start/end times", "A las": "At",
                    "from_now": "from now", "after_starting": "after starting",
                    "scheduler_opciones_stop": "If there's active renders at stop time:",
                    "Esperar se complete el frame": "Wait until frame is saved",
                    "Esperar se complete el blend": "Wait until blend is finished",
                    "Detener de inmediato": "Stop immediately", "tooltip_scheduler": "Render scheduler",
                    "lbl_timeout": "Stuck render timeout",
                    "alerta_camara": "Make sure there's an active camera in the scene you want to render.",
                    "inicio": "start", "fin": "end",
                    "alerta_viewlayer_escena": "You are changing the scene with a view layer selected."
                                               " \nMake sure the new scene contains the selected view layer, "
                                               "or update the view layer selection.",
                    "Agregar todas": "Add all", "explicacion_relativos": "Lead with + or - to offset values",
                    "Split range": "Split range",
                    "tooltip_split": "Distribute frame range between selected blends\nor a specified number of copies",
                    "label_numero_splits": "Number of items to split the range among:",
                    "variantes_resultados_combinados": "Showing combined results\nfor selected items",
                    "Tiempo total de renderizado": "Total rendering time",
                    "usar_todos": "Use for all remaining items",
                    "Elegir frames": "Choose frames", "Lista": "List", "Rango": "Range",
                    "distribuir_blenders": "Assign a different blender build to each selected job",
                    "distribuir_dispositivos": "Assign a different device to each selected job",
                    "mantener_despierta": "Keep PC awake during rendering", "VER/ABRIR": "OPEN/VIEW",
                    "msg_colapso_splitter": "The jobs status zone is about to be collapsed.\nIt can be"
                                            " restored by dragging again from the right.\nProceed?",
                    "chk_mostrar_columna_estado": "Show the status column in the main table",
                    "filas_alternan": "Alternating colors",
                    "Autoraise": "Dynamic Style", "settings_apariencia": "More",
                    "tltp_start": "Start processing queue", "tltp_stop": "Stop processing queue",
                    "Renombrar": "Rename",
                    "alerta_args_inaplicados": "There's arguments that have been customized but not added."
                                               "\nAre you sure you want to leave without adding them?",
                    "titulo_args_inaplicados": "Confirm Leaving Without Adding Customized Arguments?",
                    "Filtrar": "Filter", "gpu_fija_exe": "The blender executable for this job\n"
                                                         "is currently defined by the device selected.",
                    "parallel_gpu": "Parallel processing", "forzar_motor": "Force render engine",
                    "tooltip_forzar_motor":
                        "Force this job to be rendered with the Engine\nfor which devices where set.",
                    "tooltip_parallel_gpu": "Jobs with this setting on will be rendered\nwith one of the"
                                            " selected devices\nas soon as it is not being used\nby any"
                                            " previous job in the queue, in parallel with\nany renders being"
                                            " processed with other devices.",
                    "tooltip_set_path_eevee": "Choose a blender executable which you've setup\nvia your gpu software or o.s. settings\nto use the device to the left.",
                    "tooltip_columna_frames": "Number of rendered frames for finished/interrupted jobs.\nFrame being rendered for currently rendering jobs.",
                    "tooltip_eta": "During rendering, estimated time to completion.",
                    "alerta_tag_eevee": "Selected name is reserved.\nPlease change it.",
                    "alerta_path_eevee_gpu": "B-renderon can't find the blender executable\ncorresponding to "
                                             "the Eeevee device selected.\nDefault Blender (and Eevee device)"
                                             " will be used instead.",
                    "Dispositivos de render": "Render devices", "Elegir": "Select",
                    "frames_predef": "Predefined frame(s)",
                    "Motor": "Engine",
                    "tooltip_auto_duplicate": "When adding an job to the queue\nduplicate it so all gpu's"
                                              " can render\na frame at the same time",
                    "tooltip_overwrites": "When rendering one scene with multiple\nparallel instances, "
                                          "this makes sure\ndifferent instances render different frames",
                    "Nuevo modo": "New mode", "Editar actual": "Edit current",
                    "Quitar actual": "Remove current", "Usar argumento": "Use arg",
                    "script_ask": "Ask for a script",
                    "tooltip_script_ask": "When adding jobs in this mode\nask for a script to be assinged to them.",
                    "Restaurar modos predefinidos": "Restore built-in modes",
                    "msg_setear_gpus": "This mode requieres a set of GPU devices to be assigned.\nAssign them now?",
                    "titulo_setear_gpus": "Setup needed!",
                    "Duplicar en sitio": "Duplicate in place", "Mover": "Move", "Usando": "Using",
                    "Abrir logs individuales": "Show individual log(s)", "Cerrar todos": "Close all",
                    "Cerrar logs texto": "Close text logs",
                    "Leer colecciones": "Read collections",
                    "Colecciones": "Collections", "Restaurar": "Restore", "Elegir cola": "Select queue",
                    "Elegir modo ingesta": "Select ingest mode",
                    "tooltip_hay_opciones": "Right click or hold for options",
                    "tooltip_reset_sliders": "Double click or right click to reset value",
                    "Exportar actual": "Export current",
                    "Cambiar mundo": "Change World",
                    "Original + camara": "Original\nOriginal + camera", "Carpetas": "Folders",
                    "Activa": "Active",
                    "Patron": "Pattern",
                    "Tipo": "Type",
                    "explicacion_tareas": "Run after render",
                    "tareas_post_render": "Post-render tasks",
                    "titulo_ventana_estimador": "Total processing time estimation",
                    "opcion_estimador": "Processing time estimation",
                    "Tiempo total estimado": "Total estimated time",
                    "Calcular": "Estimate",
                    "explicacion_estimador": "(Experimental) Estimate the total rendering time for the queue by rendering"
                                             " one or more frames per job. The more frames used, the slower"
                                             " but more precise the estimation.",
                    "Elegir carpeta": "Choose folder", "color_set": "Color set",
                    "colorize_per_state": "Colorize per state",
                    "revisando_watchfolders": "Adding jobs from watchfolders",
                    "tooltip_default_token_nombrado": "Drag and drop onto the path or name fields of the pattern",
                    "tooltip_collection_token": "This token get's replaced by the name of the corresponding collection\nfor the key between brackets as set in the collections window .",
                    "warning_token_camaras": "This token get's replaced by the name of the camera assigned to each job in B-renderon.\nIt doesn't work with cameras animated with markers",
                    "Original + viewlayer": "Original\nOriginal + Viewlayer",
                    "Original + job index": "Original\nOriginal + Job index",
                    "Original + Collection": "Original/Collection\nOriginal"

                    })

diccionario.update({"estado_terminado": "Finished",
                    "estado_renderziando": "Rendering",
                    "estado_interrumpido": "Interrupted",
                    "btn_colecciones_split": "Split"})

diccionario.update({"alerta_archivo_skin_invalido": "Selected file is not a valid B-renderon skin.",
                    "alerta_nombre_repetido": "There's already a skin with that name.\nPlease choose a different name.",
                    "tooltip_collection_exclusion": "Toggle collection exclusion.\nHold alt to toggle children",
                    "info_multiples_jobs": "Multiple jobs selected. Showing active job settings. Toggles and tokens interacted with (indicated by the pencil icon) will be propagated to all selected jobs that share the same collection structure.",
                    "alerta_colecciones_diferentes": "Different collection structures detected!\nJobs with collections that differ from those of the active job will be omited.",
                    "preview_job": "based on the first of the selected jobs", "mensaje_blender_nuevo": "A newer blender version was found on the system.\nSet it as the default?",
                    "nueva_version": "New blender version", "no_volver_a_mostrar": "Don't show this again",
                    "ingresar_tag_blender": "Please enter a name for this Blender:",
                    "nombre": "Name", "version": "Version", "ruta": "Path", "warning_falta_camara": "Camera missing"

                    })

# toooltips

diccionario.update({
    "tooltip_default_token_nombrado_incremental": "Drag and drop onto the path or name fields of the pattern.\nHold shift during drag and drop to use the next key.\nHold alt to use the next split collections key",
    "tooltip_colection_token": "Click to toggle the assignment of this collection's name to collection token for output filepath patterns.\nShift+Click on different collections to assign different collection tokens.",
    "tooltip_releer_colecciones": "Read blend to update collections list", "tooltip_restaurar": "Revert",
    "tooltip_click_select_all": "Click to select all",
    "tooltip_releer_viewlayers": "Read blend to update view layers list",
    "tooltip_releer_escenas": "Read blend to update scenes list",
    "tooltip_releer_camaras": "Read blend to update cameras list",
    "tooltip_add_blender": "Click to add a Blender executable.\nYou can also drag and drop a Blender executable from your file explorer.",
    "tooltip_version_mismatch": "It seems this blend file was saved with a different Blender version than the one assigned for rendering.",
    "tooltip_double_click_dismiss": "(Double-click to dismiss this warning.)"



})
