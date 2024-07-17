import os
import datetime

def list_models(name, list_models_func, cache_directory_path):
    models = []
    file_path = os.path.join(cache_directory_path, f'{name}.models')
    if os.path.exists(file_path):
        mod_time = os.path.getmtime(file_path)
        mod_date = datetime.date.fromtimestamp(mod_time)
        if mod_date == datetime.date.today():
            with open(file_path, 'r') as f:
                models = f.read().splitlines()
    if len(models) == 0:
        models = list_models_func()
        with open(file_path, 'w') as f:
            f.write('\n'.join(models))
    return models