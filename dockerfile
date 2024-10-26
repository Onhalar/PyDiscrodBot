FROM python:3.12

ADD . .

RUN pip install discord.py

CMD ["python", "-u" , "./src/main.py"]