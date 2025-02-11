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
import re
import shutil
from distutils import spawn
from enum import StrEnum

from PyQt5.QtWidgets import QFileDialog, QMessageBox

import app_context
import os
import datas
import alertas

from traducciones import traducir
from utils import is_subdir, restore_cursor, set_cursor_espera
from pathlib import PurePath
from PyQt5.QtCore import QObject, QProcess, pyqtSignal

try:
    base_win = os.environ["ProgramW6432"] + "/Blender Foundation/"
except KeyError:
    base_win = ''
tag_default = "Default"


class Ejecutador(QObject):
    # Signals to communicate process output or errors
    outputReady = pyqtSignal(str)
    # errorOccurred = pyqtSignal(str)
    resultado = pyqtSignal(bool, str, str)

    def __init__(self, parent=None, ruta=""):
        super().__init__(parent)
        self.ruta = ruta
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)
        self.process.errorOccurred.connect(self.fallo)
        self.process_output = ""

    def run(self, args=None):
        # Start the process
        if args is None:
            args = []
        self.process.start(self.ruta, args)

    def handle_stdout(self):

        output = self.process.readAllStandardOutput().data().decode()
        self.process_output += output  # Accumulate output for version check
        self.outputReady.emit(output)

    def handle_stderr(self):
        error = self.process.readAllStandardError().data().decode()
        self.resultado.emit(False, "", "")

    def fallo(self):
        self.resultado.emit(False, self.ruta, "toto")

    def process_finished(self):
        self.outputReady.emit("Process finished.")
        # Check for the Blender version in the process output
        version = self.extract_version(self.process_output)
        self.resultado.emit(True, self.ruta, version)
        # print("Process finished.", )  # debug print

    def extract_version(self, output):
        # Use regex to find the Blender version
        version_match = re.search(r'Blender (\d+\.\d+\.\d+)', output)
        if version_match:
            return version_match.group(1)
        return None


class ParamsBlender(StrEnum):
    NOMBRE = "nombre"
    VERSION = "version"
    RUTA = "ruta"


class Blenders:
    tag_eevee = "Eevee GPU"

    def __init__(self):
        self.blenders = {}
        self.ejecutador = None
        self.debo_buscar_nueva = True
        self.no_insistir = None

    def tag_mostrado(self, tag):
        if tag == tag_default:
            version = self.blenders[tag][ParamsBlender.VERSION]
            return f"{tag_default} ({version})"
        return tag

    def agregar(self, tag, ruta, version):
        self.blenders[tag] = {ParamsBlender.RUTA: ruta, ParamsBlender.VERSION: version}

    def actualizar(self, tag, ruta="", version=""):
        data = {}
        if ruta:
            data[ParamsBlender.RUTA] = ruta
        if version:
            data[ParamsBlender.VERSION] = version
        self.blenders[tag].update(data)

    def ruta(self, tag):
        return self.blenders[tag][ParamsBlender.RUTA]

    @property
    def default(self):
        return self.blenders.get(tag_default, {})

    @default.setter
    def default(self, default):
        self.blenders[tag_default] = default

    @property
    def ruta_default(self):
        default = self.blenders.get(tag_default, None)
        if default:
            default = default[ParamsBlender.RUTA]
        return default if isinstance(default, str) else None

    def set_default(self, ruta, version):
        self.agregar(tag_default, ruta, version)
        #
        # if is_subdir(ruta, base_win):
        #     self.debo_buscar_nueva = True

    def leer(self):
        try:
            with open(datas.ruta_versiones_blender, "r", encoding="utf8") as json_versiones:
                data = json.load(json_versiones)
        except (IOError, json.decoder.JSONDecodeError) as e:
            data = {}
        self.blenders = data.get("blenders", {})
        self.debo_buscar_nueva = data.get("debo_buscar_nueva", None)
        if self.debo_buscar_nueva is None and self.ruta_default and base_win:
            self.debo_buscar_nueva = is_subdir(self.ruta_default, base_win)

        if not self.ruta_default:
            default = ruta_default()
            # validar_default(default)

    def guardar(self):
        if self.no_insistir:
            self.debo_buscar_nueva = False
        data = {"blenders": self.blenders, "debo_buscar_nueva": self.debo_buscar_nueva}
        try:
            with open(datas.ruta_versiones_blender, "w", encoding="utf8") as archivo_blenders:
                json.dump(data, archivo_blenders)
        except IOError:
            pass

    def buscar_nueva(self):
        if not (app_context.plataforma == "Windows" and self.debo_buscar_nueva):
            return False
        nuevo = checkear_nuevo_blender(self.ruta_default)
        if nuevo:
            alerta, chk_no_sugerir_mas = alertas.alerta_checkbox_yes_no("mensaje_blender_nuevo", nuevo,
                                                                           "nueva_version", "",
                                                                           "no_volver_a_mostrar", False,
                                                                           icon=QMessageBox.Information)
            decision = alerta.exec_()
            if chk_no_sugerir_mas.isChecked():
                self.no_insistir = True
                self.debo_buscar_nueva = False
                self.guardar()
            if decision == QMessageBox.StandardButton.Yes:
                versiones_blender.set_default(nuevo, "")
                validar_default(nuevo)
                self.guardar()

            return True


