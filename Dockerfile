FROM python:3
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD dashboard.py .
ADD settings.py .
RUN apt-get update && apt-get install -y gunicorn
CMD [ "gunicorn", "dashboard:server" ]
