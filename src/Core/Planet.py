import logging
from collections import defaultdict


from src.Core.GalaxyCore import GalaxyCore

class Planet(GalaxyCore):
    def __init__(self,loginInfo):
        self.updateInformation(loginInfo)
        self.fleet= defaultdict(dict)
        self.resources = {}


    def updateInformation(self,loginInfo):
        self.ssid = loginInfo['sess_id']
        self.ppy_id=loginInfo['ppy_id']
        self.server = loginInfo['server']
        self.planetId = loginInfo['planetId']
        self.position = loginInfo['position']


    def getInformation(self):
        """
        return a tuple of a tuple of position and planetId
        """
        return self.position,self.planetId
     

    def updateResources(self):
        """
        update the resources and fleet of the planet
        """
        result = self.changePlanet(self.planetId)
        for i in (result['result']['fleetInfo']['FleetsOnPlanet']):
            if i['id']==503 or i['id']==212:
                continue
            self.fleet['ship'+str(i['id'])]=i['count']

        resource= result['result']['buildInfo']['result']['PlanetInfo']
        logging.debug(resource)
        self.resources = {'metal':resource['metal'],
                'crystal':resource['crystal'],
                'deuterium':resource['deuterium'],
                }

    def getFleet(self) -> dict:
        """
        return the fleet of the planet
        """
        return self.fleet

    def getResources(self):
        """
        return the resources of the planet
        """
        return self.resources


