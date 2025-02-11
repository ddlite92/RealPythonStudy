#
# B-renderon is a render manager for Blender 3d.
# Copyright (C) 2024  Tomas Fenoglio
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the h ope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
import utilidades_tiempo as UtilidadesTiempo
import alertas as Alertas
from app_context import app


if getattr(sys, 'frozen', False):
    ruta_base = os.path.dirname(sys.executable)
else:
    ruta_base = os.path.dirname(os.path.realpath(__file__))

token_nombre_original = "[ORIGINAL_OUTPUT_NAME]"
token_path_original = "[ORIGINAL_OUTPUT_PATH]"
token_node_label = "[NODE_LABEL]"
token_marker_camera = "[CAMERA_MARKER]"
token_regular_marker = "[REGULAR_MARKER]"
token_start_time = "[START_TIME]"

separador_run_data = "; "
handle_frame_path = "br-info_frame_path:"
handle_dispositivos = "DISPOSITIVOS: "
handle_tipo = "TIPO: "
handle_scenes_info_output = "SCENES_INFO_OUTPUT:"
prefijo_nodos_output = "OUTPUT_NODES: "
prefijo_colecciones = "COLLECTIONS_DATA: "
prefijo_viewlayer_activo = "ACTIVE_VIEWLAYER: "
prefijo_escena_activa = "ACTIVE_SCENE: "
handle_colecciones_use = "COLLECTIONS_USE_TOGGLES:"
handle_output_nodes_pattern = "OUTPUT_NODES_PATTERN:"
handle_pattern_separator = "PATTERN_SEPARATOR:"
handle_apply_to_nodes = "APPLY_PATTERN_TO_NODES:"
handle_output_pattern = "OUTPUT_FILEPATH_PATTERN:"
handle_camera_token = "CAMERA_MARKER_TOKEN:"
handle_viewlayer_name = "VIEW_LAYER_NAME:"
handle_compositing_action = "COMPOSITING_HANDLING:"
handle_scene_data = "**SCENE_DATA: "
separador_colecciones_arg = "/*CEC*/"
ruta_base_configuraciones = os.path.join(ruta_base, "settings")
ruta_configuraciones_ventana = os.path.join(ruta_base_configuraciones, "mainwindow.ini")
ruta_settings = os.path.join(ruta_base_configuraciones, "settings.json")
ruta_defaultsitem = os.path.join(ruta_base_configuraciones, "itemdefaults.json")
ruta_log = os.path.join(ruta_base, "RendersLog.log")
ruta_base_colas = os.path.join(ruta_base, "queues")
ruta_base_livelogs = os.path.join(ruta_base_colas, "livelogs")
ruta_base_jobinfo = os.path.join(ruta_base, "jitmp")
ruta_base_debug = os.path.join(ruta_base, "debug")
ruta_base_aux_temp = os.path.join(ruta_base, "aux_tmp")
ruta_faltantes_chino = os.path.join(ruta_base_aux_temp, "missing_chinese_translations.json")

prefijo_archivo_scenes_info = "tmp_sc-info_"
ruta_schedules = os.path.join(ruta_base_colas, "RenderSchedule.json")

ruta_versiones_blender = None

ruta_skins = os.path.join(ruta_base_configuraciones, "Skins.json")
separador_blTag = "******"
ruta_base_dispositivos = os.path.join(ruta_base, "devices")
ruta_dispositivos_cycles = os.path.join(ruta_base_dispositivos, "CyclesDevices.json")
ruta_dispositivos_eevee = os.path.join(ruta_base_dispositivos, "EeveeDevices.json")
ruta_script_leer_dispositivos = os.path.join(ruta_base_dispositivos, "CyclesReadDevices.py")
ruta_script_usar_dispositivo = os.path.join(ruta_base_dispositivos, "CyclesUseDevices.py")
ruta_archivo_presets_nombrado = os.path.join(ruta_base_configuraciones, "NamingPresets.json")
ruta_archivo_presets_args_extra = os.path.join(ruta_base_configuraciones, "ExtraArgsPresets.json")

ruta_modos = os.path.join(ruta_base_configuraciones, "Modes.json")

