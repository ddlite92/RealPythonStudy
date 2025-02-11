import os
from pathlib import Path
from blender_asset_tracer import blendfile
from blender_asset_tracer.blendfile import iterators
import blend_render_info

OB_CAMERA = 11


def get_name(id_datablock):
    if not id_datablock:
        return ""
    return id_datablock.id_name[2:].decode('utf-8')


def get_collection_objects(collection):
    collection_objects = collection.get_pointer((b'gobject', b'first'), None)

    all_objects = set()

    if collection_objects is not None:
        for collection_obj in iterators.listbase(collection_objects):
            obj = collection_obj.get_pointer(b"ob", None)
            if obj:
                all_objects.add(obj)

    collection_children = collection.get_pointer((b'children', b'first'), None)
    if collection_children is not None:
        for collection_child in iterators.listbase(collection_children):
            collection = collection_child.get_pointer(b"collection", None)
            if collection:
                all_objects.update(get_collection_objects(collection))
    return all_objects


def get_scene_cameras(scene):

    collection = scene.get_pointer(b'master_collection', None)

    if collection is None:
        return []

    scene_objects = get_collection_objects(collection)
    return [get_name(obj) for obj in scene_objects if obj.get(b'type', None) == OB_CAMERA]


def get_view_layers(scene):
    view_layers = []
    view_layers_list = scene.get_pointer((b'view_layers', b'first'), None)

    if view_layers_list is not None:
        for view_layer in iterators.listbase(view_layers_list):
            layer_name = view_layer.get(b'name', "").decode() or ""
            if layer_name:
                view_layers.append(layer_name)

    return view_layers


def get_scene_frame_info(scene):
    output_path = scene.get((b'r', b'pic'), "").decode('utf-8') or ""
    start_frame = scene.get((b'r', b'sfra'), 0)
    end_frame = scene.get((b'r', b'efra'), 0)
    frame_step = scene.get((b'r', b'frame_step'), 1)
    return output_path, start_frame, end_frame, frame_step


def get_active_scene(blend):
    wm_blocks = blend.find_blocks_from_code(b'WM')
    wm_block = wm_blocks[0] if wm_blocks else None
    if wm_block:
        windows = wm_block.get_pointer((b'windows', b'first'), None)
        if windows:
            for window in iterators.listbase(windows):
                active_scene_ptr = window.get_pointer(b'scene', None)
                if active_scene_ptr:
                    return active_scene_ptr
    return None


def get_absolute_path(blend_directory, output_path):
    """Constructs an absolute path based on the blend directory and output path."""
    if output_path.startswith("//"):
        # Remove "//" to make it relative to the blend directory
        output_path = output_path[2:]
    return (blend_directory / output_path).resolve(strict=False)


def enderezar_ruta_output(ruta_blend, output_path):
    """Converts the output path to an absolute path based on the blend file's directory."""
    blend_directory = ruta_blend.parent  # Using pathlib to get the directory

    # Treat paths starting with "//" as relative, otherwise check if truly absolute
    if output_path.startswith("//") or not Path(output_path).is_absolute():
        # Construct the absolute path using the blend directory
        absolute_output_path = get_absolute_path(blend_directory, output_path)
    else:
        # If it's a truly absolute path, use it directly
        absolute_output_path = Path(output_path)

    return absolute_output_path


def obtener_data_escenas(file):
    print("Reading scene data", )  # debug print
    file = Path(file)
    with blendfile.open_cached(file) as blend:
        try:
            header = blend.header  # Access the header block
            version = header.version  # This gives the Blender version (e.g., 290 for Blender 2.90)
            version_str = f"{version // 100}.{version % 100}"  # Major.Minor version
            print(f"Blender version: {version_str}")
        except AttributeError as e:
            print("Error accessing version info:", e)
            version_str = ""

        active_scene_ptr = get_active_scene(blend)

        scenes = blend.find_blocks_from_code(b'SC')
        datas_escenas = []
        for scene in scenes:
            scene_name = get_name(scene)

            is_active = scene == active_scene_ptr

            output_path, start_frame, end_frame, frame_step = get_scene_frame_info(scene)

            cameras = get_scene_cameras(scene)
        
            active_camera = get_name(scene.get_pointer(b'camera', ""))

            view_layers = get_view_layers(scene)

            ruta = enderezar_ruta_output(file, output_path)

            data = {
                "nombre_Escena": scene_name,
                "inicio": str(start_frame),
                "fin": str(end_frame),
                "step": str(frame_step),
                "ruta_completa": ruta,
                "view_layers": view_layers,
                "camara": active_camera,
                "camaras": cameras
            }

            if is_active:
                datas_escenas.insert(0, data)
            else:
                datas_escenas.append(data)

    return datas_escenas, version_str


def obtencion_info_header(ruta):
    try:
        data_escenas, version = blend_render_info.read_blend_rend_chunk(ruta)
    except Exception as e:
        print("Exception reading header",) # debug print
        data_escenas, version = None, None
    return (data_escenas, version) if data_escenas and version else (None, None)



