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


# -*- coding: utf-8 -*-
import ctypes
from datetime import datetime
import json
import os
import re
import subprocess
import sys
from pathlib import Path
import copy

from collections import defaultdict

import OpenEXR
import Imath

import time

from numpy import array_split, clip
import numpy as np

from PyQt5.QtMultimedia import QSound
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QFont, QPalette, QIcon
from PyQt5.QtCore import QTime, QTimer, QObject, QDateTime, QThread, pyqtSignal, pyqtSlot, QRunnable, QThreadPool, Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, \
    QInputDialog, QMenu, QProgressBar, QBoxLayout, QLabel, QSpacerItem, QTreeWidgetItem, QTreeWidgetItemIterator, \
    QAction

from typing import List, Union
from inspect import signature



from functools import partial

# from difflib import get_close_matches

import Statusbar
import alertas

import defaults_configuracion
import items_cola
import management_modos
# import iconos_app as iconos

import utilidades_tiempo as UtilidadesTiempo
import datas as Datas
import app_context
import recursos_chuchurenderon_rc
import iconos_app as iconos
import blenders
import autonombrado as auto_nombrado
from utils import renombrar_duplicado, agregar_linea, serializar, restore_cursor, set_cursor_espera, UnDefaultDict

import atajos_y_contextuales
from atajos_y_contextuales import atajos_formateados

# import bpy
import bleuristicas
import traducciones as traduccion # deberia renombrar el modulo y ya
from traducciones import traducir
import configuracion_general
from items_cola import InfoEscenasManual, InfosBlender, ItemCola, ItemFantasma, ColumnaProp
import colas_perennes

import ui.ventana_info
import ui.visor_renders
import ui.ventana_principal_32
# import ui.ventana_principal
import ui.ventana_settings
import ui.scheduler
import ui.argumentos_extra
import ui.ventana_dispositivos
import ui.cambiar_blender
import ui.widget_distribuir_blenders
import ui.ventana_variantes
import ui.cambiar_rango
import ui.ventana_nombrado
import ui.config_watchfolder

import ui.widget_nombrado
import ui.dialogo_reubicar
import ui.numero_splits
import ui.dialogo_frames
import ui.editor_modo
import ui.ventana_colecciones
import ui.watchfolders_arbol
from ui.token_widgets import WidgetToken, WidgetTokenIncremental, get_parte_patron

from ui.widgets_universales import BotonBrowse
from ui.header_tablas import HeaderTablas
import ui.ventana_tareas
import ui.ventana_estimar
import ui.editor_skin
import ui.info_popup
import ui.blend_no_encontrado

from custom_item_widgets import ItemWidgetBasico, ItemSelector, ItemLinea, ItemTitulo, ItemChk, \
    ItemCustomWidget
# from ui.combobox_alternativa import ComboBoxAlternativa, ComboBoxModos

import util_ui
from ventana_blenders import VentanaBlenders


tipo_build = "normal"  # cualquier cosa vs debug


# tipo_build = "debug" # cualquier cosa vs debug


class InfoPopUp(QtWidgets.QDialog, ui.info_popup.Ui_popup):
    def __init__(self, parent=None, nombre_texto=""):
        super().__init__(parent)
        self.setupUi(self)
        # Set the window flags to remove the title bar
        self.old_position = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.contenedor_texto.setStyleSheet("background: transparent; border: none;")
        texto_traducido = traduccion.traducir_popup(nombre_texto)
        self.setText(texto_traducido)
        self.ico_info.setPixmap(iconos.icono_info.pixmap(32, 32))


    def setText(self, texto):
        self.contenedor_texto.setHtml(texto)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_position = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.old_position:
            delta = QtCore.QPoint(event.globalPos() - self.old_position)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_position = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_position = None


class BotonPreset(QtWidgets.QPushButton):

    def __init__(self, numero, preset, parent):
        super().__init__(parent)

        self.parent = parent
        self.numero = numero
        # self.setText("")
        # self.setMinimumHeight(self.height()*2)
        self.setText(preset.nombre_visible)
        self.preset = preset
        # self.clicked.connect(self.usar_preset)

        self.context_menu = QMenu(self)
        opcion_eliminar = self.context_menu.addAction(traducir("Borrar"))
        opcion_eliminar.triggered.connect(self.eliminar_preset)
        # opcion_modificar = self.context_menu.addAction(traducir("Modificar"))
        # opcion_modificar.triggered.connect(self.modificar_preset)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        self.setToolTip(traducir("Click derecho para opciones"))

    def modificar_preset(self):
        self.parent.modificar_preset(self, self.numero)

    def eliminar_preset(self):
        self.deleteLater()
        self.preset.eliminar = True
        auto_nombrado.actualizar_presets()
        auto_nombrado.guardar_presets()

    def mostrar_menu_contextual(self, posicion):
        self.context_menu.popup(self.mapToGlobal(posicion))
        # self.context_menu.excec_(self.mapToGlobal(posicion))



# class VentanaDispositivosLegacy(QtWidgets.QDialog, ui.ventana_dispositivos.Ui_ventana_dispositivos):
#     def __init__(self, ventana):
#         super().__init__()
#         self.setupUi(self)
#
#         self.ventana = ventana
#         self.botones_por_tipo = None
#         # self.botones_por_tipo = {"CUDA": self.btn_cuda, "CPU": self.btn_cpu, "HIP": self.btn_hip,
#         #                          "OPENCL": self.btn_opencl, "OPTIX": self.btn_optix}
#
#         self.items_por_tipo = None
#         self.btn_cpu = None
#         self.tipos_excluyentes = None
#         self.grupo_tipos = QtWidgets.QButtonGroup()
#         self.separadores_tipo = None
#         self.conectar_acciones_botones()
#         self.leer_dispositivos()
#         self.adjustSize()
#
#     def conectar_acciones_botones(self):
#         self.lista.itemClicked.connect(self.eligio_particular)
#         self.lista.itemDoubleClicked.connect(self.eligio_particular)
#         self.grupo_opciones.buttonToggled.connect(self.cambio_opcion)
#         self.btn_encontrar.clicked.connect(self.encontrar_dispositivos)
#         self.aceptar_cancelar.accepted.connect(self.aceptar)
#         self.aceptar_cancelar.rejected.connect(self.close)
#         self.btn_distribuir.pressed.connect(self.distribuir)
#         self.btn_distribuir.setToolTip(traducir("distribuir_dispositivos"))
#         atajo_cancelar_busqueda = QtWidgets.QShortcut(QtGui.QKeySequence('Esc'), self)
#         atajo_cancelar_busqueda.activated.connect(self.cancelar_busqueda)
#
#     def distribuir(self):
#         num_items_elegidos = len(self.ventana.tablaPrincipal.selectedItems())
#
#         if not self.lista.selectedItems():
#             return
#         # dispositivos_elegidos = [disp_i for disp_i in self.lista.selectedItems() if not disp_i.isHidden()]
#         dispositivos_elegidos = self.lista.selectedItems()
#         num_dispositivos_elegidos = len(dispositivos_elegidos)
#
#         for i in range(num_items_elegidos):
#             item_i = self.ventana.tablaPrincipal.selectedItems()[i]
#             indice_distribucion = i % num_dispositivos_elegidos
#             dispositivo_i = dispositivos_elegidos[indice_distribucion]
#             tipo = dispositivo_i.data(QtCore.Qt.UserRole)[0]
#             item_i.nombres_dispositivos = "(" + tipo + ") " + dispositivo_i.text()
#             item_i.dispositivos = [dispositivo_i.data(QtCore.Qt.UserRole)[1]]
#             item_i.tipo_dispositivos = tipo
#
#         self.cierre_positivo()
#
#     def inhabilitacion_botones(self):
#         if self.opcion_respetar.isChecked():
#             self.btn_distribuir.setDisabled(True)
#             self.aceptar_cancelar.button(QtWidgets.QDialogButtonBox.Ok).setDisabled(False)
#             return
#
#         hay_elegidos = bool(self.lista.selectedItems())
#         self.btn_distribuir.setDisabled(not hay_elegidos)
#         self.aceptar_cancelar.button(QtWidgets.QDialogButtonBox.Ok).setDisabled(not hay_elegidos)
#
#     def cierre_positivo(self):
#         if self.ventana.item_unico_elegido:
#             item_activo = self.ventana.item_unico_elegido
#         else:
#             item_activo = self.ventana.tablaPrincipal.currentItem()
#         if item_activo:
#             self.ventana.tablaPrincipal.setCurrentItem(item_activo,
#                                                        self.ventana.columna["nombres_dispositivos"])
#         indice_scroll = self.ventana.tablaPrincipal.currentIndex()
#         self.ventana.tablaPrincipal.scrollTo(indice_scroll)
#         colas.guardar()
#         self.close()
#
#     def cancelar_busqueda(self):
#         try:
#             dispositivos_cycles.infos_blender.proceso_blender.kill()
#         except AttributeError:
#             pass
#
#     def eligio_particular(self, item):
#         self.opcion_particulares.setChecked(True)
#         self.inhabilitacion_botones()
#         if not item.isSelected():
#             return
#         tipo_elegido = item.data(QtCore.Qt.UserRole)[0]
#         if tipo_elegido == "CPU":
#             return
#         for tipo in self.items_por_tipo:
#             if tipo == tipo_elegido or tipo == "CPU":
#                 continue
#             for item in self.items_por_tipo[tipo]:
#                 item.setSelected(False)
#
#
#     def leer_dispositivos(self):
#         self.lista.clear()
#         if any(dispositivos_cycles.por_tipo): # si ya los habia leido que no los lea de vuelta
#             self.termino_lectura(True)
#             return
#         dispositivos_cycles.reportar_hallazgos = self.termino_lectura
#         dispositivos_cycles.leer_archivo_dispositivos()
#
#     def termino_lectura(self, encontro_dispositivos):
#         if encontro_dispositivos:
#             self.rellenar_listado()
#             self.mostrar_apropiados()
#             return
#         self.lbl_filter.setDisabled(True)
#         self.opcion_particulares.setDisabled(True)
#
#     def encontrar_dispositivos(self):
#         self.lista.clear()
#         dispositivos_cycles.reportar_hallazgos = self.termino_busqueda
#         dispositivos_cycles.encontrar_dispositivos_disponibles()
#
#     def termino_busqueda(self, encontro_dispositivos):
#         if encontro_dispositivos:
#             self.rellenar_listado()
#             self.opcion_particulares.setChecked(True)
#             self.inhabilitacion_botones()
#             self.lbl_filter.setEnabled(True)
#             self.opcion_particulares.setEnabled(True)
#         else:
#             self.alertar()
#
#     def limpiar_botones(self):
#         while self.layout_tipos.count():
#             eliminado = self.layout_tipos.takeAt(0)
#             if eliminado.widget():
#                 eliminado.widget().deleteLater()
#
#     def rellenar_listado(self):
#         self.tipos_excluyentes = [tipo for tipo in dispositivos_cycles.por_tipo if tipo != "CPU"]
#         self.botones_por_tipo = {}
#         self.separadores_tipo = []
#         self.items_por_tipo = {}
#         self.limpiar_botones()
#         for tipo in dispositivos_cycles.por_tipo:
#             boton_tipo = QtWidgets.QPushButton(tipo, self)
#             boton_tipo.setCheckable(True)
#             boton_tipo.setObjectName("btn_" + tipo)
#             boton_tipo.pressed.connect(self.tipo_pressed)
#             boton_tipo.released.connect(self.tipo_released)
#             boton_tipo.clicked.connect(self.mostrar_elegidos)
#             self.layout_tipos.addWidget(boton_tipo)
#             self.botones_por_tipo[tipo] = boton_tipo
#             self.items_por_tipo[tipo] = []
#             if tipo == "CPU":
#                 self.btn_cpu = boton_tipo
#             else:
#                 self.grupo_tipos.addButton(boton_tipo)
#             separador_tipo = QtWidgets.QListWidgetItem()
#             separador_tipo.setData(QtCore.Qt.UserRole, "separador")
#             separador_tipo.setFlags(separador_tipo.flags() & ~QtCore.Qt.ItemIsEnabled & ~QtCore.Qt.ItemIsSelectable)
#             separador_tipo.setText(tipo+":")
#             self.lista.addItem(separador_tipo)
#             self.separadores_tipo.append(separador_tipo)
#             for nombre in dispositivos_cycles.por_tipo[tipo]:
#                 for i, id in enumerate(dispositivos_cycles.por_tipo[tipo][nombre]):
#                     item_i = QtWidgets.QListWidgetItem()
#                     item_i.setText(nombre + " (" + str(i+1) + ")")
#                     item_i.setData(QtCore.Qt.UserRole, [tipo, id])
#                     self.items_por_tipo[tipo].append(item_i)
#                     self.lista.addItem(item_i)
#
#
#     def mostrar_items_tipos(self, tipos_a_mostrar, dispositivos_elegidos=None, elegir=False):
#         if not tipos_a_mostrar:
#             tipos_a_mostrar = [boton for boton in self.botones_por_tipo] #si no hay elegido ninguno mostrar todos
#             for tipo in self.items_por_tipo:
#                 for item in self.items_por_tipo[tipo]:
#                     item.setSelected(False)
#             elegir = False
#         for separador in self.separadores_tipo:
#             separador.setFlags(separador.flags() & ~QtCore.Qt.ItemIsEnabled & ~QtCore.Qt.ItemIsSelectable)
#             separador.setHidden(separador.text().rstrip(":") not in tipos_a_mostrar)
#
#         for tipo in self.items_por_tipo:
#             ocultar = tipo not in tipos_a_mostrar
#             for item_i in self.items_por_tipo[tipo]:
#                 item_i.setHidden(ocultar)
#                 if ocultar:
#                     item_i.setSelected(False)
#                     continue
#                 if elegir or (dispositivos_elegidos and item_i.data(QtCore.Qt.UserRole)[1] in dispositivos_elegidos):
#                     item_i.setSelected(True)
#
#         self.inhabilitacion_botones()
#
#     def mostrar_elegidos(self):
#         elegidos = [boton for boton in self.botones_por_tipo if self.botones_por_tipo[boton].isChecked()]
#         self.mostrar_items_tipos(elegidos, elegir=True)
#         self.opcion_particulares.setChecked(True)
#
#     def mostrar_apropiados(self):
#         if self.ventana.item_unico_elegido:
#             item_activo = self.ventana.item_unico_elegido
#         else:
#             item_activo = self.ventana.tablaPrincipal.currentItem()
#         try:
#             tipos_elegidos = item_activo.tipo_dispositivos.split("+")
#             self.botones_por_tipo[tipos_elegidos[0]].setChecked(True)
#             if tipos_elegidos[-1] and tipos_elegidos[-1] == "CPU":
#                 self.btn_cpu.setChecked(True)
#             if item_activo.dispositivos:
#                 dispositivos_elegidos = item_activo.dispositivos
#                 self.opcion_particulares.setChecked(True)
#             else:
#                 dispositivos_elegidos = None
#             self.mostrar_items_tipos(tipos_elegidos, dispositivos_elegidos)
#         except Exception as e:
#             print(e)
#             self.opcion_respetar.setChecked(True)
#
#     def cambio_opcion(self):
#         # for boton in self.grupo_tipos.buttons():
#         #     boton.setDisabled(self.opcion_respetar.isChecked())
#         chequeado = self.opcion_particulares.isChecked()
#         self.btn_distribuir.setEnabled(chequeado)
#         for i in range(self.lista.count()):
#             item = self.lista.item(i)
#             if item.data(QtCore.Qt.UserRole) == "separador":
#                 continue
#             flags = item.flags()
#             toggle = [flags & ~QtCore.Qt.ItemIsEnabled & ~QtCore.Qt.ItemIsSelectable,
#                       flags | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable][chequeado]
#             item.setFlags(toggle)
#         self.inhabilitacion_botones()
#
#     def tipo_pressed(self):
#         chekeado = self.grupo_tipos.checkedButton()
#         if chekeado is not None and chekeado == self.sender():
#             self.grupo_tipos.setExclusive(False)
#
#     def tipo_released(self):
#         chekeado = self.sender()
#         if not self.grupo_tipos.exclusive():
#             chekeado.setChecked(False)
#             self.grupo_tipos.setExclusive(True)
#
#     def alertar(self):
#         alertas.alerta_generica("Error averiguando dispositivos")
#
#     def aceptar(self):
#         items = self.ventana.tablaPrincipal.selectedItems()
#         if self.chk_guardar_config.isChecked():
#             if configuracion.defaults_item is None:
#                 configuracion.defaults_item = ItemDefaults()
#             items.append(configuracion.defaults_item)
#         if self.opcion_respetar.isChecked():
#             self.no_usar_gpu(items)
#         else:
#             if not self.lista.selectedItems():
#                 return
#             self.usar_elegidos(items)
#
#         if self.chk_guardar_config.isChecked():
#             configuracion.defaults_item.guardar()
#         self.cierre_positivo()
#
#     def usar_elegidos(self, items):
#
#         lista_nombres = ''
#         lista_ids = []
#         tipo_gpu = None
#         usa_cpu = None
#
#         for disp_i in self.lista.selectedItems():
#             # if disp_i.isHidden():
#             #     continue
#             tipo = disp_i.data(QtCore.Qt.UserRole)[0]
#             lista_nombres += "(" + tipo + ") " + disp_i.text() + ", "
#             lista_ids.append(disp_i.data(QtCore.Qt.UserRole)[1])
#             if tipo == "CPU":
#                 usa_cpu = "CPU"
#             else:
#                 tipo_gpu = tipo
#
#         tipos = "+".join([tipo for tipo in [tipo_gpu, usa_cpu] if tipo])
#
#         for item_i in items:
#             if hasattr(item_i, "modo") and item_i.modo == "modo_script":
#                 continue
#             item_i.nombres_dispositivos = lista_nombres.strip(", ")
#             item_i.tipo_dispositivos = tipos
#             item_i.dispositivos = lista_ids
#             item_i.propiedades_argumentar.add('dispositivos')
#
#     def no_usar_gpu(self, items):
#         for item_i in items:
#             item_i.nombres_dispositivos = ''
#             item_i.tipo_dispositivos = ''
#             item_i.dispositivos = []
#             item_i.propiedades_argumentar.discard("dispositivos")
#
#     def retranslateUi(self, _):
#         self.setWindowTitle(traducir("Dispositivos de render (Cycles)"))
#         self.opcion_particulares.setText(traducir("Elegir dispositivos particulares"))
#         self.opcion_respetar.setText(traducir("respetar_blender_blend"))
#         self.btn_distribuir.setText(traducir("Distribuir"))
#         self.btn_encontrar.setText(traducir(traducir("Averiguar dispositivos disponibles")))
#         self.chk_guardar_config.setText(traducir("guardar_settings_gpu"))
#         self.lbl_filter.setText(traducir("Filtrar").upper() + ":")
#         self.chk_parallel.setText(traducir("parallel_gpu"))

class BarraProgresoEstado(QProgressBar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFormat('Rendering')


class ItemEstado(QTreeWidgetItem):
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





class CustomLabel(QtWidgets.QWidget):
    def __init__(self, parent=None, item=None):
        super().__init__(parent)
        self.item = item

        self.titulo = QLabel()
        padding = "padding-top: 2px; padding-bottom: 2px;"
        self.titulo.setStyleSheet(padding)
        self.mensaje_combinados = self.configurar_mensaje_combinados()
        spacer = QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.titulo)
        layout.addWidget(self.mensaje_combinados)
        layout.addItem(spacer)
        layout.setSpacing(30)
        self.setLayout(layout)
        self.setToolTip(traducir("tooltip_click_select_all"))

    def setDisabled(self, a0):
        self.titulo.setDisabled(a0)
        self.mensaje_combinados.setDisabled(a0)

    def configurar_mensaje_combinados(self):
        mensaje_combinados = QLabel()
        font = self.font()
        font.setPointSize(
            int(ConfiguracionVentana.size_default_textos["botones"] * configuracion.factor_ui_font_size / 100))
        font.setItalic(True)
        mensaje_combinados.setFont(font)
        mensaje_combinados.setAlignment(Qt.AlignCenter)
        mensaje_combinados.setText("(" + traducir("variantes_resultados_combinados") + ")")
        mensaje_combinados.hide()
        # padding = "padding-top: 3px; padding-bottom: 6px;"
        # mensaje_combinados.setStyleSheet(padding)
        return mensaje_combinados

    def mousePressEvent(self, event):
        self.item.selectAll()

    def setText(self, texto):
        self.titulo.setText(texto)


class SignalsItemLista(QObject):
    itemSelectionChanged = pyqtSignal()


class ItemLista(QTreeWidgetItem):
    def __init__(self, parent=None):
        super(ItemLista, self).__init__(parent)
        self.setExpanded(True)
        self.titulo = CustomLabel(item=self)

        self.treeWidget().setItemWidget(self, 0, self.titulo)
        self.icono = None
        self.setFlags(self.flags() & ~Qt.ItemIsUserCheckable)
        self._selected_items = self.selectedItems()
        self.treeWidget().itemSelectionChanged.connect(self.check_selection_change)
        self.signals = SignalsItemLista()
        self.itemSelectionChanged = self.signals.itemSelectionChanged
        self.paleta = self.definir_paletas()

    def definir_paletas(self):
        paleta_enabled = app.palette()
        paleta_disabled = QtGui.QPalette(paleta_enabled)
        color_disabled = QtGui.QColor(configuracion.skin_actual()["Disabled"][str(QtGui.QPalette.Light)]["color"])
        paleta_disabled.setColor(QtGui.QPalette.Highlight, color_disabled)
        return {"enabled": paleta_enabled, "disabled": paleta_disabled}

    def setDisabled(self, disabled):
        nombre_paleta = ["enabled", "disabled"][disabled]
        self.treeWidget().setPalette(self.paleta[nombre_paleta])
        self.titulo.setDisabled(disabled)

    def mostrar_mensaje_combinados(self):
        self.titulo.mensaje_combinados.show()

    def ocultar_mensaje_combinados(self):
        self.titulo.mensaje_combinados.hide()

    def setTitle(self, texto):
        self.titulo.setText(texto)

    def children(self):
        for i in range(self.childCount()):
            yield self.child(i)

    def hay_presencia(self, nombre):
        for item in self.children():
            if nombre == item.text(0):
                return True
        return False

    def findItems(self, *args):
        encontrar = args[0]
        encontrados = []
        for item in self.children():
            if item.text(0) == encontrar:
                encontrados.append(item)
        return encontrados


    def selectAll(self):
        if self.allItemsSelected():
            #si ya estaban todos elegidos emite señal. Esto es para el caso de elegir todos, cambiar a opcion "respetar" y volver a hacer click para elegir todos, para que el ui responda y se active "elegir"
            self.itemSelectionChanged.emit()
            return
        for sub_item in self.children():
            sub_item.setSelected(True)



    def allItemsSelected(self):
        for item in self.children():
            if not item.isSelected():
                return False
        return True

    def clear(self):
        self.takeChildren()

    def count(self):
        return self.childCount()

    def addItem(self, nombre, selected=False):
        item = QTreeWidgetItem(self, [nombre])
        item.setSelected(selected)
        item.setIcon(0, self.icono)

        # item.setBackground(0, self.children_bg_color)

    def addItems(self, items):
        for item in items:
            self.addItem(item)

    def selectedItems(self):
        elegidos = []
        for item in self.children():
            if item.isSelected():
                elegidos.append(item)
        return elegidos

    def enforce_selection(self):
        self.treeWidget().blockSignals(True)
        for item in self.children():
            item.setSelected(item in self._selected_items)
        self.treeWidget().blockSignals(False)

    def check_selection_change(self):
        selected_items = self.selectedItems()
        if self._selected_items and not selected_items:
            self.enforce_selection()
            return
        if selected_items != self._selected_items:
            self.itemSelectionChanged.emit()
            self._selected_items = selected_items

class SignalsItemDispositivo(QObject):
    activo = pyqtSignal(str)
    browsear = pyqtSignal(object)


class ItemDispositivo(QTreeWidgetItem):
    signals = SignalsItemDispositivo()

    def __init__(self, nombre, id=None, tipo=None, path=None, parent=None):
        super().__init__(parent)
        self.nombre = nombre
        self.id = id
        self.tipo = tipo

        self.chk_usar = QtWidgets.QCheckBox()
        self.chk_usar.setText(nombre)
        self.chk_usar.toggled.connect(self.avisar_chk)

        self._path = None
        if path is not None:  # solamente tienen variable path los de eevee, si no no los setea
            self.path = path

        if tipo == "Eevee":
            self.crear_wgt_eevee()
        else:
            self.treeWidget().setItemWidget(self, 0, self.chk_usar)


    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, valor):
        self._path = valor
        self.chk_usar.setEnabled(bool(valor))
        self.setToolTip(0, valor)

    def crear_wgt_eevee(self):
        wgt_contenedor = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.chk_usar)
        layout.setContentsMargins(5, 4, 5, 4)
        layout.addItem(QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        wgt_contenedor.setLayout(layout)
        btn_buscar_path = QtWidgets.QPushButton(traducir("Set path"))
        btn_buscar_path.clicked.connect(self.browse_path)
        layout.addWidget(btn_buscar_path)
        btn_buscar_path.setToolTip(traducir("tooltip_set_path_eevee"))
        self.treeWidget().setItemWidget(self, 0, wgt_contenedor)

    def browse_path(self):
        self.signals.browsear.emit(self)

    def update_selected(self):
        seleccionado = self.chk_usar.isChecked() and self.parent().isChecked()
        if hasattr(self.parent().parent(), "isChecked"):
            seleccionado = seleccionado and self.parent().parent().isChecked()
        self.setSelected(seleccionado)

    def avisar_chk(self):
        self.update_selected()
        self.signals.activo.emit(self.tipo)

    def isUsed(self):
        return self.chk_usar.isChecked()

    def setUsed(self, used):
        self.chk_usar.setChecked(used)


class ItemOpcionGpus(QTreeWidgetItem):
    def __init__(self, texto, id=None, parent=None):
        super().__init__(parent)
        self.opcion = QtWidgets.QRadioButton()
        self.opcion.setText(texto)
        self.crear_wgt()
        self.id = id if id else texto
        self.setExpanded(True)

    def update_selected(self):
        if not hasattr(self.parent(), "isChecked"):
            return
        self.setSelected(self.isChecked() and self.parent().isChecked())

    def crear_wgt(self):
        wgt = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(5, 4, 5, 4)
        layout.addWidget(self.opcion)
        wgt.setLayout(layout)

        self.treeWidget().setItemWidget(self, 0, wgt)
        # self.treeWidget().setItemWidget(self, 0, self.opcion)

    def text(self, _):
        return self.opcion.text()

    def isChecked(self):
        return self.opcion.isChecked()

    def setChecked(self, checked):
        self.opcion.setChecked(checked)


class VentanaDispositivos(QtWidgets.QDialog, ui.ventana_dispositivos.Ui_ventana_dispositivos):

    def __init__(self, ventana, elegidos=None, tipo=None):
        super().__init__()
        self.setupUi(self)
        self.ventana = ventana

        self.gpuitems_tipos = {}
        # items_tipos = {"cpu": {"item_tipo": item, "items_dispositivos": saraa
        self.gpuitems_eevee = []

        self.item_de_motores = None
        self.item_encontrar = None
        self.opcion_respetar = None
        self.opcion_cycles = None
        self.opcion_eevee = None
        self.configurar_items_padres()

        self.grupo_motores = self.configurar_grupo_motores()
        self.item_cpu = ItemOpcionGpus("CPU", parent=self.opcion_cycles)
        self.gpuitems_tipos["CPU"] = {"item_tipo": self.item_cpu, "items_dispositivos": []}

        self.grupo_tipos_cycles = QtWidgets.QButtonGroup()
        self.grupo_tipos_cycles.addButton(self.item_cpu.opcion)

        estilo_botones = "padding-left: 10px; padding-right: 10px; padding-top: 5px; padding-bottom: 5px;"
        self.btn_encontrar.setStyleSheet(estilo_botones)

        self.tipo_elegido = None

        if self.ventana:
            job = self.ventana.tablaPrincipal.currentItem()
            self.chk_parallel.setChecked(job.parallel_gpu)
            self.elegidos_previos = job.dispositivos
            self.tipo_previo = job.tipo_dispositivos
        elif elegidos and tipo:
            self.elegidos_previos = elegidos
            self.tipo_previo = tipo
        else:
            self.elegidos_previos = self.tipo_previo = None

        self.conectar_acciones_botones()
        self.leer_dispositivos()
        self.toggles_respeto()

        # self.adjustSize()

    def configurar_items_padres(self):

        txt_respetar = traducir("respetar_blender_blend")
        self.opcion_respetar = ItemOpcionGpus(txt_respetar, id="respetar", parent=self.arbol)
        self.opcion_respetar.setChecked(True)
        self.opcion_cycles = ItemOpcionGpus("Cycles", parent=self.arbol)
        self.opcion_eevee = ItemOpcionGpus(texto="Eevee", parent=self.arbol)
        self.item_de_motores = {"Eevee": self.opcion_eevee, "Cycles": self.opcion_cycles,
                                txt_respetar: self.opcion_respetar}

    def configurar_grupo_motores(self):
        grupo_motores = QtWidgets.QButtonGroup()
        grupo_motores.addButton(self.opcion_cycles.opcion)
        grupo_motores.addButton(self.opcion_eevee.opcion)
        grupo_motores.addButton(self.opcion_respetar.opcion)
        grupo_motores.buttonToggled.connect(self.cambio_motor)
        return grupo_motores

    def conectar_acciones_botones(self):
        ItemDispositivo.signals.activo.connect(self.elegir_tipo)
        ItemDispositivo.signals.browsear.connect(self.browse_path)
        self.grupo_tipos_cycles.buttonToggled.connect(self.cambio_tipo_cycles)
        self.grupo_tipos_cycles.buttonPressed.connect(self.toggles_automaticos)
        self.btn_encontrar.clicked.connect(self.encontrar_dispositivos)
        self.aceptar_cancelar.accepted.connect(self.aceptar)
        self.aceptar_cancelar.rejected.connect(self.close)
        self.btn_distribuir.pressed.connect(self.distribuir)
        self.btn_distribuir.setToolTip(traducir("distribuir_dispositivos"))
        self.opcion_respetar.opcion.toggled.connect(self.toggles_respeto)
        atajo_cancelar_busqueda = QtWidgets.QShortcut(QtGui.QKeySequence('Esc'), self)
        atajo_cancelar_busqueda.activated.connect(self.cancelar_busqueda)
        gpus.reportar_hallazgos.connect(self.termino_busqueda)

    def toggles_respeto(self):
        self.chk_parallel.setEnabled(not self.opcion_respetar.isChecked())

    def cambio_motor(self, opcion):
        motor = opcion.text()
        tipo = motor
        if motor == "Cycles":
            btn = self.grupo_tipos_cycles.checkedButton()
            if btn and btn.text():
                tipo = btn.text()
        self.toggleos_segun_elegidos(tipo)

        for motor_i in self.item_de_motores:
            item_motor = self.item_de_motores[motor_i]
            item_motor.setSelected(motor_i == motor)
            self.update_selection_recursivo(item_motor)

    def update_selection_recursivo(self, item):
        for i in range(item.childCount()):
            item.child(i).update_selected()
            self.update_selection_recursivo(item.child(i))

    def elegir_tipo(self, tipo):
        self.toggleos_segun_elegidos(tipo)
        if tipo == "Eevee":
            self.opcion_eevee.setChecked(True)
            return
        self.opcion_cycles.setChecked(True)

        self.opcion_cycles.setSelected(True)
        self.gpuitems_tipos[tipo]["item_tipo"].opcion.setChecked(True)
        self.gpuitems_tipos[tipo]["item_tipo"].setSelected(True)

    def distribuir(self):
        if not self.tipo_elegido_actual():
            return
        tipo_elegido = self.tipo_elegido_actual()
        num_items_elegidos = len(self.ventana.tablaPrincipal.selectedItems())

        elegidos = [item for item in self.gpuitems_tipos[tipo_elegido]["items_dispositivos"] if item.isUsed()]

        if not elegidos:
            return

        num_dispositivos_elegidos = len(elegidos)

        for i in range(num_items_elegidos):
            item_i = self.ventana.tablaPrincipal.selectedItems()[i]
            if item_i.estado == "terminado":
                item_i.reset()
            indice_distribucion = i % num_dispositivos_elegidos
            dispositivo_i = elegidos[indice_distribucion]
            item_i.nombres_dispositivos = "(" + tipo_elegido + ") " + dispositivo_i.nombre
            item_i.dispositivos = [dispositivo_i.id]
            item_i.tipo_dispositivos = tipo_elegido
            item_i.propiedades_argumentar.add("dispositivos")

        self.cierre_positivo()

    def cierre_positivo(self):
        if self.ventana.item_unico_elegido():
            item_activo = self.ventana.item_unico_elegido()
        else:
            item_activo = self.ventana.tablaPrincipal.currentItem()
        if item_activo:
            self.ventana.tablaPrincipal.setCurrentItem(item_activo,
                                                       self.ventana.columna["nombres_dispositivos"])
        indice_scroll = self.ventana.tablaPrincipal.currentIndex()
        self.ventana.tablaPrincipal.scrollTo(indice_scroll)
        colas.guardar()
        self.close()

    def cancelar_busqueda(self):
        try:
            gpus.infos_blender.proceso_blender.kill()
        except AttributeError:
            pass

    def limpiar_items_dispositivos(self):
        items_gpus_cycles = [data["item_tipo"] for tipo, data in self.gpuitems_tipos.items() if tipo != "CPU"]
        for item in items_gpus_cycles:
            self.opcion_cycles.removeChild(item)

        for item in self.gpuitems_eevee:
            self.opcion_eevee.removeChild(item)

        self.gpuitems_tipos = {"CPU": {"item_tipo": self.item_cpu, "items_dispositivos": []}}
        self.gpuitems_eevee = []

    def leer_dispositivos(self):
        self.limpiar_items_dispositivos()

        if gpus.ya_leyo:
            self.termino_lectura(True)
            return
        gpus.leer_archivos_dispositivos()

    def termino_lectura(self, encontro_dispositivos):
        if encontro_dispositivos:
            self.rellenar_listado()

    def encontrar_dispositivos(self):
        self.limpiar_items_dispositivos()
        gpus.encontrar_dispositivos_disponibles()

    def termino_busqueda(self, encontro_dispositivos):
        if not encontro_dispositivos:
            self.alertar()
            return
        self.rellenar_listado()

    def rellenar_listado(self):
        tipos_gpu = [tipo for tipo in gpus.cycles_por_tipo if tipo != "CPU"]
        nombre_cpu = [nombre for nombre in gpus.cycles_por_tipo["CPU"].keys()][0]
        id_cpu = 'CPU'

        for tipo in tipos_gpu:
            item_tipo = ItemOpcionGpus(tipo, parent=self.opcion_cycles)
            self.grupo_tipos_cycles.addButton(item_tipo.opcion)
            self.gpuitems_tipos[tipo] = {"item_tipo": item_tipo, "items_dispositivos": []}

            for nombre in gpus.cycles_por_tipo[tipo]:
                for id in gpus.cycles_por_tipo[tipo][nombre]:
                    nombre_unico = gpus.nombre_unico_para_id(id)
                    item_i = ItemDispositivo(nombre_unico, id, tipo, parent=item_tipo)
                    self.gpuitems_tipos[tipo]["items_dispositivos"].append(item_i)

            cpu_i = ItemDispositivo(nombre_cpu, id_cpu, tipo=tipo, parent=item_tipo)
            self.gpuitems_tipos[tipo]["items_dispositivos"].append(cpu_i)

        for disp in gpus.nombres_unicos.values():
            path = gpus.gpus_eevee[disp] if disp in gpus.gpus_eevee else ""
            item_i = ItemDispositivo(disp, tipo="Eevee", path=path, parent=self.opcion_eevee)
            self.gpuitems_eevee.append(item_i)

        self.elegir_elegidos()

    def elegir_elegidos(self):
        if not (self.elegidos_previos and self.tipo_previo):
            return
        if self.tipo_previo in self.gpuitems_tipos:
            self.elegir_tipo(self.tipo_previo)
            for item_disp in self.gpuitems_tipos[self.tipo_previo]["items_dispositivos"]:
                item_disp.setUsed(item_disp.id in self.elegidos_previos)
        elif self.tipo_previo == "Eevee":
            for item_disp in self.gpuitems_eevee:
                item_disp.setUsed(item_disp.nombre in self.elegidos_previos)

    def toggles_automaticos(self, opcion):
        tipo_elegido = opcion.text() if opcion and opcion.text() in self.gpuitems_tipos else None
        if not tipo_elegido:
            self.tipo_elegido = None
            return
        if tipo_elegido == self.tipo_elegido:
            habia_inusados = False
            for item_dispositivo in self.gpuitems_tipos[tipo_elegido]["items_dispositivos"]:
                if not item_dispositivo.isUsed():
                    item_dispositivo.setUsed(True)
                    habia_inusados = True

            if not habia_inusados:
                for item_dispositivo in self.gpuitems_tipos[tipo_elegido]["items_dispositivos"][1:]:
                    item_dispositivo.setUsed(False)
        else:
            ninguno_usado = True
            for item_dispositivo in self.gpuitems_tipos[tipo_elegido]["items_dispositivos"]:
                if item_dispositivo.isUsed():
                    ninguno_usado = False
                    break
            if ninguno_usado:
                for item_dispositivo in self.gpuitems_tipos[tipo_elegido]["items_dispositivos"]:
                    item_dispositivo.setUsed(True)

        self.tipo_elegido = tipo_elegido

    def cambio_tipo_cycles(self, opcion):
        tipo_elegido = opcion.text() if opcion and opcion.text() in self.gpuitems_tipos else None

        self.toggleos_segun_elegidos(tipo_elegido)
        self.opcion_cycles.setChecked(True)
        self.update_selection_recursivo(self.opcion_cycles)

    def conteo_elegidos(self, tipo):
        if tipo not in self.gpuitems_tipos and tipo != "Eevee":
            return 1
        conjunto = self.gpuitems_eevee if tipo == "Eevee" else self.gpuitems_tipos[tipo]["items_dispositivos"]
        elegidos = sum(1 for x in conjunto if x.isUsed())
        return elegidos

    def toggleos_segun_elegidos(self, tipo):
        if self.opcion_cycles.isChecked():
            if self.item_cpu.isChecked():
                self.btn_distribuir.setEnabled(False)
                self.aceptar_cancelar.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
                return
            if not self.grupo_tipos_cycles.checkedButton():
                self.btn_distribuir.setEnabled(False)
                self.aceptar_cancelar.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
                return
        if tipo == "Cycles":
            if not self.grupo_tipos_cycles.checkedButton():
                return
            tipo = self.grupo_tipos_cycles.checkedButton().text()
        elegidos = self.conteo_elegidos(tipo)

        self.aceptar_cancelar.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(elegidos)
        self.btn_distribuir.setEnabled(elegidos > 1 and self.ventana is not None)

    def tipo_elegido_actual(self):
        opcion = self.grupo_tipos_cycles.checkedButton()
        return opcion.text() if opcion and opcion.text() in self.gpuitems_tipos else None

    def alertar(self):
        alertas.alerta_generica("Error averiguando dispositivos")

    def aceptar(self):
        items = self.ventana.tablaPrincipal.selectedItems()
        for item in items:
            if item.estado != "terminado":
                continue
            item.reset()

        if self.opcion_respetar.isChecked():
            self.no_usar_gpu(items)
            motor = False
        elif self.opcion_cycles.isChecked():
            self.usar_elegidos_cycles(items)
            motor = "Cycles"
        else:
            self.usar_elegidos_eevee(items)
            motor = "Eevee"


        self.cierre_positivo()



    def usar_elegidos_cycles(self, items):
        tag_parallel = " " + traducir("Parallel GPU") if self.chk_parallel.isChecked() else ""
        prefijo = "[Cycles{}]".format(tag_parallel)
        tipo_elegido = self.tipo_elegido_actual()
        if tipo_elegido == "CPU":
            parallel_gpu = self.chk_parallel.isChecked()
            self.aux_aplicar_dispositivos_a_items(items, prefijo + " CPU", "CPU", [], parallel_gpu)
            return

        prefijo += " ({}) ".format(tipo_elegido)
        nombres, lista_ids = self.crear_lista_ids_nombres(prefijo, [], tipo_elegido)

        parallel_gpu = self.chk_parallel.isChecked()

        self.aux_aplicar_dispositivos_a_items(items, nombres, tipo_elegido, lista_ids, parallel_gpu)

    def crear_lista_ids_nombres(self, nombres, lista_ids, tipo_elegido):
        for disp_i in self.gpuitems_tipos[tipo_elegido]["items_dispositivos"]:
            if not disp_i.isUsed():
                continue
            nombres += disp_i.nombre + ", "
            lista_ids.append(disp_i.id)

        return nombres, lista_ids

    def usar_elegidos_eevee(self, items):
        usados = [item.nombre for item in self.gpuitems_eevee if item.isUsed()]
        parallel_gpu = self.chk_parallel.isChecked()
        tag_parallel = " " + traducir("Parallel GPU") if self.chk_parallel.isChecked() else ""
        nombres = "[Eevee{}] ".format(tag_parallel) + ", ".join(usados)
        tipo = "Eevee"
        self.aux_aplicar_dispositivos_a_items(items, nombres, tipo, usados, parallel_gpu)

    def aux_aplicar_dispositivos_a_items(self, items, lista_nombres, tipos_dispositivos, lista_ids, parallel_gpu):
        for item_i in items:
            item_i.nombres_dispositivos = lista_nombres.strip(", ")
            item_i.tipo_dispositivos = tipos_dispositivos
            item_i.dispositivos = lista_ids
            item_i.propiedades_argumentar.add('dispositivos')
            item_i.parallel_gpu = parallel_gpu

    def no_usar_gpu(self, items):
        for item_i in items:
            item_i.nombres_dispositivos = ''
            item_i.tipo_dispositivos = ''
            item_i.dispositivos = []
            item_i.propiedades_argumentar.discard("dispositivos")
            item_i.parallel_gpu = False

    def browse_path(self, item):
        path_elegido = blenders.explorar(self, versiones_blender.ruta_default)
        if not blenders.ruta_es_valida(path_elegido):
            return
        item.path = path_elegido
        gpus.gpus_eevee[item.nombre] = item.path
        gpus.guardar_archivo_dispositivos()

    def retranslateUi(self, _):
        self.setWindowTitle(traducir("Dispositivos de render"))
        self.btn_distribuir.setText(traducir("Distribuir"))
        texto_encontrar = traducir("averiguar_dispositivos")
        self.btn_encontrar.setText(texto_encontrar)
        self.chk_parallel.setText(traducir("parallel_gpu"))
        self.chk_parallel.setToolTip(traducir("tooltip_parallel_gpu"))


class VentanaNombrado(QtWidgets.QDialog, ui.ventana_nombrado.Ui_ventana_nombrado):
    def __init__(self, ventana, pre_preset=None, item=None, habilitar_token=""):
        super().__init__()

        self.setupUi(self)
        self.ventana = ventana

        self.item_default_watchfolders = None
        self.item_default_viewlayers = None
        self.item_default_camaras = None
        self.item_campo_nombre_preset_b = None
        self.item_campo_nombre_preset_a = None
        self.item_chk_guardar_preset = None
        self.chk_aplicar_nodos = None
        self.chk_aplicar_default = None
        self.aplico = False
        self.item_opcion = {}

        self.configurar_token_zones()

        self.item = item

        if isinstance(item, ItemFantasma):
            self.wgt_preview.hide()

        self.pre_preset = pre_preset
        auto_nombrado.leer_archivo_presets()

        self.lbl_aux_preview_aj.setVisible(len(self.ventana.tablaPrincipal.selectedItems())>1)
        self.configurar_arbol()
        self.nombres_botones_desactivables = {"collection", "view_layer", "camara"}
        self.nombres_botones_desactivables.discard(habilitar_token)
        self.botones_desactivables = {}

        self.botones_con_conteo = ["collection"]
        self.mostrar_botones("dragueable", auto_nombrado.tokens, self.layout_tokens)

        self.mostrar_botones("preset", auto_nombrado.presets, self.layout_presets)
        self.btn_explorar.inicializar(self.browse_ruta)
        self.configurar_items_arbol()

        self.boton_aceptar_cancelar.accepted.connect(self.aceptar)
        self.boton_aceptar_cancelar.rejected.connect(self.close)

        # self.nombre_output.textChanged.connect(self.usar_patron)
        # self.ruta_output.textChanged.connect(self.usar_patron)

        self.grupo_opciones_base.buttonToggled.connect(self.resaltar_opcion_elegida)

        auto_nombrado.emisor.output_preview_signal.connect(self.rellenar_preview)
        self.leer_previos()

        self.cambio_algo = False

        self.keyPressEvent = self.handle_enter_key

        self.selector_separador.setStyleSheet("""
    QComboBox {
        padding-left: 5px; padding-right: 0px; padding-top: 2px; padding-bottom: 2px;/* Padding when closed */
    }
""")
        self.selector_separador.currentIndexChanged.connect(self.interaccion_patron)



    def handle_enter_key(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.actualizar_preview()
            self.boton_aceptar_cancelar.setFocus()
            # event.ignore()
        else:
            QtWidgets.QDialog.keyPressEvent(self, event)

    def configurar_token_zones(self):
        self.wgt_borrador_path.setContentsMargins(0,0,0,0)
        alto_minimo_borradores = self.wgt_borrador_path.height()
        self.wgt_aux_borrar_path.setContentsMargins(0, 0, 0, 0)
        self.wgt_aux_borrar_path.setContentsMargins(0, 0, 0, 0)
        self.wgt_aux_borrar_name.setFixedHeight(alto_minimo_borradores)
        self.wgt_aux_borrar_path.setFixedHeight(alto_minimo_borradores)
        self.wgt_patron_path.set_boton_borrar(self.wgt_borrador_path)
        self.wgt_patron_name.set_boton_borrar(self.wgt_borrador_name)
        self.wgt_patron_path.cambio.connect(self.interaccion_patron)
        self.wgt_patron_name.cambio.connect(self.interaccion_patron)

    def conectar_segnales(self):
        pass

    @property
    def separador(self):
        return self.selector_separador.currentText()


    def leer_previos(self):
        item_modelo = self.item if self.item else self.ventana.item_unico_elegido() if self.ventana.item_unico_elegido() else \
            self.ventana.tablaPrincipal.currentItem()

        attributes = ["ruta", "nombre", "aplicar_a", "separador"]
        if self.pre_preset:
            ruta, nombre, aplicar_a, separador = [getattr(self.pre_preset, attr, "") for attr in attributes]
        elif item_modelo:
            ruta, nombre, aplicar_a, separador = [item_modelo.patron_nombrado.get(attr, "") for attr in attributes]
        else:
            aplicar_a = auto_nombrado.default_aplicar_a
            ruta = ""
            nombre = ""
            separador = ""

        separador = separador if separador in auto_nombrado.separadores else ItemCola.default_patron_nombrado["separador"]
        aplicar_a = aplicar_a if aplicar_a in iter(auto_nombrado.AplicarA) else auto_nombrado.default_aplicar_a

        self.selector_separador.setCurrentText(separador)
        self.actualizar_chks_aplicar_a(aplicar_a)

        for _, boton in self.botones_desactivables.items():
            if boton.token in auto_nombrado.tokens_propiedad_item:
                resultado = boton.token.resultado(item_modelo)
                boton.setEnabled(bool(resultado))

        if not any([ruta, nombre]):
            return

        self.opc_usar_patron.setChecked(True)
        self.load_patron_completo(ruta, nombre)
        # self.ruta_output.setText(ruta)
        # self.nombre_output.setText(nombre)


    def actualizar_chks_aplicar_a(self, aplicar_a):
        self.chk_aplicar_default.setChecked(aplicar_a in auto_nombrado.aplicar_a_incluye_escena)
        self.chk_aplicar_nodos.setChecked(aplicar_a in auto_nombrado.aplicar_a_incluye_nodos)

    def toggle_aplicar_a_seguro(self, toggle):
        if toggle:
            return
        for item in [self.chk_aplicar_default, self.chk_aplicar_nodos]:
            if self.sender() != item.chk:
                item.chk.setChecked(True)

    def ejecutar_para_item(self):
        self.exec_()
        return self.aplico

    def browse_ruta(self):
        txt_ruta = self.wgt_patron_path.text()
        if txt_ruta and Path(txt_ruta).exists():
            browser = QFileDialog.getExistingDirectory(directory=txt_ruta)
        else:
            browser = QFileDialog.getExistingDirectory()

        if browser:
            self.partir_ruta_y_mostrar(browser)

    def partir_ruta_y_mostrar(self, ruta):
        # Create a Path object
        p = Path(ruta)

        # Initialize an empty list to hold the formatted path parts
        path_parts = []

        # Handle the drive and root folder for Windows
        if p.drive:
            # Combine drive and the first part
            path_parts.append(p.drive + os.sep + p.parts[1])  # e.g., "C:/sarasa"
            # Add the remaining parts with leading separators
            for part in p.parts[2:]:
                path_parts.append(os.sep + part)  # Use os.sep for consistency
        else:
            # For Linux paths, just add the first part as root folder
            if p.parts:
                path_parts.append(os.sep + p.parts[1])  # e.g., "/home"
                # Add the remaining parts
                for part in p.parts[2:]:
                    path_parts.append(os.sep + part)  # Use os.sep for consistency
        if not path_parts:
            return
        self.wgt_patron_path.clear()
        for parte in path_parts:
            self.wgt_patron_path.agregar_editable(parte)
        self.interaccion_patron()


    def interaccion_patron(self):
        self.opc_usar_patron.setChecked(True)
        self.actualizar_preview()


    def mostrar_botones(self, tipo_widget, botones, layout):
        i = 0
        columnas = 3
        for boton_i in botones:
            columna_i, fila_i = divmod(i, columnas)
            i += 1
            if tipo_widget == "dragueable":
                if boton_i in self.botones_con_conteo:
                    elemento_i = WidgetTokenIncremental(botones[boton_i], self)
                else:
                    elemento_i = WidgetToken(botones[boton_i], self)
                if boton_i in self.nombres_botones_desactivables:
                    self.botones_desactivables.update({boton_i: elemento_i})
                elemento_i.setText(botones[boton_i].nombre_visible)
                elemento_i.setToolTip("\n".join(traducir(tooltip) for tooltip in botones[boton_i].tooltips))
            elif tipo_widget == "preset":
                elemento_i = BotonPreset(i - 1, botones[i - 1], self)
                elemento_i.clicked.connect(self.aplicar_preset)
            else:
                return
            layout.addWidget(elemento_i, columna_i, fila_i)


    def aplicar_preset(self):
        preset = self.sender().preset
        self.selector_separador.setCurrentText(preset.separador)
        self.actualizar_chks_aplicar_a(preset.aplicar_a)
        self.load_patron_completo(preset.ruta, preset.nombre)
        for chk, uso in self.iter_defaults_preset():
            chk.setChecked(uso in preset.default_para)
        nombre = preset.nombre_visible
        try:
            nombre_a, nombre_b = nombre.split("\n", 1)  # Split only at the first newline
        except ValueError:
            # If there's no newline, handle it by assigning default values
            nombre_a = nombre  # Use the whole string as `nombre_a`
            nombre_b = ""  # Assign an empty string to `nombre_b`

        self.item_campo_nombre_preset_a.setText(nombre_a)
        self.item_campo_nombre_preset_b.setText(nombre_b)


    def numero_aplicar_a(self):
        apply_to_escena = self.chk_aplicar_default.isChecked()
        apply_to_nodos = self.chk_aplicar_nodos.isChecked()

        if apply_to_escena and apply_to_nodos:
            return auto_nombrado.AplicarA.Todo
        elif apply_to_escena:
            return auto_nombrado.AplicarA.Escena
        elif apply_to_nodos:
            return auto_nombrado.AplicarA.Nodos

    def get_patron(self):
        ruta = get_parte_patron(self.wgt_patron_path)
        nombre = get_parte_patron(self.wgt_patron_name)

        aplicar_a = self.numero_aplicar_a()
        patron = {"aplicar_a": aplicar_a, "ruta": ruta, "nombre": nombre, "ruta_nodos": ruta, "nombre_nodos": nombre,
                  "separador": self.separador}

        return patron

    def load_patron_completo(self, path, name):
        self.wgt_patron_path.clear()
        self.wgt_patron_name.clear()
        self.load_patron_parte(path, self.wgt_patron_path)
        self.load_patron_parte(name, self.wgt_patron_name)
        self.interaccion_patron()

    def load_patron_parte(self, patron, token_zone):
        if isinstance(patron, str): # ignorar los legacy
            # token_zone.agregar_editable(patron)
            return

        for parte in patron:
            if isinstance(parte, list):
                token, key = parte
                token = auto_nombrado.BaseTokenNombrado.token_por_patron(token)
                if not token:
                    continue
                token_zone.agregar_incremental_de_token(token, key)
            else:
                token = auto_nombrado.BaseTokenNombrado.token_por_patron(parte)
                if token:
                    token_zone.agregar_comun_de_token(token)
                else:
                    token_zone.agregar_editable(parte)

    def actualizar_preview(self):
        item_modelo = self.item if self.item else self.ventana.item_unico_elegido() if self.ventana.item_unico_elegido() else \
            self.ventana.tablaPrincipal.currentItem()
        patron = self.get_patron()
        auto_nombrado.previsualizar(item_modelo, patron)

    def rellenar_preview(self, texto):
        self.campo_preview.setText(texto)


    def aceptar(self):
        if self.item_chk_guardar_preset.isChecked():
            guardo_preset = self.guardar_preset()
            if not guardo_preset:
                return

        if self.cambio_algo:
            for item in self.ventana.tablaPrincipal.selectedItems():
                item.reset()

        if not self.opc_usar_patron.isChecked():
            if self.item:
                return
            for item_i in self.ventana.tablaPrincipal.selectedItems():
                item_i.propiedades_argumentar.discard("nombrado")
                item_i.patron_nombrado = ItemCola.default_patron_nombrado
                item_i.nombrado = None
            colas.guardar()
            self.close()
            return

        patron = self.get_patron()
        if self.item:
            self.item.patron_nombrado = patron
            self.aplico = True
        else:
            for item_i in self.ventana.tablaPrincipal.selectedItems():
                item_i.patron_nombrado = patron
                auto_nombrado.aplicar(item_i)
                item_i.propiedades_argumentar.add("nombrado")

        colas.guardar()
        self.close()

    def iter_defaults_preset(self):
        for chk, uso in zip([self.item_default_camaras, self.item_default_viewlayers, self.item_default_watchfolders],
                            ["camaras", "view_layers", "watchfolders"]):
            yield chk, uso

    def guardar_preset(self):
        nombre_completo = "\n".join([self.item_campo_nombre_preset_a.text(), self.item_campo_nombre_preset_b.text()]).rstrip()
        for i, preset_previo in enumerate(auto_nombrado.presets):
            if preset_previo.nombre_visible == nombre_completo:
                alerta = alertas.alerta_cancelable(traducir("Atención!"), traducir("nombre_preset_duplicado"),
                                                   con_ok=True,
                                                   icono=QMessageBox.Warning)
                decision = alerta.exec_()
                reemplazar = decision == QMessageBox.Ok
                if reemplazar: # reem
                    auto_nombrado.presets.pop(i)
                    break
                else:
                    return False

        patron = self.get_patron()
        default_para = set()
        for chk, uso in self.iter_defaults_preset():
            if chk.isChecked():
                default_para.add(uso)
        default_para = default_para or None
        custom_preset = auto_nombrado.PresetNombrado(patron["ruta"], patron["nombre"], patron["separador"],
                                                     nombre_completo,
                                                     patron["aplicar_a"], default_para)
        auto_nombrado.agregar_custom_preset(custom_preset, default_para)
        return True

    def retranslateUi(self, _):
        self.setWindowTitle(traducir("Output Filepath"))
        self.lbl_path.setText(traducir("Ruta"))
        self.lbl_name.setText(traducir("Nombre"))
        self.opc_usar_patron.setText(traducir("usar_patron_salida"))
        self.opc_usar_original.setText(traducir("usar_output_original"))
        self.lbl_separador.setText(traducir("Separator"))
        self.lbl_preview.setText(traducir("Preview"))
        self.lbl_aux_preview_aj.setText("(" + traducir("preview_job") + ")")

    def configurar_arbol(self):
        # self.arbol.setAlternatingRowColors(True)
        self.arbol.setHeaderHidden(True)
        self.arbol.setIndentation(15)
        self.arbol.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.arbol.setFocusPolicy(Qt.NoFocus)
        self.arbol.setTransparente()

    def resaltar_opcion_elegida(self, boton, estado):
        nombre = boton.objectName()
        if nombre not in self.item_opcion:
            return
        self.item_opcion[boton.objectName()].setSelected(estado)

    def configurar_items_arbol(self):
        item_opcion_original = ItemWidgetBasico(self.arbol)
        item_opcion_original.agregar_wgt(0, self.opc_usar_original, spacerR=True)
        item_opcion_patron = ItemWidgetBasico(parent=self.arbol)
        item_opcion_patron.agregar_wgt(0, self.opc_usar_patron, spacerR=True)
        item_opcion_patron.setExpanded(True)
        self.item_opcion["opc_usar_original"] = item_opcion_original
        self.item_opcion["opc_usar_patron"] = item_opcion_patron

        item_titulo_presets = ItemTitulo(traducir("Presets"), parent=item_opcion_patron)
        item_presets = ItemWidgetBasico(item_titulo_presets)
        item_presets.agregar_wgt(0, self.wgt_presets, spacerL=True, spacerR=True)


        item_aplicar_a = ItemTitulo(traducir("Apply to"), parent=item_opcion_patron)
        self.chk_aplicar_default = ItemChk(traducir("Scene output path"), parent=item_aplicar_a,
                                           handle_toggle=False)
        self.chk_aplicar_default.chk.toggled.connect(self.toggle_aplicar_a_seguro)

        self.chk_aplicar_nodos = ItemChk(traducir("File output nodes"), parent=item_aplicar_a,
                                         handle_toggle=False)
        self.chk_aplicar_nodos.chk.toggled.connect(self.toggle_aplicar_a_seguro)

        item_titulo_tokens = ItemTitulo(traducir("Tokens") + " " + traducir("(drag and drop)"),
                                        parent=item_opcion_patron)
        item_tokens = ItemWidgetBasico(item_titulo_tokens)
        item_tokens.agregar_wgt(0, self.wgt_tokens, spacerL=True, spacerR=True)
        item_tokens.setFirstColumnSpanned(True)

        # ItemCustomWidget(item_opcion_patron, self.linea_divisora)

        item_titulo_patron = ItemTitulo(traducir("Patron"), parent=item_opcion_patron)
        # item_titulo_patron.setFirstColumnSpanned(True)
        item_patron = ItemWidgetBasico(item_titulo_patron)
        item_patron.agregar_wgt(0, self.wgt_patron)

        self.item_chk_guardar_preset = ItemChk(traducir("guardar_como_preset"), parent=item_opcion_patron)

        item_nombre_preset = ItemTitulo(traducir("Nombre"), parent=self.item_chk_guardar_preset)
        self.item_campo_nombre_preset_a = ItemLinea("", columna=0, parent=item_nombre_preset)
        self.item_campo_nombre_preset_a.linea.setMaximumWidth(160)
        self.item_campo_nombre_preset_b = ItemLinea("", columna=0, parent=item_nombre_preset)
        self.item_campo_nombre_preset_b.linea.setMaximumWidth(160)
        item_defaultear_preset = ItemTitulo(traducir("Establecer como default"), parent=self.item_chk_guardar_preset)
        self.item_default_camaras = ItemChk(traducir("Para cámaras"), parent=item_defaultear_preset)
        self.item_default_viewlayers = ItemChk(traducir("Para viewlayers"), parent=item_defaultear_preset)
        self.item_default_watchfolders = ItemChk(traducir("Para watchfolders"), parent=item_defaultear_preset)

        self.selector_separador.traduccion = traduccion

        self.selector_separador.addItems(auto_nombrado.separadores)

        item_titulo_tokens.setExpanded(True)
        item_titulo_patron.setExpanded(True)



    def encontrar_nodos_output(self):
        Datas.crear_script(Datas.ruta_script_leer_fileoutputs, Datas.script_leer_file_outputs)
        item = self.ventana.item_unico_elegido()
        if not item:
            return
        argumentos = ['-b', item.ruta_blend_completa]
        escena = item.escena
        if escena:
            argumentos.extend(["-S", escena])
        argumentos.extend(['--factory-startup', '-P', Datas.ruta_script_leer_fileoutputs])
        self.infos_blender = InfosBlender(self.leer_nodos_output, debug=True)
        self.infos_blender.correr_blender(argumentos)

    def leer_nodos_output(self, data_blender):
        nodos = []
        for data in data_blender.splitlines():
            if data.startswith(Datas.prefijo_nodos_output):
                nodos = json.loads(data.removeprefix(Datas.prefijo_nodos_output))
                break

    def mostrar_nodos_output(self, nodos):
        pass



class BrowserRutaOutput(QFileDialog):
    def __init__(self):
        super().__init__()
        self.setOption(QFileDialog.DontUseNativeDialog)
        self.setFileMode(QFileDialog.Directory)
        self.setAcceptMode(QFileDialog.AcceptSave)
        self.chk_relative = QtWidgets.QCheckBox(traducir("Relativo"))
        spacer = QtWidgets.QSpacerItem(40, 20)
        spacer2 = QtWidgets.QSpacerItem(40, 20)

        self.layout().addItem(spacer)
        self.layout().addItem(spacer2)
        self.layout().addWidget(self.chk_relative)


# class WidgetConsola(QtWidgets.QWidget, ui.widget_consola.Ui_widget_consola):
#     def __init__(self, ventana_madre):
#         super().__init__()
#         self.setupUi(self)
#
#     def ensureCursorVisible(self):
#         self.info_consola.ensureCursorVisible()
#
#     def setPlainText(self, texto):
#         self.info_consola.setPlainText(texto)
#
#     def appendPlainText(self, texto):
#         self.info_consola.appendPlainText(texto)

class WidgetNombrado(QtWidgets.QWidget, ui.widget_nombrado.Ui_widget_nombrado):
    def __init__(self, ventana_madre, item):
        super().__init__()

        try:
            self.nombrado_aplicar_a = item.patron_nombrado["aplicar_a"]
            self.separador = item.patron_nombrado["separador"]
        except (AttributeError, TypeError, KeyError):
            self.nombrado_aplicar_a = auto_nombrado.default_aplicar_a
            self.separador = auto_nombrado.separadores[0]
        self.setupUi(self)
        self.opcion_no_cambiar.setChecked(True)
        self.selector_preset.cambio.connect(self.usar_preset)
        self.selector_preset.cambio.connect(self.mostrar_patron_preset)
        self.opcion_no_cambiar.toggled.connect(self.no_cambiar)
        self.btn_opciones_nombrado.clicked.connect(self.nombrado_custom)
        self.ventana_madre = ventana_madre

        self.item = item
        self.patron_ruta = item.patron_nombrado["ruta"]
        self.patron_nombre = item.patron_nombrado["nombre"]

        item_nombrado_respetar = QTreeWidgetItem(self.arbol)
        item_nombrado_preseet = QTreeWidgetItem(self.arbol)
        item_nombrado_custom = QTreeWidgetItem(self.arbol)
        item_nombrado_output_path = QTreeWidgetItem(self.arbol)
        self.arbol.setItemWidget(item_nombrado_respetar, 0, self.wgt_output_respetar)
        self.arbol.setItemWidget(item_nombrado_preseet, 0, self.wgt_output_preset)
        self.arbol.setItemWidget(item_nombrado_preseet, 1, self.wgt_selector_presets)
        self.arbol.setItemWidget(item_nombrado_custom, 0, self.wgt_output_custom)
        self.arbol.setItemWidget(item_nombrado_custom, 1, self.wgt_editar_custom)
        self.arbol.setItemWidget(item_nombrado_output_path, 0, self.wgt_output_path)
        self.arbol.setFirstItemColumnSpanned(item_nombrado_output_path, True)

        self.arbol.desactivar_seleccion()

        self.opcion_usar_preset.toggled.connect(self.mostrar_patron_preset)

    def setDisabled(self, disabled):
        for wgt in [self.wgt_output_custom, self.wgt_output_path, self.wgt_output_preset,
                    self.wgt_output_respetar]:
            wgt.setDisabled(disabled)

    def setEnabled(self, enabled):
        for wgt in [self.wgt_output_custom, self.wgt_output_path, self.wgt_output_preset,
                    self.wgt_output_respetar]:
            wgt.setEnabled(enabled)


    def no_cambiar(self):
        if self.opcion_no_cambiar.isChecked():
            self.muestra_ruta.setText("")
            self.muestra_nombre.setText("")

    def usar_preset(self):
        self.opcion_usar_preset.setChecked(True)

    def mostrar_patron_preset(self, toggle):
        if not (toggle and self.selector_preset.currentData()):
            return
        self.patron_ruta = self.selector_preset.currentData().ruta
        self.patron_nombre = self.selector_preset.currentData().nombre
        self.muestra_ruta.setText(auto_nombrado.patron_a_string(self.patron_ruta))
        self.muestra_nombre.setText(auto_nombrado.patron_a_string(self.patron_nombre))

    def rellenar_presets(self, categoria=""):
        self.selector_preset.blockSignals(True)
        self.selector_preset.clear()
        presets = auto_nombrado.presets.copy()
        for i, preset in enumerate(presets):
            print("categoria", categoria, "default  para", preset.default_para) # debug print
            if categoria in preset.default_para:
                presets.insert(0, presets.pop(i))
                break

        for preset in presets:
            self.selector_preset.addItem(preset.nombre_visible, preset)

        self.selector_preset.setCurrentText(presets[0].nombre_visible)
        self.selector_preset.blockSignals(False)
        if self.opcion_usar_preset.isChecked():
            self.mostrar_patron_preset(True)

    def nombrado_custom(self):
        preset = self.selector_preset.currentData() if self.opcion_usar_preset.isChecked() else None
        token_habil = getattr(self.ventana_madre, "propiedad_variante", "")
        categoria = getattr(self.ventana_madre, "propiedad_variantes", "")
        ventana_nombrado = VentanaNombrado(self.ventana_madre.ventana, preset, self.item, token_habil)
        uso_nombrado_avanzado = ventana_nombrado.ejecutar_para_item()
        self.rellenar_presets(categoria)
        if uso_nombrado_avanzado:
            self.opcion_custom.setChecked(True)
            self.patron_ruta = self.item.patron_nombrado["ruta"]
            self.patron_nombre = self.item.patron_nombrado["nombre"]

            self.muestra_ruta.setText(auto_nombrado.patron_a_string(self.patron_ruta))
            self.muestra_nombre.setText(auto_nombrado.patron_a_string(self.patron_nombre))
            self.nombrado_aplicar_a = self.item.patron_nombrado["aplicar_a"]
            self.separador = self.item.patron_nombrado["separador"]

    def patron_custom(self):
        return {"aplicar_a": self.nombrado_aplicar_a, "ruta": self.patron_ruta,
                "nombre": self.patron_nombre, "separador": self.separador}

    def retranslateUi(self, _):
        self.opcion_usar_preset.setText(traducir("usar_preset_nombrado"))
        self.opcion_custom.setText(traducir("Nombrado customizado"))
        self.opcion_no_cambiar.setText(traducir("No cambiar"))
        self.btn_opciones_nombrado.setText(traducir("Configurar"))
        self.lbl_ruta.setText(traducir("Ruta"))
        self.lbl_nombre.setText(traducir("Nombre"))


class VentanaVariantes(QtWidgets.QDialog, ui.ventana_variantes.Ui_ventana_variantes):
    def __init__(self, ventana, grupo_nombrado=True):
        # super().__init__()
        QtWidgets.QDialog.__init__(self)
        ui.ventana_variantes.Ui_ventana_variantes.__init__(self)

        self.ha_leido = False
        self.permitir_loop_recabando = True
        self.grupo_nombrado = None
        self.setupUi(self)

        self.leer = False

        self.wgt_compositing.hide()

        self.acomodar_ventana()
        self.ventana = ventana
        self.items_elegidos = self.ventana.tablaPrincipal.selectedItems()

        self.item = self.items_elegidos[0] if self.items_elegidos else None
        self.lista_recursiva_correspondencia_archivos = None
        self.lista_fija_correspondencia_archivos = None

        if len(self.items_elegidos) > 1:
            self.crear_lista_correspondencia_items_archivos()

        self.procesos_extra = []

        self.propiedad_variantes = None
        self.propiedad_variante = None

        if grupo_nombrado:
            self.configurar_grupo_nombrado()

        item_respetar = QTreeWidgetItem(self.arbol)
        self.item_elegir = QTreeWidgetItem(self.arbol)
        self.lista_variantes = ItemLista(self.item_elegir)

        self.arbol.setItemWidget(item_respetar, 0, self.wgt_opc_respetar)
        self.arbol.setItemWidget(self.item_elegir, 0, self.wgt_opc_elegir)
        self.arbol.setItemDelegate(util_ui.ItemDelegate(height=20))

        for item in [item_respetar, self.item_elegir, self.lista_variantes]:
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)

        self.arbol.expandAll()

        self.arbol.setStyleSheet("QTreeWidget { background-color: lightgray; border: 0px solid black; }")

        self.infos_escena = None

        self.configurar_estilo_botones()
        self.busco_variantes = False
        self.conectar_botones_acciones()
        self.opcion_respetar_blend.setChecked(True)
        self.cambio_opcion()
        lado_icono = int(16 * configuracion.factor_icons_size / 100)
        size = QtCore.QSize(lado_icono, lado_icono)
        self.boton_leer_variantes.setIconSize(size)

        atajo_ajustar = QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+T'),
                                            self)
        atajo_ajustar.activated.connect(self.adjustSize)



    def definir_contextual_lista(self):

        contextual = QMenu()
        contextual.addAction(traducir("Elegir todas"))
        contextual.triggered.connect(self.lista_variantes.selectAll)
        self.lista_variantes.setContextMenuPolicy(Qt.CustomContextMenu)
        self.lista_variantes.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        return contextual

    def mostrar_menu_contextual(self, posicion):
        self.contextual_lista.actions()[0].setEnabled(self.lista_variantes.count())
        self.contextual_lista.popup(self.lista_variantes.mapToGlobal(posicion))

    def configurar_estilo_botones(self):
        pass
        estilo_botones = "padding-left: 10px; padding-right: 10px; padding-top: 5px; padding-bottom: 5px;"
        # self.boton_leer_variantes.setStyleSheet(estilo_botones)
        # self.boton_elegir_todas.setStyleSheet(estilo_botones)

    def conectar_botones_acciones(self):
        self.opcion_elegir_lista.toggled.connect(self.cambio_opcion)
        self.boton_leer_variantes.clicked.connect(self.leer_variantes)
        self.lista_variantes.itemSelectionChanged.connect(self.cambio_seleccion)
        # self.lista_variantes.clicked.connect(self.cambio_seleccion)
        self.boton_aceptar_cancelar.accepted.connect(self.aceptar)
        self.boton_aceptar_cancelar.rejected.connect(self.cancelar)
        atajo_cancelar = QtWidgets.QShortcut(QtGui.QKeySequence('Esc'), self)
        atajo_cancelar.activated.connect(self.cancelar_busqueda)

    def configurar_grupo_nombrado(self):
        print("configurando", self.propiedad_variantes) # debug print
        if self.item:
            self.grupo_nombrado = WidgetNombrado(self, self.item)
        else:
            self.grupo_nombrado = WidgetNombrado(self, ItemFantasma())


        # self.layout_widget_nombrado.addWidget(self.grupo_nombrado)
        self.grupo_nombrado.setDisabled(True)

    def mostrar_grupo_nombrado(self):
        item_nombrado = ItemTitulo(traducir("Nombrado de salida"), parent=self.item_elegir)
        item_opciones_nombrado = QTreeWidgetItem(item_nombrado)
        item_opciones_nombrado.setFlags(item_opciones_nombrado.flags() & ~Qt.ItemIsSelectable)
        self.arbol.setItemWidget(item_opciones_nombrado, 0, self.grupo_nombrado.arbol)
        # item_nombrado_respetar = QTreeWidgetItem(item_nombrado)
        # item_nombrado_preseet = QTreeWidgetItem(item_nombrado)
        # item_nombrado_custom = QTreeWidgetItem(item_nombrado)
        # item_nombrado_output_path = QTreeWidgetItem(item_nombrado)
        # self.arbol.setItemWidget(item_nombrado_respetar, 0, self.grupo_nombrado.wgt_output_respetar)
        # self.arbol.setItemWidget(item_nombrado_preseet, 0, self.grupo_nombrado.wgt_output_preset)
        # self.arbol.setItemWidget(item_nombrado_custom, 0, self.grupo_nombrado.wgt_output_custom)
        # self.arbol.setItemWidget(item_nombrado_output_path, 0, self.grupo_nombrado.wgt_output_path)
        item_nombrado.setFlags(item_nombrado.flags() & ~Qt.ItemIsSelectable)
        item_nombrado.setExpanded(True)


    def closeEvent(self, event):
        restore_cursor()
        super().closeEvent(event)

    def cancelar(self):
        self.cancelar_busqueda()
        self.close()

    def cancelar_busqueda(self):
        restore_cursor()
        self.permitir_loop_recabando = False
        try:
            self.infos_escena.infos_blender.proceso_blender.kill()
        except AttributeError as e:
            self.close()
            print(e)

    def rellenar_lista_inicial(self, leer=False):
        # if not self.loop_espera_info_previa_recabando(True):
        #     return
        if self.lista_fija_correspondencia_archivos is not None:
            self.lista_recursiva_correspondencia_archivos = self.lista_fija_correspondencia_archivos.copy()
            set_cursor_espera()
            self.recursion_variantes_conjuntos(self.rellenar_lista_items_omitiendo_escena)
            return
        self.rellenar_lista_item_individual(omitir_escena=True)


    def loop_espera_info_previa_recabando(self, chequeo_inicial=False):
        if not self.permitir_loop_recabando:
            return False
        for item in self.items_elegidos:
            if item.recabando_info:
                set_cursor_espera()
                QTimer.singleShot(500, self.loop_espera_info_previa_recabando)
                return False
        restore_cursor()

        if chequeo_inicial:
            return True
        else:
            self.rellenar_lista_inicial()

    def rellenar_lista_items_omitiendo_escena(self, items):
        self.rellenar_lista_items(items, omitir_escena=True)

    def rellenar_lista_items(self, items, omitir_escena=False):
        escenas = items[0].escenas
        variantes = []
        if escenas:
            for item in items:
                item.escenas = escenas.copy()
                variantes_escena = self.propagar_variantes_item(item, item.escenas, omitir_escena=omitir_escena)
                if not variantes_escena:
                    continue
                variantes.extend(variantes_escena)
        else:
            for item in items:
                variantes_item = getattr(item, self.propiedad_variantes, None)
                if variantes_item:
                    variantes.extend(variantes_item)
            if not variantes:
                return
        for variante in variantes:
            if self.lista_variantes.findItems(variante, Qt.MatchFlag.MatchExactly):
                continue
            self.lista_variantes.addItem(variante)
        self.recursion_variantes_conjuntos(self.rellenar_lista_items)

    def rellenar_lista_item_individual(self, *args, omitir_escena=False):
        variantes = getattr(self.item, self.propiedad_variantes, None)
        if not variantes and self.item.escenas:
            variantes = self.propagar_variantes_item(self.item, self.item.escenas, omitir_escena=omitir_escena)
            if not variantes:
                if self.ha_leido:
                    return
                self.leer_variantes()
                return
        self.leer = False
        if variantes:
            self.lista_variantes.addItems(variantes)
            self.opcion_elegir_lista.setEnabled(True)
            self.boton_leer_variantes.setEnabled(True)
            self.acomodar_ventana()
            if self.propiedad_variante in self.item.propiedades_argumentar or self.busco_variantes:
                self.opcion_elegir_lista.setChecked(True)
                variante_previa = getattr(self.item, self.propiedad_variante, None)
                if variante_previa:
                    variante_elegida_lista = self.lista_variantes.findItems(variante_previa,
                                                                            Qt.MatchFlag.MatchExactly)
                    if variante_elegida_lista:
                        variante_elegida_lista[0].setSelected(True)
                        self.grupo_nombrado.setEnabled(True)
                        return


            return
        self.opcion_elegir_lista.setEnabled(False)
        self.obtener_infos_escenas(self.item, self.rellenar_lista_item_individual, cursor_espera=True)

    def toggle_boton_aceptar(self):
        deshabilitar = self.opcion_elegir_lista.isChecked() and not self.lista_variantes.selectedItems()
        self.boton_aceptar_cancelar.button(QtWidgets.QDialogButtonBox.Ok).setDisabled(deshabilitar)

    def cambio_opcion(self):
        sentido = not self.opcion_respetar_blend.isChecked()
        self.grupo_nombrado.setEnabled(sentido)
        self.toggle_opciones_select(not sentido)
        self.toggle_boton_aceptar()
        if self.item and "nombrado" in self.item.propiedades_argumentar:
            try:
                ruta = self.item.patron_nombrado["ruta"]
                nombre = self.item.patron_nombrado["nombre"]
                self.grupo_nombrado.muestra_ruta.setText(auto_nombrado.patron_a_string(ruta))
                self.grupo_nombrado.muestra_nombre.setText(auto_nombrado.patron_a_string(nombre))
                self.grupo_nombrado.opcion_custom.setChecked(True)
                return
            except AttributeError as e:
                print("Error while changing option", e)
                pass
        self.grupo_nombrado.opcion_usar_preset.setChecked(sentido)

    def toggle_opciones_select(self, desactivar=True):
        children_count = self.item_elegir.childCount()
        for i in range(children_count):
            self.item_elegir.child(i).setDisabled(desactivar)

    def cambio_seleccion(self):
        self.opcion_elegir_lista.setChecked(True)
        self.toggle_boton_aceptar()

    def leer_variantes(self):
        self.permitir_loop_recabando = False
        self.busco_variantes = True
        self.lista_variantes.clear()
        self.leer = True
        if self.lista_fija_correspondencia_archivos:
            self.lista_recursiva_correspondencia_archivos = self.lista_fija_correspondencia_archivos.copy()
            set_cursor_espera()
            self.recursion_variantes_conjuntos(self.rellenar_lista_items)
            return
        setattr(self.item, self.propiedad_variantes, None if self.propiedad_variante != "escenas" else {})
        self.obtener_infos_escenas(self.item, self.rellenar_lista_item_individual, cursor_espera=True)

    def obtener_infos_escenas(self, item, procesar, cursor_espera=True):
        self.ha_leido = True
        dato_infaltable = self.propiedad_variantes if self.propiedad_variantes != "escenas" else None
        item.leer_escenas_item(avisar=procesar, pasar_parametro=False, cursor_espera=cursor_espera, asimilar=True,
                               dato_infaltable=dato_infaltable)


    def elegir_todas(self):
        self.lista_variantes.selectAll()
        self.cambio_seleccion()

    @property
    def variantes_elegidas(self):
        return [item.text(0) for item in self.lista_variantes.selectedItems()]

    def cambiar_y_agregar(self):
        if not self.variantes_elegidas:
            return

        if self.lista_fija_correspondencia_archivos:  # proxy para saber si hay varios elegidos
            self.agregar_variantes_items_multiples()
            return
        self.agregar_variantes_item_individual(self.item, self.variantes_elegidas)

    def leer_variantes_conjunto(self, items, procesar_variantes_conjunto):
        first_item = items[0]
        def leer_infos_escenas(): self.obtener_infos_escenas(item=first_item, procesar=lambda: procesar_variantes_conjunto(items))
        if self.leer: # para que el boton de leer cuando hay muchos items vuelva a leer en lugar de conformarse con la info vieja
            leer_infos_escenas()
            return
        escenas_o_variantes = getattr(first_item, self.propiedad_variantes, None)
        if not escenas_o_variantes:
            escenas = getattr(first_item, 'escenas', None)
            if escenas:
                escena = first_item.escena if first_item.escena in escenas else next(iter(escenas), None)
                if escena is not None:
                    escenas_o_variantes = getattr(escenas[escena],
                                                  self.propiedad_variantes, None)

        if escenas_o_variantes:
            procesar_variantes_conjunto(items)
            return
        
        leer_infos_escenas()

    def propagar_variantes_item(self, item, escenas, omitir_escena=False):
        if escenas.get(item.escena):
            escena = item.escena
        else:
            escena = next(iter(escenas))
            omitir_escena = False
        variantes = getattr(escenas[escena], self.propiedad_variantes, None)
        setattr(item, self.propiedad_variantes, variantes)
        item.asimilar_info_escena(escenas[escena], preservar_argumentadas=True, omitir_escena=omitir_escena)
        return variantes

    def agregar_variantes_item_individual(self, item, variantes):
        setattr(item, self.propiedad_variante, variantes[0])
        autonombrar = self.procesar_autonombrado_item(item)
        item.propiedades_argumentar.add(self.propiedad_variante)
        if item.estado == "terminado":
            item.reset()

        if len(variantes) > 1:
            self.ventana.agregar_variantes(self.propiedad_variantes, item, variantes[1:],
                                           autonombrar=autonombrar)

    def agregar_variantes_items_multiples(self):
        for item in self.items_elegidos:
            variantes_item = self.variantes_elegidas.copy()
            escena = item.escena if item.escena else list(item.escenas)[0]
            info_escena = item.escenas.get(escena)
            if item.estado == "terminado":
                item.reset()

            for variante in self.variantes_elegidas:
                if variante not in getattr(info_escena, self.propiedad_variantes, []):
                    variantes_item.remove(variante)
            if not variantes_item:
                continue
            self.agregar_variantes_item_individual(item, variantes_item)

    def agregar_variantes_conjunto(self, items, variantes=None):
        escenas = items[0].escenas
        eligio_variantes = bool(variantes)

        for item in items:
            item.escenas = escenas.copy()
            if not eligio_variantes:
                variantes = self.propagar_variantes_item(item, escenas)
                if not variantes:
                    continue
            self.agregar_variantes_item_individual(item, variantes)
        self.recursion_variantes_conjuntos(self.agregar_variantes_conjunto)

    def recursion_variantes_conjuntos(self, procesar_variantes_conjunto):
        if not self.lista_recursiva_correspondencia_archivos:
            self.leer = False
            restore_cursor()
            self.boton_leer_variantes.setEnabled(True)
            if not self.lista_variantes.count():
                return
            # self.configurar_mensaje_combinados()
            self.lista_variantes.mostrar_mensaje_combinados()
            self.arbol.updateGeometry()
            self.opcion_elegir_lista.setEnabled(True)
            self.opcion_elegir_lista.setChecked(True)
            self.acomodar_ventana()
            return
        item = self.lista_recursiva_correspondencia_archivos.popitem()[1]
        self.leer_variantes_conjunto(item, procesar_variantes_conjunto)  # manda los items con la ruta que popeo

    def configurar_mensaje_combinados(self):
        item_mensaje_combinados = QTreeWidgetItem()
        mensaje_combinados = QLabel()
        font = self.font()
        font.setPointSize(
            int(ConfiguracionVentana.size_default_textos["statusbar"] * configuracion.factor_ui_font_size / 100))
        font.setItalic(True)
        mensaje_combinados.setFont(font)
        mensaje_combinados.setAlignment(Qt.AlignCenter)
        mensaje_combinados.setText("(" + traducir("variantes_resultados_combinados") + ")")
        mensaje_combinados.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        padding = "padding-top: 3px; padding-bottom: 6px;"
        mensaje_combinados.setStyleSheet(padding)
        self.item_elegir.insertChild(1, item_mensaje_combinados)
        self.arbol.setItemWidget(item_mensaje_combinados, 0, mensaje_combinados)


    def crear_lista_correspondencia_items_archivos(self):
        self.lista_fija_correspondencia_archivos = {}
        for item in self.items_elegidos:
            ruta = item.ruta_blend_completa
            if ruta in self.lista_fija_correspondencia_archivos:
                self.lista_fija_correspondencia_archivos[ruta].append(item)
            else:
                self.lista_fija_correspondencia_archivos[ruta] = [item]

    def procesar_autonombrado_item(self, item):
        if self.grupo_nombrado.opcion_usar_preset.isChecked():
            item.patron_nombrado = self.grupo_nombrado.selector_preset.currentData().patron
            autonombrar = True
        elif self.grupo_nombrado.opcion_custom.isChecked():
            item.patron_nombrado = self.grupo_nombrado.patron_custom()
            autonombrar = True
        else:
            autonombrar = False  # esta variable sirve tanto para este primer item como más abajo para los otros

        if autonombrar:
            auto_nombrado.aplicar(item)

        return autonombrar

    def acomodar_ventana(self):
        self.resize(0, 0)
        QTimer.singleShot(10, self.adjustSize)
        restore_cursor()

    def aceptar(self):

        for proceso_extra in self.procesos_extra:
            proceso_extra()

        if self.opcion_elegir_lista.isChecked():
            self.cambiar_y_agregar()
        elif self.opcion_respetar_blend.isChecked():
            for item in self.items_elegidos:
                item.propiedades_argumentar.discard(self.propiedad_variante)
                setattr(item, self.propiedad_variante, None)

        colas.guardar()
        self.close()

    def retranslateUi(self, _):
        self.opcion_elegir_lista.setText(traducir("Elegir"))


class VentanaCamaras(VentanaVariantes):
    def __init__(self, ventana):
        super().__init__(ventana)
        self.lista_variantes.icono = iconos.icono_sm_camera
        self.boton_leer_variantes.setIcon(iconos.icono_update_cameras)
        self.propiedad_variantes = "camaras"
        self.propiedad_variante = "camara"
        self.procesos_extra.append(self.quitar_warning)
        self.rellenar_lista_inicial()
        self.mostrar_grupo_nombrado()
        self.grupo_nombrado.rellenar_presets(self.propiedad_variantes)
        self.lista_variantes.setTitle(traducir("Cameras"))

    def quitar_warning(self):
        for item in self.items_elegidos:
            item.quitar_warning(ColumnaProp.camara)


    def retranslateUi(self, _):
        super().retranslateUi(_)
        self.setWindowTitle(traducir("cámaras").capitalize())
        self.opcion_respetar_blend.setText(traducir("Usar cámara activa en la escena"))
        self.boton_leer_variantes.setToolTip(traducir("tooltip_releer_camaras"))
        # self.boton_leer_variantes.setText(traducir("Leer cámaras"))



class VentanaViewlayers(VentanaVariantes):
    def __init__(self, ventana):
        super().__init__(ventana)

        self.lista_variantes.icono = iconos.icono_sm_viewlayer
        self.boton_leer_variantes.setIcon(iconos.icono_update_view_layers)
        self.compositing_info_popup = None
        self.propiedad_variantes = "view_layers"
        self.propiedad_variante = "view_layer"

        self.ventana = ventana

        self.procesos_extra.append(self.aplicar_handling_compositing)

        item_compositing = ItemCustomWidget(self.item_elegir, self.wgt_compositing)
        item_compositing.setFlags(item_compositing.flags() & ~Qt.ItemIsSelectable)
        self.wgt_compositing.show()

        self.btn_info_compositing.setIcon(iconos.icono_info)
        self.btn_info_compositing.clicked.connect(self.show_compositing_info_popup)

        self.rellenar_lista_inicial()
        self.opciones_compositing = ["auto", "replicate", "disable", "leave_as_is"]

        self.rellenar_opciones_compositing()
        self.definir_popup_info()

        self.lista_variantes.setTitle(traducir("Viewlayers"))
        self.mostrar_grupo_nombrado()
        self.grupo_nombrado.rellenar_presets(self.propiedad_variantes)

        self.installEventFilter(self)
        self.arbol.clicked.connect(self.cerrar_popup)

        # if unico:
        #     self.rellenar_lista_item_individual()

    def definir_popup_info(self):
        self.compositing_info_popup = InfoPopUp(self, "info_viewlayers_compositing")


    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        self.cerrar_popup()
        event.accept()

    def cerrar_popup(self):
        if self.compositing_info_popup:
            self.compositing_info_popup.close()

    def rellenar_opciones_compositing(self):
        for opcion in self.opciones_compositing:
            self.selector_handle_compositing.addItem(traducir(opcion).capitalize(), opcion)

        # # tmp por falta de implementacion
        # self.selector_handle_compositing.setCurrentText(traducir("Disable"))
        # self.selector_handle_compositing.setDisabled(True)

    def aplicar_handling_compositing(self):
        for item in self.ventana.tablaPrincipal.selectedItems():
            item.manejar_compositing = self.selector_handle_compositing.currentData(Qt.UserRole)

    def eventFilter(self, obj, event):
        if getattr(self, "compositing_info_popup", None) and event.type() == event.MouseButtonPress:
            if not self.compositing_info_popup.geometry().contains(event.globalPos()):
                self.compositing_info_popup.close()
        return super().eventFilter(obj, event)

    def show_compositing_info_popup(self):
        cursor = QtGui.QCursor()
        posicion = cursor.pos()
        self.compositing_info_popup.move(posicion)
        self.compositing_info_popup.setVisible(not self.compositing_info_popup.isVisible())

    def retranslateUi(self, _):
        super().retranslateUi(_)
        self.setWindowTitle(traducir("viewlayers").capitalize())
        self.opcion_respetar_blend.setText(traducir("Usar configuracion de viewlayers del blend"))
        self.boton_leer_variantes.setToolTip(traducir("tooltip_releer_viewlayers"))
        self.lbl_compositing.setText(traducir("Handle compositing"))



class VentanaEscenas(VentanaVariantes):
    def __init__(self, ventana, item=None, reemplazar=True, leer=False, duplicando=0):
        super().__init__(ventana, grupo_nombrado=False)
        self.lista_variantes.icono = iconos.icono_sm_scene
        self.boton_leer_variantes.setIcon(iconos.icono_update_scenes)
        self.reemplazar = reemplazar
        self.propiedad_variantes = "escenas"
        self.propiedad_variante = "escena"
        self.leer = leer

        self.opcion_respetar_blend.setChecked(True)

        self.grupo_nombrado = None

        self.item = item
        self.rellenar_lista_inicial(leer)
        self.duplicando = duplicando
        self.lista_variantes.setTitle(traducir("Scenes"))

    def cambio_opcion(self):
        self.toggle_boton_aceptar()

    # def obtener_infos_escenas(self, item, procesar, cursor_espera=None):
    #     self.boton_leer_variantes.setEnabled(False)
    #     item.leer_escenas_item(avisar=procesar)

    def propagar_variantes_item(*args):
        pass

    def rellenar_lista_items(self, items, omitir_escena=None):
        escenas = items[0].escenas
        if not escenas:
            return
        for item in items:
            item.escenas = escenas.copy()
        for escena in escenas:
            if self.lista_variantes.findItems(escena, Qt.MatchFlag.MatchExactly):
                continue
            self.lista_variantes.addItem(escena)

        self.recursion_variantes_conjuntos(self.rellenar_lista_items)

    def rellenar_lista_item_individual(self, leer=False, omitir_escena=None):
        if not self.item:
            return
        if not self.item.escenas:
            self.leer_variantes()
            return
        self.lista_variantes.clear()
        for escena in self.item.escenas:
            # item_lista_i = QtWidgets.QListWidgetItem()
            # item_lista_i.setText(escena)
            # item_lista_i.setData(Qt.UserRole, self.item.escenas[
            #     escena])  # esto quizás ya no sea necesario con la nueva idea de asimilar todo de uan y puse uan sin querer quise poner una
            self.lista_variantes.addItem(escena, selected= escena==self.item.escena)
            # if escena == self.item.escena:
            #     item_lista_i.setSelected(True)
        self.opcion_elegir_lista.setChecked(True)
        self.boton_leer_variantes.setEnabled(True)
        self.acomodar_ventana()

    # @property
    # def variantes_elegidas(self):
    #     return [item.data(QtCore.Qt.UserRole) for item in self.lista_variantes.selectedItems()]

    def cambiar_y_agregar(self):
        if not self.variantes_elegidas:
            return

        if self.lista_fija_correspondencia_archivos:
            self.agregar_variantes_items_multiples()
            return

        self.agregar_variantes_item_individual(self.item, self.variantes_elegidas)

    def agregar_variantes_item_individual(self, item, nombres_escenas):
        escenas = [item.escenas[escena] for escena in nombres_escenas]
        item.propiedades_argumentar.add("escena")
        item.escena = escenas[0].escena
        item.asimilar_info_escena(escenas[0], preservar_argumentadas=True)
        token_escena = auto_nombrado.tokens["scene"].patron
        autonombrar = "nombrado" in item.propiedades_argumentar # and (token_escena in item.patron_nombrado["nombre"] or token_escena in item.patron_nombrado["ruta"]) # solo pido esto para actualizar si hubo otros cambios que afectan, por ejemplo si leyó el output path y se usa en el patrón
        if autonombrar:
            auto_nombrado.aplicar(item)
        if item.estado == "terminado":
            item.reset()
        if item.view_layer:  # comprobación incompleta. Y podría aplicarse lo mismo a cámara.
            if escenas[0].view_layers and "view_layer" in item.propiedades_argumentar:
                if item.view_layer not in escenas[0].view_layers:
                    item.view_layer = ""
                    item.propiedades_argumentar.discard("view_layer")
            else:
                alertas.alerta_generica("alerta_viewlayer_escena")

        items = [item]
        if len(escenas) > 1:

            items.extend(self.ventana.agregar_variantes("escenas", item, escenas[1:], autonombrar))

        for i in range(self.duplicando):
            self.ventana.duplicar_items_en_sitio(items)

    def agregar_variantes_items_multiples(self):
        for item in self.items_elegidos:
            if item.estado == "terminado":
                item.reset()
            nombres_escenas = self.variantes_elegidas.copy()
            for escena in self.variantes_elegidas:
                if escena not in item.escenas:
                    nombres_escenas.remove(escena)
            if not nombres_escenas:
                continue
            self.agregar_variantes_item_individual(item, nombres_escenas)

    def agregar_variantes_conjunto(self, items):
        info_escenas = items[0].escenas
        for item in items:
            item.escenas = info_escenas
            if item.escena:
                escena = item.escena
            else:
                escena = [*info_escenas.keys()][0]
            item.asimilar_info_escena(info_escenas[escena])
            item.view_layer = ""
            item.camara = ""
            item.propiedades_argumentar.discard("camara")
            item.propiedades_argumentar.discard("view_layer")
            item.propiedades_argumentar.add("escena")

            items = [item]
            if len(info_escenas) > 1:
                resto_info_escenas = info_escenas.copy()
                resto_info_escenas.pop(item.escena)
                resto_info_escenas = [*resto_info_escenas.values()]
                items.extend(self.ventana.agregar_variantes("escenas", item, resto_info_escenas))

        for i in range(self.duplicando):
            self.ventana.duplicar_items_en_sitio(items)

        self.recursion_variantes_conjuntos(self.agregar_variantes_conjunto)

    def retranslateUi(self, _):
        super().retranslateUi(_)
        self.setWindowTitle(traducir("Escenas"))
        self.boton_leer_variantes.setToolTip(traducir("tooltip_releer_escenas"))
        self.opcion_respetar_blend.setText(traducir("Usar escena activa en el blend"))
        # self.boton_leer_variantes.setText(traducir("Leer escenas del blend"))


class CustomHeaderWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up a basic layout
        layout = QtWidgets.QVBoxLayout(self)

        # Create a dummy table to act as a base (this can be hidden)
        table = QtWidgets.QTableWidget(0, 3)  # 3 columns
        table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

        # Extract the header
        header = table.horizontalHeader()
        header.setStretchLastSection(True)  # Stretch last section if needed
        header.setSectionsClickable(True)   # Make headers clickable if needed

        # Add header to the layout (you can hide the table or only show the header)
        layout.addWidget(header)

        # Hide the table itself but keep the header
        table.setVisible(False)

        self.setLayout(layout)


class VentanaColecciones(QtWidgets.QDialog, ui.ventana_colecciones.Ui_ventana_colecciones):
    anchos_columnas_fijas = [60, 70]
    size_icono_edito = 12

    def __init__(self, items, parent):
        super().__init__(parent)
        self.pixmap_estado = None
        self.mapeo_popups = {}
        self.setupUi(self)
        self.items = items
        # self.item = item
        self.items_por_leer = None

        self.traducir()
        self.configurar_apariencias()
        self.conectar_segnales()

        self.collection_tokens_presentes = None
        self.colecciones_dejadas_sin_token = None
        self.arbol.itemSelectionChanged.connect(self.cambio_seleccion)
        self.show()

        self.nueva_seleccion = {}

        self.tokens = set()

        self.popup_info_tokens = self.definir_popup_info(self.btn_info_tokens, "info_tokens_collections")
        self.popup_info_split= self.definir_popup_info(self.btn_info_split, "info_split_collections")
        self.btn_split.clicked.connect(self.split)

        self.mapeo_signals = {"quitar_todos_tokens": self.quitar_todos_tokens, "token_quitar": self.quitar_token}

        self.lbl_multiples_jobs.setHidden(True)

        self.arbol.clicked.connect(self.cerrar_popups)
        self.wgt_titulo.clicked.connect(self.cerrar_popups)
        self.installEventFilter(self)

        if self.items[0].colecciones:
            self.comparar_colecciones()
            self.mostrar_colecciones()
        else:
            self.leer_items()


    def hay_multiples_items(self):
        lado_icono = int(VentanaColecciones.size_icono_edito * configuracion.factor_icons_size / 100)
        empty_pixmap = QtGui.QPixmap(lado_icono, lado_icono)
        empty_pixmap.fill(Qt.transparent)
        pixmap_edito = iconos.icono_pencil.pixmap(lado_icono, lado_icono)
        self.pixmap_estado = [empty_pixmap, pixmap_edito]
        self.lbl_multiples_jobs.setHidden(False)

    def conectar_segnales(self):
        self.btn_leer.clicked.connect(self.leer_items)
        self.btn_restaurar.clicked.connect(self.restaurar)
        self.accepted.connect(self.aceptar)
        self.rejected.connect(self.cerrar_popups)

    def configurar_apariencias(self):
        self.arbol.setItemDelegate(util_ui.ItemDelegate(height=configuracion.alto_filas))
        self.wgt_titulo.setItemDelegate(util_ui.ItemDelegate(height=configuracion.alto_filas))
        self.arbol.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        for wgt in [self.arbol, self.wgt_titulo]:
            for i, ancho in enumerate(self.anchos_columnas_fijas):
                wgt.setColumnWidth(i+1, ancho)
        self.btn_info_tokens.setIcon(iconos.icono_info)
        self.btn_info_split.setIcon(iconos.icono_info)
        self.btn_restaurar.setIcon(iconos.icono_reset)
        self.btn_leer.setIcon(iconos.icono_collections_update)
        self.wgt_titulo.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.wgt_titulo.setItemWidget(self.wgt_titulo.topLevelItem(0), 0, self.wgt_titulo_name)
        self.wgt_titulo.setItemWidget(self.wgt_titulo.topLevelItem(0), 1, self.wgt_titulo_enable)
        self.wgt_titulo.setItemWidget(self.wgt_titulo.topLevelItem(0), 2, self.wgt_titulo_token)


    def definir_popup_info(self, boton, nombre_texto):
        popup = InfoPopUp(self, nombre_texto)
        self.mapeo_popups[boton.objectName()] = popup
        boton.clicked.connect(self.mostrar_info_popup)
        return popup

    def eventFilter(self, obj, event):
        if event.type() == event.MouseButtonPress:
            if not self.popup_info_split.geometry().contains(
                    event.globalPos()) and not self.popup_info_tokens.geometry().contains(event.globalPos()):
                self.cerrar_popups()
        return super().eventFilter(obj, event)

    def mostrar_info_popup(self):
        nombre = self.sender().objectName()
        popup = self.mapeo_popups[nombre]
        cursor = QtGui.QCursor()
        posicion = cursor.pos()
        popup.move(posicion)
        popup.setVisible(not popup.isVisible())


    @staticmethod
    def get_item_level(item):
        level = 0
        while item.parent() is not None:
            item = item.parent()
            level += 1
        return level

    def selected_collections_names(self):
        for col in self.arbol.selectedItems():
            yield col.nombre

    def cambio_seleccion(self):
        items_elegidos = self.arbol.selectedItems()
        spliteable = False
        if len(items_elegidos) > 1:
            primero = items_elegidos[0]
            nivel_primero = self.get_item_level(primero)
            spliteable = all(self.get_item_level(item) == nivel_primero for item in items_elegidos[1:])
        self.btn_split.setEnabled(spliteable)


    def siguiente_key(self):
        for key in auto_nombrado.token_keys:
            if key not in self.tokens:
                self.tokens.add(key)
                return key
        return ""

    @pyqtSlot(str)
    def quitar_token(self, key):
        self.tokens.discard(key)

    @pyqtSlot()
    def quitar_todos_tokens(self):
        marcar_todos = bool(self.tokens)
        self.tokens = set()
        it = QTreeWidgetItemIterator(self.arbol)
        while it.value():
            item_i = it.value()
            if item_i.token_key in auto_nombrado.split_keys:
                it += 1
                continue
            item_i.quitar_token()
            if marcar_todos:
                item_i.set_token_editado()
            it += 1

    @pyqtSlot(str)
    def reservar_num_token(self, key):
        self.tokens.add(key)

    def restaurar(self):
        self.mostrar_colecciones(restaurar=True)

    def leer(self, item):
        info_colecciones = InfoColecciones(self, item)
        info_colecciones.recabo.connect(self.verificar_items_leidos)
        info_colecciones.averiguar()

    def leer_items(self):
        self.tokens = set()
        self.items_por_leer = self.items.copy()
        self.leer(self.items_por_leer[0])

    def verificar_items_leidos(self, obj):
        self.items_por_leer.remove(obj)
        if self.items_por_leer:
            self.leer(self.items_por_leer[0])
            return

        self.comparar_colecciones()
        self.mostrar_colecciones()

    def comparar_colecciones(self):
        if not self.items or not self.items[0].colecciones:
            return
        colecciones_base = self.seleccion_original(self.items[0])
        items = self.items.copy()
        alertar = False
        for item in self.items[1:]:
            if self.seleccion_original(item) != colecciones_base:
                items.remove(item)
                alertar = True

        if alertar:
            alertas.alerta_generica("alerta_colecciones_diferentes")
        if len(items) > 1:
            self.hay_multiples_items()
        self.items = items

    def traducir(self):
        self.btn_leer.setText(traducir("Leer colecciones"))
        self.setWindowTitle(traducir("Colecciones"))
        self.btn_restaurar.setText(traducir("Restaurar"))
        self.btn_leer.setToolTip(traducir("tooltip_releer_colecciones"))
        self.btn_restaurar.setToolTip(traducir("tooltip_restaurar"))
        self.lbl_multiples_jobs.setText(traducir("info_multiples_jobs"))
        self.btn_split.setText(traducir("btn_colecciones_split"))

    def seleccion_original(self, item):
        data_completa = getattr(item, "colecciones", None)
        if not data_completa:
            return False
        escena = data_completa["escena_activa"] if not item.escena else item.escena
        viewlayer = data_completa["viewlayer_activo"] if not item.view_layer else item.view_layer
        return data_completa["data_original"][escena][viewlayer]

    def mostrar_colecciones(self, restaurar=False):
        self.arbol.clear()
        self.tokens = set()
        item = self.items[0]
        data_completa = item.colecciones
        escena = data_completa["escena_activa"] if not item.escena else item.escena
        viewlayer = data_completa["viewlayer_activo"] if not item.view_layer else item.view_layer
        if restaurar:
            seleccion = {}
        else:
            seleccion = data_completa.get("seleccion", {})

        data_colecciones = copy.deepcopy(data_completa["data_original"][escena][viewlayer])

        if seleccion:
            self.recursion_aplicar_seleccion(data_colecciones, seleccion)

        self.recursion_mostradora_colecciones(data_colecciones, self.arbol, self.nueva_seleccion)
        # self.arbol.expandAll()

        if "collection_tokens" in data_completa:
            collection_tokens = data_completa["collection_tokens"]
            collection_tokens_invertida = {v: k for k, v in collection_tokens.items()}
            self.mostrar_tokens_previos(collection_tokens_invertida)
        titulo = traducir("Colecciones") + " (" + traducir("Escena") + ": " + escena
        titulo += " - " + traducir("Viewlayer") + ": " + viewlayer + ")"
        self.setWindowTitle(titulo)

    def recursion_aplicar_seleccion(self, data_colecciones, seleccion):
        for nombre, coleccion in data_colecciones.items():
            if nombre in seleccion:
                coleccion["excluded"] = seleccion[nombre]
            self.recursion_aplicar_seleccion(coleccion["children"], seleccion)

    def recursion_mostradora_colecciones(self, data_colecciones, parent, seleccion):

        for nombre, coleccion in data_colecciones.items():
            item = ItemColeccion(parent, self, nombre, not coleccion["excluded"], seleccion)
            for signal_name, slot in self.mapeo_signals.items():
                signal = getattr(item.signals, signal_name)
                if signal:
                    signal.connect(slot)
            self.recursion_mostradora_colecciones(coleccion["children"], item, seleccion)

    def mostrar_tokens_previos(self, collection_tokens):
        it = QTreeWidgetItemIterator(self.arbol)
        while it.value():
            item_i = it.value()
            nombre = item_i.nombre
            if nombre in collection_tokens:
                key = collection_tokens[nombre]
                self.tokens.add(key)
                item_i.token_key = key
                item_i.btn_token.setText(key)
                item_i.btn_token.setChecked(True)

            it += 1

    def guardar_cambios(self):
        it = QTreeWidgetItemIterator(self.arbol)
        self.collection_tokens_presentes = {}
        self.colecciones_dejadas_sin_token = set()
        while it.value():
            item_i = it.value()
            item_i.guardar_cambios()
            if item_i.edito_token:
                if item_i.token_key:
                    self.collection_tokens_presentes[str(item_i.token_key)] = item_i.nombre
                else:
                    self.colecciones_dejadas_sin_token.add(item_i.nombre)

            it += 1

    def aceptar(self):
        self.cerrar_popups()
        self.aplicar()
        for item in self.items:
            if "nombrado" in item.propiedades_argumentar:
                token_col = auto_nombrado.tokens["collection"].patron
                if token_col in item.patron_nombrado["ruta"] or token_col in item.patron_nombrado["nombre"]:
                    auto_nombrado.aplicar(item)
        colas.guardar()

    def cerrar_popups(self):
        self.popup_info_tokens.close()
        self.popup_info_split.close()

    def aplicar(self):
        self.guardar_cambios()
        for item in self.items:
            item.colecciones["seleccion"].update(self.nueva_seleccion)
            argumentar = item.propiedades_argumentar
            if self.collection_tokens_presentes is not None:

                item.colecciones["collection_tokens"].update(self.collection_tokens_presentes)
            if self.colecciones_dejadas_sin_token is not None:
                for key, coleccion in list(item.colecciones["collection_tokens"].items()):
                    if coleccion in self.colecciones_dejadas_sin_token and key not in auto_nombrado.split_keys:
                        item.colecciones["collection_tokens"].pop(key, None)
            item.reset()
            argumentar.add("uso_colecciones")

    def split(self):
        self.aplicar()
        selected_collections = [(i, col_i.nombre) for i, col_i in enumerate(self.arbol.selectedItems())]
        selected_number = len(selected_collections)
        for item in self.items:
            seleccion_base = item.colecciones["seleccion"]
            tokens = item.colecciones["collection_tokens"]
            item.colecciones["collection_tokens"] = {k: v for k,v in tokens.items() if v not in selected_collections}

            for split_key in auto_nombrado.split_keys:
                if split_key not in item.colecciones["collection_tokens"]:
                    break
            item_j = None
            for j in range(selected_number):
                seleccion_j = seleccion_base.copy()
                for i, nombre_col_i in selected_collections:
                    seleccion_j[nombre_col_i] = j != i
                item_j = item_j.duplicar_en_sitio() if item_j else item
                item_j.colecciones["seleccion"] = seleccion_j
                item_j.colecciones["collection_tokens"][split_key] = selected_collections[j][1]

        colas.guardar()
        self.close()



class SignalsExtraArgs(QObject):
    agregar_arg = pyqtSignal(object)
    browsear = pyqtSignal(object, str)
    borrar = pyqtSignal(object)
    renombrar = pyqtSignal(object)
    interactuo = pyqtSignal(object)


class ItemExtraArgs(QTreeWidgetItem):
    lista_columnas = ["arg", "interactivo", ]
    columnas = {}
    for i, el in enumerate(lista_columnas):
        columnas[el] = i
    signals = SignalsExtraArgs()

    def __init__(self, arg, nombre=None, tipo="", aux_interactivo=None, wide=False, validator=None, parent=None):
        super().__init__(parent)
        self.nombre = nombre if nombre else arg
        self.interaccion_vacua = False
        self.validator = validator

        self.tipo = tipo
        self.arg = arg
        self.filtro_browse = None

        self.btn_arg = self.configurar_btn_arg()

        if not tipo:
            return
        self.interactivo = None
        self.interactivo_aux = None
        self.configurar_interactivo(tipo, aux_interactivo, wide)

    def dict_guardable(self):
        return {"nombre": self.nombre, "arg": self.arg, "tipo": "custom_preset"}

    def configurar_btn_arg(self):
        btn_arg = QtWidgets.QPushButton(traducir(self.nombre))
        wgt_usar = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wgt_usar)
        layout.addWidget(btn_arg)
        layout.addItem(QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum))
        layout.setContentsMargins(5, 4, 5, 4)
        self.treeWidget().setItemWidget(self, self.columnas["arg"], wgt_usar)
        btn_arg.clicked.connect(self.enviar_arg)
        return btn_arg

    def configurar_interactivo(self, tipo, aux_interactivo, wide):

        wgt_interactivo = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wgt_interactivo)
        layout.setContentsMargins(5, 2, 5, 2)
        match tipo:
            case "list":
                self.interactivo = QtWidgets.QComboBox()
                self.interactivo.addItems(aux_interactivo)
                self.interactivo.setSizeAdjustPolicy(0)
                self.interactivo.currentIndexChanged.connect(self.marcar_interaccion_vacua)
                self.arg_valor = self.arg_valor_lista
            case "bool":
                self.interactivo = QtWidgets.QCheckBox()
                self.interactivo.toggled.connect(self.marcar_interaccion_vacua)
                self.arg_valor = self.arg_valor_bool
            case "text":
                self.interactivo = QtWidgets.QLineEdit()
                self.interactivo.textChanged.connect(self.marcar_interaccion_vacua)
                if self.validator:
                    self.interactivo.setValidator(QtGui.QIntValidator())
                self.arg_valor = self.arg_valor_texto
                if not wide:
                    self.interactivo.setAlignment(Qt.AlignHCenter)
            case "file":
                self.interactivo = QtWidgets.QLineEdit()
                self.arg_valor = self.arg_valor_texto
                self.interactivo_aux = BotonBrowse()
                self.interactivo_aux.inicializar(self.browse)
                self.interactivo.textChanged.connect(self.marcar_interaccion_vacua)
                self.filtro_browse = aux_interactivo
            case "custom_preset":
                self.interactivo = QtWidgets.QPushButton(traducir("Borrar"))
                self.interactivo_aux = QtWidgets.QPushButton(traducir("Renombrar"))
                self.interactivo.clicked.connect(self.borrar_custom_preset)
                self.interactivo_aux.clicked.connect(self.renombrar_custom_preset)
                layout.addItem(
                    QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
                wide = True

        layout.addWidget(self.interactivo)
        if self.interactivo_aux:
            layout.addWidget(self.interactivo_aux)

        policy_espaciador = [QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum][wide]
        layout.addItem(QtWidgets.QSpacerItem(5, 5, policy_espaciador, QtWidgets.QSizePolicy.Minimum))

        self.treeWidget().setItemWidget(self, self.columnas["interactivo"], wgt_interactivo)

    def arg_valor_texto(self):
        return self.interactivo.text()

    def arg_valor_lista(self):
        return self.interactivo.currentText()

    def arg_valor_bool(self):
        return str(self.interactivo.isChecked())

    def arg_valor(self):
        return ""

    def marcar_interaccion_vacua(self):
        self.signals.interactuo.emit(self)
        self.interaccion_vacua = True

    def enviar_arg(self):
        self.interaccion_vacua = False
        self.signals.agregar_arg.emit(self)

    def browse(self):
        self.signals.browsear.emit(self.interactivo, self.filtro_browse)

    def renombrar_custom_preset(self):
        self.signals.renombrar.emit(self)

    def actualizar_nombre(self, nuevo_nombre):
        self.nombre = nuevo_nombre
        self.btn_arg.setText(traducir(self.nombre))

    def borrar_custom_preset(self):
        self.signals.borrar.emit(self)


class ArgsExtraBuiltin:
    formatos = ["TGA",
                "RAWTGA",
                "JPEG",
                "IRIS",
                "IRIZ",
                "AVIRAW",
                "AVIJPEG",
                "PNG",
                "BMP",
                "OPEN_EXR",
                "OPEN_EXR_MULTILAYER",
                "TIFF"]

    engines = {"Eevee_next": "BLENDER_EEVEE_NEXT",
               "Eevee": "BLENDER_EEVEE",
               "Workbench": "BLENDER_WORKBENCH",
               "Cycles": "CYCLES"}

    token_valor = "$*value*$"

    args_nativos = [
        {"arg": "--engine", "tipo": "list", "aux_interactivo": engines.values()},
        {"arg": "--threads", "tipo": "text", "validator": "int"},
        {"arg": "--render-format", "tipo": "list", "aux_interactivo": formatos},
        {"arg": "--use-extension", "tipo": "bool"},
        {"arg": "--enable-autoexec"},
        {"arg": "--disable-autoexec"},
        {"arg": "--python", "tipo": "file", "aux_interactivo": "Python Script (*.py)", "wide": True},
        {"arg": "--python-text", "tipo": "text", "wide": True},
        {"arg": "--python-expr", "tipo": "text", "wide": True}
    ]

    por_nombre = {"overwrites": '--python-expr import bpy; bpy.context.scene.render.use_overwrite = False; '
                                'bpy.context.scene.render.use_placeholder = True'}

    args_presets = [
        {"nombre": "Resolución X",
         "arg": '--python-expr import bpy; bpy.context.scene.render.resolution_x =',
         "tipo": "text", "validator": "int"},
        {"nombre": "Resolución Y",
         "arg": '--python-expr import bpy; bpy.context.scene.render.resolution_y =',
         "tipo": "text", "validator": "int"},
        {"nombre": "Resolución %",
         "arg": '--python-expr import bpy; bpy.context.scene.render.resolution_percentage =',
         "tipo": "text", "validator": "int"},
        {"nombre": "Overwrite Off\nPlaceholders On",
         "arg": por_nombre['overwrites']},
        {"nombre": "Usar distancia focal",
         "arg": '--python-expr import bpy; bpy.context.scene.camera.data.dof.use_dof =',
         "tipo": "bool"},
        {"nombre": "Cambiar mundo",
         "arg": '--python-expr import bpy; –python import bpy; bpy.context.scene.world = bpy.data.worlds["{}"]'.format(
             token_valor),
         "tipo": "text"},
        {"nombre": "Cycles samples",
         "arg": '--python-expr import bpy; bpy.context.scene.cycles.samples =',
         "tipo": "text", "validator": "int"},
        {"nombre": "Eevee samples",
         "arg": '--python-expr import bpy; bpy.context.scene.eevee.taa_render_samples =',
         "tipo": "text", "validator": "int"}
    ]


class VentanaArgsExtra(QtWidgets.QDialog, ui.argumentos_extra.Ui_ventana_argumentos_extra):
    def __init__(self, ventana, item_watchfolder=None, auxiliar_modos=False):
        super().__init__()
        self.setupUi(self)
        self.ventana = ventana
        self.interactuados_vacuos = None
        self.timer = None
        self.blinkeos = None
        self.blinkeos_max = 8
        self.items_interactuados = []
        self.highlight_color = self.obtener_highlight_color()
        self.stylesheet_default = self.btn_limpiar.styleSheet()

        ItemExtraArgs.id_custom = 0
        self.arbol.setColumnCount(len(ItemExtraArgs.lista_columnas))
        self.auxiliar_modos = auxiliar_modos

        self.nativos = QTreeWidgetItem(self.arbol)
        self.presets = QTreeWidgetItem(self.arbol)

        self.configurar_categorias()
        self.conectar_signals()
        self.configurar_vista()
        self.adaptacion_watchfolder(item_watchfolder)

        self.args_iniciales = self.item_activo.args_extra if self.item_activo else ""
        self.campo_args.setPlainText(self.args_iniciales)

        args_nativos = ArgsExtraBuiltin.args_nativos
        args_presets = ArgsExtraBuiltin.args_presets.copy()

        for args in args_nativos:
            ItemExtraArgs(**args, parent=self.nativos)

        custom_presets = self.leer_custom_presets()
        if isinstance(custom_presets, dict):  # si el archivo de custom presets tiene el formato viejo v3.1-
            customs = []
            for nombre, arg in custom_presets.items():
                customs.append({"nombre": nombre, "arg": arg, "tipo": "custom_preset"})
            custom_presets = customs

        args_presets.extend(custom_presets)
        for args in args_presets:
            ItemExtraArgs(**args, parent=self.presets)

    def obtener_highlight_color(self):
        paleta = app.palette()
        return paleta.color(paleta.Highlight)

    def conectar_signals(self):
        self.btn_guardar_preset.clicked.connect(self.agregar_custom_preset)
        self.botones_generales.accepted.connect(self.aceptar)
        self.botones_generales.rejected.connect(self.cancelar)
        self.btn_limpiar.clicked.connect(self.campo_args.clear)
        ItemExtraArgs.signals.agregar_arg.connect(self.agregar)
        ItemExtraArgs.signals.agregar_arg.connect(self.deshighlight_item)
        ItemExtraArgs.signals.browsear.connect(self.explorar)
        ItemExtraArgs.signals.renombrar.connect(self.renombrar_custom_preset)
        ItemExtraArgs.signals.borrar.connect(self.borrar_custom_preset)
        ItemExtraArgs.signals.interactuo.connect(self.interactuo_item)

    def interactuo_item(self, item):
        self.highlight_item(item)
        self.items_interactuados.append(item)

    def highlight_item(self, item):
        item.btn_arg.setStyleSheet(f"background-color: {self.highlight_color.name()}")

    def deshighlight_item(self, item):
        item.btn_arg.setStyleSheet(self.stylesheet_default)

    def iniciar_blinkeo(self):
        self.blinkeos = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.blinking_item)
        self.timer.start(200)

    def blinking_item(self):
        if self.blinkeos > self.blinkeos_max:
            self.timer.stop()
            return
        for item in self.interactuados_vacuos:
            if self.blinkeos % 2 == 0:
                self.highlight_item(item)
            else:
                self.deshighlight_item(item)
        self.blinkeos += 1

    def filtrar_interactuados_vacuos(self):
        return [item for item in self.items_interactuados if item.interaccion_vacua]

    def adaptacion_watchfolder(self, item_watchfolder):
        if self.auxiliar_modos:
            self.item_activo = None
            return
        if item_watchfolder:
            self.item_activo = item_watchfolder
            self.watchfolder = True
        else:
            self.watchfolder = False
            if self.ventana.item_unico_elegido():
                self.item_activo = self.ventana.item_unico_elegido()
            else:
                self.item_activo = self.ventana.tablaPrincipal.currentItem()

    def configurar_categorias(self):
        wgt = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wgt)
        lbl = QLabel(traducir("Built-in"))
        layout.addWidget(lbl)
        self.arbol.setItemWidget(self.nativos, 0, wgt)

        wgt = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(wgt)
        lbl = QLabel(traducir("Presets"))
        layout.addWidget(lbl)
        self.arbol.setItemWidget(self.presets, 0, wgt)

        self.nativos.setIcon(0, iconos.icono_blend)
        self.presets.setIcon(0, iconos.icono_presets)
        lado_icono = int(defaults_configuracion.icons_tablas_size * configuracion.factor_icons_size *
                         defaults_configuracion.atenuante_iconos_tablas / 100)
        size = QtCore.QSize(lado_icono, lado_icono)
        self.arbol.setIconSize(size)

    def configurar_vista(self):
        # self.arbol.setColumnWidth(ItemExtraArgs.columnas["interactivo"], 300)
        self.arbol.setColumnWidth(ItemExtraArgs.columnas["arg"], 200)
        self.arbol.header().setSectionResizeMode(ItemExtraArgs.columnas["interactivo"], QtWidgets.QHeaderView.Stretch)
        font = self.font()
        font.setPointSize(
            int(ConfiguracionVentana.size_default_textos["items_tablas"] * configuracion.factor_ui_font_size / 100))
        self.arbol.setFont(font)

        expansion = self.ventana.settings_ventana.expansion_argumentos_extra
        self.nativos.setExpanded(expansion["basicos"])
        self.presets.setExpanded(expansion["presets"])

    def agregar(self, item):
        arg_valor = item.arg_valor()
        if ArgsExtraBuiltin.token_valor in item.arg:
            arg = item.arg.replace(ArgsExtraBuiltin.token_valor, arg_valor)
        else:
            arg = item.arg + " " + arg_valor
        self.campo_args.appendPlainText(arg)

    @staticmethod
    def leer_custom_presets():
        try:
            with open(Datas.ruta_archivo_presets_args_extra, "r", encoding="utf8") as archivo_presets:
                custom_presets = json.load(archivo_presets)
        except Exception as e:
            print(e)
            return []
        return custom_presets

    def renombrar_custom_preset(self, item):
        nuevo_nombre = self.obtener_nombre_preset(item.nombre)
        if nuevo_nombre is None:
            return
        item.actualizar_nombre(nuevo_nombre)
        # self.custom_presets[item.id]["nombre"] = nuevo_nombre
        self.guardar_custom_presets()

    def borrar_custom_preset(self, item):
        # self.custom_presets[item.id] = None
        self.presets.removeChild(item)
        self.guardar_custom_presets()

    def obtener_nombre_preset(self, prelleno=""):
        text, ok_pressed = QInputDialog.getText(self, traducir("Custom preset"),
                                                traducir("Nombre"), QtWidgets.QLineEdit.Normal, prelleno)
        if ok_pressed and len(text):
            return text
        return None

    def agregar_custom_preset(self):
        nombre = self.obtener_nombre_preset()
        custom_preset = {"nombre": nombre, "arg": self.campo_args.toPlainText(), "tipo": "custom_preset"}
        # self.custom_presets.append(custom_preset)
        nuevo = ItemExtraArgs(**custom_preset, parent=self.presets)
        self.guardar_custom_presets()
        self.arbol.scrollToItem(nuevo, QtWidgets.QTreeWidget.EnsureVisible)

    def guardar_custom_presets(self):
        custom_presets = []
        for i in range(self.presets.childCount()):
            pres_i = self.presets.child(i)
            if pres_i.tipo != "custom_preset":
                continue
            custom_presets.append(self.presets.child(i).dict_guardable())

        # custom_presets = [cp for cp in self.custom_presets if cp is not None]
        try:
            with open(Datas.ruta_archivo_presets_args_extra, "w", encoding="utf8") as archivo_presets:
                archivo_presets.write(json.dumps(custom_presets))
        except IOError:
            pass

    def aceptar(self):
        if self.watchfolder:
            self.item_activo.args_extra = self.campo_args.toPlainText()
            self.close()
            return

        self.interactuados_vacuos = self.filtrar_interactuados_vacuos()
        if self.interactuados_vacuos:
            alerta, cb = alertas.alerta_checkbox("alerta_args_inaplicados")
            rta = alerta.exec_()
            if not rta == QMessageBox.StandardButton.Ok:
                self.arbol.scrollToItem(self.interactuados_vacuos[-1], QtWidgets.QTreeWidget.EnsureVisible)
                self.iniciar_blinkeo()
                return

        args_finales = self.campo_args.toPlainText()
        if args_finales == self.args_iniciales:
            self.close()
            return

        for item_i in self.ventana.tablaPrincipal.selectedItems():
            if item_i.estado == "renderizando":
                continue
            if item_i.estado == "terminado":
                item_i.reset()
            item_i.args_extra = args_finales

        self.ventana.tablaPrincipal.setCurrentItem(self.item_activo, self.ventana.columna["args_extra"])
        indice_scroll = self.ventana.tablaPrincipal.currentIndex()
        self.ventana.tablaPrincipal.scrollTo(indice_scroll)

        colas.guardar()

        self.close()

    def cancelar(self):
        self.close()

    def retranslateUi(self, ventana_argumentos_extra):
        self.setWindowTitle(traducir("Argumentos extra"))
        self.btn_limpiar.setText(traducir("Limpiar"))
        self.btn_guardar_preset.setText(traducir("Guardar como preset"))
        self.lbl_args.setText(traducir("Argumentos") + ":")

    def closeEvent(self, evento):
        self.ventana.settings_ventana.expansion_argumentos_extra["basicos"] = self.arbol.topLevelItem(0).isExpanded()
        self.ventana.settings_ventana.expansion_argumentos_extra["presets"] = self.arbol.topLevelItem(1).isExpanded()
        # self.ventana.activateWindow()
        evento.accept()

    def explorar(self, campo, filtro):
        archivo, _ = QFileDialog.getOpenFileName(self, filter=filtro)
        if archivo:
            campo.setText(archivo)


class DialogoNumeroSplits(QtWidgets.QDialog, ui.numero_splits.Ui_dialogo_numero_items):
    def __init__(self, parent, frames):
        super().__init__()
        self.setupUi(self)
        self.parent = parent
        self.numero_items.setMaximum(frames)
        self.aceptar_cancelar.rejected.connect(self.close)
        self.aceptar_cancelar.accepted.connect(self.acepto)

    def acepto(self):
        self.parent.splits = self.numero_items.value()

    def retranslateUi(self, _):
        self.setWindowTitle(traducir("Splits"))
        self.lbl_numero_items.setText(traducir("label_numero_splits"))


class VentanaCambiarRango(QtWidgets.QDialog, ui.cambiar_rango.Ui_ui_cambiar_rango):
    def __init__(self, ventana, item_activo):
        super().__init__()
        self.setupUi(self)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowTitle(traducir("Frames"))
        self.ventana = ventana
        self.item_activo = item_activo

        self.splits = None

        self.campo_inicio.setValidator(QtGui.QIntValidator())
        self.campo_fin.setValidator(QtGui.QIntValidator())
        self.campo_step.setValidator(QtGui.QIntValidator())

        self.propiedades = ["inicio", "fin", "step"]
        self.indicadores_relatividad = {"campo_inicio": self.lbl_offset_inicio, "campo_fin": self.lbl_offset_fin}

        self.campo_inicio.textChanged.connect(self.elige_limites)
        self.campo_fin.textChanged.connect(self.elige_limites)

        self.btn_partir_rango.setDisabled(True)
        self.campo_inicio.setText(self.item_activo.inicio)
        self.campo_fin.setText(self.item_activo.fin)
        self.campo_step.setText(self.item_activo.step)

        self.botones_generales.accepted.connect(self.aceptar)
        self.botones_generales.rejected.connect(self.cancelar)

        atajo_aceptar = QtWidgets.QShortcut(QtGui.QKeySequence('Return'),
                                            self)  # sto debería hacerse con defaultsun en verdas
        atajo_aceptar.activated.connect(self.aceptar)

        atajo_cerrar = QtWidgets.QShortcut(QtGui.QKeySequence('Esc'), self)
        atajo_cerrar.activated.connect(self.close)
        self.btn_partir_rango.clicked.connect(self.slpit_range)

    def slpit_range(self):
        items = self.ventana.tablaPrincipal.selectedItems()
        if len(items) > 1:
            self.split_y_asignar(items)
            return
        frames = int(self.campo_fin.text()) + 1 - int(self.campo_inicio.text())
        dialogo_splits = DialogoNumeroSplits(self, frames)
        if dialogo_splits.exec_():
            items_spliteados = [items[0]]
            while len(items_spliteados) < self.splits:
                items_spliteados.append(items[0].duplicar())
            self.split_y_asignar(items_spliteados)

    def split_y_asignar(self, items):
        numero_items = len(items)
        inicio = int(self.campo_inicio.text())
        fin = int(self.campo_fin.text()) + 1

        if numero_items > fin - inicio:  # si trata de distribuir entre más items que frames del rango
            numero_items = fin - inicio + 1
        split = array_split(range(inicio, fin), numero_items)

        for item, rango in zip(items, split):
            item.inicio = str(rango[0])
            item.fin = str(rango[-1])
            for propiedad in ["inicio", "fin"]:
                self.argumentar_propiedades_establecidas(item, propiedad)

        self.close()

    def retranslateUi(self, _):
        self.setWindowTitle(traducir("Cambiar rango frames"))
        text_inicio = traducir("Inicio:")
        text_fin = traducir("Fin:")


        self.lbl_frame_inicio_alt.setText(traducir("Inicio:"))
        self.lbl_frame_fin_alt.setText(traducir("Fin:"))
        txt_offset = "(" + traducir("Offset") + ")"
        self.lbl_offset_inicio.setText(txt_offset)
        self.lbl_offset_fin.setText(txt_offset)
        self.lbl_offset_inicio.hide()
        self.lbl_offset_fin.hide()
        self.lbl_explicacion_vacios.setText(traducir("Dejar campos vacíos para usar los valores originales"))

        self.lbl_explicacion_relativos.setText(traducir("explicacion_relativos"))
        self.lbl_frame_step.setText(traducir("Step") + ":")
        self.btn_partir_rango.setText(traducir("Split range"))
        self.btn_partir_rango.setToolTip(traducir("tooltip_split"))
        self.adjustSize()
        self.resize(self.minimumWidth(), self.minimumHeight())

    def closeEvent(self, evento):
        # todo: revisar si son necesarias todas estas macanas, parecen resabios de tiempos de ignorancia, y si no,
        #  quizás algo a aprender para iluminar los corazones de la patria
        self.campo_inicio.textChanged.disconnect()
        self.campo_fin.textChanged.disconnect()
        self.ventana.activateWindow()
        evento.accept()

    def perdio_foco(self):
        pass

    def elige_limites(self):
        campo = self.sender()
        valor = campo.text()
        if not len(valor):  # y hace falta valor, para poder continuar
            self.btn_partir_rango.setDisabled(True)
            return
        rel = self.es_relativo(valor)
        nombre_campo = campo.objectName()
        self.indicadores_relatividad[nombre_campo].setVisible(rel)
        no_split = any(
            self.es_relativo(valor_campo) for valor_campo in [self.campo_inicio.text(), self.campo_fin.text()])
        no_split = no_split or not self.campo_inicio.text() or not self.campo_fin.text()
        if not no_split:
            no_split = int(self.campo_inicio.text()) >= int(self.campo_fin.text())
        self.btn_partir_rango.setDisabled(no_split)

    def es_relativo(self, valor):
        return valor.startswith(("+", "-"))

    def argumentar_propiedades_establecidas(self, item, propiedad):
        if getattr(item, propiedad):
            item.propiedades_argumentar.add(propiedad)
        else:
            item.propiedades_argumentar.discard(propiedad)

    def asignacion_relativa(self, item, campo):
        nombre_propiedad = campo.objectName().lstrip("campo_")
        valor_previo = getattr(item, nombre_propiedad)
        if len(valor_previo):
            valor_nuevo = str(int(valor_previo) + int(campo.text()))
            if valor_previo.startswith(("+", "-")):  # si era relativo a la escena mantenerlo de esa manera
                valor_nuevo = valor_previo[0] + valor_nuevo
        else:
            valor_nuevo = campo.text()
        setattr(item, nombre_propiedad, valor_nuevo)

    def aceptar(self):
        asignacion_campo = {}
        for campo in [self.campo_inicio, self.campo_fin]:
            # demasiado abstracto?
            nombre_campo = campo.objectName()
            if len(campo.text()) and campo.text().startswith(("+", "-")):
                asignacion_campo[nombre_campo] = lambda item, pasar_campo: self.asignacion_relativa(item, pasar_campo)
            else:
                asignacion_campo[nombre_campo] = lambda item, pasar_campo: setattr(item,
                                                                                   pasar_campo.objectName().lstrip(
                                                                                       "campo_"),
                                                                                   pasar_campo.text())

        for item_i in self.ventana.tablaPrincipal.selectedItems():
            if modos.modo[item_i.modo].tipo == "frames":
                continue

            if item_i.estado == "terminado":
                item_i.reset()

            asignacion_campo["campo_inicio"](item_i, self.campo_inicio)
            asignacion_campo["campo_fin"](item_i, self.campo_fin)
            item_i.step = self.campo_step.text()
            for propiedad in self.propiedades:
                self.argumentar_propiedades_establecidas(item_i, propiedad)

        colas.guardar()
        self.close()

    def cancelar(self):
        self.close()


class DialogoFrames(QtWidgets.QDialog, ui.dialogo_frames.Ui_dialogo_frames):
    def __init__(self, item=None, nombre=None, multiples=False):
        super().__init__()
        self.setupUi(self)
        self.opcion_lista.setChecked(True)
        self.btn_a_lista.clicked.connect(self.rango_a_lista)
        if item:
            self.lbl_nombre_blend.setText(item.nombre_blend)
        elif nombre:
            self.lbl_nombre_blend.setText(nombre)
        else:
            self.lbl_nombre_blend.hide()
        if not multiples:
            self.chk_aplicar_todos.hide()
        for campo in {self.campo_lista, self.inicio, self.fin}:
            campo.textChanged.connect(self.actualizar_estado)
        if not self.lectura_frames_previos(item):
            self.campo_lista.setText("1")

    def lectura_frames_previos(self, item):
        exito = False
        self.campo_lista.setFocus()
        if item and item.frames:
            if ".." in item.frames:
                try:
                    inicio, fin = item.frames.split("..")
                    self.inicio.setValue(int(inicio))
                    self.inicio.setFocus()
                    self.fin.setValue(int(fin))
                    exito = True
                except IndexError:
                    pass
                return exito
            exito = True
            self.campo_lista.setText(item.frames)

        return exito

    def actualizar_estado(self):
        if self.sender().objectName() == "campo_lista":
            self.opcion_lista.setChecked(True)
            if self.campo_lista.text():
                self.aceptar_cancelar.button(QtWidgets.QDialogButtonBox.Ok).setDisabled(False)
                return
            self.aceptar_cancelar.button(QtWidgets.QDialogButtonBox.Ok).setDisabled(True)
            return
        self.opcion_rango.setChecked(True)
        self.aceptar_cancelar.button(QtWidgets.QDialogButtonBox.Ok).setDisabled(False)

    def lista_frames(self):
        parseado = []
        for parte in self.campo_lista.text().split(","):
            try:
                parseado.append(str(int(parte)))
            except ValueError as e:
                continue
        return ",".join(parseado)

    def rango(self):
        return self.inicio.text() + ".." + self.fin.text()

    def rango_a_lista(self):
        lista_previa = set(map(int, self.campo_lista.text().split(',')))

        inicio = int(self.inicio.text())
        fin = int(self.fin.text()) + 1
        range_numbers = set(range(inicio, fin))

        updated_numbers = lista_previa.union(range_numbers)

        lista_rango = ",".join(map(str, sorted(updated_numbers)))

        self.campo_lista.setText(lista_rango)
        self.opcion_lista.setChecked(True)

    def elegidos(self):
        if self.opcion_lista.isChecked():
            return self.lista_frames()
        return self.rango()

    def retranslateUi(self, _):
        self.lbl_inicio.setText(traducir("Inicio:"))
        self.lbl_fin.setText(traducir("Fin:"))
        self.opcion_rango.setText(traducir("Rango"))
        self.opcion_lista.setText(traducir("Lista"))
        self.chk_aplicar_todos.setText(traducir("usar_todos"))
        self.setWindowTitle(traducir("Elegir frames"))
        self.btn_a_lista.setText(traducir("Add range to list"))


class WidgetDistribuirBlenders(QtWidgets.QWidget, ui.widget_distribuir_blenders.Ui_widget_distribuir_blenders):
    def __init__(self, ventana):
        super().__init__()
        self.setupUi(self)
        self.ventana = ventana
        self.lista_blenders.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.btn_cancelar.clicked.connect(self.close)
        self.btn_distribuir.clicked.connect(self.autoasignar_blenders)

    def mostrar(self):
        self.lista_blenders.addItems(versiones_blender.blenders)
        self.show()

    def autoasignar_blenders(self):
        num_items_elegidos = len(self.ventana.tablaPrincipal.selectedItems())
        blenders_elegidos = self.lista_blenders.selectedItems()

        if not blenders_elegidos:
            return

        for i in range(num_items_elegidos):
            item_i = self.ventana.tablaPrincipal.selectedItems()[i]
            vuelta = i % len(blenders_elegidos)
            item_i.tag_blender = blenders_elegidos[vuelta].text()

        self.ventana.estado_reset_con_blends()
        self.ventana.tablaPrincipal.setCurrentItem(self.ventana.tablaPrincipal.selectedItems()[0],
                                                   self.ventana.columna["tag_blender"])
        indice_scroll = self.ventana.tablaPrincipal.currentIndex()
        self.ventana.tablaPrincipal.scrollTo(indice_scroll)

        self.close()

    def retranslateUi(self, _):
        self.setWindowTitle(traducir("Auto-asignar blenders"))
        self.btn_distribuir.setText(traducir("Distribuir"))
        self.btn_distribuir.setToolTip(traducir("distribuir_blenders"))
        self.btn_cancelar.setText(traducir("Cancelar"))






# class BotonBrowse(QtWidgets.QToolButton):
#     def __init__(self, funcion):
#         super().__init__()
#         self.setIcon(iconos.icono_browse)
#         self.clicked.connect(funcion)
#         text = traducir("Explorar")
#         self.setText(text)
#         self.setToolTip(text)

class SelectorRuta(QtWidgets.QHBoxLayout):
    def __init__(self, parent, tipo="archivo"):
        QtWidgets.QHBoxLayout.__init__(self)
        self.ventana = parent
        self.ruta = QtWidgets.QLineEdit()
        self.btn_explorar = BotonBrowse()
        self.btn_explorar.inicializar(self.explorar)
        self.addWidget(self.ruta)
        self.addWidget(self.btn_explorar)
        self.funcion_retorno = None
        self.ruta.textChanged.connect(self.enviar_ruta)
        self.tipo = tipo

    def enviar_ruta(self):
        if self.funcion_retorno:
            self.funcion_retorno(self.get())

    def explorar(self):
        if self.tipo == "archivo":
            ruta, _ = QFileDialog.getOpenFileUrl(self.ventana, traducir(""))
        else:
            ruta, _ = QFileDialog.getExistingDirectory(self.ventana, traducir(""))
        if ruta:
            self.ruta.setText(ruta.toString())
            return True
        return False

    def set(self, ruta):
        self.ruta.setText(ruta)

    def get(self):
        return self.ruta.text()


class SelectorWatchfolder(QtWidgets.QHBoxLayout):
    def __init__(self, ventana, watchfolder, item_folder=None):
        QtWidgets.QHBoxLayout.__init__(self)
        self.carpeta = QtWidgets.QLineEdit()
        self.ventana = ventana

        self.watchfolder = watchfolder
        if self.watchfolder:
            self.carpeta.setText(watchfolder.ruta)

        self.btn_explorar = BotonBrowse()
        self.btn_explorar.inicializar(self.explorar)

        self.btn_quitar = QtWidgets.QToolButton()
        self.btn_quitar.setIcon(iconos.icono_quitar_elegidos)
        self.btn_quitar.clicked.connect(self.quitar)
        self.btn_quitar.setText(traducir("Quitar"))
        self.btn_quitar.setToolTip(traducir("Quitar"))

        self.addWidget(self.carpeta)
        self.addWidget(self.btn_quitar)
        self.addWidget(self.btn_explorar)

        self.btn_explorar.setText(traducir("Explorar"))
        self.item_folder = item_folder

    def actualizar_iconos(self):
        self.btn_quitar.setIcon(iconos.icono_quitar_elegidos)
        # self.btn_explorar.vestir()

    def explorar(self):
        archivo = QFileDialog.getExistingDirectory(self.ventana, traducir("Elegir carpeta"))
        if archivo:
            self.carpeta.setText(archivo)
            return True
        return False

    def quitar(self):
        if self.item_folder:
            self.item_folder.parent.removeChild(self.item_folder)



class VentanaWatchfolderArbol(QtWidgets.QDialog, ui.watchfolders_arbol.Ui_Watchfolders):
    def __init__(self, ventana):
        super().__init__(ventana)
        self.ventana_extra_args = None
        self.setupUi(self)
        self.configurar_arbol()
        self.ventana = ventana
        self.item_folders = ItemTitulo(traducir("Carpetas"), parent=self.arbol)
        self.btn_agregar = self.configurar_boton_agregar()
        self.item_folders.agregar_wgt(1, self.btn_agregar, spacerR=True)
        self.item_escenas, self.grupo_escenas, self.botones_escenas = self.configurar_botones_escenas()
        # self.item_modo = ItemSelector(modos.lista_modos, traducir("Modo"), spacerR=True, parent=self.arbol)
        self.item_modo = self.configurar_item_modo()
        self.item_output = ItemTitulo(traducir("Nombrado de salida"), parent=self.arbol)
        self.item_output.setFirstColumnSpanned(True)
        self.item_modelo = ItemFantasma()
        self.grupo_nombrado = self.configurar_grupo_nombrado()
        self.item_extra_args, self.campo_extra_args = self.configurar_extra_args()
        self.popular()
        self.conectar_funciones()
        self.leer_previos()
        self.arbol.setTransparente()
        # self.arbol.ecualizar_altura_top_level_items()
        self.arbol.setItemDelegate(util_ui.ItemDelegate(height=30))

    def showEvent(self, event):
        self.actualizar_iconos()

    def cancelar(self):
        if not len(watch_folders.lista) or not watch_folders.activado:
            self.ventana.boton_watchfolder.setChecked(False)
        self.close()

    def aceptar(self):
        watch_folders.vaciar()
        for i in range(self.item_folders.childCount()):
            selector = self.item_folders.child(i).wgt_aux.layout()
            selector.watchfolder.ruta = selector.carpeta.text()
            watch_folders.actualizar_watchfolder(selector.watchfolder)



        if self.grupo_nombrado.opcion_usar_preset.isChecked():
            watch_folders.patron_nombrado = self.grupo_nombrado.selector_preset.currentData().patron

        elif self.grupo_nombrado.opcion_custom.isChecked() and any(self.item_modelo.patron_nombrado):
            watch_folders.patron_nombrado = self.item_modelo.patron_nombrado
        else:
            watch_folders.patron_nombrado = ItemCola.default_patron_nombrado

        watch_folders.escenas = self.grupo_escenas.checkedButton().objectName()
        watch_folders.args_extra = self.campo_extra_args.toPlainText()
        watch_folders.nombre_modo = self.item_modo.elegido()

        if not any(watch_folders.lista):
            watch_folders.activado = False
            self.ventana.boton_watchfolder.setChecked(False)
        else:
            watch_folders.activar(True)

        watch_folders.guardar()
        self.close()

    def conectar_funciones(self):
        self.btn_agregar.clicked.connect(self.agregar_y_explorar)
        self.aceptar_cancelar.rejected.connect(self.cancelar)
        self.accepted.connect(self.aceptar)

    def configurar_arbol(self):
        self.arbol.setColumnCount(2)
        self.arbol.setHeaderHidden(True)
        self.arbol.setColumnWidth(0, 100)

    def configurar_item_modo(self):
        lista_modos = [modos.traducir(modo) for modo in modos.lista_modos]
        return ItemSelector(lista_modos, lista_datas=modos.lista_modos, titulo=traducir("Modo"),
                            spacerR=True,
                            parent=self.arbol)

    def configurar_botones_escenas(self):
        grupo = QtWidgets.QButtonGroup()
        btn_activa = QtWidgets.QPushButton(traducir("Activa"))
        btn_activa.setObjectName("activa")
        btn_todas = QtWidgets.QPushButton(traducir("Add all"))
        btn_todas.setObjectName("todas")
        item = ItemTitulo(traducir("Escenas"), parent=self.arbol)

        for btn in [btn_activa, btn_todas]:
            btn.setCheckable(True)
            grupo.addButton(btn)
            item.agregar_wgt(1, btn, spacerR=btn == btn_todas)

        return item, grupo, {"activa": btn_activa, "todas": btn_todas}

    def actualizar_iconos(self):
        self.btn_agregar.setIcon(iconos.icono_add_folder)
        for i in range(self.item_folders.childCount()):
            selector = self.item_folders.child(i).wgt_aux.layout()
            selector.actualizar_iconos()

    def configurar_boton_agregar(self):
        boton = QtWidgets.QToolButton()
        boton.setToolTip((traducir("Agregar")))
        boton.setIcon(iconos.icono_add_folder)
        return boton

    def configurar_grupo_nombrado(self):
        grupo_nombrado = WidgetNombrado(self, self.item_modelo)
        # grupo_nombrado.grupo_nombrado.setTitle("")
        subitem_output = ItemWidgetBasico(self.item_output)
        subitem_output.crear_wgt(grupo_nombrado.arbol, 0, spacerR=True)
        subitem_output.setFirstColumnSpanned(True)
        grupo_nombrado.rellenar_presets("watchfolders")
        return grupo_nombrado

    def configurar_extra_args(self):
        item = ItemTitulo(texto=traducir("Argumentos extra"), parent=self.arbol)
        item.setFirstColumnSpanned(True)
        layout = QtWidgets.QVBoxLayout()
        lay_pb = QtWidgets.QHBoxLayout()
        btn_extra_args = QtWidgets.QPushButton(traducir("Establecer"))
        btn_extra_args.clicked.connect(self.set_extra_args)
        campo_extra_args = QtWidgets.QPlainTextEdit()

        spacers_params = (0, 0, QtWidgets.QSizePolicy.Expanding)
        spacer1 = QSpacerItem(*spacers_params)
        spacer2 = QSpacerItem(*spacers_params)
        lay_pb.addSpacerItem(spacer1)
        lay_pb.addWidget(btn_extra_args)
        lay_pb.addSpacerItem(spacer2)
        layout.addItem(lay_pb)
        layout.addWidget(campo_extra_args)
        layout.setSpacing(5)
        subitem_extra_args = ItemWidgetBasico(parent=item, spanned=True)
        subitem_extra_args.agregar_layout_wgt(layout, columna=0)

        return item, campo_extra_args

    def set_extra_args(self):
        self.ventana_extra_args = VentanaArgsExtra(self.ventana, auxiliar_modos=True)
        self.ventana_extra_args.botones_generales.accepted.disconnect(self.ventana_extra_args.aceptar)
        self.ventana_extra_args.botones_generales.accepted.connect(self.actualizar_extra_args)
        self.ventana_extra_args.exec_()

    def actualizar_extra_args(self):
        self.campo_extra_args.setPlainText(self.ventana_extra_args.campo_args.toPlainText())
        self.ventana_extra_args.close()
        self.item_extra_args.setExpanded(True)

    def popular(self):
        for watchfolder in watch_folders.lista:
            self.agregar_selector(watchfolder)
        self.item_folders.setExpanded(True)

    def agregar_selector(self, watchfolder=None):
        selector = self.crear_selector(watchfolder)
        self.fijar_selector(selector)
        # self.selectores_carpeta.append(nueva)
        return selector

    def crear_selector(self, watchfolder=None):
        if not watchfolder:
            watchfolder = WatchFolder("")
        selector = SelectorWatchfolder(self, watchfolder)
        return selector

    def fijar_selector(self, selector):
        item_nueva = ItemWidgetBasico(parent=self.item_folders)
        item_nueva.agregar_layout_wgt(selector, 0)
        item_nueva.setFirstColumnSpanned(True)
        selector.item_folder = item_nueva

    def agregar_y_explorar(self):
        nueva = self.crear_selector()
        if nueva.explorar():
            self.fijar_selector(nueva)

    def leer_previos(self):
        self.item_modelo.patron_nombrado = watch_folders.patron_nombrado
        self.item_modelo.args_extra = watch_folders.args_extra
        self.item_modelo.escenas = watch_folders.escenas
        self.item_modelo.nombre_modo = watch_folders.nombre_modo
        if self.item_modelo.args_extra:
            self.campo_extra_args.setPlainText(self.item_modelo.args_extra)
            self.item_extra_args.setExpanded(True)
        if self.item_modelo.patron_nombrado and self.item_modelo.patron_nombrado["ruta"] or \
                self.item_modelo.patron_nombrado["nombre"]:
            self.grupo_nombrado.opcion_custom.setChecked(True)
            self.item_output.setExpanded(True)
            patron = self.item_modelo.patron_nombrado
            self.grupo_nombrado.muestra_ruta.setText(auto_nombrado.patron_a_string(patron["ruta"]))
            self.grupo_nombrado.muestra_nombre.setText(auto_nombrado.patron_a_string(patron["nombre"]))
        escenas = self.item_modelo.escenas
        if escenas and escenas in self.botones_escenas:
            self.botones_escenas[escenas].setChecked(True)

        if self.item_modelo.nombre_modo:
            self.item_modo.set_actual(self.item_modelo.nombre_modo)

    def retranslateUi(self, _):
        self.setWindowTitle(traducir("Watchfolders"))


class VentanaScheduler(QtWidgets.QDialog, ui.scheduler.Ui_horarios_render):
    def __init__(self, ventana):
        super().__init__()
        self.setupUi(self)
        self.ventana = ventana

        self.aceptar_cancelar.accepted.connect(self.aceptar)
        self.aceptar_cancelar.rejected.connect(self.cancelar)
        self.chk_start.stateChanged.connect(self.chk_start_cambio)
        self.chk_end.stateChanged.connect(self.chk_end_cambio)
        self.asimilando = False

        self.atsart = {self.at_minutos_start, self.at_horas_start}
        self.instart = {self.in_minutos_start, self.in_horas_start}
        for control in self.atsart | self.instart:
            control.valueChanged.connect(self.cambio_start)

        self.atend = {self.at_minutos_end, self.at_horas_end}
        self.afterend = {self.after_minutos_end, self.after_horas_end}

        self.eligio_end = set()

        for control in self.atend | self.afterend:
            control.valueChanged.connect(self.cambio_end)

        self.asimilar_valores()

    def ajustar_interfaz_segun_estado_cola(self):
        for control in self.afterend:
            control.setDisabled(cola.estado == "renderizando")

    @property
    def hora_start(self):
        hora_start = QTime()
        hora_start.setHMS(self.at_horas_start.value(), self.at_minutos_start.value(), 0)
        return hora_start

    @property
    def hora_end(self):
        hora_end = QTime()
        hora_end.setHMS(self.at_horas_end.value(), self.at_minutos_end.value(), 0)
        return hora_end

    @property
    def dentro_de(self):
        dentro_de = QTime.currentTime().secsTo(self.hora_start)
        dentro_de = QTime(0, 0, 0).addSecs(dentro_de)
        return dentro_de

    def chk_start_cambio(self):
        if not self.chk_end.isChecked():
            return
        if self.chk_start.isChecked():
            self.desnulificar_controles(self.atend | self.afterend)
            if any(self.eligio_end):
                self.cambio_end_con_start()
        else:
            if any(self.eligio_end):
                self.nulificar_controles((self.atend | self.afterend) - self.eligio_end)
                self.desnulificar_controles(self.eligio_end)

    def chk_end_cambio(self):
        if not any(self.eligio_end):
            self.eligio_end = self.atend
        self.cambio_end(False)

    def toggle_bloquear_segnales(self, conjunto, bloquear):
        for control in conjunto:
            control.blockSignals(bloquear)

    def nulificar_controles(self, conjunto, nulo=" -- "):
        if conjunto is None:
            return
        for obj in conjunto:
            if nulo:
                self.toggle_bloquear_segnales(conjunto, True)
                obj.setValue(0)
                self.toggle_bloquear_segnales(conjunto, False)
            obj.setSpecialValueText(nulo)

    def desnulificar_controles(self, conjunto):
        self.nulificar_controles(conjunto, "")

    def cambio_end(self, chekar=True):
        if chekar and not self.asimilando:
            self.chk_end.setChecked(True)
        if self.chk_start.isChecked():
            self.cambio_end_con_start()
        else:
            self.cambio_end_sin_start()

    def cambio_end_con_start(self):
        if self.sender() in self.atend:
            self.eligio_end = self.atend
            self.actualizar_after()
            return
        if self.sender() in self.afterend:
            self.eligio_end = self.afterend
            self.actualizar_atend()
            return
        if self.eligio_end == self.atend:
            self.actualizar_after()
            return
        if self.eligio_end == self.afterend:
            self.actualizar_atend()

    def cambio_end_sin_start(self):
        if self.asimilando:
            if not schedules.usar_start:
                self.nulificar_controles((self.atend | self.afterend) - self.eligio_end)
            return
        for conjunto in [self.atend, self.afterend]:
            if self.sender() in conjunto:
                self.eligio_end = conjunto
                self.desnulificar_controles(conjunto)
            else:
                self.nulificar_controles(conjunto)

    def actualizar_after(self):
        after = self.hora_start.secsTo(self.hora_end)
        after = QTime(0, 0, 0).addSecs(after)
        self.toggle_bloquear_segnales(self.afterend, True)
        self.after_horas_end.setValue(after.hour())
        self.after_minutos_end.setValue(after.minute())
        self.toggle_bloquear_segnales(self.afterend, False)

    def actualizar_atend(self):
        atend = self.hora_start.addSecs(self.after_horas_end.value() * 3600 + self.after_minutos_end.value() * 60)
        self.toggle_bloquear_segnales(self.atend, True)
        self.at_horas_end.setValue(atend.hour())
        self.at_minutos_end.setValue(atend.minute())
        self.toggle_bloquear_segnales(self.atend, False)

    def cambio_start(self):
        if not self.asimilando:
            self.chk_start.setChecked(True)
        if self.sender() in self.instart:
            hora_start = QTime.currentTime().addSecs(
                self.in_horas_start.value() * 3600 + self.in_minutos_start.value() * 60)
            self.toggle_bloquear_segnales(self.atsart, True)
            self.at_minutos_start.setValue(hora_start.minute())
            self.at_horas_start.setValue(hora_start.hour())
            self.toggle_bloquear_segnales(self.atsart, False)
        else:
            dentro_de = self.dentro_de
            self.toggle_bloquear_segnales(self.instart, True)
            self.in_minutos_start.setValue(dentro_de.minute())
            self.in_horas_start.setValue(dentro_de.hour())
            self.toggle_bloquear_segnales(self.instart, False)
        if self.chk_end.isChecked():
            self.cambio_end_con_start()

    def asimilar_pares_valores(self, par):
        for elemento_valor in schedules.pares[par]:
            getattr(self, elemento_valor).setValue(getattr(schedules, elemento_valor))

    def asimilar_valores(self):
        self.asimilando = True

        self.asimilar_pares_valores("atstart")
        if schedules.tipo_end == "after":
            self.eligio_end = self.afterend
            self.asimilar_pares_valores("afterend")
        else:
            self.eligio_end = self.atend
            self.asimilar_pares_valores("atend")

        index_opcion_stop = self.opciones_stop.findData(schedules.opcion_stop, Qt.UserRole)
        self.opciones_stop.setCurrentIndex(index_opcion_stop)
        self.chk_start.setChecked(schedules.usar_start)
        self.chk_end.setChecked(schedules.usar_end)
        self.asimilando = False

    def cancelar(self):
        self.ventana.boton_scheduler.setChecked(schedules.activado)
        self.close()

    def aceptar(self):
        usa_start = self.chk_start.isChecked()
        usa_end = self.chk_end.isChecked()
        schedules.activado = usa_start or usa_end
        if not schedules.activado:
            schedules.desactivar()
        schedules.usar_start = usa_start
        schedules.at_horas_start = self.at_horas_start.value()
        schedules.at_minutos_start = self.at_minutos_start.value()
        schedules.usar_end = usa_end
        schedules.at_horas_end = self.at_horas_end.value()
        schedules.at_minutos_end = self.at_minutos_end.value()
        schedules.after_horas_end = self.after_horas_end.value()
        schedules.after_minutos_end = self.after_minutos_end.value()
        schedules.opcion_stop = self.opciones_stop.currentData(Qt.UserRole)
        if self.eligio_end == self.afterend and not usa_start:
            schedules.tipo_end = "after"
        else:
            schedules.tipo_end = "at"
        # self.ventana.render_aplazado(self.selector_horas.text(), self.selector_minutos.text())
        schedules.guardar()
        if schedules.activado:
            schedules.activar()
        self.ventana.boton_scheduler.setChecked(schedules.activado)
        self.close()

    def retranslateUi(self, selector_delay):
        self.setWindowTitle(traducir("Establecer horarios para renderizar"))
        self.lbl_at.setText(traducir("A las"))
        self.lbl_at_2.setText(traducir("A las"))
        self.lbl_from_now.setText(traducir("from_now"))
        self.lbl_after_starting.setText(traducir("after_starting"))
        self.chk_end.setText(traducir("Detener"))
        self.at_minutos_end.setSuffix(" min")
        self.at_minutos_start.setSuffix(" min")
        self.in_minutos_start.setSuffix(" min")
        self.after_minutos_end.setSuffix(" min")
        self.at_horas_end.setSuffix(" hr")
        self.at_horas_start.setSuffix(" hr")
        self.in_horas_start.setSuffix(" hr")
        self.after_horas_end.setSuffix(" hr")
        self.chk_start.setText(traducir("Iniciar"))
        self.lbl_opciones_stop.setText(traducir("scheduler_opciones_stop"))
        for opcion in schedules.opciones_stop:
            self.opciones_stop.addItem(traducir(schedules.opciones_stop[opcion]), opcion)


class SelectorColor(QtWidgets.QWidget):
    colorChanged = pyqtSignal()

    def __init__(self, *args, color=None, dict_rol=None, dict_key="color", opcional=False, **kwargs):
        super(SelectorColor, self).__init__(*args, **kwargs)

        self._color = None
        self._default = color

        self.btn_color = QtWidgets.QPushButton()
        self.btn_color.clicked.connect(self.onColorPicker)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(5, 4, 5, 4)
        layout.addWidget(self.btn_color)
        self.edit_hex = QtWidgets.QLineEdit()
        self.edit_hex.textChanged.connect(self.onHexChanged)
        layout.addWidget(self.edit_hex)
        if opcional:
            chk = QtWidgets.QCheckBox(traducir("Usar"))
            chk.setChecked(dict_rol["usar"])
            chk.toggled.connect(self.toggleo_uso)
            layout.addWidget(chk)
        layout.addItem(QtWidgets.QSpacerItem(5, 5, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.dict_rol = dict_rol
        self.dict_key = dict_key
        self.setColor(self._default)
        self.color_copiado = None

    def toggleo_uso(self, state):
        self.dict_rol["usar"] = state
        self.colorChanged.emit()

    def onHexChanged(self):
        self.setColor(self.edit_hex.text())

    def setColor(self, color):
        if color != self._color:
            self._color = color

        if self._color:
            # self.btn_color.setStyleSheet("background-color: %s;" % self._color)
            self.btn_color.setStyleSheet(
                "QPushButton { background-color: %s; color: black; border: 1px transparent; border-radius: 4px; }"
                "QPushButton:hover { background-color: %s;  border: 1px solid gray; border-radius: 4px;}"
                "QPushButton:pressed { background-color: %s; }" % (
                self._color, self._color, self.alterar_color(self._color, 0.6)))
            self.edit_hex.setText(self._color)
            self.dict_rol[self.dict_key] = self._color
            self.colorChanged.emit()
        else:
            self.setStyleSheet("")

    def alterar_color(self, color, factor):
        c = QtGui.QColor(color)
        c.setHsv(c.hue(), c.saturation(), int(clip(c.value() * factor, 0, 255)))
        return c.name()

    def color(self):
        return self._color

    def onColorPicker(self):
        dlg = QtWidgets.QColorDialog(self)
        dlg.setOption(QtWidgets.QColorDialog.DontUseNativeDialog)
        if self._color:
            dlg.setCurrentColor(QtGui.QColor(self._color))

        if dlg.exec_():
            self.setColor(dlg.currentColor().name())

    def mousePressEvent(self, e):
        if e.button() == Qt.RightButton:
            self.setColor(self._default)

        return super(SelectorColor, self).mousePressEvent(e)


class VentanaConfiguracion(QtWidgets.QDialog, ui.ventana_settings.Ui_ventana_configuracion):

    def __init__(self, ventana=None):
        super().__init__()

        self.setupUi(self)
        self.ventana = ventana
        self.settings_ventana = ventana.settings_ventana if ventana and ventana.settings_ventana else None

        self.backup_custom_skins = copy.deepcopy(
            configuracion.custom_skins)  # se podría hacer el backup recién antes del primer cambio como para pero es medio engorroso

        self.agregando_skin = False
        self.item_skin = None
        self.blender_inicial = versiones_blender.default

        self.idioma_inicial = configuracion.idioma  # estos se guardan por si cancela la configuración
        self.skin_inicial = configuracion.nombre_skin

        self.set_valores_iniciales()

        self.vestir_arbol()
        self.rellenar_secciones()

        self.conectar_signals()

        self.aplicar_seleccion_opciones()

        self.retraducir()
        # self.adjustSize()
        self.resize(500, 500)


        #lista_labels se usa para el ajuste de fonts
        self.lista_labels = [
            self.config_label_blender,
            self.config_boton_explorar,
            self.btn_explorar_sonido,
            self.chk_sonido_render,
            self.slider_altura_filas,
            self.slider_text_scale,
            self.slider_icons_scale,
            self.btn_ok,
            self.btn_cancelar,
            self.lbl_instancias_paralelas,
            self.chk_fallos,
            self.lbl_items_previos,
            self.lbl_finalizados,
            self.lbl_interrumpidos,
            self.chk_factory,
            self.lbl_viewer_imagenes,
            self.lbl_viewer_videos,
            self.chk_mantener_despierta,
            self.lbl_timeout,
            self.lbl_row_height,
            self.chk_atlernar_rows,
            self.chk_iconos,
            self.chk_texto,
            self.chk_auto_raise,
            self.lbl_apariencia_botones,
            self.lbl_filas,
            self.lbl_apariencia,
            self.lbl_scale,
            self.lbl_icons_scale,
            self.lbl_scale_button_text,
            self.lbl_scale_uitext,
            self.lbl_interfaz,
            self.lbl_sistema,
            self.lbl_renderizando,
            self.lbl_visor,
            self.lbl_font,
            self.selector_font,
            self.selector_idioma,
            self.selector_skin,
            self.selector_timeout,
            self.selector_instancias_paralelas,
            self.config_ubi_blender,
            self.ruta_sonido,
            self.selector_finalizados,
            self.selector_interrumpidos,
            self.lbl_idioma,
            self.lbl_skin,
            self.selector_viewer_imagenes,
            self.selector_viewer_secuencias,
            self.selector_viewer_videos
        ]

        self.selector_font.setCurrentText(configuracion.app_font) # se hace acá para que triggeree update para que la
        # primera vez que se abre el diálogo configuración ya salga con tamaños correctos

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_textos)

        self.exec()


    def setear_atajos(self):
        atajo_copiar = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+C"), self)
        atajo_copiar.activated.connect(self.copiar_color)
        atajo_pegar = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+V"), self)
        atajo_pegar.activated.connect(self.pegar_color)

    def conectar_signals(self):
        self.btn_ok.clicked.connect(self.config_aceptar)
        self.btn_cancelar.clicked.connect(self.config_cancelar)
        self.selector_idioma.currentIndexChanged.connect(self.cambiar_idioma)
        self.config_boton_explorar.inicializar(self.config_explorar_ruta_blender)
        self.selector_skin.currentIndexChanged.connect(self.cambiar_skin)
        self.btn_explorar_sonido.inicializar(self.explorar_sonido_render)
        self.chk_atlernar_rows.clicked.connect(self.cambio_alternar_rows)
        self.chk_auto_raise.clicked.connect(self.cambio_autoraise)
        self.slider_altura_filas.valueChanged.connect(self.cambio_altura_filas)
        self.chk_texto.clicked.connect(self.cambio_display_bootones)
        self.chk_iconos.clicked.connect(self.cambio_display_bootones)
        self.slider_text_scale.valueChanged.connect(self.cambio_text_scale)
        self.slider_uitext_scale.valueChanged.connect(self.cambio_ui_text_scale)
        self.slider_uitext_scale.sliderReleased.connect(self.actualizar_textos)
        self.slider_icons_scale.valueChanged.connect(self.cambio_icons_scale)
        for setting in [self.chk_iconos, self.chk_texto]:
            setting.toggled.connect(self.obligatoriedad_display)

        self.selector_viewer_imagenes.currentIndexChanged.connect(self.cambio_viewer)
        self.selector_viewer_secuencias.currentIndexChanged.connect(self.cambio_viewer)
        self.selector_viewer_videos.currentIndexChanged.connect(self.cambio_viewer)

        self.selector_font.currentFontChanged.connect(self.cambio_font)
        # self.selector_font.setMaximumHeight(00)
        self.selector_font.setStyleSheet("QFontComboBox { combobox-popup: 0; }")
        # self.selector_font.setView(QtWidgets.QListView())
        self.selector_font.setItemDelegate(util_ui.NoIconDelegate())
            # self.selector_font.setItemData(i, "", Qt.DecorationRole)  # Remove the icon by setting it to an empty string

        self.btn_agregar_skin.clicked.connect(self.add_skin)
        self.setear_atajos()
        self.btn_quitar_skin.clicked.connect(self.remove_skin)
        self.btn_exportar_skin.clicked.connect(self.exportar_skin)
        self.btn_importar_skin.clicked.connect(self.importar_skin)

    def set_valores_iniciales(self):

        self.slider_icons_scale.setValue(configuracion.factor_icons_size)
        self.slider_text_scale.setValue(configuracion.factor_buttons_font_size)
        self.slider_uitext_scale.setValue(configuracion.factor_ui_font_size)
        self.config_ubi_blender.setText(versiones_blender.ruta_default)
        self.chk_sonido_render.setChecked(configuracion.reproducir_sonido_render)
        if configuracion.sonido_render:
            self.ruta_sonido.setText(configuracion.sonido_render)
        self.chk_iconos.setChecked(configuracion.botones_iconos)
        self.chk_texto.setChecked(configuracion.botones_texto)
        self.chk_auto_raise.setChecked(configuracion.botones_autoraise)
        self.chk_atlernar_rows.setChecked(configuracion.alternar_color_filas)
        self.slider_altura_filas.setValue(configuracion.alto_filas)
        self.chk_fallos.setChecked(configuracion.tratar_fallidos)
        self.selector_instancias_paralelas.setValue(configuracion.instancias_max)
        self.chk_factory.setChecked(configuracion.blender_factory)
        self.chk_mantener_despierta.setChecked(configuracion.mantener_despierta)
        self.selector_timeout.setValue(configuracion.render_timeout)
        self.slider_icons_scale.default_value = 100
        self.slider_text_scale.default_value = 100
        self.slider_uitext_scale.default_value = 100
        self.slider_altura_filas.default_value = defaults_configuracion.alto_filas

        # self.btn_quitar_skin.setDisabled(True)

    def rellenar_secciones(self):
        for idioma in configuracion.opciones["idioma"]:
            self.selector_idioma.addItem(idioma, idioma)
        self.selector_idioma.setCurrentText(configuracion.idioma)

        self.rellenar_lista_skins()
        self.rellenar_editor_skin()

        for visor_imagen in configuracion.opciones["viewer_imagenes"]:
            self.selector_viewer_imagenes.addItem(traducir(visor_imagen), visor_imagen)

        for viewer_secuencias in configuracion.opciones["viewer_secuencias"]:
            self.selector_viewer_secuencias.addItem(traducir(viewer_secuencias), viewer_secuencias)

        for visor_video in configuracion.opciones["viewer_videos"]:
            self.selector_viewer_videos.addItem(traducir(visor_video), visor_video)

        self.rellenar_selector(self.selector_finalizados, "anteriores_terminados")
        self.rellenar_selector(self.selector_interrumpidos, "anteriores_interrumpidos")

        self.selector_finalizados.setCurrentText(traducir(configuracion.anteriores_terminados).capitalize())
        self.selector_interrumpidos.setCurrentText(
            traducir(configuracion.anteriores_interrumpidos).capitalize())

    def aplicar_seleccion_opciones(self):
        # esto es para los selectores en los que sirve aplicar la lectura con las señales ya conectadas
        self.selector_viewer_secuencias.setCurrentText(traducir(configuracion.viewer_secuencias))
        self.selector_viewer_videos.setCurrentText(traducir(configuracion.viewer_videos))
        self.selector_viewer_imagenes.setCurrentText(traducir(configuracion.viewer_imagenes))

    def rellenar_lista_skins(self):
        try:
            self.selector_skin.currentIndexChanged.disconnect()
        except TypeError:
            pass
        self.selector_skin.clear()
        for skin in defaults_configuracion.skins_builtin:
            self.selector_skin.addItem(traducir(skin), skin)
        for skin in configuracion.custom_skins:
            self.selector_skin.addItem(skin, skin)

        index = self.selector_skin.findData(configuracion.nombre_skin)
        if index != -1:  # If data is found
            self.selector_skin.setCurrentIndex(index)

        self.btn_quitar_skin.setEnabled(configuracion.nombre_skin not in defaults_configuracion.skins_builtin)
        self.btn_exportar_skin.setEnabled(configuracion.nombre_skin not in defaults_configuracion.skins_builtin)
        self.selector_skin.currentIndexChanged.connect(self.cambiar_skin)

    def vestir_arbol(self):
        self.arbol.setColumnCount(2)

        main_widgets = [self.wgt_lbl_interfaz, self.wgt_lbl_sistema, self.wgt_lbl_renderizando, self.wgt_lbl_visor]
        item_interfaz, item_sistema, item_renderizando, item_visor = self.subitemizar(self.arbol, main_widgets)

        _, self.item_skin = self.subitemizar(item_interfaz, [[self.wgt_lbl_idioma, self.wgt_idioma],
                                                             [self.wgt_lbl_skin, self.wgt_skin]])
        item_apariencia = self.subitemizar(item_interfaz, [self.wgt_lbl_apariencia])

        self.subitemizar(item_sistema, [[self.wgt_lbl_blender, self.wgt_ubi_blender]])
        self.subitemizar(item_apariencia, [[self.wgt_lbl_ap_botones, self.wgt_chks_botones]])

        self.subitemizar(item_apariencia, [[self.wgt_lbl_font, self.wgt_font]])

        item_columnas = self.subitemizar(item_apariencia, [self.wgt_lbl_filas])
        self.subitemizar(item_columnas, [[self.wgt_lbl_row_height, self.wgt_row_height], [None, self.wgt_chk_alternar]])

        for i in range(self.selector_font.count()):
            self.selector_font.setItemIcon(i, iconos.icono_blend)
        # item_buttons = self.subitemizar(item_apariencia, [self.wgt_lbl_ap_botones])
        # self.subitemizar(item_buttons, [self.wgt_chks_botones], offset=1)

        item_scale = self.subitemizar(item_apariencia, [self.wgt_lbl_scale])
        self.subitemizar(item_scale, [[self.wgt_lbl_scale_iconos, self.wgt_icons_scale],
                                      [self.wgt_lbl_scale_button_text, self.wgt_bt_text_scale],
                                      [self.wgt_lbl_scale_uitext, self.wgt_text_scale]])

        # item_font = self.subitemizar(item_interfaz, [self.wgt_lbl_font])
        # self.subitemizar(item_font, [self.wgt_font])

        subs_r = [self.wgt_chk_factory, self.wgt_chk_fallos, self.wgt_chk_despierta,
                  self.wgt_sonido]
        # subs_r.insert(2, self.wgt_paralelas) # de momento esta opcion no tiene más sentido y podría ser mal usada
        self.wgt_paralelas.hide()
        self.subitemizar(item_renderizando, [[self.wgt_lbl_timeout, self.wgt_timeout]])
        self.subitemizar(item_renderizando, subs_r, offset=1)

        item_previos = self.subitemizar(item_renderizando, [self.wgt_lbl_previos])

        self.subitemizar(item_previos, [[self.wgt_lbl_finalizados, self.wgt_selector_finalizados],
                                        [self.wgt_lbl_interrumpidos, self.wgt_selector_interrumpidos]])

        self.item_imagenes, self.item_secuencias, self.item_videos = self.subitemizar(item_visor, [
            [self.wgt_lbl_visor_imagenes, self.wgt_lbl_selector_imagenes],
            [self.wgt_lbl_visor_secuencias, self.wgt_lbl_selector_secuencias],
            [self.wgt_lbl_visor_videos, self.wgt_selector_videos]])

        # item_ruta_cimg = self.subitemizar(item_imagenes, [self.wgt_ruta_cviewer_imagenes], offset=1)
        # item_ruta_cseq = self.subitemizar(item_secuencias, [self.wgt_ruta_cviewer_secuencias], offset=1)
        # item_ruta_cvid = self.subitemizar(item_videos, [self.wgt_ruta_cviewer_videos], offset=1)

        # item_ruta_cimg.setHidden(True)

        self.arbol.setStyleSheet("QTreeWidget { background-color: lightgray; border: 0px solid black; }")
        item_interfaz.setExpanded(True)
        item_sistema.setExpanded(True)
        self.arbol.setItemDelegate(util_ui.ItemDelegate(height=15))

    def cambio_viewer(self):
        tipo = self.sender().objectName()
        item = {"selector_viewer_imagenes": self.item_imagenes,
                "selector_viewer_secuencias": self.item_secuencias,
                "selector_viewer_videos": self.item_videos}[tipo]
        if self.sender().currentData(Qt.UserRole) == "custom_viewer":
            self.agregar_selector_ruta_custom(tipo_visor=tipo.split("_")[-1], item_tipo=item)
            item.setExpanded(True)
        else:
            item.removeChild(item.child(0))

    def agregar_selector_ruta_custom(self, tipo_visor, item_tipo):
        selector = SelectorRuta(self)
        selector.set(configuracion.rutas_custom_viewers[tipo_visor])
        selector.funcion_retorno = lambda x: (configuracion.rutas_custom_viewers.update({tipo_visor: x}))
        selector.setContentsMargins(0, 0, 0, 3)
        selector.setSpacing(1)
        selector.addItem(QtWidgets.QSpacerItem(35, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum))
        wgt_selector = QtWidgets.QWidget()
        wgt_selector.setContentsMargins(0, 0, 0, 3)

        wgt_selector.setLayout(selector)
        self.subitemizar(item_tipo, [wgt_selector], 1)


    def subitemizar(self, parent: QTreeWidgetItem,
                    elementos: List[Union[QtWidgets.QWidget, List[QtWidgets.QWidget]]], offset: int = 0) -> List[
        QTreeWidgetItem]:
        # sacarla como utilidad general tomando arbol de parámetro, quizás conwrapper por las muchas llamadas? o quizás parte de Arbolwgts
        items = []
        for dupla in elementos:
            item_wi = QTreeWidgetItem(parent)
            items.append(item_wi)
            if isinstance(dupla, list):
                for i, widget in enumerate(dupla):
                    if widget is None:
                        continue
                    self.arbol.setItemWidget(item_wi, i, widget)
            else:
                self.arbol.setItemWidget(item_wi, offset, dupla)
        return items if len(items) > 1 else items[0]

    def mostrar_contextual_sliders(self, pos):
        self.context_menu.popup(self.mapToGlobal(pos))

    def rellenar_selector(self, selector, nombre_opciones_configuracion):
        for opcion in configuracion.opciones[nombre_opciones_configuracion]:
            selector.addItem(traducir(opcion).capitalize(), opcion)

    def traducir_selector(self, selector, nombre_opciones_configuracion):
        for index, opcion in enumerate(configuracion.opciones[nombre_opciones_configuracion]):
            selector.setItemText(index, traducir(opcion).capitalize())

    def explorar_sonido_render(self):
        filtro = "WAV (*.wav)"
        archivo, _ = QFileDialog.getOpenFileName(self, traducir("Elegir Archivos"), filter=filtro)
        if archivo:
            self.ruta_sonido.setText(archivo)
        else:
            self.ruta_sonido.setText(defaults_configuracion.sonido_render)

    def obligatoriedad_display(self):
        if self.sender().isChecked():
            return
        for setting in [self.chk_iconos, self.chk_texto]:
            if setting != self.sender():
                setting.setChecked(True)

    def cambio_font(self, font):
        app.setFont(font)
        configuracion.sig_cambio_skin.emit(self.chk_auto_raise.isChecked())
        self.cambio_text_scale()
        self.cambio_ui_text_scale()

    def cambio_text_scale(self):
        # font = self.arbol.font()
        # font.setPointSize(font.pointSize() + 2)
        # self.arbol.setFont(font)
        # self.ventana.cambiar_escala_textos(self.selector_text_scale.value()/100)
        configuracion.sig_cambio_escala_textos.emit(self.slider_text_scale.value(), self.slider_altura_filas.value())
        # configuracion.sig_cambio_escala_uitextos.emit(self.slider_uitext_scale.value())

    def cambio_ui_text_scale(self):
        self.ajustar_font_size()
        configuracion.sig_cambio_escala_uitextos.emit(self.slider_uitext_scale.value())

    def cambio_icons_scale(self):

        # self.ventana.cambiar_escala_iconos(self.selector_icons_scale.value()/100)
        configuracion.sig_cambio_escala_iconos.emit(self.slider_icons_scale.value())
        # configuracion.sig_cambio_altura_filas.emit(self.selector_altura_filas.value())

    def cambio_altura_filas(self):
        configuracion.sig_cambio_altura_filas.emit(self.slider_altura_filas.value())

    def cambio_autoraise(self):
        configuracion.sig_cambio_autoraise.emit(self.chk_auto_raise.isChecked())

    def cambio_display_bootones(self):
        configuracion.sig_cambio_display_botones.emit([self.chk_iconos.isChecked(), self.chk_texto.isChecked()])
        if self.ventana:
            QTimer.singleShot(50, self.ventana.adjustSize)

    def cambio_alternar_rows(self):
        configuracion.sig_cambio_alternar_filas.emit(self.chk_atlernar_rows.isChecked())

    def cambiar_idioma(self):  # nota: si cambia de idioma con blends en cola, creo que no voy a actualizar los estados
        # aux_idioma_previo = configuracion.idioma_elegido
        configuracion.idioma = self.selector_idioma.currentText()
        self.rellenar_lista_skins()
        self.rellenar_editor_skin()

        self.retraducir()

        self.traducir_selector(self.selector_finalizados, "anteriores_terminados")
        self.traducir_selector(self.selector_interrumpidos, "anteriores_interrumpidos")
        app_context.idioma = configuracion.idioma
        configuracion.sig_cambio_idioma.emit()
        if self.chk_texto.isChecked() and self.ventana:
            self.ventana.adjustSize()

        # self.cambiar_skin() # porque si no cambia el tamaño del as filas de la tabla

    def cambiar_skin(self):
        configuracion.nombre_skin = self.nombre_skin_actual()
        self.btn_quitar_skin.setEnabled(configuracion.nombre_skin not in defaults_configuracion.skins_builtin)
        self.btn_exportar_skin.setEnabled(configuracion.nombre_skin not in defaults_configuracion.skins_builtin)
        self.rellenar_editor_skin()
        # if self.chk_texto.isChecked():
        #     QTimer.singleShot(50, self.ventana.normalizar_botones_toolbars_verticales)
        self.aplicar_skin()

    def aplicar_skin(self):
        configuracion.setear_skin()
        configuracion.sig_cambio_skin.emit(self.chk_auto_raise.isChecked())

        self.cambio_text_scale()
        if self.ventana:
            self.ventana.actualizar_lista_estado()
            self.ventana.actualizar_color_items_desactivados()
        self.vestir_botones_iconos()

    def nombre_skin_actual(self):
        nombre = self.selector_skin.currentData(Qt.UserRole)
        return nombre if nombre else self.selector_skin.currentText()

    def exportar_skin(self):
        titulo = traducir("Guardar como")
        filtro = "JSON (*.json)"
        ruta = self.settings_ventana.ultimo_path if self.settings_ventana else ""
        nombre = self.nombre_skin_actual() + ".json"

        ruta = os.path.join(os.path.dirname(ruta), nombre) if ruta else nombre
        archivo, _ = QFileDialog.getSaveFileName(self, caption=titulo, directory=ruta, filter=filtro)
        if not archivo:
            return
        configuracion.exportar_skin(archivo)

    def importar_skin(self):
        filtro = "JSON (*.json)"
        ruta = self.settings_ventana.ultimo_path if self.settings_ventana else ""
        titulo = traducir("Elegir Archivos")
        ruta, _ = QFileDialog.getOpenFileName(self, caption=titulo, directory=ruta, filter=filtro)
        # ruta, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileName()", "", "(*.json)")
        if not ruta:
            return
        skins_nuevos = configuracion.importar_skins(ruta)
        if not skins_nuevos:
            return
        self.selector_skin.addItems(skins_nuevos)
        self.selector_skin.setCurrentIndex(self.selector_skin.count() - 1)

    def copiar_color(self):
        wgt_bajo_cursor = QApplication.widgetAt(QtGui.QCursor.pos())
        if not isinstance(wgt_bajo_cursor.parent(), SelectorColor):
            return
        self.color_copiado = wgt_bajo_cursor.parent()._color

    def pegar_color(self):
        wgt_bajo_cursor = QApplication.widgetAt(QtGui.QCursor.pos())
        if not isinstance(wgt_bajo_cursor.parent(), SelectorColor):
            return
        try:
            wgt_bajo_cursor.parent().setColor(self.color_copiado)
        except AttributeError as e:
            print(e)

    def config_aceptar(self):
        ruta = self.config_ubi_blender.text()
        es_valida = blenders.validar_ruta_someramente(ruta)
        if not es_valida:
            blenders.alerta_ubicacion_erronea()
            return


        versiones_blender.set_default(ruta, "")
        versiones_blender.guardar()

        configuracion.guardar_skins()

        configuracion.tratar_fallidos = self.chk_fallos.isChecked()

        configuracion.viewer_imagenes = self.selector_viewer_imagenes.currentData(Qt.UserRole)
        configuracion.viewer_secuencias = self.selector_viewer_secuencias.currentData(Qt.UserRole)
        configuracion.viewer_videos = self.selector_viewer_videos.currentData(Qt.UserRole)

        if self.ruta_sonido.text():
            configuracion.sonido_render = self.ruta_sonido.text()

        configuracion.reproducir_sonido_render = self.chk_sonido_render.isChecked()

        configuracion.mantener_despierta = self.chk_mantener_despierta.isChecked()

        configuracion.anteriores_terminados = self.selector_finalizados.currentData(Qt.UserRole)
        configuracion.anteriores_interrumpidos = self.selector_interrumpidos.currentData(Qt.UserRole)

        configuracion.blender_factory = self.chk_factory.isChecked()
        configuracion.instancias_max = self.selector_instancias_paralelas.value()

        configuracion.render_timeout = self.selector_timeout.value()

        configuracion.app_font = self.selector_font.currentText()

        configuracion.alternar_color_filas = self.chk_atlernar_rows.isChecked()
        configuracion.botones_iconos = self.chk_iconos.isChecked()
        configuracion.botones_texto = self.chk_texto.isChecked()
        configuracion.botones_autoraise = self.chk_auto_raise.isChecked()
        configuracion.alto_filas = self.slider_altura_filas.value()

        configuracion.factor_ui_font_size = self.slider_uitext_scale.value()
        configuracion.factor_buttons_font_size = self.slider_text_scale.value()
        configuracion.factor_icons_size = self.slider_icons_scale.value()

        configuracion.guardar()

        self.close()
        configuracion.sig_verificar_blender.emit(ruta)

    def config_cancelar(self):
        if not self.ventana:
            sys.exit()

        versiones_blender.default = self.blender_inicial
        configuracion.nombre_skin = self.skin_inicial
        configuracion.custom_skins = self.backup_custom_skins
        # if not self.selector_idioma.currentText() == self.idioma_inicial:
        #     self.cambiar_idioma()
        # esto es para que el tamaño de ventana se adapte
        configuracion.idioma = self.idioma_inicial
        self.selector_idioma.setCurrentText(configuracion.idioma)
        self.selector_skin.setCurrentText(traducir(configuracion.nombre_skin))
        # self.cambiar_skin()
        # self.cambiar_idioma()
        self.cambio_font(QFont(configuracion.app_font))
        configuracion.sig_cambio_alternar_filas.emit(None)
        configuracion.sig_cambio_autoraise.emit(None)
        configuracion.sig_cambio_display_botones.emit(None)
        configuracion.sig_cambio_altura_filas.emit(None)


        self.close()

    def config_explorar_ruta_blender(self):
        ruta_base = None
        if os.path.isfile(self.config_ubi_blender.text()):
            ruta_base = self.config_ubi_blender.text()

        explorar = blenders.explorar(self, ruta_base)
        if explorar:
            self.config_ubi_blender.setText(explorar)

    def vestir_botones_iconos(self):
        for boton in [self.btn_explorar_sonido, self.config_boton_explorar]:
            boton.vestir()
        self.btn_agregar_skin.setIcon(iconos.icono_mas)
        self.btn_quitar_skin.setIcon(iconos.icono_menos)
        self.btn_importar_skin.setIcon(iconos.icono_importar)
        self.setWindowIcon(iconos.icono_configuracion)
        # self.btn_editar_skin.setIcon(iconos.icono_configuracion)
        if self.item_skin.childCount():
            self.item_skin.setIcon(0, iconos.icono_configuracion)

        self.btn_exportar_skin.setIcon(iconos.icono_exportar)

    def retraducir(self):
        self.setWindowTitle(traducir("Configurar B-Renderon!"))
        self.lbl_skin.setText(traducir("Skin"))
        self.lbl_idioma.setText(traducir("Idioma"))

        self.btn_importar_skin.setToolTip(traducir("tooltip_importar_skin"))
        self.btn_exportar_skin.setToolTip(traducir("tooltip_exportar_skin"))
        self.btn_agregar_skin.setToolTip(traducir("tooltip_agregar_skin"))
        self.btn_quitar_skin.setToolTip(traducir("tooltip_quitar_skin"))

        self.config_label_blender.setText(traducir("Default Blender"))
        self.vestir_botones_iconos()
        self.chk_sonido_render.setText(traducir("Reproducir sonido"))

        self.slider_altura_filas.setToolTip(traducir("tooltip_reset_sliders"))
        self.slider_text_scale.setToolTip(traducir("tooltip_reset_sliders"))
        self.slider_icons_scale.setToolTip(traducir("tooltip_reset_sliders"))

        self.btn_ok.setText(traducir("Guardar"))
        self.btn_cancelar.setText(traducir("Cancel"))
        self.lbl_instancias_paralelas.setText(traducir("setting_instancias_default"))
        self.chk_fallos.setText(traducir("Intentar detectar y  continuar renders fallidos"))
        self.lbl_items_previos.setText(traducir("Previamente procesados"))
        self.lbl_finalizados.setText(traducir("finalizados").capitalize())
        self.lbl_interrumpidos.setText(traducir("interrumpidos").capitalize())

        self.chk_factory.setText(traducir("Usar blender en modo factory"))
        self.lbl_viewer_imagenes.setText(traducir("lbl_visor_imagenes"))
        self.lbl_viewer_videos.setText(traducir("lbl_visor_videos"))
        self.lbl_viewer_secuencias.setText(traducir("lbl_visor_secuencias"))
        self.chk_mantener_despierta.setText(traducir("mantener_despierta"))
        self.lbl_timeout.setText(traducir("lbl_timeout"))

        self.lbl_row_height.setText(traducir("Height"))
        self.chk_atlernar_rows.setText(traducir("filas_alternan"))
        self.chk_iconos.setText(traducir("Icons"))

        self.chk_texto.setText(traducir("Text"))
        self.chk_auto_raise.setText(traducir("Autoraise"))
        self.lbl_apariencia_botones.setText(traducir("Buttons display"))
        self.lbl_filas.setText(traducir("Queue rows"))

        self.lbl_interfaz.setText(traducir("Interfaz"))
        self.lbl_sistema.setText(traducir("Sistema"))
        self.lbl_renderizando.setText(traducir("Renderizando"))
        self.lbl_visor.setText(traducir("Visor de renders"))
        self.lbl_apariencia.setText(traducir("settings_apariencia"))

        self.lbl_scale.setText(traducir("Scale"))
        self.lbl_icons_scale.setText(traducir("Icons"))
        self.lbl_scale_button_text.setText(traducir("Buttons Text"))
        self.lbl_scale_uitext.setText(traducir("Ui Text"))

        self.lbl_font.setText(traducir("Font"))

    def ajustar_font_size(self):

        font = self.font()
        factor = self.slider_uitext_scale.value() / 100
        font.setPointSize(int(defaults_configuracion.font_size * factor))
        app.setFont(font)

        for widget in self.lista_labels:
            widget.setFont(font)

    def actualizar_textos(self):

        item_aux = ItemTitulo("", parent=self.arbol)
        self.arbol.takeTopLevelItem(self.arbol.indexOfTopLevelItem(item_aux))

    def retranslateUi(self, ventana_configuracion):
        pass

    def agregar_selector_color_dict(self, parent, dict_rol, nombre="", opcional=False):
        nombre = nombre if nombre else dict_rol["nombre"]
        color = dict_rol["color"]
        self.agregar_selector_color(parent, nombre, color, dict_rol, opcional=opcional)

    def agregar_selector_color(self, parent, nombre, color, dict_rol, dict_key="color", opcional=False):

        item = QTreeWidgetItem()
        item.setText(0, traducir(nombre).capitalize())
        item.setTextAlignment(0, Qt.AlignVCenter | Qt.AlignRight)

        parent.addChild(item)
        selector = SelectorColor(color=color, dict_rol=dict_rol, dict_key=dict_key, opcional=opcional)
        self.arbol.setItemWidget(item, 1, selector)
        selector.colorChanged.connect(self.aplicar_skin)

    def add_skin(self):
        nombre, ok_pressed = QInputDialog.getText(self, traducir("Custom skin"),
                                                  traducir("Nombre"), QtWidgets.QLineEdit.Normal, "")
        if not (ok_pressed and len(nombre)):
            return
        if nombre in [self.selector_skin.itemText(i) for i in range(self.selector_skin.count())]:
            alertas.alerta_generica("alerta_nombre_repetido")
            self.add_skin()
            return

        actual = self.selector_skin.currentData(Qt.UserRole)
        base = defaults_configuracion.skin_bdark if not actual or actual not in configuracion.custom_skins else \
            configuracion.skin_actual()
        configuracion.custom_skins[nombre] = copy.deepcopy(base)
        self.selector_skin.addItem(nombre, nombre)
        self.agregando_skin = True
        self.selector_skin.setCurrentIndex(self.selector_skin.count() - 1)

    def remove_skin(self):
        actual = self.selector_skin.currentIndex()
        if actual == -1:
            return
        nombre_actual = self.selector_skin.currentData(Qt.UserRole)
        self.selector_skin.removeItem(actual)
        configuracion.custom_skins.pop(nombre_actual)

    def rellenar_editor_skin(self):
        if not self.agregando_skin:
            expansiones = capturar_expansiones_subitems(self.item_skin)

        self.item_skin.takeChildren()
        if self.nombre_skin_actual() in defaults_configuracion.skins_builtin:
            self.item_skin.setIcon(0, QtGui.QIcon())
            return
        self.item_skin.setIcon(0, iconos.icono_configuracion)
        skin_actual = configuracion.skin_actual()

        item_main = ItemTitulo(traducir("Main"), parent=self.item_skin)
        item_disabled = ItemTitulo(traducir("Disabled"), parent=self.item_skin)
        item_progress_bar = ItemTitulo(traducir("Progress bar"), parent=self.item_skin)
        item_iconos = ItemTitulo(traducir("Icons"), parent=self.item_skin)

        for estado in ["enabled", "disabled"]:
            self.agregar_selector_color(item_iconos, nombre=estado, color=skin_actual["iconos"][estado],
                                        dict_rol=skin_actual["iconos"], dict_key=estado)

        for estado, colores in skin_actual["Progress bar"].items():
            item_estado = ItemTitulo(traduccion.estados(estado), 0, item_progress_bar)
            for nombre, color in colores.items():
                self.agregar_selector_color(item_estado, nombre, color=color, dict_rol=colores, dict_key=nombre)

        for info in skin_actual["Main"].values():
            self.agregar_selector_color(item_main, info["nombre"], color=info["color"], dict_rol=info)
        for info in skin_actual["Disabled"].values():
            self.agregar_selector_color(item_disabled, info["nombre"], color=info["color"], dict_rol=info)

        if self.agregando_skin:
            expandir_subitems_todos(self.item_skin)
            self.agregando_skin = False
        elif isinstance(expansiones, list):
            aplicar_expansiones_subitems(self.item_skin, expansiones[1])






class CheckBoxNumero(QtWidgets.QCheckBox):
    def __init__(self, number, parent=None):
        super().__init__(parent)
        self.number = number

    def paintEvent(self, event):
        # super().paintEvent(event)

        if self.isChecked():
            painter = QtGui.QPainter(self)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.setFont(QFont("Arial", 8))
            painter.setPen(Qt.black)

            # Get the checkbox rectangle
            option = QtWidgets.QStyleOptionButton()
            option.initFrom(self)
            checkbox_rect = self.style().subElementRect(self.style().SE_CheckBoxIndicator, option, self)

            # Calculate the center of the checkbox
            number_rect = checkbox_rect.center()

            # Draw the number at the center of the checkbox
            painter.drawText(checkbox_rect, Qt.AlignCenter, str(self.number))


class CenteredWidget(QtWidgets.QWidget):
    def __init__(self, widget, margenes=None, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(widget)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        margenes = margenes if margenes else (0,0,0,0)
        layout.setContentsMargins(*margenes)
        self.setLayout(layout)

class SignalsItemColeccion(QObject):
    token_quitar = pyqtSignal(str)
    quitar_todos_tokens = pyqtSignal()


class ItemColeccion(QTreeWidgetItem):

    def __init__(self, parent, ventana_colecciones, nombre, usar, conjunto):
        super().__init__(parent)  # Initialize QTreeWidgetItem

        self.editado = False
        self.edito_token = False
        self.ventana_colecciones = ventana_colecciones
        self.signals = SignalsItemColeccion()

        self.btn_token = QtWidgets.QToolButton()
        self.btn_token.setIconSize(QtCore.QSize(12, 12))
        self.btn_token.setStyleSheet("QToolButton { padding: 0px; }")
        self.btn_token.setCheckable(True)

        self.btn_token.clicked.connect(self.clickeo_token)
        # wgt_token = CenteredWidget(self.btn_token)
        # self.treeWidget().setItemWidget(self, 2, wgt_token)
        self.btn_token.setToolTip(traducir("tooltip_colection_token"))
        self.chk_usada = QtWidgets.QCheckBox()
        self.uso_original = usar
        self.chk_usada.setChecked(usar)
        self.conjunto = conjunto
        self.chk_usada.clicked.connect(self.toggle_jerarquico)
        self.chk_usada.setToolTip(traducir("tooltip_collection_exclusion"))

        self.iconito_edito_exclude = QLabel("")
        self.iconito_edito_token = QLabel("")

        self.configurar_interactivos()

        self.setText(0, nombre)
        self.nombre = nombre
        self.token_key = None

    def configurar_interactivos(self):
        self.asociar_iconito(self.chk_usada, self.iconito_edito_exclude,1)
        self.asociar_iconito(CenteredWidget(self.btn_token), self.iconito_edito_token, 2)

    def asociar_iconito(self, widget, wgt_iconito, columna):
        wgt_usar = QtWidgets.QWidget()
        ancho_spacer = int(VentanaColecciones.size_icono_edito * configuracion.factor_icons_size * 2 / 100)

        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        spacer = QtWidgets.QSpacerItem(ancho_spacer, 5, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        layout.addItem(spacer)

        layout.addWidget(widget)
        layout.addWidget(wgt_iconito)
        wgt_usar.setLayout(layout)
        self.treeWidget().setItemWidget(self, columna, wgt_usar)

    def clickeo_token(self, toggle):
        self.set_token_editado(True)
        modificadoras = QApplication.keyboardModifiers()
        if modificadoras == Qt.ShiftModifier:
            self.shift_click(toggle)
        elif modificadoras == Qt.AltModifier:
            self.alt_click()
        else:
            self.normal_click(toggle)

    def alt_click(self):
        pass
        # self.signals.quitar_todos_tokens.emit()
        # self.toggle_token()

    def shift_click(self, toggle):
        if toggle:
            self.agregar_token()
        else:
            self.quitar_token()

    def normal_click(self, toggle):
        if toggle:
            self.signals.quitar_todos_tokens.emit()
            self.btn_token.setChecked(True)
            self.agregar_token()
        else:
            self.quitar_token()


    def agregar_token(self):
        key = self.ventana_colecciones.siguiente_key()
        if not key:
            self.btn_token.setChecked(False)
            return
        self.btn_token.setText(key)
        self.token_key = key


    def quitar_token(self):
        self.btn_token.setChecked(False)
        self.signals.token_quitar.emit(self.token_key)
        self.btn_token.setText("")
        self.token_key = None


    def guardar_cambios(self):
        if not self.editado:
            return
        self.conjunto[self.nombre] = not self.usar

    @property
    def usar(self):
        return self.chk_usada.isChecked()

    def toggle_jerarquico(self):
        self.set_editado(True)

        # if self.usar: # para no propagar positivdad en vano
        #     modificadoras = QApplication.keyboardModifiers()
        #     if modificadoras != Qt.AltModifier:
        #         return
        # if not usar:
        self.recursion_toggle(self.usar, True)

    def recursion_toggle(self, valor, saltearme=False):
        if not saltearme:
            if not valor:
                usar = False
            elif self.usar:
                usar = True
            else:
                usar = self.uso_original
            #
            # if usar == self.uso_original:
            #     self.set_editado(False)

            self.chk_usada.setChecked(usar)

        for i in range(self.childCount()):
            self.child(i).recursion_toggle(valor)

    def toggle_editado(self):
        self.set_editado(not self.editado)

    def set_editado(self, valor):
        self.editado = valor
        if self.ventana_colecciones.pixmap_estado:
            self.set_iconito_exclusion(self.ventana_colecciones.pixmap_estado[self.editado])

    def set_token_editado(self, valor=True):
        self.edito_token = valor
        if self.ventana_colecciones.pixmap_estado:
            self.set_iconito_tokens(self.ventana_colecciones.pixmap_estado[self.edito_token])

    def set_iconito_exclusion(self, pixmap):
        self.iconito_edito_exclude.setPixmap(pixmap)

    def set_iconito_tokens(self, pixmap):
        self.iconito_edito_token.setPixmap(pixmap)



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


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):

        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class ManagementEstadoBotones:
    def __init__(self):
        self.requieren_items_en_cola = set()
        self.requieren_unico_elegido = set()
        self.requieren_items_elegidos = set()
        self.requieren_cola_detenida = set()
        self.requieren_cola_procesando = set()
        self.cola_renderizando = None

    def cambio_numero(self, numero):
        for btn in self.requieren_items_en_cola:
            if btn in self.requieren_cola_detenida and self.cola_renderizando:
                btn.setEnabled(False)
                continue
            btn.setEnabled(numero > 0)
        if not numero:
            self.cambio_seleccion(0)

    def cambio_seleccion(self, numero):
        for btn in self.requieren_unico_elegido:
            btn.setEnabled(numero == 1)
        for btn in self.requieren_items_elegidos:
            btn.setEnabled(numero > 0)

    def cambio_estado(self, renderizando):
        self.cola_renderizando = renderizando
        for btn in self.requieren_cola_detenida:
            btn.setEnabled(not renderizando)
        for btn in self.requieren_cola_procesando:
            btn.setEnabled(renderizando)


# implementacion ventana principal
class Ventana(QMainWindow, ui.ventana_principal_32.Ui_ui_ventana_principal):

    def __init__(self):
        super().__init__()
        app_context.ventana_principal = self
        self.agregados_tanda = None
        self.workers = []
        self.threadpool = QThreadPool()

        self.setupUi(self)

        self.columna = ItemCola.columna

        self.tablaPrincipal.hideColumn(self.columna["estado"])
        self.tablaPrincipal.itemDoubleClicked.connect(self.doble_click_item)

        self.splitter.splitterMoved.connect(self.verificar_colapso_splitter)

        screens = QtGui.QGuiApplication.screens()
        QtGui.QGuiApplication.instance().primaryScreenChanged.connect(self.restore_multipantallas)
        for screen in screens:
            screen.availableGeometryChanged.connect(self.restore_multipantallas)
        self.timer_resize = self.definir_timer_resize()
        self.restorear_multipantallas_onshow = False

        # self.test_statusbar = Statusbar.RenderonStatusbar(self, cola, self.statusbar)
        self.cola = cola

        cola.ventana = self
        cola.tablaPrincipal = self.tablaPrincipal

        self.ventana_log = VentanaInfo(self)
        self.ventana_log_individual = []

        self.widget_consola = self.definir_dock_consola()
        # self.toolBar.setWindowTitle("carranza")

        self.ventan_cambiar_blender = None
        self.dialogo_blend_no_encontrado = None
        self.lote_archivos_agregar = None
        self.ventana_estimar = None

        self.configurar_tablaprincipal()

        self.configurar_tabla_estados()
        # self.popular_selector_modos()

        self.selector_modo.accion_eligio = self.eligio_modo
        self.selector_modo.modos = modos
        self.selector_modo.filtro_nombre_visible = modos.traducir
        self.botones_modos = []
        self.popular_selector_modos()
        self.tlb_modos.setVisible(False)

        self.selector_cola.accion_eligio = self.eligio_cola

        self.actualizar_alternacion_filas()
        self.set_alto_filas()

        self.splitter.setSizes([780, 220])  # tmp arbitrario

        self.actualizar_selector_colas()
        colas.wgt_colas = self.selector_cola
        estilo_selectores = "padding-top: 3px; padding-bottom: 3px;"
        self.selector_cola.setStyleSheet(estilo_selectores)
        self.selector_modo.setStyleSheet(estilo_selectores)

        # botones status bar:

        self.manejo_statusbar = Statusbar.RenderonStatusbar(self, cola, self.statusbar, traduccion, plataforma)
        # self.statusbar.setStyleSheet(configuracion.fondo_status)

        # opciones statusbar. Desactivado por ahora
        self.btn_opciones_status = QtWidgets.QToolButton()
        # self.statusbar.addPermanentWidget(self.btn_opciones_status)
        self.btn_opciones_status.setIcon(iconos.icono_configuracion)
        self.menu_opciones_status = QMenu()
        self.menu_opciones_status.addAction("Estimated remaining")
        self.btn_opciones_status.setMenu(self.menu_opciones_status)
        self.btn_opciones_status.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # self.statusbar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        # self.statusbar.customContextMenuRequested.connect(self.mostrar_contextual_statusbar)

        self.setDockOptions(QMainWindow.AllowTabbedDocks | QMainWindow.AllowNestedDocks)
        self.ventana_watchfolders = None
        self.ventana_scheduler = None

        # menues y botones:

        self.contextual_general = None
        self.contextual_elegidos = None

        self.definicion_menu_contextual()

        colas.ventana = self
        watch_folders.ventana = self

        self.menu_colas = QMenu(self)
        self.browse_cola = None
        self.opc_cola_agregar_desde_archivo = None
        self.opcion_renombrar = None
        self.opcion_quitar_cola = None
        self.nueva_cola = None
        self.opc_exportar_cola = None
        self.colas_recientes = None
        self.rellenar_menu_colas()
        # self.menu_selector_colas = self.rellenar_selector_colas()
        self.btn_menu_colas.setMenu(self.menu_colas)

        self.menu_modos = QMenu(self)
        self.opc_modo_agregar_desde_archivo = None
        self.nuevo_modo = None
        self.opc_editar_modo = None
        self.opc_quitar_modo = None
        self.opc_restaurar = None

        self.rellenar_menu_modos()
        self.btn_menu_modos.setMenu(self.menu_modos)

        self.opciones_log = None
        self.opcion_limpiar_log = None
        self.opcion_abrir_individuales = None
        self.opcion_cerrar_logs = None

        self.opciones_detener = None
        self.opciones_render = None
        self.opcion_renderizar_elegidos = None

        self.detener_luego = None
        self.detener_luego_frame = None
        self.opcion_detener_elegidos = None
        self.definir_opciones_detener()
        self.definir_opciones_render()

        self.toolbars_verticales = set()

        self.botones_ajustes_jobs = [self.btn_reajustar_modo, self.btn_cambiar_version, self.btn_cambiar_escena,
                                     self.btn_view_layers, self.btn_camaras, self.btn_colecciones,
                                     self.btn_cambiar_rango, self.btn_nombrado,
                                     self.btn_argumentos_extra, self.btn_dispositivos]

        self.botones_ver_abrir = [self.btn_abrir_blend, self.btn_explorar_output, self.btn_ver_render, self.btn_livelog]

        self.botones_renderon = [self.btn_configuracion, self.btn_info]

        self.botones_queues = [self.btn_log]

        self.botones_sin_texto = [self.btn_menu_modos, self.btn_menu_colas]

        self.botones_render = [self.btn_render, self.btn_stop]

        self.botones_blends = [self.btn_agregar, self.btn_quitar_elegidos, self.btn_quitar_todos]

        self.botones_funciones_estado = [self.boton_watchfolder, self.boton_scheduler, self.boton_apagar]

        self.botones_menus_opciones = [self.btn_menu_modos, self.btn_menu_colas]

        self.botones_configurables = (self.botones_ajustes_jobs + self.botones_ver_abrir + self.botones_queues +
                                      self.botones_blends + self.botones_funciones_estado + self.botones_renderon +
                                      self.botones_render + self.botones_menus_opciones + self.botones_modos)

        self.conjuntos_botones = (
            self.botones_ajustes_jobs, self.botones_ver_abrir, self.botones_queues, self.botones_blends,
            self.botones_funciones_estado, self.botones_renderon, self.botones_render, self.botones_menus_opciones,
            self.botones_modos)

        self.widgets_toolbars = {}

        self.dict_toolbars = {
            "tlb_renderon": self.tlb_renderon,
            "tlb_render": self.tlb_render,
            "tlb_queues": self.tlb_queues,
            "tlb_blends": self.tlb_blends,
            "tlb_open": self.tlb_open,
            "tlb_state_functions": self.tlb_state_functions,
            "tlb_jobs_adjustments": self.tlb_jobs_adjustments,
            "tlb_modos": self.tlb_modos,

        }

        self.botones_toolbar = {
            "tlb_renderon": self.botones_renderon,
            "tlb_render": self.botones_render,
            "tlb_open": self.botones_ver_abrir,
            "tlb_state_functions": self.botones_funciones_estado,
            "tlb_jobs_adjustments": self.botones_ajustes_jobs,
            "tlb_modos": self.botones_modos
        }

        self.management_estados_botones = ManagementEstadoBotones()
        self.cola.signal_estado.connect(self.management_estados_botones.cambio_estado)

        self.management_estados_botones.requieren_cola_procesando.add(self.btn_stop)
        self.management_estados_botones.requieren_cola_detenida.update(
            [self.btn_render, self.btn_configuracion, self.selector_cola, self.btn_quitar_todos])
        self.management_estados_botones.requieren_items_en_cola.update([self.btn_render, self.btn_quitar_todos])
        self.management_estados_botones.requieren_items_elegidos.add(self.btn_quitar_elegidos)
        self.management_estados_botones.requieren_items_elegidos.update(self.botones_ajustes_jobs)
        self.management_estados_botones.requieren_items_elegidos.discard(self.btn_colecciones)
        self.management_estados_botones.requieren_items_elegidos.update(self.botones_modos)
        self.management_estados_botones.requieren_unico_elegido.update(
            [self.btn_colecciones, self.btn_abrir_blend, self.btn_ver_render, self.btn_explorar_output])

        self.labels_selectores = [self.lbl_colas, self.lbl_modo]

        self.toolbars = list(self.dict_toolbars.values())

        defaults_textos = ConfiguracionVentana.size_default_textos
        header_tp = self.tablaPrincipal.header()
        header_te = self.tabla_estados.header()
        self.widgets_texto_ajustables = [[(self.tabla_estados, self.tablaPrincipal), defaults_textos["items_tablas"]],
                                         [(header_te, header_tp), defaults_textos["headers_tablas"]],
                                         [(self.selector_modo, self.selector_cola), defaults_textos["selectores"]],
                                         [self.manejo_statusbar.widgets_all, defaults_textos["statusbar"]],
                                         [set(self.toolbars + self.labels_selectores), defaults_textos["botones"]],
                                         [[self.dock_consola.lbl_livelog, self.dock_consola.widget()],
                                          defaults_textos["general"]]
                                         ]

        self.configurar_botones_principales()
        self.conectar_funciones_botones()
        self.conectar_segnales_configuracion()

        self.management_estados_botones.cambio_numero(0)
        self.management_estados_botones.cambio_estado(renderizando=False)

        self.atajos = atajos_y_contextuales.AtajosPrincipalSinEntrada(self)

        self.menu_colores_background = self.definir_menu_colores()
        self.contextual_elegidos.entradas["cambiar_color"].setMenu(self.menu_colores_background)

        self.contextual_elegidos.entradas["reajustar_modo"].setMenu(self.selector_modo.menu)

        self.boton_taskbar = None
        self.progreso_taskbar = None

        self.actualizar_numero_blends(0)

        self.botones_comunes = [self.btn_agregar, self.btn_quitar_todos, self.btn_quitar_elegidos,
                                self.btn_cambiar_escena, self.btn_reajustar_modo,
                                self.btn_cambiar_rango,
                                self.btn_cambiar_version, self.btn_argumentos_extra, self.btn_dispositivos,
                                self.btn_explorar_output, self.btn_explorar_blend, self.btn_abrir_blend,
                                self.btn_ver_render,
                                self.btn_camaras, self.btn_view_layers, self.btn_nombrado, self.btn_log]

        self.actualizar_autoraise_botones()
        self.actualizar_display_botones()

        # self.tablaPrincipal.setStyleSheet("QTreeWidget::item { border-bottom: 1px gainsboro;}")
        # self.btn_configuracion.setStyleSheet("padding: 10px;")

        self.show()

        if plataforma == "Windows":
            self.definir_progreso_taskbar()


        self.settings_ventana = ConfiguracionVentana(self)

        self.cambiar_escala_textos(configuracion.factor_ui_font_size)
        self.cambiar_escala_textos_botones(configuracion.factor_buttons_font_size)
        self.cambiar_escala_iconos(configuracion.factor_icons_size)

        self.pos_splitter = self.inicializar_splitter()

        self.aux_buffer_cambio_seleccion = False

        self.retranslate_indicrectas()

        self.inicializacion_settings_ventana()

        # fecha = datetime.now()
        # mes = int(fecha.strftime("%m"))
        # dia = int(fecha.strftime("%d"))
        # if mes != 10 or not (15 <= dia <= 21):
        #     self.close()

        # self.adjustSize()
        # self.ajustar_columnas()

        try:
            if "-sq" in sys.argv:
                argumento_startup_queue = sys.argv.index("-sq")

                if len(sys.argv) > argumento_startup_queue + 1:
                    argumento_path = sys.argv[argumento_startup_queue + 1]
                    if not os.path.isfile(argumento_path):
                        argumento_path = ""
                else:
                    argumento_path = ""

                self.lectura_externa_launch(argumento_path)
            else:
                self.lectura_de_cola()
            # self.popular_selector_colas()
        except:
            pass

        self.validacion_inicial_blenders()



    def contextMenuEvent(self, event):

        menu = QMenu()

        labels = {}
        for titulo in ("Window", "Toolbars"):
            label_action = QtWidgets.QWidgetAction(self)
            label = QLabel(titulo)
            label.setEnabled(False)
            label.setAlignment(Qt.AlignCenter)
            label_action.setDefaultWidget(label)
            labels[titulo] = label_action

        menu.addAction(labels["Window"])
        menu.addSeparator()
        reset_ventana = QtWidgets.QAction(traducir("Reset size and position"), self)

        reset_ventana.triggered.connect(self.reset_pos_size_ventana)
        menu.addAction(reset_ventana)
        menu.addSeparator()

        menu.addAction(labels["Toolbars"])
        menu.addSeparator()
        # Create the default context menu
        menu_default = self.createPopupMenu()

        for action in menu_default.actions():
            if action.isSeparator():
                continue
            menu.addAction(action)

        # Show the context menu at the cursor position
        menu.exec_(event.globalPos())

    def set_item_background_color(self, color):
        elegidos = self.tablaPrincipal.selectedItems()
        for item in elegidos:
            item.bg_color = color

        self.tablaPrincipal.clearSelection()
        self.contextual_elegidos.qmenu.close()

    def definir_menu_colores(self):
        menu = QMenu()
        colores = ["#000000", "#444444", "#BBBBBB", "#FFFFFF"] # negro a blanco
        colores.extend(
            ["#FF4500", "#FF8C00", "#FFD700", "#ADFF2F", "#00FF00", "#20B2AA", "#00CED1", "#1E90FF", "#0000FF",
             "#8A2BE2", "#DA70D6", "#FF1493"])

        botones_colores = []
        for color in colores:
            btn_color = QtWidgets.QToolButton()
            btn_color.setStyleSheet(f"""
                background-color: {color}; 
                border: 1px solid black; 
                border-radius: 2px; 
            """)
            btn_color.clicked.connect(partial(self.set_item_background_color, color))
            botones_colores.append(btn_color)
        wgt = QtWidgets.QWidget()
        layout = QtWidgets.QGridLayout(wgt)

        for i, btn in enumerate(botones_colores):
            fila, columna = divmod(i, 4)
            layout.addWidget(btn, fila, columna, alignment=Qt.AlignHCenter | Qt.AlignVCenter)

        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(wgt)
        menu.addAction(action)

        btn_clear = QtWidgets.QToolButton()
        btn_clear.setToolTip(traducir("Limpiar"))
        btn_clear.clicked.connect(self.set_item_background_color)
        btn_clear.setIcon(iconos.icono_livelog_close)
        wgt = CenteredWidget(btn_clear, margenes=(0, 0, 0, 5))

        action = QtWidgets.QWidgetAction(self)
        action.setDefaultWidget(wgt)
        menu.addAction(action)

        return menu

    def validacion_inicial_blenders(self):
        ruta = versiones_blender.default.get("ruta", "")
        if not versiones_blender.buscar_nueva():
            self.verificar_ruta_blender_default(ruta)

    def validar_blender_default(self, valida, ruta, version):
        if not valida:
            blenders.alerta_ubicacion_erronea()
            VentanaConfiguracion(self)
            return
        versiones_blender.set_default(ruta, version)
        versiones_blender.guardar()

    def verificar_ruta_blender_default(self, ruta):
        blenders.validar_ruta_y_obtener_version(ruta, avisar=self.validar_blender_default)


        # versiones_blender.set_default(ruta, version)
        # versiones_blender.guardar()

    def item_unico_elegido(self):  # una especie de alternativa más sana a current item
        elegidos = self.tablaPrincipal.selectedItems()
        if not elegidos:
            return None
        if len(elegidos) > 1:
            return 0
        return elegidos[0]

    def hay_unico_elegido(self):
        return self.item_unico_elegido() not in (None, 0)

    def actualizar_botones_render_stop(self, renderizando):
        self.btn_stop.setEnabled(renderizando)
        self.btn_render.setEnabled(not renderizando)

    def cambio_estado_cola(self, renderizando):
        self.management_estados_botones.cambio_estado(renderizando)

    def inicializacion_settings_ventana(self):
        settings_ventana = self.settings_ventana
        self.reajustar_widgets()
        self.reajustar_ancho_minimo_ventana()

        settings_ventana.guardar_size_pos_inicial()
        settings_ventana.ajustar_columnas()
        self.tablaPrincipal.hideColumn(self.columna["estado"])
        settings_ventana.columnas_orden_por_defecto = self.tablaPrincipal.header().saveState()
        settings_ventana.columnas_estado_por_defecto = self.tabla_estados.header().saveState()
        settings_ventana.alineamiento_columnas = settings_ventana.default_alineamiento_columnas()
        settings_ventana.leer()


    def centrar_ventana(self):
        self.adjustSize()
        screen_geometry = QtWidgets.QDesktopWidget().screenGeometry()
        window_width, window_height = self.frameSize().width(), self.frameSize().height()
        center_x = (screen_geometry.width() - window_width) // 2
        center_y = (screen_geometry.height() - window_height) // 2

        self.move(center_x, center_y)

    def reset_pos_size_ventana(self):
        self.reajustar_ancho_minimo_ventana()
        # pos_inicial = self.settings_ventana.pos_inicial
        # if pos_inicial:
        #     self.move(pos_inicial)
        # size_inicial = self.settings_ventana.size_inicial
        # if size_inicial:
        #     self.resize(int(size_inicial["ancho"]*1.1), size_inicial["alto"])

    def conectar_segnales_configuracion(self):
        configuracion.sig_cambio_skin.connect(self.cambio_skin)
        configuracion.sig_cambio_idioma.connect(self.cambio_idioma)
        configuracion.sig_cambio_alternar_filas.connect(self.actualizar_alternacion_filas)
        configuracion.sig_cambio_autoraise.connect(self.actualizar_autoraise_botones)
        configuracion.sig_cambio_altura_filas.connect(self.set_alto_filas)
        configuracion.sig_cambio_escala_textos.connect(self.cambiar_escala_textos_botones)
        configuracion.sig_cambio_escala_uitextos.connect(self.cambiar_escala_textos)
        configuracion.sig_cambio_escala_iconos.connect(self.cambiar_escala_iconos)
        configuracion.sig_cambio_display_botones.connect(self.actualizar_display_botones)
        configuracion.sig_verificar_blender.connect(self.verificar_ruta_blender_default)

    def conectar_funciones_botones(self):
        self.btn_agregar.clicked.connect(self.elegir_archivos)
        self.btn_quitar_todos.clicked.connect(self.quitar_todos)
        self.btn_quitar_elegidos.clicked.connect(self.quitar_seleccionados)
        self.btn_explorar_blend.clicked.connect(self.explorar_ruta_blend)
        self.btn_explorar_blend.hide()
        self.btn_abrir_blend.clicked.connect(self.abrir_blend)
        self.btn_explorar_output.clicked.connect(self.explorar_ruta_output)
        self.btn_ver_render.setEnabled(False)
        self.btn_ver_render.clicked.connect(self.ver_render)
        self.btn_render.clicked.connect(self.accion_btn_render)
        self.btn_render.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn_render.customContextMenuRequested.connect(self.context_btn_render)
        self.btn_stop.clicked.connect(self.accion_btn_stop)
        self.btn_stop.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn_stop.customContextMenuRequested.connect(self.context_btn_stop)

        self.btn_configuracion.clicked.connect(self.configurar)
        self.btn_log.clicked.connect(self.mostrar_log)
        self.opciones_log = QMenu(self)
        self.opcion_limpiar_log = self.opciones_log.addAction("")
        self.opcion_limpiar_log.triggered.connect(self.limpiar_log)
        self.opcion_abrir_individuales = self.opciones_log.addAction("")
        self.opcion_abrir_individuales.triggered.connect(self.mostrar_logs_individuales)
        self.btn_log.setContextMenuPolicy(Qt.CustomContextMenu)
        self.btn_log.customContextMenuRequested.connect(self.mostrar_menu_log)
        self.opcion_cerrar_logs = self.opciones_log.addAction("")
        self.opcion_cerrar_logs.triggered.connect(self.cerrar_text_logs)

        # self.btn_reajustar_modo.clicked.connect(self.reajustar_modo)
        self.btn_reajustar_modo.setMenu(self.selector_modo.menu)
        self.btn_reajustar_modo.setStyleSheet("QToolButton::menu-indicator { image: none; }")

        self.btn_log.setMenu(self.opciones_log)

        # self.btn_cambiar_rango.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        # self.act_Reajustar_Modo.setMenu(self.contextual_elegidos.submenues["reajustar_modo"])
        # self.act_Reajustar_Modo.setPopupMode(QtWidgets.QToolButton.InstantPopup)

        # self.btn_reajustar_modo.setStyleSheet()
        self.btn_cambiar_version.clicked.connect(self.cambiar_blender)
        self.btn_cambiar_rango.clicked.connect(self.cambiar_rango)
        self.btn_argumentos_extra.clicked.connect(self.argumentos_extra)
        self.btn_dispositivos.clicked.connect(self.elegir_dispositivos)
        self.btn_cambiar_escena.clicked.connect(self.cambiar_escena)
        self.btn_camaras.clicked.connect(self.ajustar_camaras)
        self.btn_colecciones.clicked.connect(self.ajustar_colecciones)
        self.btn_view_layers.clicked.connect(self.ajustar_viewlayers)
        self.btn_nombrado.clicked.connect(self.ajustar_nombrado)

    def definir_opciones_detener(self):
        self.opciones_detener = QMenu(self)
        self.detener_luego = self.opciones_detener.addAction("")
        self.detener_luego.triggered.connect(self.cola.marca_tope)
        self.detener_luego_frame = self.opciones_detener.addAction("")
        self.detener_luego_frame.triggered.connect(self.cola.cortar_tras_frame)
        self.opciones_detener.addSeparator()
        self.opcion_detener_elegidos = self.opciones_detener.addAction("")
        self.opcion_detener_elegidos.triggered.connect(self.detener_render_item)
        self.btn_stop.setMenu(self.opciones_detener)

    def definir_opciones_render(self):
        self.opciones_render = QMenu(self)
        self.opcion_renderizar_elegidos = self.opciones_render.addAction("")
        self.opcion_renderizar_elegidos.triggered.connect(self.renderizar_item)
        self.btn_render.setMenu(self.opciones_render)

    def configurar_botones_principales(self):

        for toolbar in self.toolbars:
            toolbar.orientationChanged.connect(self.actualizacion_orientacion_toolbars)

        self.btn_stop.setDisabled(True)
        horizontal = QBoxLayout.LeftToRight
        vertical = QBoxLayout.TopToBottom

        for nombre_toolbar, conjunto_botones in self.botones_toolbar.items():
            toolbar = self.dict_toolbars[nombre_toolbar]
            wgt = QtWidgets.QWidget(toolbar)
            # wgt.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
            # toolbar.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
            self.widgets_toolbars[nombre_toolbar] = wgt
            toolbar.addWidget(wgt)

            direccion = vertical if toolbar.orientation() == Qt.Vertical else horizontal
            layout = QBoxLayout(direccion, wgt)
            layout.setContentsMargins(2, 2, 2, 2)
            layout.setSpacing(2)

            for boton in conjunto_botones:
                # if boton.toolButtonStyle() == QtCore.Qt.ToolButtonTextUnderIcon:
                #     boton.setMinimumSize(34, 34)
                layout.addWidget(boton, 0, Qt.AlignHCenter | Qt.AlignVCenter)



        self.boton_watchfolder.clicked.connect(self.boton_watchfolder_accion)
        self.boton_watchfolder.customContextMenuRequested.connect(self.boton_watchfolder_accion)
        self.boton_scheduler.clicked.connect(self.boton_scheduler_accion)
        self.boton_scheduler.customContextMenuRequested.connect(self.boton_scheduler_accion)
        self.boton_scheduler.setChecked(schedules.activado)


        self.btn_livelog.clicked.connect(self.dock_consola.mostrar)

        self.set_style_checkeables()

        self.btn_info.clicked.connect(self.acerca_de)

        self.tlb_blends.addWidget(self.wgt_blends)

        self.tlb_queues.addWidget(self.wgt_management_queues)

        self.set_icons_botones()



    def set_style_checkeables(self):
        skin = configuracion.skin_actual()
        bg_watchfolder = "00995F" if skin == "Bdark" else "3DE57A"
        bg_wf = skin["Main"][defaults_configuracion.watchfolders_background]["color"]
        bg_sc = skin["Main"][defaults_configuracion.scheduler_background]["color"]
        bg_sh = skin["Main"][defaults_configuracion.shutdown_background]["color"]
        self.boton_watchfolder.setStyleSheet(f"QToolButton:checked {{ background-color: {bg_wf} }}")
        self.boton_scheduler.setStyleSheet(f"QToolButton:checked {{ background-color: {bg_sc} }}")
        self.boton_apagar.setStyleSheet(f"QToolButton:checked {{ background-color: {bg_sh}; }}")

    def set_icons_botones(self):
        self.btn_log.setIcon(iconos.icono_log)
        self.boton_watchfolder.setIcon(iconos.icono_watch_folder)
        self.boton_scheduler.setIcon(iconos.icono_scheduler)
        # self.boton_apagar.setIcon([iconos.icono_apagar_off, iconos.icono_apagar_on][self.boton_apagar.isChecked()])
        self.boton_apagar.setIcon(iconos.icono_apagar_off)
        self.btn_livelog.setIcon(iconos.icono_bl_live_log)
        self.btn_info.setIcon(iconos.icono_info)
        self.btn_configuracion.setIcon(iconos.icono_configuracion)
        self.btn_agregar.setIcon(iconos.icono_agregar)
        self.btn_quitar_elegidos.setIcon(iconos.icono_quitar_elegidos)
        self.btn_quitar_todos.setIcon(iconos.icono_quitar_todos)
        self.btn_reajustar_modo.setIcon(iconos.icono_reajustar_modo)
        self.btn_cambiar_version.setIcon(iconos.icono_version)
        self.btn_cambiar_escena.setIcon(iconos.icono_escenas)
        self.btn_view_layers.setIcon(iconos.icono_viewlayers)
        self.btn_camaras.setIcon(iconos.icono_camaras)
        self.btn_colecciones.setIcon(iconos.icono_colecciones)
        self.btn_cambiar_rango.setIcon(iconos.icono_rango)
        self.btn_nombrado.setIcon(iconos.icono_setoutput)
        self.btn_argumentos_extra.setIcon(iconos.extra_args)
        self.btn_dispositivos.setIcon(iconos.icono_dispositivos)
        self.btn_abrir_blend.setIcon(iconos.icono_abrir_blend)
        self.btn_explorar_output.setIcon(iconos.icono_explorar_output)
        self.btn_ver_render.setIcon(iconos.icono_ver_render)
        self.btn_render.setIcon(iconos.icono_render)
        self.btn_stop.setIcon(iconos.icono_stop)
        self.btn_menu_colas.setIcon(iconos.icono_opciones_colas)
        self.btn_menu_colas.setStyleSheet("QToolButton::menu-indicator { image: none; }")
        self.btn_menu_modos.setIcon(iconos.icono_opciones_modos)
        self.btn_menu_modos.setStyleSheet("QToolButton::menu-indicator { image: none; }")
        self.dock_consola.vestir_iconos(iconos)

    def popular_selector_modos(self):
        self.selector_modo.traduccion = traduccion
        self.selector_modo.actualizar(modos)
        self.selector_modo.mostrar_actual()
        self.crear_botones_toolbar_modos()

    def crear_botones_toolbar_modos(self):
        self.botones_modos = []
        for accion in self.selector_modo.menu.actions():
            btn = QtWidgets.QToolButton()
            btn.setText(accion.text())
            btn.setIcon(iconos.icono_modo)
            btn.clicked.connect(accion.trigger)
            btn.setObjectName(accion.objectName())
            self.botones_modos.append(btn)
        self.actualizar_toolbar_modos()

    def actualizar_toolbar_modos(self):
        try:
            wgt = self.widgets_toolbars["tlb_modos"]
            layout = wgt.layout()
            for i in reversed(range(layout.count())):
                layout.itemAt(i).widget().setParent(None)

            for boton in self.botones_modos:
                layout.addWidget(boton, 0, Qt.AlignHCenter | Qt.AlignVCenter)
        except AttributeError:
            pass

    # def corregir_alineamiento_header_tp(self, logicalIndex):
    #
    #     header_item = self.tablaPrincipal.horizontalH
    #
    #     title = header_item.text()
    #     if header.fontMetrics().width(title) > newSize:
    #         header_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    #     else:
    #         header_item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

    def configurar_tablaprincipal(self):
        self.tablaPrincipal.ventana_principal = self
        # self.tablaPrincipal.viewport().setAcceptDrops(True)  # verificar si hacen falta ambas o cuál
        self.tablaPrincipal.selectionModel().selectionChanged.connect(self.cambio_seleccion)
        self.tablaPrincipal.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tablaPrincipal.customContextMenuRequested.connect(self.menu_contextual)

        self.tablaPrincipal.dobleclick_espacio.connect(self.elegir_archivos)

        self.tablaPrincipal.drop_interno.connect(self.estado_reset_con_blends)
        self.tablaPrincipal.drop_interno.connect(
            colas.guardar)  # esto es un backup para deshacer en caso que desaparezca
        self.tablaPrincipal.drop_interno_post_acomodo.connect(self.actualizar_lista_estado)

        self.tablaPrincipal.items_comidos.connect(self.releer_cola)
        # un item por drop. Un workaround para un bug muy ocasional

        header_tp = HeaderTablas(self.tablaPrincipal)
        self.tablaPrincipal.setHeader(header_tp)

        self.tablaPrincipal.header().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tablaPrincipal.header().customContextMenuRequested.connect(self.contextual_header_tp)
        self.tablaPrincipal.header().setSectionsMovable(True)
        self.tablaPrincipal.header().setFirstSectionMovable(True)

        # self.tablaPrincipal.itemChanged.connect(self.actualizar_lista_estado)

        self.tablaPrincipal.header().setToolTip(traducir("header tooltip"))
        self.tablaPrincipal.verticalScrollBar().valueChanged.connect(self.sincronizar_scroll_estados)

    def configurar_tabla_estados(self):
        header_tp = HeaderTablas(self.tabla_estados)
        self.tabla_estados.setHeader(header_tp)

        self.tabla_estados.header().setContextMenuPolicy(Qt.CustomContextMenu)
        self.tabla_estados.header().customContextMenuRequested.connect(self.contextual_header_estados)

        self.tabla_estados.selectionModel().selectionChanged.connect(self.sincronizar_seleccion_tablas)
        self.tabla_estados.selectionModel().setObjectName("seleccion_estados")
        self.tabla_estados.verticalScrollBar().valueChanged.connect(self.sincronizar_scroll_tp)
        self.tabla_estados.adjustSize()

    def definir_dock_consola(self):
        self.dock_consola.cola = self.cola
        self.dock_consola.setVisible(False)
        self.dock_consola.configuracion = configuracion
        widget_consola = QtWidgets.QPlainTextEdit()
        # widget_consola = WidgetConsola(self) # eso era para agregar botones, de momento no lo voy a usar
        self.dock_consola.setWidget(widget_consola)

        self.dock_consola.vestir_iconos(iconos)
        self.dock_consola.set_tooltips(traduccion)
        # self.dock_consola.visibilityChanged.connect(self.adjustSize)
        # self.dock_consola.topLevelChanged.connect(self.adjustSize)
        self.dock_consola.topLevelChanged.connect(self.consola_titular)
        # self.dock_consola.visibilityChanged.connect(self.adjustSize)
        # self.dock_consola.visibilityChanged.connect(self.test_livelog)
        self.dock_consola.dockLocationChanged.connect(self.rehabilitar_dock_consola)
        self.resizeDocks([self.dock_consola], [1], Qt.Horizontal)

        widget_consola.setMinimumHeight(250)
        self.consola_titular()
        self.consola_sin_elementos(widget_consola)

        return widget_consola



    def rehabilitar_dock_consola(self):
        self.dock_consola.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea | Qt.TopDockWidgetArea |
                                          Qt.BottomDockWidgetArea
                                          )

    def actualizar_display_botones(self, valores=None):
        for toolbar in self.toolbars:
            if toolbar.orientation() == Qt.Vertical:
                self.toolbars_verticales.add(toolbar.objectName())


        valor_icono, valor_texto = [configuracion.botones_iconos,
                                    configuracion.botones_texto] if valores is None else valores
        opciones_ver_botones = [Qt.ToolButtonIconOnly, Qt.ToolButtonTextOnly,
                                Qt.ToolButtonTextUnderIcon]
        num_opcion = valor_icono + valor_texto * 2 - 1
        opcion = opciones_ver_botones[num_opcion]
        # minimo_botones = int(configuracion.factor_icons_size/4)

        for boton in self.botones_configurables:
            boton.setToolButtonStyle(opcion)
            # boton.setMinimumSize(boton.width(), boton.height())

        self.reajustar_widgets()

        # if valor_texto:
        #     QTimer.singleShot(50, self.normalizar_botones_toolbars_verticales)
        #     # self.normalizar_botones_toolbars_verticales()
        # else:
        #     conjunto = [btn for botones_toolbar in self.botones_toolbar.values() for btn in botones_toolbar]
        #     self.desnormalizar_botones_toolbar(conjunto)

        for lbl in (self.lbl_colas, self.lbl_modo):
            lbl.show() if valor_texto else lbl.hide()

        self.reajustar_ancho_minimo_ventana()

    def reajustar_widgets(self):
        widgets = [self.wgt_blends, self.wgt_management_queues]
        if self.widgets_toolbars:
            widgets.extend([wgt for wgt in self.widgets_toolbars.values()])
        for wgt in widgets:
            wgt.adjustSize()

    def actualizar_autoraise_botones(self, valor=None):
        valor = configuracion.botones_autoraise if valor is None else valor
        for boton in self.botones_configurables + self.botones_sin_texto:
            boton.setAutoRaise(valor)

    def cambio_idioma(self):
        for i in range(self.tablaPrincipal.topLevelItemCount()):
            item_i = self.tablaPrincipal.topLevelItem(i)
            item_i.estado = item_i.estado  # actualizar el texto

        self.retranslateUi(self)
        self.retranslate_indicrectas()
        self.rellenar_menu_contextual()
        self.manejo_statusbar.actualizar_estado()
        self.actualizar_numero_blends()

        self.popular_selector_modos()
        self.rellenar_menu_colas()
        self.rellenar_menu_modos()
        # for indice, modo in enumerate(configuracion.modos):
        #     ventana_principal.selector_modo.setItemText(indice, traducir(modo))

        self.settings_ventana.ajustar_columnas()
        self.reajustar_widgets()
        self.reajustar_ancho_minimo_ventana()

        # self.adjustSize()

    def cambio_skin(self, autoraise):
        # self.statusbar.setStyleSheet(configuracion.fondo_status)
        self.set_icons_botones()
        self.set_style_checkeables()
        self.actualizar_autoraise_botones(autoraise)

    def retranslateUi(self, ui_ventana_principal):

        self.setWindowTitle(InfoRenderon.titulo)

        columnas = ItemCola.columna  # esto porque el retranslate se ejecuta antes que el init
        for col in columnas:
            self.tablaPrincipal.headerItem().setText(columnas[col], traducir(col).capitalize())

        self.tabla_estados.headerItem().setText(0, traducir("estado"))
        self.tabla_estados.headerItem().setText(1, traducir("Frame(s)"))

        self.tabla_estados.headerItem().setToolTip(1, traducir("tooltip_columna_frames"))

        self.tabla_estados.headerItem().setText(2, traducir("ETA"))
        self.tabla_estados.headerItem().setToolTip(2, traducir("tooltip_eta"))

        self.lbl_colas.setText(traducir("Colas"))
        #
        self.lbl_modo.setText(traducir("modo_ingesta"))

        # if not configuracion.botones_texto:
        #     for lbl in (self.lbl_colas, self.lbl_modo):
        #         lbl.hide()
        # self.lbl_modo.setMargin(5)
        # self.lbl_colas.setMargin(5)

        self.tlb_renderon.setWindowTitle(traducir("Info/Settings"))
        self.tlb_blends.setWindowTitle(traducir("Adding/Removing"))
        self.tlb_open.setWindowTitle(traducir("Open/View"))
        self.tlb_queues.setWindowTitle(traducir("Queues Management"))
        self.tlb_jobs_adjustments.setWindowTitle(traducir("Jobs Adjustments"))
        self.tlb_render.setWindowTitle(traducir("Queue processing"))
        self.tlb_state_functions.setWindowTitle(traducir("State Functions"))
        self.tlb_modos.setWindowTitle(traducir("Modo"))

        self.btn_configuracion.setText(traducir("Configuración"))
        self.btn_configuracion.setToolTip(traducir("Configuración"))
        self.btn_quitar_elegidos.setText(traducir("Quitar Seleccionados"))
        self.btn_quitar_elegidos.setToolTip(traducir("Quitar Seleccionados") + atajos_formateados("quitar"))
        self.btn_argumentos_extra.setText(traducir("Argumentos Extra"))
        self.btn_argumentos_extra.setToolTip(
            traducir("Argumentos Extra") + atajos_formateados("argumentos_extra"))
        self.btn_dispositivos.setText(traducir("[BOTON]_dispositivos"))
        self.btn_dispositivos.setToolTip(
            traducir("[BOTON]_dispositivos") + atajos_formateados("dispositivos"))
        self.btn_cambiar_escena.setText(traducir("Cambiar Escena"))
        self.btn_cambiar_escena.setToolTip(traducir("Cambiar Escena") + atajos_formateados("cambiar_escena"))
        self.btn_cambiar_rango.setText(traducir("Cambiar rango frames"))
        self.btn_cambiar_rango.setToolTip(
            traducir("Cambiar rango frames") + atajos_formateados("cambiar_rango"))
        self.btn_cambiar_version.setText(traducir("Versión de Blender"))
        self.btn_cambiar_version.setToolTip(
            traducir("Versión de Blender") + atajos_formateados("cambiar_blender"))
        self.btn_explorar_blend.setText(traducir("Explorar ruta Blend"))
        self.btn_explorar_blend.setToolTip(
            traducir("Explorar ruta Blend") + atajos_formateados("explorar_ruta_blend"))
        self.btn_abrir_blend.setText(traducir("btn_abrir_blend"))
        self.btn_abrir_blend.setToolTip(traducir("btn_abrir_blend") + atajos_formateados("abrir_blend"))
        self.btn_explorar_output.setText(traducir("Explorar ruta salida"))
        self.btn_explorar_output.setToolTip(
            traducir("Explorar ruta salida") + atajos_formateados("explorar_output"))
        self.btn_camaras.setText(traducir("Cámaras"))
        self.btn_camaras.setToolTip(traducir("Cámaras") + atajos_formateados("camaras"))
        self.btn_colecciones.setText(traducir("Colecciones"))
        self.btn_colecciones.setToolTip(traducir("Colecciones") + atajos_formateados("colecciones"))
        self.btn_view_layers.setText(traducir("View Layers"))
        self.btn_view_layers.setToolTip(traducir("View Layers") + atajos_formateados("view_layers"))
        self.btn_nombrado.setText(traducir("Nombrado Salida"))
        self.btn_nombrado.setToolTip(traducir("Nombrado Salida") + atajos_formateados("nombrado"))

        self.btn_info.setToolTip(traducir("Info"))
        self.btn_render.setText(traducir("Start"))
        self.btn_render.setToolTip(
            traducir("tltp_start") + atajos_formateados("renderizar") + "\n" + traducir(
                "tooltip_hay_opciones"))

        self.btn_stop.setText(traducir("Detener"))
        self.btn_stop.setToolTip(
            traducir("tltp_stop") + atajos_formateados("detener") + "\n" + traducir(
                "tooltip_hay_opciones"))
        self.btn_reajustar_modo.setToolTip(traducir("Modo"))
        self.btn_reajustar_modo.setText(traducir("Modo"))
        self.btn_agregar.setText(traducir("Añadir Blends"))
        self.btn_agregar.setToolTip(traducir("Añadir Blends") + atajos_formateados("agregar_blends"))
        self.btn_quitar_todos.setText(traducir("Quitar Todos"))
        self.btn_quitar_todos.setToolTip(traducir("Quitar Todos") + atajos_formateados("quitar_todos"))
        self.btn_info.setText(traducir("Info"))
        self.btn_info.setToolTip(traducir("Info"))
        self.btn_ver_render.setText(traducir("Ver Render"))
        self.btn_ver_render.setToolTip(traducir("Ver Render") + atajos_formateados("ver_render"))

        self.btn_menu_colas.setText(traducir("Queues options"))
        self.btn_menu_colas.setToolTip(traducir("Queues options"))
        self.btn_menu_modos.setText(traducir("Modes options"))
        self.btn_menu_modos.setToolTip(traducir("Modes options"))
        self.selector_cola.setToolTip(traducir("Elegir cola"))
        self.selector_modo.setToolTip(traducir("Elegir modo ingesta"))

        self.tlb_jobs_adjustments.setToolTip(traducir("Ajustar para los blends elegidos").upper())
        self.tlb_open.setToolTip(traducir("VER/ABRIR"))
        self.btn_log.setText(traducir("Log"))

        self.btn_log.setToolTip(
            traducir("Log") + atajos_formateados("log_texto") + "\n" + traducir(
                "tooltip_hay_opciones"))

        self.boton_watchfolder.setToolTip(traducir("tooltip_watchfolders"))
        self.boton_watchfolder.setText(traducir("Watch Folders"))

        self.boton_scheduler.setText(traducir("Scheduler"))
        self.boton_scheduler.setToolTip(traducir("tooltip_scheduler"))

        self.boton_apagar.setText(traducir("Auto shutdown"))
        self.boton_apagar.setToolTip(traducir("Shutdown PC after queue processing is completed"))

        self.btn_livelog.setText(traducir("Live Log"))
        self.btn_livelog.setToolTip(traducir("Blender Live Log") + atajos_formateados("live_log"))

    def retranslate_indicrectas(self):
        self.opcion_limpiar_log.setText(traducir("Limpiar log"))
        self.opcion_abrir_individuales.setText(traducir("Abrir logs individuales"))
        self.opcion_cerrar_logs.setText(traducir("Cerrar todos"))
        self.opcion_renderizar_elegidos.setText(traducir("renderizar_blend"))
        self.detener_luego.setText(traducir("Detener al completar"))
        self.detener_luego_frame.setText(traducir("Stop after current frame is saved"))
        self.opcion_detener_elegidos.setText(traducir("detener_item"))

    def inicializar_splitter(self):
        if self.tabla_estados.visibleRegion().isEmpty():
            self.tablaPrincipal.recuperar_scrollbar()
            return 2000
        else:
            self.tablaPrincipal.ocultar_scrollbar()
            return self.splitter.pos()

    def verificar_colapso_splitter(self, pos):
        if self.tabla_estados.visibleRegion().isEmpty():
            if pos <= self.pos_splitter:
                self.pos_splitter = pos
                self.tablaPrincipal.ocultar_scrollbar()
                return
            texto_chk = "chk_mostrar_columna_estado" if self.tablaPrincipal.isColumnHidden(
                self.columna["estado"]) else ""
            alerta, cb = alertas.alerta_checkbox("msg_colapso_splitter", texto_checkbox=texto_chk)
            rta = alerta.exec_()

            if not rta == QMessageBox.StandardButton.Ok:
                actual = self.splitter.sizes()[0]
                self.splitter.setSizes([int(actual * .9), int(actual * .1)])
            else:
                self.tablaPrincipal.recuperar_scrollbar()
                if cb and cb.isChecked():
                    self.tablaPrincipal.showColumn(self.columna["estado"])
        self.pos_splitter = pos

    def sincronizar_scroll_estados(self, value):
        self.tabla_estados.blockSignals(True)
        self.tabla_estados.verticalScrollBar().setValue(value)
        self.tabla_estados.blockSignals(False)

    def sincronizar_scroll_tp(self, value):
        self.tablaPrincipal.blockSignals(True)
        self.tablaPrincipal.verticalScrollBar().setValue(value)
        self.tablaPrincipal.blockSignals(False)

    def sincronizar_seleccion_tablas(self):
        if self.tabla_estados.seleccion_programatica:
            return
        self.tablaPrincipal.seleccion_programatica = True

        for item in self.tablaPrincipal.items():
            try:
                item.setSelected(item.item_estado.isSelected())
            except AttributeError:
                pass

    def actualizar_seleccion_lista_estado(self):
        items_tp = self.tablaPrincipal.topLevelItemCount()

        if not items_tp or not getattr(self.tablaPrincipal.topLevelItem(items_tp - 1), "item_estado", None):
            # maneja el caso en que esto se triggereo mientras agregaba objetos, porque eso se triggerea
            # apresuradamente y hace crashear y de todos modos está manejado en paralelo correctamente
            return

        if not self.tabla_estados.topLevelItemCount():
            self.actualizar_lista_estado()
            return
        self.tabla_estados.seleccion_programatica = True
        self.tabla_estados.clearSelection()
        try:
            for item in self.tablaPrincipal.items():
                item.item_estado.setSelected(item.isSelected())
        except AttributeError:
            self.actualizar_lista_estado()

    def actualizar_lista_estado(self):
        self.tabla_estados.clear()
        scroll_v = self.tablaPrincipal.verticalScrollBar().value()
        for item in self.tablaPrincipal.items():
            estado = "preparando" if item.preparando else item.estado
            item_estado = ItemEstado(self.tabla_estados, estado, item.desactivado, item.porcentaje_progreso,
                                     item.frame_reportado, faltante=not item.existe())
            item.item_estado = item_estado
            item_estado.alinear(self.settings_ventana)
            self.tabla_estados.seleccion_programatica = True
            item.item_estado.setSelected(item.isSelected())
        self.tablaPrincipal.verticalScrollBar().setValue(scroll_v)
        # self.tabla_estados.verticalScrollBar().setValue(self.tablaPrincipal.verticalScrollBar().value())

    def limpiar_progreso_taskbar(self):
        self.boton_taskbar.clearOverlayIcon()
        self.progreso_taskbar.setVisible(False)
        self.progreso_taskbar.setValue(0)

    def definir_progreso_taskbar(self):
        self.boton_taskbar = QtWinExtras.QWinTaskbarButton(self)
        self.boton_taskbar.setWindow(self.windowHandle())
        self.progreso_taskbar = self.boton_taskbar.progress()

        # self.boton_taskbar.setOverlayIcon(iconos.icono_apagar)
        # self.progreso_taskbar.setVisible(True)
        # self.progreso_taskbar.setValue(50)

    def abrir_ventana_tareas(self):
        ventana_tareas = VentanaTareas(self)
        ventana_tareas.exec_()

    def abrir_estimador(self):
        if not self.ventana_estimar:
            self.ventana_estimar = VentanaEstimar(self)
        self.ventana_estimar.exec_()

    def boton_watchfolder_accion(self):
        if self.boton_watchfolder.isChecked():
            if not self.ventana_watchfolders:
                self.ventana_watchfolders = VentanaWatchfolderArbol(self)
            self.ventana_watchfolders.open()
        else:
            watch_folders.activar(False)

    def boton_scheduler_accion(self):
        if self.boton_scheduler.isChecked():
            if not self.ventana_scheduler:
                self.ventana_scheduler = VentanaScheduler(self)
            else:
                self.ventana_scheduler.asimilando = True
                self.ventana_scheduler.cambio_start()
                self.ventana_scheduler.asimilando = False
            self.ventana_scheduler.ajustar_interfaz_segun_estado_cola()
            self.ventana_scheduler.exec_()
        else:
            schedules.activado = False
            schedules.desactivar()
        schedules.guardar()

    def boton_apagar_accion(self):
        # self.boton_apagar.setIcon([iconos.icono_apagar_off, iconos.icono_apagar_on][self.boton_apagar.isChecked()])
        self.boton_apagar.setIcon(iconos.icono_apagar_off)
        if self.cola.estado != "renderizando" or plataforma != 'Windows':
            return

    def ajustar_colecciones(self):
        if not len(self.tablaPrincipal.selectedItems()):
            return
        items = self.tablaPrincipal.selectedItems()
        VentanaColecciones(items, self)

    def ajustar_camaras(self):
        if not self.tablaPrincipal.selectedItems():
            return
        elegir_camaras = VentanaCamaras(self)
        elegir_camaras.exec_()

    def ajustar_viewlayers(self):
        if not self.tablaPrincipal.selectedItems():
            return
        elegir_viewlayers = VentanaViewlayers(self)
        elegir_viewlayers.exec_()

    def ajustar_nombrado(self):
        if not self.tablaPrincipal.selectedItems():
            return
        ventana_nombrado = VentanaNombrado(self)
        ventana_nombrado.exec_()
        # self.ventana_nombrado.ejecutar_para_item()

    def elegir_dispositivos(self):
        if not self.tablaPrincipal.selectedItems():
            return
        ventana_dispositivos = VentanaDispositivos(self)
        ventana_dispositivos.exec_()

    def definir_timer_resize(self):
        timer = QTimer()
        timer.setInterval(500)
        timer.setSingleShot(True)
        timer.timeout.connect(self.termino_resize)
        return timer

    def resizeEvent(self, event):
        self.timer_resize.start()
        super().resizeEvent(event)

    def termino_resize(self):
        self.settings_ventana.guardar()

    def event(self, event):
        # if event.type() == QtCore.QEvent.WindowStateChange and self.windowState() & QtCore.Qt.WindowMinimized:
        #     print("Window is minimized")
        # elif event.type() == QtCore.QEvent.WindowStateChange and self.windowState() & QtCore.Qt.WindowMaximized:
        #     print("Window is maximized")
        # elif event.type() == QtCore.QEvent.WindowStateChange and self.windowState() & QtCore.Qt.WindowFullScreen:
        #     print("Window is in full screen mode")
        # elif event.type() == QtCore.QEvent.WindowStateChange and self.windowState() & QtCore.Qt.WindowNoState:
        #     print("Window is restored")
        # if event.type() == QtCore.QEvent.FocusIn:
        if event.type() == QtCore.QEvent.ActivationChange and self.isActiveWindow():
            inicial = self.size()
            self.resize(40, 40)
            self.resize(inicial)
            if self.restorear_multipantallas_onshow:
                self.restore_multipantallas()

        return super().event(event)

    #

    def showEvent(self, event):
        super().showEvent(event)
        inicial = self.size()
        self.resize(40, 40)
        self.resize(inicial)

        if self.restorear_multipantallas_onshow:
            self.restore_multipantallas()

    # la razon para tener estos if's iguales en showEvent y event en lugar de que estén directamente en
    # restore_multipantallas es que solo son para estos casos de ativación de ventana, no para el caso que la ventana
    # ya está activada durante la macana

    def restore_multipantallas(self):
        if self.isMinimized():
            self.restorear_multipantallas_onshow = True
            return

        self.restorear_multipantallas_onshow = False

        main_window = self
        screen_list = app.screens()

        for screen in screen_list:
            main_window.move(screen.geometry().topLeft())

        # if len(screen_list) > 1:
        #     second_screen = screen_list[1]
        #     main_window.move(second_screen.geometry().topLeft())
        try:
            self.settings_ventana.leer()
        except AttributeError:
            return

    def set_alto_filas(self, altura=None):
        altura = configuracion.alto_filas if altura is None else altura
        self.tabla_estados.set_altura_filas(altura)
        self.tablaPrincipal.set_altura_filas(altura)
        for item in self.tabla_estados.items():
            item.reaplicar_font(altura)

    def actualizar_alternacion_filas(self, valor=None):
        valor = configuracion.alternar_color_filas if valor is None else valor
        self.tablaPrincipal.setAlternatingRowColors(valor)
        self.tabla_estados.setAlternatingRowColors(valor)

    def cambiar_escala_textos_botones(self, factor):
        factor /= 100
        for boton in self.botones_configurables:
            font = boton.font()
            font.setPointSize(int(ConfiguracionVentana.size_default_textos["botones"] * factor))
            boton.setFont(font)

    def cambiar_escala_textos(self, factor, altura=None):
        font = self.font()
        factor /= 100
        font.setPointSize(int(defaults_configuracion.font_size * factor))
        app.setFont(font)

        for conjunto_widgets, base_conjunto in self.widgets_texto_ajustables:
            for wgt in conjunto_widgets:
                font = wgt.font()
                font.setPointSize(int(base_conjunto * factor))
                wgt.setFont(font)

        for item in self.tabla_estados.items():
            item.reaplicar_font(altura)

    def cambiar_escala_iconos(self, factor):
        factor /= 100
        lado_icono = int(defaults_configuracion.icons_botones_size * factor)
        size = QtCore.QSize(lado_icono, lado_icono)
        for boton in self.botones_configurables:
            boton.setIconSize(size)

        for tlb in self.toolbars:
            tlb.setIconSize(size)

        # tablas
        lado_icono = int(
            defaults_configuracion.icons_tablas_size * factor * defaults_configuracion.atenuante_iconos_tablas)
        size = QtCore.QSize(lado_icono, lado_icono)

        self.tabla_estados.setIconSize(size)
        self.tablaPrincipal.setIconSize(size)

    def eligio(self):
        print("selected ", self.sender().text())



    def actualizar_color_items_desactivados(self):
        for item in self.tablaPrincipal.items():
            if not item.desactivado:
                continue
            item.actualizar_color_estado(desactivado=True)


    def exportar_traducciones_faltantes_chino(self):
        faltantes = json.dumps(traduccion.faltantes_chino())
        with open(Datas.ruta_faltantes_chino, 'w') as archivo_faltantes:
            archivo_faltantes.write(faltantes)

    def test(self):
        # print(set(traduccion.en_chino.items()) & set(traduccion.en_ingles.items()))

        self.exportar_traducciones_faltantes_chino()
        return
        # self.popup = InfoPopUp()
        # self.popup.show()
        #
        # for item in self.tablaPrincipal.items():
        #     print(item.__dict__)

        for toolbar in self.toolbars:
            print(f"tb {toolbar.objectName()} or {toolbar.orientation()}",) # debug print

        # self.reajustar_ancho_minimo_ventana()
        # return

        elegido = self.tablaPrincipal.selectedItems()[0]

        print("frames", elegido.frames) # debug print
        # print("renderizados", elegido.render.data.renderizados) # debug print
        print("pn", elegido.patron_nombrado) # debug print

        # elegido.setIcon(self.columna["tag_blender"], iconos.icono_warning)
        # elegido.setToolTip(self.columna["tag_blender"], "uya!")


        # auto_nombrado.aplicar(elegido)

        # ruta = elegido.ruta_blend_completa
        # print_scenes_cameras(ruta)


        return




    def test2(self):
        item = self.tablaPrincipal.currentItem()

        # item._start_time.clear()
        item.clear_start_time()

        return



    def test3(self, escenas):

        print("cornelio ", escenas)

    def test4(self):
        print("chorizo")

    def test_signal(self, sran):

        # if self.sender().objectName() == "tlb_blends":
        #     if sran == 2:
        #         self.wgt_blends.layout().takeAt(0)
        #         self.relayout = QtWidgets.QVBoxLayout(self.wgt_blends)
        #         self.relayout.setSpacing(0)
        #         self.wgt_blends.setLayout(self.relayout)
        #     else:
        #         self.relayout = QtWidgets.QHBoxLayout(self.wgt_blends)
        #         self.relayout.setSpacing(0)

        print("chk", sran)
        print(self.sender().objectName())
        tlb = self.sender()

    def actualizacion_orientacion_toolbars(self, orientation):
        toolbar = self.sender().objectName()
        widget = self.widgets_toolbars[toolbar] if toolbar in self.widgets_toolbars else None

        if not toolbar in self.botones_toolbar:
            return
        conjunto = self.botones_toolbar[toolbar]
        if orientation == Qt.Horizontal:
            if widget:
                widget.layout().setDirection(QBoxLayout.LeftToRight)
            # self.toolbars_verticales.discard(toolbar)
            # self.desnormalizar_botones_toolbar(conjunto)
        else:
            if widget:
                widget.layout().setDirection(QBoxLayout.TopToBottom)
            # self.toolbars_verticales.add(toolbar)
            # self.normalizar_botones_toolbars_verticales()
        self.reajustar_ancho_minimo_ventana()

    # def desnormalizar_botones_toolbar(self, conjunto_botones):
    #     for boton in conjunto_botones:
    #         boton.setMinimumWidth(24)
    #         boton.setMinimumHeight(24)

    # def normalizar_botones_toolbars_verticales(self):
    #     # conjunto_botones = [boton for tlb in self.toolbars_verticales for boton in self.botones_toolbar[tlb]]
    #     conjunto_botones = [boton for conjunto in self.conjuntos_botones for boton in conjunto]
    #
    #     ancho_max = 0
    #     alto_max = 0
    #
    #     for boton in conjunto_botones:
    #         tam = boton.size()
    #         if tam.width() > ancho_max:
    #             ancho_max = tam.width()
    #         if tam.height() > alto_max:
    #             alto_max = tam.height()
    #
    #     for boton in conjunto_botones:
    #         boton.setMinimumWidth(ancho_max)
    #         boton.setMinimumHeight(alto_max)


    def reajustar_ancho_minimo_ventana(self):
        ancho_total = 0
        for toolbar in self.toolbars:
            if toolbar.orientation() == Qt.Vertical:
                continue
            ancho_total += toolbar.minimumSizeHint().width()
        self.setMinimumWidth(ancho_total)
        self.centrar_ventana()

    def toggle_desactivar_items(self):
        if not self.tablaPrincipal.selectedItems():
            return
        offline = []

        for item in self.tablaPrincipal.selectedItems():
            if item.estado == "renderizando":
                continue
            if item.desactivado and not item.existe():
                offline.append(item)
                continue
            item.desactivado = not item.desactivado

        if offline:
            self.reubicar_blends(offline)

    def reset_estado_item(self):
        if not self.tablaPrincipal.selectedItems():
            return
        for item in self.tablaPrincipal.selectedItems():
            if item.estado == "renderizando":
                continue
            item.reset()
        # self.actualizar_lista_estado()

    def renderizar_item(self):
        if self.cola.estado == "renderizando":
            return

        if not self.tablaPrincipal.selectedItems():
            return

        self.cola.conjunto_render = self.tablaPrincipal.selectedItems()
        self.cola.procesar()

    def detener_render_item(self):  # operador del menu contextual
        if not self.tablaPrincipal.currentItem() or not self.tablaPrincipal.currentItem().render \
                or self.tablaPrincipal.currentItem().estado != "renderizando":
            return
        item = self.tablaPrincipal.currentItem()
        self.cola.detener_item(item)

    def abrir_blend(self):
        try:
            item = self.tablaPrincipal.currentItem()
            proceso_blender = QtCore.QProcess()
            proceso_blender.setProgram(versiones_blender.ruta(item.tag_blender))
            if plataforma == "Linux":
                argumento = item.ruta_blend_completa
            else:
                proceso_blender.setWorkingDirectory(item.ruta_blend)
                argumento = item.nombre_blend

            proceso_blender.setArguments([argumento])
            proceso_blender.startDetached()
            # subprocess.call([blenders.versiones[item.tag_blender], item.ruta_blend_completa])
        except OSError as e:
            pass
            # print(e)
        except AttributeError as e:
            pass
            # print(e)

    def reubicar_blends(self, items = None):
        items = items if items else self.tablaPrincipal.selectedItems()
        if not items:
            return
        items_por_path = {}

        for item in items:
            ruta_completa = item.ruta_blend_completa
            if ruta_completa in items_por_path:
                items_por_path[ruta_completa].append(item)
            else:
                items_por_path[ruta_completa] = [item]

        for path in items_por_path:
            item_base = items_por_path[path][0]
            dialogo_reubicar = DialogoReubicar(item_base)  # manda el primer item y si se recoso,
            # se aplica el nuevo path a todos los que tenían el mismo path
            
            if dialogo_reubicar.exec_():
                for item in items_por_path[path][1:]:
                    item.ruta_blend = item_base.ruta_blend
                    item.nombre_blend = item_base.nombre_blend
                    item.desactivado = False

    def explorar_ruta_blend(self):
        if self.tablaPrincipal.selectedIndexes() and self.tablaPrincipal.currentItem():
            item_actual = self.tablaPrincipal.currentItem()
            self.explorar_ruta(item_actual.ruta_blend)

    def explorar_ruta_output(self):
        if not self.tablaPrincipal.selectedIndexes():
            return

        if not self.tablaPrincipal.currentItem():
            self.tablaPrincipal.setCurrentItem(self.tablaPrincipal.selectedItems()[0])
        item_actual = self.tablaPrincipal.currentItem()

        ruta_a_explorar = ""
        if item_actual.nombrado:
            ruta_a_explorar = item_actual.nombrado
        elif item_actual.ruta_output and item_actual.ruta_output != "*None*":
            ruta_a_explorar = item_actual.ruta_output
        else:
            try:
                ruta_a_explorar = item_actual.render.data.ultimo_path_guardado
            except AttributeError:
                pass

        if not ruta_a_explorar:
            item_actual.leer_escenas_item(avisar=self.encontro_ruta_output, pasar_parametro=False)
            return

        ruta_a_explorar = self.ajustar_ruta_output(item_actual, ruta_a_explorar, completa=False)
        self.explorar_ruta(ruta_a_explorar)

    def encontro_ruta_output(self):
        if not (self.tablaPrincipal.selectedIndexes() and self.tablaPrincipal.currentItem()):
            return

        item_actual = self.tablaPrincipal.currentItem()
        if (not item_actual.ruta_output or item_actual.ruta_output == "*None*") and item_actual.escena:
            item_actual.ruta_output = self.ajustar_ruta_output(item_actual,
                                                               item_actual.escenas[item_actual.escena].ruta_completa)
        if not item_actual.ruta_output or item_actual.ruta_output == "*None*":  # lo pongo acá en lugar de en else para que abarque el fallo de ese for en encontrar sarasa
            info_escena_0 = item_actual.escenas[list(item_actual.escenas.keys())[0]]

            item_actual.ruta_output = self.ajustar_ruta_output(item_actual, info_escena_0.ruta_completa)

        self.explorar_ruta(item_actual.ruta_output)

    def ajustar_ruta_output(self, item, ruta, completa=True):
        if ruta.startswith("//"):
            ruta = os.path.join(item.ruta_blend, ruta[2:])
        if completa or not os.path.isdir(ruta):
            ruta = os.path.dirname(ruta)

        ruta = ruta.replace(auto_nombrado.token_start_time, "")
        return ruta

    def explorar_ruta(self, ruta):
        if not ruta:
            self.alerta_carpeta(ruta)
            return
        try:
            if plataforma == "Windows":
                os.startfile(ruta)
            elif plataforma == "Mac":
                subprocess.Popen(["open", ruta])
            else:
                subprocess.Popen(["xdg-open", ruta])
        except FileNotFoundError:
            self.alerta_carpeta(ruta)

    def alerta_carpeta(self, ruta):
        alerta = QMessageBox()
        alerta.setIcon(QMessageBox.Question)
        alerta.setWindowTitle(traducir("Atención!"))
        alerta.setText(traducir("No se encuentra la carpeta") + "\n" + ruta)
        alerta.exec_()

    def alerta_archivo(self, ruta=""):
        alerta = QMessageBox()
        alerta.setIcon(QMessageBox.Question)
        alerta.setWindowTitle(traducir("Atención!"))
        alerta.setText(traducir("alerta_file_not_found") + "\n" + ruta)
        alerta.exec_()

    def alerta_mensaje(self, mensaje):
        alerta = QMessageBox()
        alerta.setIcon(QMessageBox.Question)
        alerta.setWindowTitle(traducir("Atención!"))
        alerta.setText(mensaje)
        alerta.exec_()

    def esperar_info_video(self, item):
        if tipo_build == "debug":
            Debug.loguear_actividad("Awaiting video info")

        if not item or not item.es_video:
            return
        if not item.ruta_frame_output:
            QTimer.singleShot(500, lambda: self.esperar_info_video(item))
            return
        self.ver_render()

    def ver_render(self):
        if self.tablaPrincipal.currentItem() is None:
            return
        item = self.tablaPrincipal.currentItem()
        if item.es_video:
            tipo_render = "videos"
        else:
            if modos.modo[item.modo].tipo == "frames":
                tipo_render = "imagenes"
            else:
                tipo_render = "secuencias"

        visor_configuracion = {"imagenes": configuracion.viewer_imagenes, "secuencias": configuracion.viewer_secuencias,
                               "videos": configuracion.viewer_videos}[tipo_render]

        if visor_configuracion == "B-renderon":
            visor_renders = VisorRenders(self)
            visor_renders.exec_()
        elif visor_configuracion == "blender_player":
            self.ver_render_blender(item)
        elif visor_configuracion == "custom_viewer":
            self.ver_render_visor_custom(item, tipo_render)
        else:
            self.ver_render_visor_sysdefault(item)

    def ver_render_blender(self, item):
        self.blender_visor = InfosBlender(cursor_espera=False)
        self.blender_visor.correr_blender(
            ["-a", item.ruta_frame_output, "-s", item.inicio, "-e", item.fin])

    def ver_render_visor_sysdefault(self, item):
        try:
            subprocess.Popen([item.ruta_frame_output], shell=True)
        except OSError as e:
            print(e)
        except AttributeError as e:
            print(e)

    def ver_render_visor_custom(self, item, tipo_visor):
        try:
            self.proceso = QtCore.QProcess()
            self.proceso.start(configuracion.rutas_custom_viewers[tipo_visor], [item.ruta_frame_output])
            # subprocess.run([configuracion.rutas_custom_viewers[tipo_visor], item.ruta_frame_output])
        except OSError as e:
            print(e)
        except AttributeError as e:
            print(e)


    def cambia_foco(self):
        pass
        # self.raise_()
        # if self.ventana_overrides:
        #     self.ventana_overrides.raise_()

    def closeEvent(self, evento):
        self.settings_ventana.guardar()
        self.ventana_log.close()
        if self.cola.estado == "renderizando":
            alerta = QMessageBox()
            alerta.setIcon(QMessageBox.Question)
            alerta.setWindowTitle(traducir("Atención!"))
            alerta.setText(traducir("render en proceso"))

            alerta.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            # alerta.button(alerta.Yes).setText(traducir("Si"))
            # alerta.button(alerta.No).setText(traducir("No"))

            respuesta = alerta.exec_()

            if respuesta == QMessageBox.Yes:
                if self.cola.estado == "renderizando":  # chequea nuevamente por si terminaron los renders mientras tanto
                    self.cola.detener_cola()
            else:
                evento.ignore()
                return

        modos.guardar_modos()

        configuracion.guardar()

        colas.guardar()

        watch_folders.guardar()

        evento.accept()

    def doble_click_item(self):
        pass

    def accion_btn_stop(self):
        self.cola.detener_cola()

    def accion_btn_render(self):
        self.tablaPrincipal.clearSelection()
        self.cola.conjunto_render = None
        self.cola.procesar()

    def limpiar_log(self):
        alerta = QMessageBox()
        alerta.setIcon(QMessageBox.Question)
        alerta.setWindowTitle(traducir("Atención!"))
        alerta.setText(traducir("limpiara log"))

        alerta.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        respuesta = alerta.exec_()

        if respuesta == QMessageBox.Yes:
            try:
                with open(colas.ruta_log, 'w'):
                    pass
            except IOError as e:
                pass
            self.btn_log.setChecked(False)

    def context_btn_render(self, posicion):
        if self.cola.estado == "renderizando":
            return
        self.opciones_render.exec_(self.btn_render.mapToGlobal(posicion))

    def context_btn_stop(self, posicion):
        if self.cola.estado == "renderizando":
            self.opciones_detener.exec_(self.btn_stop.mapToGlobal(posicion))

    def mostrar_menu_log(self, posicion):
        self.opciones_log.exec_(self.btn_log.mapToGlobal(posicion))

    def consola_titular(self):
        self.dock_consola.titular(traduccion)

    def consola_sin_elementos(self, widget_consola=None):
        widget_consola = widget_consola if widget_consola else self.widget_consola
        widget_consola.setPlainText(traducir("Seleccione un blend para ver su live log"))

    def definicion_submenu_alineacion_headers(self, sufijo_tabla="_principal"):
        submenu_alineacion = QMenu(traducir("Align"))
        opcion_izquierda = submenu_alineacion.addAction(traducir("Left"))
        opcion_centro = submenu_alineacion.addAction(traducir("Center"))
        opcion_derecha = submenu_alineacion.addAction(traducir("Right"))
        opcion_izquierda.setObjectName("izquierda" + sufijo_tabla)
        opcion_derecha.setObjectName("derecha" + sufijo_tabla)
        opcion_centro.setObjectName("centro" + sufijo_tabla)
        opcion_izquierda.triggered.connect(self.alinear_columna)
        opcion_derecha.triggered.connect(self.alinear_columna)
        opcion_centro.triggered.connect(self.alinear_columna)
        return submenu_alineacion

    def contextual_header_tp(self, posicion):
        # posicion = self.tablaPrincipal.viewport().mapFromGlobal(QtGui.QCursor.pos())
        indice_columna_tocada = self.tablaPrincipal.header().logicalIndexAt(posicion)
        columnas_ocultas = {}
        cantidad_columnas_ocultas = self.tablaPrincipal.header().hiddenSectionCount()
        self.settings_ventana.columna_activa = indice_columna_tocada
        menu_header = QMenu()
        submenu_alineacion = self.definicion_submenu_alineacion_headers()
        menu_header.addMenu(submenu_alineacion)
        menu_header_reset = menu_header.addAction(traducir("Reset"))
        menu_header_reset.triggered.connect(self.settings_ventana.resetear_columnas_tp)
        opcion_ocultar = menu_header.addAction(traducir("Hide"))

        if ItemCola.columnas - cantidad_columnas_ocultas == 1:
            opcion_ocultar.setDisabled(True)
        opcion_ocultar.triggered.connect(self.ocultar_columna)
        menu_header.addSeparator()

        for columna in self.settings_ventana.columna:
            indice = self.settings_ventana.columna[columna]
            if self.tablaPrincipal.header().isSectionHidden(indice):
                texto_item = self.tablaPrincipal.headerItem().text(indice)
                self.agregar_opcion_contextual(columnas_ocultas, columna, menu_header, texto_item,
                                               self.tablaPrincipal.showColumn, indice)

        menu_header.exec_(self.tablaPrincipal.header().mapToGlobal(posicion))

    def contextual_header_estados(self):
        posicion = self.tabla_estados.viewport().mapFromGlobal(QtGui.QCursor.pos())
        indice_columna_tocada = self.tabla_estados.header().logicalIndexAt(posicion)
        self.settings_ventana.columna_activa = indice_columna_tocada
        menu_header = QMenu()
        submenu_alineacion = self.definicion_submenu_alineacion_headers("_estados")
        menu_header.addMenu(submenu_alineacion)
        menu_header_reset = menu_header.addAction(traducir("Reset"))
        menu_header_reset.triggered.connect(self.settings_ventana.resetear_headers_estado)
        menu_header.exec_(self.tabla_estados.header().mapToGlobal(posicion))

    def alinear_columna(self):
        alineamiento_elegido, tabla = self.sender().objectName().split("_")

        self.settings_ventana.alinear_columna(alineamiento_elegido, nombre_tabla=tabla)

    def ocultar_columna(self):
        # posicion = self.tablaPrincipal.viewport().mapFromGlobal(QtGui.QCursor.pos())
        # indice_columna_tocada = self.tablaPrincipal.header().logicalIndexAt(posicion)
        self.tablaPrincipal.hideColumn(self.settings_ventana.columna_activa)

    def agregar_opcion_contextual(self, lista, elemento, menu, texto, funcion, parametro):
        lista[elemento] = menu.addAction(texto)
        lista[elemento].triggered.connect(lambda: funcion(parametro))

    def definicion_menu_contextual(self):
        self.contextual_general = atajos_y_contextuales.ContextualGeneral(self)
        self.contextual_elegidos = atajos_y_contextuales.ContextualElegidos(self)

        self.rellenar_menu_contextual()

    def rellenar_menu_contextual(self):
        self.contextual_general.popular(traduccion)
        self.contextual_elegidos.popular(traduccion)

    def menu_contextual(self, position=None):
        self.contextual_elegidos.actualizar_estado()
        self.contextual_general.actualizar_estado()

        if position is None:
            position = self.tablaPrincipal.viewport().mapFromGlobal(QtGui.QCursor.pos())  # no muy elegante hacer
            # para deshacer mapeo

        [self.contextual_general, self.contextual_elegidos][bool(self.tablaPrincipal.selectedIndexes())]. \
            qmenu.exec_(self.tablaPrincipal.viewport().mapToGlobal(position))

    def cambiar_blender(self):
        if not bool(self.tablaPrincipal.selectedItems()):
            return
        if self.tablaPrincipal.currentItem().tipo_dispositivos == "Eevee":
            alertas.alerta_generica("gpu_fija_exe", base_titulo="Eeve GPU", icono="info")
            return
        # self.ventan_cambiar_blender = VentanaCambiarBlender(self)
        self.ventan_cambiar_blender = VentanaBlenders(self)
        self.ventan_cambiar_blender.tagSelected.connect(self.cambio_blender)
        self.ventan_cambiar_blender.exec_()

    def cambio_blender(self, tag_elegido):
        for item in self.tablaPrincipal.selectedItems():
            item.tag_blender = tag_elegido
            item.coinciden_versiones_blender()

    def cambiar_rango(self):
        if not bool(self.tablaPrincipal.selectedItems()):
            return
        if not self.tablaPrincipal.currentItem():  # esto se podría reemplazar por una funcion mas no se si vale la pena
            self.tablaPrincipal.setCurrentItem(self.tablaPrincipal.selectedItems()[-1])

        if self.item_unico_elegido():
            item_activo = self.item_unico_elegido()
        else:
            item_activo = self.tablaPrincipal.currentItem()

        if modos.modo[item_activo.modo].tipo == "frames":
            self.tomar_frames_items(self.tablaPrincipal.selectedItems())
            return

        self.ventana_cambiar_rango = VentanaCambiarRango(self, item_activo)
        self.ventana_cambiar_rango.exec_()

    def tomar_frames_items(self, items):
        multiples = len(items) > 1
        frames = None
        for item in items:
            if frames is not None:
                item.reset()
                item.frames = frames
                item.modo = "modo_frames"
                continue
            dialogo_frames = DialogoFrames(item=item, multiples=multiples)
            if dialogo_frames.exec_():
                item.reset()
                item.frames = dialogo_frames.elegidos()
                item.modo = "modo_frames"
                frames = item.frames if dialogo_frames.chk_aplicar_todos.isChecked() else None
            else:
                break

    def tomar_frames_al_aire(self, nombre, multiples):
        dialogo_frames = DialogoFrames(item=None, nombre=nombre, multiples=multiples)
        if dialogo_frames.exec_():
            return dialogo_frames.elegidos(), dialogo_frames.chk_aplicar_todos.isChecked()
        return None, None

    def cambiar_escena(self):
        if not self.tablaPrincipal.selectedItems():
            self.agregar_con_escenas()
            return
        item = self.item_unico_elegido() if self.item_unico_elegido() else None
        ventana_cambiar_escena = VentanaEscenas(self, item=item)
        ventana_cambiar_escena.exec_()

    def argumentos_extra(self):
        if not bool(self.tablaPrincipal.selectedItems()):
            return
        ventana_argumentos_extra = VentanaArgsExtra(self)
        ventana_argumentos_extra.exec_()

    def configurar(self):

        VentanaConfiguracion(self)

    def acerca_de(self):
        ventana_acerca_de = VentanaAcercaDe(self)
        ventana_acerca_de.exec()

    def cambio_seleccion(self):
        if not self.tablaPrincipal.seleccion_programatica:
            self.actualizar_seleccion_lista_estado()

        # if self.aux_buffer_cambio_seleccion:
        #     self.aux_buffer_cambio_seleccion = False
        #     return
        #
        # self.aux_buffer_cambio_seleccion = True

        item_u_e = self.item_unico_elegido()
        if item_u_e:
            self.manejo_statusbar.unico_elegido(item_u_e)
            self.dock_consola.activo = item_u_e
            self.dock_consola.actualizar_contenido()
            self.btn_ver_render.setEnabled(item_u_e.ruta_output not in ("", "*None*") or bool(item_u_e.ruta_frame_output))

        else:
            if item_u_e is None:
                self.manejo_statusbar.ningun_elegido()
                # aca tambien mostrar el log de cola.item_renderizando
            elif item_u_e == 0:
                self.manejo_statusbar.varios_elegidos()

            self.limpiar_info_individual()
            self.manejo_statusbar.nombre_blend.setText("")

        self.management_estados_botones.cambio_seleccion(len(self.tablaPrincipal.selectedItems()))

    def limpiar_info_individual(self):
        self.consola_sin_elementos()
        # self.btn_explorar_output.setEnabled(False)
        self.btn_ver_render.setEnabled(False)
        self.manejo_statusbar.vaciar_individual()
        # self.actualizar_statusbar_vaciar_widgets(set(self.status_widgets_item_inactivo) | set(self.status_widgets_renderizando))

    def seleccion_nada(self):
        self.tablaPrincipal.clearSelection()

    def seleccion_todo(self):
        self.tablaPrincipal.selectAll()

    def tope(self, sentido):
        items = self.tablaPrincipal.topLevelItemCount()
        tope = int(((items - 1) * (1 - sentido)) / 2)
        return items, tope

    def items_elegidos(self, sentido=1, items=None, indice_inicial=0):  # sentido puede ser +1 (subir) o -1 (bajar)
        if items is None:
            items = self.tablaPrincipal.topLevelItemCount()
        for i in range(items):
            item = self.tablaPrincipal.topLevelItem(indice_inicial)
            if item.isSelected():
                yield item
            indice_inicial += sentido

    def subir(self):
        self.mover(1)

    def bajar(self):
        self.mover(-1)

    def subir_a_tope(self):
        self.mover_a_tope(1)

    def bajar_a_tope(self):
        self.mover_a_tope(-1)

    def mover(self, sentido):
        if not self.tablaPrincipal.selectedItems():
            return

        items, tope = self.tope(sentido)

        if not self.tablaPrincipal.topLevelItem(tope).isSelected():
            for elegidaI in self.items_elegidos(sentido, items, tope):
                index = self.tablaPrincipal.indexOfTopLevelItem(elegidaI)
                removido = self.tablaPrincipal.takeTopLevelItem(index - sentido)
                self.tablaPrincipal.insertTopLevelItem(index, removido)
                self.actualizar_lista_estado()
            return
        self.actualizar_lista_estado()
        self.estado_reset_con_blends()

    def mover_a_tope(self, sentido):
        if not self.tablaPrincipal.selectedItems():
            return

        removidos = []
        for elegidaI in self.tablaPrincipal.selectedItems():
            indice = self.tablaPrincipal.indexOfTopLevelItem(elegidaI)
            removidos.append(self.tablaPrincipal.takeTopLevelItem(indice))
        if sentido == 1:
            self.tablaPrincipal.insertTopLevelItems(0, removidos)
        else:
            self.tablaPrincipal.addTopLevelItems(removidos)
        for item in removidos:
            item.setSelected(True)

        self.actualizar_lista_estado()
        self.estado_reset_con_blends()

    def aplicar_modo(self, nombre_modo):
        modo = modos.modo[nombre_modo]
        script = self.elegir_script() if modo.pedir_script else None
        items = self.tablaPrincipal.selectedItems()
        if modo.frames_predefinidos:
            frames = modo.frames_predefinidos
        else:
            frames = None

        for item_i in self.tablaPrincipal.selectedItems():
            if item_i.estado == "renderizando":
                continue
            if modo.version_blender:
                item_i.tag_blender = modo.version_blender

            item_i.reset()
            item_i.modo = nombre_modo
            item_i.args_extra = modo.args_extra
            if script:
                prefijo = "\n" if item_i.args_extra else ""
                item_i.args_extra += prefijo + "--python " + script
            if modo.tipo == "frames":
                for attr in ItemCola.datos_frames_animacion:
                    item_i.propiedades_argumentar.discard(attr)
                if frames:
                    item_i.frames = frames
                else:
                    elegidos, usar_para_todos = self.tomar_frames_al_aire(nombre=item_i.nombre_blend,
                                                                          multiples=len(items) > 1)
                    if elegidos is None:
                        break
                    item_i.frames = elegidos if elegidos else item_i.frames if item_i.frames else "1"
                    if usar_para_todos:
                        frames = elegidos
            else:
                item_i.frames = ""
                for attr in ItemCola.datos_frames_animacion:
                    valor = getattr(item_i, attr, "")
                    setattr(item_i, attr, valor)
                    if valor: # reafirmar los frames para que los muestre. Esto es para el caso de pasar de modo frames a animación cuando se saben los frames inicio, fin, sarasa
                        break

            if modo.dispositivos:
                self.asimilar_dispositivos(item_i, modo)
            else:
                item_i.dispositivos = []
                item_i.tipo_dispositivos = ""
                item_i.nombres_dispositivos = ""
                item_i.parallel_gpu = False
                item_i.propiedades_argumentar.discard("dispositivos")


        self.estado_reset_con_blends()

        colas.guardar()

    def cambiar_frames(self):
        if "modo_frames" in modos.modo:
            self.aplicar_modo("modo_frames")

    def cambiar_a_animacion(self):
        if "modo_animacion" in modos.modo:
            self.aplicar_modo("modo_animacion")

    def quitar_terminados(self):
        for i in range(self.tablaPrincipal.topLevelItemCount() - 1, -1, -1):
            if self.tablaPrincipal.topLevelItem(i).estado == "terminado":
                self.tablaPrincipal.borrar_item(i)

        self.actualizar_numero_blends()
        self.management_estados_botones.cambio_numero(self.tablaPrincipal.topLevelItemCount())

    def quitar_todos(self, preservar_livelogs=False):
        if not self.tablaPrincipal.topLevelItemCount() or self.cola.estado == "renderizando":
            return
        if not preservar_livelogs:
            for i in range(self.tablaPrincipal.topLevelItemCount()):
                item = self.tablaPrincipal.topLevelItem(i)
                item.consola.borrar_archivo_livelog()
        self.tablaPrincipal.clear()
        self.actualizar_numero_blends(0)
        self.management_estados_botones.cambio_numero(0)

    def quitar_seleccionados(self):
        for item_i in self.tablaPrincipal.selectedItems():
            if item_i.estado != "renderizando":
                self.tablaPrincipal.borrar_item(self.tablaPrincipal.indexOfTopLevelItem(item_i))

        num_items = self.tablaPrincipal.topLevelItemCount()

        if not num_items:
            self.management_estados_botones.cambio_numero(0)

        elegidos = len(self.tablaPrincipal.selectedItems())
        self.management_estados_botones.cambio_seleccion(elegidos)
        self.actualizar_numero_blends(num_items)
        colas.guardar()

    def agregar_con_escenas(self):
        self.elegir_archivos(con_escenas="elegir")

    def elegir_archivos(self, con_escenas=None):
        modificadoras = QApplication.keyboardModifiers()
        if modificadoras == Qt.ControlModifier:
            con_escenas = "elegir"
        elif modificadoras == (Qt.ControlModifier | Qt.ShiftModifier):
            con_escenas = "todas"
        filtro = "BLEND (*.blend) ;; Backup BLEND (*.blend1);; Backup BLEND (*.blend2);; " \
                 + traducir("Todos los archivos") + "(*.*)"
        if self.settings_ventana:
            ruta = self.settings_ventana.ultimo_path
        else:
            ruta = ""

        titulo = traducir("Elegir Archivos")
        archivos, _ = QFileDialog.getOpenFileNames(self, caption=titulo, directory=ruta, filter=filtro)
        if not archivos:
            return
        ruta_actualizada = os.path.dirname(archivos[0])
        self.settings_ventana.ultimo_path = ruta_actualizada
        self.settings_ventana.guardar()
        self.agregar_archivos(archivos, con_escenas)

    def agregar_variantes(self, propiedad_variantes, item_base, elegidas, autonombrar=False):
        variantes = getattr(item_base, propiedad_variantes)
        propiedad_variante = propiedad_variantes.rstrip("s")
        item_base.propiedades_argumentar.add(propiedad_variante)
        items = []
        for variante in elegidas:
            item_i = item_base.duplicar()
            setattr(item_i, propiedad_variantes, variantes)
            self.tablaPrincipal.addTopLevelItem(item_i)

            if propiedad_variantes == "escenas":
                item_i.asimilar_info_escena(variante)
            else:
                setattr(item_i, propiedad_variante, variante)
            if autonombrar:
                auto_nombrado.aplicar(item_i)
            items.append(item_i)

        self.focalizar_propiedad(propiedad_variante)
        self.actualizar_numero_blends()

        return items

    def agregar_escenas(self, infos_escenas_elegidas, item_base, duplicando=0):
        # esta funcion está solamente para el caso de la configuración "agregar todas las escenas"
        if not item_base.escenas:
            item_base.escenas = infos_escenas_elegidas  # esto es para el caso de agregar todas desde el vamos, que no
            # le carga las escenas al item ni a los datos antes de acá

        agregados = self.agregar_variantes("escenas", item_base, [*infos_escenas_elegidas.values()])
        self.agregados_tanda.extend(agregados)
        for i in range(duplicando):
            duplicados = self.duplicar_items_en_sitio(agregados)
            self.agregados_tanda.extend(duplicados)
        self.cambio_items_actualizar()  # esto está para el caso de configuracion "agregar todas las escenas"
        # con archivos comprimidos, que genera un thread paralelo y la actualización correspondiente dentro
        # del method agregar archivos pasa antes de que los archivos se hayan agregado

    def leer_header_archivo_asinc(self, item: ItemCola, cursor_espera=True, avisar=None):
        if cursor_espera:
            set_cursor_espera()
        worker = Worker(item.lectura_datos_header)
        if avisar:
            worker.signals.result.connect(avisar)
        self.workers.append(worker)

        # worker.signals.finished.connect(self.thread_complete)
        # worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)


    def leer_escenas_archivo_asinc(self, ruta, cursor_espera=True, avisar=None):
        if cursor_espera:
            set_cursor_espera()
        worker = Worker(ItemCola.leer_escenas_archivo, ruta)
        worker.signals.result.connect(avisar)
        self.workers.append(worker)

        # worker.signals.finished.connect(self.thread_complete)
        # worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)


    def leer_escenas_archivo(self, ruta, cursor_espera=True, avisar=None):
        verificar = lambda x: self.verificar_encontro_escenas_archivo(x, avisar=avisar, ruta=ruta,
                                                                      cursor_espera=cursor_espera)
        self.leer_escenas_archivo_asinc(ruta, avisar=verificar, cursor_espera=cursor_espera)


    def verificar_encontro_escenas_archivo(self, data, avisar, ruta=None, item=None, cursor_espera=True):
        if data:
            avisar(data, ruta)
        else:
            info_manual = InfoEscenasManual(item=item, archivo=ruta, avisar=avisar, pasar_parametro=True,
                                            cursor_espera=cursor_espera)
            info_manual.averiguar()


    @pyqtSlot(dict)
    def leyo_escenas(self, escenas):
        pass
        # print("escenasasa ", escenas)

    def focalizar_propiedad(self, propiedad):
        ultimo_item = self.tablaPrincipal.topLevelItemCount() - 1
        ultimo_item = self.tablaPrincipal.topLevelItem(ultimo_item)

        self.tablaPrincipal.setCurrentItem(ultimo_item, self.columna[propiedad])
        indice_scroll = self.tablaPrincipal.currentIndex()
        self.tablaPrincipal.scrollTo(indice_scroll)

    def elegir_script(self):
        script, _ = QFileDialog.getOpenFileName(self, traducir("Elegir script para renderizar"),
                                                filter=Datas.filtro_python(traducir))
        return script

    def agregar_archivos(self, archivos, con_escenas=None, patron_nombrado=None, args_extra="", nombre_modo=None,
                         evitar_repetidos=False):
        self.agregados_tanda = []
        lote_de_archivos = LoteDeArchivos(archivos, con_escenas,
                                          patron_nombrado=patron_nombrado, args_extra=args_extra,
                                          nombre_modo=nombre_modo, evitar_repetidos=evitar_repetidos)

        if modos.modo[lote_de_archivos.nombre_modo].pedir_script:
            lote_de_archivos.script = self.elegir_script()

        if configuracion.cargar_escenas == "escenas_todas" or con_escenas == "todas":  # lo de configuracion acá es legacy, se podría borrar tranquilamente nocierto?
            self.lote_archivos_agregar = lote_de_archivos
            self.iterador_lote_archivos = self.generator_lote_archivos()
            set_cursor_espera()
            self.loop_agregar_archivos_todas_escenas()
        else:
            self.loop_general_agregar_archivos(lote_de_archivos)

        self.cambio_items_actualizar()

    def loop_general_agregar_archivos(self, lote_de_archivos):
        for archivo in lote_de_archivos.archivos:
            repetido = False
            if lote_de_archivos.evitar_repetidos:
                for item in self.tablaPrincipal.items():
                    if item.estado != "no_comenzado" or item.ruta_blend_completa != archivo:
                        continue
                    attrs = LoteDeArchivos.attrs_item
                    if not all(getattr(item, attr) == getattr(lote_de_archivos, attr) for attr in attrs):
                        continue
                    repetido = True
                    break

            if repetido:
                continue

            item = self.datos_item_por_agregar(archivo, lote_de_archivos)
            if not item:
                continue
            item.agregar()
            # self.leer_header_archivo_asinc(item)
            self.agregados_tanda.append(item)

            if item.patron_nombrado and item.patron_nombrado != ItemCola.default_patron_nombrado:
                auto_nombrado.aplicar(item)

            self.tablaPrincipal.clearSelection()
            item.setSelected(True)
            self.tablaPrincipal.setCurrentItem(item)

            if configuracion.cargar_escenas == "escenas_elegir" or lote_de_archivos.con_escenas == "elegir":
                elegir_escenas = VentanaEscenas(self, item, leer=True, duplicando=lote_de_archivos.duplicando)
                elegir_escenas.exec_()
                continue
            #
            # item.leer_escenas_item(avisar=lambda item_aviso: self.duplicaciones_lote(item_aviso, lote_de_archivos),
            #                        pasar_parametro="item_aviso", cursor_espera=True, fallback_manual=False,
            #                        asimilar=True) # no hacemos esta lectura de frente porque para archivos pesados
            #                        chupa recursos de mas y tarda

            self.duplicaciones_lote(item, lote_de_archivos)

        # self.checkear_versiones_blender(self.agregados_tanda)

            # self.leer_escenas_archivo(archivo, cursor_espera=False,
            #                           avisar=lambda escenas, ruta: self.agregar_todas(escenas, ruta))
            # duplicados = []
            # item.update_id_start_time()
            # for i in range(lote_de_archivos.duplicando):
            #     duplicados.extend(self.duplicar_items_en_sitio([item]))
            # for item_i in duplicados:
            #     if any(item_i.patron_nombrado):
            #         auto_nombrado.aplicar(item_i)
            #     item_i.link_start_time(item)



    def duplicaciones_lote(self, item, lote_de_archivos):
        duplicados = []
        item.update_id_start_time()
        for i in range(lote_de_archivos.duplicando):
            duplicados.extend(self.duplicar_items_en_sitio([item]))
        self.agregados_tanda.extend(duplicados)
        for item_i in duplicados:
            if any(item_i.patron_nombrado):
                auto_nombrado.aplicar(item_i)
            item_i.link_start_time(item)


    def loop_agregar_archivos_todas_escenas(self):
        # todo esto de usar iterator es solo para el caso de tener que usar lectura manual, si no era mucho más sencillo
        try:
            archivo = next(self.iterador_lote_archivos)
        except StopIteration:
            restore_cursor()
            self.checkear_versiones_blender(self.agregados_tanda)
            return
        extension = os.path.splitext(archivo)[1]
        if extension != ".blend":
            self.loop_agregar_archivos_todas_escenas()
            return
        self.leer_escenas_archivo(archivo, cursor_espera=False,
                                  avisar=lambda data, ruta: self.agregar_todas(data, ruta))

    def generator_lote_archivos(self):
        for archivo in self.lote_archivos_agregar.archivos:
            yield archivo

    def agregar_todas(self, data, archivo):
        restore_cursor()
        if not archivo:
            return
        escenas = data.get("data_escenas", [])
        version = data.get("version_blender", "")
        item_base = self.datos_item_por_agregar(archivo, self.lote_archivos_agregar)
        item_base.version_blender = version

        self.agregar_escenas(escenas, item_base, self.lote_archivos_agregar.duplicando)
        self.loop_agregar_archivos_todas_escenas()

    def datos_item_por_agregar(self, archivo, lote_de_archivos):
        ruta_archivo, nombre_archivo = os.path.split(archivo)
        extension = os.path.splitext(nombre_archivo)[1]
        if extension == ".txt":
            self.lectura_de_cola(archivo, switchear=False)
            return False

        if extension != ".blend" and self.extension_mala_omitir(extension, nombre_archivo):
            return False

        modo = modos.modo[lote_de_archivos.nombre_modo]
        if modo.tipo == "frames":
            if modo.frames_predefinidos:
                frames_elegidos = modo.frames_predefinidos
            elif lote_de_archivos.frames:
                frames_elegidos = lote_de_archivos.frames
            else:
                frames_elegidos, usar_para_lote = self.tomar_frames_al_aire(nombre=nombre_archivo, multiples=
                len(lote_de_archivos.archivos) > 1)
                if usar_para_lote:
                    lote_de_archivos.frames = frames_elegidos
                if not frames_elegidos:
                    return False
        else:
            frames_elegidos = ""

        args_extra = lote_de_archivos.args_extra
        if lote_de_archivos.script:
            args_extra += "\n--python " + lote_de_archivos.script

        item_base = ItemCola(self)
        item_base.set_valores(ruta_blend=ruta_archivo, nombre_blend=nombre_archivo, modo=lote_de_archivos.nombre_modo,
                              frames=frames_elegidos,
                              escenas=[], escena="",
                              args_extra=lote_de_archivos.args_extra)

        if modo.version_blender:
            item_base.tag_blender = modo.version_blender

        # if configuracion.defaults_item:
        #     datos_item.asimilar(configuracion.defaults_item)

        if modo.dispositivos and modo.dispositivos['tipo'] != 'respetar':
            self.asimilar_dispositivos(item_base, modo)

        if lote_de_archivos.patron_nombrado:
            item_base.patron_nombrado = lote_de_archivos.patron_nombrado

        return item_base


    def checkear_versiones_blender(self, items):
        hay_mismatch = False
        for item in items:
            if not item.coinciden_versiones_blender():  # loop que llama a todos los testeos para que el icono se setee
                hay_mismatch = True
        if hay_mismatch:
            alertas.alerta_generica("ojo al piojo")

    def asimilar_dispositivos(self, item, modo):
        if not ("tipo" in modo.dispositivos and modo.dispositivos["tipo"] != "ask"):
            return
        item.tipo_dispositivos = modo.dispositivos["tipo"]
        motor = modo.motor_dispositivos

        if modo.parallel_gpu:
            motor += " " + traducir("Parallel GPU")
        lista_nombres = "[{}] ({}) ".format(motor, item.tipo_dispositivos)
        ids = []
        for nombre, id in modo.dispositivos.items():
            if nombre == 'tipo':
                continue
            lista_nombres += nombre + ", "
            ids.append(id)
        item.dispositivos = ids
        item.propiedades_argumentar.add("dispositivos")
        item.nombres_dispositivos = lista_nombres.strip(", ")
        item.parallel_gpu = modo.parallel_gpu
        if modo.overwrite_placeholders:
            arg = ArgsExtraBuiltin.por_nombre['overwrites']
            if item.args_extra:
                arg = "\n" + arg
            item.args_extra += arg

    def cambio_items_actualizar(self):
        num_items = self.tablaPrincipal.topLevelItemCount()
        self.actualizar_numero_blends(num_items)
        self.management_estados_botones.cambio_numero(num_items)
        colas.guardar()

    def extension_mala_omitir(self, extension, blend):
        if extension.startswith(".blend"):
            respuesta = QMessageBox.question(self, traducir("Atención!"),
                                             blend + "\n\n" + traducir("blend backup"),
                                             QMessageBox.Yes | QMessageBox.No)
            return respuesta != QMessageBox.Yes
        else:
            QMessageBox.information(self, traducir("Atención!"),
                                    blend + "\n\n" + traducir("archivo malo"))
            return True

    def duplicar_blends(self):
        for item_i in self.items_elegidos():
            item_i.duplicar()
        self.cambio_items_actualizar()
        self.actualizar_lista_estado()

    def duplicar_items_en_sitio(self, items=None):
        items = items if items else self.tablaPrincipal.selectedItems()
        duplicados = []
        for item_i in items:
            duplicados.append(item_i.duplicar_en_sitio())
        self.cambio_items_actualizar()

        return duplicados

    def rellenar_menu_modos(self):
        self.menu_modos.clear()
        self.opc_modo_agregar_desde_archivo = self.menu_modos.addAction(traducir("Añadir desde archivo"))
        self.opc_modo_agregar_desde_archivo.triggered.connect(self.modo_agregar_desde_archivo)
        self.nuevo_modo = self.menu_modos.addAction(traducir("Nuevo modo"))
        self.nuevo_modo.triggered.connect(self.crear_nuevo_modo)
        self.opc_editar_modo = self.menu_modos.addAction(traducir("Editar actual"))
        self.opc_editar_modo.triggered.connect(self.editar_modo)
        opc_exportar_modo = self.menu_modos.addAction(traducir("Exportar actual"))
        opc_exportar_modo.triggered.connect(self.exportar_modo)
        self.opc_quitar_modo = self.menu_modos.addAction(traducir("Quitar actual"))
        self.opc_quitar_modo.triggered.connect(self.quitar_modo)
        self.opc_restaurar = self.menu_modos.addAction(traducir("Restaurar modos predefinidos"))
        self.opc_restaurar.triggered.connect(self.restaurar_modos_builtin)

    def eligio_modo(self):
        atajo = False
        elegido = self.sender().objectName()
        if isinstance(self.selector_modo.triggereo, QtWidgets.QShortcut):
            atajo_activado = self.selector_modo.triggereo.key().toString()
            for nombre, modo in modos.modo.items():
                if nombre == "actual":
                    continue
                if modo.atajo and modo.atajo == atajo_activado:
                    elegido = nombre
                    atajo = True
                    break

        modo_elegido = modos.modo[elegido]
        if modo_elegido.dispositivos and modo_elegido.dispositivos["tipo"] == "ask":
            mensaje = traducir("msg_setear_gpus")
            base_titulo = traducir("titulo_setear_gpus")
            opcion = alertas.alerta_generica(mensaje=mensaje, base_titulo=base_titulo, icono="pregunta",
                                             cancelable=True).exec_()
            if opcion == QMessageBox.Ok:
                self.abrir_editor_modos(elegido, elegir_dispositivos=True)
                return
            else:
                return
        if isinstance(self.selector_modo.triggereo, QtWidgets.QAction) or atajo:
            self.aplicar_modo(elegido)
            return

        modos.set_actual(elegido)
        self.selector_modo.mostrar_actual()
        modos.guardar_modos()

    def modo_agregar_desde_archivo(self):
        filtro = "JSON (*.json)"
        ruta = self.settings_ventana.ultimo_path if self.settings_ventana else ""
        titulo = traducir("Elegir Archivos")
        ruta, _ = QFileDialog.getOpenFileName(self, caption=titulo, directory=ruta, filter=filtro)
        # ruta, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileName()", "", "(*.json)")
        if not ruta:
            return
        modos.leer_modos(ruta, reemplazar=False)
        self.selector_modo.actualizar(modos)
        self.crear_botones_toolbar_modos()
        self.selector_modo.mostrar_actual()

    def crear_nuevo_modo(self):
        self.abrir_editor_modos()

    def abrir_editor_modos(self, nombre_modo="", elegir_dispositivos=False):
        EditorModos(self, nombre_modo, elegir_dispositivos)


    def actualizar_post_edicion_modo(self):
        self.selector_modo.actualizar(modos)
        self.crear_botones_toolbar_modos()
        self.selector_modo.mostrar_actual()


    def editar_modo(self):
        actual = self.selector_modo.objectName()
        self.abrir_editor_modos(nombre_modo=actual)

    def exportar_modo(self):
        titulo = traducir("Guardar como")
        filtro = "JSON (*.json)"
        ruta = QtCore.QDir.home()
        nombre = self.selector_modo.objectName()
        ruta = ruta.filePath(nombre + ".json")
        archivo, _ = QFileDialog.getSaveFileName(self, caption=titulo, directory=ruta, filter=filtro)
        if not archivo:
            return
        # _, extension = os.path.splitext(archivo)
        # extension = extension or ".json"
        path = os.path.join(os.path.dirname(archivo), os.path.basename(archivo))
        modos.exportar_modo(path)

    def restaurar_modos_builtin(self):
        modos.crear_defaults()
        self.selector_modo.actualizar(modos)
        self.crear_botones_toolbar_modos()

    def quitar_modo(self):
        if len(modos.lista_modos) > 1:
            modos.modo.pop(modos.actual)

        modos.modo['actual'] = modos.lista_modos[-1]
        self.selector_modo.actualizar(modos)
        self.crear_botones_toolbar_modos()
        self.selector_modo.mostrar_actual()

    def actualizar_selector_colas(self):
        self.selector_cola.actualizar(colas.lista[::-1])
        self.selector_cola.setText(colas.lista[-1])

    def rellenar_menu_colas(self):
        self.menu_colas.clear()
        self.nueva_cola = self.menu_colas.addAction(traducir("Nueva cola nombrada"))
        self.nueva_cola.triggered.connect(self.crear_nueva_cola)
        self.browse_cola = self.menu_colas.addAction(traducir("Abrir cola"))
        self.browse_cola.triggered.connect(self.cargar_cola)
        self.opc_cola_agregar_desde_archivo = self.menu_colas.addAction(traducir("Añadir desde archivo"))
        self.opc_cola_agregar_desde_archivo.triggered.connect(self.cola_agregar_desde_archivo)
        self.opcion_renombrar = self.menu_colas.addAction(traducir("Renombrar"))
        self.opcion_renombrar.triggered.connect(self.renombrar_cola)
        self.opcion_quitar_cola = self.menu_colas.addAction(traducir("Quitar"))
        self.opcion_quitar_cola.triggered.connect(self.quitar_cola)
        self.opc_exportar_cola = self.menu_colas.addAction(traducir("Guardar cola"))
        self.opc_exportar_cola.triggered.connect(self.exportar_cola)
        opc_tareas_post = self.menu_colas.addAction(traducir("tareas_post_render"))
        opc_tareas_post.triggered.connect(self.abrir_ventana_tareas)
        opc_estimador = self.menu_colas.addAction(traducir("opcion_estimador"))
        opc_estimador.triggered.connect(self.abrir_estimador)

    def guardar_actual(self):
        colas.guardar()
        watch_folders.guardar()
        if cola.tareas:
            cola.tareas.guardar()

    def dejar_cola_atras(self):
        self.guardar_actual()
        self.reset_cola()

    def reset_cola(self):
        watch_folders.defaults()
        cola.tareas = None
        self.ventana_watchfolders = None
        self.quitar_todos(preservar_livelogs=True)

    def releer_cola(self):
        self.quitar_todos(preservar_livelogs=True)
        colas.abrir()

    def renombrar_cola(self):
        anterior = self.selector_cola.text()
        nombre, ok = QInputDialog.getText(self, traducir("Ingresar nuevo nombre para la cola"), anterior,
                                          text=anterior)
        if not ok or not nombre:
            return
        self.edito_nombre_cola(anterior, nombre)

    def quitar_cola(self):
        if len(colas.lista) < 2:
            return
        self.tablaPrincipal.clear()
        colas.quitar(colas.actual)
        colas.cambiar(colas.actual)
        self.selector_cola.setText(colas.actual)
        self.actualizar_selector_colas()

    def edito_nombre_cola(self, anterior, nuevo):
        if nuevo == "Default":
            self.selector_cola.setText("Default")
            return

        if nuevo in colas.lista_alias:
            nuevo = colas.renombrar_duplicado(nuevo)

        colas.set_alias(anterior, nuevo)
        colas.guardar()

        self.actualizar_selector_colas()
        self.selector_cola.setText(nuevo)

    def cambiar_cola(self, nueva):
        self.dejar_cola_atras()
        colas.cambiar(nueva)
        self.selector_cola.setText(nueva)

    def eligio_cola(self):
        elegida = self.sender().text()
        self.cambiar_cola(elegida)

    def crear_nueva_cola(self):
        nombre, ok = QInputDialog.getText(self, traducir("Ingresar nombre para la nueva cola"), "")
        if not ok or not nombre:
            return

        self.dejar_cola_atras()
        self.boton_watchfolder.setChecked(False)

        colas.add_queue(nombre)

    def elegir_json(self):
        return self.elegir_archivo("json")

    def elegir_archivo(self, formato, existente=True, nombre_sugerido=""):
        titulo = traducir("Elegir archivo")
        filtro = formato.upper() + " (*.{})".format(formato.lower())
        if existente:
            archivo, _ = QFileDialog.getOpenFileName(self, caption=titulo, directory="", filter=filtro)
        else:
            archivo, _ = QFileDialog.getSaveFileName(self, caption=titulo, directory=nombre_sugerido,  filter=filtro)

        return archivo

    def cargar_cola(self):
        archivo = self.elegir_json()
        # archivo, _ = QFileDialog.getOpenFileName(self, traducir("Elegir archivo"), "", "(*.json)")
        if archivo:
            self.lectura_de_cola(archivo, switchear=True)

    def cola_agregar_desde_archivo(self):
        archivo = self.elegir_json()
        # archivo, _ = QFileDialog.getOpenFileName(self, traducir("Elegir archivo"), "", "(*.json)")
        if archivo:
            self.lectura_de_cola(archivo, switchear=False)

    def exportar_cola(self):
        titulo = traducir("Guardar como")
        filtro = "JSON (*.json)"
        ruta = QtCore.QDir.home()
        ruta = ruta.filePath(colas.actual + ".json")
        archivo, _ = QFileDialog.getSaveFileName(self, caption=titulo, directory=ruta, filter=filtro)
        # archivo, _ = QFileDialog.getSaveFileName(self, traducir("Elegir archivo"), "", "(*.json)")
        if archivo:
            self.exportado_de_cola(archivo)

    def exportado_de_cola(self, archivo_cola):
        try:
            with open(archivo_cola, "w", encoding="utf8") as archivo_guardando:
                items = self.tablaPrincipal.topLevelItemCount()
                for n in range(items):
                    item_n = self.tablaPrincipal.topLevelItem(n)
                    archivo_guardando.write(item_n.a_json() + "\n")

        except IOError as e:
            print(e)
            return
        watch_folders.guardar(archivo_cola)

    def duplicar_cola_y_cambiar(self, nombre_duplicada):
        colas.guardar()
        colas.add_queue(nombre_duplicada)
        # colas.duplicar_archivo(nombre_duplicada)
        # self.dejar_cola_atras()
        # colas.abrir_interna_no_listada(nombre_duplicada)

    def lectura_externa_launch(self, archivo_cola=""):
        nombre_archivo = os.path.split(archivo_cola)[1]
        archivo_tentativo = os.path.join(Datas.ruta_base_colas, nombre_archivo)
        if os.path.isfile(archivo_tentativo):
            if not colas.abrir_externa(archivo_tentativo):
                if archivo_cola.endswith(".json"):
                    colas.lectura_de_cola(archivo_cola)
                else:
                    colas.lectura_cola_legacy(archivo_cola)
        else:
            colas.abrir_externa(archivo_cola)
        self.cambio_items_actualizar()
        self.actualizar_selector_colas()

    def lectura_de_cola(self, archivo_cola="", ruta_original=True, switchear=False):

        if switchear:
            self.dejar_cola_atras()

        if not archivo_cola:
            colas.abrir()
        else:
            colas.abrir_externa(archivo_cola, ruta_original, switchear)

        self.cambio_items_actualizar()
        # if archivo_cola and switchear:
        #     self.actualizar_selector_colas()

    def verificar_version_blender(self, datos_item, ruta_version_blender):
        tag_blender = datos_item.tag_blender
        if tag_blender not in versiones_blender.blenders:
            es_valida, version = blenders.validar_ruta_y_obtener_version(ruta_version_blender)
            if es_valida:
                versiones_blender.agregar(tag_blender, ruta_version_blender, version)
            else:
                pass

        # if pedir_ruta_bl_alt:
        #     ubi_blender.erronea()
        #     self.tablaPrincipal.clearSelection()
        #     ultimo_item = self.tablaPrincipal.topLevelItem(self.tablaPrincipal.topLevelItemCount() - 1)
        #     if ultimo_item:
        #         ultimo_item.setSelected(True)
        #     self.cambiar_blender()

    def verificar_existencia_blends(self, datos_item):
        if not bleuristicas.blend_existe(datos_item.ruta_blend, datos_item.nombre_blend):
            correccion_automatica = ""
            if self.dialogo_blend_no_encontrado is None:
                self.dialogo_blend_no_encontrado = bleuristicas.DialogoBlendNoEncontrado(self, datos_item)
            else:
                correccion_automatica = self.dialogo_blend_no_encontrado.actualizar(datos_item)
                if correccion_automatica:
                    datos_item.ruta_blend = correccion_automatica

            if not correccion_automatica:
                self.dialogo_blend_no_encontrado.exec_()
                if self.dialogo_blend_no_encontrado.accion == "CANCELAR":
                    return "salir"
                elif self.dialogo_blend_no_encontrado.accion == "OMITIR":
                    self.dialogo_blend_no_encontrado.accion = None
                    return "continuar"



    def cerrar_text_logs(self):
        for ventana in self.ventana_log_individual[::-1]:
            ventana.close()
        if self.ventana_log:
            self.ventana_log.close()

    def mostrar_logs_individuales(self):
        items = self.tablaPrincipal.selectedItems()
        for item in items:
            self.mostrar_log_individual(item)

        pantalla = QtGui.QGuiApplication.primaryScreen()
        ancho_pantalla = pantalla.size().width()
        ancho_log = self.ventana_log_individual[-1].width()
        alto_log = self.ventana_log_individual[-1].height()

        for i, ventana in enumerate(self.ventana_log_individual):
            offset_x = i * ancho_log % ancho_pantalla
            offset_y = alto_log * (i * ancho_log // ancho_pantalla)
            ventana.move(offset_x, offset_y)

    def mostrar_log_individual(self, item):
        ventana_log_individual = VentanaInfo(self, index=len(self.ventana_log_individual))
        self.ventana_log_individual.append(ventana_log_individual)
        try:
            with open(colas.ruta_log, 'r', encoding="utf8") as contenido_log:
                contenido_log.seek(item.last_log_start)
                log = contenido_log.read(item.last_log_end - item.last_log_start)
        except (IOError, TypeError) as error_log:
            print(error_log)
            return
        ventana_log_individual.info.setPlainText(log.strip())
        ventana_log_individual.setWindowTitle("Log - " + colas.actual + " | " + item.ruta_blend_completa)
        ventana_log_individual.show()
        # self.ventana_log_individual.setWindowState(
        #     self.ventana_log_individual.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        ventana_log_individual.activateWindow()

    def mostrar_log(self):
        try:
            with open(colas.ruta_log, 'r', encoding="utf8") as contenido_log:
                log = contenido_log.read()
        except IOError as error_log:
            print(error_log)
            log = ""
        self.ventana_log.info.setPlainText(log)
        self.ventana_log.setWindowTitle("Log - " + colas.actual)
        self.ventana_log.show()
        self.ventana_log.setWindowState(
            self.ventana_log.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.ventana_log.activateWindow()

        self.ventana_log.info.moveCursor(QtGui.QTextCursor.End)
        self.ventana_log.info.ensureCursorVisible()

    def actualizar_progreso(self, numero_frame, total_frames):
        if total_frames == 0:
            return
        progreso = numero_frame / total_frames + self.cola.renderizados_tanda
        progreso *= 100 / self.cola.num_blends_a_renderizar
        self.progreso_taskbar.setValue(int(progreso))

    def actualizar_numero_blends(self, num_items=None):
        self.actualizar_lista_estado()
        self.manejo_statusbar.actualizar_numero_blends(num_items)

    def estado_reset_con_blends(self):
        if self.cola.estado == "renderizando":
            return
        self.cola.estado = "no_iniciada"
        self.manejo_statusbar.actualizar_estado()
        self.cambio_seleccion()
    #
    # def status_agregar_separador(self, nombre):
    #     linea = QtWidgets.QFrame()
    #     linea.setFrameShape(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Raised)
    #     self.status_separadores[nombre] = linea
    #     self.statusbar.addWidget(linea)
    #
    # def status_quitar_separador(self, nombre):
    #     if nombre in self.status_separadores:
    #         self.status_separadores[nombre].hide()


class LoteDeArchivos:
    attrs_item = ["modo", "patron_nombrado", "args_extra", "frames"]
    def __init__(self, archivos, con_escenas=False, script="", patron_nombrado=None, args_extra="", frames="",
                 nombre_modo=None, evitar_repetidos=False):
        self.archivos = archivos
        self.nombre_modo = modos.actual if nombre_modo is None else nombre_modo
        self.con_escenas = con_escenas
        self.script = script
        modo_lote = modos.modo[modos.actual] if not nombre_modo else modos.modo[nombre_modo]
        self.patron_nombrado = patron_nombrado if patron_nombrado else modo_lote.patron_nombrado  # toma precedencia el de watchfolder y luego el del modo
        self.args_extra = agregar_linea(modo_lote.args_extra, args_extra)
        if modo_lote.dispositivos and modo_lote.parallel_gpu and modo_lote.auto_duplicar:
            self.duplicando = sum(1 for disp in modo_lote.dispositivos if disp != 'tipo') - 1
        else:
            self.duplicando = 0
        self.frames = frames
        self.evitar_repetidos = evitar_repetidos

    @property
    def modo(self):
        return self.nombre_modo # esta cosa fea es porque se vuelve confuso a veces referirse a nombres de modo vs objeto modo. Los itemcola tienen el nombre del modo en item.modo y para comparar con eso viene bien poder usar acá también lote.modo


#
# class ModoEncoder(json.JSONEncoder):
#     def default(self, obj):
#         if isinstance(obj, Modo):
#             return obj.__dict__  # Serialize the __dict__ attribute of the Modo instance
#         return super().default(obj)
#

# class Modo:
#     def __init__(self, nombre="", background=True, tipo="animacion", usar_arg_tipo=True, frames_predefinidos="",
#                  dispositivos=None, motor_dispositivos=None,
#                  parallel_gpu=False, auto_duplicar=False,
#                  overwrite_placeholders=False, args_extra="", pedir_script=False, atajo=None, patron_nombrado=None,
#                  version_blender="Default"):
#         self.tipo = tipo
#         self.usar_arg_tipo = usar_arg_tipo
#         self.background = background
#         self.nombre = nombre
#         self.frames_predefinidos = frames_predefinidos
#         self.dispositivos = dispositivos
#         self.motor_dispositivos = motor_dispositivos
#         self.parallel_gpu = parallel_gpu
#         self.auto_duplicar = auto_duplicar
#         self.overwrite_placeholders = overwrite_placeholders
#         self.args_extra = args_extra
#         self.pedir_script = pedir_script
#         self.patron_nombrado = patron_nombrado
#         self.atajo = atajo
#         self.version_blender = version_blender




# class ManagementModos:
#     args_tipo = {"animacion": "-a", "frames": "-f"}
#     traducibles = {"modo_animacion", "modo_frames", "modo_script"}
#
#     def __init__(self):
#         self.modo = UnDefaultDict(default=self.default)
#         self.modo.update({"actual": "modo_animacion"})
#         self.builtin = {}
#
#     def default(self, nombre_modo):
#         if not self.builtin:
#             self.crear_builtins()
#         if nombre_modo in self.builtin:
#             return self.builtin[nombre_modo]
#         else:
#             return self.builtin["modo_animacion"]
#
#     # @property
#     # def modo(self):
#     #     return self._modo()
#
#     def guardar_modos(self):
#         data = json.dumps(self.modo, cls=ModoEncoder, indent=4)
#         try:
#             with open(Datas.ruta_modos, "w") as json_modos:
#                 json_modos.write(data)
#         except IOError:
#             return False
#         return True
#
#     def exportar_modo(self, path):
#         nombre_modo_actual = self.modo['actual']
#         data = json.dumps({nombre_modo_actual: self.modo[nombre_modo_actual]}, cls=ModoEncoder, indent=4)
#         try:
#             with open(path, "w") as json_modos:
#                 json_modos.write(data)
#         except IOError:
#             pass
#
#     def leer_modos(self, ruta=None, reemplazar=True):
#         if not ruta:
#             ruta = Datas.ruta_modos
#         try:
#             with open(ruta, "r") as json_modos:
#                 data_modos = json.load(json_modos)
#                 modos_nuevos = UnDefaultDict(default=self.default)
#                 modos_nuevos.update({nombre: Modo(**data) if nombre != "actual" else data for nombre, data in
#                                      data_modos.items()})
#                 if reemplazar:
#                     self.modo = modos_nuevos
#                 else:
#                     self.modo.update(modos_nuevos)
#                     self.set_actual(list(modos_nuevos)[0])
#         except (IOError, AttributeError, json.decoder.JSONDecodeError, TypeError) as e:
#             print("Error reading modes file. ", e)
#             return False
#
#         return True
#
#     @property
#     def actual(self):
#         return self.modo["actual"]
#
#     @classmethod
#     def traducir(cls, nombre):
#         for traducible in cls.traducibles:
#             traducido = traducir(traducible)
#             if nombre == traducido:
#                 nombre += " (2)"
#             if nombre == traducible:
#                 return traducido
#         return nombre
#
#     def set_actual(self, nombre_actual):
#         self.modo["actual"] = nombre_actual
#
#     @property
#     def lista_modos(self):
#         lista = [nombre for nombre in self.modo if nombre != "actual"]
#         return lista
#
#     def crear_builtins(self):
#         modo_animacion = Modo(nombre="modo_animacion", tipo="animacion", atajo="Ctrl+Alt+A")
#         modo_frames = Modo(nombre="modo_frames", tipo="frames", atajo="Ctrl+Alt+F")
#         modo_script = Modo(nombre="modo_script", tipo="animacion", usar_arg_tipo=False, pedir_script=True)
#         modo_parallel = Modo(nombre="Parallel GPU (Anim)", tipo="animacion", dispositivos={"tipo": "ask"},
#                              parallel_gpu=True,
#                              auto_duplicar=True, overwrite_placeholders=True)
#         modo_viewport = Modo(nombre="Viewport Animation", background=False, tipo="animacion", usar_arg_tipo=False,
#                              args_extra="--python-expr import bpy; bpy.ops.render.opengl(animation=True); bpy.ops.wm.quit_blender()")
#         for modo in (modo_animacion, modo_frames, modo_script, modo_parallel, modo_viewport):
#             self.builtin.update({modo.nombre: modo})
#
#     def crear_defaults(self):
#         self.crear_builtins()
#         self.modo.update(self.builtin)


class ColaDeRender(QObject):
    signal_estado = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.item_renderizando = None
        self.tope = False
        self.ventana = None
        self.tablaPrincipal = None
        self.columna = ItemCola.columna
        self.accion_interrumpidos = None
        self.accion_renderizados = None
        self.modo_1 = {"accion_interrumpidos": "continuar", "accion_renderizados": "omitir"}
        self.modo_2 = {"accion_interrumpidos": "reiniciar", "accion_renderizados": "omitir"}
        self.modo_3 = {"accion_interrumpidos": "reiniciar", "accion_renderizados": "reiniciar"}
        self.num_activos = 0
        self.estado = "vacia"
        self.num_blends_a_renderizar = 0
        self.renderizados_tanda = 0
        self.fallados_tanda = 0
        self.intervalo_despertar = 150000
        self.intervalo_backupear = 600000 // 3  # bacfkupea cada diez minutos aunque por ahora más seguido pa proba
        self.aux_alternancia = 1
        self.flag_cortar_tras_frame = False
        self.guardo_ultimo = False
        self.activo_consola = None
        self.mensaje_final = None
        self.conjunto_render = None
        self.timer_instancia_render = QTimer()
        # self.timer_instancia_render.setInterval(3000)
        self.timer_instancia_render.timeout.connect(self.renderizar_cola)
        self.timer_instancia_render.setSingleShot(True)
        self.hora_inicio = None
        self.hora_fin = None
        self.tareas = None
        self.tope_frames_por_job = 1  # solo activo cuando está activo el flag_cortar tras frame. Se usa para la
        # medición de tiempo
        self.estimando = False

    def tiempo_total(self):
        if self.hora_fin and self.hora_inicio:
            return UtilidadesTiempo.delta_formateado(self.hora_inicio, self.hora_fin)
        else:
            return ""

    def backupear_durante_render(self):
        if self.estado != "renderizando":
            return
        if tipo_build == "debug":
            Debug.loguear_actividad("Updating queue info backup")
        colas.guardar()
        QTimer.singleShot(self.intervalo_backupear, self.backupear_durante_render)

    def mover_mouse(self):
        if self.estado != "renderizando":
            return
        cursor = QtGui.QCursor()
        posicion = cursor.pos()
        cursor.setPos(posicion.x() + self.aux_alternancia, posicion.y())
        self.aux_alternancia *= -1
        if tipo_build == "debug":
            Debug.loguear_actividad("Keeping pc awake")
        # cursor.setPos(posicion.x(), posicion.y())
        QTimer.singleShot(self.intervalo_despertar, self.mover_mouse)

    def iconos_windows(self):
        if plataforma == "Windows":
            if self.ventana.boton_apagar.isChecked():
                self.ventana.boton_taskbar.setOverlayIcon(iconos.icono_apagar_on)
            else:
                self.ventana.boton_taskbar.setOverlayIcon(iconos.estados['renderizando'])
            self.ventana.progreso_taskbar.setVisible(True)

    def valores_iniciales_procesamiento(self, accion_interrumpidos, accion_renderizados):
        self.accion_interrumpidos = accion_interrumpidos
        self.accion_renderizados = accion_renderizados
        self.tope = False
        self.flag_cortar_tras_frame = False

        self.ventana.detener_luego.setIcon(QtGui.QIcon())
        self.ventana.detener_luego_frame.setIcon(QtGui.QIcon())

    def loggear_inicio_procesamiento(self):
        if self.estimando:
            return
        try:
            with open(colas.ruta_log, "a+", encoding='utf-8') as archivo_log_escritura:
                archivo_log_escritura.write(
                    "\n\n================================================================================")
                self.hora_inicio = datetime.now()
                self.hora_fin = None
                archivo_log_escritura.write(traducir("procesamiento iniciado") + self.hora_inicio.strftime(
                    UtilidadesTiempo.formato_fecha))
        except IOError:
            pass

    def mantener_despierta(self):
        if plataforma == "Windows":
            WindowsDespierto.mantener()
        else:
            QTimer.singleShot(self.intervalo_despertar, self.mover_mouse)  # se supone que para cuando acabe
            # este timer self.renderizando() ya no va a ser none

    def marcar_omisibles(self):
        for i in range(self.tablaPrincipal.topLevelItemCount()):
            item_i = self.tablaPrincipal.topLevelItem(i)
            if self.conjunto_render is not None:
                item_i.procesado = item_i not in self.conjunto_render
            else:
                item_i.procesado = (item_i.estado == "terminado" and self.accion_renderizados == "omitir") or (
                        item_i.estado == "interrumpido" and self.accion_interrumpidos == "omitir")

    def procesar_omitiendo_previos(self):
        # esta funcion solo se usa por watchfolders.
        if watch_folders.activado:
            self.procesar("omitir", "omitir")

    def procesar_sin_preguntar(self):
        accion_interrumpidos = accion_renderizados = "omitir"
        for posible_accion_interrumpidos in [self.accion_interrumpidos, configuracion.anteriores_interrumpidos]:
            if posible_accion_interrumpidos and posible_accion_interrumpidos != "preguntar":
                accion_interrumpidos = posible_accion_interrumpidos
                break
        for posible_accion_terminados in [self.accion_renderizados, configuracion.anteriores_terminados]:
            if posible_accion_terminados and posible_accion_terminados != "preguntar":
                accion_renderizados = posible_accion_terminados
                break
        self.procesar(accion_interrumpidos, accion_renderizados)

    def verificar_gpus_procesar(self, encontro):
        if encontro:
            self.procesar_parteB()

    def procesar(self, accion_interrumpidos=None, accion_renderizados=None):
        if not self.tablaPrincipal.topLevelItemCount():
            return
        if self.mensaje_final:  # para el caso de watchfolder
            self.mensaje_final.alerta.close()
        else:
            self.renderizados_tanda = 0
            self.fallados_tanda = 0

        self.valores_iniciales_procesamiento(accion_interrumpidos, accion_renderizados)

        if not gpus.cycles_por_tipo and any(item.dispositivos for item in self.tablaPrincipal.items()):
            if not gpus.leer_archivos_dispositivos():
                gpus.reportar_hallazgos.connect(self.verificar_gpus_procesar)
                gpus.encontrar_dispositivos_disponibles()
                return

        self.procesar_parteB()

    def procesar_parteB(self):
        if schedules.usar_end and schedules.tipo_end == "after":
            if schedules.timer_stop:
                schedules.timer_stop.calcular_final_after_time()
                schedules.timer_stop.empezar()

        self.desactivar_faltantes()

        self.checkear_anteriores()
        self.loggear_inicio_procesamiento()
        self.calcular_total_a_renderizar()
        if not self.num_blends_a_renderizar:
            self.termino_cola()
            return

        if configuracion.mantener_despierta:
            self.mantener_despierta()

        if not self.estimando:
            QTimer.singleShot(self.intervalo_backupear, self.backupear_durante_render)

        self.signal_estado.emit(True)

        self.iconos_windows()
        self.marcar_omisibles()
        self.estado = "renderizando"
        self.num_activos = 0

        Datas.crear_scripts_render()
        # se crean cada vez para asegurarse que estén dispoonibles y actualizados

        for item in self.tablaPrincipal.items():
            item.clear_start_time()

        # self.ventana.actualizar_statusbar_widgets_item(self.ventana.status_widgets_renderizando)
        self.renderizar_cola()

    def desactivar_faltantes(self):
        print("Disabling missing blends",)
        for item in self.tablaPrincipal.items():
            if item.existe():
                continue
            item.desactivado = True

    def checkear_anteriores(self):
        if not self.accion_interrumpidos:
            if configuracion.anteriores_interrumpidos == "preguntar":
                self.checkear_interrumpidos()
            else:
                self.accion_interrumpidos = configuracion.anteriores_interrumpidos

        if not self.accion_renderizados:
            if self.conjunto_render:
                self.accion_renderizados = "reiniciar"
            elif configuracion.anteriores_terminados == "preguntar":
                self.checkear_terminados()
            else:
                self.accion_renderizados = configuracion.anteriores_terminados

    def checkear_terminados(self):
        for indice in range(self.tablaPrincipal.topLevelItemCount()):
            item = self.tablaPrincipal.topLevelItem(indice)
            if item.desactivado:
                continue
            if item.estado == "terminado":
                self.alerta_renderizados()
                break

    def checkear_interrumpidos(self):
        if self.conjunto_render:
            for item in self.conjunto_render:
                if item.desactivado:
                    continue
                if item.estado == "interrumpido":
                    self.alerta_interrumpidos()
                    break
        else:
            for indice in range(self.tablaPrincipal.topLevelItemCount()):
                item = self.tablaPrincipal.topLevelItem(indice)
                if item.desactivado:
                    continue
                if item.estado == "interrumpido":
                    self.alerta_interrumpidos()
                    break

    def alerta_interrumpidos(self):
        alerta = QMessageBox()
        alerta.setIcon(QMessageBox.Question)
        alerta.setWindowTitle(traducir("titulo hay interrumpidos"))
        alerta.setText(traducir("mensaje interrumpidos"))

        # alerta.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        btn_continuar = alerta.addButton(traducir("Continuarlos"), QMessageBox.ActionRole)
        if not self.conjunto_render:
            alerta.addButton(traducir("Omitirlos"), QMessageBox.ActionRole)
        btn_rerenderizarlos = alerta.addButton(traducir("Reiniciarlos"), QMessageBox.ActionRole)

        alerta.setDefaultButton(btn_continuar)

        alerta.exec_()

        if alerta.clickedButton() is btn_continuar:
            self.accion_interrumpidos = "continuar"
        elif alerta.clickedButton() is btn_rerenderizarlos:
            self.accion_interrumpidos = "reiniciar"
        else:
            self.accion_interrumpidos = "omitir"

    def alerta_renderizados(self):

        alerta = QMessageBox()
        alerta.setIcon(QMessageBox.Question)
        alerta.setWindowTitle(traducir("titulo ya renderizados"))
        alerta.setText(traducir("mensaje ya renderizados"))

        # alerta.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        btn_omitir = alerta.addButton(traducir("Omitirlos"), QMessageBox.ActionRole)
        btn_rerenderizarlos = alerta.addButton(traducir("Reiniciarlos"), QMessageBox.ActionRole)

        alerta.setDefaultButton(btn_omitir)

        alerta.exec_()

        if alerta.clickedButton() is btn_omitir:
            self.accion_renderizados = "omitir"
        elif alerta.clickedButton() is btn_rerenderizarlos:
            self.accion_renderizados = "reiniciar"

    def calcular_total_a_renderizar(self):
        if self.conjunto_render:
            self.num_blends_a_renderizar = len(self.conjunto_render)
            return
        omitidos = 0
        for indice in range(self.tablaPrincipal.topLevelItemCount()):
            item = self.tablaPrincipal.topLevelItem(indice)
            if item.desactivado:
                omitidos += 1
                continue
            if self.accion_renderizados == "omitir" and item.estado == "terminado":
                omitidos += 1
            if self.accion_interrumpidos == "omitir" and item.estado == "interrumpido":
                omitidos += 1

        self.num_blends_a_renderizar = self.tablaPrincipal.topLevelItemCount() - omitidos

    def verificar_existe_blend(self, item):
        path = os.path.join(item.ruta_blend, item.nombre_blend)
        if not os.path.isfile(path):
            item.estado = "fallo"
            item.procesado = True
            return False
        else:
            return True

    def siguiente_item_render(self):
        num_items = self.tablaPrincipal.topLevelItemCount()
        if not num_items:
            return None
        for i in range(num_items):
            item_i = self.tablaPrincipal.topLevelItem(i)
            procesado = item_i.procesado
            desactivado = item_i.desactivado
            if not item_i.procesado and not desactivado:
                break
        return i + procesado + desactivado

    def preparar_reiniciables(self, item):
        if (item.estado == "terminado" and self.accion_renderizados == "reiniciar") or \
                (
                        item.estado == "interrumpido" and self.accion_interrumpidos == "reiniciar") \
                or item.estado == "fallo":
            item.renderizados = 0
            item.porcentaje_progreso = 0

    def verificar_frames(self, item, gpus_item):
        item.frames_renderizar_parcial = 0
        modo = modos.modo[item.modo]
        if modo.tipo == "animacion":  # and modo.usar_arg_tipo:
            if item.inicio != "" and item.fin != "" and item.step != "":  # esto significa que si rerenderiza un item habiendo cambiado el
                # numero de frames desde blender entre medio el cálculo va a dar mal, podría evitar eso aplicando esto
                # solo si los inicio y fin están argumentados, pero eso arruinaría el caso de multiples escenas porque
                # no tomaría la info sabida en esos casos y este script solo lee para la escena activa
                item.recalcular_num_frames_renderizar_animacion()
                return True

            item.preparando = True

            def avisar():
                item.asimilar_info_escena(preservar_argumentadas=True)
                self.inicio_render_item(item, gpus_item)

            item.leer_escenas_item(avisar=avisar, cursor_espera=False, pasar_parametro=False)
            return False

        if modo.tipo == "frames" and modo.usar_arg_tipo:
            item.recalcular_num_frames_renderizar_frames()
        return True

    def renderizar_cola(self):
        if tipo_build == "debug":
            Debug.loguear_actividad("Starting render queue instance")
        if self.estado == "detenida":
            return

        if self.num_activos == configuracion.instancias_max:
            if "INCIERTO" in gpus.ocupados or all(
                    [item.procesado or item.desactivado or not item.parallel_gpu for item in
                     self.tablaPrincipal.items()]):
                return

        self.desactivar_faltantes() #quizás exesivo hacer estoo cada vez, es más que nada para el casoo de
        # arcivo agregado poor watchfolder, que activa el render de la coola y si se boorra, que poodría pasar,
        # que no coolapse el mundo

        if self.siguiente_item_render() > self.tablaPrincipal.topLevelItemCount() - 1:
            return
        preparando = any([item.preparando for item in self.tablaPrincipal.items()])

        if self.tope and not preparando:
            return

        item_actual = self.tablaPrincipal.topLevelItem(self.siguiente_item_render())

        if not self.verificar_existe_blend(item_actual):
            self.renderizar_cola()
            return

        self.preparar_reiniciables(item_actual)

        gpus_item = None
        if item_actual.parallel_gpu:
            if not gpus.cycles_por_tipo:
                if not gpus.leer_archivos_dispositivos():
                    gpus.encontrar_dispositivos_disponibles()
            for gpu_i in item_actual.dispositivos:
                if gpus.nombre_unico_para_id(gpu_i) not in gpus.ocupados:
                    gpus_item = [gpu_i]
                    break
        elif item_actual.tipo_dispositivos == "Eevee":  # para el caso en que eligió eevee pero no parallel
            gpus_item = item_actual.dispositivos if not set(item_actual.dispositivos).issubset(gpus.ocupados) else None
            # esto es para el caso de no parallel_gpu en eevee y ahí siempre debería haber un solo dispositivo,
            # así que esto se podría hacer chequeando dispositivos[0] también
        else:
            if self.num_activos >= configuracion.instancias_max:
                return
            # acá faltaría un paso extra de tratar de ver los dispositivos por defecto en blender si no hay seteados en
            # b-renderon y ocupar esos en lugar de incierto
            gpus_item = item_actual.dispositivos if item_actual.dispositivos else {"INCIERTO"}

        if gpus_item is None:
            if not self.num_activos:
                self.signal_estado.emit(False)
            return

        self.inicio_render_item(item_actual, gpus_item)

    def inicio_render_item(self, item_actual, gpus_item):
        if not self.verificar_frames(item_actual, gpus_item):
            # esto manda a una lectura paralela de escena si no dispone la info, volviendo a mandar a renderizar luego
            # por lo tanto es importante ver que no haya info acumulativa previo a esto. Por eso lo de los gpus se ve
            # antes pero los agregados a ocupancia se hacen después, cosa que no quede en preparing el siguiente al
            # último correcto.
            # vuelve a mandar acá para volver a verificar los frames ahora que tiene la data
            return

        if not gpus.nombres_unicos:
            if not gpus.leer_archivos_dispositivos():
                gpus.encontrar_dispositivos_disponibles()
        gpus.ocupar_gpus(gpus_item)

        item_actual.render = Render(self, item_actual, gpus_item)

        self.num_activos += 1
        if self.num_activos == 1:
            self.ventana.dock_consola.activo = item_actual
            self.ventana.dock_consola.actualizar_contenido()
            self.item_renderizando = item_actual
            if not self.ventana.tablaPrincipal.selectedItems():
                self.ventana.manejo_statusbar.cambio_item_reporta_frames(item_actual)
        else:
            self.item_renderizando = None

        self.ventana.manejo_statusbar.actualizar_item_elegido()
        self.ventana.manejo_statusbar.actualizar_estado()

        item_actual.estado = "renderizando"
        item_actual.procesado = True

        if item_actual.escena:
            item_actual.render.log_texto += "\n" + traducir("Escena") + ": " + item_actual.escena
        if item_actual.view_layer and "view_layer" in item_actual.propiedades_argumentar:
            item_actual.render.log_texto += "\n" + "Viewlayer: " + item_actual.view_layer
        if item_actual.camara and "camara" in item_actual.propiedades_argumentar:
            item_actual.render.log_texto += "\n" + traducir("camara") + ": " + item_actual.camara

        if self.estimando:
            return
        self.timer_instancia_render.start(3000)  # multi instancias

    def marcar_tope_schedule(self):
        self.flag_cortar_tras_frame = False
        self.tope = True

    def cortar_tras_frame_schedule(self):
        self.flag_cortar_tras_frame = True
        self.tope = True

    def cortar_tras_frame(self):
        self.flag_cortar_tras_frame = not self.flag_cortar_tras_frame
        self.tope = True
        icono = [QtGui.QIcon(), app.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton)][
            self.flag_cortar_tras_frame]
        self.ventana.detener_luego_frame.setIcon(icono)
        self.ventana.detener_luego.setIcon(QtGui.QIcon())

    def marca_tope(self):
        if self.estado != "renderizando":
            return
        self.flag_cortar_tras_frame = False
        if not self.tope:
            self.tope = True
            icono = app.style().standardIcon(QtWidgets.QStyle.SP_DialogApplyButton)
        else:
            self.tope = False
            icono = QtGui.QIcon()
        self.ventana.detener_luego.setIcon(icono)
        self.ventana.detener_luego_frame.setIcon(QtGui.QIcon())

    def confirmar_y_detener(self):
        if self.estado != "renderizando":
            return

        alerta = QMessageBox()
        alerta.setIcon(QMessageBox.Question)
        alerta.setWindowTitle(traducir("Atención!"))
        alerta.setText(traducir("mensaje interrumpir render"))

        alerta.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        respuesta = alerta.exec_()

        if respuesta == QMessageBox.Yes:
            self.detener_cola()
        elif respuesta == QMessageBox.No:
            self.marca_tope()

    def detener_cola(self):
        for proc in InfosBlender.procesos_activos:
            proc.kill()

        gpus.ocupados = set()
        preparando = False
        for item_i in self.tablaPrincipal.items():
            if item_i.preparando:
                item_i.estado = item_i.estado  # para que pase por el setter
                item_i.preparando = False
                preparando = True

        if not preparando and (not self.num_activos or self.estado != "renderizando"):
            return

        for i in range(self.tablaPrincipal.topLevelItemCount()):
            item_i = self.tablaPrincipal.topLevelItem(i)
            if item_i.estado != "renderizando":
                continue
            item_i.render.proceso.finished.disconnect()
            item_i.render.detener()

        self.num_activos = 0

        if plataforma == 'Windows':
            self.ventana.limpiar_progreso_taskbar()

        self.signal_estado.emit(False)

        self.estado = "detenida"
        colas.guardar()
        self.cerrar_log(detenida=True)
        self.ventana.manejo_statusbar.actualizar_estado()
        self.ventana.manejo_statusbar.actualizar_item_elegido()
        self.timer_instancia_render.stop()

    def termino_cola(self):
        self.accion_renderizados = None
        self.accion_interrumpidos = None
        if plataforma == 'Windows':
            self.ventana.limpiar_progreso_taskbar()

        self.signal_estado.emit(False)

        gpus.ocupados = set()

        if WindowsDespierto.activo:
            WindowsDespierto.liberar()

        if self.estimando:
            self.estado = "finalizada"
            self.estimando = False
            return

        if self.renderizados_tanda > 0:
            msg = traducir("Procesamiento terminado") + "! " + \
                  str(self.renderizados_tanda - self.fallados_tanda) + \
                  [" jobs " + traducir("procesados"), " job " +
                   traducir("procesado")][self.renderizados_tanda - self.fallados_tanda == 1]
            if self.fallados_tanda > 0:
                msg += ", " + str(self.fallados_tanda) + \
                       [" jobs " + traducir("fallados"), " job " +
                        traducir("fallado")][self.fallados_tanda == 1]
        else:
            msg = traducir("procesamiento hueco terminado")

        msg += "."

        set_apagar = self.ventana.boton_apagar.isChecked()

        if plataforma == "Windows" and not set_apagar:
            self.ventana.progreso_taskbar.setValue(100)
            self.ventana.boton_taskbar.setOverlayIcon(iconos.estados["terminado"])

        if configuracion.reproducir_sonido_render:
            sonido = QSound(configuracion.sonido_render)
            sonido.play()

        self.conjunto_render = None

        self.cerrar_log()
        colas.guardar()

        self.estado = "finalizada"

        self.ventana.manejo_statusbar.actualizar_estado()
        self.ventana.manejo_statusbar.actualizar_item_elegido()

        if cola.tareas and cola.tareas.usar_aq:
            Tarea(cola.tareas.ruta_aq, cola.tareas.args_aq, cola.tareas.queue_tokens)

        self.mensaje_final = MensajeTimer(self.ventana, msg, apagar=set_apagar)
        alerta = self.mensaje_final.alerta.exec_()
        self.mensaje_final = None  # esta cuestion es por un desdoblamiento de threads en el caso de watchfolders

    def cerrar_log(self, detenida=False):
        if detenida:
            tipo_fin = traducir("interrumpido") + ": "
        else:
            tipo_fin = traducir("finalizado") + ": "
        self.hora_fin = datetime.now()
        try:
            with open(colas.ruta_log, "a+", encoding='utf-8') as archivo_log_escritura:
                archivo_log_escritura.write(
                    "\n\n\n" + traducir(
                        "procesamiento").capitalize() + " " + tipo_fin + self.hora_fin.strftime(
                        UtilidadesTiempo.formato_fecha) +
                    "\n\n" + traducir("Tiempo total de renderizado") + ": " + self.tiempo_total())

                archivo_log_escritura.write("\n=============================================="
                                            "==================================\n\n\n\n\n\n")
                archivo_log_escritura.close()
        except IOError:
            pass

    def detener_item(self, item, forzo=False, fallo=False):
        item.render.proceso.finished.disconnect()  # así se salva de que quede como
        # finalizado pero queda la cola renderizando para siempre
        item.render.detener(forzo, fallo)
        item.render.data.vigilar_frame = lambda: None  # para que no siga procesando data de items que pueden ya haber
        # sido borrados inclusive, en el caso de la estimación de tiempos
        gpus.desocupar_gpus(item.render.gpus)
        self.num_activos -= 1
        if forzo:
            self.renderizados_tanda += 1
        if not self.num_activos:
            if self.tope or (self.siguiente_item_render() > self.tablaPrincipal.topLevelItemCount() - 1):
                self.termino_cola()
                return
        self.renderizar_cola()


class EscrituraLog:
    pass


class DataRender:
    tiempo_verificar_fin = 20000
    tiempo_verificar_clavada = 15 * 1000
    intervalo_verificacion_problemas = 30 * 1000

    def __init__(self, item, render, cola):

        self.timers = None
        self.timer_presunto_fin = None
        self.timer_presunta_clavada = None
        self.timer_problemas = None

        self.definir_timers()

        self.render = render
        self.item = item
        self.cola = cola
        self.ventana = self.cola.ventana
        self.buffer_info = ""
        self.guardo_ultimo = False
        self.ultimo_frame_guardado = None
        self.ultimo_path_guardado = None
        self.frame_anterior = -1
        self.renderizados = 0
        self.renderizados_alternativo = 0
        self.inicial_frames_renderizar = item.frames_renderizar_parcial

        self.consola = self.item.consola
        self.consola.reset()
        self.mensaje_completed = ""
        self.verificador_evento_post_presunto_fin = False
        self.verificador_evento_post_presunto_hang = False
        self.verificador_evento_post_timeout = None
        self.contador_timer_verificacion_timeout = 0
        self.previos = item.renderizados
        self.info_render_i = ""
        self.reportar = self.item == self.ventana.manejo_statusbar.item_reportante
        self.mensaje_error = None
        self.n_frame = -1
        self.item.skips = 0
        if tipo_build == "debug":
            ruta = Datas.ruta_livelog_blend(self.item.nombre_blend)
            self.archivo_livelog_debug = open(ruta, "w")
        else:
            self.archivo_livelog_debug = None

        if modos.modo[self.item.modo].tipo == "frames" and modos.modo[self.item.modo].usar_arg_tipo:
            frames = self.item.frames
            if ".." in frames:
                extremos = [int(f) for f in frames.split("..")]
                self.lista_frames = list(range(extremos[0], extremos[-1] + 1))
            else:
                self.lista_frames = [int(f) for f in self.item.frames.split(",")]

            self.vigilar_frame = self.vigilar_frame_lista
        else:
            self.lista_frames = None

        # self.ultimo_esperado = int(self.item.inicio) + int(self.item.step)*int((int(self.item.fin)-int(self.item.inicio))/int(self.item.step))

    def definir_timers(self):
        self.timer_problemas = QTimer()
        self.timer_problemas.setInterval(self.intervalo_verificacion_problemas)
        self.timer_problemas.setSingleShot(True)
        self.timer_problemas.timeout.connect(self.verificaciones_problemas_renders)

        self.timer_presunta_clavada = QTimer()
        self.timer_presunta_clavada.setInterval(self.tiempo_verificar_clavada)
        self.timer_presunta_clavada.setSingleShot(True)
        self.timer_presunta_clavada.timeout.connect(self.verificar_presunta_clavada)

        self.timer_presunto_fin = QTimer()
        self.timer_presunto_fin.setInterval(self.tiempo_verificar_fin)
        self.timer_presunto_fin.setSingleShot(True)
        self.timer_presunto_fin.timeout.connect(self.verificar_presunto_fin)

        self.timers = [self.timer_problemas, self.timer_presunto_fin, self.timer_presunta_clavada]

    def buscar_error(self):
        if self.mensaje_error:
            return
        self.mensaje_error = self.consola.buscar_error()

    def leer_bloque(self):
        try:
            info_render_i = self.render.proceso.readAll().data().decode('utf-8', 'ignore')
        except AttributeError:
            return False
        # todo: probar si acá, al detectar un incomplet de string conocido como skipping existing frame tomarlo como buffer y repetir. Ver que eso no ralentice demasiado, no debería porque la mayoría de las veces daría falso y sería solo peso de un if y quizás permitiría ahorrar en algún otro lado.
        # por ahora no. En teoría los inconvenientes que estaba teniendo los resolví de otro modo.
        # if "skipping existing frame".startswith(info_render_i) and info_render_i != "skipping existing frame":
        #     # esto permite que skipping esté partido en 2, no más.
        #     self.buffer_info += info_render_i
        #     return False
        if len(info_render_i) > 2:
            info_render_i = self.buffer_info + info_render_i
            self.buffer_info = ""
            return info_render_i

        self.buffer_info += info_render_i
        return False

    def conteo_frames(self):  # cuando no se sabe si es video o frames
        if self.encontrar_saved_ruta():
            self.conteo_frames = self.encontrar_saved_ruta
            self.item.es_video = False
            try:
                self.item.ruta_frame_output = self.ultimo_path_guardado
            except:
                pass
        elif self.encontrar_appended():
            self.conteo_frames = self.encontrar_appended
            self.item.es_video = True
        else:
            return
        # self.desconectar_busqueda_inicial() # si llegó hasta aquí y no encontró cosas ya fue ya

    def procesar_error(self):
        data = self.render.proceso.readAllStandardError().data().decode('utf-8', 'ignore')
        print(data)

    def preprocesar(self):
        # print("prepro")
        info_render_i = self.leer_bloque()
        if not info_render_i:
            return

        self.alimentar_consola(info_render_i)

        skips = info_render_i.count("skipping existing")

        if skips:
            self.reconteo_verificacion_skips()

        lineas = info_render_i.splitlines()
        # print("lineas ", lineas)
        for linea in lineas:
            self.info_render_i = linea  # he vuelto a usar atributo coso en vez de local para info_render para tenerla disponible para la verificacion paralela de errores
            self.procesar()

    def procesar(self):
        # print("proce")
        # self.busqueda_inicial(info_render_i) #deprecated de momento, no funcionaba bien buscar info al comienzo porque blender no siempre la larga antes del render

        self.conteo_frames()
        # además de contar acá, hay una cuenta paralela en
        # renderizados de data que usa los cambios de número de fra. Al terminar el render
        # item.renderizados toma el valor máximo entre un conteo y otro porque este a veces
        # se saltea algún frame. Eso presuntamente ya no es necesario gracias al preproceso,
        # antes cada tanto largaba varios frames en un mismo string y se confundía el conteo

        self.encontrar_tiempo_frame()
        self.vigilar_frame()
        # print("procesó")

    def nada(self, *_):
        pass

    # def busqueda_inicial(self, info_render):
    #     handle_run_data = re.search(datas.handle_infos_render + "({.*})", info_render,  re.M)
    #     if handle_run_data:
    #         try:
    #             data = json.loads(handle_run_data.group(1))
    #             if not self.item.inicio:
    #                 self.item.inicio = data["start_frame"]
    #             if not self.item.fin:
    #                 self.item.fin = data["end_frame"]
    #             if not self.item.frames_renderizar_parcial:
    #                 self.item.frames_renderizar_parcial = int(self.item.fin) + 1 - int(
    #                     self.item.inicio) - self.item.renderizados
    #             self.item.ruta_frame_output = data["saving_path"]
    #
    #         except Exception as e:
    #             print(e)
    #         self.desconectar_busqueda_inicial()

    # def desconectar_busqueda_inicial(self):
    #     self.busqueda_inicial = self.nada

    def encontrar_appended(self):
        ultimo_append = self.info_render_i.find("Append")
        if ultimo_append != -1:
            self.guardo_ultimo = True
            self.item.renderizados += 1
            self.actualizacion_alternativa_frame()
            return True

    def encontrar_saved_ruta(self):
        # si quisiera detectar los frames de file output iria un re como este pero sin las comillas
        ocurrencia_saved_ruta = re.search("Saved:\s'(.+)", self.info_render_i, re.M)
        if ocurrencia_saved_ruta:
            self.item.renderizados += 1
            # esta actualizaciono de item.reendereizados es casi superflula: al detener o terminar see cuenta todoo de
            # vuelta y durante el rendere se usa data.renderizados que es más preciso (este pro eejemplo está mal en
            # casos de nodoos file ouotput + videeo  y en exr con preview que saca exr y jpg al mismo tiempo). Para loo
            # único que creoo que sigue siendoo relevante este renderizadoos durante el render es si crasheea/se cierra
            # el programa durantte el render, looso backups van a incluir esetee numero (poteencialmente erroooneo)
            # comoo frames reenderizados antes de la interrupción, dee acueerdoo al último backup
            self.actualizacion_alternativa_frame()
            self.guardo_ultimo = True
            ruta_completa = ocurrencia_saved_ruta.group(1)
            if ruta_completa:
                self.ultimo_frame_guardado = self.frame_anterior
                self.ultimo_path_guardado = ruta_completa.strip("'")

            return True
        return False

    def actualizacion_alternativa_frame(self):
        if self.renderizados_alternativo < self.item.frames_renderizar_parcial:
            self.renderizados_alternativo += 1
        if self.renderizados == 0 and self.renderizados_alternativo > 2:  # ej. renders de workbench
            self.actualizar_progreso_item(self.renderizados_alternativo)
            if self.renderizados_alternativo >= self.item.frames_renderizar_parcial:  # or self.frame_anterior == self.ultimo_esperado: # la segunda condicion presuntamente nunca se alcanza porque con las últimas correcciones los frames renderizados parecen contarse siempre bien. Nueva enmienda: >= porque en ocasiones puede contar renderizados de mas
                self.reconteo_verificacion_skips()
            if self.reportar:
                self.reportar_progreso(self.renderizados_alternativo)

    def vigilar_frame_lista(self):
        # esto de tratar diferente las listas de frames que anim, es para poder usar > en la comparación en vigilar
        # frames de anim, que en el caso de listas no se puede hacer porque pueden estar desordenadas.
        ocurrencia_frame = re.search("Fra:(\d+)", self.info_render_i, re.M)
        if ocurrencia_frame and ocurrencia_frame.group(1):
            self.guardo_ultimo = False  # esto no contempla el caso en que en un mismo string haya saved y fra pero estoy partiendo las lineas asi que en teoria eso nunca sucede
            frame = int(ocurrencia_frame.group(1))
            try:
                n_frame = self.lista_frames.index(frame, self.renderizados)
            except ValueError:
                return False
            if n_frame > self.n_frame:
                self.actualizar_progreso_item(frame)
                self.renderizados += 1
                self.n_frame = n_frame
                if self.reportar:
                    self.reportar_progreso(self.renderizados, frame)
                return True
        return False  # estos returns no se usan creo

    def vigilar_frame(self):
        ocurrencia_frame = re.search("Fra:(\d+)", self.info_render_i, re.M)
        if ocurrencia_frame and ocurrencia_frame.group(1):
            self.guardo_ultimo = False  # esto no contempla el caso en que en un mismo string haya saved y fra pero estoy partiendo las lineas asi que en teoria eso nunca sucede
            frame = int(ocurrencia_frame.group(1))
            if frame > self.frame_anterior:
                self.actualizar_progreso_item(frame)
                self.renderizados += 1
                if self.reportar:
                    self.reportar_progreso(self.renderizados, frame)
                self.frame_anterior = frame
                return True
        return False  # estos returns no se usan creo

    def actualizar_progreso_item(self, frame):
        estado = traduccion.estados("renderizando") + "(" + traducir(
            "frame") + ": " + str(frame) + ")"
        self.item.setText(self.cola.columna["estado"],
                          estado)
        # aqui es importante dejar la referencia al texto de
        # la columna para no actualizar el atributo estado
        self.item.frame_reportado = str(frame)
        self.render.actualizar_estimado_restante()
        self.item.actualizar_status_lista()
        self.actualizar_columna_eta()

    def actualizar_columna_eta(self):
        self.item.timer_actualizacion_eta.stop()
        self.item.actualizar_columna_eta()

    def reportar_progreso(self, renderizados, frame=None):
        if frame is None:  # antes era if not frame y reportaba mal cuando renderizaba el frame 0 claaro fijate
            frame = renderizados + 1
        # if tipo_build == "debug":
        #     Debug.loguear_actividad("Updating statusbar info")

        self.ventana.manejo_statusbar.actualizar_renderizando(self.item, str(frame), renderizados)
        if plataforma == 'Windows':
            self.ventana.actualizar_progreso(renderizados, self.item.frames_renderizar_parcial)

    def encontrar_tiempo_frame(self):
        ocurrencia_tiempo = re.search("Time:\s([0-9:\.]*)", self.info_render_i, re.M)
        if ocurrencia_tiempo and ocurrencia_tiempo.group(1):
            tiempo_frame = str(ocurrencia_tiempo.group(1))
            self.render.tiempo_por_frame.append(tiempo_frame)
            if self.reportar:
                self.ventana.manejo_statusbar.tiempo_frame.setText(traducir("Last") + ": " + tiempo_frame)

            if self.cola.flag_cortar_tras_frame and self.item.renderizados >= self.cola.tope_frames_por_job:
                self.cola.detener_item(self.item)

            if self.renderizados >= self.item.frames_renderizar_parcial or self.item.renderizados >= self.item.frames_renderizar_parcial:
                # or self.frame_anterior == self.ultimo_esperado: # la segunda condicion presuntamente nunca se alcanza porque con las últimas correcciones los frames renderizados parecen contarse siempre bien.
                self.timer_verificar_presunto_fin()

    def alimentar_consola(self, texto):
        if self.item == self.ventana.dock_consola.activo and self.ventana.dock_consola.isVisible():
            self.ventana.widget_consola.appendPlainText(texto.strip())

        self.consola += texto
        # if splitline:
        #     self.consola += "\n"

        # if self.archivo_livelog_debug:
        #     self.archivo_livelog_debug.write(texto + "\n")

    def verificaciones_problemas_renders(self):
        if tipo_build == "debug":
            Debug.loguear_actividad("Checking render process health")

        if self.item.estado != "renderizando":
            return

        if self.verificador_evento_post_timeout == len(self.consola):
            self.contador_timer_verificacion_timeout += 1
        else:
            self.contador_timer_verificacion_timeout = 0

        if self.contador_timer_verificacion_timeout * self.intervalo_verificacion_problemas >= \
                configuracion.render_timeout * 60 * 1000:
            mensaje = "Reached timeout without progress. Closing Blender."
            self.alimentar_consola(mensaje)
            # self.cola.detener_item(self.item, fallo=True)
            self.mensaje_error = Datas.errores_custom["timeout"]
            self.render.proceso.kill()
            self.render.proceso.waitForFinished(5)
            return

        if self.reconteo_verificacion_skips():
            return

        # recuento_skips = ''.join(self.consola.splitlines()).count("skipping existing fra")
        # if recuento_skips >= self.inicial_frames_renderizar:
        #     self.timer_verificar_presunta_clavada()
        # if self.frame_anterior == self.ultimo_esperado: # por si llegasen a co
        #     self.timer_verificar_presunta_clavada()
        #     return
        ultimas_lineas = self.consola.ultimas_lineas()
        self.mensaje_error = None

        for error in Datas.errores_conocidos_render.values():
            if error in ultimas_lineas:
                self.mensaje_error = error
                self.timer_verificar_presunta_clavada()
                break

            # estos errores saltan a un timer corto porque son altísimamente sospechosos,
            # vs el timeout general que es largo porque un sample puede tardar bastant
            # y por lo tanto la info render puede quedar clavada legitimamente por mucho tiempo.
        self.verificador_evento_post_timeout = len(self.consola)
        self.timer_problemas.start()
        # QTimer.singleShot(self.intervalo_verificacion_problemas, self.verificaciones_problemas_renders)

    def timer_verificar_presunta_clavada(self):
        self.verificador_evento_post_presunto_hang = len(self.consola)
        self.timer_presunta_clavada.start()
        # QTimer.singleShot(self.tiempo_verificar_clavada, self.verificar_presunta_clavada)

    def verificar_presunta_clavada(self):
        if tipo_build == "debug":
            Debug.loguear_actividad("Checking possible render hang\n")

        if self.item.estado != "renderizando":
            return
        if self.verificador_evento_post_presunto_hang != len(self.consola):
            return  # sigue en el bucle tradicional de verificacion

        mensaje = Datas.errores_custom["aborted"]
        if not self.mensaje_error:
            self.mensaje_error = mensaje
        self.alimentar_consola(mensaje)
        self.render.proceso.kill()
        self.render.proceso.waitForFinished(5)

    def reconteo_verificacion_skips(self):
        frames, skips = self.consola.recuento_skips_y_frames(calcular_skips=True)

        self.item.frames_renderizar_parcial = self.inicial_frames_renderizar - skips
        self.item.frames_renderizar_total -= skips

        if frames + skips < self.inicial_frames_renderizar:  # equivalente a if frames = num frames a renderizar
            return False
        self.timer_verificar_presunto_fin()

        return True

    def timer_verificar_presunto_fin(self):
        self.verificador_evento_post_presunto_fin = len(
            self.consola)  # setea el flag a false justo antes de llamar al timer cosa de
        # verificar si en el interludio hubo nueva info o no
        self.timer_presunto_fin.start()
        # QTimer.singleShot(self.tiempo_verificar_fin, self.verificar_presunto_fin)

    def verificar_presunto_fin(self):
        if tipo_build == "debug":
            Debug.loguear_actividad("Checking possible render completion")
        if self.item.estado != "renderizando":
            return
        if self.verificador_evento_post_presunto_fin != len(self.consola):
            return
        if not self.mensaje_completed:
            self.mensaje_completed = "\nRender completed"
        else:
            self.mensaje_completed = "\nSomething is preventing blender from quitting"
        self.alimentar_consola(self.mensaje_completed)
        self.verificador_evento_post_presunto_fin += len(self.mensaje_completed)
        if self.verificador_evento_post_presunto_fin == len(self.consola):
            mensaje = "\nClosing blender"
            self.alimentar_consola(mensaje)
            self.verificador_evento_post_presunto_fin += len(mensaje)
            self.cola.detener_item(self.item, forzo=True)
        else:
            self.timer_verificar_presunto_fin()




class MensajeTimer(QtWidgets.QWidget):
    def __init__(self, parent=None, mensaje="", apagar=False):
        QtWidgets.QWidget.__init__(self, parent)
        self.ventana = parent
        self.alerta = QMessageBox(self)
        self.alerta.setWindowTitle(traducir('Procesamiento terminado'))

        self.alerta.setIconPixmap(QtGui.QPixmap(":/iconos/ico_aviso-terminado.png").scaled(64, 64,
                                                                                           transformMode=Qt.SmoothTransformation))
        self.alerta.setText(mensaje)
        self.boton = QtWidgets.QPushButton("OK")
        self.alerta.addButton(self.boton, QMessageBox.AcceptRole)
        self.alerta.setDefaultButton(self.boton)
        self.boton.clicked.connect(self.ok)


        self.apagar = apagar
        if self.apagar:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.intervalo)
            self.timer.start(1000)
            self.tiempo = 30
            if self.ventana.isMinimized():
                self.ventana.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)

            # Bring the main window to the foreground
            self.ventana.raise_()
            self.ventana.activateWindow()
            QtWidgets.QApplication.beep()
            self.alerta.setInformativeText(traducir("Pc will shutdown."))
            btn_cancelar = QtWidgets.QPushButton(traducir("Cancelar"))
            self.alerta.addButton(btn_cancelar, QMessageBox.RejectRole)
            btn_cancelar.clicked.connect(self.cancelar)
            self.boton.setIcon(iconos.icono_apagar)
            self.texto_ok_timer()

    def ok(self):
        if self.apagar:
            apagado.apagar_pc()

    def texto_ok_timer(self):
        self.boton.setText("(" + str(self.tiempo) + ") " + "OK")

    def intervalo(self):
        self.tiempo -= 1
        self.texto_ok_timer()
        if self.tiempo == 0:
            self.boton.click()
            
    def cancelar(self):
        self.timer.stop()


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


class Render:
    def __init__(self, cola, item, gpus=None):
        self.hora_actualizacion_estimado_restante = None
        self._estimado_restante = None
        self.hora_inicio = None
        self.hora_fin = None
        self.log_texto = ""
        # self.id = id
        self.cola = cola
        self.promedio_previo = getattr(item.render, 'promedio_final_segundos', False)
        self.tiempo_por_frame = []
        self._promedio_final = None
        self._tiempo_total = None
        self.escena = ""
        self.renderlayer = ""
        self.lista_frames = ""
        self.data = DataRender(item, self, self.cola)
        self.proceso = QtCore.QProcess()
        env = QtCore.QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONUNBUFFERED", "1")
        self.proceso.setProcessEnvironment(env)
        self.proceso.readyReadStandardOutput.connect(self.data.preprocesar)
        # if tipo_build == "debug":
        #     self.proceso.setStandardOutputFile(Datas.ruta_archivo_debug_livelog)
        # self.proceso.readyReadStandardError.connect(self.data.procesar_error)
        self.proceso.finished.connect(self.termino_render)
        self.item = item
        self.intentos = 0
        self.intentos_max = 6
        self.error_final = None
        self.gpus = gpus

        self.verificar_iniciar()

    def datos_finales(self):
        self.actualizar_datos_finales()
        return {"promedio_final": self.promedio_final, "tiempo_total": self.tiempo_total,
                "error_final": self.error_final, "gpus": self.gpus,
                "promedio_final_segundos": self.promedio_final_segundos}

    def actualizar_datos_finales(self):
        self._tiempo_total = UtilidadesTiempo.delta_formateado(self.hora_inicio,
                                                               self.hora_fin)  # .strftime(formato_fecha)

        # frames = self.frames_renderizados_tanda()
        # if self.item.estado == "renderizando":  # mientras renderiza frames_renderizados_tanda cuenta 1 de más
        #     frames -= 1
        # if frames:
        #     self._promedio_final = self._tiempo_total / frames

    @property
    def promedio_final(self):
        # de momento la decisión es seguir usando este promedio que omite el primer frame y eso,
        # pero para el tiempo total usar hora fin - hora inicio
        if not self._promedio_final:
            if not any(self.tiempo_por_frame):
                return
            self._promedio_final = self.promedio_tiempo(omitir_primero=True)
        return self._promedio_final

    @property
    def promedio_final_segundos(self):
        if not self._promedio_final:
            if not any(self.tiempo_por_frame):
                return
        return self.promedio_tiempo(omitir_primero=False, en_segundos=True)

    @property
    def tiempo_total(self):
        if not self._tiempo_total:
            self._tiempo_total = UtilidadesTiempo.delta_formateado(self.hora_inicio,
                                                                   self.hora_fin)  # .strftime(formato_fecha)
            # if not any(self.tiempo_por_frame):
            #     return
            # tiempo_total_segundos = self.calcular_tiempo_total(omision=0, multiplicador=1)
            # self._tiempo_total = self.recomposicion_partes_tiempo(tiempo_total_segundos)
        return self._tiempo_total

    def tiempo_hasta_ahora(self):
        if not self.hora_inicio:
            return
        return UtilidadesTiempo.delta_formateado(self.hora_inicio,
                                                 datetime.now())

    def frames_renderizados_tanda(self):
        if not self.data:
            return False
        return self.data.renderizados or max(self.data.renderizados_alternativo, 0)


    def actualizar_estimado_restante(self):
        try:
            frames_restantes = self.item.frames_renderizar_parcial - self.frames_renderizados_tanda()
        except AttributeError as e:
            print(e)
            return
        self._estimado_restante = self.promedio_tiempo(self.frames_renderizados_tanda(), multiplicador=frames_restantes,
                                                       en_segundos=True)
        self.hora_actualizacion_estimado_restante = QTime.currentTime()

    def estimado_restante(self):
        segundos_restantes_previos = self._estimado_restante
        if not segundos_restantes_previos:
            return
        transcurrido = self.hora_actualizacion_estimado_restante.msecsTo(QTime.currentTime()) / 1000
        segundos_restantes_actuales = max(segundos_restantes_previos - transcurrido, 0)

        restante_formateado = UtilidadesTiempo.recomposicion_partes_tiempo(segundos_restantes_actuales,
                                                                           centesimas=False)
        return restante_formateado

    def promedio_tiempo(self, frames=None, multiplicador=1, omitir_primero=False, en_segundos=False):
        if not any(self.tiempo_por_frame):
            if not self.promedio_previo:
                return None
            if en_segundos:
                return self.promedio_previo * multiplicador
            promedio_final = UtilidadesTiempo.recomposicion_partes_tiempo(self.promedio_previo * multiplicador)
            return promedio_final

            # return False  # self.promedio_previo
        if not frames:
            #
            # frames = self.frames_renderizados_tanda()
            #
            # if self.item.estado == "renderizando":  # mientras renderiza frames_renderizados_tanda cuenta 1 de más
            #     frames -= 1
            if not self.data:
                return
            frames = self.data.renderizados_alternativo

        omision = omitir_primero and len(self.tiempo_por_frame) > 1
        frames = frames - omision
        if not frames:
            return False

        tiempo_total_en_segundos = self.calcular_tiempo_total(omision, multiplicador)
        promedio_en_segundos = round(tiempo_total_en_segundos / frames, 2)
        if en_segundos:
            return promedio_en_segundos

        promedio_final = UtilidadesTiempo.recomposicion_partes_tiempo(promedio_en_segundos)
        return promedio_final

    def calcular_tiempo_total(self, omision, multiplicador):  # todo: mover esto a UtilidadesTiempo
        centesimas = 0
        segundos = 0
        minutos = 0
        horas = 0

        for i, tiempo_por_frame in enumerate(self.tiempo_por_frame[omision:]):
            descomposicion = re.search("((\d+):)?(\d+):(\d+)\.(\d+)",
                                       tiempo_por_frame)  # esto se podría calcular de los
            #  horarios de inicio y fin de cada render pero prefiero hacerlo así para que sea más real el promedio por frame
            if descomposicion:
                if descomposicion.group(2):
                    horas += int(descomposicion.group(2))
                if descomposicion.group(3):
                    minutos += int(descomposicion.group(3))
                if descomposicion.group(4):
                    segundos += int(descomposicion.group(4))
                if descomposicion.group(5):
                    centesimas += int(descomposicion.group(5))  # gronchesco pero de momento es lo que hay

        tiempo_total_en_segundos = multiplicador * (horas * 3600 + minutos * 60 + segundos + centesimas / 100)
        return tiempo_total_en_segundos

    def guardar_path_salida(self):
        if self.item.ruta_output not in ("", "*None*") or self.item.nombre_output not in ("", "*None*"):
            return
        try:
            self.item.ruta_output, self.item.nombre_output = os.path.split(self.data.ultimo_path_guardado)
        except AttributeError:
            pass

    def detener(self, forzo=False, fallo=False):
        if self.data.archivo_livelog_debug is not None:
            self.data.archivo_livelog_debug.close()

        for timer in self.data.timers:
            timer.stop()

        self.proceso.kill()
        self.proceso.waitForFinished(5)

        # self.item.renderizados = max(
        #     self.item.render.data.renderizados + self.item.render.data.previos + self.data.guardo_ultimo - 1,
        #     self.item.renderizados)
        # self.item.renderizados = max(
        #     self.item.render.data.renderizados + self.item.render.data.previos - 1,
        #     self.item.renderizados)

        self.guardar_path_salida()

        if self.item.es_video:
            self.item.extraer_asimilar_frame_path(self.data.consola)

        self.data.consola.cerrar()
        self.item.renderizados = self.data.consola.recuento_frames()

        if forzo:
            render_completo = True
        elif self.data.guardo_ultimo:
            render_completo = self.item.renderizados == self.item.frames_renderizar_parcial
        else:
            render_completo = False

        self.item.renderizados = self.item.renderizados + self.item.render.data.previos

        if render_completo:
            self.cierre_info(estado="terminado")
        elif fallo:
            self.cierre_info(estado="fallo")
        elif self.item.renderizados == 0:
            self.cierre_info(estado="no_comenzado")
        else:
            self.cierre_info(estado="interrumpido")

    def termino_render(self):
        for timer in self.data.timers:
            timer.stop()

        if cola.tareas and cola.tareas.usar_aj:
            Tarea(cola.tareas.ruta_aj, cola.tareas.args_aj, cola.tareas.job_tokens, self.item)

        if self.data.archivo_livelog_debug is not None:
            self.data.archivo_livelog_debug.close()

        if self.item.es_video:
            self.buscar_frame_path()

        if not self.cola.num_activos:  # legacy chequear
            return

        # saved = self.item.renderizados
        # self.item.renderizados = max(self.item.render.data.renderizados + self.item.render.data.previos,
        #                              self.item.renderizados)  # porque el conteo de saved a veces falla

        self.data.consola.cerrar()
        renderizados_tanda = self.data.consola.recuento_frames(ultima_instancia_blender=True)

        self.cola.num_activos -= 1

        self.guardar_path_salida()
        # render_esta_completo = self.item.render_completo()

        # render_esta_completo = self.item.renderizados >= self.item.frames_renderizar_parcial

        # if not render_esta_completo:
        #     self.item.renderizados = saved
        if renderizados_tanda:
            self.item.renderizados = renderizados_tanda + self.item.render.data.previos
        render_esta_completo = self.item.renderizados >= self.item.frames_renderizar_total

        self.item.render.data.buscar_error()
        mensaje_error = self.item.render.data.mensaje_error
        error_no_reintentable = mensaje_error and mensaje_error not in Datas.errores_reintentables
        if not error_no_reintentable:
            if self.verificar_reiniciar(renderizados_tanda, render_esta_completo):
                return
        if configuracion.tratar_fallidos and (error_no_reintentable or self.intentos >= self.intentos_max):
            estado_final = "fallo"
            self.cola.fallados_tanda += 1
        else:
            estado_final = "terminado" if not mensaje_error else "fallo"

        self.cola.renderizados_tanda += 1
        self.cierre_info(estado=estado_final)

        self.intentos = 0

        if not self.cola.num_activos:
            if self.cola.tope or (self.cola.siguiente_item_render() > self.cola.tablaPrincipal.topLevelItemCount() - 1):
                self.cola.termino_cola()
                return

        if self.cola.tope:
            return

        gpus.desocupar_gpus(self.item.render.gpus)

        self.cola.renderizar_cola()

    def verificar_reiniciar(self, renderizados_tanda, render_esta_completo):
        if self.intentos >= self.intentos_max or not configuracion.tratar_fallidos or render_esta_completo:
            return False
        if renderizados_tanda > 1:
            self.intentos = -1  # si avanzo al menos 2 frames se reinician los intentos. es -1 porque luego le sumo 1
            self.log_texto += "\n" + str(renderizados_tanda) + " " + traducir(
                "frames renderizados")
            self.log_texto += "\n" + UtilidadesTiempo.fecha_y_hora() + traducir("error nuevo intento")
        self.intentos += 1
        self.cola.num_activos += 1
        self.verificar_iniciar()
        return True

    def buscar_frame_path(self):
        self.item.extraer_asimilar_frame_path(self.data.consola)

    def cierre_info(self, estado="terminado"):
        self.item.estado = estado
        if estado == "fallo":
            error = self.item.render.data.mensaje_error
            # if not error:
            #     ultimas_lineas = ''.join(self.item.render.data.consola[-250:].splitlines())
            #     if all([parte in ultimas_lineas for parte in ["Writing:", "crash.txt"]]):
            #         error = Datas.errores_custom["crash"]
            if error:
                self.error_final = error

        self.hora_fin = datetime.now()
        self.actualizar_datos_finales()
        self.log_texto += "\n\n" + traduccion.estados(estado).rstrip()
        self.log_texto += ": " + self.hora_fin.strftime(UtilidadesTiempo.formato_fecha)

        self.log_texto += "\n" + traducir("frames renderizados") + ": " \
                          + str(self.item.renderizados)

        if self.item.render.data.previos:
            self.log_texto += " " + traducir("en total") + ". " \
                              + str(self.item.render.data.renderizados) \
                              + traducir("desde interrupcion")

        if modos.modo[self.item.modo].tipo == "frames":
            lista_frames_renderizados = self.item.frames.split(",")
            lista_frames_renderizados = ", ".join(
                lista_frames_renderizados[self.item.render.data.previos:self.item.renderizados])
            self.log_texto += "\n" + traducir("frames renderizados") + ": " + lista_frames_renderizados
            self.log_texto += "\n" + traducir("Tiempos por frame: ") + ", ".join(self.tiempo_por_frame)
        self.loguear_promedio()
        self.item.item_estado.setText(ItemEstado.columna["eta"], "")

        try:
            with open(colas.ruta_log, "a+", encoding='utf-8') as archivo_log_escritura:
                self.item.last_log_start = archivo_log_escritura.tell()
                archivo_log_escritura.write(self.log_texto)
                self.item.last_log_end = archivo_log_escritura.tell()
        except IOError:
            pass

        # self.cierra_blend_log(detenido)

    def loguear_promedio(self):
        if self.promedio_final:
            self.log_texto += "\n" + traducir("promedio por frame")
            self.log_texto += self.promedio_final

    def parsear_argExtras(self, argumento):
        arg_parseado = []
        for linea in argumento.splitlines():
            arg_parseado.extend(linea.split(" ", 1))
        return arg_parseado

    def basedir_plataforma(self):
        if plataforma == "Linux":
            return self.item.ruta_blend + "/"
        else:
            self.proceso.setWorkingDirectory(self.item.ruta_blend)
            return ""

    def log_inicio_render(self):
        self.hora_inicio = datetime.now()
        self.log_texto = "\n\n\n---------"
        self.log_texto += "\n" + traducir("Inicio") + ": " + self.hora_inicio.strftime(
            UtilidadesTiempo.formato_fecha)
        self.log_texto += "\n" + self.item.ruta_blend + "/" + self.item.nombre_blend

    def version_blender_verificada(self):
        # if self.item.tag_blender == blenders.tag_eevee:

        if self.item.tipo_dispositivos == "Eevee" and gpus.existe_path_eevee(self.gpus[0]):
            nombre_blender = versiones_blender.tag_eevee + " ({})".format(self.gpus[0])
            blender = gpus.gpus_eevee[self.gpus[0]]
        else:
            if self.item.tipo_dispositivos == "Eevee":
                alertas.alerta_generica("alerta_path_eevee_gpu")
            nombre_blender = self.item.tag_blender
            blender = versiones_blender.ruta(nombre_blender)
        if not os.path.isfile(blender):
            self.log_texto += "\n" + traducir("alerta ruta")
            nombre_blender = "Default"
            blender = versiones_blender.ruta(nombre_blender)
            if not os.path.isfile(blender):
                blenders.alerta_ubicacion_erronea()
                self.termino_render()
                return False, False
        return blender, nombre_blender

    def truncar_frames_frames(self):
        if not self.item.renderizados:
            return self.item.frames
        renderizados = self.item.renderizados
        if self.cola.accion_interrumpidos == "continuar" and self.item.estado == "interrumpido":
            self.log_texto += " (" + traducir("Continuando render interrumpido") + "...)"
        elif self.item.estado in ["renderizando", "fallo"]:
            self.log_texto += " (" + traducir(
                "Continuando render interrumpido") + "...)"  # todo: acá podría ir una frase específica de continuar fallos
            if renderizados:
                renderizados -= 1

        if ".." in self.item.frames:
            inicio, fin = [int(i) for i in self.item.frames.split("..")]
            inicio = inicio + int(renderizados)
            return "..".join([str(inicio), str(fin)])
        lista_frames = self.item.frames.split(",")
        frames = ",".join(lista_frames[int(renderizados):])
        return frames

    def truncar_frames_animacion(self):
        # si no hay frame inicio usa +(frames renderizados) que significa, del inicio original
        # omitir los primeros (renderizados)

        renderizados = self.item.renderizados
        if self.item.estado in ["fallo", "renderizando"]:
            renderizados = max(renderizados, 0)

        if not (self.item.inicio and "inicio" in self.item.propiedades_argumentar):
            return "+" + str(renderizados)

        step = int(self.item.step) or 1
        frames_re_inicio = int(self.item.inicio) + renderizados*step

        if self.item.inicio[0] in ["+", "-"]:  # relativo
            signo = ("+", "-")[frames_re_inicio < 0]
        else:
            signo = ""

        return signo + str(abs(frames_re_inicio))

        # el +hace que sean relativos y
        #  por eso uso frames renderizados y no último frame renderizado

    def argumentos_finales_comunes(self, frames=""):
        argumentos = []

        if self.item.fin and "fin" in self.item.propiedades_argumentar:
            argumentos.extend(["-e", self.item.fin])
            self.log_texto += "\n" + traducir("Frame fin elegido") + ": " + self.item.fin

        if self.item.step and "step" in self.item.propiedades_argumentar:
            argumentos.extend(["--frame-jump", self.item.step])

        if self.item.camara and "camara" in self.item.propiedades_argumentar:
            argumentos.extend(['--python-expr', 'import bpy; bpy.context.scene.camera '
                                                '= bpy.context.scene.objects[\'' + self.item.camara + '\']'])

        argumentos_sysargv = []

        if self.item.view_layer and "view_layer" in self.item.propiedades_argumentar:
            argumentos.extend(["-P", Datas.ruta_script_elegir_viewlayer])
            argumentos_sysargv.extend([Datas.handle_viewlayer_name, self.item.view_layer])
            accion_compositing = getattr(self.item, "manejar_compositing", None)
            if accion_compositing and accion_compositing != "leave_as_is":
                argumentos_sysargv.extend([Datas.handle_compositing_action, accion_compositing])

        if self.item.colecciones and "uso_colecciones" in self.item.propiedades_argumentar:
            argumentos.extend(["-P", Datas.ruta_script_uso_colecciones])
            data_uso_colecciones = json.dumps(self.item.colecciones["seleccion"])
            argumentos_sysargv.extend([Datas.handle_colecciones_use, data_uso_colecciones])
            argumentos_sysargv.extend([Datas.handle_viewlayer_name, self.item.colecciones["viewlayer_activo"]])

        if "nombrado" in self.item.propiedades_argumentar:
            patron = self.item.patron_nombrado
            sysargv = []
            patron_ruta = auto_nombrado.reemplazar_start_time(self.item, patron["ruta_nodos"])
            patron_nombre = auto_nombrado.reemplazar_start_time(self.item, patron["nombre_nodos"])
            if patron["aplicar_a"] in auto_nombrado.aplicar_a_incluye_nodos and (
                    patron["ruta_nodos"] or patron["nombre_nodos"]):  # si hay que aplicar a nodos

                sysargv.extend([Datas.handle_output_nodes_pattern, patron_ruta, patron_nombre])
            if patron["aplicar_a"] in auto_nombrado.aplicar_a_incluye_escena:
                for token in auto_nombrado.tokens_normales_script:  # si en el nombrado común hay algún token que necesite procesarse por script
                    if token in self.item.nombrado:
                        sysargv.extend(
                            [Datas.handle_output_pattern,
                             auto_nombrado.reemplazar_start_time(self.item, self.item.nombrado)])
                        break
            if sysargv:
                argumentos.extend(["-P", Datas.ruta_script_output_path])
                argumentos_sysargv.extend(sysargv)

        if self.item.dispositivos and self.item.tipo_dispositivos and self.item.tipo_dispositivos != "Eevee" and "dispositivos" in self.item.propiedades_argumentar:

            tipo_dispositivos = self.item.tipo_dispositivos
            if not os.path.isfile(Datas.ruta_script_usar_dispositivo):
                Datas.crear_script(Datas.ruta_script_usar_dispositivo, Datas.script_usar_dispositivos)
            if self.item.parallel_gpu:
                if not gpus.cycles_por_tipo:
                    gpus.leer_archivos_dispositivos()

                dispositivos = self.gpus
            else:
                dispositivos = self.item.dispositivos

            argumentos.extend(["-P", Datas.ruta_script_usar_dispositivo])

            argumentos_sysargv.extend([Datas.handle_tipo, tipo_dispositivos])
            argumentos_sysargv.append(Datas.handle_dispositivos)
            argumentos_sysargv.extend(dispositivos)



        elif self.item.tipo_dispositivos == "CPU":
            argumentos_sysargv.extend(["--cycles-device", self.item.tipo_dispositivos])

        if self.item.args_extra:
            argumentos.extend(self.parsear_argExtras(self.item.args_extra))

        modo = modos.modo[self.item.modo]
        if modo.tipo == "frames" and not frames:
            frames = "1"

        if modo.usar_arg_tipo:
            tipo_i = modos.args_tipo[modo.tipo]
            argumentos.extend([tipo_i, frames])

        if argumentos_sysargv:
            argumentos.append('--')
            argumentos.extend(argumentos_sysargv)

        return argumentos

    def argumento_frame_inicio_animacion(self):
        # la logica es así: si está continuando un render trunca, si no está continuando pero hay frame inicio lo usa
        if self.item.estado in ["fallo", "renderizando"] or (self.item.estado == "interrumpido" \
                                                             and self.cola.accion_interrumpidos == "continuar"):
            self.log_texto += " (" + traducir("Continuando render interrumpido") + "...)"
            frame_inicio = self.truncar_frames_animacion()
        elif self.item.inicio and "inicio" in self.item.propiedades_argumentar:
            frame_inicio = self.item.inicio
        else:
            frame_inicio = ""

        if not frame_inicio:
            return []
        # if self.item.modo == "modo_animacion":
        return ["-s", frame_inicio]
        # else:
        #     relativo = frame_inicio[0] in ("+", "-")
        #     start = "bpy.context.scene.frame_start"
        #     return ["--python-expr", "import bpy; {} = {} {}".format(start, start if relativo else "", frame_inicio)]

    def armado_argumentos(self, argumentos):

        if self.item.escena:  # and "escena" in self.item.propiedades_argumentar: No importa si no está argumentado, a la escena la podemos cambiar siempre
            argumentos.extend(["-S", self.item.escena])

        if configuracion.blender_factory:
            argumentos.append('--factory-startup')

        argumentos.append('-noaudio')

        if self.item.nombrado and "nombrado" in self.item.propiedades_argumentar and self.item.patron_nombrado[
            "aplicar_a"] != 1:
            nombrado = self.item.nombrado
            argumentos.extend(["-o", auto_nombrado.reemplazar_start_time(self.item, nombrado)])

        tipo = modos.modo[self.item.modo].tipo
        if tipo == "animacion":
            argumentos.extend(["--python-expr", Datas.expresion_obtener_frame_path()])
            argumentos.extend(self.argumento_frame_inicio_animacion())
            argumentos.extend(self.argumentos_finales_comunes())
        elif tipo == "frames":
            argumentos.extend(self.argumentos_finales_comunes(self.truncar_frames_frames()))

        argumentos = [arg_i for arg_i in argumentos if
                      arg_i != '']  # esto se podria evitar sumando solo cosas con contenido pero así me aseguro

        return argumentos

    # def leer_archivo_infos_escena(self):
    #     if self.item.frames_renderizar_parcial:
    #         return
    #     ruta = os.path.join(Datas.ruta_base_jobinfo, Datas.prefijo_archivo_scenes_info + self.item.id_tmp + ".json")
    #     if os.path.isfile(ruta):
    #         print("Ok")
    #         return
    #     QTimer.singleShot(100, self.leer_archivo_infos_escena)

    def verificar_iniciar(self):
        # deprecated: ahora el recabamiento de info se hace en tread paralelo que avisa al terminar y
        # después empieza el render.
        # if self.item.recabando_info:
        #     QTimer.singleShot(500, self.verificar_iniciar)
        #     return
        self.iniciar()

    def iniciar(self):
        self.log_inicio_render()

        blender, nombre_blender = self.version_blender_verificada()
        if not blender:
            return

        self.log_texto += "\n" + traducir("Renderizado con Blender") + ": " + nombre_blender
        self.log_texto += "\n" + traducir("Tipo de render") + ": " + traducir(self.item.modo)
        if self.gpus and self.gpus != {"INCIERTO"}:
            self.log_texto += "\n" + traducir("Usando") + " " + ", ".join(self.gpus)
        argumentos = [self.basedir_plataforma() + self.item.nombre_blend]
        if modos.modo[self.item.modo].background:
            argumentos.insert(0, "-b")

        argumentos = self.armado_argumentos(argumentos)

        print("args", argumentos)
        self.data.timer_problemas.start()
        self.proceso.setArguments(argumentos)
        self.proceso.setProgram(blender)
        self.proceso.start()


class InfoFrame:
    def __init__(self, ruta_completa, numero=None, tiempo=None):
        self.tiempo = tiempo
        self.rutas_completas = [ruta_completa]
        self.numero = numero

    @property
    def nombre(self):
        return os.path.split(self.ruta_completa)[1]

    @property
    def ruta(self):
        return os.path.split(self.ruta_completa)[0]

    @property
    def ruta_completa(self):
        return self.rutas_completas[-1] # esto ees más un tema de no generar bugs con algún llamado antiguo

    def ruta_desglosada(self):
        return os.path.split(self.ruta_completa)


class InfoFrames:
    def __init__(self):
        self.data = []

    def __getitem__(self, index):
        return self.data[index]

    def __setitem__(self, index, value):
        self.data[index] = value

    def __delitem__(self, index):
        del self.data[index]

    def __len__(self):
        return len(self.data)

    def agregar_data(self, ruta_completa, numero_frame, tiempo=None):
        for info_frame in self.data:
            if numero_frame == info_frame.numero:
                info_frame.rutas_completas.append(ruta_completa)
                return
        self.data.append(InfoFrame(ruta_completa, numero_frame, tiempo))

    def __repr__(self):
        return repr(self.data)

class CampoArgumentos(QtWidgets.QPlainTextEdit):
    def __init__(self):
        super().__init__()

        # Enable text dropping
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        super().dropEvent(event)
        cursor = self.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText('\n')
        self.setTextCursor(cursor)
    #     text = event.mimeData().text()
    #     self.appendPlainText(text)


class VentanaEstimar(QtWidgets.QDialog, ui.ventana_estimar.Ui_ventana_estimar_tiempo):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.ventana = parent
        self.btn_calcular.clicked.connect(self.calcular)
        self.btn_close.clicked.connect(self.close)
        self.prohibido_cerrar = None
        self.reset_botones()
        self.btn_cancelar.clicked.connect(self.cancelar)
        self.explicacion_base.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.selector_frames.setValue(cola.tope_frames_por_job)
        self.estimado.setText("--")
        self.cola_original = colas.actual

    def closeEvent(self, event: QtGui.QCloseEvent) -> None:
        if self.prohibido_cerrar:
            event.ignore()
        else:
            event.accept()

    def reset_botones(self):
        self.btn_cancelar.setEnabled(False)
        self.btn_calcular.setEnabled(True)
        self.btn_close.setEnabled(True)
        self.prohibido_cerrar = False

    def cancelar(self):
        restore_cursor()
        self.reset_botones()
        self.ventana.accion_btn_stop()
        self.ventana.quitar_cola()

    def calcular(self):
        self.btn_cancelar.setEnabled(True)
        self.btn_calcular.setEnabled(False)
        self.btn_close.setEnabled(False)
        self.prohibido_cerrar = True
        self.calcular_tiempo_total()

    def calcular_tiempo_total(self):
        nombre = "Aux (time estimation)"
        colas.quitar(nombre)
        self.ventana.duplicar_cola_y_cambiar(nombre)
        Datas.crear_script(Datas.ruta_script_desactivar_fileoutputs, Datas.script_disable_fonodes)
        for item in self.ventana.tablaPrincipal.items():
            item.nombrado = os.path.join(Datas.ruta_base_aux_temp, "tmp")
            item.propiedades_argumentar.add("nombrado")
            item.args_extra = agregar_linea(item.args_extra, "-P " + Datas.ruta_script_desactivar_fileoutputs)
            item.args_extra = agregar_linea(item.args_extra,
                                            "--python-expr import bpy; bpy.context.scene.render.use_overwrite = True;")
            if item.estado != "no_comenzado" and not item.desactivado:
                if not item.render or not item.render.promedio_final or not item.frames_renderizar_total:
                    item.reset()
        cola.procesar("omitir", "omitir")
        cola.flag_cortar_tras_frame = True
        cola.estimando = True
        cola.tope_frames_por_job = self.selector_frames.value()
        cola.signal_estado.connect(self.procesar_info_tiempo_total)
        set_cursor_espera()

    def procesar_info_tiempo_total(self, valor):
        restore_cursor()
        tiempo_total = 0
        cola.signal_estado.disconnect(self.procesar_info_tiempo_total)
        for item in self.ventana.tablaPrincipal.items():
            try:
                tiempo_total += item.render.promedio_final_segundos * item.frames_renderizar_total
            except Exception as e:
                print("Exc", e)
                pass
        tiempo_total_formateado = UtilidadesTiempo.recomposicion_partes_tiempo(tiempo_total, centesimas=False)
        self.estimado.setText(tiempo_total_formateado)
        self.reset_botones()
        # self.ventana.tablaPrincipal.clear()

        self.ventana.quitar_cola()

    def retranslateUi(self, _):
        self.setWindowTitle(traducir("titulo_ventana_estimador"))
        self.lbl_estimado.setText(traducir("Tiempo total estimado") + ":")
        self.btn_calcular.setText(traducir("Calcular"))
        self.explicacion_base.setPlainText(traducir("explicacion_estimador"))
        self.lbl_frames.setText(traducir("Frames"))
        self.btn_cancelar.setText(traducir("Cancelar"))


class VentanaTareas(QtWidgets.QDialog, ui.ventana_tareas.Ui_ventana_tareas):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.ventana = parent
        self.selector_ruta_job = None
        self.chk_after_job, self.ruta_after_job, self.campo_args_job = self.configurar_elementos_tarea("After job",
                                                                                                       self.job_tokens())
        self.chk_after_queue, self.ruta_after_queue, self.campo_args_queue = self.configurar_elementos_tarea(
            "After queue", self.queue_tokens())
        self.configurar_arbol()
        self.leer_previos()
        self.accepted.connect(self.aceptar)

    def retranslateUi(self, _):
        self.setWindowTitle(traducir("tareas_post_render"))
        self.lbl_explicacion.setText(traducir("explicacion_tareas"))
        self.lbl_explicacion.setAlignment(Qt.AlignCenter)

    @staticmethod
    def job_tokens():
        tokens = [auto_nombrado.TokenNombrado("Blend path", "[BLEND_PATH]"),
                  auto_nombrado.TokenNombrado("Time", "[TIME]")]
        return tokens

    @staticmethod
    def queue_tokens():
        tokens = [auto_nombrado.TokenNombrado("Queue name", "[QUEUE_NAME]"),
                  auto_nombrado.TokenNombrado("Time", "[TIME]")]
        return tokens

    def configurar_elementos_tarea(self, nombre, tokens):
        chk_tarea = ItemChk(traducir(nombre), 0, self.arbol)
        ruta = ItemTitulo(traducir("Ruta"), 0, chk_tarea, centrado=True)
        selector_ruta = SelectorRuta(self.ventana)
        ruta.agregar_layout_wgt(selector_ruta, 1)
        args_titulo = ItemTitulo(traducir("Argumentos"), 0, chk_tarea)
        tokens_titulo = ItemTitulo(traducir("Tokens") + "\n" + traducir("(drag and drop)"), 0,
                                   args_titulo, centrado=True)
        layout_tokens = QtWidgets.QHBoxLayout()
        for token in tokens:
            layout_tokens.addWidget(WidgetToken(token, self))
        tokens_titulo.agregar_layout_wgt(layout_tokens, 1)
        arguments = ItemTitulo(traducir("Argumentos"), parent=args_titulo, centrado=True)
        campo_args = CampoArgumentos()
        arguments.agregar_wgt(1, campo_args)

        return chk_tarea, selector_ruta, campo_args

    def leer_previos(self):
        if not cola.tareas:
            return
        self.chk_after_job.setChecked(cola.tareas.usar_aj)
        self.chk_after_queue.setChecked(cola.tareas.usar_aq)
        self.ruta_after_job.set(cola.tareas.ruta_aj)
        self.ruta_after_queue.set(cola.tareas.ruta_aq)
        self.campo_args_job.setPlainText(cola.tareas.args_aj)
        self.campo_args_queue.setPlainText(cola.tareas.args_aq)

    def aceptar(self):
        if not cola.tareas:
            cola.tareas = Tareas()
        cola.tareas.usar_aj = self.chk_after_job.isChecked()
        cola.tareas.usar_aq = self.chk_after_queue.isChecked()
        cola.tareas.ruta_aj = self.ruta_after_job.get()
        cola.tareas.ruta_aq = self.ruta_after_queue.get()
        cola.tareas.args_aj = self.campo_args_job.toPlainText()
        cola.tareas.args_aq = self.campo_args_queue.toPlainText()
        cola.tareas.guardar()

    def configurar_arbol(self):
        self.arbol.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.arbol.setFocusPolicy(Qt.NoFocus)
        self.arbol.setAlternatingRowColors(True)
        self.arbol.setIndentation(10)
        self.arbol.setColumnWidth(0, 150)
        self.arbol.headerItem().setText(0, "")
        self.arbol.headerItem().setText(1, "")
        self.arbol.header().setFixedHeight(10)


class EditorModos(QtWidgets.QDialog, ui.editor_modo.Ui_EditorModos):
    def __init__(self, ventana, nombre_modo=None, seleccion_dispositivos=False):
        super().__init__(ventana)

        self.motor = None
        if nombre_modo:
            self.nuevo = False
            self.modo = modos.modo[nombre_modo]
        else:
            self.nuevo = True
            nombre = traducir("Nuevo modo")
            self.modo = management_modos.Modo(nombre)

        self.item_modelo = ItemFantasma(patron_nombrado=self.modo.patron_nombrado)

        self.dict_gpus = None
        self.ids_gpus_elegidos = []
        self.item_usar_tag = None
        self.opciones_frames = None

        self.seleccion_dispositivos = seleccion_dispositivos
        self.ventana = ventana
        self.item_overwrites = None
        self.item_auto_duplicate = None
        self.item_parallel = None
        self.items_dispositivos_elegidos = []
        self.setupUi(self)
        self.arbol.setColumnCount(2)
        # self.arbol.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        self.aceptar_cancelar.accepted.connect(self.acepto)

        self.ventana_dispositivos = None

        self.item_prestablecer = None

        self.item_nombre = ItemLinea(titulo=traducir("Nombre"), texto_base="New Mode", parent=self.arbol)
        self.item_nombre.linea.editingFinished.connect(self.verificar_nombre)
        self.item_background = ItemChk(traducir("Background mode"), parent=self.arbol)
        self.item_background.setFirstColumnSpanned(True)
        self.item_version_blender = ItemSelector(versiones_blender.blenders,
                                                 titulo=traducir("Versión de Blender"), spacerR=True,
                                                 parent=self.arbol)

        elementos_selector_tipo = self.crear_selector_tipo()
        self.item_tipo, self.grupo_tipo, self.botones_tipo = elementos_selector_tipo

        self.item_output = ItemTitulo(traducir("Nombrado de salida"), parent=self.arbol, spanned=True)
        self.grupo_nombrado = self.configurar_grupo_nombrado()

        self.item_dispositivos = ItemTitulo(traducir("Dispositivos de render"), parent=self.arbol)
        self.btn_elegir = QtWidgets.QPushButton(traducir("Elegir"))
        self.item_dispositivos.agregar_wgt(1, self.btn_elegir, spacerR=True)

        self.crear_opciones_mutli_gpu()

        self.item_extra_args, self.campo_extra_args, self.item_pedir_script = self.configurar_extra_args()

        self.grupo_opciones_frames = None
        self.configurar_arbol()

        if self.modo:
            self.leer_previos()
        else:
            self.set_defaults()

        if not nombre_modo:
            self.item_nombre.linea.setFocus()

        self.show()
        # self.arbol.expandAll()

    def verificar_nombre(self, nombre=None):
        if not nombre:
            nombre = self.item_nombre.text()
        if nombre in modos.lista_modos:
            nombre = renombrar_duplicado(nombre, modos.lista_modos)
        return nombre

    def set_defaults(self):
        self.botones_tipo["animacion"].setChecked(True)
        if self.opciones_frames:
            self.opciones_frames["editor"].setText("1")

    def leer_previos(self):
        nombre = self.modo.nombre
        self.item_nombre.setText(modos.traducir(nombre))

        self.item_background.setChecked(self.modo.background)
        self.botones_tipo[self.modo.tipo].setChecked(True)
        self.item_usar_tag.setChecked(self.modo.usar_arg_tipo)

        if self.modo.tipo == "frames" and self.modo.frames_predefinidos:
            self.opciones_frames["editor"].setText(self.modo.frames_predefinidos)
            self.opciones_frames["preestablecer"].setChecked(True)

        if self.item_modelo.patron_nombrado and self.item_modelo.patron_nombrado["ruta"] or \
                self.item_modelo.patron_nombrado["nombre"]:
            self.grupo_nombrado.opcion_custom.setChecked(True)
            self.item_output.setExpanded(True)
            self.grupo_nombrado.muestra_ruta.setText(auto_nombrado.patron_a_string(self.item_modelo.patron_nombrado["ruta"]))
            self.grupo_nombrado.muestra_nombre.setText(auto_nombrado.patron_a_string(self.item_modelo.patron_nombrado["nombre"]))
        else:
            self.grupo_nombrado.opcion_no_cambiar.setChecked(True)

        if self.item_version_blender.selector.findText(self.modo.version_blender):
            self.item_version_blender.selector.setCurrentText(self.modo.version_blender)

        self.item_parallel.setChecked(self.modo.parallel_gpu)
        self.item_auto_duplicate.setChecked(self.modo.auto_duplicar)
        self.item_overwrites.setChecked(self.modo.overwrite_placeholders)
        if self.modo.dispositivos:
            if self.modo.dispositivos["tipo"] == "ask":
                self.elegir_dispositivos()
            else:
                self.dict_gpus = self.modo.dispositivos
                self.rellenar_dispositivos()

        self.item_pedir_script.setChecked(self.modo.pedir_script)

        if self.modo.args_extra:
            self.campo_extra_args.setPlainText(self.modo.args_extra)

    def configurar_arbol(self):
        self.arbol.setColumnWidth(0, 125)
        self.arbol.headerItem().setText(0, "")
        self.arbol.headerItem().setText(1, "")
        self.arbol.header().setFixedHeight(10)
        self.arbol.setItemDelegate(util_ui.ItemDelegate(height=35))
        self.arbol.setTransparente()


    def configurar_extra_args(self):
        item = ItemTitulo(texto=traducir("Argumentos extra"), parent=self.arbol)
        item.setFirstColumnSpanned(True)
        layout = QtWidgets.QVBoxLayout()
        lay_pb = QtWidgets.QHBoxLayout()
        btn_extra_args = QtWidgets.QPushButton(traducir("Establecer"))
        btn_extra_args.clicked.connect(self.set_extra_args)
        campo_extra_args = QtWidgets.QPlainTextEdit()
        spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding)
        lay_pb.addSpacerItem(spacer)
        lay_pb.addWidget(btn_extra_args)
        lay_pb.addSpacerItem(spacer)
        layout.addItem(lay_pb)
        layout.addWidget(campo_extra_args)
        layout.setSpacing(5)
        layout.setContentsMargins(5,4,5,4)
        subitem_extra_args = ItemWidgetBasico(parent=item, spanned=True)
        subitem_extra_args.agregar_layout_wgt(layout, columna=0)
        item_pedir_script = ItemChk(traducir("script_ask"), 0, item)
        item_pedir_script.setFirstColumnSpanned(True)
        item_pedir_script.chk.setToolTip(traducir("tooltip_script_ask"))

        return item, campo_extra_args, item_pedir_script

    def configurar_grupo_nombrado(self):

        grupo_nombrado = WidgetNombrado(self, self.item_modelo)
        # grupo_nombrado.grupo_nombrado.setTitle("")
        subitem_output = ItemWidgetBasico(self.item_output)
        subitem_output.crear_wgt(grupo_nombrado, 0, spacerR=True)
        subitem_output.setFirstColumnSpanned(True)
        grupo_nombrado.rellenar_presets("watchfolders")
        grupo_nombrado.arbol.setTransparente()
        return grupo_nombrado

    def crear_opciones_frames(self):
        self.grupo_opciones_frames = QtWidgets.QButtonGroup()
        self.item_prestablecer = ItemLinea(texto_base="1", parent=self.item_tipo)
        opcion_preestablecer = QtWidgets.QRadioButton(traducir("frames_predef"))
        self.item_prestablecer.agregar_wgt(0, opcion_preestablecer, spacerR=True)

        opcion_preguntar = QtWidgets.QRadioButton(traducir("Always ask"))
        item_preguntar = ItemWidgetBasico(self.item_tipo)
        item_preguntar.agregar_wgt(0, opcion_preguntar)

        self.item_prestablecer.linea.textChanged.connect(self.establecio_frames)

        self.opciones_frames = {"preestablecer": opcion_preestablecer, "preguntar": opcion_preguntar,
                                "editor": self.item_prestablecer}
        self.grupo_opciones_frames.addButton(opcion_preestablecer)
        self.grupo_opciones_frames.addButton(opcion_preguntar)
        self.item_tipo.setExpanded(True)
        opcion_preguntar.setChecked(True)

        self.item_usar_tag.chk.toggled.connect(self.togleo_arg_tipo)

    def togleo_arg_tipo(self, usa_arg):
        # self.opciones_frames["animacion"]
        for opcion in self.opciones_frames:
            if opcion == "editor":
                continue
            self.opciones_frames[opcion].setEnabled(usa_arg)

    def acepto(self):

        nombre_nuevo = self.item_nombre.text()
        if not self.nuevo:  # si está editando un modo previo

            nombre_viejo = self.modo.nombre
            nombre_viejo_traducido = modos.traducir(nombre_viejo)
            if nombre_viejo_traducido != nombre_nuevo:
                del modos.modo[nombre_viejo]
                self.modo.nombre = nombre_nuevo
                modos.modo["actual"] = nombre_nuevo
        else:
            self.modo.nombre = nombre_nuevo
            modos.modo["actual"] = nombre_nuevo

        modos.modo.update({self.modo.nombre: self.modo})

        self.modo.background = self.item_background.isChecked()
        self.modo.tipo = self.grupo_tipo.checkedButton().objectName()
        if self.modo.tipo == "frames":
            frames_predefinidos = self.opciones_frames["editor"].text() if self.opciones_frames[
                "preestablecer"].isChecked() else ""
            self.modo.frames_predefinidos = frames_predefinidos
        self.modo.usar_arg_tipo = self.item_usar_tag.isChecked()
        self.modo.dispositivos = self.dict_gpus
        self.modo.version_blender = self.item_version_blender.text()
        self.modo.motor_dispositivos = self.motor
        self.modo.parallel_gpu = self.item_parallel.isChecked()
        self.modo.auto_duplicar = self.item_auto_duplicate.isChecked()
        self.modo.overwrite_placeholders = self.item_overwrites.isChecked()
        if self.grupo_nombrado.opcion_usar_preset.isChecked():
            self.modo.patron_nombrado = self.grupo_nombrado.selector_preset.currentData().patron

        elif self.grupo_nombrado.opcion_custom.isChecked() and any(self.item_modelo.patron_nombrado):
            self.modo.patron_nombrado = self.item_modelo.patron_nombrado
        else:
            self.modo.patron_nombrado = ItemCola.default_patron_nombrado
        self.modo.args_extra = self.campo_extra_args.toPlainText()
        self.modo.pedir_script = self.item_pedir_script.isChecked()

        if self.seleccion_dispositivos:
            modo = modos.modo[nombre_nuevo]
            if modo.dispositivos and modo.dispositivos["tipo"] != "ask":
                modos.set_actual(nombre_nuevo)

        modos.guardar_modos()
        self.ventana.actualizar_post_edicion_modo()


    def crear_selector_tipo(self):
        grupo = QtWidgets.QButtonGroup()
        grupo.buttonToggled.connect(self.cambio_tipo)
        btn_anim = QtWidgets.QPushButton(traducir("Animación"))
        btn_anim.setObjectName("animacion")
        btn_frames = QtWidgets.QPushButton(traducir("Frames"))
        btn_frames.setObjectName("frames")
        item = ItemTitulo(traducir("Tipo"), parent=self.arbol)

        for btn in [btn_anim, btn_frames]:
            btn.setCheckable(True)
            grupo.addButton(btn)
            item.agregar_wgt(1, btn, spacerR=btn == btn_frames)

        botones_tipo = {"animacion": btn_anim, "frames": btn_frames, }
        return item, grupo, botones_tipo

    def cambio_tipo(self):
        self.item_tipo.takeChildren()
        tipo_elegido = self.grupo_tipo.checkedButton().objectName()
        letra_arg = tipo_elegido.strip("modo_")[0]
        self.item_usar_tag = ItemChk(traducir("Usar argumento") + " (-{})".format(letra_arg), 0,
                                     self.item_tipo)
        self.item_usar_tag.setFirstColumnSpanned(True)
        self.item_usar_tag.setChecked(True)

        if self.botones_tipo["frames"].isChecked():
            self.crear_opciones_frames()

    def establecio_frames(self):
        self.opciones_frames["preestablecer"].setChecked(True)

    def crear_opciones_mutli_gpu(self):

        self.item_parallel = ItemChk(traducir("parallel_gpu"), parent=self.item_dispositivos)
        self.item_parallel.setToolTip(0, traducir("tooltip_parallel_gpu"))
        self.item_parallel.setFirstColumnSpanned(True)
        self.item_auto_duplicate = ItemChk(traducir("Auto duplicate jobs"), columna=1,
                                           parent=self.item_parallel)
        self.item_auto_duplicate.setToolTip(1, traducir("tooltip_auto_duplicate"))
        self.item_overwrites = ItemChk("Overwrite Off - Placeholders On", columna=1, parent=self.item_parallel)
        self.item_overwrites.setToolTip(1, traducir("tooltip_overwrites"))

        self.item_parallel.chk.toggled.connect(self.toglear_sub_parallel)
        self.toglear_sub_parallel(False)
        self.item_parallel.chk.setDisabled(True)

        self.btn_elegir.clicked.connect(self.elegir_dispositivos)

    def toglear_sub_parallel(self, toggle):
        parent_enabled = self.item_parallel.chk.isEnabled()
        for i in range(self.item_parallel.childCount()):
            self.item_parallel.child(i).chk.setDisabled(parent_enabled and not toggle)

    def set_extra_args(self):
        self.ventana_extra_args = VentanaArgsExtra(self.ventana, auxiliar_modos=True)
        self.ventana_extra_args.botones_generales.accepted.disconnect(self.ventana_extra_args.aceptar)
        self.ventana_extra_args.botones_generales.accepted.connect(self.actualizar_extra_args)
        self.ventana_extra_args.exec_()

    def actualizar_extra_args(self):
        self.campo_extra_args.setPlainText(self.ventana_extra_args.campo_args.toPlainText())
        self.ventana_extra_args.close()
        self.item_extra_args.setExpanded(True)

    def elegir_dispositivos(self):
        elegidos = [gpu_id for nombre, gpu_id in self.dict_gpus.items() if nombre != "tipo"] if self.dict_gpus else None
        tipo = self.dict_gpus["tipo"] if self.dict_gpus else None
        self.ventana_dispositivos = VentanaDispositivos(None, elegidos, tipo)
        self.ventana_dispositivos.chk_parallel.setChecked(self.item_parallel.isChecked())
        self.ventana_dispositivos.aceptar_cancelar.accepted.disconnect(self.ventana_dispositivos.aceptar)
        self.ventana_dispositivos.aceptar_cancelar.accepted.connect(self.actualizar_dispositivos)
        self.ventana_dispositivos.exec_()

    def actualizar_toggles_dispositivos(self):
        self.item_parallel.chk.setDisabled(not self.dict_gpus)

    def actualizar_dispositivos(self):
        self.item_dispositivos.setExpanded(True)
        for item in self.items_dispositivos_elegidos:
            self.item_dispositivos.removeChild(item)
        self.items_dispositivos_elegidos = []

        self.item_parallel.chk.setChecked(self.ventana_dispositivos.chk_parallel.isChecked())

        respetar = self.ventana_dispositivos.opcion_respetar.isChecked()
        self.item_parallel.chk.setDisabled(respetar)

        if respetar:
            self.dict_gpus = {}
            tipo_elegido = "respetar"

        elif self.ventana_dispositivos.opcion_cycles.isChecked():
            tipo_elegido = self.ventana_dispositivos.tipo_elegido_actual()
            if tipo_elegido == "CPU":
                self.dict_gpus = {"CPU": "CPU"}
            else:
                self.dict_gpus = {disp.nombre: disp.id for disp in
                                  self.ventana_dispositivos.gpuitems_tipos[tipo_elegido]["items_dispositivos"]
                                  if disp.isUsed()}
        else:
            self.dict_gpus = {item.nombre: item.nombre for item in self.ventana_dispositivos.gpuitems_eevee if
                              item.isUsed()}
            tipo_elegido = "Eevee"

        self.dict_gpus["tipo"] = tipo_elegido
        self.rellenar_dispositivos()
        self.ventana_dispositivos.close()

    def rellenar_dispositivos(self):
        self.actualizar_toggles_dispositivos()
        tipo = self.dict_gpus["tipo"]
        self.motor = "" if tipo == "respetar" else tipo
        nombres = ["({}) {}".format(tipo, nombre) for nombre in self.dict_gpus if nombre != "tipo"]
        for nombre in nombres:
            item_disp_i = ItemTitulo(nombre, 1)
            self.items_dispositivos_elegidos.append(item_disp_i)

        self.item_dispositivos.insertChildren(0, self.items_dispositivos_elegidos)
        for item in self.items_dispositivos_elegidos:
            item.aplicar_wgt(1)


class VisorRenders(QtWidgets.QDialog, ui.visor_renders.Ui_visor_render):
    mensaje_no_encuentra = "Can't find image"
    mensaje_formato = "Unsupported image format"
    def __init__(self, ventana):
        super().__init__()

        self.base_titulo = traducir("Rendered frame")
        self.factor_escala = None

        self.rutas_agrupadas = None
        self.setupUi(self)
        self.ventana = ventana

        self.estado = "detenida"
        self.num_frame = None

        if self.ventana.item_unico_elegido():
            self.item = self.ventana.item_unico_elegido()
        else:
            self.item = self.ventana.tablaPrincipal.currentItem()


        self.items_mirables = []
        for item_i in self.ventana.tablaPrincipal.items():
            if item_i.es_video:
                continue
            self.items_mirables.append(item_i)
            self.selector_blend.addItem(item_i.nombre_blend, userData=item_i)

        self.selector_blend.setCurrentIndex(self.selector_blend.findData(self.item))

        self.leer_datos()

        self.timer = None
        self.input_fps.setValue(configuracion.fps)
        self.conectar_botones_acciones()
        self.definir_atajos()

        # self.selector_base_nombre.addItems(["tata", "cuchu"])
    #         self.selector_base_nombre.setStyleSheet("""
    #     QComboBox::down-arrow {
    #         width: 3px;
    #         height: 8px;
    #         border-right: 1px solid #999;
    #         border-bottom: 1px solid #999;
    #
    #     }
    # """)


    # para cuando no se tienen los dir investigar qdir entryinfolist o sarasa a manoplinga comabiaplaniao

    def conectar_botones_acciones(self):
        self.btn_cerrar.clicked.connect(self.guardar_fps)
        self.btn_cerrar.clicked.connect(self.close)
        self.btn_anterior_frame.clicked.connect(self.anterior_frame)
        self.btn_siguiente_frame.clicked.connect(self.siguiente_frame)
        self.btn_animacion.clicked.connect(self.reproducir_secuencia)
        self.chk_loop.toggled.connect(self.loop)
        self.selector_blend.currentIndexChanged.connect(self.cambio_blend)
        self.selector_base_nombre.currentIndexChanged.connect(self.seleccion_imagen)


    def definir_atajos(self):
        atajo_salir = atajos_y_contextuales.CrearAtajos.particular(self, "Esc", self.close)
        atajo_blend_anterior = atajos_y_contextuales.CrearAtajos.particular(self, "Ctrl+Left", self.anterior_blend)
        atajo_blend_siguiente = atajos_y_contextuales.CrearAtajos.particular(self, "Ctrl+Right", self.siguiente_blend)
        atajo_frame_anterior = atajos_y_contextuales.CrearAtajos.particular(self, "Left", self.anterior_frame)
        atajo_frame_siguiente = atajos_y_contextuales.CrearAtajos.particular(self, "Right", self.siguiente_frame)
        atajo_play = atajos_y_contextuales.CrearAtajos.particular(self, "Space", self.btn_animacion.click)

    def guardar_fps(self):
        configuracion.fps = self.input_fps.value()

    def resizeEvent(self, a0: QtGui.QResizeEvent):
        self.mostrar_imagen()
        self.actuailzar_info_nivel_zoom()
        a0.accept()
    #
    # def mouseDoubleClickEvent(self, event):
    #     self.mostrar_imagen_al_100()
    #     #
    #     # if event.pos().y() <= self.style().pixelMetric(self.style().PM_TitleBarHeight):
    #     #     self.on_header_double_click()
    #     # else:
    #     #     super().mouseDoubleClickEvent(event)


    def leer_datos(self):
        self.selector_base_nombre.blockSignals(True)
        # self.nombre_blend.setText(self.item.nombre_blend)
        self.num_frame = None # para cuando cambia de blend

        rutas = self.item.consola.extraer_rutas()
        self.rutas_agrupadas = defaultdict(lambda: {'numeros_frame': []})

        for ruta in rutas:
            carpeta, nombre_base, numeros_frame, extension = self.descomponer_ruta(ruta)
            if nombre_base is not None:
                key = (carpeta, nombre_base, extension)
                self.rutas_agrupadas[key]["numeros_frame"].append(numeros_frame)

        self.selector_base_nombre.clear()
        for (carpeta, nombre, extension) in self.rutas_agrupadas:
            if not carpeta:
                continue
            self.selector_base_nombre.addItem(nombre, userData=(carpeta, extension))

        num_nombres = self.selector_base_nombre.count()
        if num_nombres > 0:
            self.selector_base_nombre.setCurrentIndex(num_nombres - 1)

        self.seleccion_imagen()
        self.selector_base_nombre.blockSignals(False)

    @staticmethod
    def descomponer_ruta(ruta_completa):
        carpeta, nombre_con_extension = os.path.split(ruta_completa)

        # Regular expression to match filename and split it into basename, trailing integers, and extension
        match = re.match(r"^(.*?)(\d+)(\.\w+)$", nombre_con_extension)

        if match:
            nombre_base = match.group(1)
            numeros_frame = match.group(2)
            extension = match.group(3)
            return carpeta, nombre_base, numeros_frame, extension
        else:
            # Return the original path as the key if no match (which should not happen with provided examples)
            return ruta_completa, None, None

    def ruta_completa_frame_actual(self, mostrar_nombres=True):
        carpeta, nombre_base, extension = self.bases_ruta_activa()
        if not carpeta:
            return None
        secuencia_activa = self.secuencia_activa(carpeta, nombre_base, extension)

        # self.num_frame = max(self.num_frame, 0) # temp para evitar crash
        frames_secuencia = secuencia_activa["numeros_frame"]
        if self.num_frame < len(frames_secuencia):
            numeros = frames_secuencia[self.num_frame]
            parte_final = f"{numeros}{extension}"
            if mostrar_nombres:
                self.nombre_imagen.setText(parte_final)
            nombre_completo = f"{nombre_base}{parte_final}"
            ruta_completa = os.path.join(carpeta, nombre_completo)
            return ruta_completa
        return None

    def bases_ruta_activa(self):
        if not self.selector_base_nombre.count():
            return None, None, None
        carpeta, extension = self.selector_base_nombre.currentData(Qt.UserRole)
        nombre_base = self.selector_base_nombre.currentText()
        return carpeta, nombre_base, extension

    def secuencia_activa(self, carpeta=None, nombre_base=None, extension=None):
        if not (carpeta and nombre_base and extension):
            carpeta, nombre_base, extension = self.bases_ruta_activa()
        return self.rutas_agrupadas[(carpeta, nombre_base, extension)]

    def num_frames_secuencia_activa(self):
        return len(self.secuencia_activa()["numeros_frame"])

    def cambio_blend(self):
        self.item = self.selector_blend.currentData(Qt.UserRole)
        self.leer_datos()

    def anterior_blend(self, item=None):
        item = item if item else self.item
        anterior = self.ventana.tablaPrincipal.itemAbove(item)
        if not anterior:
            return
        if anterior not in self.items_mirables:
            self.anterior_blend(anterior)
            return
        self.selector_blend.setCurrentIndex(self.selector_blend.findData(anterior, Qt.UserRole))

    def siguiente_blend(self, item=None):
        item = item if item else self.item
        siguiente = self.ventana.tablaPrincipal.itemBelow(item)
        if not siguiente:
            return
        if siguiente not in self.items_mirables:
            self.siguiente_blend(siguiente)
            return
        self.selector_blend.setCurrentIndex(self.selector_blend.findData(siguiente, Qt.UserRole))

    def loop(self):
        self.btn_animacion.setCheckable(self.chk_loop.isChecked())

    def anterior_frame(self):
        if self.num_frame < 1:
            return
        self.num_frame -= 1
        self.mostrar_imagen()

    def siguiente_frame(self):
        if self.num_frame == self.num_frames_secuencia_activa() - 1:
            return False
        self.num_frame += 1
        self.mostrar_imagen()
        return True

    def seleccion_imagen(self):
        if not self.selector_base_nombre.count():
            self.sin_imagen(self.mensaje_no_encuentra)
            return
        if self.num_frame is None:
            self.num_frame = self.num_frames_secuencia_activa() - 1

        self.mostrar_imagen()
        self.actuailzar_info_nivel_zoom()

    def mostrar_imagen(self):
        ruta_completa = self.ruta_completa_frame_actual()
        imagen = None
        if not ruta_completa or not os.path.isfile(ruta_completa):
            self.sin_imagen(self.mensaje_no_encuentra)
            return

        if not QtGui.QImageReader(ruta_completa).format(): # si el formato no es sorortado
            if not ruta_completa.endswith(".exr") :
                self.sin_imagen(self.mensaje_formato)
                return
            imagen = self.exr_to_qpixmap(ruta_completa)
            if not imagen:
                return

        imagen = imagen if imagen else QtGui.QPixmap(ruta_completa)
        imagen_scaled = imagen.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.porta_imagen.setPixmap(imagen_scaled)
        self.factor_escala = imagen_scaled.width() / imagen.width()

    def sin_imagen(self, mensaje):
        self.porta_imagen.setPixmap(QtGui.QPixmap())
        self.porta_imagen.setText(traducir(mensaje))
        self.porta_imagen.setAlignment(Qt.AlignCenter)

    @staticmethod
    def exr_to_qpixmap(exr_path):
        file = OpenEXR.InputFile(exr_path)
        dw = file.header()['dataWindow']
        size = (dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1)

        # Check available channels in the EXR file
        available_channels = file.header()['channels'].keys()
        print("Available channels:", available_channels)

        FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)

        def get_channel(channel_name):
            """Returns the data for the specified channel or a channel whose name ends with 'Combined.<channel_name>'."""
            if channel_name in available_channels:
                return file.channel(channel_name, FLOAT)
            # Check if any channel name ends with 'Combined.<channel_name>'
            for ch in available_channels:
                if ch.endswith(f"Combined.{channel_name}"):
                    return file.channel(ch, FLOAT)
            # If neither the exact channel nor a 'Combined' variant exists, return None
            return None

        # Fetch each color channel
        red = get_channel('R')
        green = get_channel('G')
        blue = get_channel('B')

        # If any channel is missing, return None or handle the error
        if red is None or green is None or blue is None:
            print(f"Missing channels: R: {red is None}, G: {green is None}, B: {blue is None}")
            return None

        # Convert to a numpy array
        img_array = np.zeros((size[1], size[0], 3), dtype=np.float32)
        img_array[..., 0] = np.frombuffer(red, dtype=np.float32).reshape(size[1], size[0])
        img_array[..., 1] = np.frombuffer(green, dtype=np.float32).reshape(size[1], size[0])
        img_array[..., 2] = np.frombuffer(blue, dtype=np.float32).reshape(size[1], size[0])

        # Convert to 8-bit image
        img_array = np.clip(img_array, 0, 1) * 255
        img_array = img_array.astype(np.uint8)

        # Convert to QImage
        qimage = QtGui.QImage(img_array.data, size[0], size[1], size[0] * 3, QtGui.QImage.Format_RGB888)
        qpixmap = QtGui.QPixmap.fromImage(qimage)

        return qpixmap

    # def crear_imagen_actual(self):
    #     ruta_completa = self.ruta_completa_frame_actual()
    #     if not ruta_completa:
    #         return
    #     imagen = QtGui.QPixmap(ruta_completa)
    #     return imagen

    # def mostrar_imagen_al_100(self): # ta por separado para no agregar ifs en el otro que se usa enreproduccion de animación
    #     imagen = self.crear_imagen_actual()
    #     self.porta_imagen.setPixmap(imagen)
    #     self.adjustSize()

    def reproducir_secuencia(self):
        if self.estado == "reproduciendo":
            self.estado = "detenida"
            self.btn_animacion.setText(traducir("Reproducir"))
            return
        else:
            self.estado = "reproduciendo"
            self.btn_animacion.setText(traducir("Detener"))
        self.num_frame = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualiza_secuencia)
        self.timer.start(1000 // self.input_fps.value())

    def actualiza_secuencia(self):
        if self.estado == "detenida":
            self.timer.stop()
            return
        if not self.siguiente_frame():
            if self.btn_animacion.isChecked():
                self.num_frame = 0
            else:
                self.timer.stop()
                self.estado = "detenida"
                self.btn_animacion.setText(traducir("Reproducir"))

    def actuailzar_info_nivel_zoom(self):
        titulo = self.base_titulo
        if self.factor_escala:
            titulo += " - " + str(int(self.factor_escala*100)) + "%"
        self.setWindowTitle(titulo)

    def retranslateUi(self, _):
        self.setWindowTitle(self.base_titulo)
        self.porta_imagen.setText(traducir(""))
        self.lbl_blend.setText(traducir("Blend:"))
        self.lbl_archivo_imagen.setText(traducir("Image name:"))
        self.nombre_imagen.setText(traducir(""))
        self.btn_anterior_frame.setText(traducir("<"))
        self.btn_siguiente_frame.setText(traducir(">"))
        self.btn_animacion.setText(traducir("Reproducir"))
        self.btn_cerrar.setText(traducir("Cerrar"))
        self.chk_loop.setText(traducir("Loop"))
        self.lbl_fps.setText((traducir("Frame rate") + ": "))
        self.btn_anterior_frame.setToolTip(traducir("Anterior frame") + "\nArrow Left")
        self.btn_siguiente_frame.setToolTip(traducir("Siguiente frame") + "\nArrow Right")
        self.selector_blend.setToolTip(
            traducir("Show render from another job") + "\nCtrl+Arrow Left / Ctrl+Arrow Right")


class VentanaAcercaDe(QtWidgets.QDialog, ui.ventana_info.Ui_ventana_acerca_de):
    def __init__(self, ventana):
        super().__init__()
        self.setupUi(self)
        self.ventana = ventana
        self.atajos = self.ventana.atajos
        self.icono_info = QtGui.QIcon()
        self.icono_info.addPixmap(QtGui.QPixmap(":/iconos/ico_info.png"), QtGui.QIcon.Normal,
                                  QtGui.QIcon.Off)
        self.setWindowIcon(self.icono_info)
        self.acerca_de_notice.setOpenExternalLinks(True)
        self.acerca_de_email.setOpenExternalLinks(True)
        self.acerca_de_bajada.setText(traducir("Render manager para blender"))
        self.lbl_version.setText(traducir("Versión") + " " + str(InfoRenderon.version))
        self.setWindowTitle(traducir("Info") + " " + InfoRenderon.nombre)

        self.tabla_atajos.setColumnWidth(0, 350)
        self.tabla_atajos.headerItem().setText(0, "      " + traducir("Comando"))
        self.tabla_atajos.headerItem().setText(1, "      " + traducir("Atajo"))

        separador0 = QTreeWidgetItem(["\t" + traducir("General")])
        # separador1.setTextAlignment(0, QtCore.Qt.AlignCenter)
        separador0.setDisabled(True)
        self.tabla_atajos.addTopLevelItem(separador0)
        separador0.setFirstColumnSpanned(True)
        self.popular_atajos()

    def popular_atajos(self):
        # primero los que no estan en contextuales. Algunos definir a mano y luego loopear por los que estan
        # definidos de a roletes en atajos y contextuales
        for operador in self.atajos.operadores:
            if operador.descripcion:
                item_i = QTreeWidgetItem(
                    [traducir(operador.descripcion), operador.atajos[0]])
                self.tabla_atajos.addTopLevelItem(item_i)

        self.extraer_atajos_contextual(self.ventana.contextual_general)
        separador1 = QTreeWidgetItem(["\t" + traducir("Para blends seleccionados")])
        # separador1.setTextAlignment(0, QtCore.Qt.AlignCenter)
        separador1.setDisabled(True)
        self.tabla_atajos.addTopLevelItem(separador1)
        separador1.setFirstColumnSpanned(True)
        self.extraer_atajos_contextual(self.ventana.contextual_elegidos)

    def extraer_atajos_contextual(self, contextual):
        for grupo in contextual.grupos_contextuales:
            for nombre_operador in grupo.operadores:
                operador = contextual.operadores[nombre_operador]
                if not operador.atajos:
                    continue
                if grupo.nombre_visible:
                    nombre = traducir(grupo.nombre_visible) + " --> "
                else:
                    nombre = ''
                nombre += traducir(operador.nombre_visible)
                atajos = ", ".join(operador.atajos)
                if nombre_operador == "agregar_con_escenas":
                    atajos += ", Ctrl + " + traducir("soltar blends en cola")
                item_i = QTreeWidgetItem([nombre, atajos])
                self.tabla_atajos.addTopLevelItem(item_i)


class VentanaInfo(QtWidgets.QWidget):

    def __init__(self, ventana, index=None):
        super().__init__()
        self.resize(800, 800)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.info = QtWidgets.QPlainTextEdit(self)
        self.info.setReadOnly(True)
        self.layout.addWidget(self.info)
        self.ventana = ventana
        self.setWindowIcon(iconos.icono_log)
        self.index = index
        atajo_cerrar = QtWidgets.QShortcut(QtGui.QKeySequence('Esc'), self)
        atajo_cerrar.activated.connect(self.close)
        atajo_cerrar_todos = QtWidgets.QShortcut(QtGui.QKeySequence('Alt+L'), self)
        atajo_cerrar_todos.activated.connect(self.ventana.cerrar_text_logs)

        if index is not None:
            self.adjustSize()

    def closeEvent(self, event):
        if self.index is None:
            return
        for ventana in self.ventana.ventana_log_individual[self.index + 1:]:
            ventana.index -= 1
        self.ventana.ventana_log_individual.pop(self.index)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.WindowStateChange and self.isMinimized():
            self.close()

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.close()





class DialogoReubicar(QtWidgets.QDialog, ui.dialogo_reubicar.Ui_ventana_reubicar):
    def __init__(self, item):
        super().__init__()
        self.setupUi(self)
        path_viejo = item.ruta_blend_completa
        self.path_viejo.setText(path_viejo)
        self.path_nuevo.setText(path_viejo)
        self.aceptar_cancelar.accepted.disconnect()
        self.aceptar_cancelar.accepted.connect(self.aceptar)
        self.aceptar_cancelar.rejected.connect(self.reject)
        self.btn_explorar.clicked.connect(self.explorar)
        self.item = item

    def aceptar(self):
        path_nuevo = self.path_nuevo.text()
        if not os.path.isfile(path_nuevo):
            self.path_nuevo.selectAll()
            return
        ruta, nombre = os.path.split(self.path_nuevo.text())
        if not (ruta and nombre):
            return
        self.item.ruta_blend = ruta
        self.item.nombre_blend = nombre
        self.item.desactivado = False
        # if "nombrado" in self.item.propiedades_argumentar:
        #     auto_nombrado.aplicar(self.item)
        self.accept()

    def explorar(self):
        filtro = "BLEND (*.blend)"
        archivo, _ = QFileDialog.getOpenFileUrl(self, filter=filtro)
        if archivo:
            self.path_nuevo.setText(archivo.toLocalFile())

    def retranslateUi(self, ventana_reubicar):
        self.lbl_nuevo.setText(traducir("New") + ":")
        self.lbl_anterior.setText(traducir("Old") + ":")
        self.setWindowTitle(traducir("Relocate blend(s)"))
        self.btn_explorar.setText(traducir("Explorar"))








# class UtilidadesTiempo:
#     formato_fecha = "%Y-%m-%d %H:%M:%S"
#     formato_sanitizado = "%Y-%m-%d_%H-%M-%S"
#     formato_hora = "%H:%M:%S"
#
#     @staticmethod
#     def delta_formateado(hora_inicio, hora_fin):
#
#         if not hora_inicio:
#             return ""
#         if not hora_fin:
#             hora_fin = datetime.now()
#         delta = hora_fin - hora_inicio
#
#         return UtilidadesTiempo.formateado(delta)
#
#     @staticmethod
#     def formateado(tiempo):
#         horas, resto = divmod(tiempo.total_seconds(), 3600)
#         minutos, segundos = divmod(resto, 60)
#         horas = int(horas)
#         minutos = int(minutos)
#         segundos = int(
#             segundos)  # no uso round para no tener la situación de que de 60 segundos, si total qué importan las decimas
#         formateado = ""
#         if horas:
#             formateado += str(horas) + " hrs "
#             formateado += f'{minutos:02d} min '
#         elif minutos:  # si no hay horas a los minutos los ponemos como vengan, 0 min, 11 min, lo que sea
#             formateado += str(minutos) + " min "
#         formateado += f'{segundos:02d} sec'
#
#         return formateado
#
#     @staticmethod
#     def fecha_y_hora(formato=None):
#         if formato is None:
#             formato = UtilidadesTiempo.formato_fecha
#         fecha = datetime.now()
#         fecha = fecha.strftime(formato)
#         return fecha
#
#     @staticmethodclass UtilidadesTiempo:
#     formato_fecha = "%Y-%m-%d %H:%M:%S"
#     formato_sanitizado = "%Y-%m-%d_%H-%M-%S"
#     formato_hora = "%H:%M:%S"
#
#     @staticmethod
#     def delta_formateado(hora_inicio, hora_fin):
#
#         if not hora_inicio:
#             return ""
#         if not hora_fin:
#             hora_fin = datetime.now()
#         delta = hora_fin - hora_inicio
#
#         return UtilidadesTiempo.formateado(delta)
#
#     @staticmethod
#     def formateado(tiempo):
#         horas, resto = divmod(tiempo.total_seconds(), 3600)
#         minutos, segundos = divmod(resto, 60)
#         horas = int(horas)
#         minutos = int(minutos)
#         segundos = int(
#             segundos)  # no uso round para no tener la situación de que de 60 segundos, si total qué importan las decimas
#         formateado = ""
#         if horas:
#             formateado += str(horas) + " hrs "
#             formateado += f'{minutos:02d} min '
#         elif minutos:  # si no hay horas a los minutos los ponemos como vengan, 0 min, 11 min, lo que sea
#             formateado += str(minutos) + " min "
#         formateado += f'{segundos:02d} sec'
#
#         return formateado
#
#     @staticmethod
#     def fecha_y_hora(formato=None):
#         if formato is None:
#             formato = UtilidadesTiempo.formato_fecha
#         fecha = datetime.now()
#         fecha = fecha.strftime(formato)
#         return fecha
#
#     @staticmethod
#     def fecha_hora_sanitizados():
#         return UtilidadesTiempo.fecha_y_hora(UtilidadesTiempo.formato_sanitizado)
#
#     @staticmethod
#     def hora():
#         return UtilidadesTiempo.fecha_y_hora(UtilidadesTiempo.formato_hora)
#
#     @staticmethod
#     def recomposicion_partes_tiempo(tiempo_total_segundos, centesimas=True):
#         tiempo_horas = int(tiempo_total_segundos // 3600)
#         tiempo_sin_horas = tiempo_total_segundos % 3600
#         tiempo_minutos = int(tiempo_sin_horas // 60)
#         tiempo_segundos = tiempo_sin_horas % 60
#         tiempo_final = ""
#         if tiempo_horas:
#             tiempo_final = str(tiempo_horas) + "hr "
#         if tiempo_minutos:
#             tiempo_final += str(tiempo_minutos) + "m "
#
#         redondeo_segundos = 2 if centesimas else None
#         tiempo_final += str(round(tiempo_segundos, redondeo_segundos)) + "s "
#         return tiempo_final
#     def fecha_hora_sanitizados():
#         return UtilidadesTiempo.fecha_y_hora(UtilidadesTiempo.formato_sanitizado)
#
#     @staticmethod
#     def hora():
#         return UtilidadesTiempo.fecha_y_hora(UtilidadesTiempo.formato_hora)
#
#     @staticmethod
#     def recomposicion_partes_tiempo(tiempo_total_segundos, centesimas=True):
#         tiempo_horas = int(tiempo_total_segundos // 3600)
#         tiempo_sin_horas = tiempo_total_segundos % 3600
#         tiempo_minutos = int(tiempo_sin_horas // 60)
#         tiempo_segundos = tiempo_sin_horas % 60
#         tiempo_final = ""
#         if tiempo_horas:
#             tiempo_final = str(tiempo_horas) + "hr "
#         if tiempo_minutos:
#             tiempo_final += str(tiempo_minutos) + "m "
#
#         redondeo_segundos = 2 if centesimas else None
#         tiempo_final += str(round(tiempo_segundos, redondeo_segundos)) + "s "
#         return tiempo_final


class WatchFolder:
    def __init__(self, ruta):
        self.blends_previos = None
        self.blends_nuevos = None
        self._ruta = ruta

    @property
    def ruta(self):
        return self._ruta

    @ruta.setter  # si cambias la ruta se olvidan los blends previos y nuevos si los había. También se usa para setearlos inicialmente
    def ruta(self, nueva_ruta):
        if self._ruta == nueva_ruta:
            return
        self._ruta = nueva_ruta
        self.blends_nuevos = set()
        self.blends_previos = set()

    def serializable(self):
        serializable = vars(self).copy()
        for nombre_propiedad in serializable:
            if isinstance(serializable[nombre_propiedad], set):
                serializable[nombre_propiedad] = list(serializable[nombre_propiedad])
        return serializable


class TimerParticionado:
    intervalo_particion_timer = 10 * 60000  # en minutos pasa a milisegundos

    def __init__(self, accion_final, tiempo_final_hm=None, tiempo_after=None, accion_updates=None):
        self.tiempo_final = None if tiempo_final_hm is None else self.convertir_horario_a_fecha(tiempo_final_hm)
        self.tiempo_after_segundos = tiempo_after
        self.accion_final = accion_final
        self.accion_updates = accion_updates
        self.delta_anterior = None
        self.frenar = False

    def convertir_horario_a_fecha(self, horario):
        fecha_hora_actual = QDateTime.currentDateTime()
        fecha_hora_final = QDateTime.currentDateTime()
        fecha_hora_final.setTime(horario)

        if fecha_hora_final < fecha_hora_actual:
            fecha_hora_final = fecha_hora_final.addDays(1)

        return fecha_hora_final

    def calcular_final_after_time(self):
        self.tiempo_final = QDateTime.currentDateTime().addSecs(self.tiempo_after_segundos)

    def empezar(self):
        self.timer()

    def timer(self):
        if self.frenar:
            return
        delta_total = QDateTime.currentDateTime().secsTo(self.tiempo_final)
        if self.accion_updates:
            self.accion_updates(delta_total)
        if self.delta_anterior and delta_total > self.delta_anterior:  # si se pasó de largo llama a la acción ipsofacto
            self.llamado_a_la_accion()
            return
        self.delta_anterior = delta_total
        if delta_total > self.intervalo_particion_timer:
            QTimer.singleShot(self.intervalo_particion_timer, self.timer)
            return
        if tipo_build == "debug":
            Debug.loguear_actividad("Timer active")

        QTimer.singleShot(delta_total * 1000, self.llamado_a_la_accion)  # llamado a la accion filtra por si
        # luego del timer se frenó el timer.

    def llamado_a_la_accion(self):
        if self.frenar:
            return
        self.accion_final()


class Schedules:
    opciones_stop = {"esperar_frame": "Esperar se complete el frame",
                     "esperar_blend": "Esperar se complete el blend",
                     "detener_ipsofacto": "Detener de inmediato"}
    pares = {"atstart": {"at_horas_start", "at_minutos_start"}, "instart": {"in_horas_start", "in_minutos_start"},
             "atend": {"at_horas_end", "at_minutos_end"}, "afterend": {"after_horas_end", "after_minutos_end"}}
    exportables = {"activado", "usar_start", "at_horas_start",
                   "at_minutos_start", "usar_end", "at_horas_end", "at_minutos_end",
                   "after_horas_end",
                   "after_minutos_end",
                   "tipo_end",
                   "opcion_stop"}

    def __init__(self):
        self.ventana_scheduler = None
        self.activado = False
        self.usar_start = False
        self.at_horas_start = 0
        self.at_minutos_start = 0
        self.usar_end = False
        self.at_horas_end = 0
        self.at_minutos_end = 0
        self.after_horas_end = 0
        self.after_minutos_end = 0
        self.tipo_end = "at"
        self.opcion_stop = "esperar_frame"
        self.acciones_detener = {"esperar_frame": cola.cortar_tras_frame_schedule,
                                 "esperar_blend": cola.marcar_tope_schedule, "detener_ipsofacto": cola.detener_cola}

        self.timer_start = None
        self.timer_stop = None
        self.leer()

    def guardar(self):
        dict_exportable = {}
        for var in self.exportables:
            dict_exportable[var] = getattr(self, var)

        try:
            with open(Datas.ruta_schedules, "w", encoding="utf8") as archivo_schedules:
                archivo_schedules.write(json.dumps(dict_exportable))
        except Exception as e:
            print(e)

    def leer(self):
        try:
            with open(Datas.ruta_schedules, "r", encoding="utf8") as archivo_schedules:
                data_json = json.loads(archivo_schedules.read())
        except Exception as e:
            print(e)
            return
        for nombre_valor in data_json:
            setattr(self, nombre_valor, data_json[nombre_valor])

    def activar(self):
        self.desactivar()
        if self.usar_start:
            cola.checkear_anteriores()

            self.timer_start = TimerParticionado(cola.procesar_sin_preguntar,
                                                 QTime(self.at_horas_start, self.at_minutos_start),
                                                 accion_updates=self.actualizacion_statusbar)
            self.timer_start.empezar()
        if self.usar_end:
            accion = self.acciones_detener[self.opcion_stop]
            if self.tipo_end == "at":
                self.timer_stop = TimerParticionado(accion, QTime(self.at_horas_end, self.at_minutos_end))
                self.timer_stop.empezar()
            elif self.tipo_end == "after":
                self.timer_stop = TimerParticionado(accion, QTime(self.at_horas_end, self.at_minutos_end))
                self.timer_stop.tiempo_after_segundos = self.after_horas_end * 3600 + self.after_minutos_end * 60

    def actualizacion_statusbar(self, tiempo_restante):
        # self.ventana.status_estado.setText(traducir("El render comenzará en") + " " + tiempo_restante)
        print(traducir("El render comenzará en") + " " + str(tiempo_restante))

    def desactivar(self):
        if self.timer_start:
            self.timer_start.frenar = True
        if self.timer_stop:
            self.timer_stop.frenar = True


class Tarea:
    def __init__(self, ruta, args, tokens, item=None):
        self.proceso = QtCore.QProcess()
        self.proceso.setProgram(ruta)
        lista_args = self.parsear_args(args)
        lista_args = self.reemplazar_tokens(lista_args, tokens, item)
        self.proceso.setArguments(lista_args)
        self.proceso.startDetached()

    @staticmethod
    def parsear_args(args):
        args_parseados = []
        for linea in args.splitlines():
            args_parseados.extend(linea.split(" ", 1))
        return args_parseados

    @staticmethod
    def reemplazar_tokens(lista_args, tokens, item=None):
        lista_final = []
        for arg in lista_args:
            for token in tokens:
                if token.patron in arg:
                    if not token.funcion_valor:
                        continue
                    if "item" in signature(token.funcion_valor).parameters:
                        reemplazo = token.funcion_valor(item)
                    else:
                        reemplazo = token.funcion_valor()

                    arg = arg.replace(token.patron, reemplazo)
            lista_final.append(arg)
        return lista_final


class Tareas:
    exportables = ["usar_aj", "ruta_aj", "args_aj", "usar_aq", "ruta_aq", "args_aq"]

    def __init__(self):
        self.token_blend_path = auto_nombrado.TokenNombrado("Blend path", "[BLEND_PATH]",
                                              funcion_valor=lambda item: item.ruta_blend_completa)
        self.token_time = auto_nombrado.TokenNombrado("Time", "[TIME]", funcion_valor=lambda: QTime.currentTime().toString("hh_mm"))
        self.token_queue_name = auto_nombrado.TokenNombrado("Queue name", "[QUEUE_NAME]", funcion_valor=lambda: colas.actual)
        self.job_tokens = [self.token_blend_path, self.token_time]
        self.queue_tokens = [self.token_queue_name, self.token_time]
        self.usar_aj = None
        self.usar_aq = None
        self.ruta_aj = None
        self.args_aj = None
        self.ruta_aq = None
        self.args_aq = None
        self.defaults()

    def defaults(self):
        self.usar_aj = False
        self.usar_aq = False
        self.ruta_aj = ""
        self.args_aj = ""
        self.ruta_aq = ""
        self.args_aq = ""

        # guardamos los args como un texto, el parseo se hace en runtime para aplicar nomás.

    def dict_data(self):
        return {exp: getattr(self, exp) for exp in self.exportables}

    def guardar(self, archivo_cola=""):
        data_json = json.dumps(self.dict_data())
        try:
            with open(colas.ruta_adjunto_cola(archivo_cola, sufijo="Tasks"), "w",
                      encoding="utf8") as archivo_tasks:
                archivo_tasks.write(data_json)
        except:
            pass

    def leer(self):
        try:
            with open(colas.ruta_adjunto_cola(sufijo="Tasks"), "r", encoding="utf8") as data_tareas:
                data_leida = json.loads(data_tareas.read())
                for nombre_dato in data_leida:
                    setattr(self, nombre_dato, data_leida[nombre_dato])
        except Exception as e:
            self.defaults()

    @staticmethod
    def leer_si_existe():
        if os.path.isfile(colas.ruta_adjunto_cola(sufijo="Tasks")):
            tareas = Tareas()
            tareas.leer()
            return tareas
        return None


class WatchFolders:
    def __init__(self):
        self.wf_por_revisar = None
        self.controlador = None
        self.mensaje_controlando = None
        self.controlando = False
        self.activado = None
        self.patron_nombrado = None
        self.args_extra = None
        self.escenas = None
        self.lista = None
        self.intervalo = None
        self.ventana = None
        self.nombre_modo = None
        self.defaults()
        self.inicializado = False

    def defaults(self):
        self.activado = False
        self.patron_nombrado = ItemCola.default_patron_nombrado
        self.args_extra = ""
        self.escenas = "activa"
        self.nombre_modo = ""
        self.lista = set()
        self.intervalo = 10
        self.inicializado = True
        if self.controlador:
            self.controlador.abortar = True

    def activar(self, activar):
        if activar == self.activado:
            return
        self.activado = activar
        if activar:
            self.revisar_todas()

    def vaciar(self):
        self.lista = set()

    def exportables(self):
        return {"activado": self.activado, "patron_nombrado": self.patron_nombrado, "args_extra": self.args_extra,
                "escenas": self.escenas, "nombre_modo": self.nombre_modo, "lista": list(self.lista)}

    def agregar_ruta(self, ruta):
        self.lista.add(WatchFolder(ruta))

    def actualizar_watchfolder(self, watchfolder):
        if watchfolder.ruta:
            self.lista.add(watchfolder)
        else:
            self.lista.discard(watchfolder)

    def revisar_todas(self):
        if tipo_build == "debug":
            Debug.loguear_actividad("Checking watchfolders\n")
        if not self.activado:
            return

        if not self.wf_por_revisar:
            self.wf_por_revisar = self.lista.copy()
            self.loop_revision()

    def loop_revision(self, procesar=False):
        if not self.wf_por_revisar:
            self.guardar()
            if procesar and self.ventana.cola.estado != "renderizando":
                QTimer.singleShot(500, self.ventana.cola.procesar_omitiendo_previos)
            QTimer.singleShot(self.intervalo * 1000, self.revisar_todas)
            return

        self.revisar_watchfolder(self.wf_por_revisar.pop())

    def revisar_watchfolder(self, watchfolder):
        archivos_encontrados = set()
        try:
            for subdir, dirs, archivos in os.walk(watchfolder.ruta):
                for archivo in archivos:
                    if archivo.endswith(".blend"):
                        archivos_encontrados.add(os.path.join(subdir, archivo))
        except IOError:
            self.loop_revision()
            return

        if not archivos_encontrados:
            self.loop_revision()
            return

        data_encontrados = set()
        for nombre in archivos_encontrados:
            tiempo = os.path.getmtime(os.path.join(watchfolder.ruta, nombre))
            data_encontrados.add((nombre, tiempo))

        perdidos = watchfolder.blends_previos - data_encontrados
        watchfolder.blends_previos = watchfolder.blends_previos - perdidos
        nuevos = data_encontrados - watchfolder.blends_previos

        archivos_nuevos = set()
        for nuevo in nuevos:
            archivos_nuevos.add(os.path.join(watchfolder.ruta, nuevo[0]))

        if archivos_nuevos:
            self.controlando_estabilidad(True)
            self.controlador = EstabilidadArchivos(watchfolder, archivos_nuevos, self.agregar_jobs,
                                                   self.controlando_estabilidad)
        else:
            self.controlador = None
            self.loop_revision()

    def agregar_jobs(self, watchfolder, rutas):
        nuevos = {(ruta, os.path.getmtime(ruta)) for ruta in rutas}
        watchfolder.blends_previos.update(nuevos)
        por_agregar = {
            "archivos": rutas,
            "con_escenas": self.escenas,
            "patron_nombrado": self.patron_nombrado,
            "args_extra": self.args_extra,
            "nombre_modo": self.nombre_modo,
            "evitar_repetidos": True
        }
        # for item in self.ventana.tablaPrincipal.items():
        #     if item.ruta_blend_completa in rutas:
        #         print("ruta", item.ruta_blend_completa, "repetiuda") # debug print
        self.ventana.agregar_archivos(**por_agregar)

    def controlando_estabilidad(self, controlando=False):
        self.controlando = controlando
        if controlando:
            self.mensaje_controlando = alertas.alerta_cancelable(titulo="Watchfolders", mensaje="revisando_watchfolders")
            self.mensaje_controlando.buttonClicked.connect(self.abortar)
            self.mensaje_controlando.show()
        else:
            self.mensaje_controlando.close()
            procesar = self.controlador and not self.controlador.abortar
            self.controlador = None
            self.loop_revision(procesar)

    def abortar(self):
        self.controlador.abortar = True
        # self.controlando_estabilidad(False)

    def leer(self):
        try:
            with open(colas.ruta_adjunto_cola(sufijo="Watchfolders"), "r", encoding="utf8") as data_watchfolders:
                data_leida = json.loads(data_watchfolders.read())
                self.activado = data_leida["activado"]
                self.patron_nombrado = data_leida["patron_nombrado"]
                if isinstance(self.patron_nombrado, list):
                    patron_ruta = self.patron_nombrado[0]
                    patron_nombre = self.patron_nombrado[1]
                    self.patron_nombrado = {"aplicar_a": 2, "ruta": patron_ruta, "nombre": patron_nombre,
                                            "ruta_nodos": patron_ruta, "nombre_nodos": patron_nombre}
                self.args_extra = data_leida["args_extra"]
                self.escenas = data_leida["escenas"]
                self.nombre_modo = data_leida["nombre_modo"]
                # estas cosas van aquí para evitar crash en caso que el
                # archivo esté fraguado por alguna razón, como cambio de versión manteniendo un archivo con parámetros
                # que cambiaron
        except Exception as e:
            self.ventana.boton_watchfolder.setChecked(False)
            self.defaults()
            return

        for data_watch in data_leida["lista"]:
            watch_i = WatchFolder(data_watch["_ruta"])
            blends_previos_i = {tuple(bp) for bp in data_watch["blends_previos"]}
            blends_nuevos_i = {tuple(bp) for bp in data_watch["blends_nuevos"]}

            watch_i.blends_previos = blends_previos_i
            watch_i.blends_nuevos = blends_nuevos_i
            self.lista.add(watch_i)

        self.ventana.boton_watchfolder.setChecked(self.activado)
        if self.activado:
            self.revisar_todas()

    def guardar(self, archivo_cola=""):
        if not any(self.lista):
            return
        data_json = json.dumps(self.exportables(), default=self.serializado)
        if not data_json:
            return
        try:
            with open(colas.ruta_adjunto_cola(archivo_cola, sufijo="Watchfolders"), "w",
                      encoding="utf8") as archivo_watchfolders:
                archivo_watchfolders.write(data_json)
        except:
            pass

    def serializado(self, elemento):
        try:
            return elemento.serializable()
        except:
            pass


class EstabilidadArchivos:
    intervalo_verificacion = 2 # para ir agregando cada uno lo antes poosible hago ciclos coortoos y
    # exijo varios ciclos en lugar de ciclos largos
    interervalos_ok = 5

    def __init__(self, watchfolder, rutas_completas, retorno_parcial, fin):
        self.worker = None
        self.watchfolder = watchfolder
        self.por_verificar = {ruta_completa: {"size_previo": os.path.getsize(ruta_completa),
                                              "tiempo_previo": os.path.getmtime(ruta_completa), "ciclos_ok": 0} for
                                              ruta_completa in rutas_completas}
        self.abortar = False
        self.retorno = retorno_parcial
        self.fin = fin

        self.thread_pool = QThreadPool()
        self.iniciar_loop_verificacion()

    def iniciar_loop_verificacion(self):
        self.worker = Worker(self.loop_verificacion)
        self.worker.signals.result.connect(self.handle_result)
        self.worker.signals.finished.connect(self.fin)
        self.thread_pool.start(self.worker)

    def loop_verificacion(self):
        while self.por_verificar and not self.abortar:
            ok_tanda = []
            for ruta_completa, datas in self.por_verificar.items():
                if not os.path.isfile(ruta_completa):
                    continue
                size_nuevo = os.path.getsize(ruta_completa)
                tiempo_nuevo = os.path.getmtime(ruta_completa)
                if size_nuevo == datas["size_previo"] and tiempo_nuevo == datas["tiempo_previo"]:
                    datas["ciclos_ok"] += 1
                else:
                    datas["ciclos_ok"] = 0
                    datas["size_previo"] = size_nuevo
                    datas["tiempo_previo"] = tiempo_nuevo
                if datas["ciclos_ok"] == self.interervalos_ok:
                    ok_tanda.append(ruta_completa)

            for ruta_ok in ok_tanda:
                del self.por_verificar[ruta_ok]

            if ok_tanda:
                self.worker.signals.result.emit((self.watchfolder, ok_tanda))

            time.sleep(self.intervalo_verificacion)


    def handle_result(self, result):
        if result is not None:
            self.retorno(result[0], result[1])
        # if not self.por_verificar:
        #     self.fin()

    def stop(self):
        self.abortar = True


class ConfiguracionVentana:
    columna = {}

    proporciones_ancho_columnas = {
        ColumnaProp.ruta_blend.name: 0.15,
        ColumnaProp.nombre_blend.name: 0.21,
        ColumnaProp.loQue.name: 0.13,
        ColumnaProp.frames_display.name: 0.16,
        ColumnaProp.estado.name: 0.26,
        ColumnaProp.tag_blender.name: 0.13,
        ColumnaProp.escena.name: 0.13,
        ColumnaProp.view_layer.name: 0.1,
        ColumnaProp.camara.name: 0.09,
        ColumnaProp.nombrado.name: 0.23,
        ColumnaProp.args_extra.name: 0.30,
        ColumnaProp.nombres_dispositivos.name: 0.60
    }

    proporciones_columnas_estado = {"estado": 0.5, "frames": 0.25, "eta": 0.25}

    size_default_textos = {"items_tablas": 9, "headers_tablas": 12, "selectores": 8, "statusbar": 8, "supratitulos": 6,
                           "botones": 7, "general": 8}

    alineamientos = {"centro": Qt.AlignmentFlag.AlignCenter, "derecha": Qt.AlignmentFlag.AlignRight,
                     "izquierda": Qt.AlignmentFlag.AlignLeft}

    def __init__(self, ventana):
        self.size_inicial = None
        self.pos_inicial = None
        self.ultimo_path = None
        self.ventana = ventana
        self.tablaPrincipal = ventana.tablaPrincipal
        self.tabla_estados = ventana.tabla_estados
        self.alineamiento_columnas = None
        self.columnas_orden_por_defecto = None
        self.columnas_estado_por_defecto = None
        self.columna_activa = None
        self.expansion_argumentos_extra = {"basicos": True, "presets": True}
        self.tablas = {"principal": self.tablaPrincipal, "estados": self.tabla_estados}
        self.alineamientos_estados_default = ["centro", "centro", "centro"]
        self.alineamientos_estados = self.alineamientos_estados_default.copy()
        self.tabla_estados.header().setStretchLastSection(True)
        self.tablaPrincipal.header().setStretchLastSection(True)
        self.tabla_estados.header().setMinimumSectionSize(15)
        self.propiedades_expuestas = items_cola.propiedades_expuestas
        self.columna = ItemCola.columna

    def set_ventana(self, ventana):
        self.ventana = ventana
        self.tablaPrincipal = ventana.tablaPrincipal

    def nombre_columna(self, col):
        return self.propiedades_expuestas[col]

    def alinear_columna(self, alineamiento_elegido, columna=None, nombre_tabla="principal"):
        tabla = self.tablas[nombre_tabla]
        if columna is None:
            columna = self.columna_activa

        if nombre_tabla == "principal":
            self.actualizar_alineamientos_tp(alineamiento_elegido, columna)
        else:
            self.actualizar_alineamientos_estados(alineamiento_elegido, columna)

        i = 0
        while i < tabla.topLevelItemCount():
            item = tabla.topLevelItem(i)
            item.setTextAlignment(columna,
                                  Qt.AlignmentFlag.AlignVCenter | self.alineamientos[alineamiento_elegido])
            i += 1

    def actualizar_alineamientos_estados(self, elegido, columna):
        self.alineamientos_estados[columna] = elegido

    def actualizar_alineamientos_tp(self, elegido, columna):
        for alineamiento in self.alineamiento_columnas:
            if alineamiento == elegido:
                self.alineamiento_columnas[alineamiento].add(self.nombre_columna(columna))
            else:
                self.alineamiento_columnas[alineamiento].discard(self.nombre_columna(columna))

    def ajustar_columnas(self):
        ancho_tablaprincipal = self.tablaPrincipal.size().width()
        for col in self.columna:
            self.tablaPrincipal.setColumnWidth(self.columna[col],
                                               int(self.proporciones_ancho_columnas[col] * ancho_tablaprincipal))

        ancho_tabla_estados = self.tabla_estados.size().width()
        for indice, columna in ItemEstado.columna.items():
            self.tabla_estados.setColumnWidth(ItemEstado.columna[indice],
                                              int(self.proporciones_columnas_estado[indice] * ancho_tabla_estados))

    def resetear_columnas_tp(self):
        self.tablaPrincipal.header().restoreState(self.columnas_orden_por_defecto)

        alineamiento_default = self.default_alineamiento_columnas()
        if self.alineamiento_columnas != alineamiento_default:
            self.alineamiento_columnas = alineamiento_default
            for col in self.columna:
                for alineamiento, columnas in self.alineamiento_columnas.items():
                    if col in columnas:
                        self.alinear_columna(alineamiento, self.columna[col])

        self.tablaPrincipal.header().update_forzoso()

    def resetear_headers_estado(self):
        self.tabla_estados.header().restoreState(self.columnas_estado_por_defecto)
        for col in ItemEstado.columna.values():
            self.alinear_columna(self.alineamientos_estados_default[col], col, "estados")

        self.tablaPrincipal.header().update_forzoso()



    def leer(self):
        configuracion_ventana = QtCore.QSettings(Datas.ruta_configuraciones_ventana, QtCore.QSettings.IniFormat)
        orden_columnas = configuracion_ventana.value("orden_columnas")
        orden_columnas_estado = configuracion_ventana.value("orden_columnas_estado")
        state_ventana = configuracion_ventana.value("state_ventana")
        dimensiones = configuracion_ventana.value("dimensiones")
        posicion = configuracion_ventana.value("posicion")
        splitter_tabla_estado = configuracion_ventana.value("splitter_tabla_estado")
        expansion_argumentos_extra = configuracion_ventana.value("expansion_argumentos_extra")
        if expansion_argumentos_extra:
            self.expansion_argumentos_extra = expansion_argumentos_extra

        self.ultimo_path = configuracion_ventana.value("ultimo_path")

        if splitter_tabla_estado:
            self.ventana.splitter.restoreState(splitter_tabla_estado)

        if state_ventana:
            self.ventana.restoreState(state_ventana)

        if dimensiones:
            dimensiones = [int(i) for i in dimensiones]
            dimensiones = QtCore.QSize(*dimensiones)
            self.ventana.resize(dimensiones)
        if posicion:
            # posicion = QtCore.QPoint(*posicion)
            self.ventana.move(posicion)

        if configuracion_ventana.value("alineamiento_columnas"):
            self.alineamiento_columnas = configuracion_ventana.value("alineamiento_columnas")

        alineamientos_estados = configuracion_ventana.value("alineamiento_columnas_estados")
        self.alineamientos_estados = alineamientos_estados if alineamientos_estados else self.alineamientos_estados

        try:
            self.tablaPrincipal.header().restoreState(orden_columnas)
            self.tabla_estados.header().restoreState(orden_columnas_estado)
        except TypeError as e:
            # print()
            pass
        self.tabla_estados.header().update_forzoso()
        self.tablaPrincipal.header().update_forzoso()

    def guardar_size_pos_inicial(self):
        self.pos_inicial = self.ventana.pos()
        self.size_inicial = {"ancho": self.ventana.width(), "alto": self.ventana.height()}


    def guardar(self):
        configuracion_ventana = QtCore.QSettings(Datas.ruta_configuraciones_ventana, QtCore.QSettings.IniFormat)
        configuracion_ventana.setValue("orden_columnas", self.tablaPrincipal.header().saveState())
        configuracion_ventana.setValue("orden_columnas_estado", self.tabla_estados.header().saveState())
        configuracion_ventana.setValue("alineamiento_columnas", self.alineamiento_columnas)
        configuracion_ventana.setValue("alineamiento_columnas_estados", self.alineamientos_estados)
        configuracion_ventana.setValue("state_ventana", self.ventana.saveState())
        configuracion_ventana.setValue("dimensiones", self.ventana.size())
        configuracion_ventana.setValue("posicion", self.ventana.pos())
        configuracion_ventana.setValue("ultimo_path", self.ultimo_path)
        configuracion_ventana.setValue("splitter_tabla_estado", self.ventana.splitter.saveState())
        configuracion_ventana.setValue("expansion_argumentos_extra", self.expansion_argumentos_extra)

        ancho = self.ventana.width()
        alto = self.ventana.height()
        configuracion_ventana.setValue("dimensiones", [ancho, alto])

    def default_alineamiento_columnas(self):
        default_columnas_alineadas_izquierda = {"ruta_blend", "nombre_blend", "estado"}
        default_alineamiento_columnas = {
            "centro": {col for col in self.columna if col not in default_columnas_alineadas_izquierda},
            "izquierda": {col for col in default_columnas_alineadas_izquierda}, "derecha": set()}
        return default_alineamiento_columnas




class InfoRenderon:
    fecha = datetime.now()
    fecha = fecha.strftime("%d-%m-%Y")
    version = "4.0b" + " - " + fecha
    tolongui = "Chucrut con transistores"
    nombre = "B-Renderon"
    titulo = nombre + " (debug)" if tipo_build == "debug" else nombre







class WindowsDespierto:
    ES_CONTINUOUS = 0x80000000
    ES_SYSTEM_REQUIRED = 0x00000001
    ES_DISPLAY_REQUIRED = 0x00000002
    activo = False

    @classmethod
    def mantener(wd):
        ctypes.windll.kernel32.SetThreadExecutionState(
            wd.ES_CONTINUOUS | \
            wd.ES_DISPLAY_REQUIRED)
        wd.activo = True

    @classmethod
    def liberar(wd):
        ctypes.windll.kernel32.SetThreadExecutionState(
            wd.ES_CONTINUOUS)
        wd.activo = False



class Debug:

    @staticmethod
    def loguear_actividad(texto):
        with open(Datas.ruta_Archivo_debug_acciones_timeadas, "a") as archivo:
            archivo.write(UtilidadesTiempo.hora() + " " + texto + "\n")



# app.setStyle('')






class DispositivosGpu(QObject):
    reportar_hallazgos = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.ya_leyo = False

        self.cycles_por_tipo = {}
        # forma: {tipo: {nombre: [lista ids], ...} ...}

        self.hay_dispositivos = False
        self.infos_blender = None

        self.ocupados = set()

        self.gpus_eevee = {}

        # forma: {nombre: path}

        self.nombres_unicos = {}
        # forma: {nombre: id_depurado}

    def desocupar_gpus(self, lista_ids):
        for id in lista_ids:
            self.ocupados.discard(self.nombre_unico_para_id(id))

    def ocupar_gpus(self, lista_ids):
        for id in lista_ids:
            self.ocupados.add(self.nombre_unico_para_id(id))

    def existe_path_eevee(self, gpu):
        if not self.gpus_eevee:
            self.leer_archivos_dispositivos()
        if not gpu in self.gpus_eevee:
            return False
        return os.path.isfile(self.gpus_eevee[gpu])

    def update_nombres_unicos(self):
        nombres_unicos = {}

        for tipo in self.cycles_por_tipo:
            if tipo == "CPU":
                continue

            for nombre in self.cycles_por_tipo[tipo]:
                i = 1  # indice inicial para nombres
                for id in self.cycles_por_tipo[tipo][nombre]:
                    depurado = self.depurar_id(id)
                    if depurado in nombres_unicos:
                        continue
                    nombres_unicos[depurado] = nombre + " ({})".format(i)
                    i += 1

        self.nombres_unicos = nombres_unicos

    def depurar_id(self, id):
        # los id's incluyen al final a veces info de cómo lo está tomando cycles, ej. _Optix, que deseo eliminar para
        # solo distingir dispositivos físicos diferentes

        patron_prefijo = r'^[a-zA-Z]+_'
        depurado = re.sub(patron_prefijo, '', id)
        patron_sufijo = r'_[a-zA-Z]+$'
        depurado = re.sub(patron_sufijo, '', depurado)

        return depurado

    def nombre_unico_para_id(self, id):
        if id in {"CPU", "INCIERTO"}:
            return id
        if id in self.nombres_unicos.values():
            return id  # esto es medio chancho, es porque en eevee guardo el nombre unico como id directamente
        depurado = self.depurar_id(id)
        return self.nombres_unicos[depurado]

    def leer_archivos_dispositivos(self):
        try:
            with open(Datas.ruta_dispositivos_cycles, "r", encoding="utf8") as archivo_dispositivos:
                data_dispositivos_cycles = archivo_dispositivos.read()
        except IOError as E:
            print(E)
            self.reportar_hallazgos.emit(False)
            return False
        try:
            with open(Datas.ruta_dispositivos_eevee, "r", encoding="utf8") as archivo_dispositivos:
                data_dispositivos_eevee = archivo_dispositivos.read()
        except IOError as E:
            print(E)
            data_dispositivos_eevee = None

        return self.leer_data_dispositivos(data_dispositivos_cycles, data_dispositivos_eevee)

    def leer_data_blender(self, data_blender):
        for data in data_blender.splitlines():
            if data.startswith(Datas.handle_dispositivos):
                self.leer_data_dispositivos(data.removeprefix(Datas.handle_dispositivos))
                break

    def leer_data_dispositivos(self, data_dispositivos_cycles, data_dispositivos_eevee=None):
        try:
            self.cycles_por_tipo = json.loads(data_dispositivos_cycles)
        except Exception as e:
            self.reportar_hallazgos.emit(False)
            return False
        try:
            self.gpus_eevee = json.loads(data_dispositivos_eevee)
        except Exception as e:
            pass

        self.update_nombres_unicos()

        self.ya_leyo = True
        self.reportar_hallazgos.emit(any(self.cycles_por_tipo))

        # if self.reportar_hallazgos:
        #     self.reportar_hallazgos(any(self.por_tipo))

        self.guardar_archivo_dispositivos()
        return True

    def guardar_archivo_dispositivos(self):
        json_dispositivos_cycles = json.dumps(self.cycles_por_tipo, default=serializar)
        json_dispositivos_eevee = json.dumps(self.gpus_eevee, default=serializar)
        try:
            with open(Datas.ruta_dispositivos_cycles, "w", encoding="utf8") as archivo_dispositivos:
                archivo_dispositivos.write(json_dispositivos_cycles)
            with open(Datas.ruta_dispositivos_eevee, "w", encoding="utf8") as archivo_dispositivos:
                archivo_dispositivos.write(json_dispositivos_eevee)
        except IOError:
            pass

    def encontrar_dispositivos_disponibles(self):
        Datas.crear_script(Datas.ruta_script_leer_dispositivos, Datas.script_leer_dispositivos)
        argumentos = ['-b', '--factory-startup', '-P', Datas.ruta_script_leer_dispositivos]
        self.infos_blender = InfosBlender(self.leer_data_blender)
        self.infos_blender.correr_blender(argumentos)




# class InfosEscenaManual:
#
#     def __init__(self, items, avisar=None, cursor_espera=True):
#         self.item = items[0]
#         self.items = items.copy()
#         if self.item.tag_blender != "Default":
#             version_blender = versiones_blender.versiones[self.item.tag_blender]
#         else:
#             version_blender = None
#         self.infos_blender = InfosBlender(retorno_info=self.leer_data, cursor_espera=cursor_espera,
#                                           version_blender=version_blender)
#         self.avisar = avisar
#         self.preservar_propiedades_argumentadas = False
#         self.argumentos_base = None
#
#     def averiguar(self):
#         path = os.path.join(self.item.ruta_blend, self.item.nombre_blend)
#         Datas.crear_script(Datas.ruta_script_infos_escena,
#                            Datas.script_infos_escena)
#
#         self.argumentos_base = ['-b', path, '--factory-startup']
#         self.recursion_items()
#
#     def recursion_items(self):
#         if not self.items:
#             if self.avisar:
#                 self.avisar()
#             return
#         self.item = self.items.pop()
#         argumentos = self.argumentos_base.copy()
#         if self.item.escena:
#             argumentos.extend(["-S", self.item.escena])
#         argumentos.extend(['-P', Datas.ruta_script_infos_escena])
#         self.item.recabando_info = True
#         self.infos_blender.correr_blender(argumentos)
#
#     def leer_data_legacy(self, data):
#         data_json = ""
#         for linea in data.splitlines():
#             if not linea.startswith(Datas.handle_scene_data):
#                 continue
#
#             try:
#                 data_json = json.loads(linea.removeprefix(Datas.handle_scene_data))
#                 break
#             except Exception as e:
#                 print(e)
#                 return
#         if not data_json:
#             return
#         info_escena = InfosEscenaBlend(*data_json)
#         self.item.asimilar_info_escena(info_escena, self.preservar_propiedades_argumentadas)
#
#         self.recursion_items()
#
#     def leer_data(self, data):
#         patron_str = rf'{re.escape(Datas.handle_scene_data)}\s*(\[.*?\])'
#         patron = re.compile(patron_str)
#
#         # Search for the pattern in the text
#         match = patron.search(data)
#         if match:
#             json_list_str = match.group(1)
#             try:
#                 data_json = json.loads(json_list_str)
#                 print("Captured list:", data_json)
#             except json.JSONDecodeError as e:
#                 print("Error parsing JSON:", e)
#                 return
#         else:
#             print("List not found")
#             return
#
#         info_escena = InfosEscenaBlend(*data_json)
#         self.item.asimilar_info_escena(info_escena, self.preservar_propiedades_argumentadas)
#
#         self.recursion_items()
#
#
# class InfoEscenasManual:  # esto incluye todo lo que hace infosescenamanual pero mantengo por separadas por cuetsiones
#     #  de performance posibles, aunque no probé
#
#     def __init__(self, archivo=None, item=None, avisar=None, pasar_parametro=False, cursor_espera=True):
#         if archivo:
#             self.archivo = archivo
#         elif item:
#             self.archivo = item.ruta_blend_completa
#         else:
#             return
#
#         self.item = item
#         version_blender = versiones_blender.versiones[item.tag_blender]
#         self.infos_blender = InfosBlender(self.leer_data, cursor_espera=cursor_espera, version_blender=version_blender)
#         self.avisar = avisar
#         self.pasar_parametro = pasar_parametro
#         self.output_blender = ""
#
#     def averiguar(self):
#         Datas.crear_script(Datas.ruta_script_escenas,
#                            Datas.script_escenas)
#         argumentos = ['-b', self.archivo, '--factory-startup', '-P', Datas.ruta_script_escenas]
#         # argumentos = ['-b', self.archivo, '-P', Datas.ruta_script_escenas]
#         self.infos_blender.correr_blender(argumentos)
#         if self.item:
#             self.item.recabando_info = True
#
#     def leer_data(self, data):
#         escenas = {}
#         for linea in data.splitlines():
#             if not linea.startswith(Datas.handle_scene_data):
#                 continue
#
#             try:
#                 data_json = json.loads(linea.removeprefix(Datas.handle_scene_data))
#                 info_escena = InfosEscenaBlend(*data_json)
#                 escenas[info_escena.escena] = info_escena
#             except Exception as e:
#                 print(e)
#
#         if not (escenas and len(escenas)):
#             return
#
#         if self.item:
#             self.item.escenas = escenas
#             # for escena in escenas:
#             #     if not escena.camara:
#             #         alertas.alerta_generica("alerta_camara")
#             self.item.recabando_info = False
#
#         if self.avisar:
#             parametros_aceptados = signature(self.avisar).parameters
#             parametros_pasar = {}
#             if "escenas" in parametros_aceptados:
#                 parametros_pasar["escenas"] = escenas
#             if "ruta" in parametros_aceptados:
#                 parametros_pasar["ruta"] = self.archivo
#
#             self.avisar(**parametros_pasar)


class InfoColecciones(QObject):
    recabo = pyqtSignal(ItemCola)

    def __init__(self, parent, item=None, avisar=None, cursor_espera=True):
        super().__init__()
        self.archivo = item.ruta_blend_completa

        atajo_cancelar_busqueda = QtWidgets.QShortcut(QtGui.QKeySequence('Esc'), parent)
        atajo_cancelar_busqueda.activated.connect(self.cancelar_busqueda)

        self.item = item
        self.infos_blender = InfosBlender(self.leer_data, debug=True, cursor_espera=cursor_espera)
        self.avisar = avisar
        self.output_blender = ""

    def cancelar_busqueda(self):
        self.infos_blender.proceso_blender.kill()

    def averiguar(self):
        Datas.crear_script(Datas.ruta_script_colecciones,
                           Datas.script_colecciones)

        argumentos = ['-b', self.archivo, '--factory-startup']
        if self.item.escena:
            argumentos.extend(["-S", self.item.escena])

        argumentos.extend(['-P', Datas.ruta_script_colecciones])

        self.infos_blender.correr_blender(argumentos)
        if self.item:
            self.item.recabando_info = True

    def leer_data(self, data):
        data_json = escena_activa = view_layer_activo = None
        for linea in data.splitlines():
            if linea.startswith(Datas.prefijo_viewlayer_activo):
                view_layer_activo = linea.removeprefix(Datas.prefijo_viewlayer_activo)
                continue
            elif linea.startswith(Datas.prefijo_escena_activa):
                escena_activa = linea.removeprefix(Datas.prefijo_escena_activa)
                continue
            elif not linea.startswith(Datas.prefijo_colecciones):
                continue
            try:
                data_json = json.loads(linea.removeprefix(Datas.prefijo_colecciones))
            except Exception as e:
                print(e)


        self.item.colecciones = {"data_original": data_json, "escena_activa": escena_activa,
                                 "viewlayer_activo": view_layer_activo, "seleccion": {}, "collection_tokens": {}}

        self.item.recabando_info = False
        self.recabo.emit(self.item)


# class InfosBlender:
#     procesos_activos = set()
#
#     def __init__(self, retorno_info=None, cursor_espera=True, debug=True, version_blender=None, live=False):
#         self.proceso_blender = None
#         self.retorno_info = retorno_info
#         self.output_blender = ""
#         self.version_blender = version_blender if version_blender else versiones_blender.default
#         self.debug = debug
#         self.cursor_espera = cursor_espera
#         self.live = live # actualmente no en uso. La idea sería poder ir leyendo e interpretando la data a medida
#         # que va saliendo. Originalmente para poder prescindir del factory-settings e igual tomar la data ligeramente
#         # aún si algún addon bloquea el cierre de blender
#
#     def correr_blender(self, argumentos=None):
#         if argumentos is None:  # esto para permitir corridas diagnóstico supongo yo, no recuerdo
#             argumentos = ["-b"]
#         if self.cursor_espera:
#             QApplication.setOverrideCursor(Qt.WaitCursor)
#         self.proceso_blender = QtCore.QProcess()
#         self.procesos_activos.add(self.proceso_blender)
#         self.proceso_blender.setArguments(argumentos)
#         self.proceso_blender.setProgram(self.version_blender)
#         self.proceso_blender.start()
#         self.proceso_blender.readyReadStandardOutput.connect(self.leer_output)
#         self.proceso_blender.finished.connect(self.termino)
#
#     def leer_output(self):  # esto requiere refactor asoluto
#         lectura = self.proceso_blender.readAll().data().decode('utf-8', 'ignore')
#         self.output_blender += lectura
#         if self.live:
#             self.retorno_info(lectura)
#         if self.debug:
#             print(lectura)
#             # os.makedirs(Datas.ruta_base_debug, exist_ok=True)
#             # with open(Datas.ruta_archivo_debug_infoescenas, "a", encoding="utf8") as output_debug:
#             #     output_debug.write(lectura)
#
#
#     def termino(self):
#         self.procesos_activos.discard(self.proceso_blender)
#         if self.retorno_info and not self.live:
#             self.retorno_info(self.output_blender)
#         self.output_blender = ""
#         QApplication.restoreOverrideCursor()


class apagado:
    @staticmethod
    def apagar_pc():
        if plataforma == "Windows":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"], check=True)
            # os.system("shutdown -s -t 1")
        elif plataforma == "Linux":
            subprocess.run(["systemctl", "suspend"], check=True)
            # os.system("shutdown -h now")
        sys.exit(app.exec_())





def capturar_expansiones_subitems(item: QTreeWidgetItem):
    # if not item.isExpanded():
    #     return False
    expansiones = []
    for i in range(item.childCount()):
        child_i = item.child(i)
        if not child_i.childCount():
            expansiones.append(False)
            continue
        expansiones.append(capturar_expansiones_subitems(child_i))
    return [item.isExpanded(), expansiones] if expansiones else item.isExpanded()

def aplicar_expansiones_subitems(item: QTreeWidgetItem, expansiones):
    for i, xp in enumerate(expansiones):
        item_i = item.child(i)
        if not item_i:
            continue
        if isinstance(xp, bool):
            item_i.setExpanded(xp)
            continue
        item_i.setExpanded(xp[0])
        aplicar_expansiones_subitems(item_i, xp[1])


def expandir_subitems_todos(item: QTreeWidgetItem):
    item.setExpanded(True)
    for i in range(item.childCount()):
        child_item = item.child(i)
        expandir_subitems_todos(child_item)



os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

# os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
# os.environ["QT_SCALE_FACTOR"] = "1.5"


if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

# app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

app = QApplication(sys.argv)
app_context.app = app

plataforma = sys.platform
if plataforma.startswith("win"):
    plataforma = "Windows"
elif plataforma.startswith("lin"):
    plataforma = "Linux"
elif plataforma.lower().startswith("dar"):
    plataforma = "Mac"
else:
    sys.exit(app.exec_())

app_context.plataforma = plataforma

if plataforma == "Windows":
    from PyQt5 import QtWinExtras


iconos.set_iconos_no_themeables() # es la primera carga de resources y necesita que exista app para no crashear
iconos.set_icons_for_theme(defaults_configuracion.skin_bdark)

app.setWindowIcon(iconos.icono_app)
app.setStyle('Fusion')

ventana_principal = None

Datas.update_ruta_versiones_blender(plataforma)


configuracion = configuracion_general.configuracion
configuracion.inicializar()


versiones_blender = blenders.versiones_blender
versiones_blender.leer()

app_context.versiones_blender = versiones_blender
colas = colas_perennes.colas
colas.inicializar()
app_context.colas = colas


Datas.crear_subcarpetas(tipo_build)


# auto_nombrado = AutoNombrado()

watch_folders = WatchFolders()
app_context.watch_folders = watch_folders

gpus = DispositivosGpu()

cola = ColaDeRender()
app_context.cola = cola

modos = management_modos.modos
app_context.modos = modos

if not modos.leer_modos():
    modos.crear_defaults()

schedules = Schedules()

# test_config = VentanaConfiguracion()


if not configuracion.leer_configuracion_json():
    dialogo_inicial = VentanaConfiguracion()


ventana_principal = Ventana()
#a app context se pasa al inicio del init


exit_code = app.exec_()

print(f"Exit code: {exit_code}")
sys.exit(exit_code)