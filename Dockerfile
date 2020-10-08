FROM python:3.8
RUN mkdir /app
WORKDIR "/app"
VOLUME /app
RUN pip install --upgrade pip
ADD requirements.txt /app/
ADD src /app/src
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "src/main.py"]
