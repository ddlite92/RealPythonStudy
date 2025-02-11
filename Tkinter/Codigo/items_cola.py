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

import copy
import json
import os
import re
from enum import IntEnum, auto
from inspect import signature

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QProgressBar

import alertas
import app_context
import autonombrado
from obtencion_info_blend import obtener_data_escenas, obtencion_info_header

from configuracion_general import configuracion
from consola import ConsolaRender
import utilidades_tiempo
import traducciones as traduccion
from traducciones import traducir
import iconos_app as iconos
from utils import encoder_json_items, restore_cursor, set_cursor_espera
import datas
import blenders
import management_modos

versiones_blender = blenders.versiones_blender

modos = management_modos.modos


# propiedades_expuestas = ["ruta_blend", "nombre_blend", "loQue", "estado", "escena", "view_layer",
#                              "camara", "tag_blender",
#                              "nombrado", "inicio", "fin", "step", "args_extra", "nombres_dispositivos"]

class ColumnaProp(IntEnum):
    ruta_blend = 0
    nombre_blend = auto()
    loQue = auto()
    frames_display = auto()
    estado = auto()
    escena = auto()
    view_layer = auto()
    camara = auto()
    tag_blender = auto()
    nombrado = auto()
    args_extra = auto()
    nombres_dispositivos = auto()


propiedades_expuestas = list(ColumnaProp.__members__.keys())


