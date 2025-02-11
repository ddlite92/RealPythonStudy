from PyQt5.QtWidgets import QMessageBox, QCheckBox
from traducciones import traducir


def alerta_permisos():
    alerta = QMessageBox()
    alerta.setIcon(QMessageBox.Warning)
    alerta.setWindowTitle(traducir("Atención!"))
    alerta.setText(traducir("faltan permisos"))
    alerta.setStandardButtons(QMessageBox.Ok)
    alerta.button(alerta.Ok).setText(traducir("Aceptar"))
    alerta.exec_()


def alerta_generica(mensaje, anexo_mensaje="", anexo_titulo="", base_titulo="Atención!", icono="warning", cancelable=False):
    iconos = {"info": QMessageBox.Information, "warning": QMessageBox.Warning, "pregunta": QMessageBox.Question}
    icono = iconos[icono]

    alerta = QMessageBox()
    alerta.setIcon(icono)

    if anexo_titulo:
        anexo_titulo = " - " + anexo_titulo
    alerta.setWindowTitle(traducir(base_titulo) + anexo_titulo)
    alerta.setText(traducir(mensaje))
    alerta.setInformativeText(anexo_mensaje)
    alerta.addButton(QMessageBox.Ok)
    alerta.button(alerta.Ok).setText(traducir("Aceptar"))
    if cancelable:
        alerta.addButton(QMessageBox.Cancel)
        return alerta

    alerta.exec_()


def alerta_cancelable(titulo, mensaje, con_ok=False, icono=QMessageBox.NoIcon):
    alerta = QMessageBox()
    alerta.setIcon(icono)
    alerta.setWindowTitle(traducir(titulo))
    alerta.setText(traducir(mensaje))
    if con_ok:
        alerta.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    else:
        alerta.setStandardButtons(QMessageBox.Cancel)

    return alerta


def alerta_checkbox(mensaje, anexo_titulo="", texto_checkbox="", checked=True):
    alerta = QMessageBox()
    alerta.setIcon(QMessageBox.Warning)
    if anexo_titulo:
        anexo_titulo = " - " + anexo_titulo
    alerta.setWindowTitle(traducir("Atención!") + anexo_titulo)
    alerta.setText(traducir(mensaje))
    alerta.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    alerta.button(alerta.Ok).setText(traducir("Aceptar"))
    alerta.button(alerta.Cancel).setText(traducir("Cancelar"))
    if texto_checkbox:
        cb = QCheckBox(traducir(texto_checkbox))
        cb.setChecked(checked)
        alerta.setCheckBox(cb)
    else:
        cb = None
    return alerta, cb

def alerta_checkbox_yes_no(mensaje, anexo_mensaje="", titulo="", anexo_titulo="", texto_checkbox="", checked=True, icon=QMessageBox.Warning):
    alerta = QMessageBox()
    alerta.setIcon(icon)
    if anexo_titulo:
        anexo_titulo = " - " + anexo_titulo
    alerta.setWindowTitle(traducir(titulo) + anexo_titulo)
    alerta.setText(traducir(mensaje) + "\n" + anexo_mensaje)
    alerta.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    alerta.button(alerta.Yes).setText(traducir("Yes"))
    alerta.button(alerta.No).setText(traducir("No"))
    if texto_checkbox:
        cb = QCheckBox(traducir(texto_checkbox))
        cb.setChecked(checked)
        alerta.setCheckBox(cb)
    else:
        cb = None
    return alerta, cb