ruta_archivo_debug_infoescenas = os.path.join(ruta_base_debug, "read_info_log.txt")
ruta_archivo_debug_livelog = os.path.join(ruta_base_debug, "livelog.txt")
nombre_acciones_timeadas = UtilidadesTiempo.fecha_hora_sanitizados() + "_activity.txt"  # de este archivo se crea
# como mucho uno por sesion, por eso la fecha es estática, es la de comienzo de sesion
ruta_Archivo_debug_acciones_timeadas = os.path.join(ruta_base_debug, nombre_acciones_timeadas)

ruta_base_scripts = os.path.join(ruta_base, "scripts")
ruta_script_camaras = os.path.join(ruta_base_scripts, "ReadCameras.py")
ruta_script_infos_escena = os.path.join(ruta_base_scripts, "ReadSceneInfo.py")
ruta_script_escenas = os.path.join(ruta_base_scripts, "ReadScenes.py")
ruta_script_colecciones = os.path.join(ruta_base_scripts, "ReadCollections.py")
ruta_script_escenas_jobinfofile = os.path.join(ruta_base_scripts, "GetScenes.py")
ruta_script_elegir_viewlayer = os.path.join(ruta_base_scripts, "UseViewlayer.py")
ruta_script_uso_colecciones = os.path.join(ruta_base_scripts, "UseCollections.py")
ruta_script_output_nodos = os.path.join(ruta_base_scripts, "OutputNodesPath.py")
ruta_script_output_path = os.path.join(ruta_base_scripts, "UseOutputPath.py")
ruta_script_output_markers = os.path.join(ruta_base_scripts, "OutputCameraMarkersPath.py")
ruta_script_desactivar_fileoutputs = os.path.join(ruta_base_scripts, "DisableFOnodes.py")
ruta_archivo_lista_colas = os.path.join(ruta_base_colas, "recent.json")
ruta_script_leer_fileoutputs = os.path.join(ruta_base_scripts, "ReadFileOutputs.py")



subcarpetas = {ruta_base_configuraciones, ruta_base_dispositivos, ruta_base_scripts,
               ruta_base_colas, ruta_base_livelogs}



def update_ruta_versiones_blender(plataforma):
    global ruta_versiones_blender
    ruta_versiones_blender = os.path.join(ruta_base_configuraciones, f"BlenderVersions{plataforma}.json")


def crear_subcarpetas(tipo_build="normal"):
    if tipo_build == "debug":
        subcarpetas.add(ruta_base_debug)

    for subcarpeta in subcarpetas:
        try:
            os.makedirs(subcarpeta, exist_ok=True)
        except:
            Alertas.alerta_permisos()
            sys.exit(app.exec_())


# es metodo para que la traduccion sea dinamica
def filtro_python(traducir):
    return "PYTHON (*.py) ;; " + traducir("Todos los archivos") + "(*.*)"


def ruta_livelog_blend(nombre_blend):
    ruta = UtilidadesTiempo.fecha_hora_sanitizados() + "_" + nombre_blend.rstrip(".blend") + "_livelog.txt"
    ruta = os.path.join(ruta_base_debug, ruta)
    return ruta


def crear_scripts_render():
    scripts_render = {ruta_script_usar_dispositivo: script_usar_dispositivos,
                      ruta_script_elegir_viewlayer: script_usar_viewlayer,
                      ruta_script_uso_colecciones: script_uso_colecciones,
                      ruta_script_output_path: script_blender_output_path}

    for ruta_script in scripts_render:
        crear_script(ruta_script, scripts_render[ruta_script])


def crear_script(ruta_script, script):
    try:
        with open(ruta_script, "w", encoding="utf8") as archivo_script:
            archivo_script.write(script)
    except IOError:
        Alertas.alerta_permisos()
        pass


def expresion_auxiliar_setear_frames(item):
    expr = ""
    if item.inicio:
        if item.inicio.startswith("+") or item.inicio.startswith("-"):
            expr += "scene.frame_start = scene.frame_start " + item.inicio
        else:
            expr += "scene.frame_start = " + item.inicio
        expr += ";"

    if item.fin:
        if item.fin.startswith("+") or item.fin.startswith("-"):
            expr += "scene.frame_end = scene.frame_end " + item.fin
        else:
            expr += "scene.frame_end = " + item.fin
        expr += ";"
    return expr


