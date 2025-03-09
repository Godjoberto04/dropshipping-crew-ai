# Routes pour les boutiques et produits
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

@app.post("/products")
async def register_product(product_data: Dict[str, Any], db_pool = Depends(get_db_pool)):
    """Enregistre un produit dans la base de données"""
    try:
        if "store_url" not in product_data:
            raise HTTPException(status_code=400, detail="L'URL de la boutique est requise")
        
        if "product" not in product_data:
            raise HTTPException(status_code=400, detail="Les données du produit sont requises")
        
        store_url = product_data["store_url"]
        product = product_data["product"]
        
        # Vérifier que le produit a un ID
        if "id" not in product:
            raise HTTPException(status_code=400, detail="L'ID du produit est requis")
        
        product_id = str(product["id"])
        
        # Enregistrer dans la base de données
        async with db_pool.acquire() as conn:
            # Vérifier si le produit existe déjà
            product_exists = await conn.fetchval(
                "SELECT COUNT(*) FROM products WHERE product_id = $1 AND store_url = $2",
                product_id, store_url
            )
            
            if product_exists:
                # Mettre à jour le produit existant
                await conn.execute(
                    """
                    UPDATE products 
                    SET data = $1, updated_at = NOW()
                    WHERE product_id = $2 AND store_url = $3
                    """,
                    json.dumps(product),
                    product_id,
                    store_url
                )
                db_id = await conn.fetchval(
                    "SELECT id FROM products WHERE product_id = $1 AND store_url = $2",
                    product_id, store_url
                )
            else:
                # Créer un nouveau produit
                db_id = await conn.fetchval(
                    """
                    INSERT INTO products (product_id, store_url, data, created_at, updated_at)
                    VALUES ($1, $2, $3, NOW(), NOW())
                    RETURNING id
                    """,
                    product_id,
                    store_url,
                    json.dumps(product)
                )
        
        return {
            "status": "success",
            "message": "Produit enregistré avec succès",
            "id": db_id,
            "product_id": product_id,
            "store_url": store_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement du produit: {str(e)}")

# Point d'entrée principal
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)