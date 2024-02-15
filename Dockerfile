FROM python:3.10
WORKDIR /home/ashley

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /home/ashley/requirements.txt
RUN pip install -r requirements.txt

COPY . /home/ashley
ENTRYPOINT ["sh", "/home/ashley/entrypoint.sh"]