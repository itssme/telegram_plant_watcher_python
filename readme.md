# Telegram Plant Watcher
Simple telegram bot that sends me images of my plant.

## Installation
Install python3, opencv and pip3 on your system.


Then download and install this project.
```bash
git clone https://github.com/itssme/telegram_plant_watcher_python.git
sudo python3 setup.py install
```

You will be asked for a bot token which will be stored in the systemd file for the service.

Then you should be able to enable and then start the service:
```bash
sudo service plant_watcher enable
sudo service plant_watcher start
```

## Updates
Simply stop the service
```bash
sudo service plant_watcher stop
```

and run the installation again.

# Usage

If you want to start the service type:
```bash
sudo service plant_watcher stop
```

If you want to stop the service type:
```bash
sudo service plant_watcher stop
```

After you started the service add the bot in telegram or add it to a group etc.
Then type ```/register``` once and the bot will memories your chat id and send you messages.

![/register command demonstrated](https://i.imgur.com/kAS5ip9.png "/register command demonstrated")

Then the bot should send you an image of your plant every day at 12am.

![picture of the bot sending an image](https://i.imgur.com/eX0jQQv.png "picture of the bot sending an image")

You can also see all commands with ```/help```

![/help command demonstrated](https://i.imgur.com/ZIbJQ33.png "/help command demonstrated")
