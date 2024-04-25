#!/bin/bash
#replace with your endpoint name in format <<endpoint-name>>
export ENDPOINT_NAME=$1
export CONTENT_TYPE=application/json
export RUN_TIME=1mg
#Check if $REGION is empty, if empty set it to us-east-1
if [ -z "$REGION" ]; then
    export REGION=us-east-1
    echo "REGION was empty, setting it to $REGION"
fi
if [ -z "$USERS" ]; then
    export USERS=240
    echo "USERS was empty, setting it to $USERS"
fi
if [ -z "$WORKERS" ]; then
    export WORKERS=60
    echo "WORKERS was empty, setting it to $WORKERS"
fi
if [ -z "$LOCUST_UI" ]; then
    export LOCUST_UI=false # Use Locust UI
    echo "LOCUST_UI was empty, setting it to $LOCUST_UI"
fi
if [ -z "$MAX_NEW_TOKENS" ]; then
    export MAX_NEW_TOKENS=256
    echo "MAX_NEW_TOKENS was empty, setting it to $MAX_NEW_TOKENS"
fi
## Create a string with DDMMYYYYHHmmSS format
export TIMESTAMP=$(date +%d%m%Y%H%M%S)


#replace with the locust script that you are testing, this is the locust_script that will be used to make the InvokeEndpoint API calls.
export SCRIPT=locust_script.py

#make sure you are in a virtual environment
#. ./venv/bin/activate
# if LOCUST_UI is false, then run the locust script in headless mode
if $LOCUST_UI ; then
    locust -f $SCRIPT -H $ENDPOINT_NAME --master --expect-workers $WORKERS -u $USERS -t $RUN_TIME \
    --loglevel INFO --logfile results"$TIMESTAMP".log \
    --csv results"$TIMESTAMP" --html results"$TIMESTAMP".html &
else
    locust -f $SCRIPT -H $ENDPOINT_NAME --master --expect-workers $WORKERS -u $USERS -t $RUN_TIME \
    --loglevel INFO --logfile results"$TIMESTAMP".log \
    --csv results"$TIMESTAMP" --headless --html results"$TIMESTAMP".html &
fi

for (( c=1; c<=$WORKERS; c++ ))
do
    locust -f $SCRIPT -H $ENDPOINT_NAME --worker --master-host=localhost &
done

