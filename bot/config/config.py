from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

    API_ID: int
    API_HASH: str


    REF_LINK: str = "https://t.me/Binance_Moonbix_bot/start?startApp=ref_6624523270&startapp=ref_6624523270&utm_medium=web_share_copy"
    AUTO_TASK: bool = True
    AUTO_PLAY_GAME: bool = True

    USE_PROXY_FROM_FILE: bool = False


settings = Settings()

