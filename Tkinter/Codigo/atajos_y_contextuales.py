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


from PyQt5 import QtGui, QtWidgets


class CrearAtajos:
    secuencias_usadas = set()
    def __init__(self, parent):
        self.parent = parent
        self.atajos = []
        self.operadores = []

    def crear_atajo(self, nombre_interno, funcion, atajos, parent_alternativo = None, descripcion = None):
        if not parent_alternativo:
            parent = self.parent
        else:
            parent = parent_alternativo
        self.operadores.append(operador(parent, nombre_interno, funcion, atajos=atajos, descripcion=descripcion))

    def conectar_atajos(self):
        self.atajos = self.por_operadores(self.operadores)

    @staticmethod
    def por_operadores(operadores):
        atajos = {}
        for operador in operadores:
            num_atajos = len(operador.atajos)
            if num_atajos > 0:
                sufijo = num_atajos > 1
                for i, atajo_i in enumerate(operador.atajos):
                    if atajo_i in CrearAtajos.secuencias_usadas:
                        continue
                    nombre_atajo = operador.nombre_interno + [str(i), ""][sufijo]
                    atajos[nombre_atajo] = QtWidgets.QShortcut(QtGui.QKeySequence(atajo_i), operador.parent)
                    atajos[nombre_atajo].activated.connect(operador.funcion)
                    CrearAtajos.secuencias_usadas.add(atajo_i)
        return atajos

    @staticmethod
    def particular(parent, teclas, funcion):
        atajo = QtWidgets.QShortcut(QtGui.QKeySequence(teclas), parent)
        atajo.activated.connect(funcion)
        return atajo


class operador:
    def __init__(self, parent, nombre_interno, funcion, nombre_visible=None, atajos=None, descripcion = None):
        self.parent = parent
        self.nombre_interno = nombre_interno
        self.funcion = funcion
        self.nombre_visible = nombre_visible
        self.atajos = atajos
        self.descripcion = descripcion



class GrupoContextual:
    def __init__(self, nombre_interno, operadores, nombre_visible=None, es_submenu=False):
        self.es_submenu = es_submenu
        self.nombre_interno = nombre_interno
        self.nombre_visible = nombre_visible
        self.operadores = operadores


class MenuContextual:
    def __init__(self, parent, qmenu):
        self.parent = parent
        self.qmenu = qmenu
        self.entradas = {}
        self.grupos_contextuales = []
        self.submenues = {}
        self.operadores = {}
        self.atajos = []
        self.inactivos_sin_blends = ()
        self.inactivos_renderizando = ()
        self.inactivos_varios_elegidos = ()

    def definir(self): # cómo manejar submenues? subgrupos sarasa
        for grupo in self.grupos_contextuales:
            if grupo.es_submenu:
                self.submenues[grupo.nombre_interno] = self.qmenu.addMenu("")
                self.menu_actual = self.submenues[grupo.nombre_interno]
            else:
                self.menu_actual = self.qmenu

            for operador_i in grupo.operadores:
                self.agregar_entrada(self.menu_actual, operador_i)

            self.qmenu.addSeparator()

    def agregar_entrada(self, menu, operador):
        self.entradas[operador] = menu.addAction("")
        funcion = self.operadores[operador].funcion
        if not funcion:
            return
        self.entradas[operador].triggered.connect(funcion)

    def popular(self, traduccion):
        for grupo in self.grupos_contextuales:
            if grupo.es_submenu:
                self.submenues[grupo.nombre_interno].setTitle(traduccion.traducir(grupo.nombre_visible))

            for operador_i in grupo.operadores:
                texto = traduccion.traducir(self.operadores[operador_i].nombre_visible)
                atajos = self.operadores[operador_i].atajos
                if atajos:
                    texto += "\t" + self.operadores[operador_i].atajos[0]

                self.entradas[operador_i].setText(texto)

    def agregar_operador(self, nombre_interno, funcion=None, nombre_visible=None):
        atajos_op = ATAJOS[nombre_interno] if nombre_interno in ATAJOS else None
        self.operadores[nombre_interno] = operador(self.parent, nombre_interno, funcion, nombre_visible, atajos_op)
        if atajos_op:
            self.atajos.append(CrearAtajos.por_operadores([self.operadores[nombre_interno]]))

    def agregar_grupo_contextual(self, nombre_interno, operadores, nombre_visible=None, es_submenu=False):
        self.grupos_contextuales.append(GrupoContextual(nombre_interno, operadores, nombre_visible, es_submenu))

    def actualizar_estado(self):
        if self.parent.cola.estado == "renderizando":
            for nombre_operador in self.inactivos_sin_blends: # aca hay items que se deshabilitan y se habilitan de
                # vuelta al toque y viceversa pero qué más da
                self.entradas[nombre_operador].setEnabled(True)
            for nombre_operador in self.inactivos_renderizando:
                self.entradas[nombre_operador].setEnabled(False)
        else:
            for nombre_operador in self.inactivos_renderizando:
                self.entradas[nombre_operador].setEnabled(True)
            for nombre_operador in self.inactivos_sin_blends:
                self.entradas[nombre_operador].setEnabled(bool(self.parent.tablaPrincipal.topLevelItemCount()))

        hay_varios = len(self.parent.tablaPrincipal.selectedItems()) > 1
        for nombre_operador in self.inactivos_varios_elegidos:
            self.entradas[nombre_operador].setEnabled(not hay_varios)

