# Mise à jour du statut d'une tâche
@app.put("/tasks/{task_id}/status")
async def update_task_status(task_id: str, update: TaskUpdate, db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Met à jour le statut d'une tâche"""
    try:
        # Vérifier si la tâche existe
        async with db_pool.acquire() as conn:
            task_exists = await conn.fetchval(
                "SELECT COUNT(*) FROM tasks WHERE id = $1",
                task_id
            )
            
            if not task_exists:
                raise HTTPException(status_code=404, detail=f"Tâche non trouvée: {task_id}")
            
            # Mettre à jour la tâche dans la base de données
            await conn.execute(
                """
                UPDATE tasks 
                SET status = $1, progress = $2, result = $3, updated_at = NOW()
                WHERE id = $4
                """,
                update.status,
                update.progress,
                json.dumps(update.result) if update.result else None,
                task_id
            )
        
        # Mettre à jour Redis
        redis_update = {
            "status": update.status,
            "updated_at": datetime.now().isoformat()
        }
        
        if update.progress is not None:
            redis_update["progress"] = str(update.progress)
            
        if update.result:
            redis_update["result"] = json.dumps(update.result)
        
        await redis.hset(f"task:{task_id}", mapping=redis_update)
        
        # Si la tâche est terminée, la retirer de la liste des tâches en attente
        if update.status in ["completed", "failed"]:
            # Récupérer l'ID de l'agent
            agent_id = await redis.hget(f"task:{task_id}", "agent_id")
            if agent_id:
                await redis.lrem(f"tasks:pending:{agent_id}", 0, task_id)
                
                # Mettre à jour le statut de l'agent
                await redis.hset(f"agent:{agent_id}", "last_run", datetime.now().isoformat())
        
        return {
            "status": "success",
            "message": f"Statut de la tâche {task_id} mis à jour"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour de la tâche: {str(e)}")