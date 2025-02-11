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

import json
import os
from enum import IntEnum
from pathlib import PurePath

from PyQt5.QtCore import QObject, pyqtSignal

from datas import token_nombre_original, token_path_original, token_node_label, token_marker_camera, \
    token_regular_marker, token_start_time, ruta_archivo_presets_nombrado
from traducciones import traducir
from utils import set_cursor_espera

# constants
token_keys = ["A", "B", "C", "D", "E"]  # tokens comunes
split_keys = ["S", "T", "U", "V"]  # tokens split

tokens_nodos_script = [token_path_original, token_nombre_original,
                       token_node_label]
tokens_normales_script = [token_marker_camera, token_regular_marker]
# estos se mantienen como tokens en "aplicar" se aplican dentro de blender por script


tokens_momento_render = [token_start_time]
separadores = ["_", "-", ".", "+", "~", ""]


class AplicarA(IntEnum):
    Escena = 0
    Nodos = 1
    Todo = 2


aplicar_a_incluye_nodos = {AplicarA.Nodos, AplicarA.Todo}
aplicar_a_incluye_escena = {AplicarA.Escena, AplicarA.Todo}

default_aplicar_a = AplicarA.Todo


def patron_a_string(patron):
    return "".join(map(str, patron))


def actualizar_presets():
    presets[:] = [preset for preset in presets if not preset.eliminar]


def leer_archivo_presets():
    try:
        presets_leidos = []
        with open(ruta_archivo_presets_nombrado, "r", encoding="utf8") as archivo_presets:
            for preset in archivo_presets:
                presets_leidos.append(PresetNombrado.de_json(preset))
        return presets_leidos
    except (IOError, json.decoder.JSONDecodeError, TypeError) as e:
        print("Exception reading presets", e)  # debug print
        return []


def guardar_presets():
    try:
        with open(ruta_archivo_presets_nombrado, "w", encoding="utf8") as archivo_presets:
            for preset in presets:
                if preset.eliminar:
                    continue
                archivo_presets.write(json.dumps(preset.exportar()) + "\n")
    except IOError:
        pass


def agregar_custom_preset(preset_nuevo, default_para):
    if default_para:
        for preset in presets:
            if not preset.default_para:
                continue
            preset.default_para -= default_para
    presets.append(preset_nuevo)
    guardar_presets()


def actualizar_item_duplicado(item):
    if not item.patron_nombrado:
        return
    reaplicar = False
    for token_i in tokens_reaplicar_duplicar:
        patron = token_i.patron
        if patron in item.patron_nombrado["ruta"] or patron in item.patron_nombrado["nombre"]:
            reaplicar = True
            break
    if not reaplicar:
        return
    aplicar(item)


def aplicar(item):
    nombrado = item.patron_nombrado["ruta"] + item.patron_nombrado["nombre"]
    item.propiedades_argumentar.add("nombrado")

    def post_proceso(item_aviso):
        asimilar_info_y_reemplazar(item_aviso)

    if not obtener_info_si_falta(item, nombrado, post_proceso):
        reemplazo_tokens_item(item)


def previsualizar(item, patron):
    # if not isinstance(item, ItemCola):
    #     preview = os.path.join(patron_a_string(patron["ruta"]), patron_a_string(patron["nombre"]))
    #     emisor.output_preview_signal.emit(preview)
    #     return

    nombrado = patron["ruta"] + patron["nombre"]

    def post_proceso(item_aviso):
        asimilar_info_y_actualizar_preveiw(item_aviso, patron)

    if not obtener_info_si_falta(item, nombrado, post_proceso):
        reemplazo_tokens_preview(item, patron)