# definiciones de menues y atajos concretos
class ContextualGeneral(MenuContextual):
    def __init__(self, parent):
        self.parent = parent
        self.qmenu = QtWidgets.QMenu()
        super().__init__(self.parent, self.qmenu)

        self.agregar_operador("agregar_blends", self.parent.elegir_archivos, "Añadir Blends")
        self.agregar_operador("agregar_con_escenas", self.parent.agregar_con_escenas,
                              "Añadir escenas")
        self.agregar_grupo_contextual("agregar_blends", operadores=["agregar_blends",
                                                                    "agregar_con_escenas"])

        self.agregar_operador("quitar_todos", self.parent.quitar_todos, "Quitar Todos")
        self.agregar_operador("quitar_terminados", self.parent.quitar_terminados, "Quitar terminados")
        self.agregar_grupo_contextual("quitar_items", ["quitar_todos", "quitar_terminados"])

        self.agregar_operador("abrir_cola", self.parent.cargar_cola, "Abrir cola")
        self.agregar_operador("guardar_cola", self.parent.exportar_cola, "Guardar cola")
        # self.agregar_operador("recuperar_sesion", self.parent.lectura_de_cola,
        #                       "Recuperar sesión anterior", ["Ctrl+Shift+R"])
        self.agregar_grupo_contextual("operaciones_cola", ["abrir_cola", "guardar_cola"])

        self.agregar_operador("log_texto", self.parent.mostrar_log, "Text log")
        self.agregar_operador("live_log", self.parent.dock_consola.mostrar, "Live log")
        # self.agregar_operador("recuperar_sesion", self.parent.lectura_de_cola,
        #                       "Recuperar sesión anterior", ["Ctrl+Shift+R"])
        self.agregar_grupo_contextual("logs", ["log_texto", "live_log"], nombre_visible="Logs", es_submenu=True)

        self.agregar_operador("configuracion", funcion=self.parent.configurar,
                              nombre_visible="Configuración")
        self.agregar_operador("reset_ventana", funcion=self.parent.reset_pos_size_ventana,
                              nombre_visible="Reset window size and position")

        self.agregar_operador("info", funcion=self.parent.acerca_de,
                              nombre_visible="Info")

        self.agregar_grupo_contextual("sistema", ["configuracion", "reset_ventana", "info"])

        self.definir()

        self.inactivos_sin_blends = ("quitar_todos", "quitar_terminados")
        self.inactivos_renderizando = ("abrir_cola", "quitar_todos", "configuracion")


