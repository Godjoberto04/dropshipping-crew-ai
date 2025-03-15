#!/bin/bash
# Script pour fusionner la branche order-manager-merge-test dans main

# Vérifier que nous sommes sur le bon répertoire
if [ ! -d ".git" ]; then
  echo "Erreur: Ce script doit être exécuté depuis la racine du dépôt git."
  exit 1
fi

# Sauvegarder la branche actuelle
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Sauvegarde de la branche actuelle: $CURRENT_BRANCH"

# Mettre à jour les branches locales
echo "Mise à jour des branches locales..."
git fetch origin

# Vérifier la branche order-manager-merge-test
echo "Vérification de la branche order-manager-merge-test..."
git checkout order-manager-merge-test
git pull origin order-manager-merge-test

# Exécuter les tests de base pour s'assurer que tout fonctionne
echo "Exécution des tests de base..."
if [ -d "services/order-manager/tests" ]; then
  cd services/order-manager
  python -m unittest discover tests
  if [ $? -ne 0 ]; then
    echo "Les tests ont échoué. Annulation de la fusion."
    cd ../..
    git checkout $CURRENT_BRANCH
    exit 1
  fi
  cd ../..
fi

# Passer à la branche main et la mettre à jour
echo "Passage à la branche main..."
git checkout main
git pull origin main

# Effectuer la fusion
echo "Fusion de order-manager-merge-test dans main..."
git merge --no-ff order-manager-merge-test -m "Intégration de l'agent Order Manager avec supports AliExpress et CJ Dropshipping"

# Vérifier s'il y a des conflits
if [ $? -ne 0 ]; then
  echo "Des conflits sont survenus lors de la fusion. Veuillez les résoudre manuellement."
  exit 1
fi

echo "Fusion réussie! Vous pouvez maintenant pousser les modifications vers le dépôt distant avec:"
echo "git push origin main"

# Options pour archiver les anciennes branches
echo ""
echo "Pour archiver les branches obsolètes, exécutez les commandes suivantes:"
echo "git push origin order-manager-complete:refs/heads/archived/order-manager-complete"
echo "git push origin feature/agent-order-manager:refs/heads/archived/feature/agent-order-manager"
echo "git push origin order-manager-impl-new:refs/heads/archived/order-manager-impl-new"
echo "git push origin order-manager-implementation:refs/heads/archived/order-manager-implementation"

# Retourner à la branche d'origine
git checkout $CURRENT_BRANCH
