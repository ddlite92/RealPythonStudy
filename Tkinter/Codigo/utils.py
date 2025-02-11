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
from pathlib import Path

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QApplication


def is_subdir(path_a, path_b):
    # Convert the paths to absolute Path objects
    try:
        path_a = Path(path_a).resolve()
        path_b = Path(path_b).resolve()
    except TypeError:
        return False

    try:
        # Check if pathA is a subdirectory of pathB
        return path_b in path_a.parents
    except ValueError:
        # Handle edge cases where resolve() fails or paths are invalid
        return False


def agregar_linea(a, b):
    return f"{a}\n{b}" if a and b else a + b


def renombrar_duplicado(nombre, lista):
    match = re.search(r'\d+$', nombre)
    if match:
        numero = match.group()
        nuevo = int(numero) + 1
        return nombre.rstrip(numero) + str(nuevo)
    num_sufijo = 1
    while agregar_sufijo(nombre, num_sufijo) in lista:
        num_sufijo += 1
    return agregar_sufijo(nombre, num_sufijo)


def agregar_sufijo(nombre, numero):
    return nombre + "." + f'{numero:03d}'


def serializar(objeto):
    try:
        return objeto.toJSON()
    except AttributeError:
        return objeto.__dict__


def encoder_json_items(obj):
    if isinstance(obj, str) and obj == "":
        return obj
    if isinstance(obj, set):
        return list(obj)
    return json.JSONEncoder.default(obj)


def restore_cursor():
    while QApplication.overrideCursor() is not None:
        QApplication.restoreOverrideCursor()
    QApplication.processEvents()


def set_cursor_espera():
    #
    # if QThread.currentThread() == QApplication.instance().thread():
    #     print("Called from the main thread")
    # else:
    #     print("Called from a different thread")
    # if tooltip:
    #     QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), traducir(tooltip))
    if QApplication.overrideCursor() is None:
        QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))


class UnDefaultDict(dict):
    def __init__(self, default, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default = default

    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self.default(key)