class ItemCola(QtWidgets.QTreeWidgetItem):
    columna = {}
    for i, el in enumerate(propiedades_expuestas):
        columna[el] = i
    columnas = len(columna)

    variables_exportables = ["ruta_blend", "nombre_blend", "tag_blender", "modo", "escena", "view_layer", "camara",
                             "inicio",
                             "fin", "step", "args_extra",
                             "nombres_dispositivos", "frames", "script", "estado", "renderizados",
                             "tipo_dispositivos", "dispositivos", "ruta_output", "nombre_output",
                             "ruta_frame_output", "es_video",
                             "propiedades_argumentar",
                             "patron_nombrado", "tag_blend", "nombrado", "view_layers", "manejar_compositing",
                             "camaras", "desactivado", "parallel_gpu", "last_log_start", "last_log_end",
                             "porcentaje_progreso", "colecciones", "id_start_time", "id", "bg_color"]

    mutables_a_independizar = ("propiedades_argumentar", "colecciones",
                               "patron_nombrado")  # a escenas y eso dejo que sigan vinculás
    resetear_al_duplicar = ("estado", "porcentaje_progreso", "id", "renderizados")
    default_patron_nombrado = {'aplicar_a': 2, 'ruta': '', 'nombre': '', 'ruta_nodos': '', 'nombre_nodos': '',
                               'separador': "_"}

    datos_frames_animacion = ["inicio", "fin", "step"]

    # en a_json se
    # agregan las que necesitan tratamiento extra como "render"
    # no incluyo escenas de momento porque es medio brete
    # y pueden haber cambiado en el blend entre sesiones, si incluyo la escena de cada item que de
    # última lleva al default técnico

    ids = {}

    def __init__(self, ventana, arbol=None):

        super().__init__(arbol)

        self.ventana = ventana

        self.settings_ventana = ventana.settings_ventana

        self.ruta_blend = ""
        self.nombre_blend = ""
        self.tag_blender = blenders.tag_default
        self.view_layer = ""
        self.camara = ""
        self.modo = ""
        self.inicio = ""
        self.fin = ""
        self.step = ""
        self.args_extra = ""
        self.nombres_dispositivos = ""
        self.frames = ""
        self.script = ""
        self.estado = "no_comenzado"
        self.renderizados = 0
        self.escenas = {}
        self.escena = ""
        self.colecciones = None
        self.view_layers = []
        self.manejar_compositing = ""
        self.camaras = []
        self.tipo_dispositivos = ""
        self.dispositivos = []
        self.parallel_gpu = False
        self.ruta_output = ""
        self.nombre_output = ""
        self.ruta_frame_output = ""
        self.es_video = False
        self.patron_nombrado = self.default_patron_nombrado
        self.nombrado = None
        self.propiedades_argumentar = set()
        self.tag_blend = None
        self.desactivado = False
        self.last_log_start = None
        self.last_log_end = None
        self.porcentaje_progreso = 0
        self.id_start_time = None
        self.id = None
        self.bg_color = None
        self.tooltips_columnas = {}  # no está en uso actualmente

        self.render = None
        self.infoblendo = None
        self.preparando = False
        # en vez de guardar preparando como un estado más lo guardo como un flag aparte para no perder dato de detenidos en ocasiones
        self.procesado = False
        self.frames_renderizar_parcial = 0
        self.frames_renderizar_total = 0
        self.recabando_info = False

        self.item_estado = None
        self.frame_reportado = str(self.renderizados) if self.renderizados else ""

        self._start_time = []

        self.timer_actualizacion_eta = QTimer()
        self.timer_actualizacion_eta.setInterval(1000)
        self.timer_actualizacion_eta.setSingleShot(True)
        self.timer_actualizacion_eta.timeout.connect(self.actualizar_columna_eta)

        self.asegurar_id_unico()

        self.consola = ConsolaRender(self)

        self.version_blender = None
        self.mismatch_version = False

        if self.tag_blend:
            self.setText(self.columna["nombre_blend"], self.tag_blend)

        self.setFlags(self.flags() & ~Qt.ItemIsDropEnabled)

        alineamientos = {"izquierda": Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                         "centro": Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter,
                         "derecha": Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight}

        for col in self.columna:
            for alineamiento in alineamientos:
                if col in self.settings_ventana.alineamiento_columnas[alineamiento]:
                    self.setTextAlignment(self.columna[col], alineamientos[alineamiento])
                    break

    def doble_click(self, columna):
        self.quitar_warning(columna)

    def quitar_warning(self, columna):
        self.setIcon(columna, QIcon())
        self.setToolTip(columna, self.tooltips_columnas.get(columna, ""))

    def agregar_warning(self, columna, tooltip):
        self.setIcon(columna, iconos.icono_warning)
        tooltip += f"\n{traducir('tooltip_double_click_dismiss')}"
        self.setToolTip(columna, tooltip)

    def tooltip_mismatch(self):
        tooltip = traducir("tooltip_version_mismatch")
        tooltip += f"\n{traducir('Assigned')}: {self.version_blender_asignada()}"
        tooltip += f"\n{traducir('Saved with')}: {self.version_blender}"

        return tooltip

    def agregar(self):
        self.ventana.tablaPrincipal.addTopLevelItem(self)

    def set_valores(self, **kwargs):
        for attr, value in kwargs.items():
            if hasattr(self, attr):
                setattr(self, attr, value)
            else:
                print("Invalid attribute", attr, value)

    def lectura_datos_header(self):
        data_escena, version = obtencion_info_header(self.ruta_blend_completa)
        if not (isinstance(data_escena, list) and len(data_escena) > 0):
            return
        try:
            inicio, fin, escena = data_escena[0]
            if self.inicio is None:
                self.inicio = inicio
            if self.fin is None:
                self.fin = fin
            if self.escena is None:
                self.escena = escena
        except (IndexError, KeyError):
            pass
        self.version_blender = version

    def coinciden_versiones_blender(
            self):  # esto se llama así porque originalmente se iba a procesar el resultado para largar una alerta y cosas, pero si no hacemos eso debería de renombrarle
        version_asignada = self.version_blender_asignada()
        if not (self.version_blender and version_asignada):
            return True
        for char_guardada, char_asiganda in zip(self.version_blender, version_asignada):
            if char_guardada != char_asiganda:
                self.mismatch_version = True
                return False
        self.mismatch_version = False
        return True

    def version_blender_asignada(self):
        return versiones_blender.blenders.get(self.tag_blender, {}).get(blenders.ParamsBlender.VERSION, {})

    def asegurar_id_unico(self):
        # Casos posibles: que el objeto ya venga con id: porque está siendo leído de un json o duplicado.
        # En ese caso el objeto conserva el id, y si el nombre ya está en el tracker de ids de colas,
        # se asegura de actualizarlo si es necesario (si el id de este es mayor que el que había).
        # Puede no pasar por ejemplo si se eliminó otra instancia de ese archivo (u otro con el mismo nombre) de la cola.
        # Que no venga con id: se genera uno aumentando el valor del tracker o asignandole uno e iniciando el tracker
        # para ese nombre

        # estos ids son únicos por nombre de archivo, por archivo mostrado en cola en la sesión, aunque pertenezca a
        # otra cola que cambió. Bastaría con que sean únicos por nombre y por cola nombrada, porque se guardan en
        # carpetas diferentes, pero no perdemos nada haciendolos únicos así y es más sencillo.

        nombre_sin_extension = os.path.splitext(self.nombre_blend)[0]
        id_max = self.ids.get(nombre_sin_extension)

        if id_max is not None:
            if self.id:
                self.ids[nombre_sin_extension] = max(id_max, int(self.id))
                return
            self.ids[nombre_sin_extension] += 1
            self.id = str(id_max + 1)
        else:
            self.ids[nombre_sin_extension] = 1
            self.id = self.id or "1"

    def update_id_start_time(self):
        self.id_start_time = id(self._start_time)

    def clear_start_time(self):
        self._start_time.clear()

    def link_start_time(self, item):
        self._start_time = item.start_time_reference()
        self.id_start_time = item.id_start_time

    def start_time_reference(self):
        return self._start_time

    def start_time(self):
        if not len(self._start_time):
            self._start_time.append(utilidades_tiempo.fecha_hora_sanitizados())
        return self._start_time[0]

    @property
    def job_index(self):
        return str(self.treeWidget().indexOfTopLevelItem(self))

    @property
    def ruta_blend_completa(self):
        return os.path.join(self.ruta_blend, self.nombre_blend)

    def existe(self):
        return os.path.isfile(self.ruta_blend_completa)

    def actualizar_columna_eta(self):
        if self.estado != "renderizando":
            self.timer_actualizacion_eta.stop()
            return
        try:
            self.item_estado.setText(ItemEstado.columna["eta"],
                                     self.render.estimado_restante())
            if self == self.ventana.manejo_statusbar.item_reportante:
                self.ventana.manejo_statusbar.actualizar_estimado_restante(self)
            self.timer_actualizacion_eta.start()
        except Exception as e:
            pass

    def actualizar_status_lista(self, estado="", desactivado=None):
        # normalmente estado y desactivado se deducen pero para el caso preparing se pasan
        if not getattr(self, "item_estado", None):
            return
        try:
            renderizados = self.render.data.renderizados
            if not renderizados:
                renderizados = self.render.data.renderizados_alternativo

            valor = int(100 * renderizados / self.frames_renderizar_parcial)
            valor = min(valor, 100)
        except (AttributeError, ZeroDivisionError) as e:
            valor = None
        desactivado = desactivado if desactivado is not None else self.desactivado

        estado = estado if estado else self.estado

        if estado == "terminado":
            self.porcentaje_progreso = 100
        elif valor is not None:
            self.porcentaje_progreso = valor

        self.item_estado.actualizar(estado, desactivado, self.porcentaje_progreso, self.frame_reportado,
                                    faltante=not self.existe())

    def render_completo(self):  # parece que esto no se usa?
        if self.frames_renderizar_parcial > 0 and self.renderizados >= int(self.frames_renderizar_parcial * 0.8):
            return True
        if not self.frames_renderizar_parcial and self.renderizados:
            return True
        try:
            if self.render.data.ultimo_frame_guardado == self.fin:
                return True
        except AttributeError:
            pass

        return False

    def recalcular_num_frames_renderizar_animacion(self):
        if (not self.fin) or (not self.inicio):
            return
        if not self.step:
            self.step = "1"
        self.frames_renderizar_parcial = 1 + (int(self.fin) - int(self.inicio) - self.renderizados) // int(self.step)
        self.frames_renderizar_total = 1 + (int(self.fin) - int(self.inicio)) // int(self.step)

    def recalcular_num_frames_renderizar_frames(self):
        if ".." in self.frames:
            inicio, fin = [int(i) for i in self.frames.split("..")]
            self.frames_renderizar_total = fin - inicio + 1
            self.frames_renderizar_parcial = self.frames_renderizar_total - self.renderizados
            return
        lista_frames = [int(i) for i in self.frames.split(",")]
        self.frames_renderizar_total = len(lista_frames)
        self.frames_renderizar_parcial = self.frames_renderizar_total - self.renderizados

    def a_json(self):
        exportables = {k: self.__dict__[k] for k in self.variables_exportables}
        try:
            exportables["render"] = self.render.datos_finales()
        except AttributeError:
            pass

        if self.tag_blender != "Default":
            try:
                exportables["ruta_blender"] = versiones_blender.ruta(self.tag_blender)
            except KeyError:
                pass
        return json.dumps(exportables, default=encoder_json_items)

    def duplicar(self):
        item_duplicado = ItemCola(self.ventana, self.treeWidget())
        for nombre_atributo, valor in self.__dict__.items():
            if nombre_atributo in ItemCola.resetear_al_duplicar:
                continue
            if nombre_atributo in ItemCola.mutables_a_independizar:
                valor = copy.deepcopy(valor)
            setattr(item_duplicado, nombre_atributo, valor)
        autonombrado.actualizar_item_duplicado(item_duplicado)
        return item_duplicado

    def duplicar_en_sitio(self):
        duplicado = self.duplicar()
        index_actual = self.treeWidget().indexOfTopLevelItem(self)
        index_duplicado = self.treeWidget().indexOfTopLevelItem(duplicado)
        self.treeWidget().takeTopLevelItem(index_duplicado)
        self.treeWidget().insertTopLevelItem(index_actual + 1, duplicado)
        self.ventana.actualizar_lista_estado()
        return duplicado

    @staticmethod
    def leer_escenas_archivo(archivo):
        data = InfosEscenaBlend.obtener_infos_escenas(archivo)
        if data:
            for escena in data["data_escenas"].values():
                print("Scene:", escena)  # debug print1
            print("\n", )  # debug print
            # restore_cursor()
            return data
        return {}

    def leer_escenas_item_manual(self, avisar=None, pasar_parametro=False, cursor_espera=True):
        info_escenas = InfoEscenasManual(item=self, avisar=avisar, pasar_parametro=pasar_parametro,
                                         cursor_espera=cursor_espera)
        info_escenas.averiguar()

    def leer_info_escena_manual(self, avisar=None, preservar_propiedades_argumentadas=False):
        # script para leer camaras, viewlayers, escenas, y output path del blend
        infos_blender = InfosEscenaManual([self], avisar)
        infos_blender.preservar_propiedades_argumentadas = preservar_propiedades_argumentadas
        return infos_blender.averiguar()

    def leer_escenas_item(self, avisar, pasar_parametro=True, cursor_espera=True, fallback_manual=True, asimilar=False,
                          dato_infaltable=None):
        self.recabando_info = True

        def verificar(x): self.verificar_encontro_escenas(x, avisar=avisar, pasar_parametro=pasar_parametro,
                                                          cursor_espera=cursor_espera, fallback_manual=fallback_manual,
                                                          asimilar=asimilar, dato_infaltable=dato_infaltable)

        self.ventana.leer_escenas_archivo_asinc(self.ruta_blend_completa, avisar=verificar,
                                                cursor_espera=cursor_espera)

    def verificar_encontro_escenas(self, data, avisar, pasar_parametro, cursor_espera, fallback_manual=True,
                                   asimilar=False, dato_infaltable=None):
        self.recabando_info = False
        restore_cursor()
        escenas = data.get("data_escenas", [])
        version = data.get("version_blender", "")
        self.version_blender = version or self.version_blender
        self.coinciden_versiones_blender()
        if escenas:
            self.escenas = escenas
            if asimilar:
                if not (self.escena and self.escena in escenas):
                    self.escena = next(iter(escenas))
                self.asimilar_info_escena(escenas[self.escena])

            if fallback_manual and dato_infaltable and not self.__getattribute__(dato_infaltable):
                self.leer_escenas_item_manual(avisar, pasar_parametro=pasar_parametro, cursor_espera=cursor_espera)
                return

            parametros_aceptados = signature(avisar).parameters
            parametros_pasar = {}
            if "escenas" in parametros_aceptados:
                parametros_pasar["escenas"] = escenas
            if "item_aviso" in parametros_aceptados:
                parametros_pasar["item_aviso"] = self

            if avisar:
                avisar(**parametros_pasar)
        elif fallback_manual:
            self.leer_escenas_item_manual(avisar, pasar_parametro=pasar_parametro, cursor_espera=cursor_espera)

    def asimilar_info_escena(self, data_escena=None, preservar_argumentadas=False, omitir_escena=False):
        if not self:  # porque si cierra b-renderon durante preparing se va a llamar asimilar_info pero por ahí ya no
            # hay item y es un crash durante el cierre que mejor evitar nocierto
            return
        if not data_escena:
            if not self.escenas:
                return
            data_escena = self.escenas[self.escena] if self.escena and self.escena in self.escenas else self.escenas[
                next(iter(self.escenas))]

        for nombre_propiedad, valor in vars(data_escena).items():
            if omitir_escena and nombre_propiedad == "escena":
                continue
            if nombre_propiedad == "ruta_completa":
                self.desglosar_path_salida(valor)
                continue
            if preservar_argumentadas and getattr(self,
                                                  nombre_propiedad) and nombre_propiedad in self.propiedades_argumentar:
                continue
            
            if nombre_propiedad == "camara":
                if valor == "**Missing**" or not valor:
                    alertas.alerta_generica("alerta_camara", "Scene: " + data_escena.escena)
                    self.camara = ""
                    self.agregar_warning(ColumnaProp.camara, traducir("warning_falta_camara"))
                    continue
            setattr(self, nombre_propiedad, valor)

        self.recabando_info = False

    def buscar_frame_path(self):
        self.infoblendo = InfosBlender(retorno_info=self.extraer_asimilar_frame_path)
        self.infoblendo.correr_blender([self.ruta_blend_completa, "-b", "--factory-startup", "--python-expr",
                                        datas.expresion_obtener_frame_path()])

    def extraer_asimilar_frame_path(self, data):
        path = re.search(datas.handle_frame_path + "\((.*)\)", str(data), re.M)
        try:
            self.ruta_frame_output = path.group(1)
        except Exception as e:
            print(e)
            pass

    def desglosar_path_salida(self, path):
        path = os.path.split(path)
        self.ruta_output = path[0] if path[0] else "*None*"
        self.nombre_output = path[1] if path[1] else "*None*"

    def reset(self):
        self.estado = "no_comenzado"
        self.renderizados = 0
        self.frame_reportado = ""
        self.procesado = False
        self.desactivado = False
        self.porcentaje_progreso = 0
        self.item_estado.actualizar(self.estado, self.desactivado, self.porcentaje_progreso, self.renderizados)

    def set_bg_color(self, color):
        for column in self.columna.values():
            self.setBackground(column, color)

    def __setattr__(self, dato, valor):
        if dato in propiedades_expuestas:
            if dato == "tag_blender":
                self.update_tag(valor)
            else:
                self.setText(self.columna[dato], valor)

        if dato == "bg_color" and valor is not None:
            color = QtGui.QColor(valor) if valor else QtGui.QBrush()
            self.set_bg_color(color)

        if dato == "modo":
            texto = traducir(valor)
            self.setText(ColumnaProp.loQue, texto)

        if dato == "frames" and modos.modo[self.modo].tipo == "frames":
            self.setText(ColumnaProp.frames_display, valor)

        if dato == "tipo_dispositivos":
            if valor == "Eevee":
                self.setText(self.columna["tag_blender"], versiones_blender.tag_eevee)
            else:
                self.update_tag(self.tag_blender)  # esto es para cuando deja de elegir un disp eevee

        if dato == "mismatch_version":
            if valor:
                self.agregar_warning(ColumnaProp.tag_blender, self.tooltip_mismatch())
            else:
                self.quitar_warning(ColumnaProp.tag_blender)

        estado_temporal = ""
        if dato == "estado":
            self.preparando = False
            icono = iconos.estados[valor]
            self.setIcon(self.columna["estado"], icono)
            estado_temporal = valor
            texto_estado_tablaprincipal = traduccion.estados(valor)
            if valor in ["interrumpido", "terminado"]:
                texto_estado_tablaprincipal += " (" + traducir(
                    ["frames renderizados", "frame renderizado"][self.renderizados == 1]) + ": " + str(
                    self.renderizados) + ")"
                self.frame_reportado = str(self.renderizados)
            else:
                self.frame_reportado = ""
            self.setText(self.columna["estado"], texto_estado_tablaprincipal)

        if dato == "preparando" and valor:
            estado_temporal = "preparando"
            icono = iconos.estados[estado_temporal]
            self.setIcon(self.columna["estado"], icono)
            texto_estado = traduccion.estados(estado_temporal)
            self.setText(self.columna["estado"], texto_estado)

        desactivado = False
        if dato == "desactivado":
            if self.treeWidget() and not self.existe():
                valor = True
            self.actualizar_color_estado(valor)

            if valor:
                estado_temporal = self.estado
                desactivado = True
                icono = iconos.estados["desactivado"]
                self.setIcon(self.columna["estado"], icono)
                texto_estado = traduccion.estados("desactivado") if self.existe() else traduccion.estados("faltante")
                texto_estado.capitalize()
                self.setText(self.columna["estado"], texto_estado)
                self.setSelected(False)
                self.frame_reportado = ""
            else:
                self.frame_reportado = str(self.renderizados)
                self.__setattr__("estado", self.estado)

        if estado_temporal:
            self.actualizar_status_lista(estado=estado_temporal, desactivado=desactivado)

        super().__setattr__(dato, valor)

        if dato in self.datos_frames_animacion and modos.modo[self.modo].tipo == "animacion":
            texto_frames = ""
            for atributo in self.datos_frames_animacion:
                valor_atributo = getattr(self, atributo, "")
                if atributo == "step" and valor == "1":
                    continue
                if valor_atributo:
                    atributo_traducido = traducir(atributo.capitalize() + ":")
                    texto_frames += f"{atributo_traducido} {valor_atributo}  "
            self.setText(ColumnaProp.frames_display, texto_frames)

    def update_tag(self, tag):
        tag_mostrado = versiones_blender.tag_mostrado(tag)
        self.setText(self.columna["tag_blender"], tag_mostrado)

    def actualizar_color_estado(self, desactivado):
        for i, _ in enumerate(self.columna):
            self.setForeground(i, self.brush(desactivado))

    @staticmethod
    def brush(desactivado=False):
        configuracion.skin_actual()
        color = configuracion.skin_actual()["Disabled"][str(QtGui.QPalette.Text)]["color"]
        brushes = [QtGui.QBrush(), QtGui.QBrush(QtGui.QColor(color))]
        return brushes[desactivado]

    @classmethod
    def de_json(cls, datos_json):
        try:
            datos = json.loads(datos_json)
        except json.decoder.JSONDecodeError:
            return
        ruta_bl_alt = ""

        filtros_datos = {"propiedades_argumentar": lambda d: set(d),
                         "render": lambda d: DatosFinalesRender(*d.values()),
                         "patron_nombrado": lambda d: {"aplicar_a": 2, "ruta": d[0], "nombre": d[1], "ruta_nodos": d[0],
                                                       "nombre_nodos": d[1]} if isinstance(d, list) else d}

        item = cls(app_context.ventana_principal)
        for nombre_dato, dato in datos.items():
            if nombre_dato in filtros_datos:
                datos[nombre_dato] = filtros_datos[nombre_dato](dato)
            if not hasattr(item, nombre_dato):
                if nombre_dato == "ruta_blender":
                    ruta_bl_alt = datos[nombre_dato]
                continue
            setattr(item, nombre_dato, datos[nombre_dato])
        if ruta_bl_alt:
            try:
                versiones_blender.actualizar(datos["tag_blender"], ruta_bl_alt)
            except TypeError as e:
                print("e", e)  # debug print
        return item


