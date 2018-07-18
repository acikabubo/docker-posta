#!/bin/bash
docker build --force-rm -t acikabubo/posta-pratki \
    --build-arg user=$USER \
    --build-arg uid=`id -u $USER` \
    --build-arg gid=`id -g $GROUP` \
    .

DANGLING=$(docker images -f "dangling=true" -q)
if [ "x""$DANGLING" != "x" ]; then
    docker rmi $DANGLING
fi

docker volume ls -qf dangling=true | xargs -r docker volume rm