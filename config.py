import os


class FastAPIConfig():
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = os.getenv('PORT', 5080)


class DatabaseConfig():
    POSTGRES_USER = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB_HOST = os.getenv('POSTGRES_DB_HOST')
    POSTGRES_DB_PORT = os.getenv('POSTGRES_DB_PORT')
    POSTGRES_DB = os.getenv('POSTGRES_DB')


class RedisConfig():
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    REDIS_PASS = os.getenv('REDIS_PASS')
    REDIS_DB = os.getenv('REDIS_DB')


class RedisEventsConfig():
    REDIS_HOST = os.getenv('REDIS_EV_HOST')
    REDIS_PORT = os.getenv('REDIS_EV_PORT')
    REDIS_PASS = os.getenv('REDIS_EV_PASS')
    REDIS_DB = os.getenv('REDIS_EV_DB')


class AuthConfig():
    SECRET_KEY = os.getenv('SECRET_KEY')
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    REFRESH_TOKEN_EXPIRE_DAYS = 7


class EmailConfig():
    SMTP_SERVER = os.getenv('SMTP_SERVER')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
    EMAIL_VERIFICATION_URL = os.getenv('EMAIL_VERIFICATION_URL')


class YookassaConfig():
    SHOP_ID = os.getenv('YOOKASSA_SHOP_ID')
    SECRET_KEY = os.getenv('YOOKASSA_SECRET_KEY')
    PAYMENT_RETURN_URL = os.getenv('PAYMENT_RETURN_URL', 'https://ashleyvpn.com/payment/success')
