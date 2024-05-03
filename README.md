# MicroServicio de Diccionario

## Descripción

Este un microservicio para diccionario en español y en ingles

#### Prerequisitos

Tener Docker instalado en el sistema

#### Construcción de imagen de Docker

##### Produccion

```bash
docker build -t diccionario -f Dockerfile.prod .

```
##### Dev

```bash
docker build -t diccionario -f Dockerfile.dev .
```

#### Despliegue de imagen de Docker en dev

```bash
docker run -p 5000:5000 -v $(pwd):/app diccionario
```

#### Despliegue de imagen de Docker en producción

```bash
docker run -p 5000:5000 diccionario
```
