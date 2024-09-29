from aiogram.filters.callback_data import CallbackData 

class ProjectDetails(CallbackData, prefix='details'):
    action: str
    num_task: int
