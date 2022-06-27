import time as tm
import traceback as tb
import math as mt
import sys as ss
import os
import asyncio
import websockets
import json

ss.path += [os.path.abspath(relPath) for relPath in  ('..',)]
import parameters as pm

class HardcodedClient:
    def __init__ (self):
        self.steeringAngle = 0
        self.halfApertureAngle = False

        with open(pm.sampleFileName, 'a') as self.sampleFile:
            asyncio.run(self.connect())

    async def connect(self):
        async with websockets.connect('ws://localhost:8080/') as websocket:
            self.websocket = websocket
            while True:
                await self.input()
                self.sweep()
                await self.output()
                self.logTraining()
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

    def sonarSweep(self):
        obstacleDistances = [pm.finity for sectorIndex in range(3)]
        obstacleAngles = [0 for sectorIndex in range(3)]

        for sectorIndex in(-1, 0, 1):
            sonarDistance = self.sonarDistances[sectorIndex]
            sonarAngle = 2 * self.halfMiddleApertureAngle * sectorIndex

            if sonarDistance < obstacleDistances[sectorIndex]:
                obstacleDistances[sectorIndex] = sonarDistance
                obstacleAngles[sectorIndex] = sonarAngle

        if obstacleDistances[-1] > obstacleDistances[0]:
            leftIndex = -1
        else:
            leftIndex = 0

        if obstacleDistances[1] > obstacleDistances[0]:
            rightIndex = 1
        else:
            rightIndex = 0

        self.steeringAngle = (obstacleAngles[leftIndex] + obstacleAngles[rightIndex]) / 2
        self.targetVelocity = pm.getTargetVelocity(self.steeringAngle)

    def sweep(self):
        if hasattr(self, 'lidarDistances'):
            self.lidarSweep()
        else:
            self.sonarSweep()

    async def output(self):
        actuators = {
            'type': 'updateStats',
            'steeringAngle': self.steeringAngle,
            'targetVelocity': self.targetVelocity
        }
        await self.websocket.send(json.dumps(actuators))

    def logLidarTraining(self):
        sample = [pm.finity for entryIndex in range(pm.lidarInputDim + 1)]

        for lidarAngle in range(-self.halfApertureAngle, self.halfApertureAngle):
            sectorIndex = round(lidarAngle / self.sectorAngle)
            sample[sectorIndex] = min(sample[sectorIndex], self.lidarDistances[lidarAngle])

        sample[-1] = self.steeringAngle
        print(*sample, file = self.sampleFile)

    def logSonarTraining(self):
        sample = [pm.finity for entryIndex in range(pm.sonarInputDim + 1)]

        for entryIndex, sectorIndex in((2, -1), (0, 0), (1, 1)):
            sample[entryIndex] = self.sonarDistances[sectorIndex]

        sample[-1] = self.steeringAngle
        print(*sample, file = self.sampleFile)

    def logTraining(self):
        if hasattr(self, 'lidarDistances'):
            self.logLidarTraining()
        else:
            self.logSonarTraining()

HardcodedClient()
