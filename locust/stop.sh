#!/bin/bash
## search for locust processes and kill them
ps aux | grep locust | grep -v grep | awk '{print $2}' | xargs kill -9
