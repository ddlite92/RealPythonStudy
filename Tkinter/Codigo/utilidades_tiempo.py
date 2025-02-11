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

from datetime import datetime

formato_fecha = "%Y-%m-%d %H:%M:%S"
formato_sanitizado = "%Y-%m-%d_%H-%M-%S"
formato_hora = "%H:%M:%S"


def delta_formateado(hora_inicio, hora_fin):

    if not hora_inicio:
        return ""
    if not hora_fin:
        hora_fin = datetime.now()
    delta = hora_fin - hora_inicio

    return formateado(delta)

def formateado(tiempo):
    horas, resto = divmod(tiempo.total_seconds(), 3600)
    minutos, segundos = divmod(resto, 60)
    horas = int(horas)
    minutos = int(minutos)
    segundos = int(
        segundos)  # no uso round para no tener la situación de que de 60 segundos, si total qué importan las decimas
    formateado = ""
    if horas:
        formateado += str(horas) + " hrs "
        formateado += f'{minutos:02d} min '
    elif minutos:  # si no hay horas a los minutos los ponemos como vengan, 0 min, 11 min, lo que sea
        formateado += str(minutos) + " min "
    formateado += f'{segundos:02d} sec'

    return formateado

def fecha_y_hora(formato=None):
    if formato is None:
        formato = formato_fecha
    fecha = datetime.now()
    fecha = fecha.strftime(formato)
    return fecha


def fecha_hora_sanitizados():
    return fecha_y_hora(formato_sanitizado)


def hora():
    return fecha_y_hora(formato_hora)


def recomposicion_partes_tiempo(tiempo_total_segundos, centesimas=True):
    tiempo_horas = int(tiempo_total_segundos // 3600)
    tiempo_sin_horas = tiempo_total_segundos % 3600
    tiempo_minutos = int(tiempo_sin_horas // 60)
    tiempo_segundos = tiempo_sin_horas % 60
    tiempo_final = ""
    if tiempo_horas:
        tiempo_final = str(tiempo_horas) + "hr "
    if tiempo_minutos:
        tiempo_final += str(tiempo_minutos) + "m "

    redondeo_segundos = 2 if centesimas else None
    tiempo_final += str(round(tiempo_segundos, redondeo_segundos)) + "s "
    return tiempo_final