class ItemFantasma:
    def __init__(self, ruta_blend="",
                 nombre_blend="",
                 tag_blender="Default",
                 escena="",
                 view_layer="",
                 camara="",
                 inicio="",
                 fin="",
                 args_extra="",
                 nombres_dispositivos="",
                 modo="",
                 frames="",
                 script="",
                 estado="no_comenzado",
                 renderizados=0,
                 escenas=None,
                 view_layers=None,
                 camaras=None,
                 tipo_dispositivos="",
                 dispositivos=None,
                 ruta_output="",
                 nombre_output="",
                 patron_nombrado=None,
                 nombrado=None,
                 propiedades_argumentar=None,
                 tag_blend=None
                 ):
        self.ruta_blend = ruta_blend
        self.nombre_blend = nombre_blend
        self.tag_blender = tag_blender
        self.escena = escena
        self.view_layer = view_layer
        self.camara = camara
        self.inicio = inicio
        self.fin = fin
        self.args_extra = args_extra
        self.nombres_dispositivos = nombres_dispositivos
        self.modo = modo
        self.frames = frames
        self.script = script
        self.estado = estado
        self.renderizados = renderizados
        self.escenas = escenas
        self.view_layers = view_layers
        self.camaras = camaras
        self.tipo_dispositivos = tipo_dispositivos
        self.dispositivos = dispositivos
        self.ruta_output = ruta_output
        self.nombre_output = nombre_output
        self.patron_nombrado = patron_nombrado if patron_nombrado else ItemCola.default_patron_nombrado
        self.nombrado = nombrado
        self.propiedades_argumentar = propiedades_argumentar if propiedades_argumentar else set()
        self.tag_blend = tag_blend


