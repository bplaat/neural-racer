import time as tm
import traceback as tb
import math as mt
import sys as ss
import os
import asyncio
import websockets
import json
import pickle

ss.path += [os.path.abspath(relPath) for relPath in  ('..',)]
import parameters as pm

class NeuralClient:
    def __init__ (self):
        self.steeringAngle = 0
        self.halfApertureAngle = False

        with open('neural_network_func', 'rb') as handle:
            self.neuralNetworkFunc = pickle.load(handle)

        with open(pm.sampleFileName, 'w') as self.sampleFile:
            asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect('ws://localhost:8080/') as websocket:
            self.websocket = websocket
            while True:
                await self.input()
                self.sweep()
                await self.output()
                await asyncio.sleep(0.02)

    async def input(self):
        await self.websocket.send(json.dumps({ 'type': 'readSensors' }))
        sensors = json.loads(await self.websocket.recv())

        if not self.halfApertureAngle:
            self.halfApertureAngle = sensors['halfApertureAngle']
            self.sectorAngle = 2 * self.halfApertureAngle / pm.lidarInputDim
            self.halfMiddleApertureAngle = sensors['halfMiddleApertureAngle']

        if 'lidarDistances' in sensors:
            self.lidarDistances = sensors['lidarDistances']
        else:
            self.sonarDistances = sensors['sonarDistances']

    def lidarSweep(self):
        nearestObstacleDistance = pm.finity
        nearestObstacleAngle = 0

        nextObstacleDistance = pm.finity
        nextObstacleAngle = 0

        for lidarAngle in range(-self.halfApertureAngle, self.halfApertureAngle):
            lidarDistance = self.lidarDistances[lidarAngle]

            if lidarDistance < nearestObstacleDistance:
                nextObstacleDistance =  nearestObstacleDistance
                nextObstacleAngle = nearestObstacleAngle

                nearestObstacleDistance = lidarDistance
                nearestObstacleAngle = lidarAngle

            elif lidarDistance < nextObstacleDistance:
                nextObstacleDistance = lidarDistance
                nextObstacleAngle = lidarAngle

        targetObstacleDistance = (nearestObstacleDistance + nextObstacleDistance) / 2

        self.steeringAngle = (nearestObstacleAngle + nextObstacleAngle) / 2
        self.targetVelocity = pm.getTargetVelocity(self.steeringAngle)

    def sweep(self):
        sample = [pm.finity for entryIndex in range(pm.lidarInputDim)]

        for lidarAngle in range(-self.halfApertureAngle, self.halfApertureAngle):
            sectorIndex = round(lidarAngle / self.sectorAngle)
            sample[sectorIndex] = min(sample[sectorIndex], self.lidarDistances[lidarAngle])

        self.steeringAngle = self.neuralNetworkFunc.predict([sample])[0]
        self.targetVelocity = pm.getTargetVelocity(self.steeringAngle)

    async def output(self):
        actuators = {
            'type': 'updateStats',
            'steeringAngle': self.steeringAngle,
            'targetVelocity': self.targetVelocity
        }
        await self.websocket.send(json.dumps(actuators))

NeuralClient()
