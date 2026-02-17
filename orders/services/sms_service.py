import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms_msg91(phone, message, order_id=None):
    """Send SMS via MSG91 API"""
    try:
        api_key = settings.MSG91_API_KEY
        sender_id = settings.MSG91_SENDER_ID
        route = settings.MSG91_ROUTE
        
        if not api_key:
            logger.warning("MSG91 API key not configured")
            return {'status': 'failed', 'message': 'SMS service not configured'}
        
        url = "https://api.msg91.com/api/v5/flow/"
        
        payload = {
            "sender": sender_id,
            "route": route,
            "country": "91",
            "sms": [
                {
                    "message": message,
                    "to": [phone.replace("+", "").replace(" ", "")]
                }
            ]
        }
        
        headers = {
            "authkey": api_key,
            "content-type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            logger.info(f"MSG91 SMS sent to {phone}")
            return {
                'status': 'success',
                'message': 'SMS sent successfully',
                'response': response.json()
            }
        else:
            logger.error(f"MSG91 SMS failed: {response.text}")
            return {
                'status': 'failed',
                'message': response.text,
                'status_code': response.status_code
            }
    
    except requests.exceptions.Timeout:
        logger.error(f"MSG91 SMS timeout for {phone}")
        return {'status': 'failed', 'message': 'Request timeout'}
    except Exception as e:
        logger.exception(f"MSG91 SMS error: {str(e)}")
        return {'status': 'failed', 'message': str(e)}


def send_sms_fast2sms(phone, message, order_id=None):
    """Send SMS via Fast2SMS API"""
    try:
        api_key = settings.FAST2SMS_API_KEY
        
        if not api_key:
            logger.warning("Fast2SMS API key not configured")
            return {'status': 'failed', 'message': 'SMS service not configured'}
        
        url = "https://www.fast2sms.com/dev/bulkV2"
        
        payload = {
            "route": "v3",
            "sender_id": settings.FAST2SMS_SENDER_ID,
            "message": message,
            "language": "english",
            "flash": 0,
            "numbers": phone.replace("+91", "").replace(" ", "")
        }
        
        headers = {
            "authorization": api_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "Cache-Control": "no-cache"
        }
        
        response = requests.post(url, data=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('return'):
                logger.info(f"Fast2SMS sent to {phone}")
                return {
                    'status': 'success',
                    'message': 'SMS sent successfully',
                    'response': result
                }
            else:
                logger.error(f"Fast2SMS failed: {result}")
                return {
                    'status': 'failed',
                    'message': result.get('message', 'Unknown error')
                }
        else:
            logger.error(f"Fast2SMS failed: {response.text}")
            return {
                'status': 'failed',
                'message': response.text,
                'status_code': response.status_code
            }
    
    except requests.exceptions.Timeout:
        logger.error(f"Fast2SMS timeout for {phone}")
        return {'status': 'failed', 'message': 'Request timeout'}
    except Exception as e:
        logger.exception(f"Fast2SMS error: {str(e)}")
        return {'status': 'failed', 'message': str(e)}


def send_sms(phone, message, order_id=None):
    """
    Main SMS sending function - uses configured provider
    Fallback to secondary provider if primary fails
    """
    provider = getattr(settings, 'SMS_PROVIDER', 'msg91').lower()
    
    if provider == 'fast2sms':
        result = send_sms_fast2sms(phone, message, order_id)
        if result['status'] == 'failed':
            logger.info("Trying MSG91 as fallback")
            result = send_sms_msg91(phone, message, order_id)
    else:
        result = send_sms_msg91(phone, message, order_id)
        if result['status'] == 'failed':
            logger.info("Trying Fast2SMS as fallback")
            result = send_sms_fast2sms(phone, message, order_id)
    
    return result
