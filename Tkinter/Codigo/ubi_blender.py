from traducciones import traducir
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from distutils import spawn

configuracion = None


def erronea():
    alerta = QMessageBox()
    alerta.setIcon(QMessageBox.Warning)
    alerta.setWindowTitle(traducir("Atención!"))
    alerta.setText(traducir("alerta ruta"))
    alerta.setStandardButtons(QMessageBox.Ok)
    alerta.button(alerta.Ok).setText(traducir("Aceptar"))
    alerta.exec_()


def es_valida(ubi_blender):
    # ruta, nombre = os.path.split(ubi_blender)
    return ubi_blender and spawn.find_executable(ubi_blender) is not None


def explorar(parent, ruta_base):
    if ruta_base is None:
        try:  # esto para asegurar porque hubo crash en distribución de linux no soportada
            ruta_base = configuracion.blenders.ruta_default
        except:
            ruta_base = ""

    ruta_nueva, _ = QFileDialog.getOpenFileName(parent, traducir("Ruta Blender"), ruta_base)  # a traduccion.traducir
    if ruta_nueva:
        if es_valida(ruta_nueva):
            return ruta_nueva
        else:
            erronea()
            explorar(parent, ruta_base, configuracion)
