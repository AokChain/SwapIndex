from sqlmodel import create_engine, SQLModel
import config

engine = create_engine(config.sqlite_path)
