# Gyver Lamp Domoticz Plugin
Плагин поддержки Gyver Lamp для системы автоматизации Domoticz
Работает с версией прошивки https://github.com/Whilser/GyverLamp

## Установка:
```
cd domoticz/plugins
git clone https://github.com/Whilser/Gyver-Lamp-Domoticz-Plugin.git GyverLamp
sudo service domoticz restart
```
## Обновление:
```cd domoticz/plugins/GyverLamp
git pull
sudo service domoticz restart
```
## Настройка
В панеле настройки оборудования введите идентификатор лампы. Если ID лампы неизвестен, просто оставьте в поле идентификатора значение 0, это запустит процедуру поиска лампы в сети. По окончании поиска ID лампы отобразится в Журнале.