def obtener_info_si_falta(item, nombrado, post_proceso):
    if not hasattr(item, "asimilar_info_escena"):
        # item fantasma
        return False
    for token_prop_item in tokens_propiedad_item:
        if not nombrado.count(token_prop_item.patron):
            continue

        resultado = token_prop_item.resultado(item)

        if not resultado and token_prop_item.resultado_propiedad_item not in ("view_layer", "camara"):
            # si querés usar token de view layer o cámara tenés que usar la ventana correspondiente
            # no hay otra, porque si no igual el blend puede renderizar varios viewlayers, uno qué sabe.
            if item.escenas:
                item.asimilar_info_escena(preservar_argumentadas=True)
                return False

            set_cursor_espera()
            item.leer_escenas_item(post_proceso, pasar_parametro=True,
                                   cursor_espera=False)
            return True

    return False

    # def reemplazo_tokens_legacy(self, item):
    #     patron_ruta, patron_nombre = item.patron_nombrado["ruta"].rstrip("/\\"), item.patron_nombrado["nombre"]
    #     separador = item.patron_nombrado.get("separador", "")
    #
    #     tokens_preservados_nodos = set(tokens_nodos_script).union(set(tokens_normales_script))
    #
    #     re_tokens_regulares = '|'.join(re.escape(token.patron) for token in tokens_propiedad_item)
    #     re_tokens_incrementales = '|'.join(
    #         re.escape(token.patron) + re_keys_incrementales.format("", "") for token in tokens_incrementales)
    #     re_combinado = f'({re_tokens_regulares})|({re_tokens_incrementales})'
    #
    #     parametros_comunes = (re_combinado, tokens_preservados_nodos, separador, item)
    #     resultado_ruta, resultado_ruta_nodos = split_reemplazo_tokens(*parametros_comunes, patron_ruta)
    #     resultado_nombre, resultado_nombre_nodos = split_reemplazo_tokens(*parametros_comunes, patron_nombre)
    #
    #     item.nombrado = os.path.join(resultado_ruta, resultado_nombre)
    #     item.patron_nombrado["ruta_nodos"] = resultado_ruta_nodos
    #     item.patron_nombrado["nombre_nodos"] = resultado_nombre_nodos
    #     item.propiedades_argumentar.add("nombrado")
    #
    # def split_reemplazo_tokens(self, re_combinado, tokens_preservados_nodos, separador, item, patron):
    #
    #     partes = re.split(re_combinado, patron)
    #     partes = (parte for parte in partes if parte)
    #
    #     partes_procesadas = []
    #     partes_procesadas_nodos = []
    #
    #     hubo_previo = False
    #     hubo_previo_nodos = False
    #     for parte in partes:
    #         preservar_token_nodos = False
    #         match_incremental = next(
    #             (re.match(r'(' + re.escape(token.patron) + r')' + re_keys_incrementales.format("(", ")"), parte)
    #              for token in
    #              tokens_incrementales), None)
    #
    #         es_token = True
    #         if match_incremental:
    #             patron = match_incremental.group(1)
    #             key = match_incremental.group(2)
    #             token = TokenNombradoIncremental.token_por_patron(patron)
    #             resultado = token.resultado(item, key)
    #         elif any(parte == token.patron for token in tokens_propiedad_item):
    #             token = TokenNombrado.token_por_patron(parte)
    #             resultado = token.resultado(item)
    #             if token.resultado_propiedad_item == "nombre_blend":
    #                 resultado = str(PurePath(resultado).stem)
    #
    #             if not resultado or resultado == "*None*":
    #                 resultado = ""
    #
    #             if parte in tokens_preservados_nodos:
    #                 preservar_token_nodos = True
    #
    #         else:
    #             resultado = parte
    #             es_token = parte in tokens_preservados_nodos  # los tokens tokens_normales_script no son prop item ni incrementales
    #
    #         if hubo_previo and es_token:
    #             partes_procesadas.append(separador)
    #
    #         if hubo_previo_nodos and es_token:
    #             partes_procesadas_nodos.append(separador)
    #
    #         if resultado:
    #             partes_procesadas.append(resultado)
    #             hubo_previo = True
    #         else:
    #             hubo_previo = False
    #
    #         if resultado or preservar_token_nodos:
    #             partes_procesadas_nodos.append(parte if preservar_token_nodos else resultado)
    #             hubo_previo_nodos = True
    #         else:
    #             hubo_previo_nodos = False
    #
    #     return ''.join(partes_procesadas), ''.join(partes_procesadas_nodos)


