def get_task_keys(id: int, ct_id: int) -> dict:
    return {"lock_key": f"lock:{id}:{ct_id}", "key": f"task:{id}:{ct_id}"}
