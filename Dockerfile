FROM python:3.8-slim-buster as base

FROM base as requirements
RUN apt-get update && apt-get install -y curl
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

FROM requirements as app

COPY . /
RUN python setup.py install 

FROM app as run-time

ENV FLASK_RUN_PORT 5000
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_APP pyatlas.AutomaticKeyMachine
ENTRYPOINT [ "flask" ]
CMD [ "run" ]
#CMD [ "run", "--host", "0.0.0.0" ]
