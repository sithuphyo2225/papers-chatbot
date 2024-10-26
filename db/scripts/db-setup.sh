#!/bin/bash

set -e
set -u

export PGUSER="postgres"

echo "Creating the database named chatbot"

psql -c "CREATE DATABASE chatbot"

psql chatbot -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"