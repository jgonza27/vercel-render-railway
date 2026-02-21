# Práctica Final: Despliegue en Vercel y Render con CI/CD

**Alumno:** Jesús  
**Asignatura:** Despliegue de Aplicaciones Web  
**Fecha:** Febrero 2026

---

## Índice

1. [Introducción](#1-introducción)
2. [Clonación del repositorio](#2-clonación-del-repositorio)
3. [Configuración del entorno local](#3-configuración-del-entorno-local)
4. [Ejecución local con Docker Compose](#4-ejecución-local-con-docker-compose)
5. [Verificación del funcionamiento local](#5-verificación-del-funcionamiento-local)
6. [Creación de la base de datos en Railway](#6-creación-de-la-base-de-datos-en-railway)
7. [Despliegue del Backend en Render](#7-despliegue-del-backend-en-render)
8. [Despliegue del Frontend en Vercel](#8-despliegue-del-frontend-en-vercel)
9. [Configuración de CI/CD con GitHub Actions](#9-configuración-de-cicd-con-github-actions)
10. [Verificación del despliegue en producción](#10-verificación-del-despliegue-en-producción)

---

## 1. Introducción

Esta práctica consiste en el despliegue de una aplicación web full-stack utilizando plataformas PaaS (Platform as a Service):

| Componente | Tecnología | Plataforma de despliegue |
|---|---|---|
| **Frontend** | Vue 3 + Vite + Tailwind CSS | Vercel |
| **Backend** | FastAPI (Python) + SQLAlchemy | Render |
| **Base de datos** | MySQL | Railway |

La aplicación es un gestor de tareas (Todo List) con operaciones CRUD completas. El backend persiste los datos en una base de datos MySQL mediante SQLAlchemy.

El repositorio base utilizado es: https://github.com/josejuansanchez/vercel-render

---

## 2. Clonación del repositorio

Clonamos el repositorio del profesor en nuestra carpeta de trabajo:

```bash
git clone https://github.com/josejuansanchez/vercel-render.git .
```

![Clonación del repositorio y git log](image.png)

La estructura del proyecto clonado es la siguiente:

```
.
├── backend/                # API REST con FastAPI
│   ├── main.py             # Lógica de la API
│   ├── requirements.txt    # Dependencias Python
│   └── Dockerfile          # Imagen Docker (multi-stage)
├── frontend/               # Aplicación Vue 3
│   ├── src/
│   │   ├── App.vue         # Componente principal
│   │   └── services/
│   │       └── api.ts      # Servicio HTTP con axios
│   ├── Dockerfile          # Imagen Docker (multi-stage)
│   └── package.json
├── .github/workflows/      # CI/CD con GitHub Actions
│   ├── deploy-backend.yaml
│   └── deploy-frontend.yaml
├── .env.example            # Variables de entorno de ejemplo
├── compose.yaml            # Docker Compose para desarrollo
└── README.md
```

---

## 3. Configuración del entorno local

Creamos el archivo `.env` a partir del archivo de ejemplo:

```bash
cp .env.example .env
```

El contenido del archivo `.env` es:

```env
# Puertos
BACKEND_PORT=8000
FRONTEND_PORT=3000
MYSQL_PORT=3306

# Frontend
VITE_API_URL=http://localhost:8000

# MySQL (local)
MYSQL_DATABASE=app_db
MYSQL_USER=app
MYSQL_PASSWORD=app
MYSQL_ROOT_PASSWORD=root

# Backend DB (local)
DB_HOST=mysql
DB_PORT=3306
DB_NAME=app_db
DB_USER=app
DB_PASSWORD=app

# Producción (Railway)
DATABASE_URL=
```

![Archivo .env configurado en VS Code](image-1.png)

---

## 4. Ejecución local con Docker Compose

Levantamos todos los servicios (frontend, backend y MySQL) con Docker Compose:

```bash
docker compose up -d --build
```

Este comando:
- Construye las imágenes Docker del frontend y backend usando sus respectivos Dockerfiles (multi-stage)
- Descarga la imagen oficial de MySQL 8.3
- Levanta los 3 contenedores en segundo plano

![Ejecución de docker compose up --build](image-2.png)

Verificamos que los contenedores están ejecutándose:

```bash
docker compose ps
```

![Resultado de docker compose ps mostrando los 3 contenedores](image-3.png)

---

## 5. Verificación del funcionamiento local

### 5.1. Backend API

Accedemos al backend en http://localhost:8000 para verificar que responde:

![Backend respondiendo con status online en localhost:8000](image-4.png)

Accedemos a la documentación Swagger en http://localhost:8000/docs:

![Documentación Swagger de la API con todos los endpoints](image-5.png)

Verificamos que los endpoints devuelven datos de la base de datos MySQL accediendo a http://localhost:8000/api/items:

![Endpoint /api/items devolviendo los 3 items de la base de datos](image-6.png)

La base de datos se inicializa automáticamente con 3 tareas de ejemplo (seed data):
- Módulo CI/CD → Completado
- Módulo Docker → En progreso
- Módulo Despliegue → Pendiente

### 5.2. Frontend

Accedemos al frontend en http://localhost:3000:

![Frontend Vue 3 mostrando la Todo List con datos del backend](image-7.png)

El frontend muestra los datos obtenidos del backend, incluyendo el estado de conexión y la lista de tareas.

---

## 6. Creación de la base de datos en Railway

Para producción, necesitamos una base de datos MySQL accesible desde internet. Utilizamos Railway.

### 6.1. Crear cuenta y proyecto

1. Accedemos a [railway.com](https://railway.com) y creamos una cuenta (o iniciamos sesión con GitHub)
2. Hacemos clic en **"New Project"**

![Pantalla de nuevo proyecto en Railway con las opciones disponibles](image-8.png)

### 6.2. Añadir servicio MySQL

1. Seleccionamos **"Database"** → **"MySQL"**
2. Railway crea automáticamente la base de datos con todas las variables de conexión

![Servicio MySQL creado y online en Railway](image-9.png)

### 6.3. Obtener la cadena de conexión

1. Hacemos clic en el servicio MySQL
2. Vamos a la pestaña **"Variables"**
3. Copiamos el valor de `MYSQL_PUBLIC_URL`

![Variables del servicio MySQL con MYSQL_PUBLIC_URL visible](image-10.png)

> **Nota:** La cadena de conexión tiene el formato:  
> `mysql://user:password@host:port/database`  
> El backend la convierte automáticamente a `mysql+pymysql://...`

---

## 7. Despliegue del Backend en Render

### 7.1. Crear cuenta y vincular GitHub

1. Accedemos a [render.com](https://render.com) e iniciamos sesión con GitHub

### 7.2. Crear Web Service

1. Hacemos clic en **"New +"** → **"Web Service"**

![Selección del tipo de servicio en Render](image-11.png)

2. Conectamos nuestro repositorio de GitHub y seleccionamos `vercel-render-railway`

### 7.3. Configurar el servicio

Configuramos los siguientes parámetros:

| Parámetro | Valor |
|---|---|
| **Name** | `vercel-render-backend` |
| **Root Directory** | `./backend` |
| **Runtime** | `Docker` |
| **Branch** | `main` |
| **Region** | Oregon (US West) |
| **Plan** | Free |

![Configuración del Web Service en Render con Docker y root directory](image-12.png)

### 7.4. Configurar variables de entorno

En la sección **"Environment Variables"** de Render, añadimos:

| Variable | Valor |
|---|---|
| `DATABASE_URL` | La cadena de conexión de Railway (paso 6.3) |

Seleccionamos el plan **Free** y configuramos la variable `DATABASE_URL` con la cadena de conexión de Railway:

![Plan Free seleccionado y variable DATABASE_URL configurada en Render](image-13.png)

### 7.5. Despliegue

Hacemos clic en **"Create Web Service"** y esperamos a que se complete el despliegue.

Una vez desplegado, obtenemos la URL del backend, por ejemplo:  
`https://vercel-render-backend-xxx.onrender.com`

### 7.6. Obtener el Deploy Hook

1. En el dashboard de Render, vamos a nuestro servicio → **Settings**
2. Buscamos la sección **"Deploy Hook"** y copiamos la URL

---

## 8. Despliegue del Frontend en Vercel

### 8.1. Crear cuenta y vincular GitHub

1. Accedemos a [vercel.com](https://vercel.com) e iniciamos sesión con GitHub

### 8.2. Importar el proyecto

1. Hacemos clic en **"Add New"** → **"Project"**
2. Seleccionamos nuestro repositorio y hacemos clic en **"Import"**

### 8.3. Configurar el proyecto

Configuramos los siguientes parámetros en **Build and Deployment Settings**:

| Parámetro | Valor |
|---|---|
| **Project Name** | `vercel-render-frontend` |
| **Root Directory** | `./frontend` |
| **Framework Preset** | `Vite` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### 8.4. Configurar variables de entorno

En la sección **"Environment Variables"**, añadimos:

| Variable | Valor |
|---|---|
| `VITE_API_URL` | `https://vercel-render-backend-xxx.onrender.com` (URL del backend en Render) |

### 8.5. Despliegue

Hacemos clic en **"Deploy"** y esperamos a que termine.

Una vez desplegado, obtenemos la URL del frontend, por ejemplo:  
`https://vercel-render-frontend-xxx.vercel.app`

### 8.6. Obtener el Token de Vercel

1. Vamos a [Vercel Settings → Tokens](https://vercel.com/account/tokens)
2. Hacemos clic en **"Create"**
3. Nombre: `GitHub CI/CD`
4. Scope: **Full Account**
5. Copiamos el token generado

---

## 9. Configuración de CI/CD con GitHub Actions

### 9.1. Configurar GitHub Secrets

Vamos a nuestro repositorio en GitHub → **Settings** → **Secrets and variables** → **Actions** y creamos los siguientes secrets:

| Secret | Valor |
|---|---|
| `RENDER_DEPLOY_HOOK` | URL del Deploy Hook de Render (paso 7.6) |
| `VERCEL_TOKEN` | Token de Vercel (paso 8.6) |

### 9.2. Workflows de GitHub Actions

El repositorio ya incluye dos workflows configurados:

**`.github/workflows/deploy-backend.yaml`** — Se ejecuta cuando hay cambios en `backend/`:

```yaml
name: Deploy Backend to Render

on:
  push:
    branches: [ "main" ]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Trigger Render Deploy Hook
        run: |
          curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}
```

**`.github/workflows/deploy-frontend.yaml`** — Se ejecuta cuando hay cambios en `frontend/`:

```yaml
name: Deploy Frontend to Vercel

on:
  push:
    branches: [ "main" ]
    paths:
      - 'frontend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Vercel CLI
        run: npm install --global vercel@latest
      - name: Pull Vercel Environment Information
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: ./frontend
      - name: Build Project Artifacts
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: ./frontend
      - name: Deploy Project Artifacts to Vercel
        run: vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }}
        working-directory: ./frontend
```

### 9.3. Verificar CI/CD

Para probar que el CI/CD funciona, realizamos un cambio y hacemos push:

```bash
git add .
git commit -m "Test CI/CD deployment"
git push origin main
```

Verificamos en GitHub → **Actions** que los workflows se ejecutan correctamente.

---

## 10. Verificación del despliegue en producción

### 10.1. Backend en Render

Accedemos a la URL del backend en Render y comprobamos que responde.

Accedemos a `/api/items` para verificar que la base de datos funciona.

### 10.2. Frontend en Vercel

Accedemos a la URL del frontend en Vercel y comprobamos que carga correctamente y muestra los datos del backend.

---

## Resumen de URLs

| Servicio | URL |
|---|---|
| **Frontend (Vercel)** | `https://COMPLETAR.vercel.app` |
| **Backend (Render)** | `https://COMPLETAR.onrender.com` |
| **Base de datos (Railway)** | (interna, no accesible públicamente) |
| **Repositorio GitHub** | `https://github.com/jgonza27/vercel-render-railway` |

---

## Tecnologías utilizadas

| Componente | Tecnología |
|---|---|
| Frontend | Vue 3 + Vite + Tailwind CSS |
| Backend | FastAPI + SQLAlchemy + PyMySQL |
| Base de datos | MySQL 8.3 |
| Contenedores | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Hosting Frontend | Vercel |
| Hosting Backend | Render |
| Hosting Base de datos | Railway |
