import asyncio
import threading
import uuid
import os
import shutil
import websockets
from MyFlaskApp import MyFlaskApp
from globals import emulator_connections, event_emitter


async def websocket_server():
    async def handle_client(websocket):
        client_id = str(uuid.uuid4())

        print(f"Emulator websocket connected: {client_id}")

        emulator_connections[client_id] = websocket

        try:
            while True:
                message = await websocket.recv()
                assert isinstance(message, str), f"Received non-string message: {message}, Type: ({type(message)})"
                #print(f"Received message from {client_id}: {message}")

                event_emitter.emit("message_received", client_id, message)

                if not hasattr(emulator_connections[client_id],"fake_port"):
                    fake_port = message.split('port":"')[-1].split('",')[0]
                    print(f"Fake port: {fake_port}" if fake_port else "No fake port found")
                    if fake_port:
                        emulator_connections[client_id].fake_port = fake_port
                    fake_name = message.split('Name":"')[-1].split('",')[0]
                    print(f"Fake name: {fake_name}" if fake_name else "No fake name found")
                    if fake_name:
                        emulator_connections[client_id].fake_name = fake_name
                    fake_hwid = message.split('Hwid":"')[-1].split('",')[0]
                    print(f"Fake Hwid: {fake_hwid}" if fake_hwid else "No fake Hwid found")
                    if fake_hwid:
                        emulator_connections[client_id].fake_hwid = fake_hwid
                else:
                    print(f"Fake port: {emulator_connections[client_id].fake_port}")
                    print(f"Fake name: {emulator_connections[client_id].fake_name}")
                    print(f"Fake Hwid: {emulator_connections[client_id].fake_hwid}")
                #await websocket.send(f"Echo from {client_id}: {message}")
        except websockets.exceptions.ConnectionClosed as e:
            # Handle disconnection gracefully
            print(f"Emulator '{client_id}' has been disconnected.")
        except Exception as e:
            # Handle any other exception (unexpected disconnection, etc.)
            print(f"Error with client {client_id}: {e}")
        finally:
             if client_id in emulator_connections:
                del emulator_connections[client_id]

    try:
        server = await websockets.serve(handle_client, "localhost", 8001)
        await server.wait_closed()
    except Exception as e:
        print(f"WebSocket server error: {e}")

def start_websocket():
    print("Starting WebSocket server...")
    asyncio.run(websocket_server())

websocket_thread = threading.Thread(target=start_websocket)
websocket_thread.daemon = True  # Make it a daemon thread to exit with the main program
websocket_thread.start()


# moved this up here so we can pass the app to the PrinterStatusService
# Basic app setup

app = MyFlaskApp()

# own thread
with app.app_context():
    try:
        # Define directory paths for uploads and tempcsv
        uploads_folder = os.path.abspath('../uploads')
        tempcsv = os.path.abspath('../tempcsv')
        # Check if directories exist and handle them accordingly
        for folder in [uploads_folder, tempcsv]:
            if os.path.exists(folder):
                # Remove the folder and all its contents
                shutil.rmtree(folder)
                app.logger.info(f"{folder} removed and will be recreated.")
            # Recreate the folder
            os.makedirs(folder)
            app.logger.info(f"{folder} recreated as an empty directory.")

    except Exception as e:
        # Log any exceptions for troubleshooting
        app.handle_errors_and_logging(e)

def run_socketio(app):
    try:
        app.socketio.run(app, allow_unsafe_werkzeug=True)
    except Exception as e:
        app.handle_errors_and_logging(e)

if __name__ == "__main__":
    # If hits last line in GCode file: 
        # query for status ("done printing"), update. Use frontend to update status to "ready" once user removes print from plate. 
        # Before sending to printer, query for status. If error, throw error. 
    # since we are using socketio, we need to use socketio.run instead of app.run
    # which passes the app anyways
    run_socketio(app)  # Replace app.run with socketio.run
