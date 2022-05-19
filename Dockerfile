FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /ht-portfolio-app

COPY requirements.txt /ht-portfolio-app/

RUN pip install -r requirements.txt

COPY . /ht-portfolio-app/

EXPOSE 8000

CMD python3 manage.py runserver 0.0.0.0:8000