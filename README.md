# telegram-notifier-for-todoist
Telegram notifier for todoist

## Config

In order to run project you have to create configuration file:

```
{
	"telegram_bot_token" : "xxx",
	"redis": "redis://10.0.0.11:6379/0",
	"subscriber_password" : "ppp"
}
```

**telegram_bot_token*& - your telegram bot token created by bothfather
https://core.telegram.org/bots

**redis** - redis connection string,

**subscriber_password** - password to protect your bot agains subscriptions 
by random users (optional)

## Redis

This project requires redis. You can setup one by running vagrant vm from vagrant folder:

```
vagrant up
```

## Running python app

To run this app you need pipenv installed. Then run:

```
pipenv install
pipenv run telegram_notifier_for_todoist.py
```