class ContextualElegidos(MenuContextual):
    def __init__(self, parent):
        self.parent = parent
        self.qmenu = QtWidgets.QMenu()
        super().__init__(self.parent, self.qmenu)

        self.agregar_operador("duplicar_simple", self.parent.duplicar_blends, "Duplicar")
        self.agregar_operador("duplicar_en_sitio", self.parent.duplicar_items_en_sitio, "Duplicar en sitio")
        self.agregar_grupo_contextual("duplicar", operadores=["duplicar_simple", "duplicar_en_sitio"],
                                      nombre_visible="Duplicar", es_submenu=True)

        self.agregar_operador("quitar", self.parent.quitar_seleccionados, "Quitar")
        self.agregar_grupo_contextual("quitar", ["quitar"])

        self.agregar_operador("subir", self.parent.subir, "Subir")
        self.agregar_operador("bajar", self.parent.bajar, "Bajar")
        self.agregar_operador("subir_a_tope", self.parent.subir_a_tope, "Subir a tope")
        self.agregar_operador("bajar_a_tope", self.parent.bajar_a_tope, "Bajar a tope")
        self.agregar_grupo_contextual("mover", ["subir", "bajar", "subir_a_tope", "bajar_a_tope"],
                                      nombre_visible="Mover", es_submenu=True)

        self.agregar_operador("cambiar_escena", self.parent.cambiar_escena, "Escenas")
        self.agregar_operador("camaras", self.parent.ajustar_camaras, "Cámaras")
        self.agregar_operador("colecciones", self.parent.ajustar_colecciones, "Colecciones")
        self.agregar_operador("view_layers", self.parent.ajustar_viewlayers, "View Layers")
        self.agregar_operador("nombrado", self.parent.ajustar_nombrado, "Nombrado de salida")

        self.agregar_operador("cambiar_rango", self.parent.cambiar_rango, "Cambiar rango de frames")
        self.agregar_operador("cambiar_blender", self.parent.cambiar_blender,
                              "Versión de Blender")
        self.agregar_operador("argumentos_extra", self.parent.argumentos_extra,
                              "Argumentos extra")
        self.agregar_operador("dispositivos", self.parent.elegir_dispositivos,
                              "Dispositivos de render")

        self.agregar_grupo_contextual("setear_propiedades",
                                      operadores=["cambiar_blender", "argumentos_extra", "cambiar_escena",
                                                  "view_layers", "camaras", "colecciones", "nombrado",
                                                  "dispositivos"],
                                      nombre_visible="Change/Set", es_submenu=True)


        self.agregar_operador("reajustar_modo", nombre_visible="Modo")
        self.agregar_grupo_contextual("modo", operadores=["reajustar_modo"])


        self.agregar_operador("cambiar_color", nombre_visible="Background Color")
        self.agregar_grupo_contextual("background_color", operadores=["cambiar_color"])

        self.agregar_operador("resetear_estado", self.parent.reset_estado_item,
                              "resetear_estado_blends")
        self.agregar_operador("renderizar_item", self.parent.renderizar_item,
                              "renderizar_blend")
        self.agregar_operador("detener_item", self.parent.detener_render_item,
                              "detener_item")

        self.agregar_operador("desactivar_items", self.parent.toggle_desactivar_items,
                              "Desactivar/Activar")

        self.agregar_grupo_contextual("procesamiento_individual",
                                      operadores=["resetear_estado", "renderizar_item",
                                                  "detener_item", "desactivar_items"])


        self.agregar_operador("abrir_blend", self.parent.abrir_blend, "Abrir blend")
        self.agregar_operador("reubicar_blends", self.parent.reubicar_blends, "Relocate blend(s)")
        self.agregar_operador("explorar_ruta_blend", self.parent.explorar_ruta_blend,
                              "Explorar ruta blend")
        self.agregar_operador("explorar_output", self.parent.explorar_ruta_output,
                              "Explorar ruta output")
        self.agregar_operador("ver_render", self.parent.ver_render, "Ver render")

        self.agregar_grupo_contextual("explorar", operadores=["abrir_blend", "reubicar_blends", "explorar_ruta_blend",
                                                              "explorar_output", "ver_render"])

        self.agregar_operador("log_texto", self.parent.mostrar_log, "Text log")
        self.agregar_operador("logs_texto_individuales", self.parent.mostrar_logs_individuales,
                              "Individual text log(s)")
        self.agregar_operador("cerrar_logs_texto", self.parent.cerrar_text_logs,
                              "Cerrar logs texto")
        self.agregar_operador("live_log", self.parent.dock_consola.mostrar, "Live log")
        # self.agregar_operador("recuperar_sesion", self.parent.lectura_de_cola,
        #                       "Recuperar sesión anterior", ["Ctrl+Shift+R"])
        self.agregar_grupo_contextual("logs", ["log_texto", "logs_texto_individuales", "cerrar_logs_texto", "live_log"],
                                      nombre_visible="Logs", es_submenu=True)

        self.definir()

        self.inactivos_varios_elegidos = ("colecciones",)
        self.inactivos_script = ("cambiar_escena", "view_layers", "camaras", "nombrado", "dispositivos")
        self.inactivos_renderizando = {"renderizar_item"}

    def actualizar_estado(self):
        super().actualizar_estado()
        # self.entradas["explorar_output"].setEnabled(bool(
            # self.parent.tablaPrincipal.currentItem() and self.parent.tablaPrincipal.currentItem().ruta_output))
        self.entradas["detener_item"].setEnabled(bool(
            self.parent.tablaPrincipal.currentItem() and self.parent.tablaPrincipal.currentItem().estado == "renderizando"))
        self.entradas["desactivar_items"].setEnabled(bool(
            self.parent.tablaPrincipal.currentItem() and self.parent.tablaPrincipal.currentItem().estado != "renderizando"))
        for nombre_operador in self.inactivos_script: # hago el loop por fuera de la comprobacion para que se vuelvan a activar si luego elijo uno que no está en script
            current_script = self.parent.tablaPrincipal.currentItem() and\
                             self.parent.tablaPrincipal.currentItem().modo == "modo_script"
            self.entradas[nombre_operador].setEnabled(not current_script)

        hay_varios = len(self.parent.tablaPrincipal.selectedItems()) > 1
        for nombre_operador in self.inactivos_varios_elegidos:
            self.entradas[nombre_operador].setEnabled(not hay_varios)
        # self.entradas["cambiar_escena"].setEnabled(len(self.parent.tablaPrincipal.selectedItems()) == 1)


