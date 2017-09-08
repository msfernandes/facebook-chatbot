[![Build Status](https://travis-ci.org/msfernandes/facebook-chatbot.svg?branch=master)](https://travis-ci.org/msfernandes/facebook-chatbot)
[![Coverage Status](https://coveralls.io/repos/github/msfernandes/facebook-chatbot/badge.svg?branch=master)](https://coveralls.io/github/msfernandes/facebook-chatbot?branch=master)

# Me Indica - Facebook Chatbot

This chatbot aims to suggest an ideal notebook offer through facebook chat.

The user have to answer some questions to define his profile. After that, the system can suggest the best matches using a Neural Network and previous successful cases.

## Development

Assuming you have `pipenv` installed on you computer, just run:

```
cd application
pipenv install --dev
pipenv shell
./manage.py migrate
```

All offers data used here was obtained from [Lomadee API](https://www.lomadee.com/). In order to get all data, you have to [create an account on Lomadee](https://sso.lomadee.com/register.html?platform=1&lang=pt_BR) and configure three settings variables, creating a file `settings.ini` on `application/facebook_chatbot` containing:

```
[settings]

LOMADEE_APP_TOKEN = your_app_token
LOMADEE_SOURCE_ID = your_source_id
LOMADEE_API_URL = sandbox_or_api_url
```

After setup all Lomadee configurations you can import all data:

```
./manage.py import_data
```

