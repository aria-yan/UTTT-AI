FROM ubuntu

# install dependencies
RUN apt-get update
RUN apt-get install -y python3 python3-pip
RUN pip install pygame numpy

# make directories for the biz
RUN mkdir /root/wt
RUN mkdir /root/arenalog

# copy in arena
COPY arena.py /root/wt

# copy in referee 
COPY core_gameplay.py /root/wt
COPY display.py /root/wt
COPY external_players.py /root/wt
COPY headlessgame.py /root/wt
COPY human.py /root/wt
COPY referee.py /root/wt

# copy in wongtron
COPY wongtron.py /root/wt

WORKDIR /root/wt
CMD ["python3", "arena.py"]
