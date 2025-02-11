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

from PyQt5.QtGui import QIcon

import recursos_chuchurenderon_rc
import os
from PyQt5 import QtGui
import defaults_configuracion


def pixmaps_iconos_themeables(set_iconos):
    for nombre_icono in iconos_themeables_basicos:
        ruta = os.path.join(":/iconos/{}".format(set_iconos), nombre_icono + ".png")
        yield nombre_icono, QtGui.QPixmap(ruta)


def set_icons_for_theme(skin):
    color_enabled = skin["iconos"]["enabled"].upper()
    colores_base = defaults_configuracion.sets_iconos.get(color_enabled, "White")
    pool_iconos = pixmaps_iconos_themeables(colores_base)

    for nombre_icono, pixmap in pool_iconos:
        if color_enabled not in defaults_configuracion.sets_iconos:
            colorizar_icono(pixmap, color_enabled)

        iconos_themeables_basicos[nombre_icono].addPixmap(pixmap, QtGui.QIcon.Normal,
                                                          QtGui.QIcon.Off)

        colorizar_icono(pixmap, skin["iconos"]["disabled"])
        iconos_themeables_basicos[nombre_icono].addPixmap(pixmap, QtGui.QIcon.Disabled)


def set_iconos_no_themeables():
    icono_render.addPixmap(QtGui.QPixmap(":/iconos/render.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    icono_stop.addPixmap(QtGui.QPixmap(":/iconos/stop_render.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    icono_apagar.addPixmap(QtGui.QPixmap(":/iconos/ico_apagar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
    icono_interaccion_vacua.addPixmap(QtGui.QPixmap(":/iconos/interaccion_vacua.png"), QtGui.QIcon.Normal,
                                      QtGui.QIcon.Off)
    icono_nocomenzado.addPixmap(QtGui.QPixmap(":/iconos/icoestado_nocomenzado.png"), QtGui.QIcon.Normal,
                                QtGui.QIcon.Off)
    icono_renderizando.addPixmap(QtGui.QPixmap(":/iconos/icoestado_renderizando.png"), QtGui.QIcon.Normal,
                                 QtGui.QIcon.Off)
    icono_interrumpido.addPixmap(QtGui.QPixmap(":/iconos/icoestado_interrumpido.png"), QtGui.QIcon.Normal,
                                 QtGui.QIcon.Off)
    icono_fallado.addPixmap(QtGui.QPixmap(":/iconos/icoestado_fallado.png"), QtGui.QIcon.Normal,
                            QtGui.QIcon.Off)
    icono_terminado.addPixmap(QtGui.QPixmap(":/iconos/icoestado_terminado.png"), QtGui.QIcon.Normal,
                              QtGui.QIcon.Off)
    icono_desactivado.addPixmap(QtGui.QPixmap(":/iconos/icoestado_desactivado.png"), QtGui.QIcon.Normal,
                                QtGui.QIcon.Off)
    icono_modo.addPixmap(QtGui.QPixmap(":/iconos/mode.svg"), QtGui.QIcon.Normal,
                         QtGui.QIcon.Off)
    icono_app.addPixmap(QtGui.QPixmap(":/iconos/icoapp.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)


def colorizar_icono(pixmap, color):
    painter = QtGui.QPainter(pixmap)
    painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceIn)
    color = QtGui.QColor(color)
    painter.setBrush(color)
    painter.setPen(color)

    painter.drawRect(pixmap.rect())
    painter.end()

    painter.end()


icono_configuracion = QIcon()

icono_info = QIcon()

icono_agregar = QIcon()
icono_quitar_elegidos = QIcon()
icono_quitar_todos = QIcon()

icono_reajustar_modo = QIcon()
icono_version = QIcon()
icono_escenas = QIcon()
icono_viewlayers = QIcon()
icono_camaras = QIcon()
icono_rango = QIcon()
icono_setoutput = QIcon()
extra_args = QIcon()
icono_dispositivos = QIcon()
icono_colecciones = QIcon()

icono_abrir_blend = QIcon()
icono_explorar_output = QIcon()
icono_ver_render = QIcon()

icono_render = QIcon()
icono_stop = QIcon()

icono_apagar = QIcon()

icono_blend = QIcon()
icono_interaccion_vacua = QIcon()

icono_app = QIcon()

icono_log = QIcon()

icono_bl_live_log = QIcon()

icono_livelog_close = QIcon()
icono_livelog_save = QIcon()
icono_livelog_floating = QIcon()
icono_livelog_top = QIcon()
icono_livelog_bottom = QIcon()
icono_livelog_left = QIcon()
icono_livelog_right = QIcon()
icono_livelog_next_save = QIcon()
icono_livelog_previous_save = QIcon()
icono_livelog_fin = QIcon()
icono_livelog_inicio = QIcon()

icono_apagar_on = QIcon()
icono_apagar_off = QIcon()

icono_presets = QIcon()
icono_opciones_modos = QIcon()
icono_opciones_colas = QIcon()

icono_watch_folder = QIcon()
icono_add_folder = QIcon()

icono_browse = QIcon()

icono_scheduler = QIcon()

icono_mas = QIcon()
icono_menos = QIcon()
icono_importar = QIcon()
icono_exportar = QIcon()

icono_reset = QIcon()
icono_collections_update = QIcon()

icono_sm_viewlayer = QIcon()
icono_sm_scene = QIcon()
icono_sm_camera = QIcon()

icono_update_view_layers = QIcon()
icono_update_cameras = QIcon()
icono_update_scenes = QIcon()

icono_pencil = QIcon()

icono_grab = QIcon()

icono_nocomenzado = QIcon()
icono_renderizando = QIcon()
icono_interrumpido = QIcon()
icono_fallado = QIcon()
icono_terminado = QIcon()
icono_desactivado = QIcon()

icono_agregar_blender = QIcon()

icono_modo = QIcon()

icono_warning = QIcon()

estados = {"no_comenzado": icono_nocomenzado, "renderizando": icono_renderizando, "terminado":
    icono_terminado, "interrumpido": icono_interrumpido, "fallo": icono_fallado,
           "desactivado": icono_desactivado, "preparando": icono_renderizando}

iconos_themeables_basicos = {"info": icono_info, "log": icono_log,
                             "settings": icono_configuracion,
                             "add_blends": icono_agregar, "console": icono_bl_live_log,
                             "delete": icono_quitar_elegidos, "clear_queue": icono_quitar_todos,
                             "mode": icono_reajustar_modo,
                             "blender_version": icono_version,
                             "scenes": icono_escenas,
                             "view_layers": icono_viewlayers,
                             "cameras": icono_camaras,
                             "frame ranges": icono_rango,
                             "output_filepath": icono_setoutput,
                             "extra": extra_args,
                             "devices": icono_dispositivos, "open_blend": icono_abrir_blend,
                             "open_output_path": icono_explorar_output,
                             "view_render": icono_ver_render,
                             "watchfolders": icono_watch_folder,
                             "shutdown_off": icono_apagar_off,
                             "shutdown_on": icono_apagar_on,
                             "scheduler": icono_scheduler,
                             "preset": icono_presets,
                             "blend": icono_blend,
                             "collections": icono_colecciones,
                             "modes_options": icono_opciones_modos,
                             "queues_options": icono_opciones_colas,
                             "add_folder": icono_add_folder,
                             "browse": icono_browse,
                             "mas": icono_mas,
                             "menos": icono_menos,
                             "import": icono_importar,
                             "export": icono_exportar,
                             "livelog_close": icono_livelog_close,
                             "livelog_floating": icono_livelog_floating,
                             "livelog_top": icono_livelog_top,
                             "livelog_bottom": icono_livelog_bottom,
                             "livelog_left": icono_livelog_left,
                             "livelog_right": icono_livelog_right,
                             "livelog_previous_save": icono_livelog_previous_save,
                             "livelog_next_save": icono_livelog_next_save,
                             "livelog_inicio": icono_livelog_inicio,
                             "livelog_fin": icono_livelog_fin,
                             "livelog_save": icono_livelog_save,
                             "collections_update": icono_collections_update,
                             "reset": icono_reset,
                             "sm_viewlayer": icono_sm_viewlayer,
                             "sm_scene": icono_sm_scene,
                             "sm_camera": icono_sm_camera,
                             "update_view_layers": icono_update_view_layers,
                             "update_cameras": icono_update_cameras,
                             "update_scenes": icono_update_scenes,
                             "pencil": icono_pencil,
                             "grab": icono_grab,
                             "add_blender": icono_agregar_blender,
                             "warning": icono_warning
                             }
