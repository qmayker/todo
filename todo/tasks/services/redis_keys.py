def get_task_keys(
    id: int,
    ct_id: int,
    delete: bool = False,
) -> dict:
    keys = {"key": f"task:{id}:{ct_id}", "lock_key": f"{id}:{ct_id}"}
    return keys