def expresion_obtener_frame_path():
    expr = "import bpy; import json; scene = bpy.context.scene;"
    # expr += Datas.expresion_auxiliar_setear_frames(item)
    expr += " print('{}' + '(' + scene.render.frame_path(frame=scene.frame_start) + ')')".format(handle_frame_path)

    return expr


errores_viewlayer_elegido = ["Error: cannot render selected viewlayer.",
                             "Selected view layer is not present in selected scene."]
errores_conocidos_render = {"viewlayer": errores_viewlayer_elegido[0],
                            "gpu_memory": "Error: System is out of GPU memory",
                            "permission_denied": "Error: Render error (Permission denied) cannot save",
                            "skipped": "Info: No frames rendered, skipped to not overwrite",
                            "no_camera": "Error: Cannot render, no camera",
                            "generico": "Error: Cannot render", "rango_malo": "Warning: negative range ignored"}
# la razón de tener al ultimo un generico que es parte de otros mensajes es que mejor tener los mensajes
# completos si conocidos, para mostrarlos en el status bar, pero por las dudas haya otros que no se pero
# empiezan igual, agrego ese truncado al último para capturarlo igual
errores_custom = {"crash": "Failure: Blender crash", "timeout": "Failure: reached timeout",
                  "aborted": "Render aborted. Closing blender"}
errores_reintentables = {errores_conocidos_render["gpu_memory"], errores_custom["crash"], errores_custom["timeout"]}

script_viejo_usar_viewlayer = """import sys
import bpy

selected_viewlayer = sys.argv[sys.argv.index("VIEWLAYER:") + 1]
scene_viewlayers = [vl.name for vl in bpy.context.scene.view_layers]

if selected_viewlayer not in scene_viewlayers:
    print("{0}")
    print("{1}")
    sys.exit()
for vl in bpy.context.scene.view_layers:
    vl.use = vl.name == selected_viewlayer
    print("Viewlayer: ", vl.name, "use: ", vl.use)
         """.format(errores_viewlayer_elegido[0], errores_viewlayer_elegido[1])

script_usar_viewlayer = f"""
import sys
import bpy

scene = bpy.context.scene
selected_viewlayer = sys.argv[sys.argv.index("{handle_viewlayer_name}") + 1]
scene_viewlayers = [vl.name for vl in scene.view_layers]

if selected_viewlayer not in scene_viewlayers:
    print("{errores_viewlayer_elegido[0]}")
    print("{errores_viewlayer_elegido[1]}")
    sys.exit()
    
for vl in scene.view_layers:
    vl.use = vl.name == selected_viewlayer
    print("Viewlayer: ", vl.name, "use: ", vl.use)

def handle_compositing(selected_viewlayer, compositing_handle_method, scene):
    if compositing_handle_method == "leave_as_is":
        return
    if compositing_handle_method == "disable":
        scene.use_nodes = False
        return

    nodes = scene.node_tree.nodes
    render_layer_nodes = [node for node in nodes if node.type == 'R_LAYERS' and not node.mute]
    if len(render_layer_nodes) == 1:
        active_rl_node = render_layer_nodes[0]
        if compositing_handle_method == "replicate":
            active_rl_node.layer = selected_viewlayer
        elif compositing_handle_method == "auto":
            scene.use_nodes = active_rl_node.layer == selected_viewlayer
    else:
        scene.use_nodes = False


if scene.use_nodes:
    try:
        method_index = sys.argv.index("{handle_compositing_action}") + 1
        compositing_handle_method = sys.argv[method_index]
        print("Compositing action:", compositing_handle_method)
    except ValueError:
        print("No compositing handling selected.")
    except IndexError:
        print("Compositing handling action missing.")
    else:
        handle_compositing(selected_viewlayer, compositing_handle_method, scene)

"""