class DatosFinalesRender:
    def __init__(self, promedio_final, tiempo_total, error_final="", gpus="", promedio_final_segundos=None):
        self.promedio_final = promedio_final
        self.tiempo_total = tiempo_total
        self.error_final = error_final
        self.gpus = gpus
        self.promedio_final_segundos = promedio_final_segundos

    def datos_finales(self):
        return {"promedio_final": self.promedio_final, "tiempo_total": self.tiempo_total,
                "error_final": self.error_final, "gpus": self.gpus,
                "promedio_final_segundos": self.promedio_final_segundos}


class InfosEscenaBlend:
    def __init__(self, nombre_Escena=None, inicio=None, fin=None, step=None, ruta_completa=None,
                 ruta_frame_output="", view_layers=None,
                 camara=None, camaras=None):
        self.escena = nombre_Escena
        self.inicio = inicio
        self.fin = fin
        self.step = step
        self.ruta_completa = ruta_completa
        self.ruta_frame_output = ruta_frame_output
        self.view_layers = view_layers
        self.camara = camara
        self.camaras = camaras

    def __str__(self):
        attributes = [f"{key}={value}" for key, value in self.__dict__.items()]
        return ', '.join(attributes)

    @classmethod
    def obtener_infos_escenas(cls, ruta):
        try:
            datas_escenas, version_blender = obtener_data_escenas(ruta)
        except Exception as e:
            print("e", e)  # debug print
            return {}
        return {"version_blender": version_blender,
                "data_escenas": {datas_escena["nombre_Escena"]: cls(**datas_escena) for datas_escena in datas_escenas}}


