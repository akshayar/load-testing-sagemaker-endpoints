#!/bin/bash
#replace with your endpoint name in format <<endpoint-name>>
export ENDPOINT_NAME=$1
export CONTENT_TYPE=application/json
export RUN_TIME=1mg
export USE_CASE=$2
if [ -z "$USE_CASE" ]; then
    export USE_CASE=test
    echo "USE_CASE was empty, setting it to $USE_CASE"
fi
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
mkdir -p  results
mkdir -p  logs
export LOG_FILE=logs/${USE_CASE}_"$TIMESTAMP".log
export STD_OUT=logs/${USE_CASE}_"$TIMESTAMP".out
export RESULT_FILE=results/${USE_CASE}_"$TIMESTAMP"
export HTML_RESULT_FILE=results/${USE_CASE}_"$TIMESTAMP".html

#make sure you are in a virtual environment
#. ./venv/bin/activate
# if LOCUST_UI is false, then run the locust script in headless mode
if $LOCUST_UI ; then
    locust -f $SCRIPT -H $ENDPOINT_NAME --master --expect-workers $WORKERS -u $USERS -t $RUN_TIME \
    --loglevel INFO --logfile ${LOG_FILE} \
    --csv ${RESULT_FILE} --html ${HTML_RESULT_FILE} >> $STD_OUT &
else
    locust -f $SCRIPT -H $ENDPOINT_NAME --master --expect-workers $WORKERS -u $USERS -t $RUN_TIME \
    --loglevel INFO --logfile ${LOG_FILE} \
    --csv ${RESULT_FILE} --headless --html ${HTML_RESULT_FILE} >> $STD_OUT &
fi

for (( c=1; c<=$WORKERS; c++ ))
do
    locust -f $SCRIPT -H $ENDPOINT_NAME --worker --master-host=localhost &
done

