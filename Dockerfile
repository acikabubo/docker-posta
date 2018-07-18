FROM python:3.7

LABEL Aleksandar Krsteski "krsteski_aleksandar@hotmail.com"

ENV LANG=C.UTF-8

RUN apt-get update -qq  && \
    apt-get upgrade -yqq && \
    apt-get install tmux -yqq && \
    apt-get autoremove -y

ARG user=acika
ARG uid=1000
ARG gid=1000

RUN groupadd -g $gid $user; exit 0  # do not crash on already existing GID
RUN useradd -ms /bin/bash -u $uid -g $gid $user

ADD reqs /tmp/reqs.txt

RUN pip3 install -U setuptools
RUN pip3 install --upgrade pip
RUN pip3 install -r /tmp/reqs.txt

RUN rm -rf /tmp/reqs/txt

ADD . /home/$user/posta_pratki

RUN chown -R $user:$gid /home/$user/posta_pratki

USER $user

WORKDIR /home/$user/posta_pratki

CMD [ "python", "./pratki.py" ]
