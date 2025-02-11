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

from traducciones import traducir
from utils import UnDefaultDict
import datas


class ModoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Modo):
            return obj.__dict__  # Serialize the __dict__ attribute of the Modo instance
        return super().default(obj)


class Modo:
    def __init__(self, nombre="", background=True, tipo="animacion", usar_arg_tipo=True, frames_predefinidos="",
                 dispositivos=None, motor_dispositivos=None,
                 parallel_gpu=False, auto_duplicar=False,
                 overwrite_placeholders=False, args_extra="", pedir_script=False, atajo=None, patron_nombrado=None,
                 version_blender="Default", **kwargs):
        self.tipo = tipo
        self.usar_arg_tipo = usar_arg_tipo
        self.background = background
        self.nombre = nombre
        self.frames_predefinidos = frames_predefinidos
        self.dispositivos = dispositivos
        self.motor_dispositivos = motor_dispositivos
        self.parallel_gpu = parallel_gpu
        self.auto_duplicar = auto_duplicar
        self.overwrite_placeholders = overwrite_placeholders
        self.args_extra = args_extra
        self.pedir_script = pedir_script
        self.patron_nombrado = patron_nombrado
        self.atajo = atajo
        self.version_blender = version_blender
        if kwargs:
            print("Unused parameters", kwargs) # debug print


class ManagementModos:
    args_tipo = {"animacion": "-a", "frames": "-f"}
    traducibles = {"modo_animacion", "modo_frames", "modo_script"}

    def __init__(self):
        self.modo = UnDefaultDict(default=self.default)
        self.modo.update({"actual": "modo_animacion"})
        self.builtin = {}

    def default(self, nombre_modo):
        if not self.builtin:
            self.crear_builtins()
        if nombre_modo in self.builtin:
            return self.builtin[nombre_modo]
        else:
            return self.builtin["modo_animacion"]

    # @property
    # def modo(self):
    #     return self._modo()

    def guardar_modos(self):
        data = json.dumps(self.modo, cls=ModoEncoder, indent=4)
        try:
            with open(datas.ruta_modos, "w") as json_modos:
                json_modos.write(data)
        except IOError:
            return False
        return True

    def exportar_modo(self, path):
        nombre_modo_actual = self.modo['actual']
        data = json.dumps({nombre_modo_actual: self.modo[nombre_modo_actual]}, cls=ModoEncoder, indent=4)
        try:
            with open(path, "w") as json_modos:
                json_modos.write(data)
        except IOError:
            pass

    def leer_modos(self, ruta=None, reemplazar=True):
        if not ruta:
            ruta = datas.ruta_modos
        try:
            with open(ruta, "r") as json_modos:
                data_modos = json.load(json_modos)
                modos_nuevos = UnDefaultDict(default=self.default)
                modos_nuevos.update({nombre: Modo(**data) if nombre != "actual" else data for nombre, data in
                                     data_modos.items()})
                if reemplazar:
                    self.modo = modos_nuevos
                else:
                    self.modo.update(modos_nuevos)
                    self.set_actual(list(modos_nuevos)[0])
        except (IOError, AttributeError, json.decoder.JSONDecodeError, TypeError) as e:
            print("Error reading modes file. ", e)
            return False

        return True

    @property
    def actual(self):
        return self.modo["actual"]

    @classmethod
    def traducir(cls, nombre):
        for traducible in cls.traducibles:
            traducido = traducir(traducible)
            if nombre == traducido:
                nombre += " (2)"
            if nombre == traducible:
                return traducido
        return nombre

    def set_actual(self, nombre_actual):
        self.modo["actual"] = nombre_actual

    @property
    def lista_modos(self):
        lista = [nombre for nombre in self.modo if nombre != "actual"]
        return lista

    def crear_builtins(self):
        modo_animacion = Modo(nombre="modo_animacion", tipo="animacion", atajo="Ctrl+Alt+A")
        modo_frames = Modo(nombre="modo_frames", tipo="frames", atajo="Ctrl+Alt+F")
        modo_script = Modo(nombre="modo_script", tipo="animacion", usar_arg_tipo=False, pedir_script=True)
        modo_parallel = Modo(nombre="Parallel GPU (Anim)", tipo="animacion", dispositivos={"tipo": "ask"},
                             parallel_gpu=True,
                             auto_duplicar=True, overwrite_placeholders=True)
        modo_viewport = Modo(nombre="Viewport Animation", background=False, tipo="animacion", usar_arg_tipo=False,
                             args_extra="--python-expr import bpy; bpy.ops.render.opengl(animation=True); bpy.ops.wm.quit_blender()")
        for modo in (modo_animacion, modo_frames, modo_script, modo_parallel, modo_viewport):
            self.builtin.update({modo.nombre: modo})

    def crear_defaults(self):
        self.crear_builtins()
        self.modo.update(self.builtin)


modos = ManagementModos()
