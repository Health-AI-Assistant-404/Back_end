import requests
import random
import string


class SMSService:
    """Service for sending SMS using Payamak panel"""

    API_URL = 'https://rest.payamak-panel.com/api/SendSMS/SendSMS'
    USERNAME = '9136633633'
    PASSWORD = '95e081e4-4458-40cb-83b1-8239264b1a84'
    FROM_NUMBER = '50002710043538'

    @staticmethod
    def generate_otp(length=6):
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def send_otp(phone_number, otp_code):
        """Send OTP code to the given phone number"""
        try:
            payload = {
                'username': SMSService.USERNAME,
                'password': SMSService.PASSWORD,
                'to': phone_number,
                'from': SMSService.FROM_NUMBER,
                'text': f'کد یکبار مصرف: {otp_code}',
                'isFlash': 'false'
            }

            response = requests.post(
                SMSService.API_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                return True, 'SMS sent successfully'
            else:
                return False, f'Failed to send SMS: {response.text}'

        except requests.exceptions.Timeout:
            return False, 'SMS service timeout'
        except requests.exceptions.RequestException as e:
            return False, f'SMS service error: {str(e)}'