class ItemEstado(QtWidgets.QTreeWidgetItem):
    columna = {"estado": 0, "frames": 1, "eta": 2}

    def __init__(self, parent, estado, desactivado, valor, frames="", faltante=False):
        super().__init__(parent)
        wgt = QtWidgets.QWidget()
        wgt.setContentsMargins(0, 0, 0, 0)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 10, 0)
        self.pb = QProgressBar()
        self.reaplicar_font()
        layout.addWidget(self.pb)
        wgt.setLayout(layout)
        self.treeWidget().setItemWidget(self, 0, wgt)
        self.actualizar(estado, desactivado, valor, frames, faltante=faltante)

    def reaplicar_font(self, altura=None):
        font = self.font(0)
        self.pb.setFont(font)
        altura = configuracion.alto_filas if altura is None else altura
        maxa = int(min(altura * font.pointSize() / 11, altura * .85))
        self.pb.setMaximumHeight(maxa)

    def actualizar(self, estado, desactivado, valor, frames, faltante=False):
        # visibilizar_pb = estado not in ("no_comenzado", "preparando")
        # self.pb.setVisible(visibilizar_pb)

        if desactivado:
            estado = "desactivado"
        self.pb.setStyleSheet(configuracion.stylesheet_pb(estado))
        self.setIcon(self.columna["estado"], iconos.estados[estado])
        self.pb.setValue(valor)

        estado = "faltante" if faltante else estado
        texto_estado = traduccion.estados(estado)
        self.pb.setFormat(texto_estado)
        frames = str(frames) if frames else ""
        self.setText(self.columna["frames"], str(frames))

    def alinear(self, settings_ventana):
        for i in self.columna.values():
            self.setTextAlignment(i, settings_ventana.alineamientos[
                settings_ventana.alineamientos_estados[i]] | Qt.AlignmentFlag.AlignVCenter)

    def toggle_pb(self):
        self.pb.setVisible(not self.pb.isVisible())