script_colecciones = """import bpy
import json

def collect_hierarchy(collection):
    data = {{
        "excluded": collection.exclude,
        "children": {{}}
    }}

    for child in collection.children:
        data["children"][child.name] = collect_hierarchy(child)

    return data

cols_per_vl_per_scene = {{}}
for scene in bpy.data.scenes:
    view_layer_collections = {{}}

    for vl in scene.view_layers:
        view_layer_collections[vl.name] = {{}}

        for collection in vl.layer_collection.children:
            view_layer_collections[vl.name][collection.name] = collect_hierarchy(collection)

    cols_per_vl_per_scene[scene.name] = view_layer_collections

print("{prefijo_colecciones_placeholder}"+json.dumps(cols_per_vl_per_scene))
print("{prefijo_viewlayer_activo_placeholder}"+bpy.context.view_layer.name)
print("{prefijo_escena_activa_placeholder}"+bpy.context.scene.name)

            """.format(
    prefijo_colecciones_placeholder=prefijo_colecciones,
    prefijo_viewlayer_activo_placeholder=prefijo_viewlayer_activo,
    prefijo_escena_activa_placeholder=prefijo_escena_activa
)
script_uso_colecciones = f"""import sys
import bpy
import json

collections_exclude = json.loads(sys.argv[sys.argv.index("{handle_colecciones_use}") + 1])
print("Collections exclusion:", collections_exclude)
view_layer_name = sys.argv[sys.argv.index("{handle_viewlayer_name}") + 1]
print("view layer", view_layer_name)
C = bpy.context
vl = C.scene.view_layers[view_layer_name]
C.window.view_layer = vl

def collections_toggle_recursion(parent):
    for collection in parent.children:
        name = collection.name
        if name in collections_exclude:
            collection.exclude = collections_exclude[name]
        collections_toggle_recursion(collection)

collections_toggle_recursion(vl.layer_collection)

                 """

script_uso_colecciones_legacy = """import sys
import bpy
import json

collections_use = json.loads(sys.argv[sys.argv.index("{0}") + 1])
print("coluse", collections_use)
view_layer_name = sys.argv[sys.argv.index("{1}") + 1]
print("view layer", view_layer_name)
C = bpy.context
vl = C.scene.view_layers[view_layer_name]
C.window.view_layer = vl

def collections_toggle_recursion(parent, use_data):
    for collection in parent.children:
        collection.exclude = use_data[collection.name]["excluded"]
        collections_toggle_recursion(collection, use_data[collection.name]["children"])
        
collections_toggle_recursion(vl.layer_collection, collections_use)
    
             """.format(handle_colecciones_use, handle_viewlayer_name)


