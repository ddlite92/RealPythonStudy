import os
import re

from PyQt5.QtWidgets import QDockWidget, QPushButton, QGridLayout, QHBoxLayout, QSpacerItem, QWidget, QSizePolicy, \
    QLabel, QFileDialog
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QTextCursor, QTextDocument

import datas
import app_context


class DockConsola(QDockWidget):
    def __init__(self, ventana_principal):
        super().__init__()

        self.ventana = ventana_principal
        self.cola = None

        self.configuracion = None
        self.activo = None
        self.ancho_ventana_sin_dock = None
        self.alto_ventana_sin_dock = None

        self.lbl_livelog = QLabel("Livelog")
        layout_titulo = QHBoxLayout()
        layout_titulo.addItem(QSpacerItem(5, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout_titulo.addWidget(self.lbl_livelog)
        layout_titulo.addItem(QSpacerItem(5, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # self.lbl_livelog.setAlignment(Qt.AlignCenter)

        self.btn_save = QPushButton()
        self.btn_resumir = QPushButton()
        self.btn_borrar = QPushButton()

        self.layout_file = QHBoxLayout(self)
        self.layout_file.addWidget(self.btn_save)
        # self.layout_file.addWidget(self.btn_borrar)
        # self.layout_file.addWidget(self.btn_resumir)
        # self.layout_file.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        # self.layout_file.setSpacing(1)

        self.btn_anterior_save = QPushButton()
        self.btn_siguiente_save = QPushButton()
        self.btn_fin = QPushButton()
        self.btn_inicio = QPushButton()

        self.layout_navegacion = QHBoxLayout(self)
        self.layout_navegacion.addItem(QSpacerItem(5, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout_navegacion.addWidget(self.btn_anterior_save)
        self.layout_navegacion.addWidget(self.btn_siguiente_save)
        self.layout_navegacion.addWidget(self.btn_inicio)
        self.layout_navegacion.addWidget(self.btn_fin)
        self.layout_navegacion.addItem(QSpacerItem(5, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout_navegacion.setSpacing(1)

        self.btn_close = QPushButton()
        self.btn_bottom = QPushButton()
        self.btn_top = QPushButton()
        self.btn_left = QPushButton()
        self.btn_floating = QPushButton()
        self.btn_right = QPushButton()

        self.layout_posicionamiento = QHBoxLayout(self)
        self.layout_posicionamiento.addItem(QSpacerItem(5, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout_posicionamiento.addWidget(self.btn_floating)
        self.layout_posicionamiento.addWidget(self.btn_top)
        self.layout_posicionamiento.addWidget(self.btn_bottom)
        self.layout_posicionamiento.addWidget(self.btn_left)
        self.layout_posicionamiento.addWidget(self.btn_right)
        self.layout_posicionamiento.addItem(QSpacerItem(5, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.layout_posicionamiento.setSpacing(1)
        # self.layout_posicionamiento.addWidget(self.btn_close)

        layout_operaciones_texto = QGridLayout(self)
        layout_operaciones_texto.addLayout(self.layout_file, 0, 0)
        layout_operaciones_texto.addLayout(self.layout_navegacion, 0, 1)
        self.layout = QGridLayout(self)
        self.layout.addLayout(self.layout_file, 0, 0)
        self.layout.addLayout(layout_operaciones_texto, 0, 1)
        self.layout.addLayout(layout_titulo, 0, 2)
        self.layout.addLayout(self.layout_posicionamiento, 0, 3)
        self.layout.addWidget(self.btn_close, 0, 4)
        # self.layout.setContentsMargins(20, -1, -1, -1)
        # self.layout.addItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum), 0, 0)

        self.title_bar = QWidget()
        self.title_bar.setLayout(self.layout)

        self.conectar_segnales()

        self.setTitleBarWidget(self.title_bar)
        # debería haber boton dock/undock, botón close. No

    def set_tooltips(self, traduccion):
        self.btn_top.setToolTip(traduccion.traducir("Dock to top"))
        self.btn_bottom.setToolTip(traduccion.traducir("Dock to bottom"))
        self.btn_left.setToolTip(traduccion.traducir("Dock to left"))
        self.btn_right.setToolTip(traduccion.traducir("Dock to right"))
        self.btn_save.setToolTip(traduccion.traducir("Save livelog as"))
        self.btn_floating.setToolTip(traduccion.traducir("Toggle Dock Floating"))
        self.btn_close.setToolTip(traduccion.traducir("Cerrar"))
        self.btn_siguiente_save.setToolTip(traduccion.traducir("Jump to Next Save/Append Entry"))
        self.btn_anterior_save.setToolTip(traduccion.traducir("Jump to Previous Save/Append Entry"))
        self.btn_inicio.setToolTip(traduccion.traducir("Jump to Beginning"))
        self.btn_fin.setToolTip(traduccion.traducir("Jump to End"))

    def exportar_log(self):
        if not self.activo:
            return
        nombre = "livelog_" + self.activo.nombre_blend.strip(".blend")
        ruta_destino = self.ventana.elegir_archivo("txt", existente=False, nombre_sugerido=nombre)
        self.activo.consola.exportar(ruta_destino)

    def conectar_segnales(self):
        self.btn_bottom.setProperty("area", Qt.BottomDockWidgetArea)
        self.btn_top.setProperty("area", Qt.TopDockWidgetArea)
        self.btn_left.setProperty("area", Qt.LeftDockWidgetArea)
        self.btn_right.setProperty("area", Qt.RightDockWidgetArea)
        self.btn_left.clicked.connect(self.posicionar)
        self.btn_right.clicked.connect(self.posicionar)
        self.btn_top.clicked.connect(self.posicionar)
        self.btn_bottom.clicked.connect(self.posicionar)
        self.btn_floating.clicked.connect(self.toggle)
        self.btn_close.clicked.connect(self.close)
        self.btn_siguiente_save.setProperty("sentido", int(QTextDocument.FindFlags()))
        self.btn_siguiente_save.clicked.connect(self.saltar_entre_saves)
        self.btn_anterior_save.setProperty("sentido", int(QTextDocument.FindBackward))
        self.btn_anterior_save.clicked.connect(self.saltar_entre_saves)
        self.btn_resumir.clicked.connect(self.mostrar_resumen)
        self.btn_fin.setProperty("sentido", QTextCursor.End)
        self.btn_inicio.setProperty("sentido", QTextCursor.Start)
        self.btn_fin.clicked.connect(self.mover_extremo)
        self.btn_inicio.clicked.connect(self.mover_extremo)
        self.btn_save.clicked.connect(self.exportar_log)

    def vestir_iconos(self, iconos):
        self.btn_close.setIcon(iconos.icono_livelog_close)
        self.btn_floating.setIcon(iconos.icono_livelog_floating)
        self.btn_top.setIcon(iconos.icono_livelog_top)
        self.btn_bottom.setIcon(iconos.icono_livelog_bottom)
        self.btn_left.setIcon(iconos.icono_livelog_left)
        self.btn_right.setIcon(iconos.icono_livelog_right)
        self.btn_save.setIcon(iconos.icono_livelog_save)
        self.btn_borrar.setIcon(iconos.icono_quitar_elegidos)
        self.btn_siguiente_save.setIcon(iconos.icono_livelog_next_save)
        self.btn_anterior_save.setIcon(iconos.icono_livelog_previous_save)
        self.btn_fin.setIcon(iconos.icono_livelog_fin)
        self.btn_inicio.setIcon(iconos.icono_livelog_inicio)

    def saltar_entre_saves(self):
        sentido = self.sender().property("sentido")
        flag = QTextDocument.FindFlags(sentido)
        if not self.widget().find("Saved:", flag):
            self.widget().find("Append", flag)
        self.widget().ensureCursorVisible()

    def mover_extremo(self):
        sentido = self.sender().property("sentido")
        self.widget().moveCursor(sentido)
        self.widget().ensureCursorVisible()

    def posicionar(self):
        if self.isFloating():
            self.setFloating(False)
        self.ventana.removeDockWidget(self)
        self.ventana.addDockWidget(self.sender().property("area"), self)
        self.mostrar()

    def toggle(self):
        self.setFloating(not self.isFloating())
        # if self.isFloating():
        #     self.ventana.addDockWidget(Qt.BottomDockWidgetArea, self)
        # else:
        #     self.setFloating(True)

    def mostrar_resumen(self):
        resumen = self.activo.consola.resumen(str(self.activo.consola))
        self.widget().setPlainText(resumen)

    def closeEvent(self, e):
        ancho = self.ventana.size().width()
        e.accept()
        QTimer.singleShot(10, lambda: self.ventana.resize(ancho, 1))
        # esto de dar 1 de altura es como un adjustsize vertical, achica al minimo en que caben las cuestiones. Así se
        # puede estar perdiendo parte de la información si el usuario había agrandado la ventana a lo alto pero dentro
        # de todo va bastante bien y preservar todo sería enrroscado.

    def titular(self, traduccion):
        base_titulo = traduccion.traducir("Live log")
        if self.isFloating():
            self.setWindowTitle(
                base_titulo + " - " + traduccion.traducir("Doble click para anexar"))
        else:
            self.setWindowTitle(base_titulo)

    def mostrar(self):
        if self.isVisible():
            self.close()
            return
        tamaño_previo_ventana = self.ventana.size()
        self.setVisible(True)
        self.ventana.resize(tamaño_previo_ventana)
        self.actualizar_contenido()

    def actualizar_contenido(self):
        # if not self.isVisible():
        # return
        if not self.activo:
            return
        if not self.isVisible():
            return

        texto_consola = str(self.activo.consola) + "\n"
        # texto_consola = self.activo.consola.leer_resumen() + "\n"
        if texto_consola.startswith("Livelog unavailable."):
            if self.activo.estado == "no_comenzado":
                texto_consola = ""
            texto_consola += self.activo.text(self.activo.columna["estado"])

        if not texto_consola:
            return
        self.widget().setPlainText("Reading log...")
        QTimer.singleShot(10, lambda: self.mostrar_texto_nuevo(texto_consola))

    def mostrar_texto_nuevo(self, texto):
        self.widget().setPlainText(texto)
        self.widget().moveCursor(QTextCursor.End)
        self.widget().ensureCursorVisible()


class ConsolaRender:
    numero_lineas_finales_revisar = 250
    numero_lineas_buffer = 400

    def __init__(self, item):
        self.newline_buffer = 0
        self.buffer = []

        nombre_sin_extension = os.path.splitext(item.nombre_blend)[0]
        base_path = os.path.join(datas.ruta_base_livelogs, app_context.colas.actual)

        self.path = os.path.join(base_path, nombre_sin_extension + "_" + item.id + ".txt")

        self.caracteres = 0

        # self.buffer = []
        # self.semi_buffer = ""
        # self.newline_buffer = 0

    def reset(self):
        try:
            with open(self.path, 'w', encoding='utf-8') as archivo_consola:
                self.caracteres = 0
        except FileNotFoundError:
            print("File not found A: " + self.path)
        except IOError as e:
            print("Error reading file A: " + str(e))
        return self

    def cerrar(self):
        self.__iadd__("")

    def __iadd__(self, agregar):
        self.caracteres += len(agregar)
        if agregar and len(self.buffer) < self.numero_lineas_buffer:
            self.buffer.append(agregar)
            return self
        buffer_previo = self.string_buffer()
        self.buffer = [agregar]
        try:
            with open(self.path, 'a', encoding='utf-8') as archivo_consola:
                archivo_consola.write(buffer_previo + "\n")

        except FileNotFoundError:
            print("File not found A: " + self.path)
        except IOError as e:
            print("Error reading file A: " + str(e))
        return self

    def __str__(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as archivo_consola:
                texto_consola = archivo_consola.read()
                texto_consola += self.string_buffer()
                self.caracteres = len(texto_consola)
                return texto_consola
        except FileNotFoundError:
            return "Livelog unavailable. File not found: " + self.path
        except IOError as e:
            return "Livelog unavailable. Error reading file: " + str(e)

    def __len__(self):
        return self.caracteres

    def string_buffer(self):
        return "\n".join(self.buffer)

    def exportar(self, ruta_archivo):
        log = self.__str__()
        try:
            with open(ruta_archivo, 'a', encoding='utf-8') as archivo_log:
                archivo_log.write(log)
        except FileNotFoundError:
            print("File not found A: " + self.path)
        except IOError as e:
            print("Error reading file A: " + str(e))

    def recuento_skips_y_frames(self, calcular_skips=False, ultima_instancia_blender=False):
        texto_consola = ''.join(self.__str__().splitlines())
        if ultima_instancia_blender:
            index_ultima_instancia = texto_consola.rfind("Read blend")
            if index_ultima_instancia != -1:
                texto_consola = texto_consola[index_ultima_instancia:]

        skips = 0
        if calcular_skips:
            skips = texto_consola.count("skipping existing fra")
        pattern = r'Saved:\s*\'(.*?)\'\s*Time:'
        appends = texto_consola.count("Append frame")
        if appends:
            frames = appends
        else:
            saves = re.findall(pattern, texto_consola)
            frames = len(saves) if saves else texto_consola.count(
                "Saved: ")  # esto ultimo para render viewport por ejemplo, que no reporta time

        return frames, skips

    def recuento_frames(self, ultima_instancia_blender=False):
        return self.recuento_skips_y_frames(calcular_skips=False, ultima_instancia_blender=ultima_instancia_blender)[0]

    def ultimas_lineas(self, texto=None):
        if texto is None:
            if self.numero_lineas_finales_revisar <= len(self.buffer):
                texto = self.string_buffer()
            else:
                texto = self.__str__()
        return ''.join(texto[self.numero_lineas_finales_revisar:].splitlines())

    def buscar_error(self):
        texto = self.__str__()
        if all([parte in self.ultimas_lineas(texto) for parte in ["Writing:", "crash.txt"]]):
            return datas.errores_custom["crash"]
        for mensaje_error in datas.errores_conocidos_render.values():
            posicion_error = texto.rfind(mensaje_error)
            if posicion_error != -1:
                parte_final = texto[posicion_error:]
                if "Saved" not in parte_final and "Append" not in parte_final:
                    return mensaje_error

    def extraer_rutas(self):
        texto = self.__str__()
        texto = texto.replace('\n', '')

        # Regular expression to find paths after 'Saved:'
        pattern = r"Saved:\s*'([^']*)'"
        return re.findall(pattern, texto)

    def borrar_archivo_livelog(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            print(f"Error: {self.path} not found")
        except PermissionError:
            print(f"Error: Permission denied to delete {self.path}")
        except OSError as e:
            print(f"Error: {e}")

    @staticmethod
    def resumen(texto):
        lineas = texto.splitlines()
        resumen = []
        buffer = []
        semi_buffer = ""
        newline_buffer = 0

        for linea in lineas:
            linea_limpia = linea.strip()

            if semi_buffer:
                linea_compuesta = semi_buffer + linea_limpia
                semi_buffer = ""
            else:
                linea_compuesta = ""
            if linea_limpia.startswith("Fra:") or linea_compuesta.strip().startswith("Fra:"):
                buffer.append(linea)
                newline_buffer = 0

            elif linea_limpia.startswith("F"):
                semi_buffer = linea
            elif linea_limpia == "":
                newline_buffer += 1
            else:
                if buffer:
                    resumen.append("\n" + buffer[-1])
                    buffer = []
                elif newline_buffer:
                    resumen.append("\n" * (newline_buffer - 1))
                newline_buffer = 0
                resumen.append(linea)

        if buffer:
            resumen.append(buffer[-1])

        return '\n'.join(resumen)