class InfoEscenasManual:  # esto incluye todo lo que hace infosescenamanual pero mantengo por separadas por cuetsiones
    #  de performance posibles, aunque no probé

    def __init__(self, archivo=None, item=None, avisar=None, pasar_parametro=False, cursor_espera=True):
        if archivo:
            self.archivo = archivo
        elif item:
            self.archivo = item.ruta_blend_completa
        else:
            return

        self.item = item
        version_blender = versiones_blender.ruta(item.tag_blender)
        self.infos_blender = InfosBlender(self.leer_data, cursor_espera=cursor_espera, version_blender=version_blender)
        self.avisar = avisar
        self.pasar_parametro = pasar_parametro
        self.output_blender = ""

    def averiguar(self):
        datas.crear_script(datas.ruta_script_escenas,
                           datas.script_escenas)
        argumentos = ['-b', self.archivo, '--factory-startup', '-P', datas.ruta_script_escenas]
        # argumentos = ['-b', self.archivo, '-P', datas.ruta_script_escenas]
        self.infos_blender.correr_blender(argumentos)
        if self.item:
            self.item.recabando_info = True

    def leer_data(self, data):
        escenas = {}
        for linea in data.splitlines():
            if not linea.startswith(datas.handle_scene_data):
                continue

            try:
                data_json = json.loads(linea.removeprefix(datas.handle_scene_data))
                info_escena = InfosEscenaBlend(*data_json)
                escenas[info_escena.escena] = info_escena
            except Exception as e:
                print(e)

        if not (escenas and len(escenas)):
            return

        if self.item:
            self.item.escenas = escenas
            # for escena in escenas:
            #     if not escena.camara:
            #         alertas.alerta_generica("alerta_camara")
            self.item.recabando_info = False

        if self.avisar:
            parametros_aceptados = signature(self.avisar).parameters
            parametros_pasar = {}
            if "escenas" in parametros_aceptados:
                parametros_pasar["escenas"] = escenas
            if "ruta" in parametros_aceptados:
                parametros_pasar["ruta"] = self.archivo

            self.avisar(**parametros_pasar)


