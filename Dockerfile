FROM python:3

WORKDIR /usr/src/app

RUN pip install  --no-cache-dir -U goodwe pymodbus

COPY goodwe_modbus.py ./

# will expose port 8899/tcp
EXPOSE 8899

CMD  /usr/local/bin/python goodwe_modbus.py $GOODWE_IP 
