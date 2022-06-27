import asyncio
import websockets
from simpylc import world
import json

loop = asyncio.get_event_loop()

class WebSocketServer:
    def __init__(self):
        with open('server.samples', 'a') as self.logFile:
            asyncio.set_event_loop(loop)
            websocketServer = websockets.serve(self.onConnection, 'localhost', 8080)
            loop.run_until_complete(websocketServer)
            loop.run_forever()

    async def onConnection(self, websocket):
        async for message in websocket:
            data = json.loads(message)

            if data['type'] == 'readSensors':
                sensors = {
                    'halfApertureAngle': world.visualisation.scanner.halfApertureAngle,
                    'halfMiddleApertureAngle': world.visualisation.scanner.halfMiddleApertureAngle
                } | (
                    {'lidarDistances': world.visualisation.scanner.lidarDistances}
                    if hasattr (world.visualisation.scanner, 'lidarDistances') else
                        {'sonarDistances': world.visualisation.scanner.sonarDistances}
                )
                await websocket.send(json.dumps(sensors))

            if data['type'] == 'updateStats':
                print('New target velocity: ' + str(data['targetVelocity']) + ', new steering angle: ' + str(data['steeringAngle']))
                world.physics.targetVelocity.set(data['targetVelocity'])
                world.physics.steeringAngle.set(data['steeringAngle'])

            if data['type'] == 'log':
                self.logFile.write(data['message'] + '\n')
