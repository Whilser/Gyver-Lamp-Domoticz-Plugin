# Gyver Lamp Domoticz Plugin
Плагин поддержки Gyver Lamp для системы автоматизации Domoticz. 
Работает с версией прошивки https://github.com/Whilser/GyverLamp

![Gyver lamp](https://raw.githubusercontent.com/Whilser/Gyver-Lamp-Domoticz-Plugin/master/img/lamp.png)

![Effects](https://raw.githubusercontent.com/Whilser/Gyver-Lamp-Domoticz-Plugin/master/img/effects.png)

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
В панеле настройки оборудования введите идентификатор лампы. Если ID лампы неизвестен, просто оставьте в поле идентификатора значение 0, это запустит процедуру поиска лампы в сети. По окончании поиска ID лампы отобразится в Журнале.  Идентификатор лампы можно также посмотреть в веб интерфейсе на вкладке "Инфо" в графе ID лампы. 

![Setup](https://raw.githubusercontent.com/Whilser/Gyver-Lamp-Domoticz-Plugin/master/img/Setup.png)

## В планах доработки

- [ ] Синхронизация "бегунков" масштабирования и скорости
- [ ] Расширение диапазона масштабирования с 0-100 в диапазон 0-255