script_blender_output_path = f"""import sys
import bpy

def apply_output_nodes(scene, path_pattern, name_pattern):
    path_pattern = path_pattern or ""
    name_pattern = name_pattern or ""
    if not scene.node_tree:
        return
    compositing_nodes = scene.node_tree.nodes
    for node in compositing_nodes:
        if node.type != 'OUTPUT_FILE':
            continue
            
        if not node.get("original_base_path"):
            node["original_base_path"] = node.base_path
        
        original_base_path = node["original_base_path"]
        node.base_path = path_pattern.replace("{token_path_original}", original_base_path)
        label = node.label if node.label else node.name
        node.base_path = node.base_path.replace("{token_node_label}", label)
        
        if not node.get("original_slot_path"):
            node["original_slot_path"] = {{}}
   
        for i, slot in enumerate(node.file_slots):
            key = str(i)
            if key not in node["original_slot_path"]:
                node["original_slot_path"][key] = slot.path
            original_slot_path = node["original_slot_path"][key]
            
            slot.path = name_pattern.replace("{token_nombre_original}", original_slot_path)
            slot.path = slot.path.replace("{token_node_label}", label)
    
        

def update_output_path(scene):
    current_frame = scene.frame_current
    
    updated_full_path = full_original_pattern
    updated_nodes_path = nodes_path_pattern
    updated_nodes_name = nodes_name_pattern
    
    active_regular_marker = active_marker(current_frame, regular_markers)
    active_camera_marker = active_marker(current_frame, camera_markers)
   
    replacements = [
        ("{token_regular_marker}", active_regular_marker),
        ("{token_marker_camera}", active_camera_marker)
    ]
    
    paths_to_update = [updated_full_path, updated_nodes_path, updated_nodes_name]
    
    for token, replacement in replacements:
        for i, updated_path in enumerate(paths_to_update):
            if updated_path:  # Only perform replacement if the path is not None or empty
                paths_to_update[i] = updated_path.replace(token, replacement)

    if full_original_pattern:
        scene.render.filepath = paths_to_update[0]
    
    if nodes_path_pattern:
        apply_output_nodes(scene, paths_to_update[1], paths_to_update[2])


def active_marker(current_frame, markers):
    last_marker = ""
    for frame in markers:
        if frame <= current_frame:
            last_marker = markers[frame]
        else:
            break
    return last_marker

def sort_markers(markers):
    sorted_markers = {{key: markers[key] for key in sorted(markers.keys())}}
    return sorted_markers

def register_handler():
    if update_output_path not in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.append(update_output_path)

def unregister_handler():
    if update_output_path in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(update_output_path)

use_regular_markers = use_camera_markers = None
try:
    pattern_index = sys.argv.index("OUTPUT_FILEPATH_PATTERN:")
    full_original_pattern = sys.argv[pattern_index + 1]
    use_regular_markers = "[REGULAR_MARKER]" in full_original_pattern 
    use_camera_markers = "[CAMERA_MARKER]" in full_original_pattern
except ValueError:
    full_original_pattern = None
except IndexError:
    full_original_pattern = None

try:
    pattern_index = sys.argv.index("OUTPUT_NODES_PATTERN:")
    nodes_path_pattern = sys.argv[pattern_index + 1]
    nodes_name_pattern = sys.argv[pattern_index + 2]
    aux_full_nodes_pattern = nodes_path_pattern + nodes_name_pattern 
    use_regular_markers = use_regular_markers or "[REGULAR_MARKER]" in aux_full_nodes_pattern
    use_camera_markers = use_camera_markers or "[CAMERA_MARKER]" in aux_full_nodes_pattern
except ValueError:
    print("No nodes output pattern.")
    nodes_path_pattern = nodes_name_pattern = None
except IndexError:
    print("Nodes pattern missing.")
    nodes_path_pattern = nodes_name_pattern = None

original_slot_paths = []

if use_regular_markers or use_camera_markers:
    camera_markers = {{}}
    regular_markers = {{}}
    for marker in bpy.context.scene.timeline_markers:
        if marker.camera:
            camera = marker.camera
            camera_markers[marker.frame] = camera.name
        else:
            regular_markers[marker.frame] = marker.name
    camera_markers = sort_markers(camera_markers)
    regular_markers = sort_markers(regular_markers)
    
    if __name__ == "__main__":
        register_handler()
        
elif nodes_path_pattern or nodes_name_pattern:
    apply_output_nodes(bpy.context.scene, nodes_path_pattern, nodes_name_pattern)
    
"""

script_output_markers = f"""import sys
import bpy
import os

full_path_pattern = sys.argv[sys.argv.index("{handle_camera_token}") + 1]

def update_output_path(scene):
    current_frame = scene.frame_current
    active_camera = None
    for marker in scene.timeline_markers:
        if marker.frame <= current_frame:
            if marker.camera:
                active_camera = marker.camera
                print("Active cam:", active_camera)
 
    if not active_camera:
        print("no active")
        active_camera = scene.camera

    if active_camera:
        print("candel abro")
        camera_name = active_camera.name
        try:
            output_path = full_path_pattern.replace("{token_marker_camera}", camera_name)
        except Exception as e:
            print(e)
        print("fpath:", output_path)
        scene.render.filepath = output_path


def register_handler():
    bpy.app.handlers.frame_change_pre.append(update_output_path)

def unregister_handler():
    bpy.app.handlers.frame_change_pre.remove(update_output_path)

if __name__ == "__main__":
    register_handler()
                     """


script_disable_fonodes = """import sys
import bpy

C = bpy.context
file_output_nodes = C.scene.node_tree.nodes
for node in file_output_nodes:
    if node.type == 'OUTPUT_FILE':
        node.mute = True
                     """

script_leer_dispositivos = """import bpy
import json

preferencias = bpy.context.preferences.addons['cycles'].preferences

try:
    preferencias.refresh_devices()
except AttributeError:
    preferencias.get_devices()

dispositivos = {{}}
for dispositivo in preferencias.devices:
    if dispositivo.type in dispositivos:
        try:
            dispositivos[dispositivo.type][dispositivo.name].append(dispositivo.id)
        except KeyError:
            dispositivos[dispositivo.type][dispositivo.name] = [dispositivo.id]
    else:
        dispositivos[dispositivo.type] = {{dispositivo.name: [dispositivo.id]}}

print("{0}", json.dumps(dispositivos))""".format(handle_dispositivos)

