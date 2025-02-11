from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QWidget, QApplication, QHBoxLayout, QSpacerItem, QVBoxLayout, QFrame, QMenu
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve, QEvent, pyqtSignal, QTimer
from traducciones import traducir
import iconos_app as iconos
from configuracion_general import configuracion


def get_parte_patron(tokenzone):
    parte_patron = []
    for widget, _ in tokenzone.widgets():
        text = getattr(widget, "text", None)
        if not text:
            continue
        if hasattr(widget, "key"):  # tokens incrementales
            parte_patron.append([text, widget.key])
        else:
            parte_patron.append(text)
    return parte_patron


class TokenZone(QWidget):
    cambio = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # Create a layout for the overall widget
        self.flag_renovador = False
        self.wgt_desplazado = None
        self.layout_supra = QVBoxLayout(self)
        self.frame = QFrame(self)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.btn_borrar = None

        palette = self.palette()
        field_color = palette.color(QtGui.QPalette.Base).name()
        border_color = "gray" # palette.color(QtGui.QPalette.Window).name()


        self.frame.setStyleSheet(f"""
                QFrame#FrameTokenZone {{ 
                background-color: {field_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 0px;
                }}
            """)
        self.frame.setObjectName("FrameTokenZone")

        self.layout_supra.addWidget(self.frame)
        self.layout_supra.setContentsMargins(0, 2, 0, 2)

        # Inside the frame, create layout_principal for the widgets to be added to
        self.layout_principal = QHBoxLayout(self.frame)
        self.layout_principal.addSpacerItem(
            QSpacerItem(5, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))

        self.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("TokenZoneWgt")
        self.setStyleSheet("""
                QWidget#TokenZoneWgt { 
                background-color: red;
                padding: 0px;
                }
            """)
        self.layout_principal.setContentsMargins(4, 3, 4, 3)
        self.layout_principal.setSpacing(4)
        self.frame.setContentsMargins(0, 0, 0, 0)

        self.current_hovered_index = None
        self.animations = []

        self.contextual = self.definir_contextual()
        # self.agregar_editable("bochorni")

    def definir_contextual(self):
        contextual = QMenu()
        contextual.addAction(traducir("Limpiar"))
        contextual.triggered.connect(self.clear)
        self.frame.setContextMenuPolicy(Qt.CustomContextMenu)
        self.frame.customContextMenuRequested.connect(self.mostrar_contextual)
        return contextual

    def mostrar_contextual(self, posicion):
        if self.childAt(posicion) == self.frame:
            self.contextual.popup(self.frame.mapToGlobal(posicion))

    def clear(self):
        while self.layout_principal.count() > 1:  # no borrar el spacer
            item = self.layout_principal.takeAt(0)  # Take the first item
            widget = item.widget()  # Get the widget
            if widget:  # If there's a widget, delete it
                widget.deleteLater()
        self.frame.update()
        self.cambio.emit()

    def widgets(self):
        for i in range(self.layout_principal.count() - 1):
            yield self.layout_principal.itemAt(i).widget(), i

    def dragLeaveEvent(self, a0):
        self.clear_animations()
        # self.flag_renovador = True

    def clear_animations(self):

        for anim in self.animations:
            anim.stop()  # Stop any running animations
        self.animations.clear()  # Clear the animations list
        self.layout_principal.invalidate()
        self.current_hovered_index = None

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        wgt = event.source()
        drop_position = event.pos()
        dragged_index = self.layout_principal.indexOf(wgt)
        insert_position = self.getInsertionIndex(drop_position)

        if hasattr(wgt, "aplicado"):
            wgt.setVisible(False)
            # wgt.hide()

        # print("ip", insert_position, "di", dragged_index, "chi", self.current_hovered_index)

        if insert_position != self.current_hovered_index:
            self.clear_animations()
            if not self.flag_renovador and (insert_position == dragged_index or insert_position - 1 == dragged_index):
                return
            self.flag_renovador = not self.flag_renovador
            self.current_hovered_index = insert_position
            QTimer.singleShot(0, lambda: self.animatePreview(insert_position, wgt))

        # event.accept()

    def dropEvent(self, event):
        drop_position = event.pos()
        dragged_text = event.mimeData().text()

        source = event.source()

        if isinstance(source, WidgetTokenAplicado) or isinstance(source, WidgetTokenAplicadoEditable):
            # Reorder the widget and reset hover state
            self.reordenar_token(event.source(), drop_position)
        elif isinstance(source, WidgetTokenIncremental):
            self.agregar_incremental_de_widget(source, drop_position)
        else:
            default_editable = getattr(source.token, "default_editable", None)
            if default_editable:
                self.agregar_editable(default_editable, drop_position)
            else:
                self.agregar_comun_de_widget(source, drop_position)
        self.cambio.emit()
        self.current_hovered_index = None
        event.accept()

    def getInsertionIndex(self, drop_position):
        for widget, i in self.widgets():
            widget_midpoint = widget.geometry().center().x()
            # respect_delta = int(widget.geometry().width() / 4)
            if widget_midpoint > drop_position.x():  # + respect_delta:
                return i
        return self.layout_principal.count() - 1

    def animatePreview(self, insert_position, wgt_desplazado):
        desplazamiento = wgt_desplazado.geometry().width() + 10

        for i in range(insert_position, self.layout_principal.count() - 1, 1):
            item = self.layout_principal.itemAt(i)
            widget = item.widget()

            if widget is None:
                continue
            # Create a new animation for each widget
            animation = QPropertyAnimation(widget, b"geometry")
            animation.setDuration(200)
            animation.setEasingCurve(QEasingCurve.OutQuad)

            widget_rect = widget.geometry()

            new_rect = QRect(widget_rect.x() + desplazamiento, widget_rect.y(),
                             widget_rect.width(), widget_rect.height())

            animation.setStartValue(widget.geometry())
            animation.setEndValue(new_rect)

            # Start the animation
            animation.start()
            self.animations.append(animation)

    def enterEvent(self, event):
        self.setCursor(QtCore.Qt.IBeamCursor)
        super().enterEvent(event)

    def mousePressEvent(self, event):
        # Check if there's a child widget at the click position
        posicion = event.pos()
        clicked_child = self.childAt(posicion)
        if event.button() == QtCore.Qt.LeftButton and clicked_child == self.frame:
            editable = self.agregar_editable("", posicion)
            editable.setFocus()
        if clicked_child is None:
            pass  # Clicked on empty space
        else:
            pass
            # Clicked on a child widget

        super().mousePressEvent(event)

        # super(TokenZone, self).mousePressEvent(event)

    def insersion_token(self, btn, posicion=None):


        btn.set_token_zone(self)
        index = self.getInsertionIndex(posicion) if posicion else self.layout_principal.count() - 1
        self.layout_principal.insertWidget(index, btn)
        max_height = btn.height()
        for widget, _ in self.widgets():
            widget_height = widget.height()
            max_height = max(max_height, widget_height)

        for widget, _ in self.widgets():
            widget.setFixedHeight(max_height)

    def reordenar_token(self, widget, posicion):
        self.layout_principal.removeWidget(widget)
        widget.set_token_zone(self)

        insert_position = self.getInsertionIndex(posicion)
        self.layout_principal.insertWidget(insert_position, widget)

    def agregar_comun_de_widget(self, widget_token, posicion):
        btn = WidgetTokenAplicado(widget_token.token, self)
        self.insersion_token(btn, posicion)

    def agregar_comun_de_token(self, token):
        btn = WidgetTokenAplicado(token, self)
        self.insersion_token(btn)

    def agregar_editable(self, texto, posicion=None, token=None):
        btn = WidgetTokenAplicadoEditable(texto, self, token)
        self.insersion_token(btn, posicion)
        return btn

    def agregar_incremental_de_token(self, token, key):
        btn = WidgetTokenAplicadoIncremental(token, key, self)
        self.insersion_token(btn)

    def agregar_incremental_de_widget(self, widget_token, posicion):
        if not hasattr(widget_token, "keys"):
            return
        if QApplication.keyboardModifiers() == Qt.ShiftModifier:
            key = widget_token.siguiente_key()
        elif QApplication.keyboardModifiers() == Qt.AltModifier:
            if widget_token.keys_alternativas:
                key = widget_token.siguiente_key_alternativa()
            else:
                key = ""
        else:
            widget_token.resetear_keys()
            key = widget_token.siguiente_key()

        btn = WidgetTokenAplicadoIncremental(widget_token.token, key, self)
        self.insersion_token(btn, posicion)

    def set_boton_borrar(self, btn):
        self.btn_borrar = btn
        self.btn_borrar.signal_cambio = self.cambio
        self.ocultar_boton_borrar()

    def mostrar_boton_borrar(self, pos):
        if not self.btn_borrar:
            return

        x_boton = pos - int(self.btn_borrar.width() / 2)
        y_boton = self.btn_borrar.pos().y()

        self.btn_borrar.setVisible(True)
        self.btn_borrar.move(x_boton, y_boton)

    def ocultar_boton_borrar(self):
        self.btn_borrar.setVisible(False)

    def text(self):
        return "".join([wgt.text for wgt, _ in self.widgets()])


