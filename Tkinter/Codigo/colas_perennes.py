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
import os
import shutil
from inspect import signature
from pathlib import Path

from PyQt5 import QtCore
from PyQt5.QtCore import QTime

import alertas
import autonombrado
import bleuristicas
import datas
from utils import renombrar_duplicado
import blenders
import app_context
from bleuristicas import DialogoBlendNoEncontrado
from items_cola import ItemCola

class ColasPerennes:
    max = 100
    nombre_default = "Default"

    def __init__(self):
        self.dialogo_blend_no_encontrado = None
        self.ventana = None

        self.lista = []
        self._alias = {}
        self.wgt_colas = None

        self.rutas_externas = {}


    def inicializar(self):
        self.lectura_lista_colas()
        if not self.lista:
            self.add_queue(self.nombre_default)

    @property
    def ruta_log(self):
        return self.path_real(sufijo="_RendersLog", extension=".txt")

    def loguear(self, texto):
        try:
            with open(self.ruta_log, "a+", encoding='utf-8') as archihvo_log_escritura:
                archihvo_log_escritura.write(texto)
        except IOError:
            pass

    def ruta_adjunto_cola(self, archivo="", sufijo=""):
        if archivo:
            ruta, nombre = os.path.split(archivo)
            nombre = os.path.splitext(nombre)[0]
            dato = [nombre, ruta]
        else:
            dato = None
        return self.path_real(nombre=dato, sufijo="_" + sufijo)

    @property
    def actual(self):
        return self.lista[-1]

    def alias(self, nombre):
        return nombre if nombre not in self._alias else self._alias[nombre]

    def set_alias(self, nombre, alias):
        self._alias[nombre] = alias
        self.actualizar_lista()

    @property
    def lista_alias(self):
        return [nombre if nombre not in self._alias else self._alias[nombre] for nombre in self.lista]

    def path_real(self, nombre=None, sufijo="", extension=".json"):
        if not nombre:
            nombre = self.lista[-1]

        if nombre in self.rutas_externas:
            ruta_base = self.rutas_externas[nombre]
        else:
            ruta_base = datas.ruta_base_colas

        return os.path.join(ruta_base, nombre + sufijo + extension)

    def renombrar_duplicado(self, nombre, ):
        return renombrar_duplicado(nombre, self.lista_alias)

    def add_queue(self, nombre, path=None):  # nombre redundante pero add solo tiene sus dificultades con el editor.

        if nombre in self.lista_alias:
            nombre = self.renombrar_duplicado(nombre)
        self.lista.append(nombre)
        self.crear_carpeta_livelogs(nombre_cola=nombre)

        if path:
            self.rutas_externas[nombre] = path
        if len(self.lista) > self.max:
            if self.lista[0] == self.nombre_default:
                nombre_olvidado = self.lista[1]
                self.lista[1] = self.lista[0]  # siempre conservar la queue default
            else:
                nombre_olvidado = self.lista[0]
            self.borrar_carpeta_livelogs(nombre_olvidado)
            self.lista = self.lista[1:]
        if self.ventana:  # para que no crashee al cerrar
            self.ventana.actualizar_selector_colas()
        self.guardado_lista_colas()

    # def set_alias(self, nombre, alias):
    #     self._original[alias] = nombre
    #
    # def original(self, alias):
    #     return alias if alias not in self._original else self._original[alias]

    def quitar(self, nombre):
        if nombre in self.lista:
            self.lista.remove(nombre)
        self.borrar_carpeta_livelogs(nombre_cola=nombre)

    def actualizar_current(self, indice):
        self.lista.append(self.lista.pop(indice))
        self.guardado_lista_colas()

    def cambiar(self, cola_elegida):
        indice = self.lista.index(cola_elegida)
        self.actualizar_current(indice)
        self.abrir()

    def abrir_externa(self, archivo, ruta_original=False, switchear=True):
        if archivo.endswith(".json"):
            if not self.lectura_de_cola(archivo):
                return False
        elif not self.lectura_cola_legacy(archivo):
            return False

        path, nombre = os.path.split(archivo)

        if path == datas.ruta_base_colas:  # or ruta_original: Antes incorporaba las externas a recientes pero ahora no. Ruta original se volvió inutil, pero lo dejo de momento por si revierto.
            path = ""

        nombre = os.path.splitext(nombre)[0]  # quitar .json
        if switchear:
            self.add_queue(nombre, path)
        app_context.watch_folders.leer()
        self.ventana.cambio_items_actualizar()
        return True

    def abrir(self):
        self.lectura_de_cola(self.path_real())
        app_context.cola.tareas = Tareas.leer_si_existe()
        app_context.watch_folders.leer()
        self.ventana.cambio_items_actualizar()

    def abrir_interna_no_listada(self, nombre):
        path = self.path_real(nombre)
        self.abrir_externa(path, switchear=True)

    def guardar(self):
        self.guardado_lista_colas()  # esto solo hace falta por si renombró alguna y hay que renombrar archivo
        self.guardado_de_cola(self.path_real())

    def duplicar_archivo(self, nombre_duplicada):
        path = self.path_real(nombre_duplicada)
        self.guardado_de_cola(path)

    def lectura_de_cola(self, archivo_cola):
        ids_start_time = dict()
        try:
            hubo_errores = False
            with open(archivo_cola, "r", encoding="utf-8-sig") as cola_leida:
                for json_item_i in cola_leida:
                    item_i = ItemCola.de_json(json_item_i)

                    if item_i.modo not in app_context.modos.modo:
                        hubo_errores = True
                        continue
                    if not item_i.desactivado:
                        blend_existe = self.ventana.verificar_existencia_blends(item_i)
                        if blend_existe == "continuar":
                            continue
                        elif blend_existe == "salir":
                            return False

                    if item_i.estado == "renderizando":
                        item_i.estado = "interrumpido"

                    # datos_item_i.args_extra = datos_item_i.args_extra.strip()
                    item_i.agregar()
                    # self.ventana.actualizar_lista_estado()
                    if item_i.id_start_time and item_i.id_start_time in ids_start_time:
                        ids_start_time[item_i.id_start_time].append(item_i)
                    else:
                        ids_start_time.setdefault(item_i.id_start_time, []).append(item_i)

                for lista_items in ids_start_time.values():
                    for item in lista_items[1:]:
                        item.link_start_time(lista_items[0])

                self.crear_carpeta_livelogs(nombre_cola=Path(archivo_cola).stem)
                return True

        except Exception as e:
            print("exception", e, type(e))
            return False

    def lectura_cola_legacy(self, archivo_cola):
        try:
            with open(archivo_cola, "r", encoding="utf-8-sig") as cola_leida:
                lineas_vacias = 0
                while True:
                    hubo_errores = False
                    item_i = ItemCola(self.ventana)
                    tag_i = ""
                    ruta_blalt_i = ""
                    tag_blend = ""
                    for n in range(len(ItemCola.variables_exportables)):
                        linea_n = cola_leida.readline()
                        if linea_n.strip() == '':
                            lineas_vacias += 1
                            break
                        else:
                            lineas_vacias = 0
                        try:
                            nombre_dato_n, dato_n = linea_n.split(' ', 1)
                        except Exception as e:
                            continue
                        dato_n = dato_n.strip()
                        if nombre_dato_n == 'dispositivos':
                            dispositivos = dato_n.strip("][").split(', ')
                            dispositivos = [disp.strip("'") for disp in dispositivos]
                            if dispositivos:
                                item_i.__dict__[nombre_dato_n] = dispositivos
                        elif nombre_dato_n == 'patron_nombrado':
                            partes_patron = dato_n.strip("][").split(', ')
                            partes_patron = [parte.strip("'") for parte in partes_patron]
                            if partes_patron:
                                item_i.__dict__[nombre_dato_n] = partes_patron
                        elif nombre_dato_n == "tag_blender":  # este se maneja aparte porque la ruta se guarda pero no es propiedad del item
                            tag_i, ruta_blalt_i = dato_n.split(datas.separador_blTag)
                            item_i.tag_blender = tag_i
                        elif nombre_dato_n == "propiedades_argumentar":
                            propiedades = dato_n.strip("}{").split(', ')
                            propiedades = {prop.strip("'") for prop in propiedades}
                            item_i.__dict__[nombre_dato_n] = propiedades
                        elif nombre_dato_n == "modo":  # esto es una corrección para no hacerle cambiar al de shot manager
                            if dato_n == "Animación":
                                dato_n = "modo_animacion"
                            elif dato_n == "Frames":
                                dato_n = "modo_frames"
                            setattr(item_i, nombre_dato_n, dato_n)
                        else:
                            if nombre_dato_n == "renderizados":
                                dato_n = int(dato_n)
                            item_i.__dict__[nombre_dato_n] = dato_n

                    if lineas_vacias == 1 and n == 0:
                        continue

                    if lineas_vacias == 2:
                        break

                    if item_i.modo in self.ventana.modo:  # esta es la única variable esencial aparte de ruta y nombre
                        if not bleuristicas.blend_existe(item_i.ruta_blend, item_i.nombre_blend):
                            correccion_automatica = ""
                            if self.dialogo_blend_no_encontrado is None:
                                self.dialogo_blend_no_encontrado = DialogoBlendNoEncontrado(self, item_i)
                            else:
                                correccion_automatica = self.dialogo_blend_no_encontrado.actualizar(item_i)
                                if correccion_automatica:
                                    item_i.ruta_blend = correccion_automatica

                            if not correccion_automatica:
                                self.dialogo_blend_no_encontrado.exec_()
                                if self.dialogo_blend_no_encontrado.accion == "CANCELAR":
                                    return
                                elif self.dialogo_blend_no_encontrado.accion == "OMITIR":
                                    self.dialogo_blend_no_encontrado.accion = None
                                    continue

                        pedir_ruta_bl_alt = False
                        if tag_i:
                            if tag_i not in app_context.versiones_blender.blenders:
                                if not blenders.ruta_es_valida(ruta_blalt_i):
                                    pedir_ruta_bl_alt = True
                                app_context.versiones_blender.agregar(tag_i, ruta_blalt_i, "")

                            item_i.tag_blender = tag_i

                        self.ventana.tablaPrincipal.addTopLevelItem(item_i)

                        if pedir_ruta_bl_alt:
                            blenders.alerta_ubicacion_erronea()
                            self.ventana.tablaPrincipal.clearSelection()
                            ultimo_item = self.ventana.tablaPrincipal.topLevelItem(
                                self.ventana.tablaPrincipal.topLevelItemCount() - 1)
                            if ultimo_item:
                                ultimo_item.setSelected(True)
                            self.ventana.cambiar_blender()

                    else:
                        hubo_errores = True

            if hubo_errores:  # esta mecánica es para hacer una sola alerta y no muchas si hay varios archivos que fallan
                alertas.alerta_generica("alerta no encontrados")
            return True

        except Exception as E:
            print(E)
            alertas.alerta_generica("error general lectura")
            return False

    def guardado_de_cola(self, archivo_cola):
        try:
            with open(archivo_cola, "w", encoding="utf8") as archivo_guardando:
                items = self.ventana.tablaPrincipal.topLevelItemCount()
                for n in range(items):
                    item_n = self.ventana.tablaPrincipal.topLevelItem(n)
                    archivo_guardando.write(item_n.a_json() + "\n")

        except IOError as e:
            pass

    def lectura_lista_colas(self):
        try:
            with open(datas.ruta_archivo_lista_colas, "r", encoding="utf-8-sig") as lista_colas:
                data_colas = json.load(lista_colas)
                self.lista = data_colas["list"]
                self.rutas_externas = data_colas["external_paths"]
        except Exception as e:
            print(e)
            return

    def actualizar_lista(self):
        self.lista = [nombre for nombre in self.lista_alias]

    def guardado_lista_colas(self):

        for nombre, alias in self._alias.items():
            ruta_actual = self.path_real(nombre)
            ruta_nueva = self.path_real(alias)
            try:
                os.rename(ruta_actual, ruta_nueva)
            except FileExistsError:
                os.remove(ruta_nueva)
                os.rename(ruta_actual, ruta_nueva)
            except FileNotFoundError:
                pass

        self.actualizar_lista()

        with open(datas.ruta_archivo_lista_colas, "w", encoding="utf-8-sig") as lista_colas:
            lista_colas.write(json.dumps({"list": self.lista, "external_paths": self.rutas_externas}))

    def path_livelogs(self, nombre_cola=None):
        if nombre_cola is None:
            nombre_cola = self.actual
        return os.path.join(datas.ruta_base_livelogs, nombre_cola)

    def crear_carpeta_livelogs(self, nombre_cola=None):
        os.makedirs(self.path_livelogs(nombre_cola=nombre_cola), exist_ok=True)

    def borrar_carpeta_livelogs(self, nombre_cola=None):
        try:
            shutil.rmtree(self.path_livelogs(nombre_cola=nombre_cola))
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}.")


