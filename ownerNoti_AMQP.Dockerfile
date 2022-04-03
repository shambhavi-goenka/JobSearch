FROM python:3-slim
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY ./ownerNoti_AMQP.py ./ direct_amqp_setup.py ./
CMD [ "python", "./ownerNoti_AMQP.py" ]

