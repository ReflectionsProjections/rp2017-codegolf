#!/bin/bash

i=0
declare -a containers

if [ $# -ne 1 ]
  then
    echo "Usage: ""$0"" <# containers>"
    exit 1
fi

# check docker-machine exists and attached
rc=$(docker-machine status)
if ! [[ $rc =~ "Running" ]]
  then
    echo "docker-machine not running. exiting"
    exit 1
  else
    rc2=$(docker images)
    if [[ $rc2 =~ "error" ]]
      then
        eval "$(docker-machine env default)"
    fi
fi

# check image exists, create
if ! [[ $rc2 =~ "code-golf-sandbox" ]]
  then
    echo "image does not exist, creating"
    docker build docker -t code-golf-sandbox
fi

while [ $i -lt $1 ]
  do
    docker run -id code-golf-sandbox bash
    i=$[$i+1]
done

echo "Successfully created ""$#"" containers"
exit 0

