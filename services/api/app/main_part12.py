# Liste des tâches en attente pour un agent
@app.get("/tasks/pending/{agent_id}")
async def get_pending_tasks(agent_id: str, redis = Depends(get_redis), db_pool = Depends(get_db_pool)):
    """Récupère les tâches en attente pour un agent donné"""
    try:
        # Récupérer les IDs des tâches en attente depuis Redis
        task_ids = await redis.lrange(f"tasks:pending:{agent_id}", 0, -1)
        
        if not task_ids:
            return []
        
        # Récupérer les détails des tâches
        tasks = []
        for task_id in task_ids:
            # D'abord essayer de récupérer depuis Redis
            task_data = await redis.hgetall(f"task:{task_id}")
            
            if task_data:
                # Convertir les types de données depuis Redis
                if "params" in task_data and task_data["params"]:
                    task_data["params"] = json.loads(task_data["params"])
                if "progress" in task_data:
                    task_data["progress"] = int(task_data["progress"])
                
                # Ajouter l'ID de la tâche au dictionnaire
                task_data["task_id"] = task_id
                
                # Ajouter la tâche à la liste
                tasks.append(task_data)
            else:
                # Sinon, récupérer depuis la base de données
                async with db_pool.acquire() as conn:
                    task_row = await conn.fetchrow(
                        "SELECT * FROM tasks WHERE id = $1 AND status = 'pending'",
                        task_id
                    )
                    
                    if task_row:
                        # Convertir la ligne en dictionnaire
                        task_data = dict(task_row)
                        
                        # Convertir les types de données
                        if "params" in task_data and task_data["params"]:
                            task_data["params"] = json.loads(task_data["params"])
                        
                        # Ajouter l'ID de la tâche au dictionnaire
                        task_data["task_id"] = task_id
                        
                        # Ajouter la tâche à la liste
                        tasks.append(task_data)
        
        return tasks
        
    except Exception as e:
        # En cas d'erreur, logger l'erreur et retourner une liste vide
        print(f"Erreur lors de la récupération des tâches en attente: {str(e)}")
        return []