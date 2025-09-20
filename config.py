from pydantic_settings import BaseSettings
from datetime import timedelta


class Settings(BaseSettings):
    database_url: str
    admin_username: str
    admin_password: str
    secret_key: str
    debug: bool = False
    algorithm: str
    access_token_expire_min: int

    @property
    def access_token_expire_minutes(self):
        return timedelta(minutes=self.access_token_expire_min)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        populate_by_name = True


settings = Settings()
print(settings.access_token_expire_minutes)