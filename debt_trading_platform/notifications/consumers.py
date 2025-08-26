import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Notification, Device
import logging

logger = logging.getLogger('debt_trading')


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications"""
    
    async def connect(self):
        """Handle new WebSocket connection"""
        # Check if user is authenticated
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            # Add user to their personal notification group
            self.user_group_name = f"user_{self.scope['user'].id}_notifications"
            
            # Join room group
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            
            await self.accept()
            
            # Send connection confirmation
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Connected to notification service',
                'timestamp': timezone.now().isoformat()
            }))
            
            # Send unread notification count
            unread_count = await self.get_unread_notification_count()
            await self.send(text_data=json.dumps({
                'type': 'unread_count',
                'count': unread_count
            }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave room group
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'mark_as_read':
                notification_id = data.get('notification_id')
                if notification_id:
                    await self.mark_notification_as_read(notification_id)
                    # Send updated unread count
                    unread_count = await self.get_unread_notification_count()
                    await self.send(text_data=json.dumps({
                        'type': 'unread_count',
                        'count': unread_count
                    }))
            
            elif message_type == 'mark_all_as_read':
                await self.mark_all_notifications_as_read()
                # Send updated unread count
                unread_count = await self.get_unread_notification_count()
                await self.send(text_data=json.dumps({
                    'type': 'unread_count',
                    'count': unread_count
                }))
            
            elif message_type == 'get_recent_notifications':
                limit = data.get('limit', 10)
                notifications = await self.get_recent_notifications(limit)
                await self.send(text_data=json.dumps({
                    'type': 'recent_notifications',
                    'notifications': notifications
                }))
                
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from WebSocket")
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {str(e)}")

    async def notification_message(self, event):
        """Send notification message to WebSocket"""
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
        
        # Update unread count
        unread_count = await self.get_unread_notification_count()
        await self.send(text_data=json.dumps({
            'type': 'unread_count',
            'count': unread_count
        }))

    # Database operations (async)
    @database_sync_to_async
    def get_unread_notification_count(self):
        """Get count of unread notifications for user"""
        return Notification.objects.filter(
            user=self.scope['user'],
            status='UNREAD'
        ).count()

    @database_sync_to_async
    def mark_notification_as_read(self, notification_id):
        """Mark a specific notification as read"""
        try:
            notification = Notification.objects.get(
                id=notification_id,
                user=self.scope['user']
            )
            notification.mark_as_read()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_all_notifications_as_read(self):
        """Mark all notifications as read for user"""
        Notification.objects.filter(
            user=self.scope['user'],
            status='UNREAD'
        ).update(
            status='READ',
            read_at=timezone.now()
        )

    @database_sync_to_async
    def get_recent_notifications(self, limit=10):
        """Get recent notifications for user"""
        notifications = Notification.objects.filter(
            user=self.scope['user']
        ).order_by('-created_at')[:limit]
        
        return [
            {
                'id': str(notification.id),
                'title': notification.title,
                'message': notification.message,
                'priority': notification.priority,
                'status': notification.status,
                'created_at': notification.created_at.isoformat(),
                'is_read': notification.status == 'READ',
                'data': notification.data
            }
            for notification in notifications
        ]


class DeviceConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for device management and push notifications"""
    
    async def connect(self):
        """Handle new WebSocket connection for device management"""
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            # Add user to their device management group
            self.device_group_name = f"user_{self.scope['user'].id}_devices"
            
            await self.channel_layer.group_add(
                self.device_group_name,
                self.channel_name
            )
            
            await self.accept()

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'device_group_name'):
            await self.channel_layer.group_discard(
                self.device_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle incoming device management messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'register_device':
                device_token = data.get('device_token')
                platform = data.get('platform')
                name = data.get('name', '')
                model = data.get('model', '')
                os_version = data.get('os_version', '')
                
                if device_token and platform:
                    await self.register_device(
                        device_token, platform, name, model, os_version
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'device_registered',
                        'message': 'Device registered successfully'
                    }))
            
            elif message_type == 'unregister_device':
                device_token = data.get('device_token')
                if device_token:
                    await self.unregister_device(device_token)
                    await self.send(text_data=json.dumps({
                        'type': 'device_unregistered',
                        'message': 'Device unregistered successfully'
                    }))
                    
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from device WebSocket")
        except Exception as e:
            logger.error(f"Error processing device WebSocket message: {str(e)}")

    @database_sync_to_async
    def register_device(self, device_token, platform, name, model, os_version):
        """Register a new device for push notifications"""
        try:
            device, created = Device.objects.get_or_create(
                user=self.scope['user'],
                device_token=device_token,
                defaults={
                    'platform': platform,
                    'name': name,
                    'model': model,
                    'os_version': os_version,
                    'is_active': True
                }
            )
            
            if not created:
                # Update existing device
                device.platform = platform
                device.name = name
                device.model = model
                device.os_version = os_version
                device.is_active = True
                device.save()
                
            return device
        except Exception as e:
            logger.error(f"Error registering device: {str(e)}")
            return None

    @database_sync_to_async
    def unregister_device(self, device_token):
        """Unregister a device from push notifications"""
        try:
            Device.objects.filter(
                user=self.scope['user'],
                device_token=device_token
            ).update(is_active=False)
            return True
        except Exception as e:
            logger.error(f"Error unregistering device: {str(e)}")
            return False


# Utility functions for sending notifications
async def send_notification_to_user(user_id, notification_data):
    """Send notification to a specific user via WebSocket"""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    group_name = f"user_{user_id}_notifications"
    
    await channel_layer.group_send(
        group_name,
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )


async def send_notification_to_all_users(notification_data):
    """Send notification to all connected users (use with caution)"""
    from channels.layers import get_channel_layer
    
    channel_layer = get_channel_layer()
    
    # This would require tracking all user groups
    # Implementation depends on specific use case
    pass