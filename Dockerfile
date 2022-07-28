#-- builder

FROM python:3.10.5-slim-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /wheels

COPY ./requirements.txt /wheels/requirements/netorg.txt

COPY . /opt/sources

RUN find /opt/sources -type f -not -name '*.py' -delete && \
    find /opt/sources -depth -type d -name '.*' -exec rm -r '{}' \; && \
    find /opt/sources -depth -type d -name '__pycache__' -exec rm -r '{}' \; && \
    find /opt/sources -name 'test_*.py' -delete 

ADD https://files.pythonhosted.org/packages/9b/9e/9e0610f25e65e2cdf90b1ee9c47ca710865401904038558ac0129ea23cbc/pip-22.2-py3-none-any.whl \
    /wheels/pip.whl

RUN python3 /wheels/pip.whl/pip wheel -r ./requirements/netorg.txt

#-- runner

FROM gcr.io/distroless/python3

COPY --from=0 /wheels /wheels

RUN python3 /wheels/pip.whl/pip install -r /wheels/requirements/netorg.txt -f /wheels && \
    python3 -c 'import shutil; shutil.rmtree("/wheels")'

COPY --from=0 /opt/sources /opt/netorg

COPY ./LICENSE /opt/netorg/LICENSE

WORKDIR /opt/netorg

ENV HOME /home/netorg

ENTRYPOINT ["python3", "/opt/netorg/netorg.py"]
