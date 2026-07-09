import sys
with open('infra/shared/docker/backend/entrypoint.sh', 'rb') as f:
    text = f.read().replace(b'\r\n', b'\n')
with open('infra/shared/docker/backend/entrypoint.sh', 'wb') as f:
    f.write(text)
print("CRLF fixed")
