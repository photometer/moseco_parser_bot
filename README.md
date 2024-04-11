# moseco_parser_bot

## Parser for pollutants' concentrations from [Mosecomonitoring]

It is a parser that collects hourly data on PM<sub>10</sub>, PM<sub>2.5</sub>, NO<sub>2</sub>, NO, O<sub>3</sub>, SO<sub>2</sub>, CO concentrations in real time from [Mosecomonitoring] and adds it to Google Spreadsheets document. If errors occur, program sends them to you by Telegram Bot.
> Note: list of pollutants and their order in sheets can be changed in `PARAMETERS` variable in `services.py` file.


## Technologies

- Python;
- Scrapy;
- Google Drive API and Google Sheets API;
- Telegram bot.


<details><summary><h2>Installation and launch</h2></summary>

- Clone the repository and go to its folder via command line:

    ```bash
    git clone https://github.com/photometer/moseco_parser_bot
    cd moseco_parser_bot
   ```

- Create and activate virtual environment

    * On Linux/MacOS:

        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

    * On Windows:

        ```bash
        python -m venv venv
        source venv/scripts/activate
        ```

- In venv upgrade package manager `pip` and install requirements (Windows):

    ```bash
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    ```

- Create `.env` file and fill it with necessary values:

    ```env
    TYPE=<type>
    PROJECT_ID=<project_id>
    PRIVATE_KEY_ID=<private_key_id>
    PRIVATE_KEY=<private_key>
    CLIENT_EMAIL=<client_email>
    CLIENT_ID=<client_id>
    AUTH_URI=<auth_uri>
    TOKEN_URI=<token_uri>
    AUTH_PROVIDER_X509_CERT_URL=<auth_provider_x509_cert_url>
    CLIENT_X509_CERT_URL=<client_x509_cert_url>
    EMAIL=<email that will be allowed to edit the spreadsheet>
    SPREADSHEET_ID=<spreadsheet id, fill it after creating the spreadsheet!>
    TELEGRAM_TOKEN=<telegram_token>
    TELEGRAM_CHAT_ID=<your_telegram_id>
    ```

    > Note: get all variables before `EMAIL` from service account access key to Google Cloud Platform JSON-file, `TELEGRAM_TOKEN` from [@BotFather](https://t.me/BotFather) and `TELEGRAM_CHAT_ID` from [@userinfobot](https://t.me/userinfobot).

- All launch options shold be done in `./moseco/moseco` directory:

    ```bash
    cd moseco/moseco
    ```

- Create spreasheet and get its id:

    ```bash
    python spreadsheets.py -c
    ```

    > Note: copy spreasheet id from output and add it to `.env` file

- Launch parsing + updating the spreadsheet

    * If you want one-time execution:

        ```bash
        scrapy crawl moseco
        ```

    * Continious execution on local PC:

        ```bash
        python main.py
        ```

        > Note: Requests to [Mosecomonitoring] will be sent hourly (you can change this time in seconds in `RETRY_TIME` variable). If there are errors during crawling, last error wil be sent to you via Telegram bot. Don't forget to activate the bot in order to receive messages!
        > 
        > In `BOT_MESSAGE_TIMES` there are hours during which bot will send a message about how many times crawling has been done from the previous such message to track the continuity of the process. You can change hours or disable info message setting `()`.

</details>

---


## Author
[Androsova Elizaveta](https://github.com/photometer) :wink:


## License
BSD-3 Clause


[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job)

   [Mosecomonitoring]: <https://mosecom.mos.ru/>