def asimilar_info_y_reemplazar(item):
    asimilar_info(item)
    reemplazo_tokens_item(item)


def asimilar_info_y_actualizar_preveiw(item, patron):
    asimilar_info(item)
    reemplazo_tokens_preview(item, patron)


def asimilar_info(item):
    escenas = item.escenas
    escena = item.escena if item.escena else [*escenas.keys()][0]
    item.asimilar_info_escena(escenas[escena], preservar_argumentadas=True)
    # QApplication.restoreOverrideCursor()


def reemplazo_tokens_item(item):
    patron_completo, resultado_ruta_nodos, resultado_nombre_nodos = reemplazo_tokens_patron(item, item.patron_nombrado)
    item.nombrado = patron_completo
    item.patron_nombrado["ruta_nodos"] = resultado_ruta_nodos
    item.patron_nombrado["nombre_nodos"] = resultado_nombre_nodos


def reemplazo_tokens_preview(item, patron):
    patron_completo = reemplazo_tokens_patron(item, patron, preview=True)[0]
    emisor.output_preview_signal.emit(patron_completo)


def reemplazo_tokens_patron(item, patron, preview=False):
    tokens_preservados_nodos = set(tokens_nodos_script).union(set(tokens_normales_script))
    separador = patron.get("separador", "")
    parametros_comunes = (item, separador, tokens_preservados_nodos, preview)
    resultado_ruta, resultado_ruta_nodos = reemplazo_tokens_parte_patron(*parametros_comunes, patron=patron["ruta"])
    resultado_nombre, resultado_nombre_nodos = reemplazo_tokens_parte_patron(*parametros_comunes,
                                                                             patron=patron["nombre"])
    patron_completo = os.path.join(resultado_ruta.rstrip(separador), resultado_nombre)
    return patron_completo, resultado_ruta_nodos, resultado_nombre_nodos


def reemplazo_tokens_parte_patron(item, separador_patron, tokens_preservados_nodos, preview, patron):
    partes_procesadas = []
    partes_procesadas_nodos = []
    hubo_previo = False
    hubo_previo_nodos = False

    for parte in patron:
        preservar_token_nodos = False
        es_exclusivo_nodo = False
        if isinstance(parte, list):
            token_patron, key = parte
            token_patron = BaseTokenNombrado.token_por_patron(token_patron)
            if not token_patron:
                continue
            resultado = token_patron.resultado(item, key)
            es_token = True
        elif parte in (tokens_normales_script + tokens_momento_render):
            resultado = parte
            es_token = True
        else:
            token_patron = BaseTokenNombrado.token_por_patron(parte)
            if token_patron:
                resultado = token_patron.resultado(item)
                if token_patron in tokens_solo_nodos:
                    es_exclusivo_nodo = True
                elif token_patron.resultado_propiedad_item == "nombre_blend":
                    resultado = str(PurePath(resultado).stem)
                es_token = True
                if parte in tokens_preservados_nodos:
                    preservar_token_nodos = True
            else:
                resultado = parte
                es_token = False

        if not resultado or resultado == "*None*":
            resultado = ""

        es_exclusivo_nodo = es_exclusivo_nodo and not preview
        es_token_normal = es_token and not es_exclusivo_nodo
        if hubo_previo and es_token_normal and not anterior_fue_separador(partes_procesadas, separador_patron):
            partes_procesadas.append(separador_patron)

        if hubo_previo_nodos and es_token and not anterior_fue_separador(partes_procesadas_nodos, separador_patron):
            partes_procesadas_nodos.append(separador_patron)

        if resultado and not es_exclusivo_nodo:
            partes_procesadas.append(resultado)
            hubo_previo = True
        else:
            hubo_previo = False

        if resultado or preservar_token_nodos:
            partes_procesadas_nodos.append(parte if preservar_token_nodos else resultado)
            hubo_previo_nodos = True
        else:
            hubo_previo_nodos = False

    return ''.join(partes_procesadas), ''.join(partes_procesadas_nodos)


