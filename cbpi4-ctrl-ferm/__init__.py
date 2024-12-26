
# -*- coding: utf-8 -*-
import os
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.controller.fermentation_controller import FermentationController
from cbpi.api import *

logger = logging.getLogger(__name__)


class FermentorPID(CBPiFermenterLogic):
    
    async def run(self):
        try:
            self.heater_offset_min = float(self.props.get("HeaterOffsetOn", 0))
            self.heater_offset_max = float(self.props.get("HeaterOffsetOff", 0))
            self.cooler_offset_min = float(self.props.get("CoolerOffsetOn", 0))
            self.cooler_offset_max = float(self.props.get("CoolerOffsetOff", 0))
            self.heater_max_power = int(self.props.get("HeaterMaxPower", 100))
            self.cooler_max_power = int(self.props.get("CoolerMaxPower", 100))
            
            self.fermenter = self.get_fermenter(self.id)
            self.heater = self.fermenter.heater
            self.cooler = self.fermenter.cooler

            heater = self.cbpi.actor.find_by_id(self.heater)
            cooler = self.cbpi.actor.find_by_id(self.cooler)

            while self.running == True:
                
                beer_value = float(self.get_sensor_value(self.fermenter.beer_sensor).get("value"))
                sensor_value = float(self.get_sensor_value(self.fermenter.chamber_sensor).get("value"))
                target_temp = float(self.get_fermenter_target_temp(self.id))

                try:
                    heater_state = heater.instance.state
                except:
                    heater_state= False
                try:
                    cooler_state = cooler.instance.state
                except:
                    cooler_state= False

                if sensor_value + self.heater_offset_min <= target_temp:
                    if self.heater and (heater_state == False):
                        await self.actor_on(self.heater, self.heater_max_power)
                    
                if sensor_value + self.heater_offset_max >= target_temp:
                    if self.heater and (heater_state == True):
                        await self.actor_off(self.heater)

                if sensor_value >=  self.cooler_offset_min + target_temp:
                    if self.cooler and (cooler_state == False):
                        await self.actor_on(self.cooler, self.cooler_max_power)
                    
                if sensor_value <= self.cooler_offset_max + target_temp:
                    if self.cooler and (cooler_state == True):
                        await self.actor_off(self.cooler)

                await asyncio.sleep(1)

        except asyncio.CancelledError as e:
            pass
        except Exception as e:
            logging.error("Fermenter Hysteresis Error {}".format(e))
        finally:
            self.running = False
            if self.heater:
                await self.actor_off(self.heater)
            if self.cooler:
                await self.actor_off(self.cooler)


@parameters([Property.Number(label="HeaterOffsetOn", configurable=True, description="Offset as decimal number when the heater is switched on. Should be greater then 'HeaterOffsetOff'. For example a value of 2 switches on the heater if the current temperature is 2 degrees below the target temperature"),
             Property.Number(label="HeaterOffsetOff", configurable=True, description="Offset as decimal number when the heater is switched off. Should be smaller then 'HeaterOffsetOn'. For example a value of 1 switches off the heater if the current temperature is 1 degree below the target temperature"),
             Property.Number(label="CoolerOffsetOn", configurable=True, description="Offset as decimal number when the cooler is switched on. Should be greater then 'CoolerOffsetOff'. For example a value of 2 switches on the cooler if the current temperature is 2 degrees below the target temperature"),
             Property.Number(label="CoolerOffsetOff", configurable=True, description="Offset as decimal number when the cooler is switched off. Should be smaller then 'CoolerOffsetOn'. For example a value of 1 switches off the cooler if the current temperature is 1 degree below the target temperature"),
             Property.Number(label="SpundingOffsetOpen", configurable=True, description="Offset above target pressure as decimal number when the valve is opened"),
             Property.Select(label="ValveRelease", options=[1,2,3,4,5],description="Valve Release time in seconds"),
             Property.Select(label="Pause", options=[1,2,3,4,5],description="Pause time in seconds between valve release"),
             Property.Select(label="AutoStart", options=["Yes","No"],description="Autostart Fermenter on cbpi start"),
             Property.Sensor(label="sensor2",description="Optional Sensor for LCDisplay(e.g. iSpindle)")])


def setup(cbpi):
    cbpi.plugin.register("Fermentor PID", FermentorPID)
    pass
