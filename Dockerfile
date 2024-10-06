FROM python:3.11.5-alpine3.18

WORKDIR app/

COPY requirements.txt requirements.txt

RUN pip3 install --upgrade pip setuptools wheel
RUN pip3 install --no-warn-script-location --no-cache-dir -r requirements.txt

COPY . .

CMD ["python3", "main.py", "-a", "1"]