script_usar_dispositivos = """import bpy
import sys

tipo = sys.argv[sys.argv.index("{0}") + 1]
dispositivos = sys.argv[sys.argv.index("{1}") + 1:]
print(tipo)
print(dispositivos)
C = bpy.context
C.scene.cycles.device = 'GPU'
if tipo and len(dispositivos):
    prefs_cycles = C.preferences.addons['cycles'].preferences
    try:
        prefs_cycles.compute_device_type = tipo
    except TypeError:
        pass
    try:
        prefs_cycles.refresh_devices()
    except AttributeError:
        prefs_cycles.get_devices()
    for disp in prefs_cycles.devices:
        disp.use = disp.id in dispositivos""".format(handle_tipo, handle_dispositivos)

# todo: por ahora uso script diferente para sacar info de varias escenas que para 1 por un tema de performance pero creo que no tiene goyete, no debe cambiar nada porque el loop es sobre un listado de escenas, no es que haya un switch de escena para casa cosa que yo sepa
script_infos_escena = f"""import bpy 
import json

scene = bpy.context.scene
data = []

viewlayers_names = []
for vl in scene.view_layers:
    viewlayers_names.append(vl.name)

cameras_names = []
try:
    active_camera = scene.camera.name
except AttributeError:
    active_camera = "**Missing**"
for ob in scene.objects:
    if ob.type == "CAMERA":
        cameras_names.append(ob.name)

data.append(scene.name)
data.append(str(scene.frame_start))
data.append(str(scene.frame_end))
data.append(str(scene.frame_step))
data.append(bpy.path.abspath(scene.render.filepath))
data.append(scene.render.frame_path(frame=scene.frame_start))
data.append(viewlayers_names)
data.append(active_camera)
data.append(cameras_names)

print("\\n{handle_scene_data}", json.dumps(data))

"""

script_escenas = f"""import bpy
import json

def get_scene_data(scene):
    data = []

    viewlayers_names = []
    for vl in scene.view_layers:
        viewlayers_names.append(vl.name)

    cameras_names = []
    try:
        active_camera = scene.camera.name
    except AttributeError:
        active_camera = "**Missing**"
    for ob in scene.objects:
        if ob.type == "CAMERA":
            cameras_names.append(ob.name)

    data.append(scene.name)
    data.append(str(scene.frame_start))
    data.append(str(scene.frame_end))
    data.append(str(scene.frame_step))
    data.append(bpy.path.abspath(scene.render.filepath))
    data.append(scene.render.frame_path(frame=scene.frame_start))
    data.append(viewlayers_names)
    data.append(active_camera)
    data.append(cameras_names)

    print("\\n{handle_scene_data}", json.dumps(data))
    
get_scene_data(bpy.context.scene) # get active scene first
for scene in bpy.data.scenes:
    if scene.name == bpy.context.scene.name:
        continue
    get_scene_data(scene)

"""  # en este caso no cambio los frames de la escena para tener el frame_path porque al agregar escenas por ahora se

#    toman los frames de cada escena, no los que había seteado de antes el usuario. Igualmente tiene más chances de ser
#    correcto, si ya se rendereó con nuevos valores hay información más actualizada proveniente de ahí

script_leer_file_outputs = """import bpy
import json
scene = bpy.context.scene
fo_nodes = []
if scene.use_nodes and scene.node_tree:
    node_tree = scene.node_tree
    for node in node_tree.nodes:
        if node.type == 'OUTPUT_FILE' and node.mute == False:
            fo_nodes.append(node.name)
    
print("{}", json.dumps(fo_nodes))
    

""".format(prefijo_nodos_output)

escribir_data_archivo = """output_file = sys.argv[sys.argv.index("{0}") + 1]
    path = os.path.join("{1}", "{2}" + output_file + ".json")
    with open(path, "w", encoding="utf8") as archivo_escenas:
        archivo_escenas.write(json.dumps(data))
    """.format(handle_scenes_info_output, ruta_base_jobinfo, prefijo_archivo_scenes_info)

script_escenas_outputarchivo = "import sys\nimport os\n" + script_escenas.replace(
    'print("DATA: ", json.dumps(data))',
    escribir_data_archivo)
