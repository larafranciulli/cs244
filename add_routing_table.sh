#!/bin/bash

# This script sets up a dedicated routing table for experiment traffic

# CONFIGURATION
EXPERIMENT_TABLE_ID=200      # Pick an unused table ID (between 1 and 252)
EXPERIMENT_TABLE_NAME="pingtable"
EXPERIMENT_INTERFACE="tap9"
EXPERIMENT_NEXT_HOP="100.73.128.1"

# 1. Create a new entry in /etc/iproute2/rt_tables (if not already there)
if ! grep -q "$EXPERIMENT_TABLE_NAME" /etc/iproute2/rt_tables; then
    echo "$EXPERIMENT_TABLE_ID $EXPERIMENT_TABLE_NAME" | sudo tee -a /etc/iproute2/rt_tables
fi

# 2. Flush any existing routes in the experiment table
sudo ip route flush table $EXPERIMENT_TABLE_NAME

# 3. Add default routes (1.0.0.0/8 to 223.0.0.0/8) into pingtable
for i in $(seq 1 255); do
    sudo ip route add $i.0.0.0/8 via $EXPERIMENT_NEXT_HOP dev $EXPERIMENT_INTERFACE table $EXPERIMENT_TABLE_NAME
done

# 4. Add a rule: use pingtable for traffic going out tap11
# You can also match on src IP if you prefer: (e.g., `from 100.75.128.2`)
sudo ip rule add oif $EXPERIMENT_INTERFACE lookup $EXPERIMENT_TABLE_NAME

echo "✅ All done! Routes installed in $EXPERIMENT_TABLE_NAME."
