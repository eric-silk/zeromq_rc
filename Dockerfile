FROM python:3.10
WORKDIR /app
COPY ./dist/zeromq_rc-0.1.0-py3-none-any.whl .
RUN python3 -m pip install zeromq_rc-0.1.0-py3-none-any.whl
ENTRYPOINT [ "python3", "-u", "-m", "zeromq_rc" ]