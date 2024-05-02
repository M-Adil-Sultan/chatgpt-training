# Django ChatGPT Chatbot

![ChatGPT Logo](./images/demo.png)

Welcome to the Django ChatGPT Chatbot repository! This project aims to create a chatbot powered by GPT-3.5, a powerful language model developed by OpenAI. The chatbot is integrated into a Django web application, allowing users to interact with it in real-time and get responses based on natural language inputs.

## Features

- Real-time chat with GPT-3.5 powered Chatbot
- Seamless integration with Django web application
- Natural Language Processing for human-like interactions
- Easily extendable and customizable for specific use cases

## Prerequisites

Before you start using the Django ChatGPT Chatbot, make sure you have the following installed:

- Python (>= 3.6)
- Django (>= 3.0)
- OpenAI GPT-3.5 API key (sign up at [OpenAI website](https://platform.openai.com/api-keys) to get the API key)

## Installation

Follow these steps to set up the Django ChatGPT Chatbot:

1. Clone the repository:

```
git clone https://github.com/nativebrains/chatgpt-training

cd chatgpt-training
```
2. Creating virtual environments
Creation of virtual environments is done by executing the command venv:
For Windows:
Open Command Prompt.
Navigate to the directory where you want to create the virtual environment using cd command.
Run the following command to create a virtual environment named "env":

```
python -m venv venv
```
Run virtual environment:

```
<source> venv\Scripts\activate
```
For Linux and macOS:
Open Terminal.
Navigate to the directory where you want to create the virtual environment using cd command.
Run the following command to create a virtual environment named "env":

```
python3 -m venv venv
```

(Note: On some systems, python command might be used instead of python3)

Activate the virtual environment by running:

```
<source> venv/bin/activate

```

3. Install the required Python packages using pip:

```
pip install -r requirements.txt
```

4. For PRODUCTION make sure you have:
.env (file)
PostgreSQL (configured)  

## Usage

To run the Django ChatGPT Chatbot, follow these steps:

1. Make sure to run migrations of the Django development server:

For LOCAL DEV environment:

```
python manage.py migrate --settings=django_chatbot.settings.dev
```

For PRODUCTION environment:

```
python manage.py migrate --settings=django_chatbot.settings.prod
```
2. To run project of the Django development server:

For LOCAL DEV environment:

```
python manage.py runserver --settings=django_chatbot.settings.dev
```

For PRODUCTION environment:

```
python manage.py runserver --settings=django_chatbot.settings.prod
```

2. Open your web browser and navigate to `http://localhost:8000/` to create a new user account. 

![registor.png](./images/register.png)

3. You'll see the chat interface with the ChatGPT-powered chatbot ready to interact with you!

4. To create a `admin` user:

```python
python manage.py createsuperuser
```
You will be prompted to enter the details for the new admin user:

- **Username**: Choose a username for the admin user.
- **Email address**: Enter the email address for the admin user (optional).
- **Password**: Choose a strong password for the admin user. Note that the password will not be visible as you type it for security reasons.

After entering the required information, press Enter.

If everything is successful, you will see a message confirming that the admin user has been created:
```python
Superuser created successfully.
```
Congratulations! You have now created a Django admin user. You can now use this username and password to log in to the Django admin interface by accessing the `/admin/` URL .

![admin.png](./images/admin.png)

![admin-in.png](./images/admin-in.png)

5. To `logout`, navigate to `http://localhost:8000/logout`. You will be logged out and redirected to the login page.

![login.png](./images/login.png)

## Contributing

I welcome contributions to the Django ChatGPT Chatbot repository! If you find any issues, have suggestions for improvements, or want to add new features, feel free to submit a pull request.

## License

The Django ChatGPT Chatbot is released under the [MIT License](LICENSE).

## Acknowledgments

I would like to thank the developers and contributors of the following libraries and tools, which made this project possible:

- Django: https://www.djangoproject.com/
- OpenAI GPT-3.5: https://openai.com

Happy chatting with ChatGPT! 🤖💬