class BotonBorrador(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._pixmap_resaltado = None
        self._pixmap_normal = None
        self.reset_pixmap()
        self.setAlignment(Qt.AlignCenter)
        self.signal_cambio = None
        # self.setStyleSheet("padding: 0; margin: 0; background-color: red;")

    def reset_pixmap(self):
        lado = int(18 * configuracion.factor_icons_size / 100)
        if not self._pixmap_normal:
            self._pixmap_normal = iconos.icono_quitar_elegidos.pixmap(lado, lado)
        self.setPixmap(self._pixmap_normal)
        self.setFixedSize(lado, lado)

    def set_pixmap_resaltado(self):
        if not self._pixmap_resaltado:
            self._pixmap_resaltado = QtGui.QPixmap(self.pixmap())
            iconos.colorizar_icono(self._pixmap_resaltado, Qt.red)
        self.setPixmap(self._pixmap_resaltado)

    def dragEnterEvent(self, event):
        if hasattr(event.source(), "aplicado"):
            self.set_pixmap_resaltado()
            event.accept()  #

    def dragLeaveEvent(self, event):
        self.reset_pixmap()
        event.accept()

    def dropEvent(self, event):
        wgt = event.source()
        wgt.deleteLater()
        self.reset_pixmap()
        self.setVisible(False)
        if self.signal_cambio:
            self.signal_cambio.emit()
        event.accept()


class WidgetParte(QtWidgets.QFrame):
    def __init__(self, parent, wgt_principal=None):
        super().__init__(parent)
        self.text = ""
        self.wgt_principal = wgt_principal
        self.draggable_handle = QtWidgets.QLabel()
        self.draggable_handle.setPixmap(iconos.icono_grab.pixmap(20, 3))
        self.draggable_handle.setAlignment(QtCore.Qt.AlignCenter)
        self.aplicar_estilo()
        self.token_zone = None

    def mostrar_boton_borrar(self):
        if not self.token_zone:
            return
        pos = self.geometry().center().x()
        self.token_zone.mostrar_boton_borrar(pos)

    def ocultar_boton_borrar(self):
        if not self.token_zone:
            return
        self.token_zone.ocultar_boton_borrar()

    def set_token_zone(self, token_zone):
        if self.token_zone and self.token_zone != token_zone:
            self.ocultar_boton_borrar()
        self.token_zone = token_zone

    def mostrar_token(self, widget):
        if not widget:
            widget = QtWidgets.QLabel()
        self.wgt_principal = widget

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.draggable_handle, alignment=QtCore.Qt.AlignCenter)
        layout_contenido = QHBoxLayout()
        layout_contenido.addWidget(self.wgt_principal, alignment=QtCore.Qt.AlignCenter)
        layout_contenido.setContentsMargins(0, 2, 0, 0)
        layout_contenido.setSpacing(0)
        layout.addLayout(layout_contenido)
        self.layout_contenido = layout_contenido

        layout.setContentsMargins(3, 3, 2, 4)
        layout.setSpacing(1)

    def aplicar_estilo(self):
        palette = self.palette()
        hover_border_color = palette.color(QtGui.QPalette.Highlight).name()  # Highlight color for the border
        border_color = palette.color(QtGui.QPalette.Light).name()  # Lighter color for hover border
        button_color = palette.color(QtGui.QPalette.Button)  # Base color for background
        lighter_button_color = button_color.lighter(120).name()  # Darken by 10%
        button_color = button_color.name()
        alternate_base_color = palette.color(QtGui.QPalette.AlternateBase)  # AlternateBase color

        alternate_base_color = alternate_base_color.name()

        self.setStyleSheet(f"""
               QWidget#BotonDraggueable {{
                   border: 1px solid {lighter_button_color};
                   border-radius: 6px;
                   background: qlineargradient(
                       spread:pad, 
                       x1:0, y1:0, x2:0, y2:1, 
                       stop:0 {alternate_base_color}, stop:1 {button_color});
                   padding: 0px;
               }}
               QWidget#BotonDraggueable:hover {{
                   background: qlineargradient(
                       spread:pad, 
                       x1:0, y1:0, x2:0, y2:1, 
                       stop:0 {button_color}, stop:1 {alternate_base_color});
                   border: 2px solid {hover_border_color};
               }}
           """)

        # Assign a unique object name to the widget so the stylesheet only applies to this widget
        self.setObjectName("BotonDraggueable")

        shadow_effect = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow_effect.setBlurRadius(10)  # Change this value to adjust shadow softness
        shadow_effect.setXOffset(0)  # X offset of shadow
        shadow_effect.setYOffset(0)  # Y offset of shadow
        shadow_effect.setColor(QtGui.QColor(0, 0, 0, 100))  # Shadow color and transparency
        self.setGraphicsEffect(shadow_effect)

    def setText(self, text):
        self.text = text
        self.wgt_principal.setText(text)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            drag = QtGui.QDrag(self)
            dragMimeData = QtCore.QMimeData()
            dragMimeData.setText(self.text)

            original_pixmap = self.grab()
            transparent_pixmap = QtGui.QPixmap(original_pixmap.size())
            transparent_pixmap.fill(QtCore.Qt.transparent)

            painter = QtGui.QPainter(transparent_pixmap)
            painter.setOpacity(0.5)
            painter.drawPixmap(0, 0, original_pixmap)
            painter.end()

            drag.setPixmap(transparent_pixmap)
            drag.setMimeData(dragMimeData)

            hot_spot_x = event.pos().x()
            hot_spot_y = event.pos().y()
            drag.setHotSpot(QtCore.QPoint(hot_spot_x, hot_spot_y))

            self.setCursor(QtCore.Qt.ClosedHandCursor)

            result = drag.exec_(QtCore.Qt.MoveAction)
            self.setVisible(True)
            self.ocultar_boton_borrar()

    def enterEvent(self, event):
        self.setCursor(QtCore.Qt.OpenHandCursor)
        super().enterEvent(event)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mostrar_boton_borrar()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            if isinstance(self.parent(), TokenZone):
                self.parent().flag_renovador = False
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setCursor(QtCore.Qt.OpenHandCursor)
            self.ocultar_boton_borrar()
            # self.signals.mouse_released.emit()

        super().mouseReleaseEvent(event)
    #
    # def mousePressEvent(self, event):
    #     if isinstance(self.parent(), TokenZone):
    #         self.parent().startDrag(self)
    #     super().mousePressEvent(event)


