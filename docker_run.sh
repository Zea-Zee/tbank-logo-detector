docker run -d \
  --name tbank-detector-container \
  -p 8000:8000 \
  --restart unless-stopped \
  -v "$(pwd)/models:/models" \
  tbank-detector \
  tail -f /dev/null

