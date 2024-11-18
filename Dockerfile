# Usar una imagen base de Python
FROM python:3.12

# Establecer el directorio de trabajo en el contenedor
WORKDIR /core

# Copiar los archivos de requisitos y instalarlos
COPY core/requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt --timeout 200

# Copiar el resto de la aplicación
COPY core/ .

# Exponer el puerto que usa Streamlit
EXPOSE 8501

# Comando para ejecutar la aplicación Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
