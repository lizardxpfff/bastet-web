# Proyecto Bastet

## Descripción

**Bastet** es una aplicación de **consulta de cámaras** que permite buscar cámaras cercanas en un radio determinado (200 metros) utilizando coordenadas geográficas (latitud y longitud). Los usuarios pueden agregar nuevas cámaras, buscar cámaras cercanas y almacenar datos en una base de datos SQLite.

Este proyecto está diseñado para ser fácil de usar, con una interfaz gráfica limpia utilizando **Tkinter** y una integración con la **API de Google Maps** para obtener direcciones basadas en coordenadas geográficas.

## Funcionalidades

- **Buscar cámaras cercanas**: Ingresar coordenadas geográficas y obtener una lista de cámaras cercanas en un radio de 200 metros.
- **Agregar cámaras**: Permite a los usuarios ingresar las coordenadas de una cámara, propietario y contacto, y guardar esta información en una base de datos SQLite.
- **Interfaz gráfica**: Utiliza la librería **Tkinter** para crear una interfaz fácil de usar, con botones para buscar cámaras, agregar cámaras y limpiar los campos de entrada.
- **API de Google Maps**: Utiliza la API de Google Maps para obtener direcciones a partir de las coordenadas proporcionadas.

## Tecnologías utilizadas

- **Python 3.11**: Lenguaje de programación.
- **Tkinter**: Biblioteca para crear interfaces gráficas de usuario (GUIs) en Python.
- **SQLite**: Base de datos ligera para almacenar la información de las cámaras.
- **requests**: Biblioteca para hacer peticiones HTTP y obtener la dirección desde la API de Google Maps.
- **API de Google Maps**: Para obtener direcciones basadas en las coordenadas geográficas.

