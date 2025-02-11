import os
import shutil
import subprocess
from distutils import spawn

from PyQt5.QtWidgets import QFileDialog, QMessageBox

 import , traduccion

def ubi_erronea():
    alerta = QMessageBox()
    alerta.setIcon(QMessageBox.Warning)
    alerta.setWindowTitle(traduccion.traducir("Atención!"))
    alerta.setText(traduccion.traducir("alerta ruta"))
    alerta.setStandardButtons(QMessageBox.Ok)
    alerta.button(alerta.Ok).setText(traduccion.traducir("Aceptar"))
    alerta.exec_()


def ubi_blender_es_valida(ubi_blender):
    if os.path.isdir(ubi_blender):
        if shutil.which("blender", path=ubi_blender) is not None:
            return True
    elif spawn.find_executable(ubi_blender) is not None:
        return True
    return False


def explorar_binario_blender(parent, ruta_base=None):
    if ruta_base is None:
        ruta_base = configuracion.blenders.ruta_default

    explorar, _ = QFileDialog.getOpenFileName(parent, traduccion.traducir("Ruta Blender"), ruta_base)  # a traduccion.traducir
    if explorar:
        if ubi_blender_es_valida(explorar):
            return explorar
        else:
            ubi_erronea()
            explorar_binario_blender(parent)


def explorar_ruta(ruta):
    if plataforma == "Windows":
        os.startfile(ruta)
    elif plataforma == "Mac":
        subprocess.Popen(["open", ruta])
    else:
        subprocess.Popen(["xdg-open", ruta])
