FROM ubuntu:24.04
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

RUN apt-get update -y && apt-get install -y dictd dict dict-wn python3-pip python3-venv

# Crear el entorno virtual
RUN python3 -m venv /opt/venv

#Flask en el ambiente virtual
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install Flask

# Instalar Flask 
RUN pip3 install Flask

# Copiar arhivos de diccionario

COPY dic_es.dict.dz /usr/share/dictd/
COPY dic_es.index /usr/share/dictd/

# Comandos para volver valido el diccionario

RUN  ./usr/sbin/dictdconfig --write   
RUN ./etc/init.d/dictd restart 
# Copiar Aplicacion de Flask

COPY app.py /app.py

EXPOSE 5000

CMD ["python3", "app.py"]
