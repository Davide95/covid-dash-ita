FROM python:3
WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD dashboard.py .
ADD settings.py .
CMD [ "python3", "dashboard.py" ]