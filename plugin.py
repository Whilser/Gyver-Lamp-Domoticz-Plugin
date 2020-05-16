

"""
<plugin key="GyverLamp" name="GyverLamp domoticz plugin" author="Whilser" version="0.1.0" wikilink="" externallink="">
    <description>
        <h2>GyverLamp </h2><br/>
        <h3>Настройка</h3>
        Введите идентификатор лампы. Если ID лампы неизвестен, просто оставьте в поле идентификатора значение 0, это запустит процедуру поиска лампы в сети. <br/>
        По окончании поиска ID лампы отобразится в Журнале. <br/>

    </description>
    <params>
        <param field="Mode1" label="ID" width="300px" required="true" default="0"/>
        <param field="Mode2" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="True" />
            </options>
        </param>
    </params>
</plugin>
"""

import os
import sys
import os.path
import json
import socket

import Domoticz

class BasePlugin:

    UNIT_LAMP = 1
    UNIT_SPEED = 2
    UNIT_SCALE = 3
    UNIT_EFFECTS = 4

    discovered = False
    id = 1
    IP = ''
    port = 0

    def __init__(self):

        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters['Mode2'] == 'Debug': Domoticz.Debugging(1)

        if Parameters['Mode1'] == '0':
            self.discover()
            return

        self.loadConfig()
        self.createLamp()

        DumpConfigToLog()
        Domoticz.Heartbeat(60)

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level)+ ", Color: "+str(Color))

        if Unit == self.UNIT_EFFECTS:
            self.HandleEffects(Level)
            return

        Level = max(min(Level, 100), 1)
        if not self.discover(Parameters['Mode1']): return

        try:
            if Command == 'On':
                reply = self.sendCommand('P_ON').split()
                if reply[5] == '1':
                    Devices[Unit].Update(nValue=1, sValue='On', TimedOut = False)
                    if self.UNIT_SPEED in Devices: Devices[self.UNIT_SPEED].Update(nValue=1, sValue='On')
                    if self.UNIT_SCALE in Devices: Devices[self.UNIT_SCALE].Update(nValue=1, sValue='On')
                    if self.UNIT_EFFECTS in Devices: Devices[self.UNIT_EFFECTS].Update(nValue=1, sValue=Devices[self.UNIT_EFFECTS].sValue)

            elif Command == 'Off':
                reply = self.sendCommand('P_OFF').split()
                if reply[5] == '0':
                    Devices[Unit].Update(nValue=0, sValue='Off', TimedOut = False)
                    if self.UNIT_SPEED in Devices: Devices[self.UNIT_SPEED].Update(nValue=0, sValue='0')
                    if self.UNIT_SCALE in Devices: Devices[self.UNIT_SCALE].Update(nValue=0, sValue='0')
                    if self.UNIT_EFFECTS in Devices: Devices[self.UNIT_EFFECTS].Update(nValue=0, sValue=Devices[self.UNIT_EFFECTS].sValue)

            elif Command == 'Set Level':
                if (Unit == self.UNIT_LAMP):
                  reply = self.sendCommand('BRI ' + str(Level)).split()
                  if reply[0] == 'BRI': Devices[Unit].Update(nValue=1, sValue=reply[1], TimedOut = False)

                if (Unit == self.UNIT_SCALE):
                  reply = self.sendCommand('SCA ' + str(Level)).split()
                  if reply[0] == 'SCA': Devices[Unit].Update(nValue=1, sValue=reply[1], TimedOut = False)

                if (Unit == self.UNIT_SPEED):
                  reply = self.sendCommand('SPD ' + str(Level)).split()
                  if reply[0] == 'SPD': Devices[Unit].Update(nValue=1, sValue=reply[1], TimedOut = False)

        except Exception as e:
            Domoticz.Error('Error send command to {0} with IP {1}. Device is not responding, check power/network connection. Errror: {2}'.format(Parameters['Name'], self.IP, e.__class__))
            Devices[Unit].Update(nValue=Devices[Unit].nValue, sValue=Devices[Unit].sValue, TimedOut = True)

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

        if Parameters['Mode1'] == '0': return

        try:
            if (self.UNIT_LAMP in Devices):
                reply = self.sendCommand("GET").split()

                if (reply[5] == "1"):
                    if ((Devices[self.UNIT_LAMP].sValue != 'On') or (Devices[self.UNIT_LAMP].nValue != 1) or (Devices[self.UNIT_LAMP].TimedOut == True)):
                        Devices[self.UNIT_LAMP].Update(nValue=1, sValue='On', TimedOut = False)

                    if (self.UNIT_SCALE in Devices):
                      if ((Devices[self.UNIT_SCALE].sValue != 'On') or (Devices[self.UNIT_SCALE].nValue != 1) or (Devices[self.UNIT_SCALE].TimedOut == True)):
                        Devices[self.UNIT_SCALE].Update(nValue=1, sValue=Devices[self.UNIT_SCALE].sValue, TimedOut = False)

                    if (self.UNIT_SPEED in Devices):
                      if ((Devices[self.UNIT_SPEED].sValue != 'On') or (Devices[self.UNIT_SPEED].nValue != 1) or (Devices[self.UNIT_SPEED].TimedOut == True)):
                        Devices[self.UNIT_SPEED].Update(nValue=1, sValue=Devices[self.UNIT_SPEED].sValue, TimedOut = False)

                if (reply[5] == "0"):
                    if ((Devices[self.UNIT_LAMP].sValue != 'Off') or (Devices[self.UNIT_LAMP].nValue != 0) or (Devices[self.UNIT_LAMP].TimedOut == True)):
                        Devices[self.UNIT_LAMP].Update(nValue=0, sValue='Off', TimedOut = False)

                    if (self.UNIT_SCALE in Devices):
                      if ((Devices[self.UNIT_SCALE].sValue != 'Off') or (Devices[self.UNIT_SCALE].nValue != 0) or (Devices[self.UNIT_SCALE].TimedOut == True)):
                        Devices[self.UNIT_SCALE].Update(nValue=0, sValue=reply[4], TimedOut = False)

                    if (self.UNIT_SPEED in Devices):
                      if ((Devices[self.UNIT_SPEED].sValue != 'Off') or (Devices[self.UNIT_SPEED].nValue != 0) or (Devices[self.UNIT_SPEED].TimedOut == True)):
                        Devices[self.UNIT_SPEED].Update(nValue=0, sValue=reply[3], TimedOut = False)

        except Exception as e:
            Devices[self.UNIT_LAMP].Update(nValue=Devices[self.UNIT_LAMP].nValue, sValue=Devices[self.UNIT_LAMP].sValue, TimedOut = True)
            Devices[self.UNIT_SCALE].Update(nValue=Devices[self.UNIT_SCALE].nValue, sValue=Devices[self.UNIT_SCALE].sValue, TimedOut = True)
            Devices[self.UNIT_SPEED].Update(nValue=Devices[self.UNIT_SPEED].nValue, sValue=Devices[self.UNIT_SPEED].sValue, TimedOut = True)
            Devices[self.UNIT_EFFECTS].Update(nValue=Devices[self.UNIT_EFFECTS].nValue, sValue=Devices[self.UNIT_EFFECTS].sValue, TimedOut = True)

    def HandleEffects(self, Level):

        if (Level > 0):
            reply = self.sendCommand("EFF "+str((Level/10)-1))
            Domoticz.Debug('Reply: '+reply)
            if self.UNIT_EFFECTS in Devices: Devices[self.UNIT_EFFECTS].Update(nValue=1, sValue=str(Level))

            reply = self.sendCommand('P_ON').split()
            if reply[5] == '1':
                if (self.UNIT_LAMP in Devices): Devices[self.UNIT_LAMP].Update(nValue=1, sValue='On', TimedOut = False)
                if self.UNIT_SPEED in Devices: Devices[self.UNIT_SPEED].Update(nValue=1, sValue='On', TimedOut = False)
                if self.UNIT_SCALE in Devices: Devices[self.UNIT_SCALE].Update(nValue=1, sValue='On', TimedOut = False)

    def loadConfig(self):
        config_Path = os.path.join(str(Parameters['HomeFolder']), "GyverLamp"+str(Parameters["HardwareID"])+'.json')

        if os.path.isfile(config_Path):
            Domoticz.Debug('Loading config from '+config_Path)

            with open(config_Path) as json_file:
                config = json.load(json_file)

            self.IP = config['IP']
            self.deviceID = config['DeviceID']
            self.port = config['Port']

        else: self.discover(Parameters['Mode1'])

    def createLamp(self):

        if self.UNIT_LAMP not in Devices:  Domoticz.Device(Name='lamp',  Unit=self.UNIT_LAMP, Type=244, Subtype=73, Switchtype=7, Used=1).Create()
        if self.UNIT_SPEED not in Devices: Domoticz.Device(Name='Speed', Unit=self.UNIT_SPEED, Type=244, Subtype=73, Switchtype=7, Used=1).Create()
        if self.UNIT_SCALE not in Devices: Domoticz.Device(Name='Scale', Unit=self.UNIT_SCALE, Type=244, Subtype=73, Switchtype=7, Used=1).Create()

        if (self.UNIT_EFFECTS not in Devices):
            fx_list = self.sendCommand("FX_GET")
            Options = { "Effects": "|||||", "LevelNames": fx_list, "LevelOffHidden": "true", "SelectorStyle": "1" }
            Domoticz.Device(Name="Effects", Unit=self.UNIT_EFFECTS, Type=244, Subtype=62 , Switchtype=18, Options = Options, Used=1).Create()

    def sendCommand(self, command):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(command.encode(), (self.IP, self.port))
            data = s.recvfrom(1024)
            s.close()
            self.id += 1

            Domoticz.Debug('Command sent: '+command)
            Domoticz.Debug("Reply received: {}".format(data[0].decode()))
            return data[0].decode()

        except Exception as e:
            Domoticz.Error('Error send command {0} to {1} with IP {2} and port {3}. Device is not responding, check power/network connection. Errror: {4}'.format(command, Parameters['Name'], self.IP, self.port, e.__class__))

            for x in Devices:
                if  Devices[x].TimedOut == False: Devices[x].Update(nValue=Devices[x].nValue, sValue=Devices[x].sValue, TimedOut = True)

            self.discovered = False
            return "Error"

    def discover(self, deviceID = None):
        if self.discovered: return True

        if len(self.IP) > 0:
            Domoticz.Debug('Loaded saved configuration.')
            Domoticz.Log('Attempt to connect to device with ID: {0}, IP address: {1} '.format(self.deviceID, self.IP))

            status = self.sendCommand("DEB").split()
            if (status[0] != "OK"):
                Domoticz.Log('Could not connect to {0} with IP {1}, starting discover.'.format(Parameters['Name'], self.IP))
                self.IP = ''
            else:
                Domoticz.Log('Connected to device ID: {0} with IP address: {1}'.format(self.deviceID, self.IP))
                self.discovered = True
                return self.discovered

        Domoticz.Log('Starting discover with Device ID: {}.'.format(deviceID))
        self.discovered = False
        timeout = 5
        addr = '<broadcast>'
        discoveredDevice = None
        helobytes = 'DISCOVER'.encode()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(timeout)
        s.sendto(helobytes, (addr, 8888))

        while True:
            try:
                data, addr = s.recvfrom(1024)

                reply = json.loads(data.decode())
                self.deviceID = reply["deviceID"]
                self.IP = reply["IP"]
                self.port = reply["port"]

                if deviceID is None:
                    Domoticz.Log('Discovered. Device ID: {0}, IP: {1}, Port: {2}'.format(self.deviceID, self.IP, self.port))

                else:
                    if self.deviceID == deviceID:
                        Domoticz.Log('Connected to device ID: {0} with IP address: {1}'.format(self.deviceID, self.IP))

                        config = {
                            "DeviceID": self.deviceID,
                            "IP": self.IP,
                            "Port": self.port
                        }

                        config_Path = os.path.join(str(Parameters['HomeFolder']), "GyverLamp"+str(Parameters["HardwareID"])+'.json')
                        with open(config_Path, 'w') as outfile:
                            if json.dump(config, outfile, indent=4): Domoticz.Debug('Config file was saved.')

                    self.discovered = True

                    for x in Devices:
                        if  Devices[x].TimedOut == True: Devices[x].Update(nValue=Devices[x].nValue, sValue=Devices[x].sValue, TimedOut = False)

                    return self.discovered

            except socket.timeout:
                Domoticz.Log('Discovery done')
                if ((deviceID is not None) and (self.discovered == False)):
                    Domoticz.Error('Could not discover with Device ID = {0}. Check power/network/Device ID.'.format(deviceID))
                    self.IP = ''

                    for x in Devices:
                        if  Devices[x].TimedOut == False: Devices[x].Update(nValue=Devices[x].nValue, sValue=Devices[x].sValue, TimedOut = True)

                return self.discovered
            except Exception as ex:
                Domoticz.Error('Error while reading discover results: {0}'.format(ex))
                break

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
        Domoticz.Debug("Device TimedOut: " + str(Devices[x].TimedOut))
    return