def anterior_fue_separador(partes_procesadas, separador):
    return partes_procesadas[-1].endswith(separador) or partes_procesadas[-1].endswith(os.sep)


def reemplazar_start_time(item, nombrado):
    return nombrado.replace(token_start_time, item.start_time())


class SignalsNombrado(QObject):
    output_preview_signal = pyqtSignal(str)


class BaseTokenNombrado:
    _token_por_patron = {}

    def __init__(self, nombre_visible, patron, tooltip, default_tooltip, direccion_resultado=None,
                 funcion_obtencion=None):
        self.nombre_visible = traducir(nombre_visible)
        self.patron = patron
        BaseTokenNombrado._token_por_patron[patron] = self
        self.tooltips = [tooltip] if tooltip else []
        self.tooltips.append(default_tooltip)
        self.direccion_resultado = direccion_resultado if direccion_resultado else lambda x: x
        self.funcion_obtencion = funcion_obtencion if funcion_obtencion else getattr

    @classmethod
    def token_por_patron(cls, patron):
        return cls._token_por_patron.get(patron, None)


class TokenNombrado(BaseTokenNombrado):
    default_tooltip = "tooltip_default_token_nombrado"

    def __init__(self, nombre_visible, patron, resultado_propiedad_item=None, funcion_valor=None,
                 direccion_resultado=None, funcion_obtencion=None, tooltip="", default_editable=None):
        super().__init__(nombre_visible, patron, tooltip, self.default_tooltip, direccion_resultado, funcion_obtencion)
        self.resultado_propiedad_item = resultado_propiedad_item
        self.funcion_valor = funcion_valor
        self.default_editable = default_editable

    def resultado(self, item):
        objeto_propiedad = self.direccion_resultado(item)
        return self.funcion_obtencion(objeto_propiedad, self.resultado_propiedad_item, None)


class TokenNombradoIncremental(BaseTokenNombrado):
    default_tooltip = "tooltip_default_token_nombrado_incremental"

    def __init__(self, nombre_visible, patron, direccion_resultado, funcion_obtencion, keys, tooltip="",
                 keys_alternativas=None):
        super().__init__(nombre_visible, patron, tooltip, self.default_tooltip, direccion_resultado, funcion_obtencion)
        self.keys = keys
        self.keys_alternativas = keys_alternativas

    def resultado(self, item, key):
        objeto_propiedad = self.direccion_resultado(item)
        return self.funcion_obtencion(objeto_propiedad, key, "")


class TokenSoloNodos(BaseTokenNombrado):
    default_tooltip = "tooltip_default_token_nombrado"

    def __init__(self, nombre_visible, patron, tooltip=""):
        super().__init__(nombre_visible, patron, tooltip, self.default_tooltip)
        self.resultado_propiedad_item = None

    def resultado(self, _):
        return self.patron


class PresetNombrado:
    def __init__(self, ruta, nombre, separador, nombre_visible, aplicar_a=None, default_para=None):
        self.ruta = ruta
        self.nombre = nombre
        self.aplicar_a = aplicar_a if aplicar_a is not None else default_aplicar_a
        self.nombre_visible = nombre_visible
        self.separador = separador
        self.eliminar = False
        if isinstance(default_para, str):
            default_para = {default_para}
        self.default_para = default_para or set()

    def exportar(self):
        export = vars(self).copy()
        export["default_para"] = list(self.default_para)
        del export["eliminar"]
        return export

    @staticmethod
    def de_json(json_str):
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            data = {}

        params = {
            "ruta": "",
            "nombre": "",
            "separador": "",
            "nombre_visible": "",
            "aplicar_a": "",
            "default_para": []
        }
        params.update(data)
        return PresetNombrado(params["ruta"], params["nombre"], params["separador"], params["nombre_visible"],
                              params["aplicar_a"], set(params["default_para"]))

    @property
    def patron(self):
        return {"aplicar_a": self.aplicar_a, "ruta": self.ruta, "nombre": self.nombre,
                "ruta_nodos": self.ruta, "nombre_nodos": self.nombre, "separador": self.separador}


