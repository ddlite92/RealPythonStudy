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

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog

from traducciones import traducir
import ui.blend_no_encontrado


class DialogoBlendNoEncontrado(QtWidgets.QDialog, ui.blend_no_encontrado.Ui_item_no_encontrado):
    def __init__(self, ventana, datos_item):
        super().__init__()
        self.setupUi(self)
        self.datos_item = None
        self.paths_erroneos = []
        self.paths_correctos = []
        self.boton_omitir.clicked.connect(self.omitir)
        self.boton_reubicar.clicked.connect(self.reubicar)
        self.btn_offline.clicked.connect(self.offlinear)
        self.accion = None
        self.ventana = ventana
        self.actualizar(datos_item)

        self.boton_aceptar.clicked.connect(self.aceptar)
        self.boton_cancelar.clicked.connect(self.cancelar)
        self.ruta_blend.textChanged.connect(self.ruta_cambio)

        self.chk_adivinar.setEnabled(False)

    def actualizar(self, datos_item):
        self.datos_item = datos_item
        self.nombre_blend.setText(self.datos_item.nombre_blend)
        self.ruta_blend.setText(self.datos_item.ruta_blend)
        self.boton_aceptar.setEnabled(False)
        if self.paths_correctos and self.chk_adivinar.isChecked():
            for erroneos_previo_i, correctos_previo_i in zip(self.paths_erroneos, self.paths_correctos):
                conjetura_i = conjetura(erroneos_previo_i, correctos_previo_i, datos_item["ruta_blend"])
                if blend_existe(conjetura_i, datos_item["nombre_blend"]):
                    return conjetura_i
        return 0


    def aceptar(self):
        self.paths_erroneos.append(self.datos_item.ruta_blend)
        self.datos_item.ruta_blend = self.ruta_blend.text()
        self.paths_correctos.append(self.ruta_blend.text())

        self.accion = "AGREGAR"
        self.close()

    def cancelar(self):
        self.close()

    def offlinear(self):
        self.accion = "OFFLINEAR"
        self.close()

    def omitir(self):
        self.accion = "OMITIR"
        self.close()

    def ruta_cambio(self):
        self.verificacion(self.ruta_blend.text())

    def reubicar(self):
        ruta_elegida = QFileDialog.getExistingDirectory(self, traducir("Explorar ruta blend"),
                                                        self.datos_item.ruta_blend)
        self.verificacion(ruta_elegida)

    def verificacion(self, ruta_nueva):
        verifica = blend_existe(ruta_nueva, self.datos_item.nombre_blend)
        self.boton_aceptar.setEnabled(verifica)
        self.chk_adivinar.setEnabled(verifica)
        self.ruta_blend.setText(ruta_nueva)

    def closeEvent(self, evento):
        if not self.accion:
            self.accion = "CANCELAR"

    def retranslateUi(self, ventana_item_no_encontrado):
        ventana_item_no_encontrado.setWindowTitle(traducir("Blend not found!"))
        self.chk_adivinar.setText(traducir("Try to guess the path for other missing blends"))
        self.boton_cancelar.setText(traducir("Cancel"))
        self.boton_omitir.setText(traducir("Skip"))
        self.mensaje_blend_no_encontrado.setText(traducir("Blend not found:"))
        self.nombre_blend.setText(traducir("Blend Name"))
        self.boton_reubicar.setText(traducir("Relocate"))
        self.boton_aceptar.setText(traducir("Accept"))
        self.btn_offline.setText(traducir("Offline"))

def particionar(path):
    path = os.path.normpath(path)
    return path.split(os.sep)


def indice_divergencia_particiones(path_particionado_a, path_particionado_b):
    i = 0  # por si las particiones estuvieren vacías?
    for i, (parte_i_a, parte_i_b) in enumerate(zip(path_particionado_a, path_particionado_b)):
        print(i)
        if parte_i_a != parte_i_b:
            break
    return i


def parte_cambiada(path_erroneo, path_correcto):
    path_erroneo_particionado = particionar(path_erroneo)
    path_correcto_particionado = particionar(path_correcto)

    indice_divergencia = indice_divergencia_particiones(reversed(path_erroneo_particionado),
                                                        reversed(path_correcto_particionado))

    parte_osoleta = path_erroneo_particionado[:-indice_divergencia]
    parte_nueva = path_correcto_particionado[:-indice_divergencia]

    return [parte_osoleta, parte_nueva]


def conjetura(path1_erroneo, path1_correcto, path2_erroneo):
    if path1_erroneo == path2_erroneo:
        return path1_correcto

    try:
        raiz_comun = os.path.commonpath([path1_erroneo, path2_erroneo])
    except Exception as e:
        print("Exception", e) # debug print
        return ""

    path1_parte_obsoleta, parte_nueva = parte_cambiada(path1_erroneo, path1_correcto)

    path1_string_obsoleta = os.sep.join(path1_parte_obsoleta)
    string_nueva = os.sep.join(parte_nueva)

    path2_erroneo = os.path.normpath(path2_erroneo)

    if path1_string_obsoleta in raiz_comun:
        return path2_erroneo.replace(path1_string_obsoleta, string_nueva)


def blend_existe(ruta, nombre):
    return os.path.isfile(os.path.join(ruta, nombre)) and os.path.splitext(nombre)[1].startswith(".blend")


# 
# 
# path1 = "c:/tarata/popocha/sarasa/"
# path2 = "c:/tarata/popocha/botrolnio/"
# 
# path1B = "d:/stromboli/murmus/popocha/sarasa/"
# 
# conjetura(path1, path1B, path2)
