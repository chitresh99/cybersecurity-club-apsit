"""Application configuration from environment variables."""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str
    db_pool_size: int = 10
    db_max_overflow: int = 20
    
    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_seconds: int = 3600
    
    # Argon2
    argon2_time_cost: int = 2
    argon2_memory_cost: int = 65536
    argon2_parallelism: int = 4
    
    # CORS
    frontend_url: str = "http://localhost:5500"
    allowed_origins: str = "http://localhost:5500,http://127.0.0.1:5500"
    
    # File Upload
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 10
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated allowed origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