class WidgetToken(WidgetParte):
    def __init__(self, token, parent, widget_principal=None):
        super().__init__(parent, widget_principal)
        self.wgt_principal = None
        self.token = token
        self.layout_contenido = None
        self.mostrar_token(widget_principal)
        self.rellenar_texto_token()

    def rellenar_texto_token(self):
        self.setText(self.token.nombre_visible)


class WidgetTokenIncremental(WidgetToken):
    def __init__(self, token, parent):
        super().__init__(token, parent)
        self.token = token
        self.keys = None
        self.keys_alternativas = None
        self.resetear_keys()
        self.resetear_keys_alternativas()

    def resetear_keys(self):
        self.keys = iter(self.token.keys)

    def resetear_keys_alternativas(self):
        self.keys_alternativas = iter(self.token.keys_alternativas) if self.token.keys_alternativas else None

    def siguiente_key(self):
        try:
            return next(self.keys)
        except StopIteration:
            return self.token.keys[-1]

    def siguiente_key_alternativa(self):
        try:
            return next(self.keys_alternativas)
        except StopIteration:
            return self.token.keys_alternativas[-1]


class WidgetTokenAplicado(WidgetToken):
    aplicado = True

    def __init__(self, token, parent, widget_principal=None, ajustar=True):
        super().__init__(token, parent, widget_principal)
        if ajustar:
            self.adjustSize()
            self.setFixedSize(self.size())

    def rellenar_texto_token(self):
        self.setText(self.token.patron)


