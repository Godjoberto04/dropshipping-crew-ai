@app.get("/agents/{agent_id}/status")
async def get_agent_status(agent_id: str, redis = Depends(get_redis)):
    """Renvoie le statut d'un agent spécifique"""
    try:
        # Récupérer le statut de l'agent depuis Redis
        agent_status = await redis.hgetall(f"agent:{agent_id}")
        
        if not agent_status:
            # Agent non trouvé, retourner un statut par défaut
            if agent_id == "data-analyzer":
                return {
                    "status": "partial",
                    "version": "0.1.0",
                    "last_run": datetime.now().isoformat(),
                    "capabilities": [
                        "Website scraping",
                        "Product analysis"
                    ],
                    "pending_capabilities": [
                        "Trend analysis",
                        "Competition assessment"
                    ]
                }
            elif agent_id == "website-builder":
                return {
                    "status": "offline",
                    "version": "0.1.0",
                    "last_run": None,
                    "capabilities": [
                        "Store configuration",
                        "Theme management",
                        "Navigation setup",
                        "Product management"
                    ]
                }
            else:
                return {
                    "status": "offline",
                    "version": None,
                    "last_run": None,
                    "capabilities": []
                }
        
        # Convertir les champs JSON
        if "capabilities" in agent_status and agent_status["capabilities"]:
            agent_status["capabilities"] = json.loads(agent_status["capabilities"])
            
        if "last_run" in agent_status and agent_status["last_run"]:
            agent_status["last_run"] = agent_status["last_run"]
            
        return agent_status
        
    except Exception as e:
        # En cas d'erreur, retourner un statut par défaut
        return {
            "status": "unknown",
            "error": str(e)
        }

@app.put("/agents/{agent_id}/status")
async def update_agent_status(agent_id: str, status: AgentStatus, db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Met à jour le statut d'un agent"""
    try:
        # Préparer les données pour Redis
        redis_data = {
            "status": status.status,
            "updated_at": datetime.now().isoformat()
        }
        
        if status.version:
            redis_data["version"] = status.version
            
        if status.capabilities:
            redis_data["capabilities"] = json.dumps(status.capabilities)
            
        if status.last_run:
            redis_data["last_run"] = status.last_run.isoformat()
        
        # Mettre à jour Redis
        await redis.hset(f"agent:{agent_id}", mapping=redis_data)
        
        # Mettre à jour la base de données
        async with db_pool.acquire() as conn:
            # Vérifier si l'agent existe déjà
            agent_exists = await conn.fetchval(
                "SELECT COUNT(*) FROM agents WHERE id = $1",
                agent_id
            )
            
            if agent_exists:
                # Mettre à jour l'agent existant
                await conn.execute(
                    """
                    UPDATE agents 
                    SET status = $1, version = $2, capabilities = $3, 
                        last_run = $4, updated_at = NOW()
                    WHERE id = $5
                    """,
                    status.status,
                    status.version,
                    json.dumps(status.capabilities) if status.capabilities else None,
                    status.last_run,
                    agent_id
                )
            else:
                # Créer un nouvel agent
                await conn.execute(
                    """
                    INSERT INTO agents (id, status, version, capabilities, last_run, updated_at)
                    VALUES ($1, $2, $3, $4, $5, NOW())
                    """,
                    agent_id,
                    status.status,
                    status.version,
                    json.dumps(status.capabilities) if status.capabilities else None,
                    status.last_run
                )
        
        return {
            "status": "success",
            "message": f"Statut de l'agent {agent_id} mis à jour"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour du statut: {str(e)}")