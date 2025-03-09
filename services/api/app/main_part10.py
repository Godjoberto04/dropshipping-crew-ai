# Route pour récupérer le statut d'une tâche
@app.get("/tasks/{task_id}")
async def get_task_status(task_id: str, db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Récupère le statut d'une tâche en cours"""
    try:
        # Récupérer la tâche depuis Redis (plus rapide que la base de données)
        task_data = await redis.hgetall(f"task:{task_id}")
        
        if not task_data:
            # Si la tâche n'est pas dans Redis, vérifier la base de données
            async with db_pool.acquire() as conn:
                task_row = await conn.fetchrow(
                    "SELECT * FROM tasks WHERE id = $1",
                    task_id
                )
                
                if not task_row:
                    raise HTTPException(status_code=404, detail=f"Tâche non trouvée: {task_id}")
                
                # Convertir la ligne en dictionnaire
                task_data = dict(task_row)
                
                # Convertir les types de données
                if "params" in task_data and task_data["params"]:
                    task_data["params"] = json.loads(task_data["params"])
                if "result" in task_data and task_data["result"]:
                    task_data["result"] = json.loads(task_data["result"])
                task_data["created_at"] = task_data["created_at"].isoformat()
                task_data["updated_at"] = task_data["updated_at"].isoformat()
        else:
            # Convertir les types de données depuis Redis
            if "params" in task_data and task_data["params"]:
                task_data["params"] = json.loads(task_data["params"])
            if "result" in task_data and task_data["result"]:
                task_data["result"] = json.loads(task_data["result"])
            if "progress" in task_data:
                task_data["progress"] = int(task_data["progress"])
        
        # Calculer le temps restant estimé si la tâche est en cours
        if task_data.get("status") == "in_progress":
            progress = task_data.get("progress", 0)
            if progress > 0:
                elapsed_time = (datetime.now() - datetime.fromisoformat(task_data["created_at"])).total_seconds()
                total_estimated_time = elapsed_time / (progress / 100)
                remaining_time = total_estimated_time - elapsed_time
                task_data["remaining_time_seconds"] = max(0, remaining_time)
        
        return task_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération de la tâche: {str(e)}")