class WidgetTokenAplicadoEditable(WidgetParte):
    aplicado = True

    def __init__(self, texto, parent, token=None):
        campo_texto = QtWidgets.QLineEdit()
        super().__init__(parent, campo_texto)
        self.zone = parent
        self.token = token
        # campo_texto.setFixedHeight(self.wgt_principal.sizeHint().height())
        self.setText(texto)
        # campo_texto.setContentsMargins(0,1,0,1)
        self.mostrar_token(campo_texto)
        campo_texto.setAlignment(Qt.AlignBottom)
        campo_texto.setMinimumWidth(0)
        char_height = self.fontMetrics().boundingRect("A").height()
        campo_texto.setFixedHeight(char_height + 2)
        campo_texto.setObjectName("campo_texto")
        border_color = self.palette().color(QtGui.QPalette.Window).name()
        campo_texto.setStyleSheet(
            f"QLineEdit#campo_texto {{ border: 1px solid {border_color};  border-radius: 4px; padding: 0px; }}")
        campo_texto.adjustSize()
        # self.adjustSize()
        # self.setFixedSize(self.size())
        campo_texto.setAcceptDrops(False)
        self.campo_texto = campo_texto
        self.adjust_size_to_text()
        campo_texto.textChanged.connect(self.adjust_size_to_text)
        campo_texto.textChanged.connect(self.update_text)


    def setFocus(self):
        self.campo_texto.setFocus()

    def update_text(self):
        self.text = self.campo_texto.text()
        self.zone.cambio.emit()

    def adjust_size_to_text(self):
        font_metrics = self.fontMetrics()
        texto = self.campo_texto.text() or "AAAA"

        text_width = font_metrics.horizontalAdvance(texto)

        padding = 8
        new_width = text_width + padding

        self.campo_texto.setFixedWidth(new_width)
        self.setFixedWidth(new_width + 10)


