@app.post("/agents/data-analyzer/analyze")
async def trigger_analysis(urls_list: UrlsList, background_tasks: BackgroundTasks, db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Déclenche une analyse de marché sur les URLs spécifiées"""
    if not urls_list.urls or len(urls_list.urls) == 0:
        raise HTTPException(status_code=400, detail="Au moins une URL est requise")
    
    try:
        # Générer un ID unique pour la tâche
        task_id = str(uuid.uuid4())
        
        # Préparer les paramètres de la tâche
        task_params = {
            "urls": urls_list.urls,
            "market_segment": urls_list.market_segment,
            "min_margin": urls_list.min_margin
        }
        
        # Enregistrer la tâche dans la base de données
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO tasks (id, agent_id, status, params, progress, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                """,
                task_id,
                "data-analyzer",
                "pending",
                json.dumps(task_params),
                0
            )
        
        # Enregistrer la tâche dans Redis pour que l'agent puisse la récupérer
        await redis.hset(
            f"task:{task_id}",
            mapping={
                "agent_id": "data-analyzer",
                "status": "pending",
                "params": json.dumps(task_params),
                "progress": "0",
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Ajouter la tâche à la liste des tâches en attente
        await redis.lpush("tasks:pending:data-analyzer", task_id)
        
        # Calculer le temps estimé de fin (environ 1 minute par URL)
        estimated_completion = datetime.now().timestamp() + (len(urls_list.urls) * 60)
        
        return {
            "task_id": task_id,
            "status": "queued",
            "message": f"Analyse démarrée sur {len(urls_list.urls)} URLs",
            "estimated_completion": estimated_completion
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la tâche: {str(e)}")