class Tarea:
    def __init__(self, ruta, args, tokens, item=None):
        self.proceso = QtCore.QProcess()
        self.proceso.setProgram(ruta)
        lista_args = self.parsear_args(args)
        lista_args = self.reemplazar_tokens(lista_args, tokens, item)
        self.proceso.setArguments(lista_args)
        self.proceso.startDetached()

    @staticmethod
    def parsear_args(args):
        args_parseados = []
        for linea in args.splitlines():
            args_parseados.extend(linea.split(" ", 1))
        return args_parseados

    @staticmethod
    def reemplazar_tokens(lista_args, tokens, item=None):
        lista_final = []
        for arg in lista_args:
            for token in tokens:
                if token.patron in arg:
                    if not token.funcion_valor:
                        continue
                    if "item" in signature(token.funcion_valor).parameters:
                        reemplazo = token.funcion_valor(item)
                    else:
                        reemplazo = token.funcion_valor()

                    arg = arg.replace(token.patron, reemplazo)
            lista_final.append(arg)
        return lista_final


class Tareas:
    exportables = ["usar_aj", "ruta_aj", "args_aj", "usar_aq", "ruta_aq", "args_aq"]

    def __init__(self):
        self.token_blend_path = autonombrado.TokenNombrado("Blend path", "[BLEND_PATH]",
                                              funcion_valor=lambda item: item.ruta_blend_completa)
        self.token_time = autonombrado.TokenNombrado("Time", "[TIME]", funcion_valor=lambda: QTime.currentTime().toString("hh_mm"))
        self.token_queue_name = autonombrado.TokenNombrado("Queue name", "[QUEUE_NAME]", funcion_valor=lambda: colas.actual)
        self.job_tokens = [self.token_blend_path, self.token_time]
        self.queue_tokens = [self.token_queue_name, self.token_time]
        self.usar_aj = None
        self.usar_aq = None
        self.ruta_aj = None
        self.args_aj = None
        self.ruta_aq = None
        self.args_aq = None
        self.defaults()

    def defaults(self):
        self.usar_aj = False
        self.usar_aq = False
        self.ruta_aj = ""
        self.args_aj = ""
        self.ruta_aq = ""
        self.args_aq = ""

        # guardamos los args como un texto, el parseo se hace en runtime para aplicar nomás.

    def dict_data(self):
        return {exp: getattr(self, exp) for exp in self.exportables}

    def guardar(self, archivo_cola=""):
        data_json = json.dumps(self.dict_data())
        try:
            with open(colas.ruta_adjunto_cola(archivo_cola, sufijo="Tasks"), "w",
                      encoding="utf8") as archivo_tasks:
                archivo_tasks.write(data_json)
        except:
            pass

    def leer(self):
        try:
            with open(colas.ruta_adjunto_cola(sufijo="Tasks"), "r", encoding="utf8") as data_tareas:
                data_leida = json.loads(data_tareas.read())
                for nombre_dato in data_leida:
                    setattr(self, nombre_dato, data_leida[nombre_dato])
        except Exception as e:
            self.defaults()

    @staticmethod
    def leer_si_existe():
        if os.path.isfile(colas.ruta_adjunto_cola(sufijo="Tasks")):
            tareas = Tareas()
            tareas.leer()
            return tareas
        return None


colas = ColasPerennes()
