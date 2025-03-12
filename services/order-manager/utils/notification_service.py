import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class NotificationService:
    """Service de notification pour l'agent Order Manager"""
    
    def __init__(self):
        """Initialise le service de notification"""
        self.logger = logging.getLogger("order-manager.notification_service")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.notification_email = os.getenv("NOTIFICATION_EMAIL", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
    
    async def send_email(self, subject: str, message: str, recipient: Optional[str] = None) -> bool:
        """Envoie un email de notification
        
        Args:
            subject: Sujet de l'email
            message: Corps de l'email
            recipient: Destinataire de l'email (utilise NOTIFICATION_EMAIL par défaut)
            
        Returns:
            bool: True si l'email a été envoyé avec succès, False sinon
        """
        if not recipient:
            recipient = self.notification_email
        
        if not recipient or not self.smtp_username or not self.smtp_password:
            self.logger.warning("Configuration SMTP incomplète, impossible d'envoyer l'email")
            return False
        
        try:
            # Création du message
            msg = MIMEMultipart()
            msg["From"] = self.from_email
            msg["To"] = recipient
            msg["Subject"] = subject
            
            # Ajout du corps du message
            msg.attach(MIMEText(message, "html"))
            
            # Connexion au serveur SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            self.logger.info(f"Email envoyé à {recipient}: {subject}")
            return True
        except Exception as e:
            self.logger.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
            return False
    
    async def notify_new_order(self, order_data: Dict) -> bool:
        """Envoie une notification pour une nouvelle commande
        
        Args:
            order_data: Données de la commande
            
        Returns:
            bool: True si la notification a été envoyée avec succès, False sinon
        """
        subject = f"Nouvelle commande reçue - #{order_data.get('id', 'N/A')}"
        
        # Création du tableau des articles commandés
        items_html = ""
        for item in order_data.get("line_items", []):
            items_html += f"""<tr>
                <td>{item.get('title', 'N/A')}</td>
                <td>{item.get('quantity', 0)}</td>
                <td>{item.get('price', '0.00')}€</td>
            </tr>"""
        
        message = f"""
        <html>
        <head>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h2>Nouvelle commande reçue</h2>
            <p><strong>Commande #:</strong> {order_data.get('id', 'N/A')}</p>
            <p><strong>Date:</strong> {order_data.get('created_at', 'N/A')}</p>
            <p><strong>Client:</strong> {order_data.get('customer', {}).get('first_name', '')} {order_data.get('customer', {}).get('last_name', '')}</p>
            <p><strong>Email client:</strong> {order_data.get('customer', {}).get('email', 'N/A')}</p>
            <p><strong>Total:</strong> {order_data.get('total_price', '0.00')}€</p>
            
            <h3>Articles commandés:</h3>
            <table>
                <tr>
                    <th>Produit</th>
                    <th>Quantité</th>
                    <th>Prix unitaire</th>
                </tr>
                {items_html}
            </table>
            
            <p>Veuillez traiter cette commande dès que possible.</p>
        </body>
        </html>
        """
        
        return await self.send_email(subject, message)
    
    async def notify_order_processed(self, order_id: int, supplier: str, tracking_info: Optional[Dict] = None) -> bool:
        """Envoie une notification pour une commande traitée
        
        Args:
            order_id: Identifiant de la commande
            supplier: Fournisseur utilisé pour la commande
            tracking_info: Informations de suivi (optionnel)
            
        Returns:
            bool: True si la notification a été envoyée avec succès, False sinon
        """
        subject = f"Commande traitée - #{order_id}"
        
        tracking_html = ""
        if tracking_info:
            tracking_html = f"""
            <p><strong>Numéro de suivi:</strong> {tracking_info.get('tracking_number', 'N/A')}</p>
            <p><strong>Transporteur:</strong> {tracking_info.get('carrier', 'N/A')}</p>
            <p><strong>Lien de suivi:</strong> <a href="{tracking_info.get('tracking_url', '#')}">{tracking_info.get('tracking_url', 'N/A')}</a></p>
            """
        
        message = f"""
        <html>
        <body>
            <h2>Commande traitée avec succès</h2>
            <p><strong>Commande #:</strong> {order_id}</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Fournisseur:</strong> {supplier}</p>
            {tracking_html}
            <p>La commande a été traitée et envoyée au fournisseur avec succès.</p>
        </body>
        </html>
        """
        
        return await self.send_email(subject, message)
    
    async def notify_error(self, order_id: Optional[int], error_message: str, error_details: Optional[Dict] = None) -> bool:
        """Envoie une notification d'erreur
        
        Args:
            order_id: Identifiant de la commande (optionnel)
            error_message: Message d'erreur
            error_details: Détails de l'erreur (optionnel)
            
        Returns:
            bool: True si la notification a été envoyée avec succès, False sinon
        """
        subject = f"ERREUR - Traitement de commande" + (f" #{order_id}" if order_id else "")
        
        details_html = ""
        if error_details:
            details_html = "<h3>Détails techniques:</h3><pre>" + str(error_details) + "</pre>"
        
        message = f"""
        <html>
        <body>
            <h2 style="color: red;">Erreur lors du traitement d'une commande</h2>
            <p><strong>Commande #:</strong> {order_id if order_id else 'N/A'}</p>
            <p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Erreur:</strong> {error_message}</p>
            {details_html}
            <p>Veuillez vérifier le système et résoudre le problème dès que possible.</p>
        </body>
        </html>
        """
        
        return await self.send_email(subject, message)
    
    async def notify_shipment_update(self, order_id: int, tracking_info: Dict) -> bool:
        """Envoie une notification de mise à jour d'expédition
        
        Args:
            order_id: Identifiant de la commande
            tracking_info: Informations de suivi
            
        Returns:
            bool: True si la notification a été envoyée avec succès, False sinon
        """
        subject = f"Mise à jour d'expédition - Commande #{order_id}"
        
        status_emoji = {
            "pending": "⏳",
            "in_transit": "🚚",
            "out_for_delivery": "🚚",
            "delivered": "✅",
            "exception": "⚠️",
            "returned": "↩️",
            "failure": "❌"
        }
        
        status = tracking_info.get('status', 'pending')
        emoji = status_emoji.get(status, "📦")
        
        message = f"""
        <html>
        <body>
            <h2>Mise à jour d'expédition {emoji}</h2>
            <p><strong>Commande #:</strong> {order_id}</p>
            <p><strong>Date de mise à jour:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>Statut actuel:</strong> {tracking_info.get('status_text', status)}</p>
            <p><strong>Transporteur:</strong> {tracking_info.get('carrier', 'N/A')}</p>
            <p><strong>Numéro de suivi:</strong> {tracking_info.get('tracking_number', 'N/A')}</p>
            <p><strong>Dernière localisation:</strong> {tracking_info.get('location', 'N/A')}</p>
            <p><strong>Dernière mise à jour:</strong> {tracking_info.get('last_update', 'N/A')}</p>
            <p><strong>Lien de suivi:</strong> <a href="{tracking_info.get('tracking_url', '#')}">{tracking_info.get('tracking_url', 'N/A')}</a></p>
        </body>
        </html>
        """
        
        return await self.send_email(subject, message)
