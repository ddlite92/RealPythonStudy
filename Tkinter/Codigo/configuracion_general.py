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

from PyQt5 import QtGui
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtWidgets import QFileDialog, QLineEdit

import datas as Datas
import alertas as Alertas
import defaults_configuracion
from PyQt5.QtCore import QObject, pyqtSignal
import iconos_app as iconos
import app_context
from distutils import spawn
from traducciones import traducir


class ConfiguracionGeneral(QObject):
    sig_cambio_altura_filas = pyqtSignal(object)
    sig_cambio_autoraise = pyqtSignal(object)
    sig_cambio_display_botones = pyqtSignal(object)
    sig_cambio_alternar_filas = pyqtSignal(object)
    sig_cambio_idioma = pyqtSignal()
    sig_cambio_skin = pyqtSignal(object)
    sig_cambio_escala_textos = pyqtSignal(int, int)
    sig_cambio_escala_uitextos = pyqtSignal(int)
    sig_cambio_escala_iconos = pyqtSignal(int)
    sig_verificar_blender = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # siempre la primera opción es la default

        self.opciones = defaults_configuracion.opciones
        self.booleanas = defaults_configuracion.booleanas
        self.valores_unicos = defaults_configuracion.valores_unicos

        # todo: refactor esto para loopear para set default y así.

        self.idioma = None
        self.nombre_skin = None
        self.custom_skins = {}

        self.reproducir_sonido_render = None
        self.sonido_render = None

        self.auto_frame1 = None
        self.cargar_escenas = None
        self.anteriores_terminados = None
        self.anteriores_interrumpidos = None
        self.alternar_color_filas = None
        self.botones_iconos = None
        self.botones_texto = None
        self.botones_autoraise = None

        self.alto_filas = None

        self.skin_dark = None

        self.instancias_max = None

        self.tratar_fallidos = None

        self.blender_factory = None
        self.mantener_despierta = None

        self.viewer_imagenes = None
        self.viewer_secuencias = None
        self.viewer_videos = None

        self.rutas_custom_viewers = None

        self.render_timeout = None

        self.app_font = None

        self.factor_ui_font_size = None
        self.factor_buttons_font_size = None

        self.factor_icons_size = None

        self.fps = None

        # try:
        #     if os.path.isfile(Datas.ruta_defaultsitem):
        #         self.defaults_item = ItemDefaults()
        #         self.defaults_item.leer()
        #     else:
        #         self.defaults_item = None  # esto es parte de configuración para tener acceso universal sin crearlo desde el
        #     # vamos y porque tiene sentido pero se guarda aparte por sus propios medios
        # except NameError:
        #     self.defaults_item = None

    # def guardar_defaults_item(self, defaults=None):
    #     if self.defaults_items is not None:
    #         self.defaults_items.update(defaults)
    #     else:
    #         self.defaults_items = {defaults}
    #     self.guardar_configuracion_json()

    def inicializar(self):
        self.definir_sin_skin()
        self.resetear_configuracion()

    def definir_sin_skin(self):
        self.sinskin = app_context.app.palette()
        self.sinskin.setColor(QtGui.QPalette.Highlight,
                              QtGui.QColor(0, 120, 215))  # importante para la seleccion en tabla estado

    def resetear_configuracion(self):
        for nombre_opcion, opcion in self.__dict__.items():
            if nombre_opcion in self.opciones:
                self.__dict__[nombre_opcion] = self.opciones[nombre_opcion][0]
            if nombre_opcion in self.booleanas:
                self.__dict__[nombre_opcion] = self.booleanas[nombre_opcion]

        self.nombre_skin = "bdark"
        self.sonido_render = defaults_configuracion.sonido_render
        self.instancias_max = 1
        self.render_timeout = defaults_configuracion.render_timeout
        self.alto_filas = defaults_configuracion.alto_filas
        self.factor_ui_font_size = 100
        self.factor_buttons_font_size = 100
        self.factor_icons_size = 100
        self.app_font = defaults_configuracion.default_font()
        self.fps = defaults_configuracion.default_fps
        self.rutas_custom_viewers = defaults_configuracion.rutas_custom_viewers
        self.setear_skin()
        self.set_font()
        app_context.idioma = self.idioma

    def leer_skins(self):
        try:
            with open(Datas.ruta_skins, "r", encoding="utf8") as archivo_skins:
                data_json = archivo_skins.readline()
            self.custom_skins = json.loads(data_json)

        except (IOError, json.decoder.JSONDecodeError) as e:
            from skins_extra_incluidos import skins_extra
            self.custom_skins = skins_extra
        defaults_configuracion.actualizar_formato_skins(self.custom_skins)

    def guardar_skins(self):
        if not self.custom_skins:
            return
        try:
            with open(Datas.ruta_skins, "w", encoding="utf8") as archivo_skins:
                archivo_skins.write(json.dumps(self.custom_skins))
        except (IOError, json.decoder.JSONDecodeError, TypeError) as e:
            print(e)

    def importar_skins(self, ruta):
        try:
            with open(ruta, "r", encoding="utf8") as archivo_skins:
                skin_dict = json.load(archivo_skins)
        except (IOError, json.decoder.JSONDecodeError, TypeError) as e:
            print(e)
            Alertas.alerta_generica("alerta_archivo_skin_invalido")
            return
        nombre = os.path.basename(ruta)
        nombre, _ = os.path.splitext(nombre)
        if not validar_corregir_estructura_dict(skin_dict, defaults_configuracion.validador_skins,
                                                defaults_configuracion.actualizar_formato_skin_iconos):
            for skin in skin_dict.values():
                if not validar_corregir_estructura_dict(skin, defaults_configuracion.validador_skins,
                                                        defaults_configuracion.actualizar_formato_skin_iconos):
                    Alertas.alerta_generica("alerta_archivo_skin_invalido")
                    return False
            self.custom_skins.update(skin_dict)
            self.nombre_skin = next(iter(skin_dict))
            return skin_dict.keys()
        self.custom_skins[nombre] = skin_dict
        self.nombre_skin = nombre
        return [nombre]

    def exportar_skin(self, ruta):
        try:
            with open(ruta, "w", encoding="utf8") as archivo_skins:
                archivo_skins.write(json.dumps(self.skin_actual()))
        except (IOError, json.decoder.JSONDecodeError, TypeError) as e:
            print(e)

    def leer_configuracion_json(self):
        self.leer_skins()

        try:
            with open(Datas.ruta_settings, "r", encoding="utf8") as archivo_config:
                data_json = archivo_config.readline()

        except IOError:
            self.resetear_configuracion()
            return False
        try:
            data_json = json.loads(data_json)
        except json.decoder.JSONDecodeError:
            return False
        for nombre_tipo in data_json:
            for nombre_opcion in data_json[nombre_tipo]:
                setattr(self, nombre_opcion, data_json[nombre_tipo][nombre_opcion])

        if not self.sonido_render:
            self.sonido_render = "completed.wav"

        self.set_font()
        self.setear_skin()

        app_context.idioma = self.idioma
        return True

    def guardar(self):
        json_config = {}
        json_config["opciones"] = self.loop_jsonear_opciones(self.opciones)
        json_config["booleanas"] = self.loop_jsonear_opciones(self.booleanas)
        json_config["valores_unicos"] = self.loop_jsonear_opciones(self.valores_unicos)
        self.guardar_skins()
        try:
            with open(Datas.ruta_settings, "w", encoding="utf8") as archivo_config:
                archivo_config.write(json.dumps(json_config))
        except IOError:
            Alertas.alerta_permisos()

    def loop_jsonear_opciones(self, dict_opciones):
        dict_json_opcion = {}
        for nombre_opcion in dict_opciones:
            opcion_elegida = getattr(self, nombre_opcion, None)
            dict_json_opcion[nombre_opcion] = opcion_elegida
        return dict_json_opcion

    def set_font(self):
        nombre_font = self.app_font if self.app_font else defaults_configuracion.default_font()
        app_context.app.setFont(QFont(nombre_font))

    @staticmethod
    def setear_estilo_botones(botones, estilo):
        for boton in botones:
            boton.setStyleSheet(estilo)
        return

    def skin_actual(self):

        skin = defaults_configuracion.skins_builtin.get(self.nombre_skin, self.custom_skins.get(self.nombre_skin))
        return skin if skin else defaults_configuracion.skin_bdark

    def setear_skin(self):
        skin = self.skin_actual()
        paleta = self.sinskin if self.nombre_skin == "sin_skin" else self.paleta_de_skin(skin)

        app_context.app.setPalette(paleta)

        iconos.set_icons_for_theme(skin)

        color_borde = "gray"
        color_borde_highlight = paleta.color(QPalette.Highlight).name()
        color_relleno = paleta.color(QPalette.Base).name()

        app_context.app.setStyleSheet(f"""
                                 QLineEdit {{
                    border: 1px solid {color_borde};
                    border-radius: 7px;
                    padding: 2 8px;
                    background-color: {color_relleno};
                }}

                QLineEdit:focus {{
                    border: 1px solid {color_borde_highlight};
                    background-color: {color_relleno};
                }}
                                    }}
                                """)

    @staticmethod
    def paleta_de_skin(skin):

        paleta = app_context.app.palette()

        for rol, info in skin["Main"].items():
            if rol in defaults_configuracion.backgrounds_state_functions:
                continue
            paleta.setColor(int(rol), QtGui.QColor(info["color"]))
        for rol, info in skin["Disabled"].items():
            paleta.setColor(QtGui.QPalette.Disabled, int(rol), QtGui.QColor(info["color"]))
        return paleta

    def stylesheet_pb(self, estado):
        skin = self.skin_actual()
        if estado in skin["Progress bar"]:
            base = defaults_configuracion.base_qss_fallidos_pb if estado == "fallo" else defaults_configuracion.base_qss_pb
            base += defaults_configuracion.chunk_qss_pb
            return base.format(*skin["Progress bar"][estado].values())
        else:
            return ""


def validar_corregir_estructura_dict(json_dict, expected_structure, funcion_correctora):
    if not validar_estructura_json_dict(json_dict, expected_structure):
        funcion_correctora(json_dict)
        return validar_estructura_json_dict(json_dict, expected_structure)
    return True


def validar_estructura_json_dict(json_dict, expected_structure):
    if isinstance(expected_structure, dict):
        for key, value in expected_structure.items():
            if key not in json_dict:
                return False
            if not validar_estructura_json_dict(json_dict[key], value):
                return False
    elif isinstance(expected_structure, type):
        if not isinstance(json_dict, expected_structure):
            return False
    return True


def get_color_de_skin(skin, grupo, rol):
    colores_grupo = skin.get(grupo, {})
    data_color = colores_grupo.get(str(rol), {})
    return data_color.get("color", "")



configuracion = ConfiguracionGeneral()
