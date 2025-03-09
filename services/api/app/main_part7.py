# Endpoint pour enregistrer la configuration d'une boutique
@app.post("/stores/config")
async def register_store_config(store_data: Dict[str, Any], db_pool = Depends(get_db_pool), redis = Depends(get_redis)):
    """Enregistre la configuration d'une boutique dans la base de données"""
    try:
        if "store_url" not in store_data:
            raise HTTPException(status_code=400, detail="L'URL de la boutique est requise")
        
        store_url = store_data["store_url"]
        config = store_data.get("config", {})
        
        # Enregistrer dans la base de données
        async with db_pool.acquire() as conn:
            # Vérifier si la boutique existe déjà
            store_exists = await conn.fetchval(
                "SELECT COUNT(*) FROM stores WHERE store_url = $1",
                store_url
            )
            
            if store_exists:
                # Mettre à jour la boutique existante
                await conn.execute(
                    """
                    UPDATE stores 
                    SET config = $1, updated_at = NOW()
                    WHERE store_url = $2
                    """,
                    json.dumps(config),
                    store_url
                )
                store_id = await conn.fetchval(
                    "SELECT id FROM stores WHERE store_url = $1",
                    store_url
                )
            else:
                # Créer une nouvelle boutique
                store_id = await conn.fetchval(
                    """
                    INSERT INTO stores (store_url, config, created_at, updated_at)
                    VALUES ($1, $2, NOW(), NOW())
                    RETURNING id
                    """,
                    store_url,
                    json.dumps(config)
                )
        
        # Mettre en cache la configuration dans Redis (expire après 1 heure)
        await redis.set(f"store:config:{store_url}", json.dumps(config), ex=3600)
        
        return {
            "status": "success",
            "message": "Configuration de la boutique enregistrée avec succès",
            "store_id": store_id,
            "store_url": store_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement de la configuration: {str(e)}")