class InfosBlender:
    procesos_activos = set()

    def __init__(self, retorno_info=None, cursor_espera=True, debug=True, version_blender=None, live=False):
        self.proceso_blender = None
        self.retorno_info = retorno_info
        self.output_blender = ""
        self.version_blender = version_blender if version_blender else versiones_blender.ruta_default
        self.debug = debug
        self.cursor_espera = cursor_espera
        self.live = live  # actualmente no en uso. La idea sería poder ir leyendo e interpretando la data a medida
        # que va saliendo. Originalmente para poder prescindir del factory-settings e igual tomar la data ligeramente
        # aún si algún addon bloquea el cierre de blender

    def correr_blender(self, argumentos=None):
        if argumentos is None:  # esto para permitir corridas diagnóstico supongo yo, no recuerdo
            argumentos = ["-b"]
        if self.cursor_espera:
            set_cursor_espera()
        self.proceso_blender = QtCore.QProcess()
        self.procesos_activos.add(self.proceso_blender)
        self.proceso_blender.setArguments(argumentos)
        self.proceso_blender.setProgram(self.version_blender)
        self.proceso_blender.start()
        self.proceso_blender.readyReadStandardOutput.connect(self.leer_output)
        self.proceso_blender.finished.connect(self.termino)

    def leer_output(self):  # esto requiere refactor asoluto
        lectura = self.proceso_blender.readAll().data().decode('utf-8', 'ignore')
        self.output_blender += lectura
        if self.live:
            self.retorno_info(lectura)
        if self.debug:
            print(lectura)
            # os.makedirs(Datas.ruta_base_debug, exist_ok=True)
            # with open(Datas.ruta_archivo_debug_infoescenas, "a", encoding="utf8") as output_debug:
            #     output_debug.write(lectura)

    def termino(self):
        self.procesos_activos.discard(self.proceso_blender)
        if self.retorno_info and not self.live:
            self.retorno_info(self.output_blender)
        self.output_blender = ""
        restore_cursor()


