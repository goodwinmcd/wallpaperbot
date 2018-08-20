FROM ubuntu
RUN mkdir /app
RUN apt-get update &&\
    apt-get -y install mongodb \
                python \
                git \
                pip &&\
    service mongodb start &&\
    pip install -r /app/requirements.txt &&\
    git clone https://github.com/goodwinmcd/wallpaperbot.git /app &&\
    git clone https://github.com/goodwinmcd/wallpapers /app &&\
    mongo &&\
    use wallpapers &&\
    db.createCollection("wallpapers") &&\
    exit &&\
    /app/load_wallpapers.py
CMD /app/wallpaperbot.py
