FROM python:3
ENV TZ 'Europe/Rome'
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt && pip install gunicorn
COPY dashboard.py settings.py /app/
CMD [ "gunicorn", "dashboard:server", "-b 0.0.0.0:8080", "--access-logfile", "gunicorn.log" ]
  