class InfosEscenaManual:

    def __init__(self, items, avisar=None, cursor_espera=True):
        self.item = items[0]
        self.items = items.copy()
        if self.item.tag_blender != "Default":
            version_blender = versiones_blender.ruta(self.item.tag_blender)
        else:
            version_blender = None
        self.infos_blender = InfosBlender(retorno_info=self.leer_data, cursor_espera=cursor_espera,
                                          version_blender=version_blender)
        self.avisar = avisar
        self.preservar_propiedades_argumentadas = False
        self.argumentos_base = None

    def averiguar(self):
        path = os.path.join(self.item.ruta_blend, self.item.nombre_blend)
        datas.crear_script(datas.ruta_script_infos_escena,
                           datas.script_infos_escena)

        self.argumentos_base = ['-b', path, '--factory-startup']
        self.recursion_items()

    def recursion_items(self):
        if not self.items:
            if self.avisar:
                self.avisar()
            return
        self.item = self.items.pop()
        argumentos = self.argumentos_base.copy()
        if self.item.escena:
            argumentos.extend(["-S", self.item.escena])
        argumentos.extend(['-P', datas.ruta_script_infos_escena])
        self.item.recabando_info = True
        self.infos_blender.correr_blender(argumentos)

    def leer_data_legacy(self, data):
        data_json = ""
        for linea in data.splitlines():
            if not linea.startswith(datas.handle_scene_data):
                continue

            try:
                data_json = json.loads(linea.removeprefix(datas.handle_scene_data))
                break
            except Exception as e:
                print(e)
                return
        if not data_json:
            return
        info_escena = InfosEscenaBlend(*data_json)
        self.item.asimilar_info_escena(info_escena, self.preservar_propiedades_argumentadas)

        self.recursion_items()

    def leer_data(self, data):
        patron_str = rf'{re.escape(datas.handle_scene_data)}\s*(\[.*?\])'
        patron = re.compile(patron_str)

        # Search for the pattern in the text
        match = patron.search(data)
        if match:
            json_list_str = match.group(1)
            try:
                data_json = json.loads(json_list_str)
                print("Captured list:", data_json)
            except json.JSONDecodeError as e:
                print("Error parsing JSON:", e)
                return
        else:
            print("List not found")
            return

        info_escena = InfosEscenaBlend(*data_json)
        self.item.asimilar_info_escena(info_escena, self.preservar_propiedades_argumentadas)

        self.recursion_items()
