import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK (Only do this once)
cred = credentials.Certificate('ecommerce/firebase/serviceAccountKey.json')
firebase_admin.initialize_app(cred)
