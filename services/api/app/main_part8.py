# Endpoint pour enregistrer un produit
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