def checkear_nuevo_blender(ruta):
    versiones = sorted(os.listdir(base_win))
    version_ruta = PurePath(ruta).parent.name
    if version_ruta in versiones and version_ruta != versiones[-1]:
        return base_win + versiones[-1] + "/blender.exe"
    return ""


def ruta_default():
    plataforma = app_context.plataforma
    try:
        if plataforma == "Windows":
            ruta_steam = os.path.join(os.environ["ProgramFiles(x86)"], "Steam/steamapps/common/Blender/blender.exe")
            if os.path.isfile(ruta_steam):
                return ruta_steam
            if os.path.isdir(base_win):
                versiones = sorted(os.listdir(base_win))
                return base_win + versiones[-1] + "/blender.exe"
        elif plataforma == "Linux":
            paths_posibles = ["/snap/blender/current/blender", "/opt/blender/blender", "/snap/bin/blender",
                              "~/blender/blender"]
            for path in paths_posibles:
                if os.path.isfile(path):
                    return path
            encontrar_ruta = shutil.which("blender")
            if encontrar_ruta is not None:
                return encontrar_ruta
            else:
                return ""
        elif plataforma == "Mac":
            return "/Applications/Blender./blender.app/Contents/MacOS/"
    except:
        return ""


def ruta_es_valida(ruta):
    return validar_ruta_y_obtener_version(ruta)[0]


def validar_default(ruta=None):
    ruta = ruta or versiones_blender.ruta_default
    validar_ruta_y_obtener_version(ruta, avisar=procesar_validacion)
    # if es_valida:
    #     versiones_blender.set_default(ruta, version)
    #     versiones_blender.guardar()
    #     return True
    # alerta_ubicacion_erronea()
    #
    # return False


def procesar_validacion(valida, ruta, version):
    if valida:
        versiones_blender.set_default(ruta, version)
        versiones_blender.guardar()
        return
    alerta_ubicacion_erronea()


def validar_ruta_someramente(ruta):
    return os.path.isfile(ruta)


def validar_ruta_y_obtener_version(ruta, cursor_espera=False, avisar=None):
    # if cursor_espera:
    #     set_cursor_espera()
    ejecutador = versiones_blender.ejecutador = Ejecutador(ruta=ruta)
    if avisar:
        ejecutador.resultado.connect(avisar)
    ejecutador.run(["-b", "--factory-startup"])
    # if cursor_espera:
    #     restore_cursor()



def explorar(parent, ruta_base, validar=True):
    if ruta_base is None:
        ruta_base = Blenders.ruta_default
    try:
        ruta_nueva, _ = QFileDialog.getOpenFileName(parent, traducir("Ruta Blender"),
                                                    ruta_base)
    except Exception as e:  # todo: verificar este posible crasheo en linux y corregir
        print("Exception", e)
        ruta_nueva, _ = QFileDialog.getOpenFileName(parent, traducir("Ruta Blender"))

    if ruta_nueva:
        if not validar:
            return ruta_nueva
        if validar_ruta_someramente(ruta_nueva):
            return ruta_nueva
        else:
            alerta_ubicacion_erronea()
            explorar(parent, ruta_base)


def alerta_ubicacion_erronea():
    alertas.alerta_generica("alerta ruta")


versiones_blender = Blenders()
