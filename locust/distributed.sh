#!/bin/bash
function default_if_empty() {
    if [ -z "$2" ]; then
      echo "$1"
    else
      echo "$2"
    fi
}
#replace with your endpoint name in format <<endpoint-name>>
export ENDPOINT_NAME=$1
if  [ -z "$ENDPOINT_NAME" ]; then
    echo "Endpoint name not provided"
    echo "Usage ./distributed.sh <<endpoint-name>> [config.sh]"
    exit 1
fi
export PROPERTIES_FILE=$(default_if_empty config.sh $2)
source "${PROPERTIES_FILE}"

export USE_CASE=$(default_if_empty test "$USE_CASE")
export CONTENT_TYPE=$(default_if_empty application/json "${CONTENT_TYPE}")
export RUN_TIME=$(default_if_empty 10m "${RUN_TIME}")
export PAYLOAD_FILE=$(default_if_empty test.txt "${PAYLOAD_FILE}")
export REGION=$(default_if_empty us-east-1 "${REGION}")
export USERS=$(default_if_empty 10 "${USERS}")
export WORKERS=$(default_if_empty 10 "${WORKERS}")
export LOCUST_UI=$(default_if_empty false "${LOCUST_UI}")
export MAX_NEW_TOKENS=$(default_if_empty 256 "${MAX_NEW_TOKENS}")
export SCRIPT=$(default_if_empty locust_script.py "${SCRIPT}")

## Create a string with DDMMYYYYHHmmSS format
export TIMESTAMP=$(date +%d%m%Y%H%M%S)

#replace with the locust script that you are testing, this is the locust_script that will be used to make the InvokeEndpoint API calls.

mkdir -p  results
mkdir -p  logs
export LOG_FILE=logs/${USE_CASE}_"$TIMESTAMP".log
export STD_OUT=logs/${USE_CASE}_"$TIMESTAMP".out
export RESULT_FILE=results/${USE_CASE}_"$TIMESTAMP"
export HTML_RESULT_FILE=results/${USE_CASE}_"$TIMESTAMP".html

echo "ENDPOINT_NAME: $ENDPOINT_NAME"
echo "USE_CASE: $USE_CASE"
echo "CONTENT_TYPE: $CONTENT_TYPE"
echo "RUN_TIME: $RUN_TIME"
echo "PAYLOAD_FILE: $PAYLOAD_FILE"
echo "REGION: $REGION"
echo "USERS: $USERS"
echo "WORKERS: $WORKERS"
echo "LOCUST_UI: $LOCUST_UI"
echo "MAX_NEW_TOKENS: $MAX_NEW_TOKENS"
echo "TIMESTAMP: $TIMESTAMP"
echo "LOG_FILE: $LOG_FILE"
echo "STD_OUT: $STD_OUT"
echo "RESULT_FILE: $RESULT_FILE"
echo "HTML_RESULT_FILE: $HTML_RESULT_FILE"
echo "SCRIPT: $SCRIPT"


#make sure you are in a virtual environment
#. ./venv/bin/activate
# if LOCUST_UI is false, then run the locust script in headless mode
if $LOCUST_UI ; then
    locust -f $SCRIPT -H $ENDPOINT_NAME --master --expect-workers $WORKERS -u $USERS -t $RUN_TIME \
    --loglevel INFO --logfile ${LOG_FILE} \
    --csv ${RESULT_FILE} --html ${HTML_RESULT_FILE}  &
else
    locust -f $SCRIPT -H $ENDPOINT_NAME --master --expect-workers $WORKERS -u $USERS -t $RUN_TIME \
    --loglevel INFO --logfile ${LOG_FILE} \
    --csv ${RESULT_FILE} --headless --html ${HTML_RESULT_FILE}  &
fi

for (( c=1; c<=$WORKERS; c++ ))
do
    locust -f $SCRIPT -H $ENDPOINT_NAME --worker --master-host=localhost &
done

