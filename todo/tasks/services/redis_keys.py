def get_task_keys(id: int, ct: int) -> dict:
    return {"lock_key": f"lock:{id}:{ct}", "key": f"task:{id}:{ct}"}
