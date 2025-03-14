#!/usr/bin/env python3
"""
Tests unitaires pour le gestionnaire de notifications
Fait partie du projet Dropshipping Crew AI
"""

import unittest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
import smtplib
import aiohttp

from notifications.notification_manager import NotificationManager, NotificationType


class TestNotificationManager(unittest.TestCase):
    """
    Tests pour la classe NotificationManager.
    """
    
    def setUp(self):
        """Configuration initiale pour les tests."""
        # Configuration de test
        self.test_config = {
            "email": {
                "smtp_server": "test-smtp.example.com",
                "smtp_port": 587,
                "smtp_username": "test@example.com",
                "smtp_password": "test-password",
                "sender_email": "noreply@dropshipping-crew.ai",
                "sender_name": "Test Store"
            },
            "webhooks": {
                "enabled": True,
                "urls": ["https://webhook.example.com/test"]
            },
            "admin": {
                "admin_emails": ["admin@dropshipping-crew.ai"],
                "notify_on": ["order_issue", "stock_issue", "admin_alert"]
            }
        }
        
        self.notification_manager = NotificationManager(self.test_config)
        
        # Données de test
        self.test_order_id = "ORD-123456"
        self.test_customer_email = "customer@example.com"
        self.test_customer_name = "John Doe"
        self.test_product_names = ["Product 1", "Product 2"]
        self.test_supplier = "AliExpress"
        self.test_issue_details = "Product out of stock"

    @patch('smtplib.SMTP')
    async def test_send_email(self, mock_smtp):
        """Test de l'envoi d'email via SMTP."""
        # Configuration du mock
        mock_smtp_instance = MagicMock()
        mock_smtp.return_value = mock_smtp_instance
        
        # Appel de la méthode à tester
        result = await self.notification_manager._send_email(
            self.test_customer_email,
            "Test Subject",
            "Test Body",
            cc=["cc@example.com"],
            bcc=["bcc@example.com"]
        )
        
        # Vérifications
        self.assertTrue(result)
        mock_smtp.assert_called_once_with(
            self.test_config["email"]["smtp_server"],
            self.test_config["email"]["smtp_port"]
        )
        mock_smtp_instance.ehlo.assert_called_once()
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(
            self.test_config["email"]["smtp_username"],
            self.test_config["email"]["smtp_password"]
        )
        mock_smtp_instance.sendmail.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()

    @patch('aiohttp.ClientSession.post')
    async def test_send_webhook(self, mock_post):
        """Test de l'envoi de notification via webhook."""
        # Configuration du mock
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Appel de la méthode à tester
        result = await self.notification_manager._send_webhook(
            NotificationType.ORDER_PLACED,
            {"order_id": self.test_order_id}
        )
        
        # Vérifications
        self.assertTrue(result)
        mock_post.assert_called_once()

    @patch.object(NotificationManager, '_send_email')
    @patch.object(NotificationManager, '_send_webhook')
    async def test_send_notification(self, mock_send_webhook, mock_send_email):
        """Test de l'envoi d'une notification complète."""
        # Configuration des mocks
        mock_send_email.return_value = True
        mock_send_webhook.return_value = True
        
        # Données de test
        data = {
            "order_id": self.test_order_id,
            "customer_name": self.test_customer_name
        }
        
        # Appel de la méthode à tester
        result = await self.notification_manager.send_notification(
            NotificationType.ORDER_PLACED,
            self.test_customer_email,
            data
        )
        
        # Vérifications
        self.assertTrue(result)
        mock_send_email.assert_called_once()
        mock_send_webhook.assert_called_once_with(NotificationType.ORDER_PLACED, data)

    @patch.object(NotificationManager, 'send_notification')
    async def test_notify_order_status(self, mock_send_notification):
        """Test de la notification d'un changement de statut d'une commande."""
        # Configuration du mock
        mock_send_notification.return_value = True
        
        # Données supplémentaires de test
        additional_data = {
            "tracking_number": "TRACK123",
            "carrier": "Test Carrier",
            "tracking_url": "https://example.com/track/TRACK123"
        }
        
        # Appel de la méthode à tester
        result = await self.notification_manager.notify_order_status(
            self.test_order_id,
            self.test_customer_email,
            self.test_customer_name,
            NotificationType.SHIPPED,
            additional_data
        )
        
        # Vérifications
        self.assertTrue(result)
        mock_send_notification.assert_called_once()
        
        # Vérification des arguments
        args, kwargs = mock_send_notification.call_args
        self.assertEqual(args[0], NotificationType.SHIPPED)
        self.assertEqual(args[1], self.test_customer_email)
        self.assertEqual(args[2]["order_id"], self.test_order_id)
        self.assertEqual(args[2]["customer_name"], self.test_customer_name)
        self.assertEqual(args[2]["tracking_number"], "TRACK123")

    @patch.object(NotificationManager, 'send_notification')
    async def test_send_admin_alert(self, mock_send_notification):
        """Test de l'envoi d'une alerte aux administrateurs."""
        # Configuration du mock
        mock_send_notification.return_value = True
        
        # Appel de la méthode à tester
        result = await self.notification_manager.send_admin_alert(
            "TEST_ALERT",
            "Test Alert Subject",
            "This is a test alert."
        )
        
        # Vérifications
        self.assertTrue(result)
        mock_send_notification.assert_called_once()
        
        # Vérification des arguments
        args, kwargs = mock_send_notification.call_args
        self.assertEqual(args[0], NotificationType.ADMIN_ALERT)
        self.assertEqual(args[1], self.test_config["admin"]["admin_emails"][0])
        self.assertEqual(args[2]["alert_type"], "TEST_ALERT")
        self.assertEqual(args[2]["alert_subject"], "Test Alert Subject")
        self.assertEqual(args[2]["alert_details"], "This is a test alert.")

    @patch.object(NotificationManager, 'send_notification')
    async def test_notify_stock_issue(self, mock_send_notification):
        """Test de la notification d'un problème de stock."""
        # Configuration du mock
        mock_send_notification.return_value = True
        
        # Appel de la méthode à tester
        result = await self.notification_manager.notify_stock_issue(
            self.test_order_id,
            self.test_customer_name,
            self.test_product_names,
            self.test_supplier,
            self.test_issue_details
        )
        
        # Vérifications
        self.assertTrue(result)
        mock_send_notification.assert_called_once()
        
        # Vérification des arguments
        args, kwargs = mock_send_notification.call_args
        self.assertEqual(args[0], NotificationType.STOCK_ISSUE)
        self.assertEqual(args[1], self.test_config["admin"]["admin_emails"][0])
        self.assertEqual(args[2]["order_id"], self.test_order_id)
        self.assertEqual(args[2]["customer_name"], self.test_customer_name)
        self.assertEqual(args[2]["product_names"], "Product 1, Product 2")
        self.assertEqual(args[2]["supplier"], self.test_supplier)
        self.assertEqual(args[2]["issue_details"], self.test_issue_details)

    @patch.object(NotificationManager, '_send_email')
    async def test_notify_admins(self, mock_send_email):
        """Test de la notification des administrateurs."""
        # Configuration du mock
        mock_send_email.return_value = True
        
        # Données de test
        data = {
            "order_id": self.test_order_id,
            "customer_name": self.test_customer_name,
            "issue_details": self.test_issue_details
        }
        
        # Appel de la méthode à tester
        result = await self.notification_manager._notify_admins(
            NotificationType.ORDER_ISSUE,
            data
        )
        
        # Vérifications
        self.assertTrue(result)
        mock_send_email.assert_called_once()

    @patch.object(NotificationManager, '_send_email')
    async def test_send_notification_error_handling(self, mock_send_email):
        """Test de la gestion des erreurs lors de l'envoi de notification."""
        # Configuration du mock pour simuler une erreur
        mock_send_email.side_effect = Exception("Test exception")
        
        # Données de test
        data = {
            "order_id": self.test_order_id,
            "customer_name": self.test_customer_name
        }
        
        # Appel de la méthode à tester
        result = await self.notification_manager.send_notification(
            NotificationType.ORDER_PLACED,
            self.test_customer_email,
            data
        )
        
        # Vérifications
        self.assertFalse(result)
        mock_send_email.assert_called_once()

    @patch.object(NotificationManager, '_send_webhook_request')
    async def test_send_webhook_multiple_urls(self, mock_send_webhook_request):
        """Test de l'envoi de webhooks à plusieurs URLs."""
        # Configuration du mock
        mock_send_webhook_request.side_effect = [True, False]  # Premier succès, deuxième échec
        
        # Modifier la configuration pour avoir plusieurs URLs
        self.notification_manager.webhook_config["urls"] = [
            "https://webhook.example.com/test1",
            "https://webhook.example.com/test2"
        ]
        
        # Données de test
        data = {
            "order_id": self.test_order_id,
            "customer_name": self.test_customer_name
        }
        
        # Appel de la méthode à tester
        result = await self.notification_manager._send_webhook(
            NotificationType.ORDER_PLACED,
            data
        )
        
        # Vérifications
        self.assertTrue(result)  # Devrait être True car au moins une requête a réussi
        self.assertEqual(mock_send_webhook_request.call_count, 2)

    def test_notification_types_enum(self):
        """Test de l'énumération des types de notification."""
        # Vérification des valeurs de l'enum
        self.assertEqual(NotificationType.ORDER_PLACED.value, "order_placed")
        self.assertEqual(NotificationType.SHIPPED.value, "shipped")
        self.assertEqual(NotificationType.DELIVERED.value, "delivered")
        self.assertEqual(NotificationType.ORDER_ISSUE.value, "order_issue")
        
        # Vérification de la conversion
        self.assertEqual(str(NotificationType.ORDER_PLACED), "order_placed")


def run_async_tests():
    """Exécute les tests asynchrones."""
    loop = asyncio.get_event_loop()
    unittest.main(defaultTest='TestNotificationManager')


if __name__ == '__main__':
    run_async_tests()
