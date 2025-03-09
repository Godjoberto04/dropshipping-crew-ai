# Guide de configuration de Shopify pour l'agent Website Builder

Ce guide détaillé vous guidera pas à pas pour configurer votre compte Shopify et obtenir les informations nécessaires pour l'agent Website Builder.

## 1. Création d'un compte Shopify

### Étape 1: Inscription

1. Rendez-vous sur [Shopify.com](https://www.shopify.com/)
2. Cliquez sur le bouton **Commencer l'essai gratuit**
3. Remplissez le formulaire avec:
   - Votre adresse e-mail
   - Un mot de passe sécurisé
   - Le nom de votre boutique (peut être modifié ultérieurement)
4. Cliquez sur **Créer votre boutique**

### Étape 2: Informations personnelles

1. Répondez aux questions concernant votre expérience en e-commerce
2. Fournissez les informations demandées sur votre activité
3. Remplissez votre adresse personnelle ou professionnelle

### Étape 3: Sélection d'un forfait

1. Sélectionnez le forfait **Lite** à 9$ par mois (recommandé pour commencer)
   - Ce forfait vous permet de vendre sur les canaux de vente, mais pas d'avoir une boutique en ligne complète
   - Vous pourrez passer à un forfait supérieur ultérieurement
2. Configurez les paramètres de facturation

## 2. Configuration de l'API Shopify

### Étape 1: Accéder aux applications et autorisations

1. Dans votre tableau de bord Shopify, cliquez sur **Applications** dans le menu latéral gauche
2. Faites défiler jusqu'en bas et cliquez sur **Gérer les applications personnelles**
3. Cliquez sur le bouton **Créer une application**

### Étape 2: Créer une application personnalisée

1. Donnez un nom à votre application (ex: "Dropshipping Crew AI")
2. Cliquez sur **Créer l'application**

### Étape 3: Configurer les autorisations de l'API

1. Dans la section **Configuration de l'API Admin**, cliquez sur **Configurer les autorisations de l'API Admin**
2. Activez les autorisations suivantes (au minimum):
   - `read_products`, `write_products`: Pour gérer les produits
   - `read_orders`, `write_orders`: Pour gérer les commandes
   - `read_themes`, `write_themes`: Pour modifier le thème
   - `read_content`, `write_content`: Pour gérer les pages et le contenu
   - `read_customers`, `write_customers`: Pour gérer les clients
   - `read_inventory`, `write_inventory`: Pour gérer les stocks
3. Cliquez sur **Enregistrer**

### Étape 4: Créer des informations d'identification d'API

1. Cliquez sur **Installer l'application** pour obtenir un token d'accès
2. Une fois l'installation terminée, notez les informations suivantes:
   - **Clé API**: Visible sous le nom de l'application
   - **Secret API**: Visible sous la clé API
   - **Token d'accès**: Visible dans la section "Tokens d'accès à l'API Admin"

## 3. Configuration de l'URL de la boutique

1. Notez l'URL de votre boutique Shopify qui est sous la forme: `votre-boutique.myshopify.com`
2. Cette URL servira pour l'accès à l'API

## 4. Mise à jour du fichier .env

Modifiez le fichier `.env` de votre projet pour y intégrer les informations d'API Shopify:

```
# Informations Shopify
SHOPIFY_API_KEY=votre_clé_api
SHOPIFY_API_SECRET=votre_secret_api
SHOPIFY_STORE_URL=votre-boutique.myshopify.com
SHOPIFY_ACCESS_TOKEN=votre_token_accès
```

## 5. Tester la connexion

Pour vérifier que votre configuration fonctionne correctement:

1. Redémarrez les conteneurs du projet pour prendre en compte les nouvelles variables d'environnement:
   ```bash
   docker-compose restart
   ```

2. Testez la configuration de base de votre boutique:
   ```bash
   curl -X POST "http://votre-serveur:8000/agents/website-builder/action" \
     -H "Content-Type: application/json" \
     -d '{
       "action": "setup_store",
       "store_config": {
         "name": "Ma Boutique Test",
         "currency": "EUR"
       }
     }'
   ```

3. Si tout fonctionne correctement, vous devriez recevoir un ID de tâche, et la boutique devrait être mise à jour avec les paramètres spécifiés

## 6. Résolution des problèmes courants

### Erreur de connexion à l'API

Si vous rencontrez des erreurs de connexion à l'API Shopify:

1. Vérifiez que les clés API, le secret et le token sont correctement copiés (sans espaces supplémentaires)
2. Assurez-vous que l'URL de la boutique est correcte et sous la forme `votre-boutique.myshopify.com`
3. Vérifiez que les autorisations d'API sont correctement configurées

### Erreur d'autorisation

Si vous rencontrez des erreurs d'autorisation:

1. Vérifiez que le token d'accès est valide
2. Essayez de régénérer un nouveau token dans les paramètres de l'application
3. Assurez-vous que l'application a les autorisations nécessaires pour les opérations que vous tentez d'effectuer

## Prochaines étapes

Une fois Shopify configuré, vous pouvez:

1. Utiliser l'agent Website Builder pour configurer le thème et la navigation
2. Configurer l'intégration avec l'agent Data Analyzer
3. Tester le script d'intégration entre les agents
4. Développer l'agent Content Generator pour enrichir votre boutique

## Ressources supplémentaires

- [Documentation officielle de l'API Shopify Admin](https://shopify.dev/docs/admin-api)
- [Guide des meilleures pratiques pour Shopify](https://www.shopify.com/blog/topics/shopify-tutorials)
- [Forum de la communauté Shopify](https://community.shopify.com/)