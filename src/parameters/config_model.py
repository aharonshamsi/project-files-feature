
from pydantic import BaseModel


class AppConfig(BaseModel):

    input_file: str 
    model_name: str

    source_mode: str
    language_mode: str
    number_words_in_file: int = 0

    open_questions_count: int
    multiple_choice_questions_count: int
    file_questions_count: int

