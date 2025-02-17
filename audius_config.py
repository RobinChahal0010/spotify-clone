import requests

# Audius API se host list fetch karo
response = requests.get("https://api.audius.co")

# JSON response check karo
data = response.json()

# List ke first item ko access karo
host = data["data"][0]  # Ye ek string return karega

print("Audius API Host:", host)
