import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException

from config import AuthConfig


class EmailService:
    def __init__(self, smtp_server: str, smtp_port: int, smtp_username: str, smtp_password: str, 
                 from_email: str, verification_url: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email
        self.verification_url = verification_url
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """
        Отправляет email
        """
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            print(f"Ошибка при отправке email: {str(e)}")
            return False
    
    def create_verification_token(self, user_id: str, expires_delta: Optional[timedelta] = None) -> str:
        """
        Создает токен для подтверждения email
        """
        to_encode = {"sub": user_id, "type": "email_verification"}
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=24)  # Токен действителен 24 часа
            
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[str]:
        """
        Проверяет токен подтверждения email и возвращает user_id
        """
        try:
            payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if user_id is None or token_type != "email_verification":
                return None
                
            return user_id
        except jwt.JWTError:
            return None
    
    def send_verification_email(self, user_id: str, email: str) -> bool:
        """
        Отправляет email с ссылкой для подтверждения
        """
        token = self.create_verification_token(user_id)
        verification_link = f"{self.verification_url}?token={token}"
        
        subject = "Подтверждение регистрации в AshleyVPN"
        body = f"""
        <html>
        <body>
            <h2>Добро пожаловать в AshleyVPN!</h2>
            <p>Для завершения регистрации, пожалуйста, подтвердите ваш email, перейдя по ссылке ниже:</p>
            <p><a href="{verification_link}">Подтвердить email</a></p>
            <p>Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.</p>
            <p>С уважением,<br>Команда AshleyVPN</p>
        </body>
        </html>
        """
        
        return self.send_email(email, subject, body, is_html=True)