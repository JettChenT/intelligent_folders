import asyncio
import uvicorn
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

def run_server(port):
    config = uvicorn.Config(app, host="127.0.0.1", port=port)
    server = uvicorn.Server(config)
    server.serve()

def main():
    port = 8000
    try:
        run_server(port)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"Port {port} is already in use. Please choose another port.")
        else:
            raise

    # Add any additional code you want to run after starting the server here
    print("Server is running...")

if __name__ == "__main__":
    asyncio.run(main())
