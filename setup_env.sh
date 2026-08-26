#!/usr/bin/env bash

set -e

ENV_FILE=".env"
EXAMPLE_FILE=".env.example"

cat <<'EOF' > "$EXAMPLE_FILE"
# OpenAI
# API_KEY=sk-...
# BASE_URL=
# MODEL=gpt-4o-mini
# MODEL_SUMMARIZER=gpt-4o-mini

# Groq
# API_KEY=gsk_...
# BASE_URL=https://api.groq.com/openai/v1
# MODEL=llama-3.3-70b-versatile
# MODEL_SUMMARIZER=llama-3.3-70b-versatile

# Google AI Studio (Gemini)
# API_KEY=AIzaSy...
# BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
# MODEL=gemini-2.5-flash
# MODEL_SUMMARIZER=gemini-2.5-flash

# Active Configuration
API_KEY=
BASE_URL=
MODEL=gpt-4o-mini
MODEL_SUMMARIZER=gpt-4o-mini
EOF

if [ ! -f "$ENV_FILE" ]; then
    cp "$EXAMPLE_FILE" "$ENV_FILE"
    echo "Created $ENV_FILE from template."
else
    echo "$ENV_FILE already exists. Kept existing file."
fi

echo "Template ready at $EXAMPLE_FILE."
