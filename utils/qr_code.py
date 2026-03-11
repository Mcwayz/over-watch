"""
QR Code generation utility module
"""
import qrcode
from io import BytesIO
from django.core.files import File
import json


class QRCodeGenerator:
    """QR Code generation utility"""

    @staticmethod
    def generate_parcel_qr(tracking_number):
        """Generate QR code for parcel tracking number"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(tracking_number)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img

    @staticmethod
    def generate_qr_file(tracking_number):
        """Generate QR code and return as Django File"""
        img = QRCodeGenerator.generate_parcel_qr(tracking_number)
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return File(buf, name=f'qr_{tracking_number}.png')

    @staticmethod
    def generate_driver_qr(driver_id):
        """Generate QR code for driver identification"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_data = json.dumps({
            'type': 'driver',
            'driver_id': str(driver_id),
        })
        qr.add_data(qr_data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        return img

    @staticmethod
    def decode_qr_data(qr_data):
        """Decode QR code data"""
        try:
            return json.loads(qr_data)
        except json.JSONDecodeError:
            # If it's just a tracking number
            return {'type': 'parcel', 'tracking_number': qr_data}