class WidgetTokenAplicadoIncremental(WidgetTokenAplicado):
    def __init__(self, token, key, parent):
        super().__init__(token, parent, ajustar=False)
        field_key = QtWidgets.QLineEdit(key)
        field_key.setMaxLength(1)

        field_key.setAlignment(Qt.AlignCenter)
        field_key.setObjectName("field_key")
        field_key.setStyleSheet("QLineEdit#field_key { border: 0px solid; padding: 0px; }")
        # field_key.setContentsMargins(0,0,0,0)
        lbl_pre = QtWidgets.QLabel("[")
        lbl_post = QtWidgets.QLabel("]")
        lbl_pre.setAlignment(Qt.AlignTop)
        lbl_post.setAlignment(Qt.AlignTop)
        self.wgt_principal.setAlignment(Qt.AlignTop)
        self.layout_contenido.addWidget(lbl_pre)
        self.layout_contenido.addWidget(field_key)
        self.layout_contenido.addWidget(lbl_post)
        self.ajustar_size(field_key)
        self.field_key = field_key
        self.adjustSize()
        self.setFixedSize(self.size())
        # field_key.setFixedHeight(lbl_pre.sizeHint().height())

    @property
    def key(self):
        return self.field_key.text()

    def ajustar_size(self, field, ):
        font_metrics = self.fontMetrics()
        char_width = font_metrics.boundingRect("A").width()
        char_height = font_metrics.boundingRect("A").height()
        field.setFixedWidth(char_width + 6)
        field.setFixedHeight(char_height - 1)


class DropEventFilter(QObject):
    enter_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

    def eventFilter(self, obj, event):
        if event.type == QEvent.Enter:
            self.enter_signal.emit()
        return super().eventFilter(obj, event)
        # if isinstance(obj, QtWidgets.QLineEdit):
        #     if event.type() == QtCore.QEvent.DragEnter:
        #         obj.setFocus()
        #         if event.mimeData().hasText():
        #             event.acceptProposedAction()
        #             return True
        #     elif event.type() == QtCore.QEvent.Drop:
        #         if event.mimeData().hasText():
        #             texto = event.mimeData().text()
        #             drag_source = event.source()
        #
        #             if hasattr(drag_source, "keys"):
        #                 if QApplication.keyboardModifiers() == Qt.ShiftModifier:
        #                     key = drag_source.siguiente_key()
        #                 elif QApplication.keyboardModifiers() == Qt.AltModifier:
        #                     if drag_source.keys_alternativas:
        #                         key = drag_source.siguiente_key_alternativa()
        #                 else:
        #                     drag_source.resetear_keys()
        #                     key = drag_source.siguiente_key()
        #
        #                 texto += patron_clave_token.format(key)
        #
        #             obj.insert(texto)
        #             event.acceptProposedAction()
        #
        #             return True
        # return False