# definiciones tokens
tokens = dict()
tokens["camara"] = TokenNombrado("Cámara", "[CAMERA_NAME]",
                                 resultado_propiedad_item="camara", tooltip="warning_token_camaras")
tokens["marker_camera"] = TokenNombrado("Camera Marker",
                                        token_marker_camera)
tokens["regular_marker"] = TokenNombrado("Regular Marker",
                                         token_regular_marker)
tokens["view_layer"] = TokenNombrado("Viewlayer", "[VIEWLAYER_NAME]",
                                     resultado_propiedad_item="view_layer")
tokens["scene"] = TokenNombrado("Escena", "[SCENE_NAME]",
                                resultado_propiedad_item="escena")
tokens["nombre_blend"] = TokenNombrado("Nombre del blend", "[BLEND_NAME]",
                                       resultado_propiedad_item="nombre_blend")
tokens["ruta_blend"] = TokenNombrado("Ruta del blend", "[BLEND_PATH]",
                                     resultado_propiedad_item="ruta_blend")
tokens["path_original"] = TokenNombrado("Ruta de salida original",
                                        token_path_original,
                                        resultado_propiedad_item="ruta_output")
tokens["nombre_original"] = TokenNombrado("Nombre de salida original",
                                          token_nombre_original,
                                          resultado_propiedad_item="nombre_output")
tokens["frame_number"] = TokenNombrado("Número de frame",
                                       "#", default_editable="####")
tokens["version_blender"] = TokenNombrado("Version de blender",
                                          "[BLENDER_VERSION]", resultado_propiedad_item="tag_blender")
tokens["job_index"] = TokenNombrado("Job index",
                                    "[JOB_INDEX]", resultado_propiedad_item="job_index")
tokens["node_label"] = TokenSoloNodos("Node Label",
                                      token_node_label)

tokens["start_time"] = TokenNombrado("Start time",
                                     token_start_time)

funcion_obtencion_collection = lambda x, y, z: (x or {}).get(y, z)
direccion = lambda x: (getattr(x, "colecciones", None) or {}).get("collection_tokens")
tokens["collection"] = TokenNombradoIncremental("Collection", "[COLLECTION]",
                                                tooltip="tooltip_collection_token",
                                                direccion_resultado=direccion,
                                                funcion_obtencion=funcion_obtencion_collection,
                                                keys=token_keys,
                                                keys_alternativas=split_keys)

# definiciones preseets nombrado
presets = leer_archivo_presets()
if not presets:
    presets = [
        PresetNombrado(
            [tokens["path_original"].patron],
            [tokens["nombre_original"].patron, tokens["camara"].patron],
            "_",
            traducir("Original + camara"),
            default_para="camaras"
        ),
        PresetNombrado(
            [tokens["path_original"].patron],
            [tokens["nombre_original"].patron, tokens["view_layer"].patron],
            "_",
            traducir("Original + viewlayer"),
            default_para="view_layers"
        ),
        PresetNombrado(
            [tokens["ruta_blend"].patron, os.sep, "render"],
            [tokens["nombre_blend"].patron],
            "_",
            "Blend path/render/\nBlend name"
        ),
        PresetNombrado(
            [tokens["path_original"].patron],
            [tokens["nombre_original"].patron, tokens["job_index"].patron],
            "_",
            traducir("Original + job index")
        )
    ]

tokens_propiedad_item = []
tokens_incrementales = [tokens["collection"]]
tokens_solo_nodos = []
for token in tokens.values():
    if getattr(token, "resultado_propiedad_item", None):
        tokens_propiedad_item.append(token)
        continue
    if isinstance(token, TokenSoloNodos):
        tokens_solo_nodos.append(token)

tokens_reaplicar_duplicar = [tokens["job_index"]]

emisor = SignalsNombrado()
