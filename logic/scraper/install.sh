#!/bin/bash

SCRIPT_DIR="./"

# wrapper script to be run hourly
cat << EOF > /usr/local/bin/fetch-rss-feeds.sh
#!/bin/bash
cd $SCRIPT_DIR
/usr/bin/python3 $SCRIPT_DIR/scraper.py
EOF

chmod +x /usr/local/bin/fetch-rss-feeds.sh

#systemd service file
cat << EOF > fetch-rss-feeds.service
[Unit]
Description=Hourly Python Task Service
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/fetch-rss-feeds.sh
WorkingDirectory=$SCRIPT_DIR

[Install]
WantedBy=multi-user.target
EOF

sudo cp fetch-rss-feeds.service /etc/systemd/system/


#timer file
cat << EOF > fetch-rss-feeds.timer
[Unit]
Description=Run fetch-rss-feeds.service every hour

[Timer]
OnBootSec=5min
OnUnitActiveSec=1h

[Install]
WantedBy=timers.target
EOF

# Copy the timer file to the appropriate directory
sudo cp fetch-rss-feeds.timer /etc/systemd/system/

# Step 5: Reload systemd, enable and start the timer
sudo systemctl daemon-reload
sudo systemctl enable fetch-rss-feeds.timer
sudo systemctl start fetch-rss-feeds.timer

echo "All good, set up to fetch rss feeds hourly."