# Nouvel endpoint pour déclencher une action de l'agent Website Builder
@app.post("/agents/website-builder/action")
async def trigger_website_builder_action(action: WebsiteBuilderAction, background_tasks: BackgroundTasks, db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Déclenche une action (setup_store ou add_product) pour l'agent Website Builder"""
    try:
        # Vérifier que l'action est valide
        if action.action not in ["setup_store", "add_product"]:
            raise HTTPException(status_code=400, detail=f"Action invalide: {action.action}. Les actions disponibles sont 'setup_store' et 'add_product'.")
        
        # Vérifier que les données nécessaires sont fournies
        if action.action == "setup_store" and not action.store_config:
            raise HTTPException(status_code=400, detail="La configuration de la boutique est requise pour l'action 'setup_store'")
        
        if action.action == "add_product" and not action.product_data:
            raise HTTPException(status_code=400, detail="Les données du produit sont requises pour l'action 'add_product'")
        
        # Générer un ID unique pour la tâche
        task_id = str(uuid.uuid4())
        
        # Préparer les paramètres de la tâche
        task_params = {
            "action": action.action
        }
        
        if action.store_config:
            task_params["store_config"] = action.store_config.dict()
        
        if action.product_data:
            task_params["product_data"] = action.product_data.dict()
        
        # Enregistrer la tâche dans la base de données
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO tasks (id, agent_id, status, params, progress, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, NOW(), NOW())
                """,
                task_id,
                "website-builder",
                "pending",
                json.dumps(task_params),
                0
            )
        
        # Enregistrer la tâche dans Redis pour que l'agent puisse la récupérer
        await redis.hset(
            f"task:{task_id}",
            mapping={
                "agent_id": "website-builder",
                "status": "pending",
                "params": json.dumps(task_params),
                "progress": "0",
                "created_at": datetime.now().isoformat()
            }
        )
        
        # Ajouter la tâche à la liste des tâches en attente
        await redis.lpush("tasks:pending:website-builder", task_id)
        
        # Estimer le temps de complétion
        if action.action == "setup_store":
            estimated_completion = datetime.now().timestamp() + 300  # 5 minutes pour la configuration de la boutique
        else:  # add_product
            estimated_completion = datetime.now().timestamp() + 120  # 2 minutes pour l'ajout d'un produit
        
        return {
            "task_id": task_id,
            "status": "queued",
            "message": f"Action '{action.action}' démarrée pour l'agent Website Builder",
            "estimated_completion": estimated_completion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création de la tâche: {str(e)}")