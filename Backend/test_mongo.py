from pymongo import MongoClient

uri = "mongodb+srv://rohit98kumar:War14Par%40@cluster0.u3tzcib.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(uri)
    client.admin.command('ping')
    print("✅ Successfully connected to MongoDB Atlas!")
except Exception as e:
    print("❌ Connection failed:", e)
    exit(1)