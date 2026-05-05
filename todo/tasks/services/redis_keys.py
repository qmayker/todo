def get_task_keys(id: int, ct_id: int, end: bool=False) -> dict:
    return {"lock_key": f"{id}:{ct_id}:{end}", "key": f"task:{id}:{ct_id}"}
