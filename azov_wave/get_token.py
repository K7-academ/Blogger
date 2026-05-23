import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Вказуємо область доступу: повний доступ до Blogger
SCOPES = ['https://www.googleapis.com/auth/blogger']

def main():
    if not os.path.exists('credentials.json'):
        print("Помилка: Файл 'credentials.json' не знайдено.")
        print("Вам потрібно завантажити його з Google Cloud Console (тип: Desktop App).")
        return

    print("Запуск процесу авторизації...")
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    
    # Відкриває браузер для авторизації
    creds = flow.run_local_server(port=0)

    # Зберігає отриманий токен у файл
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())
    
    print("\n✅ Успіх! Файл 'token.json' створено.")
    print("Тепер ви можете скопіювати вміст 'token.json' і додати його у GitHub Secrets.")

if __name__ == '__main__':
    main()
