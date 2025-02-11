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

import re
import en_chino, en_ingles, en_castellano
import textos_info_popups
import app_context




# Dictionaries for translations
en_chino = en_chino.diccionario
en_ingles = en_ingles.diccionario
en_castellano = en_castellano.diccionario

# Status messages in different languages
estados_ingles = {
    "no_comenzado": "Not Started ",
    "renderizando": "Rendering ",
    "terminado": "Finished ",
    "interrumpido": "Interrupted ",
    "fallo": "Failed ",
    "desactivado": "Disabled",
    "preparando": "Preparing",
    "faltante": "Blend Missing"
}

estados_castellano = {
    "no_comenzado": "No comenzado ",
    "renderizando": "Renderizando ",
    "terminado": "Terminado ",
    "interrumpido": "Interrumpido ",
    "fallo": "Falló ",
    "preparando": "Preparando",
    "desactivado": "Desactivado",
    "faltante": "Blend no encontrado"
}

estados_chino = {
    "no_comenzado": "未启动",
    "renderizando": "渲染 ",
    "terminado": "完成 ",
    "interrumpido": "暂停",
    "fallo": "失败",
    "desactivado": "禁用",
    "preparando": "准备",
    "faltante": "Missing"
}

estados_por_idioma = {
    "English": estados_ingles,
    "Castellano": estados_castellano,
    "中文": estados_chino
}

dic_estados = [estados_ingles, estados_castellano, estados_chino]
dic_palabras = {
    "English": en_ingles,
    "Castellano": en_castellano,
    "中文": en_chino
}



# # Function to translate states based on current language
# def traducir_estados():
#     global estados
#     estados = estados_por_idioma[app_context.idioma]

def faltantes_chino():
    traducciones_faltantes = {}
    for key_traduccion, traduccion in en_ingles.items():
        if key_traduccion in en_chino:
            if en_chino[key_traduccion] != traduccion:
                continue
        tf = f"'{key_traduccion}': {repr(traduccion)},"
        traducciones_faltantes.update({key_traduccion: traduccion})
        print(tf)

    return traducciones_faltantes

def estados(estado):
    return estados_por_idioma[app_context.idioma][estado]

# Function to translate popup messages
def traducir_popup(nombre):
    popup = getattr(textos_info_popups, nombre, None)
    traduccion = popup.get(app_context.idioma, None)
    return traduccion or popup or ""


# Function to translate a word based on the dictionary
def traducir(palabra, diccionario=None):
    if not diccionario:
        diccionario = dic_palabras[app_context.idioma]
    if palabra in diccionario:
        return diccionario[palabra]
    elif app_context.idioma != "Castellano" and palabra in en_ingles:
        return en_ingles[palabra]
    else:
        return palabra


# Function to translate the current information based on previous language
def traducir_info_actual(idioma_previo, mensaje_actual, diccionario):
    for clave, elemento in diccionario[idioma_previo].items():
        if mensaje_actual == elemento:
            return diccionario[app_context.idioma][clave]
    return mensaje_actual


# Function to translate the current state based on previous language
def traducir_estado_actual(idioma_previo, estado_actual):
    patron = r"([a-zA-Z\s]+.\s)(\((\d\s)(.+)\))?"
    partes = re.search(patron, estado_actual)
    estado_traducido = estado_actual

    if partes:
        if partes.group(1):
            base = partes.group(1)
            estado_traducido = traducir_info_actual(idioma_previo, base, dic_estados)

        if partes.group(4):
            info_frames = partes.group(4)
            estado_traducido += "(" + partes.group(3) + traducir_info_actual(idioma_previo, info_frames,
                                                                             dic_palabras) + ")"

    return estado_traducido


# Function to translate a phrase
def traducir_frase(frase):
    descomposicion = re.findall(r'\w+|\W+', frase)
    frase_traducida = ""
    for palabra in descomposicion:
        frase_traducida += traducir(palabra)
    return frase_traducida
