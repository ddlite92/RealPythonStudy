from PyQt5 import QtWidgets, QtGui
import os


class RenderonStatusbar:
    def __init__(self, ventana, cola, statusbar, traduccion, plataforma):
        self.ventana = ventana
        self.cola = cola
        self.statusbar = statusbar
        self.traduccion = traduccion
        self.plataforma = plataforma

        self.estado = QtWidgets.QLabel()

        self.item_reportante = None

        self.estado.setObjectName("status_estado")
        self.num_blends = QtWidgets.QLabel()
        self.num_blends.setObjectName("status_num_blends")

        self.nombre_blend = QtWidgets.QLabel()
        self.nombre_blend.setObjectName("status_estado_blend")

        self.num_frame = QtWidgets.QLabel()
        self.num_frame.setObjectName("status_num_frame")

        self.tiempo_frame = QtWidgets.QLabel()
        self.tiempo_frame.setObjectName("status_tiempo_frame")

        self.tiempo_promedio = QtWidgets.QLabel()
        self.tiempo_promedio.setObjectName("status_tiempo_promedio")

        self.tiempo_estimado = QtWidgets.QLabel()
        self.tiempo_estimado.setObjectName("status_tiempo_estimado")

        self.tiempo_total = QtWidgets.QLabel()
        self.tiempo_total.setObjectName("status_tiempo_total")

        self.tiempo_hasta_ahora = QtWidgets.QLabel()
        self.tiempo_hasta_ahora.setObjectName("status_tiempo_hasta_ahora")

        self.error = QtWidgets.QLabel()
        self.error.setObjectName("status_error")

        self.gpu = QtWidgets.QLabel()
        self.gpu.setObjectName("status_gpu")

        self.widgets = [self.estado, self.nombre_blend, self.num_frame,
                               self.tiempo_frame, self.tiempo_promedio, self.tiempo_estimado,
                               self.tiempo_total, self.tiempo_hasta_ahora, self.error, self.gpu]

        # nuevo funcionamiento: siempre van a estar todos los widgets pero se ocultan los que no se usan.

        self.widgets_renderizando = [self.num_frame, self.tiempo_frame,
                                     self.tiempo_promedio, self.tiempo_estimado, self.tiempo_hasta_ahora, self.gpu]

        self.widgets_item_inactivo = [self.nombre_blend, self.num_frame,
                                             self.tiempo_promedio, self.tiempo_total, self.error, self.gpu]

        self.separadores = {}

        self.statusbar.addWidget(self.num_blends) # a este lo agrego por separado porque no lleva separador y está siempre presente como la 12
        self.actualizar_widgets_poblar(self.widgets)

        self.widgets_all = set(self.widgets)
        self.widgets_all.add(self.num_blends)


        # fuente_status = QtGui.QFont()
        # fuente_status.setPointSize(9)
        # fuente_status.setWeight(40)
        # self.statusbar.setFont(fuente_status)
        self.ventana.setStatusBar(self.statusbar)

    def actualizar_numero_blends(self, num_items=None):
        if num_items is None:
            num_items = self.ventana.tablaPrincipal.topLevelItemCount()

        if num_items == 0:
            self.cola_vacia()
            self.cola.estado = "vacia"
            return

        if self.cola.estado == "renderizando":
            self.cola.calcular_total_a_renderizar()
            self.actualizar_estado()
        else:
            self.cola.estado = "no_iniciada"
            self.estado.setText(self.traduccion.traducir(self.cola.estado))

        self.num_blends.setText(" " +
                                str(num_items) + " " + self.traduccion.traducir(
            "tareas") + " " + self.traduccion.traducir("en cola"))

        self.actualizar_visibilidad_widgets()

    def cola_vacia(self):
        self.num_blends.setText(" " + self.traduccion.traducir("vacia"))
        self.estado.setText("")
        self.actualizar_vaciar_widgets(self.widgets_item_inactivo)
        self.actualizar_visibilidad_widgets()

    def agregar_separador(self, nombre):
        linea = QtWidgets.QFrame()
        linea.setFrameShape(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Raised)
        self.separadores[nombre] = linea
        self.statusbar.addWidget(linea)

    def quitar_separador(self, nombre):
        if nombre in self.separadores:
            self.separadores[nombre].hide()

    def actualizar_widgets_poblar(self, widgets):
        for widget in widgets:
            self.agregar_separador(widget.objectName())
            self.statusbar.addWidget(widget)
            # widget.setMaximumWidth(200)
            widget.setMinimumWidth(50)
            widget.hide()

    def cambio_item_reporta_frames(self, item_nuevo):
        try:
            self.item_reportante.render.data.reportar = False
        except AttributeError as e:
            # print(e)
            pass
        self.item_reportante = item_nuevo
        try:
            item_nuevo.render.data.reportar = True
        except AttributeError as e:
            # print(e)
            pass

    def unico_elegido(self, item):
        self.cambio_item_reporta_frames(item)
        self.nombre_blend.setText(os.path.splitext(item.nombre_blend)[0])
        self.actualizar_item_elegido()

    def ningun_elegido(self):
        item_activo = self.cola.item_renderizando
        if item_activo:
            self.cambio_item_reporta_frames(item_activo)
            return
        self.cambio_item_reporta_frames(None)

    def varios_elegidos(self):
        self.cambio_item_reporta_frames(None)

    def actualizar_item_elegido(self):
        self.actualizar_vaciar_widgets(
            set(self.widgets_item_inactivo) | set(self.widgets_renderizando))
        if not self.ventana.item_unico_elegido():
            return
        item = self.ventana.item_unico_elegido()
        if item.estado == "renderizando":
            self.actualizar_renderizando(item, str(item.render.data.frame_anterior), item.render.data.renderizados)
        else:
            self.actualizar_item_inactivo(item)

    def actualizar_estimado_restante(self, item):
        estimado = item.render.estimado_restante()
        if estimado:
            self.tiempo_estimado.setText(self.traduccion.traducir("Tiempo estimado restante: ") + estimado)

    def actualizar_renderizando(self, item, frame_abs, frame_rel):

        promedio = item.render.promedio_tiempo(omitir_primero=True)
        if promedio:
            self.tiempo_promedio.setText(self.traduccion.traducir("Promedio: ") + promedio)
        if item.frames_renderizar_parcial:
            self.actualizar_estimado_restante(item)

        try:
            self.tiempo_frame.setText(self.traduccion.traducir("Last") + ": " + item.render.tiempo_por_frame[-1])
        except IndexError:
            pass

        self.tiempo_hasta_ahora.setText(self.traduccion.traducir("Tiempo") + ": " + item.render.tiempo_hasta_ahora())

        if frame_abs == "-1":
            frame_abs = ""
        self.num_frame.setText(self.traduccion.traducir("Frame") + ": " + frame_abs + "  (" + str(
            frame_rel) + "/" + str(item.frames_renderizar_parcial) + ")")

        self.gpu.setText("")
        if item.render.gpus and "INCIERTO" not in item.render.gpus:
            self.gpu.setText(", ".join(item.render.gpus))

        self.actualizar_visibilidad_widgets()

    def actualizar_item_inactivo(self, item):
        self.nombre_blend.setText(os.path.splitext(item.nombre_blend)[0])

        try:
            self.error.setText(item.render.error_final)
        except AttributeError as e:
            pass

        if item.renderizados:
            self.num_frame.setText(self.traduccion.traducir("frames renderizados") + ": " + str(
                item.renderizados))
        else:
            self.actualizar_visibilidad_widgets()
            return

        self.gpu.setText("")
        if item.render:

            promedio = item.render.promedio_final
            if promedio:
                self.tiempo_promedio.setText(self.traduccion.traducir("Promedio: ") + promedio)
            tiempo_total = item.render.tiempo_total
            if tiempo_total:
                self.tiempo_total.setText(self.traduccion.traducir("Tiempo") + ": " + tiempo_total)
            if item.render.gpus and "INCIERTO" not in item.render.gpus:
                self.gpu.setText(", ".join(item.render.gpus))




        self.actualizar_visibilidad_widgets()

    def actualizar_visibilidad_widgets(self):
        for widget in self.widgets:
            if widget.text():
                widget.show()
                self.separadores[widget.objectName()].show()
            else:
                widget.hide()
                self.separadores[widget.objectName()].hide()

    def vaciar_individual(self):
        self.actualizar_vaciar_widgets(
            set(self.widgets_item_inactivo) | set(self.widgets_renderizando))

    def actualizar_vaciar_widgets(self, widgets):
        for widget in widgets:
            widget.setText('')
        self.actualizar_visibilidad_widgets()
        
    def actualizar_estado(self):
        partes_estado = [self.traduccion.traducir(self.cola.estado)]
        if self.cola.estado == "renderizando":
            blends_renderizando = []
            for i in range(self.cola.num_activos):
                blends_renderizando.append(str(self.cola.renderizados_tanda + i + 1))

            partes_estado.append(', '.join(blends_renderizando))
            partes_estado.append(" / " + str(self.cola.num_blends_a_renderizar))

        elif self.cola.estado in ["detenida", "finalizada"]:
            partes_estado.append(str(self.cola.renderizados_tanda))
            partes_estado.append(" jobs " + self.traduccion.traducir("procesados"))
            if self.cola.tiempo_total():
                partes_estado.append(
                    ". " + self.traduccion.traducir("Tiempo total de renderizado") + ": " + self.cola.tiempo_total())

        self.estado.setText(''.join(partes_estado))
        self.estado.adjustSize()
