#!/usr/bin/env python3
"""
Gestionnaire de notifications pour l'agent Order Manager.
Ce module est responsable de l'envoi des notifications aux clients et aux administrateurs.
"""

import os
import json
import smtplib
import aiohttp
import asyncio
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional, Union
from loguru import logger
from datetime import datetime


class NotificationType(str, Enum):
    """Types de notifications supportés par le système."""
    ORDER_PLACED = "order_placed"
    ORDER_CONFIRMED = "order_confirmed"
    PAYMENT_RECEIVED = "payment_received"
    SHIPPED = "shipped"
    DELIVERY_UPDATE = "delivery_update"
    DELIVERED = "delivered"
    ORDER_ISSUE = "order_issue"
    TRACKING_AVAILABLE = "tracking_available"
    ADMIN_ALERT = "admin_alert"
    STOCK_ISSUE = "stock_issue"


class NotificationManager:
    """
    Gestionnaire de notifications pour l'agent Order Manager.
    
    Cette classe est responsable de l'envoi des notifications aux clients
    et aux administrateurs via divers canaux (email, webhooks, etc.).
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialise le gestionnaire de notifications.
        
        Args:
            config: Configuration du gestionnaire de notifications
        """
        self.config = config or {}
        
        # Charger la configuration depuis les variables d'environnement si non fournies
        self.email_config = self.config.get("email", {})
        if not self.email_config:
            self.email_config = {
                "smtp_server": os.getenv("NOTIFICATION_SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": int(os.getenv("NOTIFICATION_SMTP_PORT", "587")),
                "smtp_username": os.getenv("NOTIFICATION_SMTP_USERNAME", ""),
                "smtp_password": os.getenv("NOTIFICATION_SMTP_PASSWORD", ""),
                "sender_email": os.getenv("NOTIFICATION_SENDER_EMAIL", ""),
                "sender_name": os.getenv("NOTIFICATION_SENDER_NAME", "Dropshipping Store")
            }
        
        # Configuration des webhooks
        self.webhook_config = self.config.get("webhooks", {})
        if not self.webhook_config:
            self.webhook_config = {
                "enabled": os.getenv("NOTIFICATION_WEBHOOKS_ENABLED", "false").lower() == "true",
                "urls": json.loads(os.getenv("NOTIFICATION_WEBHOOK_URLS", "[]"))
            }
        
        # Configuration des notifications administrateur
        self.admin_config = self.config.get("admin", {})
        if not self.admin_config:
            self.admin_config = {
                "admin_emails": json.loads(os.getenv("NOTIFICATION_ADMIN_EMAILS", "[]")),
                "notify_on": json.loads(os.getenv("NOTIFICATION_ADMIN_EVENTS", '["order_issue", "stock_issue", "admin_alert"]'))
            }
        
        # Templates des messages
        self.templates = {
            NotificationType.ORDER_PLACED: {
                "subject": "Votre commande #{order_id} a été reçue",
                "body": "Bonjour {customer_name},\n\nNous avons bien reçu votre commande #{order_id}. Nous la traiterons dans les plus brefs délais.\n\nMerci pour votre achat !\n\nL'équipe {store_name}"
            },
            NotificationType.ORDER_CONFIRMED: {
                "subject": "Votre commande #{order_id} est confirmée",
                "body": "Bonjour {customer_name},\n\nVotre commande #{order_id} a été confirmée et est en cours de préparation.\n\nVous recevrez bientôt un message avec les informations de suivi.\n\nL'équipe {store_name}"
            },
            NotificationType.PAYMENT_RECEIVED: {
                "subject": "Paiement reçu pour votre commande #{order_id}",
                "body": "Bonjour {customer_name},\n\nNous avons bien reçu votre paiement pour la commande #{order_id}. Votre commande est maintenant en cours de préparation.\n\nL'équipe {store_name}"
            },
            NotificationType.SHIPPED: {
                "subject": "Votre commande #{order_id} a été expédiée",
                "body": "Bonjour {customer_name},\n\nVotre commande #{order_id} a été expédiée.\n\nNuméro de suivi : {tracking_number}\nService de livraison : {carrier}\nLien de suivi : {tracking_url}\n\nDate d'expédition estimée : {ship_date}\nDate de livraison estimée : {delivery_date}\n\nL'équipe {store_name}"
            },
            NotificationType.DELIVERY_UPDATE: {
                "subject": "Mise à jour de livraison pour votre commande #{order_id}",
                "body": "Bonjour {customer_name},\n\nVoici une mise à jour concernant votre commande #{order_id}.\n\nStatut actuel : {status}\nEmplacement actuel : {location}\nDate de livraison estimée : {delivery_date}\n\nSuivez votre colis ici : {tracking_url}\n\nL'équipe {store_name}"
            },
            NotificationType.DELIVERED: {
                "subject": "Votre commande #{order_id} a été livrée",
                "body": "Bonjour {customer_name},\n\nVotre commande #{order_id} a été livrée à l'adresse indiquée.\n\nNous espérons que vous apprécierez votre achat ! N'hésitez pas à nous contacter si vous avez des questions.\n\nL'équipe {store_name}"
            },
            NotificationType.ORDER_ISSUE: {
                "subject": "Important : Problème avec votre commande #{order_id}",
                "body": "Bonjour {customer_name},\n\nNous avons rencontré un problème avec votre commande #{order_id}.\n\nDétails du problème : {issue_details}\n\nVeuillez nous contacter dès que possible pour résoudre ce problème.\n\nL'équipe {store_name}"
            },
            NotificationType.TRACKING_AVAILABLE: {
                "subject": "Informations de suivi disponibles pour votre commande #{order_id}",
                "body": "Bonjour {customer_name},\n\nLes informations de suivi sont maintenant disponibles pour votre commande #{order_id}.\n\nNuméro de suivi : {tracking_number}\nService de livraison : {carrier}\nLien de suivi : {tracking_url}\n\nDate de livraison estimée : {delivery_date}\n\nL'équipe {store_name}"
            },
            NotificationType.ADMIN_ALERT: {
                "subject": "[ADMIN] Alerte : {alert_subject}",
                "body": "Alerte administrateur :\n\nType : {alert_type}\nDétails : {alert_details}\n\nDate et heure : {timestamp}\n\nCeci est un message automatique du système de notification de l'agent Order Manager."
            },
            NotificationType.STOCK_ISSUE: {
                "subject": "[ADMIN] Problème de stock pour la commande #{order_id}",
                "body": "Alerte problème de stock :\n\nCommande : #{order_id}\nClient : {customer_name}\nProduit(s) concerné(s) : {product_names}\nFournisseur : {supplier}\n\nDétails : {issue_details}\n\nDate et heure : {timestamp}\n\nCeci est un message automatique du système de notification de l'agent Order Manager."
            }
        }
        
        logger.info("Gestionnaire de notifications initialisé")
    
    async def send_notification(self, 
                              notification_type: NotificationType, 
                              recipient_email: str, 
                              data: Dict[str, Any],
                              cc: Optional[List[str]] = None,
                              bcc: Optional[List[str]] = None) -> bool:
        """
        Envoie une notification à un destinataire.
        
        Args:
            notification_type: Type de notification
            recipient_email: Email du destinataire
            data: Données à injecter dans le template
            cc: Liste d'emails en copie
            bcc: Liste d'emails en copie cachée
            
        Returns:
            Succès de l'envoi
        """
        logger.info(f"Envoi de notification {notification_type} à {recipient_email}")
        
        # Préparer le template
        template = self.templates.get(notification_type)
        if not template:
            logger.error(f"Template non trouvé pour le type de notification {notification_type}")
            return False
        
        # Remplacer les variables dans le template
        subject = template["subject"]
        body = template["body"]
        
        for key, value in data.items():
            subject = subject.replace(f"{{{key}}}", str(value))
            body = body.replace(f"{{{key}}}", str(value))
        
        # Envoyer l'email
        try:
            await self._send_email(recipient_email, subject, body, cc=cc, bcc=bcc)
            logger.info(f"Notification {notification_type} envoyée avec succès à {recipient_email}")
            
            # Envoyer également par webhook si configuré
            if self.webhook_config.get("enabled"):
                await self._send_webhook(notification_type, data)
            
            # Notifier les administrateurs si nécessaire
            if notification_type in self.admin_config.get("notify_on", []):
                await self._notify_admins(notification_type, data)
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification {notification_type} à {recipient_email}: {str(e)}")
            return False
    
    async def notify_order_status(self, 
                                order_id: str, 
                                customer_email: str, 
                                customer_name: str,
                                status: NotificationType,
                                additional_data: Dict[str, Any] = None) -> bool:
        """
        Envoie une notification concernant le statut d'une commande.
        
        Args:
            order_id: Identifiant de la commande
            customer_email: Email du client
            customer_name: Nom du client
            status: Statut de la commande (type de notification)
            additional_data: Données supplémentaires pour le template
            
        Returns:
            Succès de l'envoi
        """
        data = {
            "order_id": order_id,
            "customer_name": customer_name,
            "store_name": self.email_config.get("sender_name", "Dropshipping Store"),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **(additional_data or {})
        }
        
        return await self.send_notification(status, customer_email, data)
    
    async def _send_email(self, 
                        recipient: str, 
                        subject: str, 
                        body: str,
                        is_html: bool = False,
                        cc: Optional[List[str]] = None,
                        bcc: Optional[List[str]] = None) -> bool:
        """
        Envoie un email via SMTP.
        
        Args:
            recipient: Email du destinataire
            subject: Sujet de l'email
            body: Corps de l'email
            is_html: Indique si le corps de l'email est au format HTML
            cc: Liste d'emails en copie
            bcc: Liste d'emails en copie cachée
            
        Returns:
            Succès de l'envoi
        """
        if not self.email_config.get("smtp_server") or not self.email_config.get("sender_email"):
            logger.warning("Configuration SMTP incomplète, email non envoyé")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = f"{self.email_config.get('sender_name')} <{self.email_config.get('sender_email')}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        
        if cc:
            msg['Cc'] = ", ".join(cc)
            
        # Ajouter le corps du message
        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Configuration du serveur SMTP
        try:
            server = smtplib.SMTP(self.email_config.get("smtp_server"), self.email_config.get("smtp_port"))
            server.ehlo()
            if self.email_config.get("smtp_port") == 587:
                server.starttls()
            
            # Authentification si nécessaire
            if self.email_config.get("smtp_username") and self.email_config.get("smtp_password"):
                server.login(self.email_config.get("smtp_username"), self.email_config.get("smtp_password"))
            
            # Préparer la liste des destinataires
            all_recipients = [recipient]
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
            
            # Envoi
            server.sendmail(self.email_config.get("sender_email"), all_recipients, msg.as_string())
            server.quit()
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
            return False
    
    async def _send_webhook(self, notification_type: NotificationType, data: Dict[str, Any]) -> bool:
        """
        Envoie une notification via webhook.
        
        Args:
            notification_type: Type de notification
            data: Données de la notification
            
        Returns:
            Succès de l'envoi
        """
        if not self.webhook_config.get("enabled") or not self.webhook_config.get("urls"):
            logger.debug("Webhooks désactivés ou aucune URL configurée")
            return False
        
        webhook_data = {
            "type": notification_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        tasks = []
        for url in self.webhook_config.get("urls", []):
            tasks.append(self._send_webhook_request(url, webhook_data))
        
        if not tasks:
            return False
        
        # Exécuter les requêtes en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Vérifier si au moins une requête a réussi
        return any(result is True for result in results)
    
    async def _send_webhook_request(self, url: str, data: Dict[str, Any]) -> bool:
        """
        Envoie une requête webhook à une URL spécifique.
        
        Args:
            url: URL du webhook
            data: Données à envoyer
            
        Returns:
            Succès de l'envoi
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, timeout=10) as response:
                    if response.status >= 200 and response.status < 300:
                        logger.info(f"Webhook envoyé avec succès à {url}")
                        return True
                    else:
                        logger.warning(f"Erreur lors de l'envoi du webhook à {url}: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi du webhook à {url}: {str(e)}")
            return False
    
    async def _notify_admins(self, notification_type: NotificationType, data: Dict[str, Any]) -> bool:
        """
        Notifie les administrateurs d'un événement.
        
        Args:
            notification_type: Type de notification
            data: Données de la notification
            
        Returns:
            Succès de l'envoi
        """
        admin_emails = self.admin_config.get("admin_emails", [])
        if not admin_emails:
            logger.warning("Aucun email d'administrateur configuré, notification non envoyée")
            return False
        
        # Préparer le template administrateur
        template = self.templates.get(notification_type)
        if not template:
            logger.error(f"Template non trouvé pour le type de notification {notification_type}")
            return False
        
        # Remplacer les variables dans le template
        subject = template["subject"]
        body = template["body"]
        
        for key, value in data.items():
            subject = subject.replace(f"{{{key}}}", str(value))
            body = body.replace(f"{{{key}}}", str(value))
        
        # Ajouter préfixe [ADMIN] si absent
        if not subject.startswith("[ADMIN]"):
            subject = f"[ADMIN] {subject}"
        
        # Envoyer l'email à tous les administrateurs
        try:
            await self._send_email(admin_emails[0], subject, body, cc=admin_emails[1:] if len(admin_emails) > 1 else None)
            logger.info(f"Notification {notification_type} envoyée aux administrateurs")
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'envoi de la notification aux administrateurs: {str(e)}")
            return False
    
    async def send_admin_alert(self, alert_type: str, alert_subject: str, alert_details: str) -> bool:
        """
        Envoie une alerte aux administrateurs.
        
        Args:
            alert_type: Type d'alerte
            alert_subject: Sujet de l'alerte
            alert_details: Détails de l'alerte
            
        Returns:
            Succès de l'envoi
        """
        data = {
            "alert_type": alert_type,
            "alert_subject": alert_subject,
            "alert_details": alert_details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        admin_emails = self.admin_config.get("admin_emails", [])
        if not admin_emails:
            logger.warning("Aucun email d'administrateur configuré, alerte non envoyée")
            return False
        
        return await self.send_notification(NotificationType.ADMIN_ALERT, admin_emails[0], data, 
                                          cc=admin_emails[1:] if len(admin_emails) > 1 else None)
    
    async def notify_stock_issue(self, 
                               order_id: str, 
                               customer_name: str,
                               product_names: List[str],
                               supplier: str,
                               issue_details: str) -> bool:
        """
        Notifie les administrateurs d'un problème de stock.
        
        Args:
            order_id: Identifiant de la commande
            customer_name: Nom du client
            product_names: Noms des produits concernés
            supplier: Nom du fournisseur
            issue_details: Détails du problème
            
        Returns:
            Succès de l'envoi
        """
        data = {
            "order_id": order_id,
            "customer_name": customer_name,
            "product_names": ", ".join(product_names),
            "supplier": supplier,
            "issue_details": issue_details,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        admin_emails = self.admin_config.get("admin_emails", [])
        if not admin_emails:
            logger.warning("Aucun email d'administrateur configuré, notification non envoyée")
            return False
        
        return await self.send_notification(NotificationType.STOCK_ISSUE, admin_emails[0], data,
                                          cc=admin_emails[1:] if len(admin_emails) > 1 else None)
