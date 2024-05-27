#!/bin/sh






echo "                 Configuring API Keys "
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ "
echo "- You will need API keys for OpenAI and ElevenLabs to run this program."
echo "- You will need an account to both of these services to get the keys and will be charged for usage."
echo "- These keys will only be stored within your instance of docker and will not be shared."
echo "\n                  OpenAI "
echo "───────────────────────────────────────────────────────────"
echo "OpenAI API keys can be found at https://platform.openai.com/account/api-keys"
echo "Example format: sk-ABC123def456GHI789jkl012MNOpqr345stu678"
read -p "Please enter your OpenAI API key, followed by Enter: " openai_api_key
echo "\n     -> Setting OpenAI key to $openai_api_key"
export OPENAI_API_KEY="$openai_api_key"

echo "\n                  ElevenLabs "
echo "───────────────────────────────────────────────────────────"
echo "ElevenLabs API keys can be found at https://www.eleven-labs.com/fr/api"
echo "Example format: 528916324ku09b9w59135950928662z3"
read -p "Please enter your ElevenLabs API key, followed by Enter: " elevenlabs_api_key
echo "\n     -> Setting OpenAI key to $elevenlabs_api_key"
export ELEVENLABS_API_KEY="$openai_api_key"

echo "\n\n┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"
echo "OpenAI API key set to: $OPENAI_API_KEY"
echo "ElevenLabs API key set to: $ELEVENLABS_API_KEY"
echo "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄"


echo "\n                 Launching Application "
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ "


sleep 20 && open http://localhost:5000/client &
docker run -it --rm -p 5000:5000 --expose 5000 --entrypoint="/home/sp/code/start.sh" -e OPENAI_API_KEY="$OPENAI_API_KEY" -e ELEVENLABS_API_KEY="$ELEVENLABS_API_KEY" synpt/base
