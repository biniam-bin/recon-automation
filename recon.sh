#!/bin/bash

DOMAIN=$1
OUTPUT_DIR="output/$DOMAIN"
mkdir -p $OUTPUT_DIR

/root/go/bin/subfinder -d $DOMAIN -silent -o $OUTPUT_DIR/subs.txt

cat $OUTPUT_DIR/subs.txt | /root/go/bin/httpx -silent -o $OUTPUT_DIR/alive.txt

python3 send_notification.py $DOMAIN $OUTPUT_DIR/alive.txt
python3 save_to_db.py $DOMAIN $OUTPUT_DIR/alive.txt
