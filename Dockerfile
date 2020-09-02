FROM python:3
WORKDIR /app
RUN apt-get update && apt-get install -y gunicorn
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD dashboard.py .
ADD settings.py .
CMD [ "gunicorn", "dashboard:server" ]
