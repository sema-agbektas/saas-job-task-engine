from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings): 
    POSTGRES_PASSWORD: str 
    POSTGRES_DB: str 
    REDIS_URL: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    APP_PORT: int
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