class AtajosPrincipalSinEntrada(CrearAtajos):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # self.atajos = CrearAtajos(self.parent)

        # self.crear_atajo("cambiar_modo", self.parent.toggle_modo, ["Ctrl+Tab"], descripcion="Cambiar modo para agregar")
        # self.crear_atajo("togglear_log", self.parent.btn_log.click, ["L"], descripcion="Abrir log")
        # self.crear_atajo("togglear_consola", self.parent.btn_livelog.click, ["Ctrl+L"],
        #                  descripcion="Mostrar/Ocultar consola blender")
        self.crear_atajo("renderizar", self.parent.accion_btn_render, ATAJOS["renderizar"], descripcion="Renderizar")
        self.crear_atajo("deseleccionar", self.parent.seleccion_nada, ATAJOS["deseleccionar"], descripcion="Deseleccionar todo")
        self.crear_atajo("seleccionar_todo", self.parent.seleccion_todo, ATAJOS["seleccionar_todo"], descripcion="Seleccionar todo")
        self.crear_atajo("detener", self.parent.cola.confirmar_y_detener, ATAJOS["detener"])
        self.crear_atajo("contextual", self.parent.menu_contextual, ATAJOS["contextual"], descripcion="Menu contextual")

        self.crear_atajo("test1", self.parent.test, ["Ctrl+T"])
        self.crear_atajo("test2", self.parent.test2, ["Ctrl+Shift+T"])


        self.conectar_atajos()



ATAJOS = {
    "duplicar_simple": ["Shift+D"],
    "duplicar_en_sitio": ["Ctrl+D"],
    "quitar": ["Delete", "Backspace"],
    "subir": ["Ctrl+Up"],
    "bajar": ["Ctrl+Down"],
    "subir_a_tope": ["Ctrl+Shift+Up"],
    "bajar_a_tope": ["Ctrl+Shift+Down"],
    "cambiar_escena": ["Alt+S"],
    "camaras": ["Alt+C"],
    "colecciones": ["Alt+T"],
    "view_layers": ["Alt+V"],
    "nombrado": ["Alt+O"],
    "cambiar_rango": ["Alt+F"],
    "cambiar_blender": ["Alt+B"],
    "argumentos_extra": ["Alt+E"],
    "dispositivos": ["Alt+D"],
    "reajustar_modo": [],  # No shortcut specified
    "resetear_estado": ["Ctrl+R"],
    "renderizar_item": [],  # No shortcut specified
    "detener_item": [],  # No shortcut specified
    "desactivar_items": ["M"],
    "abrir_blend": ["Shift+Return", "Shift+Enter"],
    "reubicar_blends": [],  # No shortcut specified
    "explorar_ruta_blend": ["Ctrl+Return", "Ctrl+Enter"],
    "explorar_output": ["Ctrl+Shift+Return", "Ctrl+Shift+Enter"],
    "ver_render": ["Ctrl+Space"],
    "logs_texto_individuales": ["Shift+L"],
    "cerrar_logs_texto": ["Alt+L"],
    "agregar_blends": ["Shift+A"],
    "agregar_con_escenas": ["Ctrl+Shift+A"],
    "quitar_todos": ["Ctrl+Shift+Delete"],
    "quitar_terminados": ["Alt+Delete"],
    "abrir_cola": ["Ctrl+O"],
    "guardar_cola": ["Ctrl+S"],
    "log_texto": ["L"],
    "live_log": ["Ctrl+L"],
    "renderizar": ["Ctrl+F12"],
    "deseleccionar": ["Alt+A"],
    "seleccionar_todo": ["A"],
    "detener": ["Esc"],
    "contextual": ["Space"],
    "reset_ventana": ["Alt+W"],




}


def atajos_formateados(nombre_operador):
    if not nombre_operador in ATAJOS:
        return ""
    atajo = ATAJOS[nombre_operador][0]
    return " ({})".format(atajo)

