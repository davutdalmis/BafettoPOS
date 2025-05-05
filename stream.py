# dosya ismi: test_stream.py

import requests
import sseclient
import json

FIREBASE_DATABASE_URL = "https://bafetto-d00f2-default-rtdb.europe-west1.firebasedatabase.app"
# Eğer veritabanın public ise SECRET gerekmez
FIREBASE_SECRET = None  # veya gerekiyorsa secret'ı buraya koy

def listen_to_firebase():
    url = f"{FIREBASE_DATABASE_URL}/pendingOrders.json"
    client = sseclient.SSEClient(url)

    for event in client:
        if event.event == 'put' and event.data:
            print("Yeni event geldi!")
            data = json.loads(event.data)
            print(json.dumps(data, indent=2))

if __name__ == "__main__":
    listen_to_firebase()