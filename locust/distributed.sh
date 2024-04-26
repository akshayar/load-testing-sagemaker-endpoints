#!/bin/bash
function default_if_empty() {
    if [ -z "$2" ]; then
      echo "$1"
    else
      echo "$2"
    fi
}
#replace with your endpoint name in format <<endpoint-name>>
export LOCUST_HOST=$1
if  [ -z "$LOCUST_HOST" ]; then
    echo "Endpoint name not provided"
    echo "Usage ./distributed.sh <<endpoint-name>> [config.sh] [run-label]"
    exit 1
fi
export PROPERTIES_FILE=$(default_if_empty config.sh $2)
source "${PROPERTIES_FILE}"

export RUN_LABEL=$(default_if_empty test "$3")
export CONTENT_TYPE=$(default_if_empty application/json "${CONTENT_TYPE}")
export PAYLOAD_FILE=$(default_if_empty test.txt "${PAYLOAD_FILE}")
export REGION=$(default_if_empty us-east-1 "${REGION}")
export MAX_NEW_TOKENS=$(default_if_empty 256 "${MAX_NEW_TOKENS}")
export LOCUST_LOCUSTFILE=$(default_if_empty locust_script.py "${LOCUST_LOCUSTFILE}")
export LOCUST_RUN_TIME=$(default_if_empty 10m "${LOCUST_RUN_TIME}")
export LOCUST_USERS=$(default_if_empty 10 "${LOCUST_USERS}")
export LOCUST_EXPECT_WORKERS=$(default_if_empty 10 "${LOCUST_EXPECT_WORKERS}")
export LOCUST_UI=$(default_if_empty false "${LOCUST_UI}")


## Create a string with DDMMYYYYHHmmSS format
export TIMESTAMP=$(date +%d%m%Y%H%M%S)


#replace with the locust script that you are testing, this is the locust_script that will be used to make the InvokeEndpoint API calls.

mkdir -p  results
mkdir -p  logs
export STD_OUT=logs/${RUN_LABEL}_"$TIMESTAMP".out
export LOCUST_CSV=results/${RUN_LABEL}_"$TIMESTAMP"
export LOCUST_HTML=results/${RUN_LABEL}_"$TIMESTAMP".html
export LOCUST_LOGFILE=logs/${RUN_LABEL}_"$TIMESTAMP".log
export LOCUST_LOGLEVEL=INFO


echo "RUN_LABEL: $RUN_LABEL"
echo "CONTENT_TYPE: $CONTENT_TYPE"
echo "PAYLOAD_FILE: $PAYLOAD_FILE"
echo "REGION: $REGION"
echo "MAX_NEW_TOKENS: $MAX_NEW_TOKENS"
echo "TIMESTAMP: $TIMESTAMP"
echo "STD_OUT: $STD_OUT"
echo "LOCUST_RUN_TIME: $LOCUST_RUN_TIME"
echo "LOCUST_LOCUSTFILE: $LOCUST_LOCUSTFILE"
echo "LOCUST_USERS: $LOCUST_USERS"
echo "LOCUST_EXPECT_WORKERS: $LOCUST_EXPECT_WORKERS"
echo "LOCUST_UI: $LOCUST_UI"
echo "LOCUST_LOGFILE: $LOCUST_LOGFILE"
echo "LOCUST_CSV: $LOCUST_CSV"
echo "LOCUST_HTML: $LOCUST_HTML"
echo "LOCUST_HOST: $LOCUST_HOST"


#make sure you are in a virtual environment
#. ./venv/bin/activate
# if LOCUST_UI is false, then run the locust script in headless mode
if $LOCUST_UI ; then
    locust  --master   | tee $STD_OUT &
else
    locust  --master  --headless  | tee $STD_OUT &
fi

for (( c=1; c<=$LOCUST_EXPECT_WORKERS; c++ ))
do
    locust   --worker --master-host=localhost &
done

